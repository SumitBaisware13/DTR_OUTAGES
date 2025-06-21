import streamlit as st
import pandas as pd
import plotly.graph_objs as go

# ---- LOAD DATA ----
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
st.sidebar.title("DTR KPI Dashboard")
feeder = st.sidebar.selectbox("Select Feeder", options=list(files.keys()))
dtr_options = [d for d in files[feeder].keys() if d != "master"]
dtr_code = st.sidebar.selectbox("Select DTR", options=dtr_options)

master = files[feeder]['master']
dtr_data = files[feeder][dtr_code]

# ---- FILTER MASTER FOR THIS DTR ----
master_dtr = master[master['dtrcode'] == int(dtr_code)]
feeder_customers = set(master['Meter_Serial_Number'])
dtr_customers_master = set(master_dtr['Meter_Serial_Number'])
dtr_customers_outage = set(dtr_data['Meter_Serial_Number'])

# ---- KPI LOGIC ----
correctly_tagged = dtr_customers_outage & dtr_customers_master
not_mapped = dtr_customers_outage - dtr_customers_master
other_feeder_customers = feeder_customers - dtr_customers_master
total_tagged = len(dtr_customers_master)

# ---- KPI CARDS ----
st.markdown("## KPIs for Selected Feeder & DTR")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Correctly Tagged", len(correctly_tagged))
kpi2.metric("Not Mapped (in Outage)", len(not_mapped))
kpi3.metric("Other Feeder Customers", len(other_feeder_customers))
kpi4.metric("Total Tagged to DTR (Master)", total_tagged)

# ---- PLOTLY CHART ----
fig = go.Figure(data=[
    go.Bar(name='Count', x=[
        "Correctly Tagged", "Not Mapped", "Other Feeder Customers", "Total Tagged"
    ], y=[
        len(correctly_tagged), len(not_mapped), len(other_feeder_customers), total_tagged
    ], marker_color=['green', 'red', 'blue', 'orange'])
])
fig.update_layout(title="KPI Overview", showlegend=False)
st.plotly_chart(fig, use_container_width=True)

# ---- DETAIL TABLES ----
st.markdown("### Detailed Customer Lists")

detail_type = st.radio(
    "Show table for:",
    ("Correctly Tagged", "Not Mapped (in Outage)", "Other Feeder Customers")
)

if detail_type == "Correctly Tagged":
    detail_df = dtr_data[dtr_data['Meter_Serial_Number'].isin(correctly_tagged)]
elif detail_type == "Not Mapped (in Outage)":
    detail_df = dtr_data[dtr_data['Meter_Serial_Number'].isin(not_mapped)]
else:
    detail_df = master[master['Meter_Serial_Number'].isin(other_feeder_customers)]

st.dataframe(detail_df, use_container_width=True)

# ---- DOWNLOAD BUTTON ----
def to_excel(df):
    return df.to_excel(index=False, engine='openpyxl')

st.download_button(
    "Download Table as Excel",
    data=detail_df.to_csv(index=False),
    file_name=f'{feeder}_DTR_{dtr_code}_{detail_type.replace(" ", "_")}.csv',
    mime='text/csv'
)

st.caption("© Your Company | Powered by Streamlit + Plotly")

