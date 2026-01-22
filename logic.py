import pandas as pd
import numpy as np
from config import LEAD_TIME

def prepare_transaksi(df):
    df["Tanggal"] = pd.to_datetime(df["Tanggal"])
    df["Qty"] = np.where(df["In Out"] == "IN", df["Karton"], -df["Karton"])
    return df

def inventory_position(df):
    stock = df.groupby(["Nama Barang","Gudang"],as_index=False)["Qty"].sum()
    stock.rename(columns={"Qty":"Stok Karton"}, inplace=True)

    out = df[df["In Out"]=="OUT"]
    avg = out.groupby("Nama Barang",as_index=False)["Karton"].mean()
    avg.rename(columns={"Karton":"Avg Daily Out"}, inplace=True)

    inv = stock.merge(avg,on="Nama Barang",how="left")
    inv["Days Cover"] = inv["Stok Karton"] / inv["Avg Daily Out"]
    return inv

def pallet_calculation(inv, master):
    inv = inv.merge(
        master[["Nama Barang","Kategori","Karton per Pallet"]],
        on="Nama Barang", how="left"
    )
    inv["Pallet Used"] = inv["Stok Karton"] / inv["Karton per Pallet"]
    return inv

def warehouse_utilization(inv, kapasitas):
    util = inv.groupby("Gudang",as_index=False)["Pallet Used"].sum()
    util = util.merge(kapasitas,on="Gudang")
    util["Utilisasi %"] = util["Pallet Used"] / util["Total Pallet Capacity"] * 100
    return util
