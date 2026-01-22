from prophet import Prophet
import pandas as pd

def forecast_item(transaksi, item, days=30):
    df = transaksi[
        (transaksi["Nama Barang"]==item) &
        (transaksi["In Out"]=="OUT")
    ][["Tanggal","Karton"]]

    df = df.rename(columns={"Tanggal":"ds","Karton":"y"})

    model = Prophet()
    model.fit(df)

    future = model.make_future_dataframe(periods=days)
    forecast = model.predict(future)

    return forecast
