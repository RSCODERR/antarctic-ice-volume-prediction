import os
import geopandas as gpd
import pandas as pd
import numpy as np
import rasterio
from rasterio.mask import mask as rmask

BASE_DIR = os.path.abspath('antarctic-ice-volume-prediction')
IMBIE_SHP = os.path.join(BASE_DIR, 'data', 'raw', 'imbie_basins', 'IMBIE_AIS_Regional_Delineations', 'IMBIE_AIS_Regional_Delineations.shp')
BM3_MASK = os.path.join(BASE_DIR, 'data', 'processed', 'bedmap3_masks_peninsula_500m.tif')
BM3_THICK = os.path.join(BASE_DIR, 'data', 'processed', 'bedmap3_thickness_peninsula_500m.tif')

gdf = gpd.read_file(IMBIE_SHP)

print("=== RAW VECTOR POLYGON AREAS (EPSG:3031) ===")
pen_ice = gdf[(gdf['Region'] == 'Peninsula') & (gdf['Type'] == 'Ice_sheet')].copy()
for _, r in pen_ice.iterrows():
    raw_area = r.geometry.area / 1e6
    print(f"Basin {r['Basin']:6s}: Raw Vector Area = {raw_area:10.2f} km2")
print(f"Total Peninsula Ice_sheet Vector Area = {pen_ice.geometry.area.sum() / 1e6:10.2f} km2")

print("\n=== PHASE 2.6 COMMON GROUNDED RASTER DOMAIN ===")
# Let's inspect common_domain_comparison.csv
df_common = pd.read_csv(os.path.join(BASE_DIR, 'reports', 'tables', 'common_domain_comparison.csv'))
print(df_common[['Basin', 'Common_Cells', 'Common_Area_km2']].to_string())

print("\n=== DIFFERENCE BREAKDOWN ===")
for _, r in pen_ice.iterrows():
    b = r['Basin']
    vec_area = r.geometry.area / 1e6
    c_row = df_common[df_common['Basin'] == b]
    if len(c_row) > 0:
        com_area = c_row['Common_Area_km2'].iloc[0]
        diff = vec_area - com_area
        pct_non_grounded = (diff / vec_area) * 100.0
        print(f"Basin {b:6s}: Vector={vec_area:9.2f} km2 | Grounded Raster={com_area:9.2f} km2 | Diff (Rock/Ocean/Shelf)={diff:8.2f} km2 ({pct_non_grounded:5.2f}%)")

tot_vec = pen_ice.geometry.area.sum() / 1e6
tot_com = df_common[df_common['Basin'] == 'Peninsula Total']['Common_Area_km2'].iloc[0]
tot_diff = tot_vec - tot_com
print(f"Total  : Vector={tot_vec:9.2f} km2 | Grounded Raster={tot_com:9.2f} km2 | Diff={tot_diff:8.2f} km2 ({(tot_diff/tot_vec)*100:5.2f}%)")

