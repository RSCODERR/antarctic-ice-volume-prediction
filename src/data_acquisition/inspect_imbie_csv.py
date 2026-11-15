import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
IMBIE_DIR = os.path.join(BASE_DIR, "data", "raw", "imbie")

f1 = os.path.join(IMBIE_DIR, "imbie3_antarctic_peninsula_Gt_partitioned.csv")
f2 = os.path.join(IMBIE_DIR, "imbie_antarctic_peninsula_2021_Gt.csv")

print("--- IMBIE 2023 (Otosaka et al., 2023) ---")
df1 = pd.read_csv(f1)
print(f"Shape: {df1.shape}")
print(f"Columns: {list(df1.columns)}")
print(df1.head(5))
print(df1.tail(5))

print("\n--- IMBIE 2021 (IPCC AR6) ---")
df2 = pd.read_csv(f2)
print(f"Shape: {df2.shape}")
print(f"Columns: {list(df2.columns)}")
print(df2.head(5))
print(df2.tail(5))

