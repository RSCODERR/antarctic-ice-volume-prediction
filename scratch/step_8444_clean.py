"antarctic-ice-volume-prediction\.venv\Scripts\python.exe -c "
import os, numpy as np, netCDF4 as nc, scipy.ndimage, pandas as pd

p_c = os.path.join('antarctic-ice-volume-prediction', 'data', 'processed', 'stage4_7', 'stage4_7_calibrated_velocity.nc')
ds_c = nc.Dataset(p_c)
u_cal = ds_c.variables['u_calibrated'][:].astype(np.float64)
v_cal = ds_c.variables['v_calibrated'][:].astype(np.float64)
ds_c.close()

p_u = os.path.join('antarctic-ice-volume-prediction', 'data', 'processed', 'stage4_5_3', 'stage4_5_3_unified_physical_fields.nc')
ds_u = nc.Dataset(p_u)
H_init = ds_u.variables['thickness'][:].astype(np.float64)
surface_init = ds_u.variables['surface'][:].astype(np.float64)
bed = ds_u.variables['bed'][:].astype(np.float64)
alpha_g_init = ds_u.variables['alpha_grounded'][:].astype(np.float64)
alpha_f_init = ds_u.variables['alpha_floating'][:].astype(np.float64)
cell_area = ds_u.variables['cell_area_wgs84_m2'][:].astype(np.float64)
vx_0761 = ds_u.variables['vx_0761'][:].astype(np.float64)
vy_0761 = ds_u.variables['vy_0761'][:].astype(np.float64)
ds_u.close()

grounded_init = (alpha_g_init >= alpha_f_init) & (alpha_g_init > 0) & (H_init > 10.0)
floating_init = (alpha_f_init > alpha_g_init) & (alpha_f_init > 0) & (H_init > 10.0)
ice_mask = grounded_init | floating_init
not_ice = ~ice_mask

Ny, Nx = H_init.shape
dx, dy = 1000.0, 1000.0
k_scale = np.sqrt((dx * dy) / cell_area)
ds_x = dy / k_scale
ds_y = dx / k_scale
h_flot = np.where(bed < 0, -bed * (1028.0 / 917.0), 0.0)

# Load RACMO 40-year inventory pre-extracted
# Using f_lin_all from before
p_racmo = os.path.join('antarctic-ice-volume-prediction', 'data', 'raw', 'racmo', 'smb_monthlyS_XPEN055_ERAINx_RACMO2.3p2_197901_201908.nc')
ds_r = nc.Dataset(p_racmo)
lat_r = ds_r.variables['lat'][:]
lon_r = ds_r.variables['lon'][:]
smb_m = ds_r.variables['smb'][:480, 0, :, :]
ds_r.close()
smb_ann_r = smb_m.reshape(40, 12, 294, 390).sum(axis=1)

import pyproj
from scipy.interpolate import LinearNDInterpolator, NearestNDInter
<truncated 3386 bytes>