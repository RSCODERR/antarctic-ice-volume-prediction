import os
import zipfile
import io
import requests
import geopandas as gpd

raw_dir = "antarctic-ice-volume-prediction/data/raw/imbie_basins"
os.makedirs(raw_dir, exist_ok=True)

zip_path = os.path.join(raw_dir, "IMBIE_AIS_Regional_Delineations.zip")
url = "https://imbie.org/wp-content/uploads/2026/10/IMBIE_AIS_Regional_Delineations.zip"

if not os.path.exists(zip_path):
    print("Downloading IMBIE Regional Delineations...")
    r = requests.get(url, timeout=30)
    with open(zip_path, "wb") as f:
        f.write(r.content)
    print("Saved zip to:", zip_path)

with zipfile.ZipFile(zip_path, "r") as zf:
    zf.extractall(raw_dir)
print("Extracted files to:", raw_dir)

# Read README.txt if present
readme_path = os.path.join(raw_dir, "IMBIE_AIS_Regional_Delineations", "README.txt")
if os.path.exists(readme_path):
    print("\n--- README.txt ---")
    with open(readme_path, "r", encoding="utf-8", errors="ignore") as f:
        print(f.read())

# Read Shapefile with GeoPandas
shp_path = os.path.join(raw_dir, "IMBIE_AIS_Regional_Delineations", "IMBIE_AIS_Regional_Delineations.shp")
if os.path.exists(shp_path):
    gdf = gpd.read_file(shp_path)
    print("\n--- Shapefile Summary ---")
    print("CRS:", gdf.crs)
    print("Columns:", gdf.columns.tolist())
    print("Number of features:", len(gdf))
    print("\nAttribute Table:")
    for idx, row in gdf.iterrows():
        print(f"Index {idx}: {dict(row.drop('geometry'))}")

