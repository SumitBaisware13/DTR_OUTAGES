import streamlit as st
import pandas as pd
import plotly.graph_objs as go

st.set_page_config(page_title="DTR Outage KPIs Dashboard", layout="wide")

# === Mapping DTRs, feeders, and their file/sheet structure ===
dtr_info = {
    "7088-57": {
        "master_file": "Master_7088.xlsx",
        "master_sheet": "Sheet1",
        "outage_file": "7088-57.xlsx",
        "outage_sheet": "outage_154",
        "untagged_sheet": "untagged_19_meters",
        "wrongly_mapped_sheet": "wrongly_mapped_to_72",
        "feeder": "7088",
        "dtr": "57"
    },
    "7088-32": {
        "master_file": "Master_7088.xlsx",
        "master_sheet": "Sheet1",
        "outage_file": "7088-32.xlsx",
        "outage_sheet": "Outage_37",
        "untagged_sheet": "Untagged_4",
        "wrongly_mapped_sheet": "32_meters_wrongly_mapped",
        "feeder": "7088",
        "dtr": "32"
    },
    "7088-86": {
        "master_file": "Master_7088.xlsx",
        "master_sheet": "Sheet1",
        "outage_file": "7088-86.xlsx",
        "outage_sheet": "outage_164",
        "untagged_sheet": "untagged_34_meters",
        "wrongly_mapped_sheet": "26_meter_wrongly_mapped_to _82",
        "feeder": "7088",
        "dtr": "86"
    },
    "15631-34": {
        "master_file": "Master_Feeder_15631.xlsx",
        "master_sheet": "Sheet1",
        "outage_file": "15631-34.xlsx",
        "outage_sheet": "Outage_345",
        "untagged_sheet": "Unmapped_67",
        "wrongly_mapped_sheet": "wrongly_mapped_40",
        "feeder": "15631",
        "dtr": "34"
    }
}


# --- For dropdowns ---
feeder_options = sorted(set(x['feeder'] for x in dtr_info.values()))
feeder_to_dtr = {}
for dtr_key, v in dtr_info.items():
    feeder_to_dtr.setdefault(v['feeder'], []).append(v['dtr'])

# --- SIDEBAR FOR SELECTION ---
st.sidebar.title("🔌 Select Feeder & DTR")
selected_feeder = st.sidebar.selectbox("Feeder", feeder_options)
selected_dtr = st.sidebar.selectbox("DTR", sorted(feeder_to_dtr[selected_feeder]))

# --- Lookup key for dtr_info ---
key = f"{selected_feeder}-{selected_dtr}"
d = dtr_info[key]

# --- LOAD DATA ---
# Master (always filter for this DTR)
master_all = pd.read_excel(d['master_file'], sheet_name=d['master_sheet'])
master = master_all[(master_all['dtrcode'] == int(d['dtr'])) & (master_all['Feedercode'] == int(d['feeder']))]
outage = pd.read_excel(d['outage_file'], sheet_name=d['outage_sheet'])
untagged = pd.read_excel(d['outage_file'], sheet_name=d['untagged_sheet'])
wrongly_mapped = pd.read_excel(d['outage_file'], sheet_name=d['wrongly_mapped_sheet'])

# --- Calculate KPIs ---
kpi1_master_tagged = len(master)
kpi2_connected_outage = len(outage)
kpi3_untagged = len(untagged)
kpi4_wrongly_mapped = len(wrongly_mapped)
kpi5_total_corrected = kpi2_connected_outage + kpi4_wrongly_mapped

# --- Dashboard layout ---
st.markdown(f"""
    <h1 style='color:#1e3799;font-weight:700;margin-bottom:6px'>
        ⚡ DTR Outage KPIs Dashboard <span style='font-size:18px;'>[Feeder: {selected_feeder}, DTR: {selected_dtr}]</span>
    </h1>
    <div style='color:#555;font-size:18px;margin-bottom:24px'>
        Consumer mapping, outage verification, and correction dashboard for <b>DTR {selected_feeder}-{selected_dtr}</b>.
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
    title=f"DTR Outage KPIs Breakdown ({selected_feeder}-{selected_dtr})",
    yaxis_title="Number of Consumers",
    xaxis_title="KPI Category",
    bargap=0.3
)
st.plotly_chart(fig, use_container_width=True)

# --- Details download ---
st.markdown("### 🗂️ Downloadable Detailed Lists")

with st.expander("Master Tagged Consumers (Sheet1, filtered for selected DTR)"):
    st.dataframe(master, use_container_width=True)
    st.download_button(
        "Download as CSV",
        data=master.to_csv(index=False),
        file_name=f"{selected_feeder}-{selected_dtr}_master_tagged_consumers.csv",
        mime="text/csv"
    )

with st.expander("Connected (Outage File)"):
    st.dataframe(outage, use_container_width=True)
    st.download_button(
        "Download as CSV",
        data=outage.to_csv(index=False),
        file_name=f"{selected_feeder}-{selected_dtr}_connected_outage.csv",
        mime="text/csv"
    )

with st.expander("Untagged (Master Only)"):
    st.dataframe(untagged, use_container_width=True)
    st.download_button(
        "Download as CSV",
        data=untagged.to_csv(index=False),
        file_name=f"{selected_feeder}-{selected_dtr}_untagged_master.csv",
        mime="text/csv"
    )

with st.expander("Wrongly Mapped (Other DTR, Same Feeder)"):
    st.dataframe(wrongly_mapped, use_container_width=True)
    st.download_button(
        "Download as CSV",
        data=wrongly_mapped.to_csv(index=False),
        file_name=f"{selected_feeder}-{selected_dtr}_wrongly_mapped.csv",
        mime="text/csv"
    )

st.markdown("""
    <div style='text-align:center;margin-top:24px;font-size:17px;color:#7f8c8d;'>
        🚀 <b>Power Analytics Dashboard</b> | <i>Sheet-driven, Business-defined KPIs</i>
    </div>
""", unsafe_allow_html=True)
