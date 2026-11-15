"""
Test RACMO climatological SMB remapping and conservation.
"""
import netCDF4 as nc
import numpy as np
import pyproj
from scipy.interpolate import griddata, NearestNDInterpolator, CloughTocher2DInterpolator, LinearNDInterpolator

# Load RACMO
ds_racmo = nc.Dataset("data/raw/racmo/smb_monthlyS_XPEN055_ERAINx_RACMO2.3p2_197901_201908.nc")
lat = ds_racmo.variables['lat'][:]
lon = ds_racmo.variables['lon'][:]
smb_monthly = ds_racmo.variables['smb'][:] # (488, 1, 294, 390)

# Mean annual SMB over 1979-2018 (40 years = 480 months)
smb_annual = smb_monthly[:480, 0, :, :].reshape(40, 12, 294, 390).sum(axis=1).mean(axis=0) # mm w.e./yr

# Project RACMO to EPSG:3031
transformer = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:3031", always_xy=True)
rx, ry = transformer.transform(lon, lat)

# Load 1 km macro-mesh grid
ds_bm = nc.Dataset("data/processed/bedmachine_v4.1_peninsula_aligned_to_bedmap3.nc")
x_500 = ds_bm.variables["x"][:]
y_500 = ds_bm.variables["y"][:]
x_1km = x_500.reshape(-1, 2).mean(axis=1) # 1300
y_1km = y_500.reshape(-1, 2).mean(axis=1) # 1700

# Bounding box filter for RACMO points to speed up interpolation
# Peninsula box: x in [-2750000, -1350000], y in [200000, 2000000]
mask_pts = (rx >= -2800000) & (rx <= -1300000) & (ry >= 150000) & (ry <= 2050000)
pts_x = rx[mask_pts]
pts_y = ry[mask_pts]
pts_val = smb_annual[mask_pts]
print(f"RACMO points in Peninsula domain: {len(pts_x)}")

# Grid coordinates for 1 km
gx_1km, gy_1km = np.meshgrid(x_1km, y_1km)

# Linear interpolation
print("Interpolating to 1 km macro-mesh...")
smb_1km = griddata((pts_x, pts_y), pts_val, (gx_1km, gy_1km), method='linear')

# Fill NaNs near edges with nearest neighbor
nan_mask = np.isnan(smb_1km)
if np.any(nan_mask):
    print(f"Filling {np.sum(nan_mask)} edge NaNs with nearest neighbor...")
    smb_nn = griddata((pts_x, pts_y), pts_val, (gx_1km[nan_mask], gy_1km[nan_mask]), method='nearest')
    smb_1km[nan_mask] = smb_nn

print(f"1 km remapped SMB stats: min={smb_1km.min():.1f}, max={smb_1km.max():.1f}, mean={smb_1km.mean():.1f} mm w.e./yr")

