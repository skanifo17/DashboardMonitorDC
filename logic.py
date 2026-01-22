import pandas as pd
import numpy as np
from config import LEAD_TIME

def prepare_transaksi(df):
    # Rename kolom agar konsisten
    df = df.rename(columns={
        "Nama_Barang": "Nama Barang",
        "Jumlah_Karton": "Karton"
    })

    # Pilih kolom penting
    df = df[
        ["Tanggal", "SKU", "Nama Barang", "Tipe", "Karton", "Gudang"]
    ]

    # Bersihkan data
    df["Tanggal"] = pd.to_datetime(
        df["Tanggal"],
        errors="coerce",
        dayfirst=True
    )
    df = df.dropna(subset=["Tanggal"])

    df["Karton"] = pd.to_numeric(df["Karton"], errors="coerce").fillna(0)
    df["Tipe"] = df["Tipe"].str.upper().str.strip()

    # Mapping IN / OUT dari Tipe
    df["Qty"] = np.where(
        df["Tipe"].str.contains("OUT"),
        -df["Karton"],
        df["Karton"]
    )

    return df


def inventory_position(df):
    stock = (
        df.groupby(["Nama Barang", "Gudang"], as_index=False)["Qty"]
        .sum()
        .rename(columns={"Qty": "Stok Karton"})
    )

    outbound = df[df["Tipe"].str.contains("OUT")]
    avg_out = (
        outbound.groupby("Nama Barang", as_index=False)["Karton"]
        .mean()
        .rename(columns={"Karton": "Avg Daily Out"})
    )

    inv = stock.merge(avg_out, on="Nama Barang", how="left")
    inv["Avg Daily Out"] = inv["Avg Daily Out"].fillna(0.1)
    inv["Days Cover"] = inv["Stok Karton"] / inv["Avg Daily Out"]

    return inv


def pallet_calculation(inv, master):
    inv = inv.merge(
        master[["Nama Barang", "Kategori", "Karton per Pallet"]],
        on="Nama Barang",
        how="left"
    )
    inv["Pallet Used"] = inv["Stok Karton"] / inv["Karton per Pallet"]
    return inv


def warehouse_utilization(inv, kapasitas):
    util = inv.groupby("Gudang", as_index=False)["Pallet Used"].sum()
    util = util.merge(kapasitas, on="Gudang")
    util["Utilisasi %"] = util["Pallet Used"] / util["Total Pallet Capacity"] * 100
    return util
