import os, numpy as np, netCDF4 as nc, scipy.ndimage, pandas as pd

NC_UNIFIED = 'antarctic-ice-volume-prediction/data/processed/stage4_5_3/stage4_5_3_unified_physical_fields.nc'
NC_CAL = 'antarctic-ice-volume-prediction/data/processed/stage4_7/stage4_7_calibrated_velocity.nc'

ds_c = nc.Dataset(NC_CAL)
u_cal = np.nan_to_num(np.asarray(ds_c.variables['u_calibrated'][:]), nan=0.0)
v_cal = np.nan_to_num(np.asarray(ds_c.variables['v_calibrated'][:]), nan=0.0)
ds_c.close()

ds_u = nc.Dataset(NC_UNIFIED)
H_init = np.nan_to_num(np.asarray(ds_u.variables['thickness'][:]), nan=0.0)
surface_init = np.nan_to_num(np.asarray(ds_u.variables['surface'][:]), nan=0.0)
bed = np.nan_to_num(np.asarray(ds_u.variables['bed'][:]), nan=0.0)
ag = np.nan_to_num(np.asarray(ds_u.variables['alpha_grounded'][:]), nan=0.0)
af = np.nan_to_num(np.asarray(ds_u.variables['alpha_floating'][:]), nan=0.0)
cell_area = np.nan_to_num(np.asarray(ds_u.variables['cell_area_wgs84_m2'][:]), nan=1e6)
vx_0761 = np.nan_to_num(np.asarray(ds_u.variables['vx_0761'][:]), nan=0.0)
vy_0761 = np.nan_to_num(np.asarray(ds_u.variables['vy_0761'][:]), nan=0.0)
ds_u.close()

grd_init = (ag >= af) & (ag > 0) & (H_init > 10.0)
flt_init = (af > ag) & (af > 0) & (H_init > 10.0)
ice_mask = grd_init | flt_init

Ny, Nx = H_init.shape
dx, dy = 1000.0, 1000.0
k_scale = np.sqrt((dx * dy) / cell_area)
ds_x = dy / k_scale
ds_y = dx / k_scale
h_flot = np.where(bed < 0, -bed * (1028.0 / 917.0), 0.0)

# Precomputed RACMO forcing
df_inv = pd.read_csv('antarctic-ice-volume-prediction/reports/tables/stage5_1_historical_forcing_inventory.csv')
print('Inventory loaded, years:', len(df_inv))

# Load RACMO fields from file
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

u_sim_base = np.where(grd_init, np.clip(u_cal, -5000.0, 5000.0), np.nan_to_num(vx_0761, nan=0.0))
v_sim_base = np.where(grd_init, np.clip(v_cal, -5000.0, 5000.0), np.nan_to_num(vy_0761, nan=0.0))

s0 = scipy.ndimage.gaussian_filter(surface_init, sigma=1.0)
ds_dy0, ds_dx0 = np.gradient(s0, -dy, dx)
td0 = np.maximum(1e-3, 917.0 * 9.81 * H_init * np.sqrt(ds_dx0**2 + ds_dy0**2))

H_curr = H_init.copy()
grd_curr = grd_init.copy()
flt_curr = flt_init.copy()
ever_ungrd = np.zeros_like(grd_init, dtype=bool)

years = list(range(2000, 2019))
results = []

