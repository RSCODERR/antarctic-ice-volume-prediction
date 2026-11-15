"""
Test script for Stage 4.5.2 pipeline components.
"""
import netCDF4 as nc
import numpy as np
import geopandas as gpd
from shapely.geometry import box
import pyproj
from scipy.interpolate import RegularGridInterpolator, griddata
import rasterio

# 1. Inspect Aligned BedMachine grid & Domain A mask
ALIGNED_NC = "data/processed/bedmachine_v4.1_peninsula_aligned_to_bedmap3.nc"
BM3_MASK = "data/processed/bedmap3_masks_peninsula_500m.tif"
BM3_THICK = "data/processed/bedmap3_thickness_peninsula_500m.tif"
IMBIE_SHP = "data/raw/imbie_basins/IMBIE_AIS_Regional_Delineations/IMBIE_AIS_Regional_Delineations.shp"

ds_bm = nc.Dataset(ALIGNED_NC)
x_500 = ds_bm.variables["x"][:] # 2600
y_500 = ds_bm.variables["y"][:] # 3400
bm_mask = ds_bm.variables["mask"][:]
bm_thick = ds_bm.variables["thickness"][:]
bm_surf = ds_bm.variables["surface"][:]
bm_bed = ds_bm.variables["bed"][:]

with rasterio.open(BM3_MASK) as src_m:
    bm3_mask = src_m.read(1)
with rasterio.open(BM3_THICK) as src_t:
    bm3_thick = src_t.read(1)

# Domain A mask
bm3_gr = (bm3_mask == 1) & (bm3_thick > 0) & (bm3_thick != -9999)
bm_gr = (bm_mask == 2) & (bm_thick > 0) & (bm_thick != -9999)

gdf_imbie = gpd.read_file(IMBIE_SHP)
pen_basins = gdf_imbie[(gdf_imbie["Region"] == "Peninsula") & (gdf_imbie["Type"] == "Ice_sheet")]

from rasterio.mask import mask as rmask
basin_masks = {}
for _, row in pen_basins.iterrows():
    b_name = row["Basin"]
    with rasterio.open(BM3_MASK) as src:
        m_masked, _ = rmask(src, [row["geometry"]], crop=False, all_touched=False, nodata=-9999)
        basin_masks[b_name] = (m_masked[0] == 1)

dom_a_masks = {b_name: basin_masks[b_name] & bm3_gr & bm_gr for b_name in basin_masks}
dom_a_total = np.zeros((3400, 2600), dtype=bool)
for m in dom_a_masks.values():
    dom_a_total |= m

print(f"Domain A 500m cells: {np.sum(dom_a_total)} (Expected: 866,358)")

# 1 km macro-mesh coordinates
x_1km = x_500.reshape(-1, 2).mean(axis=1) # 1300
y_1km = y_500.reshape(-1, 2).mean(axis=1) # 1700
# 1 km Domain A area fraction alpha
dom_a_1km_fraction = dom_a_total.reshape(1700, 2, 1300, 2).mean(axis=(1, 3))
print(f"1 km macro-mesh cells with alpha > 0: {np.sum(dom_a_1km_fraction > 0)}")
print(f"1 km integrated area (sum alpha * 1.0 km2): {np.sum(dom_a_1km_fraction):.2f} km2 (500m projected: {866358*0.25:.2f} km2)")

# 2. Test Grounding Line clip to Peninsula
gdf_gl = gpd.read_file("data/raw/measures_gl/InSAR_GL_Antarctica_v02.1.gpkg")
pen_box = box(-2700000, 250000, -1400000, 1950000)
gdf_gl_pen = gdf_gl[gdf_gl.intersects(pen_box)].copy()
gdf_gl_pen["pen_geom"] = gdf_gl_pen.intersection(pen_box)
print(f"\nGrounding line features intersecting Peninsula: {len(gdf_gl_pen)} / {len(gdf_gl)}")
print("Peninsula GL breakdown by Year:")
for yr, grp in gdf_gl_pen.groupby("Year"):
    tot_len_km = grp["pen_geom"].length.sum() / 1000.0
    print(f"  Year {yr}: {len(grp)} features, Total length: {tot_len_km:.1f} km, Sensors: {grp['Sensor'].unique().tolist()}")

