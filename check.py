import pandas as pd

files = [
    "Master_7088.xlsx",
    "Master_Feeder_15631.xlsx",
    "7088-57.xlsx",
    "7088-32.xlsx",
    "7088-86.xlsx",
    "15631-34.xlsx"
]

for fname in files:
    print(f"\n==== File: {fname} ====")
    try:
        xl = pd.ExcelFile(fname)
        print("Sheets Found:", xl.sheet_names)
    except Exception as e:
        print(f"  Error opening file: {e}")
