import os, hashlib, geopandas as gpd

base = 'c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction'
path = os.path.join(base, 'data/raw/imbie_basins/IMBIE_AIS_Regional_Delineations/IMBIE_AIS_Regional_Delineations.shp')
print(f"Path: {path}, Exists: {os.path.exists(path)}")
if os.path.exists(path):
    h = hashlib.sha256(open(path, 'rb').read()).hexdigest()
    sz = os.path.getsize(path)
    print(f"SHA256: {h}, Size: {sz}")
    gdf = gpd.read_file(path)
    print("CRS:", gdf.crs)
    print("Features:", len(gdf))
    print("Columns:", list(gdf.columns))
    print("Basin values:", gdf['Basin'].tolist() if 'Basin' in gdf.columns else gdf.head())
