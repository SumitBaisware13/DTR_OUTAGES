import streamlit as st
import pandas as pd
import plotly.graph_objs as go

@st.cache_data
def load_data():
    files = {
        '7088': {
            'master': pd.read_excel('Master_7088.xlsx'),
            '57': pd.read_excel('7088-57.xlsx'),
            '32': pd.read_excel('7088-32.xlsx'),
            '86': pd.read_excel('7088-86.xlsx'),
        },
        '15631': {
            'master': pd.read_excel('Master_Feeder_15631.xlsx'),
            '34': pd.read_excel('15631-34.xlsx')
        }
    }
    return files

files = load_data()

# ---- SIDEBAR FILTERS ----
st.sidebar.title("🔌 Power Feeder/DTR Dashboard")
feeder = st.sidebar.selectbox("Select Feeder", list(files.keys()), help="Pick a Feeder")
dtr_options = [d for d in files[feeder].keys() if d != "master"]
dtr_code = st.sidebar.selectbox("Select DTR", dtr_options, help="Pick a DTR")

master = files[feeder]['master']
dtr_data = files[feeder][dtr_code]

# --- Data Preparation ---
# For DTR, filter master and get outage data
master_dtr = master[master['dtrcode'] == int(dtr_code)]
meters_master = set(master_dtr['Meter_Serial_Number'])
meters_outage = set(dtr_data['Meter_Serial_Number'])

# KPIs
currently_connected = dtr_data  # All meters in outage file
correctly_tagged = dtr_data[dtr_data['Meter_Serial_Number'].isin(meters_master)]
not_mapped = dtr_data[~dtr_data['Meter_Serial_Number'].isin(meters_master)]
total_tagged = master_dtr.shape[0]
loss_pct = ((total_tagged - correctly_tagged.shape[0]) / total_tagged) * 100 if total_tagged > 0 else 0

# ---- PAGE TITLE ----
st.markdown(
    """
    <h1 style='color:#1570ef'>DTR Live Outage & Tagging Dashboard</h1>
    <h3 style='font-weight:normal;color:#666'>Visualize "Currently Connected" customers using live outage data, see mapping quality, and download detailed lists.<br>
    <span style='font-size:16px;color:#2980b9'><b>Feeder:</b> {}</span> | 
    <span style='font-size:16px;color:#27ae60'><b>DTR:</b> {}</span></h3>
    """.format(feeder, dtr_code), unsafe_allow_html=True
)

# ---- KPI CARDS ----
st.markdown("### ⚡️ Live KPIs from Outage Data")
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("🟢 Currently Connected", currently_connected.shape[0], help="Customers in outage (live) data for this DTR")
c2.metric("✅ Correctly Tagged", correctly_tagged.shape[0], help="Outage customers matched in master for this DTR")
c3.metric("🚫 Not Mapped", not_mapped.shape[0], help="Outage customers NOT found in master for this DTR")
c4.metric("🏷️ Total Tagged (Master)", total_tagged, help="All meters tagged to this DTR in master data")
c5.metric("⚠️ Loss %", f"{loss_pct:.2f}%", help="Proportion of master-tagged customers not found live")

# ---- PIE CHART ----
pie_labels = [
    "Currently Connected (Outage)", 
    "Correctly Tagged", 
    "Not Mapped (Outage Not in Master)", 
    "Total Tagged (Master)"
]
pie_values = [
    currently_connected.shape[0], 
    correctly_tagged.shape[0], 
    not_mapped.shape[0], 
    total_tagged
]
pie_colors = ['#00b894', '#0984e3', '#d63031', '#e67e22']
fig_pie = go.Figure(
    data=[go.Pie(
        labels=pie_labels, 
        values=pie_values, 
        hole=.5, 
        marker_colors=pie_colors, 
        pull=[0.03, 0.05, 0.07, 0]
    )]
)
fig_pie.update_traces(
    textinfo='label+value+percent', 
    textfont_size=14,
    marker=dict(line=dict(color='#fff', width=2))
)
fig_pie.update_layout(
    title="Live Customer Connection & Tagging Breakdown",
    legend_title_text='Category'
)
st.plotly_chart(fig_pie, use_container_width=True)

# ---- BAR CHART ----
fig_bar = go.Figure(data=[
    go.Bar(
        x=pie_labels, 
        y=pie_values, 
        marker_color=pie_colors, 
        text=pie_values, 
        textposition='outside'
    )
])
fig_bar.update_layout(
    title="Customer Counts by Category",
    yaxis_title="Count",
    xaxis_title="Category",
    bargap=0.5
)
st.plotly_chart(fig_bar, use_container_width=True)

# ---- SECTION TITLE ----
st.markdown("### 👁️‍🗨️ View and Download Customer Details")
table_type = st.radio(
    "Select table to view below:",
    (
        "Currently Connected (Outage)", 
        "Correctly Tagged", 
        "Not Mapped (Outage Not in Master)"
    )
)

if table_type == "Currently Connected (Outage)":
    table_df = currently_connected
elif table_type == "Correctly Tagged":
    table_df = correctly_tagged
else:
    table_df = not_mapped

st.dataframe(table_df, use_container_width=True)

# ---- DOWNLOAD BUTTON ----
st.download_button(
    "⬇️ Download Table as CSV",
    data=table_df.to_csv(index=False),
    file_name=f'{feeder}_DTR_{dtr_code}_{table_type.replace(" ", "_")}.csv',
    mime='text/csv'
)

st.markdown(
    "<hr><div style='text-align:center;font-size:18px;color:#555;'>Designed for real-time DTR/Feeder analytics | 🚀 Built by Esyasoft</div>", 
    unsafe_allow_html=True
)
