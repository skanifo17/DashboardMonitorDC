import pandas as pd
import numpy as np

# =============================
# TRANSAKSI
# =============================
def prepare_transaksi(df):
    # Rename agar konsisten
    df = df.rename(columns={
        "Nama_Barang": "nama_barang",
        "Jumlah_Karton": "karton"
    })

    df = df[
        ["Tanggal", "SKU", "nama_barang", "Tipe", "karton", "Gudang"]
    ]

    # Tanggal aman
    df["Tanggal"] = pd.to_datetime(
        df["Tanggal"],
        errors="coerce",
        dayfirst=True
    )
    df = df.dropna(subset=["Tanggal"])

    # Karton numerik
    df["karton"] = pd.to_numeric(df["karton"], errors="coerce").fillna(0)

    # Normalisasi tipe
    df["Tipe"] = df["Tipe"].astype(str).str.upper().str.strip()

    # Qty logic
    df["qty"] = np.where(
        df["Tipe"] == "OUTBOUND",
        -df["karton"],
        df["karton"]
    )

    return df


# =============================
# INVENTORY POSITION
# =============================
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


# =============================
# PALLET CALCULATION
# =============================
def pallet_calculation(inv, master):
    master = master.rename(columns={
        "Nama_Barang": "nama_barang",
        "Karton_per_Pallet": "karton_per_pallet",
        "Kategori": "kategori"
    })

    master = master[
        ["nama_barang", "kategori", "karton_per_pallet"]
    ]

    inv = inv.merge(master, on="nama_barang", how="left")

    inv["karton_per_pallet"] = inv["karton_per_pallet"].fillna(1)
    inv["pallet_used"] = inv["stok_karton"] / inv["karton_per_pallet"]

    return inv


# =============================
# WAREHOUSE UTILIZATION
# =============================
def warehouse_utilization(inv, kapasitas):
    kapasitas = kapasitas.rename(columns={
        "Total_Pallet": "total_pallet"
    })

    util = (
        inv.groupby("Gudang", as_index=False)["pallet_used"]
        .sum()
        .merge(kapasitas, on="Gudang", how="left")
    )

    util["total_pallet"] = util["total_pallet"].fillna(1)
    util["utilisasi_pct"] = util["pallet_used"] / util["total_pallet"] * 100

    return util
