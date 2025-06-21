import streamlit as st
import pandas as pd
import plotly.graph_objs as go

st.set_page_config(
    page_title="DTR Consumer Tagging Quality - DTR 7088-32",
    layout="wide"
)

# ---- LOAD DATA ----
master = pd.read_excel('Master_7088.xlsx')
outage = pd.read_excel('7088-32.xlsx')

dtr_code = 32
feeder_code = 7088

# ---- CLEAN METER SERIALS ----
master['Meter_Serial_Number'] = master['Meter_Serial_Number'].astype(str).str.strip().str.upper()
outage['Meter_Serial_Number'] = outage['Meter_Serial_Number'].astype(str).str.strip().str.upper()

# --- FILTER master for selected DTR and Feeder ---
master_dtr = master[(master['dtrcode'] == dtr_code) & (master['Feedercode'] == feeder_code)]
outage_meters = set(outage['Meter_Serial_Number'])
master_meters = set(master_dtr['Meter_Serial_Number'])

# 1. How many consumer are connected to DTR (all in outage file)
kpi1_connected = len(outage_meters)

# 2. Out of master, how many consumer have got outage (intersection)
kpi2_master_outage = len(master_meters & outage_meters)

# 3. Untagged customer (in master, not in outage)
kpi3_untagged = len(master_meters - outage_meters)

# 4. Outage seen in customer in belonging to same feeder(wrongly mapped)
# Outage meters not in this DTR as per master
wrongly_mapped_meters = outage_meters - master_meters
# These meters are found in master, same feeder, different DTR
wrongly_mapped_df = master[
    (master['Feedercode'] == feeder_code) &
    (master['dtrcode'] != dtr_code) &
    (master['Meter_Serial_Number'].isin(wrongly_mapped_meters))
]
kpi4_wrongly_mapped = wrongly_mapped_df.shape[0]

# 5. Total consumer connected after correction (sum of KPI 2 and 4)
kpi5_corrected = kpi2_master_outage + kpi4_wrongly_mapped

# Loss %
loss_percent = (kpi3_untagged / len(master_meters) * 100) if len(master_meters) > 0 else 0

# ---- DASHBOARD ----

st.markdown("""
    <h1 style='color:#1e3799;font-weight:700;margin-bottom:6px'>
        ⚡ Power Distribution Consumer Tagging Quality - DTR 7088-32
    </h1>
    <div style='color:#555;font-size:18px;margin-bottom:24px'>
        Professional dashboard for real-time mapping quality, outage verification, and consumer connection correction on DTR <b>7088-32</b>.
    </div>
""", unsafe_allow_html=True)

# ---- KPI CARDS ----
st.markdown("### 🏆 Core KPIs at a Glance")

col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("🟢 Live Connections on DTR", kpi1_connected)
col2.metric("✅ Master-Tagged with Outage", kpi2_master_outage)
col3.metric("🚫 Untagged Customers (Master only)", kpi3_untagged)
col4.metric("🔄 Wrongly Mapped (Other DTR, Same Feeder)", kpi4_wrongly_mapped)
col5.metric("🏆 Total After Correction", kpi5_corrected)
col6.metric("📉 Loss %", f"{loss_percent:.2f}%")

# ---- BAR CHART VISUALIZATION ----
kpi_labels = [
    "Live on DTR",
    "Master-Tagged Outage",
    "Untagged (Master only)",
    "Wrongly Mapped (Other DTR)",
    "Total After Correction"
]
kpi_values = [
    kpi1_connected,
    kpi2_master_outage,
    kpi3_untagged,
    kpi4_wrongly_mapped,
    kpi5_corrected
]
bar_colors = ['#27ae60', '#3498db', '#e74c3c', '#f39c12', '#9b59b6']
fig = go.Figure(data=[
    go.Bar(
        x=kpi_labels,
        y=kpi_values,
        marker_color=bar_colors,
        text=kpi_values,
        textposition='auto'
    )
])
fig.update_layout(
    title="Consumer Tagging Quality Breakdown for DTR 7088-32",
    yaxis_title="Number of Consumers",
    xaxis_title="KPI Category",
    bargap=0.3
)
st.plotly_chart(fig, use_container_width=True)

# ---- DETAILS TABLES ----
st.markdown("### 🗂️ Downloadable Details")

with st.expander("Live Connections on DTR (Outage File)"):
    st.dataframe(outage, use_container_width=True)
    st.download_button(
        "Download as CSV",
        data=outage.to_csv(index=False),
        file_name="7088-32_live_connections.csv",
        mime="text/csv"
    )

with st.expander("Master-Tagged Consumers with Outage"):
    df_master_tagged_outage = master_dtr[master_dtr['Meter_Serial_Number'].isin(outage_meters)]
    st.dataframe(df_master_tagged_outage, use_container_width=True)
    st.download_button(
        "Download as CSV",
        data=df_master_tagged_outage.to_csv(index=False),
        file_name="7088-32_master_tagged_outage.csv",
        mime="text/csv"
    )

with st.expander("Untagged Customers (Master Only)"):
    df_untagged = master_dtr[~master_dtr['Meter_Serial_Number'].isin(outage_meters)]
    st.dataframe(df_untagged, use_container_width=True)
    st.download_button(
        "Download as CSV",
        data=df_untagged.to_csv(index=False),
        file_name="7088-32_untagged_master_only.csv",
        mime="text/csv"
    )

with st.expander("Wrongly Mapped (Other DTR, Same Feeder)"):
    st.dataframe(wrongly_mapped_df, use_container_width=True)
    st.download_button(
        "Download as CSV",
        data=wrongly_mapped_df.to_csv(index=False),
        file_name="7088-32_wrongly_mapped.csv",
        mime="text/csv"
    )

st.markdown("""
    <div style='text-align:center;margin-top:24px;font-size:17px;color:#7f8c8d;'>
        🚀 <b>Power Analytics Dashboard</b> &nbsp;|&nbsp; <i>Smart, Reliable, Actionable</i>
    </div>
""", unsafe_allow_html=True)
