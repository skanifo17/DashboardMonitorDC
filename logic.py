import pandas as pd
import numpy as np
from config import LEAD_TIME

def normalize_columns(df):
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )
    return df


def prepare_transaksi(df):
    df = normalize_columns(df)

    df = df.rename(columns={
        "nama_barang": "nama_barang",
        "jumlah_karton": "karton"
    })

    required = ["tanggal", "nama_barang", "tipe", "karton", "gudang"]
    df = df[required]

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


def inventory_position(df):
    stock = (
        df.groupby(["nama_barang", "gudang"], as_index=False)["qty"]
        .sum()
        .rename(columns={"qty": "stok_karton"})
    )

    outbound = df[df["tipe"].str.contains("OUT")]
    avg_out = (
        outbound.groupby("nama_barang", as_index=False)["karton"]
        .mean()
        .rename(columns={"karton": "avg_daily_out"})
    )

    inv = stock.merge(avg_out, on="nama_barang", how="left")
    inv["avg_daily_out"] = inv["avg_daily_out"].fillna(0.1)
    inv["days_cover"] = inv["stok_karton"] / inv["avg_daily_out"]

    return inv


def pallet_calculation(inv, master):
    master = normalize_columns(master)

    # rename agar konsisten
    master = master.rename(columns={
        "nama_barang": "nama_barang",
        "kategori": "kategori",
        "karton_per_pallet": "karton_per_pallet"
    })

    required = ["nama_barang", "kategori", "karton_per_pallet"]
    master = master[required]

    inv = inv.merge(master, on="nama_barang", how="left")

    inv["karton_per_pallet"] = inv["karton_per_pallet"].fillna(1)
    inv["pallet_used"] = inv["stok_karton"] / inv["karton_per_pallet"]

    return inv


def warehouse_utilization(inv, kapasitas):
    kapasitas = normalize_columns(kapasitas)
    kapasitas = kapasitas.rename(columns={
        "total_pallet_capacity": "total_pallet_capacity"
    })

    util = (
        inv.groupby("gudang", as_index=False)["pallet_used"]
        .sum()
        .merge(kapasitas, on="gudang", how="left")
    )

    util["total_pallet_capacity"] = util["total_pallet_capacity"].fillna(1)
    util["utilisasi_%"] = (
        util["pallet_used"] / util["total_pallet_capacity"] * 100
    )

    return util
