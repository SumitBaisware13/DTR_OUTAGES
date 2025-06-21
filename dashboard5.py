import streamlit as st
import pandas as pd
import plotly.graph_objs as go

st.set_page_config(
    page_title="DTR Consumer Tagging Quality - Power Analytics",
    layout="wide"
)

# ---- LOAD DATA ----
master = pd.read_excel('Master_7088.xlsx')
outage = pd.read_excel('7088-57.xlsx')

dtr_code = 57
feeder_code = 7088

# ---- CLEAN METER SERIALS ----
master['Meter_Serial_Number'] = master['Meter_Serial_Number'].astype(str).str.strip().str.upper()
outage['Meter_Serial_Number'] = outage['Meter_Serial_Number'].astype(str).str.strip().str.upper()

# --- FILTER master for selected DTR and Feeder ---
master_dtr = master[(master['dtrcode'] == dtr_code) & (master['Feedercode'] == feeder_code)]
outage_meters = set(outage['Meter_Serial_Number'])
master_meters = set(master_dtr['Meter_Serial_Number'])

# 1. Live Connections on DTR
kpi1_live_connections = len(outage_meters)

# 2. Master-Tagged Consumers Experiencing Outage
kpi2_master_outage = len(master_meters & outage_meters)

# 3. Potentially Disconnected (Untagged in Outage)
kpi3_unmapped = len(master_meters - outage_meters)

# 4. Outage in Feeder-Mapped (Possibly Misassigned)
wrongly_mapped_meters = outage_meters - master_meters
feeder_others = master[
    (master['Feedercode'] == feeder_code) &
    (master['dtrcode'] != dtr_code) &
    (master['Meter_Serial_Number'].isin(wrongly_mapped_meters))
]
kpi4_wrongly_mapped = feeder_others.shape[0]

# 5. Total Effective Connections (Master-Tagged + Corrected)
kpi5_total_effective = kpi2_master_outage + kpi4_wrongly_mapped

# ---- KPI CARDS ----
st.markdown("### 🔑 Core KPIs at a Glance")

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("🟢 Live Connections on DTR", kpi1_live_connections)
col2.metric("✅ Master-Tagged Consumers Experiencing Outage", kpi2_master_outage)
col3.metric("🚫 Potentially Disconnected (Untagged in Outage)", kpi3_unmapped)
col4.metric("🔄 Outage in Feeder-Mapped (Possibly Misassigned)", kpi4_wrongly_mapped)
col5.metric("🏆 Total Effective Connections (Master-Tagged + Corrected)", kpi5_total_effective)
