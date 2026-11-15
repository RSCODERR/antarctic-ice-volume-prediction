"""
Compute SMB mass integration over Domain A basins.
"""
import sys, os
sys.path.insert(0, ".")
import netCDF4 as nc
import numpy as np
import pyproj
from scipy.interpolate import griddata
import geopandas as gpd
import rasterio
from rasterio.mask import mask as rmask
from src.geospatial.audit_distortion import compute_scale_factor_grid

# 1. Load BedMachine & Domain A
ALIGNED_NC = "data/processed/bedmachine_v4.1_peninsula_aligned_to_bedmap3.nc"
BM3_MASK = "data/processed/bedmap3_masks_peninsula_500m.tif"
BM3_THICK = "data/processed/bedmap3_thickness_peninsula_500m.tif"
IMBIE_SHP = "data/raw/imbie_basins/IMBIE_AIS_Regional_Delineations/IMBIE_AIS_Regional_Delineations.shp"

ds_bm = nc.Dataset(ALIGNED_NC)
x_500 = ds_bm.variables["x"][:]
y_500 = ds_bm.variables["y"][:]
bm_mask = ds_bm.variables["mask"][:]
bm_thick = ds_bm.variables["thickness"][:]

with rasterio.open(BM3_MASK) as src_m:
    bm3_mask = src_m.read(1)
    bm3_transform = src_m.transform
    height, width = src_m.shape
with rasterio.open(BM3_THICK) as src_t:
    bm3_thick = src_t.read(1)

bm3_gr = (bm3_mask == 1) & (bm3_thick > 0) & (bm3_thick != -9999)
bm_gr = (bm_mask == 2) & (bm_thick > 0) & (bm_thick != -9999)

gdf = gpd.read_file(IMBIE_SHP)
pen_basins = gdf[(gdf["Region"] == "Peninsula") & (gdf["Type"] == "Ice_sheet")].sort_values("Basin")

basin_masks_500m = {}
for _, row in pen_basins.iterrows():
    b_name = row["Basin"]
    with rasterio.open(BM3_MASK) as src:
        m_masked, _ = rmask(src, [row["geometry"]], crop=False, all_touched=False, nodata=-9999)
        basin_masks_500m[b_name] = (m_masked[0] == 1) & bm3_gr & bm_gr

areal_scale, lats, lons = compute_scale_factor_grid(bm3_transform, height, width)
cell_area_km2_500m = 0.25 / areal_scale.astype(np.float64)

# 1 km grid
x_1km = x_500.reshape(-1, 2).mean(axis=1)
y_1km = y_500.reshape(-1, 2).mean(axis=1)
gx_1km, gy_1km = np.meshgrid(x_1km, y_1km)

basin_masks_1km = {}
basin_area_1km = {}
for b_name, m500 in basin_masks_500m.items():
    # 1 km area fraction
    alpha = m500.reshape(1700, 2, 1300, 2).mean(axis=(1, 3))
    basin_masks_1km[b_name] = alpha
    # ellipsoidal area
    ellip_area = (m500 * cell_area_km2_500m).reshape(1700, 2, 1300, 2).sum(axis=(1, 3))
    basin_area_1km[b_name] = ellip_area
    print(f"Basin {b_name}: 500m cells={np.sum(m500)}, 500m ellip area={np.sum(cell_area_km2_500m[m500]):.2f} km2, 1km ellip area={np.sum(ellip_area):.2f} km2")

# 2. Load RACMO and interpolate
ds_racmo = nc.Dataset("data/raw/racmo/smb_monthlyS_XPEN055_ERAINx_RACMO2.3p2_197901_201908.nc")
lat = ds_racmo.variables['lat'][:]
lon = ds_racmo.variables['lon'][:]
smb_monthly = ds_racmo.variables['smb'][:]
smb_annual = smb_monthly[:480, 0, :, :].reshape(40, 12, 294, 390).sum(axis=1).mean(axis=0)

transformer = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:3031", always_xy=True)
rx, ry = transformer.transform(lon, lat)

mask_pts = (rx >= -2800000) & (rx <= -1300000) & (ry >= 150000) & (ry <= 2050000)
pts_x = rx[mask_pts]
pts_y = ry[mask_pts]
pts_val = smb_annual[mask_pts]

smb_1km = griddata((pts_x, pts_y), pts_val, (gx_1km, gy_1km), method='linear')
nan_mask = np.isnan(smb_1km)
if np.any(nan_mask):
    smb_nn = griddata((pts_x, pts_y), pts_val, (gx_1km[nan_mask], gy_1km[nan_mask]), method='nearest')
    smb_1km[nan_mask] = smb_nn

# Integrated SMB per basin (in Gt/yr)
print("\n--- Integrated SMB over Domain A Basins ---")
tot_mass_gt = 0.0
for b_name in ["Hp-I", "I-Ipp", "Ipp-J"]:
    area = basin_area_1km[b_name] # km2
    mass_gt = np.sum(smb_1km * area) * 1e-3
    mean_smb = np.sum(smb_1km * area) / np.sum(area)
    tot_mass_gt += mass_gt
    print(f"Basin {b_name}: Mean SMB = {mean_smb:.1f} mm w.e./yr, Integrated Mass = {mass_gt:.2f} Gt/yr")

print(f"Total Domain A Integrated SMB: {tot_mass_gt:.2f} Gt/yr")
