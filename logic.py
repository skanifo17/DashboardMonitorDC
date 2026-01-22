import pandas as pd
import numpy as np

# =========================
# TRANSAKSI (SESUI GSHEET)
# =========================
def prepare_transaksi(df):

    # VALIDASI WAJIB
    required_cols = [
        "Tanggal",
        "Nama_Barang",
        "Tipe",
        "Jumlah_Karton",
        "Gudang"
    ]
    for c in required_cols:
        if c not in df.columns:
            raise ValueError(f"Kolom '{c}' tidak ada di Sheet Transaksi")

    # Rename internal (BIAR RAPI)
    df = df.rename(columns={
        "Nama_Barang": "nama_barang",
        "Jumlah_Karton": "karton"
    })

    df = df[["Tanggal", "nama_barang", "Tipe", "karton", "Gudang"]]

    # Parse tanggal (ANTI ERROR)
    df["Tanggal"] = pd.to_datetime(
        df["Tanggal"],
        errors="coerce",
        dayfirst=True
    )
    df = df.dropna(subset=["Tanggal"])

    # Pastikan numerik
    df["karton"] = pd.to_numeric(df["karton"], errors="coerce").fillna(0)

    # Normalisasi tipe
    df["Tipe"] = df["Tipe"].astype(str).str.upper().str.strip()

    # LOGIC STOK
    df["qty"] = np.where(
        df["Tipe"] == "OUTBOUND",
        -df["karton"],
        df["karton"]
    )

    return df


# =========================
# INVENTORY POSITION
# =========================
def inventory_position(df):

    stok = (
        df.groupby(["nama_barang", "Gudang"], as_index=False)["qty"]
        .sum()
        .rename(columns={"qty": "stok_karton"})
    )

    outbound = df[df["Tipe"] == "OUTBOUND"]

    avg_out = (
        outbound.groupby("nama_barang", as_index=False)["karton"]
        .mean()
        .rename(columns={"karton": "avg_daily_out"})
    )

    inv = stok.merge(avg_out, on="nama_barang", how="left")
    inv["avg_daily_out"] = inv["avg_daily_out"].fillna(0.1)
    inv["days_cover"] = inv["stok_karton"] / inv["avg_daily_out"]

    return inv


# =========================
# PALLET
# =========================
def pallet_calculation(inv, master):

    required_cols = [
        "Nama_Barang",
        "Kategori",
        "Karton_per_Pallet"
    ]
    for c in required_cols:
        if c not in master.columns:
            raise ValueError(f"Kolom '{c}' tidak ada di Master_Barang")

    master = master.rename(columns={
        "Nama_Barang": "nama_barang",
        "Karton_per_Pallet": "karton_per_pallet",
        "Kategori": "kategori"
    })

    master["karton_per_pallet"] = (
        pd.to_numeric(master["karton_per_pallet"], errors="coerce")
        .fillna(1)
    )

    inv = inv.merge(
        master[["nama_barang", "kategori", "karton_per_pallet"]],
        on="nama_barang",
        how="left"
    )

    inv["karton_per_pallet"] = inv["karton_per_pallet"].fillna(1)
    inv["pallet_used"] = inv["stok_karton"] / inv["karton_per_pallet"]

    return inv


# =========================
# UTILISASI GUDANG
# =========================
def warehouse_utilization(inv, kapasitas):

    # Pastikan kolom Gudang ada
    if "Gudang" not in kapasitas.columns:
        raise ValueError("Sheet Kapasitas_Gudang tidak punya kolom 'Gudang'")

    # === AUTO DETECT KOLOM KAPASITAS ===
    capacity_candidates = [
        "Total_Pallet",
        "Total Pallet",
        "Total_Pallet_Capacity",
        "Kapasitas_Pallet",
        "Capacity"
    ]

    capacity_col = None
    for c in capacity_candidates:
        if c in kapasitas.columns:
            capacity_col = c
            break

    # Jika tidak ketemu → WARNING, bukan error
    if capacity_col is None:
        kapasitas["total_pallet"] = 1
    else:
        kapasitas = kapasitas.rename(columns={capacity_col: "total_pallet"})
        kapasitas["total_pallet"] = (
            pd.to_numeric(kapasitas["total_pallet"], errors="coerce")
            .fillna(1)
        )

    util = (
        inv.groupby("Gudang", as_index=False)["pallet_used"]
        .sum()
        .merge(kapasitas[["Gudang", "total_pallet"]], on="Gudang", how="left")
    )

    util["total_pallet"] = util["total_pallet"].fillna(1)
    util["utilisasi_pct"] = util["pallet_used"] / util["total_pallet"] * 100

    return util


