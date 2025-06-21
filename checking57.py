import pandas as pd

# ---- LOAD DATA FROM CORRECT SHEETS ----
master = pd.read_excel('Master_7088.xlsx', sheet_name='Sheet1')
outage = pd.read_excel('7088-57.xlsx', sheet_name='outage_154')

dtr_code = 57
feeder_code = 7088

# ---- CLEAN METER SERIALS ----
master['Meter_Serial_Number'] = master['Meter_Serial_Number'].astype(str).str.strip().str.upper()
outage['msn'] = outage['msn'].astype(str).str.strip().str.upper()

# --- FILTER master for selected DTR and Feeder ---
master_dtr = master[(master['dtrcode'] == dtr_code) & (master['Feedercode'] == feeder_code)]
outage_meters = set(outage['msn'])
master_meters = set(master_dtr['Meter_Serial_Number'])

# Master mein aur kaunse DTR hain feeder 7088 mein?
print("All DTRs in feeder 7088:", master[master['Feedercode'] == 7088]['dtrcode'].unique())

# Outage file ke meters jo master ke DTR 57 ke alawa hain (same feeder)
other_dtr_meters = master[
   (master['Feedercode'] == 7088) & (master['dtrcode'] != 57)
]['Meter_Serial_Number'].unique()
wrongly_mapped = outage_meters & set(other_dtr_meters)
print("Wrongly mapped:", wrongly_mapped)
print("Wrongly mapped count:", len(wrongly_mapped))

# Master mein jo outage mein nahi hain
untagged = set(master_dtr['Meter_Serial_Number']) - outage_meters
print("Untagged:", untagged)
print("Untagged count:", len(untagged))

# Master tagged + outage
correctly_tagged = set(master_dtr['Meter_Serial_Number']) & outage_meters
print("Correctly tagged:", correctly_tagged)
print("Correctly tagged count:", len(correctly_tagged))

# All in outage file (live connections)
print("All live connections (outage file):", len(outage_meters))

# Total after correction (KPI 2 + KPI 4)
total_corrected = len(correctly_tagged) + len(wrongly_mapped)
print("Total after correction:", total_corrected)
