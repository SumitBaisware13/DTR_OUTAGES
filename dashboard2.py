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

# ---- SIDEBAR ----
st.sidebar.title("🔌 DTR KPI Analytics Dashboard")
feeder = st.sidebar.selectbox("Select Feeder", options=list(files.keys()), help="Choose the Feeder to analyze")
dtr_options = [d for d in files[feeder].keys() if d != "master"]
dtr_code = st.sidebar.selectbox("Select DTR", options=dtr_options, help="Choose DTR on this feeder")

master = files[feeder]['master']
dtr_data = files[feeder][dtr_code]
master_dtr = master[master['dtrcode'] == int(dtr_code)]
feeder_customers = set(master['Meter_Serial_Number'])
dtr_customers_master = set(master_dtr['Meter_Serial_Number'])
dtr_customers_outage = set(dtr_data['Meter_Serial_Number'])

# ---- KPI LOGIC ----
correctly_tagged = dtr_customers_outage & dtr_customers_master
not_mapped = dtr_customers_outage - dtr_customers_master
other_feeder_customers = feeder_customers - dtr_customers_master
currently_connected = dtr_customers_outage & dtr_customers_master  # same as correctly_tagged with current data

total_tagged = len(dtr_customers_master)
loss_pct = (1 - len(correctly_tagged)/total_tagged)*100 if total_tagged > 0 else 0

# ---- TITLE & SUBTITLE ----
st.title("📊 DTR & Feeder Customer Tagging Analysis")
st.caption(f"Analyze consumer mapping quality for Feeder **{feeder}** and DTR **{dtr_code}**. Visualize mapping KPIs, customer breakdown, and export details for action.")

# ---- KPI CARDS ----
st.markdown("### Key Performance Indicators")
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("✔️ Correctly Tagged", len(correctly_tagged), help="Meters tagged to this DTR in both master and current outage data")
col2.metric("❌ Not Mapped", len(not_mapped), help="Meters in outage, but not found in master tagging for this DTR")
col3.metric("🔄 Currently Connected", len(currently_connected), help="Meters in both master & live on DTR now")
col4.metric("📦 Other Feeder Customers", len(other_feeder_customers), help="Meters on same feeder, not tagged to this DTR")
col5.metric("🏷️ Total Tagged (Master)", total_tagged, help="All meters tagged to this DTR as per master list")

st.markdown(f"**Estimated Loss %:** <span style='color:red;font-size:1.2em'>{loss_pct:.2f}%</span>", unsafe_allow_html=True)

# ---- PIE CHART ----
pie_labels = ["Correctly Tagged", "Not Mapped", "Currently Connected", "Other Feeder Customers"]
pie_values = [len(correctly_tagged), len(not_mapped), len(currently_connected), len(other_feeder_customers)]
fig_pie = go.Figure(data=[go.Pie(labels=pie_labels, values=pie_values, hole=.4)])
fig_pie.update_traces(textinfo='label+percent', pull=[0.08,0.08,0.08,0], marker=dict(line=dict(color='#000', width=2)))
fig_pie.update_layout(title="Customer Tagging Breakdown")
st.plotly_chart(fig_pie, use_container_width=True)

# ---- BAR CHART ----
fig_bar = go.Figure(data=[
    go.Bar(x=pie_labels, y=pie_values, marker_color=['#2ecc71', '#e74c3c', '#3498db', '#e67e22'],
           text=pie_values, textposition='outside')
])
fig_bar.update_layout(title="Customer Counts by Category", yaxis_title="Count", xaxis_title="Customer Type")
st.plotly_chart(fig_bar, use_container_width=True)

# ---- LOSS INFO CARD ----
st.info(f"**Loss %** shows potential mismatch in consumer tagging between master and outage data for this DTR. High value indicates need for data cleansing or field verification.", icon="ℹ️")

# ---- DETAIL TABLES ----
st.markdown("### 🔍 Detailed Customer Table & Download")
detail_type = st.radio(
    "Choose Detail Table:",
    ("Correctly Tagged", "Not Mapped", "Currently Connected", "Other Feeder Customers")
)

if detail_type == "Correctly Tagged":
    detail_df = dtr_data[dtr_data['Meter_Serial_Number'].isin(correctly_tagged)]
elif detail_type == "Not Mapped":
    detail_df = dtr_data[dtr_data['Meter_Serial_Number'].isin(not_mapped)]
elif detail_type == "Currently Connected":
    detail_df = master_dtr[master_dtr['Meter_Serial_Number'].isin(currently_connected)]
else:
    detail_df = master[master['Meter_Serial_Number'].isin(other_feeder_customers)]

st.dataframe(detail_df, use_container_width=True)

# ---- DOWNLOAD BUTTON ----
st.download_button(
    "⬇️ Download This Table as CSV",
    data=detail_df.to_csv(index=False),
    file_name=f'{feeder}_DTR_{dtr_code}_{detail_type.replace(" ", "_")}.csv',
    mime='text/csv'
)

st.caption("Designed for Power Distribution Data Analytics | © Your Organization")