for yr in years:
    smb_yr = f_lin_all[:, :, yr - 1979]
    m_g_start = np.sum(H_curr[grd_curr] * cell_area[grd_curr]) * 917.0 * 1e-12

    # Evolve surface continuously
    s_curr = surface_init + np.where(grd_curr, H_curr - H_init, (1.0 - 917.0/1028.0) * (H_curr - H_init))
    s_curr_sm = scipy.ndimage.gaussian_filter(s_curr, sigma=1.0)
    ds_dy_c, ds_dx_c = np.gradient(s_curr_sm, -dy, dx)
    td_curr = 917.0 * 9.81 * H_curr * np.sqrt(ds_dx_c**2 + ds_dy_c**2)
    # Physical Weertman perturbation response
    ratio = np.clip(td_curr / td0, 0.85, 1.15)**(1.0/3.0)
    u_c = u_sim_base * ratio
    v_c = v_sim_base * ratio

    ann_gl = 0.0
    ann_cg = 0.0
    ann_cf = 0.0
    ann_smb_g = 0.0
    ann_smb_f = 0.0
    ann_ungrd_cnt = 0
    ann_regrd_cnt = 0
    ann_res = 0.0

    for st in range(10):
        act = grd_curr | flt_curr
        H_curr[~act] = 0.0
        m_s0 = np.sum(H_curr[act] * cell_area[act]) * 917.0 * 1e-12

        u_fx = 0.5 * (u_c[:, :-1] + u_c[:, 1:])
        h_up_x = np.where(u_fx > 0, H_curr[:, :-1], H_curr[:, 1:])
        fx = h_up_x * u_fx * 0.5 * (ds_x[:, :-1] + ds_x[:, 1:])

        v_fy = 0.5 * (v_c[:-1, :] + v_c[1:, :])
        h_up_y = np.where(v_fy > 0, H_curr[1:, :], H_curr[:-1, :])
        fy = h_up_y * v_fy * 0.5 * (ds_y[:-1, :] + ds_y[1:, :])

        div_F = np.zeros((Ny, Nx), dtype=np.float64)
        div_F[:, :-1] += fx
        div_F[:, 1:] -= fx
        div_F[1:, :] += fy
        div_F[:-1, :] -= fy

        gl_x = np.sum(fx[grd_curr[:, :-1] & flt_curr[:, 1:]]) - np.sum(fx[flt_curr[:, :-1] & grd_curr[:, 1:]])
        gl_y = np.sum(fy[grd_curr[1:, :] & flt_curr[:-1, :]]) - np.sum(fy[flt_curr[1:, :] & grd_curr[:-1, :]])
        F_gl_st = (gl_x + gl_y) * 917.0 * 1e-12

        not_ice = ~act
        cg_x = np.sum(fx[grd_curr[:, :-1] & not_ice[:, 1:]]) - np.sum(fx[not_ice[:, :-1] & grd_curr[:, 1:]])
        cg_y = np.sum(fy[grd_curr[1:, :] & not_ice[:-1, :]]) - np.sum(fy[not_ice[1:, :] & grd_curr[:-1, :]])
        F_cg_st = (cg_x + cg_y) * 917.0 * 1e-12

        cf_x = np.sum(fx[flt_curr[:, :-1] & not_ice[:, 1:]]) - np.sum(fx[not_ice[:, :-1] & flt_curr[:, 1:]])
        cf_y = np.sum(fy[flt_curr[1:, :] & not_ice[:-1, :]]) - np.sum(fy[not_ice[1:, :] & flt_curr[:-1, :]])
        F_cf_st = (cf_x + cf_y) * 917.0 * 1e-12

        smb_g_st = np.sum(smb_yr[grd_curr] * cell_area[grd_curr]) * 1e-12 * 0.1
        smb_f_st = np.sum(smb_yr[flt_curr] * cell_area[flt_curr]) * 1e-12 * 0.1

        ann_gl += F_gl_st * 0.1
        ann_cg += F_cg_st * 0.1
        ann_cf += F_cf_st * 0.1
        ann_smb_g += smb_g_st
        ann_smb_f += smb_f_st

        dH = 0.1 * (smb_yr / 917.0 - div_F / cell_area)
        H_nxt = H_curr + dH

        hf_nxt = H_nxt - h_flot
        ungrd = grd_curr & (hf_nxt <= 0) & (bed < 0) & (H_nxt > 10.0) & (H_init > h_flot)
        regrd = flt_curr & ever_ungrd & (hf_nxt > 0) & (H_nxt > 10.0)
        ever_ungrd = (ever_ungrd | ungrd) & (~regrd)

        ann_ungrd_cnt += int(np.sum(ungrd))
        ann_regrd_cnt += int(np.sum(regrd))

        grd_curr = (grd_curr & (~ungrd)) | regrd
        flt_curr = (flt_curr & (~regrd)) | ungrd
        H_curr = H_nxt

        m_s1 = np.sum(H_curr[grd_curr | flt_curr] * cell_area[grd_curr | flt_curr]) * 917.0 * 1e-12
        act_dM = m_s1 - m_s0
        prd_dM = (smb_g_st + smb_f_st) - (F_cg_st + F_cf_st) * 0.1
        ann_res += abs(act_dM - prd_dM)

    m_g_end = np.sum(H_curr[grd_curr] * cell_area[grd_curr]) * 917.0 * 1e-12
    dMg = m_g_end - m_g_start

    results.append({
        'Year': yr, 'SMB_g': ann_smb_g, 'GL': ann_gl, 'Calv_g': ann_cg,
        'dMg': dMg, 'Ungrd': ann_ungrd_cnt, 'Regrd': ann_regrd_cnt, 'Res': ann_res
    })
    print(f"Year {yr}: SMB_g={ann_smb_g:.1f}, GL={ann_gl:.1f}, Calv_g={ann_cg:.1f}, dMg={dMg:+.2f} Gt/yr, Res={ann_res:.2e}")

df_res = pd.DataFrame(results)
print('\n--- 19-Year Summary ---')
print(f"Mean dMg: {df_res['dMg'].mean():.2f} Gt/yr")
print(f"Cumulative dMg: {df_res['dMg'].sum():.2f} Gt")
print(f"Mean GL Flux: {df_res['GL'].mean():.2f} Gt/yr")
print(f"Mean Calv_g Flux: {df_res['Calv_g'].mean():.2f} Gt/yr")
print(f"Total Residual: {df_res['Res'].sum():.2e} Gt")
