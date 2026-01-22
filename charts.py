import plotly.express as px

def inventory_bar(inv):
    return px.bar(
        inv,
        x="Nama Barang",
        y="Stok Karton",
        color="Kategori",
        title="Inventory per SKU"
    )

def utilization_bar(util):
    return px.bar(
        util,
        x="Gudang",
        y="Utilisasi %",
        title="Warehouse Utilization (%)"
    )

def inout_line(df):
    return px.line(
        df,
        x="Tanggal",
        y="Karton",
        color="In Out",
        title="Inbound vs Outbound Trend"
    )

def cost_pie(df):
    return px.pie(
        df,
        names="Jenis Biaya",
        values="Total Biaya",
        hole=0.45,
        title="Logistic Cost Structure"
    )

def forecast_chart(fc, rop):
    fig = px.line(fc, x="ds", y="yhat", title="Demand Forecast")
    fig.add_hline(y=rop, line_dash="dash", annotation_text="ROP")
    return fig
