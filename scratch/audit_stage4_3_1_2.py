import os, sys
sys.path.insert(0, os.path.abspath("."))

import numpy as np
import rasterio
from rasterio.mask import mask as rmask
import netCDF4 as nc
import geopandas as gpd

from src.geospatial.audit_distortion import compute_scale_factor_grid

BM3_MASK = "data/processed/bedmap3_masks_peninsula_500m.tif"
BM3_THICK = "data/processed/bedmap3_thickness_peninsula_500m.tif"
ALIGNED_NC = "data/processed/bedmachine_v4.1_peninsula_aligned_to_bedmap3.nc"
IMBIE_SHP = "data/raw/imbie_basins/IMBIE_AIS_Regional_Delineations/IMBIE_AIS_Regional_Delineations.shp"

with rasterio.open(BM3_MASK) as src:
    bm3_m = src.read(1)
    trans = src.transform
    h, w = src.shape

with rasterio.open(BM3_THICK) as src:
    bm3_t = src.read(1)

ds = nc.Dataset(ALIGNED_NC)
bm_m = ds.variables["mask"][:]
bm_t = ds.variables["thickness"][:]
bm_f = ds.variables["firn"][:]
bm_s = ds.variables["surface"][:]
bm_b = ds.variables["bed"][:]

scale, lats, lons = compute_scale_factor_grid(trans, h, w)
true_area = 0.25 / scale

gdf = gpd.read_file(IMBIE_SHP)
pen = gdf[(gdf["Region"] == "Peninsula") & (gdf["Type"] == "Ice_sheet")]

bm3_gr = (bm3_m == 1) & (bm3_t > 0) & (bm3_t != -9999)
bm_gr = (bm_m == 2) & (bm_t > 0) & (bm_t != -9999)

dom_a = np.zeros((h, w), dtype=bool)
basin_masks = {}
for _, row in pen.iterrows():
    b_name = row["Basin"]
    with rasterio.open(BM3_MASK) as src:
        masked, _ = rmask(src, [row.geometry], crop=False, all_touched=False, nodata=-9999)
        basin_masks[b_name] = ((masked[0] == 1) & bm3_gr & bm_gr)
        dom_a |= basin_masks[b_name]

print("Domain A cell count:", int(np.sum(dom_a)))

# 1. Projected Volume
v_proj = float(np.sum(bm_t[dom_a])) * 0.25 * 1e6 / 1e9

# 2. Ellipsoidal Volume
v_ellip = float(np.sum(bm_t[dom_a] * true_area[dom_a])) * 1e6 / 1e9

print(f"Projected Volume (H * 0.25 km2):    {v_proj:,.4f} km3")
print(f"Ellipsoidal Volume (H * A_true):   {v_ellip:,.4f} km3")
print(f"Difference (v_ellip - v_proj):     {v_ellip - v_proj:+,.4f} km3")
print(f"Approved BM4 baseline:             140,702.5100 km3")
print(f"Discrepancy (v_ellip - 140702.51): {v_ellip - 140702.51:+,.4f} km3")
print(f"Discrepancy (v_proj - 140702.51):  {v_proj - 140702.51:+,.4f} km3")

for b_name in ["Hp-I", "I-Ipp", "Ipp-J"]:
    m = basin_masks[b_name]
    vp = float(np.sum(bm_t[m])) * 0.25 * 1e6 / 1e9
    ve = float(np.sum(bm_t[m] * true_area[m])) * 1e6 / 1e9
    print(f"Basin {b_name}: Projected Vol = {vp:,.2f} km3, Ellipsoidal Vol = {ve:,.2f} km3, Delta = {ve - vp:+,.2f} km3")

