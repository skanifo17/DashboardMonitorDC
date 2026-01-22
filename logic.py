import pandas as pd
import numpy as np
from schema import auto_map_columns

# =========================
# TRANSAKSI
# =========================
def prepare_transaksi(df):

    alias = {
        "tanggal": ["Tanggal", "Date"],
        "sku": ["SKU"],
        "nama_barang": ["Nama_Barang", "Nama Barang"],
        "tipe": ["Tipe", "Type"],
        "karton": ["Jumlah_Karton", "Jumlah Karton", "Karton"],
        "gudang": ["Gudang", "Warehouse"]
    }

    df = auto_map_columns(
        df,
        alias,
        required=["tanggal", "nama_barang", "tipe", "karton", "gudang"]
    )

    df["tanggal"] = pd.to_datetime(
        df["tanggal"],
        errors="coerce",
        dayfirst=True
    )
    df = df.dropna(subset=["tanggal"])

    df["karton"] = pd.to_numeric(df["karton"], errors="coerce").fillna(0)
    df["tipe"] = df["tipe"].astype(str).str.upper().str.strip()

    df["qty"] = np.where(
        df["tipe"].str.contains("OUT"),
        -df["karton"],
        df["karton"]
    )

    return df


# =========================
# INVENTORY
# =========================
def inventory_position(df):
    stok = (
        df.groupby(["nama_barang", "gudang"], as_index=False)["qty"]
        .sum()
        .rename(columns={"qty": "stok_karton"})
    )

    outbound = df[df["tipe"].str.contains("OUT")]

    avg = (
        outbound.groupby("nama_barang", as_index=False)["karton"]
        .mean()
        .rename(columns={"karton": "avg_daily_out"})
    )

    inv = stok.merge(avg, on="nama_barang", how="left")
    inv["avg_daily_out"] = inv["avg_daily_out"].fillna(0.1)
    inv["days_cover"] = inv["stok_karton"] / inv["avg_daily_out"]

    return inv


# =========================
# PALLET
# =========================
def pallet_calculation(inv, master):

    alias = {
        "nama_barang": ["Nama_Barang", "Nama Barang"],
        "kategori": ["Kategori"],
        "karton_per_pallet": [
            "Karton_per_Pallet",
            "Karton per Pallet"
        ]
    }

    master = auto_map_columns(
        master,
        alias,
        required=["nama_barang", "karton_per_pallet"]
    )

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

    alias = {
        "gudang": ["Gudang"],
        "total_pallet": [
            "Total_Pallet",
            "Total Pallet",
            "Capacity"
        ]
    }

    kapasitas = auto_map_columns(
        kapasitas,
        alias,
        required=["gudang", "total_pallet"]
    )

    kapasitas["total_pallet"] = (
        pd.to_numeric(kapasitas["total_pallet"], errors="coerce")
        .fillna(1)
    )

    util = (
        inv.groupby("gudang", as_index=False)["pallet_used"]
        .sum()
        .merge(kapasitas, on="gudang", how="left")
    )

    util["utilisasi_pct"] = util["pallet_used"] / util["total_pallet"] * 100

    return util
