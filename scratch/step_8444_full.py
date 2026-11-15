antarctic-ice-volume-prediction\.venv\Scripts\python.exe -c "
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
from scipy.interpolate import LinearNDInterpolator, NearestNDInterpolator
transformer = pyproj.Transformer.from_crs('EPSG:4326', 'EPSG:3031', always_xy=True)
rx, ry = transformer.transform(lon_r, lat_r)
mask_pts = (rx >= -2800000) & (rx <= -1300000) & (ry >= 150000) & (ry <= 2050000)
pts = np.column_stack([rx[mask_pts], ry[mask_pts]])

p_bm = os.path.join('antarctic-ice-volume-prediction', 'data', 'processed', 'bedmachine_v4.1_peninsula_aligned_to_bedmap3.nc')
ds_bm = nc.Dataset(p_bm)
x_1km = ds_bm.variables['x'][:].reshape(-1, 2).mean(axis=1)
y_1km = ds_bm.variables['y'][:].reshape(-1, 2).mean(axis=1)
ds_bm.close()
gx_1km, gy_1km = np.meshgrid(x_1km, y_1km)

vals_all = smb_ann_r[:, mask_pts].T
interp_lin = LinearNDInterpolator(pts, vals_all)
f_lin_all = interp_lin(gx_1km, gy_1km)
nan_m = np.isnan(f_lin_all[:, :, 0])
if np.any(nan_m):
    interp_nn = NearestNDInterpolator(pts, vals_all)
    f_lin_all[nan_m, :] = interp_nn(gx_1km[nan_m], gy_1km[nan_m])

u_base = np.where(grounded_init, np.clip(u_cal, -5000.0, 5000.0), np.nan_to_num(vx_0761, nan=0.0))
v_base = np.where(grounded_init, np.clip(v_cal, -5000.0, 5000.0), np.nan_to_num(vy_0761, nan=0.0))

s0 = surface_init.copy()
ds_dy0, ds_dx0 = np.gradient(scipy.ndimage.gaussian_filter(s0, sigma=1.0), -dy, dx)
td0 = 917.0 * 9.81 * H_init * np.sqrt(ds_dx0**2 + ds_dy0**2)

H_sim = H_init.copy()
grd_sim = grounded_init.copy()
flt_sim = floating_init.copy()
ever_ungrd = np.zeros_like(grounded_init, dtype=bool)

years = list(range(2000, 2019))
dm_list = []

for yr in years:
    idx = yr - 1979
    smb_yr = f_lin_all[:, :, idx]
    m_g_start = np.sum(H_sim[grd_sim] * cell_area[grd_sim]) * 917.0 * 1e-12

    s_curr = np.where(grd_sim, bed + H_sim, (1.0 - 917.0/1028.0) * H_sim)
    ds_dy_c, ds_dx_c = np.gradient(scipy.ndimage.gaussian_filter(s_curr, sigma=1.0), -dy, dx)
    td_curr = 917.0 * 9.81 * H_sim * np.sqrt(ds_dx_c**2 + ds_dy_c**2)
    ratio = np.clip(td_curr / np.maximum(td0, 1e-3), 0.8, 1.25)**(1.0/3.0)
    
    u_c = u_base * ratio
    v_c = v_base * ratio

    for st in range(10):
        act = grd_sim | flt_sim
        H_sim[~act] = 0.0

        u_fx = 0.5 * (u_c[:, :-1] + u_c[:, 1:])
        h_up_x = np.where(u_fx > 0, H_sim[:, :-1], H_sim[:, 1:])
        fx = h_up_x * u_fx * 0.5 * (ds_x[:, :-1] + ds_x[:, 1:])

        v_fy = 0.5 * (v_c[:-1, :] + v_c[1:, :])
        h_up_y = np.where(v_fy > 0, H_sim[1:, :], H_sim[:-1, :])
        fy = h_up_y * v_fy * 0.5 * (ds_y[:-1, :] + ds_y[1:, :])

        div_F = np.zeros((Ny, Nx), dtype=np.float64)
        div_F[:, :-1] += fx
        div_F[:, 1:] -= fx
        div_F[1:, :] += fy
        div_F[:-1, :] -= fy

        dH = 0.1 * (smb_yr / 917.0 - div_F / cell_area)
        H_nxt = H_sim + dH

        hf_nxt = H_nxt - h_flot
        ungrd = grd_sim & (hf_nxt <= 0) & (bed < 0) & (H_nxt > 10.0) & (H_init > h_flot)
        regrd = flt_sim & ever_ungrd & (hf_nxt > 0) & (H_nxt > 10.0)
        ever_ungrd = (ever_ungrd | ungrd) & (~regrd)

        grd_sim = (grd_sim & (~ungrd)) | regrd
        flt_sim = (flt_sim & (~regrd)) | ungrd
        H_sim = H_nxt

    m_g_end = np.sum(H_sim[grd_sim] * cell_area[grd_sim]) * 917.0 * 1e-12
    dMg = m_g_end - m_g_start
    dm_list.append(dMg)
    print(f'Year {yr}: dMg = {dMg:+.2f} Gt/yr')

print(f'Mean dMg (2000-2018): {np.mean(dm_list):.2f} Gt/yr, Cumulative: {np.sum(dm_list):.2f} Gt')
"