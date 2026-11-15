"""
Test script to inspect RACMO grid coordinates and reprojection to EPSG:3031.
"""
import netCDF4 as nc
import numpy as np
import pyproj
from scipy.interpolate import griddata

ds = nc.Dataset("data/raw/racmo/smb_monthlyS_XPEN055_ERAINx_RACMO2.3p2_197901_201908.nc")
lat = ds.variables['lat'][:]
lon = ds.variables['lon'][:]
smb = ds.variables['smb'][:] # (488, 1, 294, 390)

print(f"RACMO lat shape: {lat.shape}, lon shape: {lon.shape}, smb shape: {smb.shape}")

# Compute mean annual SMB over ERA-Interim period (1979-2018: 40 years = 480 months)
# smb is monthly accumulation in kg m-2 (mm w.e. / month)
smb_40yr = smb[:480, 0, :, :] # (480, 294, 390)
smb_annual_mean = np.mean(smb_40yr.reshape(40, 12, 294, 390).sum(axis=1), axis=0) # mm w.e. / yr
print(f"Annual mean SMB min: {smb_annual_mean.min():.1f}, max: {smb_annual_mean.max():.1f}, mean: {smb_annual_mean.mean():.1f} mm w.e./yr")

# Transform RACMO lat/lon to EPSG:3031
transformer = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:3031", always_xy=True)
racmo_x, racmo_y = transformer.transform(lon, lat)
print(f"RACMO X in 3031: min={racmo_x.min():.1f}, max={racmo_x.max():.1f}")
print(f"RACMO Y in 3031: min={racmo_y.min():.1f}, max={racmo_y.max():.1f}")

