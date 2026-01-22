import streamlit as st
from gsheet import load_sheet
from logic import *
from charts import *
from forecast import forecast_item
from pdf_report import generate_pdf
from wa_alert import send_alert
from config import DOC_ALERT, LEAD_TIME

st.set_page_config(layout="wide")
st.title("🏢 EXECUTIVE CONTROL TOWER – WAREHOUSE SCM")

# === THEME ===
with st.sidebar:
    theme = st.radio("Executive Mode", ["Light","Dark"])
    if theme == "Dark":
        st.markdown("""
        <style>
        body, .stApp { background-color:#0E1117; color:white; }
        </style>
        """, unsafe_allow_html=True)

# LOAD DATA
master = load_sheet("Master_Barang")
trans = prepare_transaksi(load_sheet("Transaksi"))
invoice = load_sheet("Invoice")
kapasitas = load_sheet("Kapasitas_Gudang")

# FILTER
with st.sidebar:
    gudang = st.multiselect(
        "Gudang",
        trans["Gudang"].unique(),
        default=trans["Gudang"].unique()
    )
trans = trans[trans["Gudang"].isin(gudang)]

# PROCESS
inv = inventory_position(trans)
inv = pallet_calculation(inv, master)
util = warehouse_utilization(inv, kapasitas)

# KPI
c1,c2,c3,c4 = st.columns(4)
c1.metric("Total Stok Karton", int(inv["Stok Karton"].sum()))
c2.metric("Total Pallet Used", round(inv["Pallet Used"].sum(),1))
c3.metric("Max Utilisasi (%)", round(util["Utilisasi %"].max(),1))
c4.metric("Item Risiko", inv[inv["Days Cover"]<=DOC_ALERT].shape[0])

# INVENTORY
st.subheader("📦 Inventory Control")
st.plotly_chart(inventory_bar(inv), use_container_width=True)
st.dataframe(inv)

# WAREHOUSE
st.subheader("🏗 Warehouse Utilization")
st.plotly_chart(utilization_bar(util), use_container_width=True)
st.dataframe(util)

# FLOW
st.subheader("🔄 Inbound & Outbound")
st.plotly_chart(inout_line(trans), use_container_width=True)

# COST
st.subheader("💰 Logistics Cost")
cost = invoice.melt(
    id_vars=["Periode","Gudang"],
    value_vars=[
        "Total Biaya Storing",
        "Total Biaya Handling",
        "Total Biaya Overtime",
        "Total Biaya Repacking",
        "Total Biaya Relabeling"
    ],
    var_name="Jenis Biaya",
    value_name="Total Biaya"
)
st.plotly_chart(cost_pie(cost), use_container_width=True)

# FORECAST
st.subheader("📈 Forecast & ROP")
item = st.selectbox("Pilih Barang", inv["Nama Barang"].unique())
fc = forecast_item(trans, item)

avg_out = trans[
    (trans["Nama Barang"]==item) &
    (trans["In Out"]=="OUT")
]["Karton"].mean()

rop = avg_out * LEAD_TIME
st.plotly_chart(forecast_chart(fc, rop), use_container_width=True)

# PDF
if st.button("📄 Download Executive PDF"):
    generate_pdf(inv, util)
    st.success("Executive PDF berhasil dibuat")

# ALERT
risk = inv[inv["Days Cover"]<=DOC_ALERT]
for _,r in risk.iterrows():
    send_alert(
        f"""⚠️ ALERT STOCK
Barang: {r['Nama Barang']}
Gudang: {r['Gudang']}
DOC: {round(r['Days Cover'],1)} hari"""
    )
    trans = prepare_transaksi(load_sheet("Transaksi"))



