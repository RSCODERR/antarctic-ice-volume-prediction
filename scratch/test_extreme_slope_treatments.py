import os, sys
sys.path.insert(0, os.path.abspath("."))

import numpy as np
import netCDF4 as nc
import rasterio
from rasterio.mask import mask as rmask
from scipy.ndimage import gaussian_filter
import geopandas as gpd

BM3_MASK = "data/processed/bedmap3_masks_peninsula_500m.tif"
BM3_THICK = "data/processed/bedmap3_thickness_peninsula_500m.tif"
ALIGNED_NC = "data/processed/bedmachine_v4.1_peninsula_aligned_to_bedmap3.nc"
IMBIE_SHP = "data/raw/imbie_basins/IMBIE_AIS_Regional_Delineations/IMBIE_AIS_Regional_Delineations.shp"

with rasterio.open(BM3_MASK) as src:
    bm3_m = src.read(1)
with rasterio.open(BM3_THICK) as src:
    bm3_t = src.read(1)

ds = nc.Dataset(ALIGNED_NC)
bm_m = ds.variables["mask"][:]
bm_t = ds.variables["thickness"][:]
bm_s = ds.variables["surface"][:]

gdf = gpd.read_file(IMBIE_SHP)
pen = gdf[(gdf["Region"] == "Peninsula") & (gdf["Type"] == "Ice_sheet")]

bm3_gr = (bm3_m == 1) & (bm3_t > 0) & (bm3_t != -9999)
bm_gr = (bm_m == 2) & (bm_t > 0) & (bm_t != -9999)

dom_a = np.zeros(bm3_m.shape, dtype=bool)
for _, row in pen.iterrows():
    with rasterio.open(BM3_MASK) as src:
        masked, _ = rmask(src, [row.geometry], crop=False, all_touched=False, nodata=-9999)
        dom_a |= ((masked[0] == 1) & bm3_gr & bm_gr)

# Raw 500m gradients
ds_dy, ds_dx = np.gradient(bm_s, 500.0, 500.0)
grad_s_raw = np.sqrt(ds_dx**2 + ds_dy**2)
tau_raw = 917.0 * 9.81 * bm_t * grad_s_raw / 1000.0
tau_dom_raw = tau_raw[dom_a]

print("=== RAW DIAGNOSTIC (PRESERVED) ===")
print(f"Max:    {np.max(tau_dom_raw):.2f} kPa")
print(f"P95:    {np.percentile(tau_dom_raw, 95):.2f} kPa")
print(f"Mean:   {np.mean(tau_dom_raw):.2f} kPa")
print(f"Median: {np.median(tau_dom_raw):.2f} kPa")

# Treatment 1: Exact Trigonometric Slope Projection (sin(theta) = grad / sqrt(1 + grad^2))
grad_s_trig = grad_s_raw / np.sqrt(1.0 + grad_s_raw**2)
tau_trig = 917.0 * 9.81 * bm_t * grad_s_trig / 1000.0
tau_dom_trig = tau_trig[dom_a]
print("\n=== TREATMENT 1: EXACT TRIGONOMETRIC SLOPE PROJECTION ===")
print(f"Formula: grad_eff = grad / sqrt(1 + grad^2)")
print(f"Max:    {np.max(tau_dom_trig):.2f} kPa (at same peak cell: {tau_trig[1774, 721]:.2f} kPa)")
print(f"P95:    {np.percentile(tau_dom_trig, 95):.2f} kPa")
print(f"Mean:   {np.mean(tau_dom_trig):.2f} kPa")
print(f"Median: {np.median(tau_dom_trig):.2f} kPa")

# Treatment 2: Physical Longitudinal Stress Coupling Scale (Kamb & Echelmeyer, 1986)
# Smoothing surface elevation over characteristic membrane coupling length L = 4*H (sigma ~ 1 km or 2 cells)
s_smooth_1km = gaussian_filter(bm_s, sigma=2.0) # sigma=2 cells = 1.0 km (window ~ 4-6 km)
ds_dy_sm, ds_dx_sm = np.gradient(s_smooth_1km, 500.0, 500.0)
grad_s_sm = np.sqrt(ds_dx_sm**2 + ds_dy_sm**2)
tau_sm = 917.0 * 9.81 * bm_t * grad_s_sm / 1000.0
tau_dom_sm = tau_sm[dom_a]
print("\n=== TREATMENT 2: LONGITUDINAL STRESS COUPLING SCALE (Kamb & Echelmeyer 1986, sigma=1.0 km) ===")
print(f"Max:    {np.max(tau_dom_sm):.2f} kPa (at Row 1774, Col 721: {tau_sm[1774, 721]:.2f} kPa)")
print(f"P95:    {np.percentile(tau_dom_sm, 95):.2f} kPa")
print(f"Mean:   {np.mean(tau_dom_sm):.2f} kPa")
print(f"Median: {np.median(tau_dom_sm):.2f} kPa")

# Treatment 3: Combined Physically Consistent Formulation (Trigonometric + Longitudinal Coupling)
grad_s_comb = grad_s_sm / np.sqrt(1.0 + grad_s_sm**2)
tau_comb = 917.0 * 9.81 * bm_t * grad_s_comb / 1000.0
tau_dom_comb = tau_comb[dom_a]
print("\n=== TREATMENT 3: COMBINED PHYSICAL FORMULATION (Trigonometric + Longitudinal Coupling) ===")
print(f"Max:    {np.max(tau_dom_comb):.2f} kPa (at Row 1774, Col 721: {tau_comb[1774, 721]:.2f} kPa)")
print(f"P95:    {np.percentile(tau_dom_comb, 95):.2f} kPa")
print(f"Mean:   {np.mean(tau_dom_comb):.2f} kPa")
print(f"Median: {np.median(tau_dom_comb):.2f} kPa")

