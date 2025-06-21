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

# --- FILTER master for selected DTR and Feeder ---
master_dtr = master[(master['dtrcode'] == dtr_code) & (master['Feedercode'] == feeder_code)]
outage_meters = set(outage['Meter_Serial_Number'])
master_meters = set(master_dtr['Meter_Serial_Number'])

# 1. Live Connections on DTR (Consumers connected as per outage data)
kpi1_live_connections = len(outage_meters)

# 2. Master-Tagged Consumers Experiencing Outage
kpi2_master_outage = len(master_meters & outage_meters)

# 3. Potentially Disconnected (Untagged in Outage)
kpi3_unmapped = len(master_meters - outage_meters)

# 4. Outage in Feeder-Mapped (Possibly Misassigned)
#  - Meters in outage file but NOT belonging to this DTR as per master, but belong to the same feeder.
wrongly_mapped = set(outage['Meter_Serial_Number']) - master_meters
# Which of these are in master for feeder but other DTRs
feeder_mapped = master[(master['Feedercode'] == feeder_code) & (master['Meter_Serial_Number'].isin(wrongly_mapped))]
kpi4_wrongly_mapped = feeder_mapped.shape[0]

# 5. Total Effective Connections (Master-Tagged + Corrected)
kpi5_total_effective = kpi2_master_outage + kpi4_wrongly_mapped

# ---- DASHBOARD ----

st.markdown("""
    <h1 style='color:#1e3799;font-weight:700;margin-bottom:6px'>
        ⚡ Power Distribution Consumer Tagging Quality - DTR 7088-57
    </h1>
    <div style='color:#555;font-size:18px;margin-bottom:24px'>
        Advanced dashboard for real-time mapping quality, outage verification, and consumer connection correction on DTR <b>7088-57</b>.
    </div>
""", unsafe_allow_html=True)

# ---- KPI Cards ----
st.markdown("### 🔑 Core KPIs at a Glance")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("🟢 Live Connections on DTR", kpi1_live_connections, help="Consumers currently connected to this DTR as per live outage data")
col2.metric("✅ Master-Tagged Consumers Experiencing Outage", kpi2_master_outage, help="Consumers tagged in master for this DTR and present in outage data")
col3.metric("🚫 Potentially Disconnected (Untagged in Outage)", kpi3_unmapped, help="Master-tagged consumers for this DTR not found in outage data")
col4.metric("🔄 Outage in Feeder-Mapped (Possibly Misassigned)", kpi4_wrongly_mapped, help="Consumers present in outage for this feeder but assigned to other DTRs in master")
col5.metric("🏆 Total Effective Connections (Master-Tagged + Corrected)", kpi5_total_effective, help="Sum of master-tagged plus feeder-mapped consumers with outage")

st.divider()

# ---- BAR CHART VISUALIZATION ----
kpi_labels = [
    "Live on DTR", 
    "Master-Tagged Outage", 
    "Untagged (Potentially Disconnected)", 
    "Feeder-Mapped Outage", 
    "Total Effective Connections"
]
kpi_values = [
    kpi1_live_connections, 
    kpi2_master_outage, 
    kpi3_unmapped, 
    kpi4_wrongly_mapped, 
    kpi5_total_effective
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
    title="Consumer Tagging Quality Breakdown for DTR 7088-57",
    yaxis_title="Number of Consumers",
    xaxis_title="KPI Category",
    bargap=0.3
)
st.plotly_chart(fig, use_container_width=True)

st.divider()

# ---- DETAILED TABLES ----
st.markdown("### 🗂️ Detailed Consumer Lists (Click to Expand)")

with st.expander("Live Connections on DTR (Outage File)"):
    st.dataframe(outage, use_container_width=True)
    st.download_button(
        "Download as CSV",
        data=outage.to_csv(index=False),
        file_name="7088-57_live_connections.csv",
        mime="text/csv"
    )

with st.expander("Master-Tagged Consumers Experiencing Outage"):
    df_master_tagged_outage = master_dtr[master_dtr['Meter_Serial_Number'].isin(outage_meters)]
    st.dataframe(df_master_tagged_outage, use_container_width=True)
    st.download_button(
        "Download as CSV",
        data=df_master_tagged_outage.to_csv(index=False),
        file_name="7088-57_master_tagged_outage.csv",
        mime="text/csv"
    )

with st.expander("Potentially Disconnected (Untagged in Outage)"):
    df_unmapped = master_dtr[~master_dtr['Meter_Serial_Number'].isin(outage_meters)]
    st.dataframe(df_unmapped, use_container_width=True)
    st.download_button(
        "Download as CSV",
        data=df_unmapped.to_csv(index=False),
        file_name="7088-57_unmapped.csv",
        mime="text/csv"
    )

with st.expander("Feeder-Mapped Outage (Wrongly Mapped)"):
    st.dataframe(feeder_mapped, use_container_width=True)
    st.download_button(
        "Download as CSV",
        data=feeder_mapped.to_csv(index=False),
        file_name="7088-57_feeder_mapped_outage.csv",
        mime="text/csv"
    )

st.markdown("""
    <div style='text-align:center;margin-top:24px;font-size:17px;color:#7f8c8d;'>
        🚀 <b>Power Analytics Dashboard</b> &nbsp;|&nbsp; <i>Smart, Reliable, Actionable</i>
    </div>
""", unsafe_allow_html=True)
