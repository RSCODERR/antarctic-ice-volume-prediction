import netCDF4 as nc
import numpy as np
import pyproj
from scipy.interpolate import griddata
import time

t0 = time.perf_counter()

# Load raw RACMO
p_racmo = "antarctic-ice-volume-prediction/data/raw/racmo/smb_monthlyS_XPEN055_ERAINx_RACMO2.3p2_197901_201908.nc"
ds_r = nc.Dataset(p_racmo)
lat = ds_r.variables["lat"][:]
lon = ds_r.variables["lon"][:]
smb_m = ds_r.variables["smb"][:480, 0, :, :] # 40 years, 1979-2018
ds_r.close()

# 40 annual sums: (40, 294, 390)
smb_annual = smb_m.reshape(40, 12, 294, 390).sum(axis=1) # mm w.e. / yr
years = list(range(1979, 2019))

# Project coordinates to EPSG:3031
transformer = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:3031", always_xy=True)
rx, ry = transformer.transform(lon, lat)

mask_pts = (rx >= -2800000) & (rx <= -1300000) & (ry >= 150000) & (ry <= 2050000)
pts_x = rx[mask_pts]
pts_y = ry[mask_pts]

# 1 km grid
p_bm = "antarctic-ice-volume-prediction/data/processed/bedmachine_v4.1_peninsula_aligned_to_bedmap3.nc"
ds_bm = nc.Dataset(p_bm)
x_1km = ds_bm.variables["x"][:].reshape(-1, 2).mean(axis=1)
y_1km = ds_bm.variables["y"][:].reshape(-1, 2).mean(axis=1)
ds_bm.close()

gx_1km, gy_1km = np.meshgrid(x_1km, y_1km)

pilot_years = [2014, 2015, 2016, 2017]
pilot_smb_1km = {}

for yr in pilot_years:
    idx = years.index(yr)
    smb_y = smb_annual[idx][mask_pts]
    # Linear interpolation
    f_lin = griddata((pts_x, pts_y), smb_y, (gx_1km, gy_1km), method="linear")
    nan_m = np.isnan(f_lin)
    if np.any(nan_m):
        f_nn = griddata((pts_x, pts_y), smb_y, (gx_1km[nan_m], gy_1km[nan_m]), method="nearest")
        f_lin[nan_m] = f_nn
    pilot_smb_1km[yr] = f_lin
    print(f"Remapped RACMO {yr}: min={f_lin.min():.1f}, max={f_lin.max():.1f}, mean={f_lin.mean():.1f} mm w.e./yr")

t1 = time.perf_counter()
print(f"Total remapping time for 4 years: {t1 - t0:.2f} s")
