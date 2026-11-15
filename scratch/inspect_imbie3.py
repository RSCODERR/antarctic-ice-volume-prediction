import pandas as pd

df = pd.read_csv("antarctic-ice-volume-prediction/data/raw/imbie/imbie3_antarctic_peninsula_Gt_partitioned.csv", comment="#")
print("Date min and max:", df["Date"].min(), df["Date"].max())
df["Year"] = pd.to_datetime(df["Date"]).dt.year
print("\nAnnual mass balance around 2010-2020:")
ann = df.groupby("Year")[["Mass balance (Gt/yr)", "Surface mass balance anomaly (Gt/yr)", "Dynamics mass balance anomaly (Gt/yr)"]].mean()
print(ann.loc[2010:2020])
