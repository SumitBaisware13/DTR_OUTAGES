import pandas as pd

# File names
files = ['Master_7088.xlsx', '7088-57.xlsx']

for fname in files:
    print(f"\n==== File: {fname} ====")
    xl = pd.ExcelFile(fname)
    print("Sheets Found:", xl.sheet_names)
