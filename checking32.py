

import pandas as pd
import plotly.graph_objs as go


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


# Master mein aur kaunse DTR hain feeder 7088 mein?
print(master[master['Feedercode'] == 7088]['dtrcode'].unique())

# Outage file ke meters jo master ke DTR 32 ke alawa hain
other_dtr_meters = master[
   (master['Feedercode'] == 7088) & (master['dtrcode'] != 32)
]['Meter_Serial_Number'].unique()
wrongly_mapped = set(outage['Meter_Serial_Number']) & set(other_dtr_meters)
print("Wrongly mapped:", wrongly_mapped)

# Master mein jo outage mein nahi hain
untagged = set(master_dtr['Meter_Serial_Number']) - set(outage['Meter_Serial_Number'])
print("Untagged:", untagged)
