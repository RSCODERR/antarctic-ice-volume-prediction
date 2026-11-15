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

scale, lats, lons = compute_scale_factor_grid(trans, h, w)
true_area = 0.25 / scale

gdf = gpd.read_file(IMBIE_SHP)
pen = gdf[(gdf["Region"] == "Peninsula") & (gdf["Type"] == "Ice_sheet")]

bm3_gr = (bm3_m == 1) & (bm3_t > 0) & (bm3_t != -9999)
bm_gr = (bm_m == 2) & (bm_t > 0) & (bm_t != -9999)

dom_a = np.zeros((h, w), dtype=bool)
for _, row in pen.iterrows():
    with rasterio.open(BM3_MASK) as src:
        masked, _ = rmask(src, [row.geometry], crop=False, all_touched=False, nodata=-9999)
        dom_a |= ((masked[0] == 1) & bm3_gr & bm_gr)

# 500m volumes
v500_proj = float(np.sum(bm_t[dom_a])) * 0.25 * 1e6 / 1e9
v500_ellip = float(np.sum(bm_t[dom_a] * true_area[dom_a])) * 1e6 / 1e9

# Pad to even
h_pad = h if h % 2 == 0 else h + 1
w_pad = w if w % 2 == 0 else w + 1

dom_pad = np.zeros((h_pad, w_pad), dtype=bool)
dom_pad[:h, :w] = dom_a

thick_pad = np.zeros((h_pad, w_pad), dtype=np.float64)
thick_pad[:h, :w] = np.where(dom_a, bm_t, 0.0)

area_pad = np.zeros((h_pad, w_pad), dtype=np.float64)
area_pad[:h, :w] = np.where(dom_a, true_area, 0.0)

b_dom = dom_pad.reshape(h_pad // 2, 2, w_pad // 2, 2)
b_thick = thick_pad.reshape(h_pad // 2, 2, w_pad // 2, 2)
b_area = area_pad.reshape(h_pad // 2, 2, w_pad // 2, 2)

subcell_k = b_dom.sum(axis=(1, 3))
thick_sum = b_thick.sum(axis=(1, 3))
vol_ellip_sum = (b_thick * b_area).sum(axis=(1, 3))

# 1km macro-element exact summation
v1km_macro_proj = float(np.sum(thick_sum)) * 0.25 * 1e6 / 1e9
v1km_macro_ellip = float(np.sum(vol_ellip_sum)) * 1e6 / 1e9

print(f"500m Projected:      {v500_proj:,.4f} km3")
print(f"1km Macro Projected: {v1km_macro_proj:,.4f} km3 (Error: {v1km_macro_proj - v500_proj:+.6f} km3)")
print(f"500m Ellipsoidal:    {v500_ellip:,.4f} km3")
print(f"1km Macro Ellip:     {v1km_macro_ellip:,.4f} km3 (Error: {v1km_macro_ellip - v500_ellip:+.6f} km3)")

