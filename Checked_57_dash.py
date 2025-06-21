import streamlit as st
import pandas as pd
import plotly.graph_objs as go

st.set_page_config(
    page_title="DTR Outage KPIs Dashboard - 7088-57",
    layout="wide"
)

# ---- LOAD DATA FROM CORRECT SHEETS ----
master_all = pd.read_excel('Master_7088.xlsx', sheet_name='Sheet1')
outage = pd.read_excel('7088-57.xlsx', sheet_name='outage_154')
untagged = pd.read_excel('7088-57.xlsx', sheet_name='untagged_19_meters')
wrongly_mapped = pd.read_excel('7088-57.xlsx', sheet_name='wrongly_mapped_to_72')

# --- Robust filtering for this DTR only (57) ---
dtr_code = 57
feeder_code = 7088

master = master_all[(master_all['dtrcode'] == dtr_code) & (master_all['Feedercode'] == feeder_code)]

# --- Calculate KPIs ---
kpi1_master_tagged = len(master)
kpi2_connected_outage = len(outage)
kpi3_untagged = len(untagged)
kpi4_wrongly_mapped = len(wrongly_mapped)
kpi5_total_corrected = kpi2_connected_outage + kpi4_wrongly_mapped

# --- Dashboard layout ---
st.markdown("""
    <h1 style='color:#1e3799;font-weight:700;margin-bottom:6px'>
        ⚡ DTR Outage KPIs Dashboard <span style='font-size:18px;'>[Feeder: 7088, DTR: 57]</span>
    </h1>
    <div style='color:#555;font-size:18px;margin-bottom:24px'>
        Consumer mapping, outage verification, and correction dashboard for <b>DTR 7088-57</b>.
    </div>
""", unsafe_allow_html=True)

# --- KPI Cards ---
st.markdown("### 🏆 Core KPIs at a Glance")
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("📒 Master Tagged Consumers", kpi1_master_tagged)
col2.metric("🟢 Connected (Outage File)", kpi2_connected_outage)
col3.metric("🚫 Untagged (Master Only)", kpi3_untagged)
col4.metric("🔄 Wrongly Mapped (Other DTR, Same Feeder)", kpi4_wrongly_mapped)
col5.metric("🏆 Total After Correction", kpi5_total_corrected)

# --- Bar Chart ---
kpi_labels = [
    "Master Tagged",
    "Connected (Outage)",
    "Untagged",
    "Wrongly Mapped",
    "Total Corrected"
]
kpi_values = [
    kpi1_master_tagged,
    kpi2_connected_outage,
    kpi3_untagged,
    kpi4_wrongly_mapped,
    kpi5_total_corrected
]
bar_colors = ['#0984e3', '#27ae60', '#e74c3c', '#f39c12', '#9b59b6']
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
    title="DTR Outage KPIs Breakdown (7088-57)",
    yaxis_title="Number of Consumers",
    xaxis_title="KPI Category",
    bargap=0.3
)
st.plotly_chart(fig, use_container_width=True)

# --- Details download ---
st.markdown("### 🗂️ Downloadable Detailed Lists")

with st.expander("Master Tagged Consumers (Sheet1, filtered for DTR 57)"):
    st.dataframe(master, use_container_width=True)
    st.download_button(
        "Download as CSV",
        data=master.to_csv(index=False),
        file_name="7088-57_master_tagged_consumers.csv",
        mime="text/csv"
    )

with st.expander("Connected (Outage File)"):
    st.dataframe(outage, use_container_width=True)
    st.download_button(
        "Download as CSV",
        data=outage.to_csv(index=False),
        file_name="7088-57_connected_outage.csv",
        mime="text/csv"
    )

with st.expander("Untagged (Master Only)"):
    st.dataframe(untagged, use_container_width=True)
    st.download_button(
        "Download as CSV",
        data=untagged.to_csv(index=False),
        file_name="7088-57_untagged_master.csv",
        mime="text/csv"
    )

with st.expander("Wrongly Mapped (Other DTR, Same Feeder)"):
    st.dataframe(wrongly_mapped, use_container_width=True)
    st.download_button(
        "Download as CSV",
        data=wrongly_mapped.to_csv(index=False),
        file_name="7088-57_wrongly_mapped.csv",
        mime="text/csv"
    )

st.markdown("""
    <div style='text-align:center;margin-top:24px;font-size:17px;color:#7f8c8d;'>
        🚀 <b>Power Analytics Dashboard</b> | <i>Sheet-driven, Business-defined KPIs</i>
    </div>
""", unsafe_allow_html=True)
