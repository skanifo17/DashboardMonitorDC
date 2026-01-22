import pandas as pd
import numpy as np

def prepare_transaksi(df):
    # Pastikan kolom ada
    required_cols = ["Tanggal", "Nama Barang", "Gudang", "In Out", "Karton"]
    df = df[required_cols]

    # Bersihkan spasi
    df["Tanggal"] = df["Tanggal"].astype(str).str.strip()

    # Convert tanggal (ANTI ERROR)
    df["Tanggal"] = pd.to_datetime(
        df["Tanggal"],
        errors="coerce",        # <-- KUNCI UTAMA
        dayfirst=True           # <-- AMAN untuk format Indonesia
    )

    # Drop baris tanggal invalid
    df = df.dropna(subset=["Tanggal"])

    # Pastikan Karton numerik
    df["Karton"] = pd.to_numeric(df["Karton"], errors="coerce").fillna(0)

    # Normalisasi IN / OUT
    df["In Out"] = df["In Out"].str.upper().str.strip()

    # Quantity signed
    df["Qty"] = np.where(
        df["In Out"] == "IN",
        df["Karton"],
        -df["Karton"]
    )

    return df
