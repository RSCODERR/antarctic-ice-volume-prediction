import netCDF4 as nc
import numpy as np
import pandas as pd
import pyproj
from scipy.interpolate import griddata

NC_UNIFIED = "data/processed/stage4_5_3/stage4_5_3_unified_physical_fields.nc"
NC_CAL = "data/processed/stage4_7/stage4_7_calibrated_velocity.nc"
RACMO_RAW = "data/raw/racmo/smb_monthlyS_XPEN055_ERAINx_RACMO2.3p2_197901_201908.nc"
IMBIE3_CSV = "data/raw/imbie/imbie3_antarctic_peninsula_Gt_partitioned.csv"

ds_u = nc.Dataset(NC_UNIFIED)
H_init = ds_u.variables["thickness"][:].astype(np.float64)
bed = ds_u.variables["bed"][:].astype(np.float64)
ag = ds_u.variables["alpha_grounded"][:].astype(np.float64)
af = ds_u.variables["alpha_floating"][:].astype(np.float64)
area = ds_u.variables["cell_area_wgs84_m2"][:].astype(np.float64)
vx_0761 = ds_u.variables["vx_0761"][:].astype(np.float64)
vy_0761 = ds_u.variables["vy_0761"][:].astype(np.float64)
ds_u.close()

ds_c = nc.Dataset(NC_CAL)
u_cal = ds_c.variables["u_calibrated"][:].astype(np.float64)
v_cal = ds_c.variables["v_calibrated"][:].astype(np.float64)
ds_c.close()

RHO_ICE = 917.0
RHO_WATER = 1028.0
Ny, Nx = H_init.shape
dx, dy = 1000.0, 1000.0
k_scale = np.sqrt((dx * dy) / area)
ds_x = dy / k_scale
ds_y = dx / k_scale

grounded_init = (ag >= af) & (ag > 0) & (H_init > 10.0)
floating_init = (af > ag) & (af > 0) & (H_init > 10.0)
ice_mask_init = grounded_init | floating_init

h_flot = np.where(bed < 0, -bed * (RHO_WATER / RHO_ICE), 0.0)

u_sim_base = np.where(grounded_init, np.clip(u_cal, -5000.0, 5000.0), np.nan_to_num(vx_0761, nan=0.0))
v_sim_base = np.where(grounded_init, np.clip(v_cal, -5000.0, 5000.0), np.nan_to_num(vy_0761, nan=0.0))

# RACMO
ds_r = nc.Dataset(RACMO_RAW)
lat_r = ds_r.variables["lat"][:]
lon_r = ds_r.variables["lon"][:]
smb_m = ds_r.variables["smb"][:480, 0, :, :]
ds_r.close()
smb_ann_r = smb_m.reshape(40, 12, 294, 390).sum(axis=1)
years_r = list(range(1979, 2019))

transformer = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:3031", always_xy=True)
rx, ry = transformer.transform(lon_r, lat_r)
m_pts = (rx >= -2800000) & (rx <= -1300000) & (ry >= 150000) & (ry <= 2050000)
pts_x = rx[m_pts]
pts_y = ry[m_pts]

p_bm = "data/processed/bedmachine_v4.1_peninsula_aligned_to_bedmap3.nc"
ds_bm = nc.Dataset(p_bm)
x_1km = ds_bm.variables["x"][:].reshape(-1, 2).mean(axis=1)
y_1km = ds_bm.variables["y"][:].reshape(-1, 2).mean(axis=1)
ds_bm.close()
gx_1km, gy_1km = np.meshgrid(x_1km, y_1km)

historical_smb = {}
for yr in [2014, 2015, 2016, 2017]:
    idx = years_r.index(yr)
    val = smb_ann_r[idx][m_pts]
    f_lin = griddata((pts_x, pts_y), val, (gx_1km, gy_1km), method="linear")
    nan_m = np.isnan(f_lin)
    if np.any(nan_m):
        f_nn = griddata((pts_x, pts_y), val, (gx_1km[nan_m], gy_1km[nan_m]), method="nearest")
        f_lin[nan_m] = f_nn
    historical_smb[yr] = f_lin

df_imbie3 = pd.read_csv(IMBIE3_CSV, comment="#")
df_imbie3["Year"] = pd.to_datetime(df_imbie3["Date"]).dt.year
imbie_ann = df_imbie3.groupby("Year")[["Mass balance (Gt/yr)", "Mass balance uncertainty (Gt/yr)"]].mean()

pilot_dt = 0.1
H_sim = H_init.copy()
H_sim[~ice_mask_init] = 0.0
grd_sim = grounded_init.copy()
flt_sim = floating_init.copy()

# Track which cells were dynamically ungrounded during the simulation
ever_ungrounded = np.zeros_like(grounded_init, dtype=bool)

print("\n--- Running 4-Year Pilot with Dynamic Tracking of Ungrounded Cells ---")
for yr in [2014, 2015, 2016, 2017]:
    smb_yr = historical_smb[yr]
    m_g_start = np.sum(H_sim[grd_sim] * area[grd_sim]) * RHO_ICE * 1e-12

    ann_gl = 0.0
    ann_cg = 0.0
    ann_smb_g = 0.0
    tot_unground = 0
    tot_reground = 0

    for st in range(10):
        act_ice = grd_sim | flt_sim
        H_sim[~act_ice] = 0.0

        u_fx = 0.5 * (u_sim_base[:, :-1] + u_sim_base[:, 1:])
        h_up_x = np.where(u_fx > 0, H_sim[:, :-1], H_sim[:, 1:])
        ds_x_f = 0.5 * (ds_x[:, :-1] + ds_x[:, 1:])
        fx = h_up_x * u_fx * ds_x_f

        v_fy = 0.5 * (v_sim_base[:-1, :] + v_sim_base[1:, :])
        h_up_y = np.where(v_fy > 0, H_sim[1:, :], H_sim[:-1, :])
        ds_y_f = 0.5 * (ds_y[:-1, :] + ds_y[1:, :])
        fy = h_up_y * v_fy * ds_y_f

        div_F = np.zeros((Ny, Nx), dtype=np.float64)
        div_F[:, :-1] += fx
        div_F[:, 1:] -= fx
        div_F[1:, :] += fy
        div_F[:-1, :] -= fy

        gl_x = np.sum(fx[grd_sim[:, :-1] & flt_sim[:, 1:]]) - np.sum(fx[flt_sim[:, :-1] & grd_sim[:, 1:]])
        gl_y = np.sum(fy[grd_sim[1:, :] & flt_sim[:-1, :]]) - np.sum(fy[flt_sim[1:, :] & grd_sim[:-1, :]])
        F_gl_st = (gl_x + gl_y) * RHO_ICE * 1e-12

        not_ice = ~act_ice
        cg_x = np.sum(fx[grd_sim[:, :-1] & not_ice[:, 1:]]) - np.sum(fx[not_ice[:, :-1] & grd_sim[:, 1:]])
        cg_y = np.sum(fy[grd_sim[1:, :] & not_ice[:-1, :]]) - np.sum(fy[not_ice[1:, :] & grd_sim[:-1, :]])
        F_cg_st = (cg_x + cg_y) * RHO_ICE * 1e-12

        smb_g_st = np.sum(smb_yr[grd_sim] * area[grd_sim]) * 1e-12
        ann_gl += F_gl_st * pilot_dt
        ann_cg += F_cg_st * pilot_dt
        ann_smb_g += smb_g_st * pilot_dt

        dH_st = pilot_dt * (smb_yr / RHO_ICE - div_F / area)
        H_nxt = H_sim.copy()
        H_nxt[act_ice] = H_sim[act_ice] + dH_st[act_ice]

        # Ungrounding: grounded cell thins below flotation
        # Note: only cells that were initially grounded with H_init > h_flot can unground when H_nxt <= h_flot
        # For the 1077 cells initially grounded with H_init <= h_flot, they unground if they thin by > 1m
        hf_val = H_nxt - h_flot
        ungrd = grd_sim & (hf_val <= 0) & (bed < 0) & (H_nxt > 10.0) & (H_init > h_flot)
        
        # Regrounding: ONLY cells that were previously grounded and ungrounded during the simulation can reground
        regrd = flt_sim & ever_ungrounded & (hf_val > 0) & (H_nxt > 10.0)

        ever_ungrounded = (ever_ungrounded | ungrd) & (~regrd)
        tot_unground += int(np.sum(ungrd))
        tot_reground += int(np.sum(regrd))

        grd_sim = (grd_sim & (~ungrd)) | regrd
        flt_sim = (flt_sim & (~regrd)) | ungrd
        H_sim = H_nxt

    m_g_end = np.sum(H_sim[grd_sim] * area[grd_sim]) * RHO_ICE * 1e-12
    ann_dMg = m_g_end - m_g_start
    imb_mb = float(imbie_ann.loc[yr, "Mass balance (Gt/yr)"])
    imb_unc = float(imbie_ann.loc[yr, "Mass balance uncertainty (Gt/yr)"])

    print(f"Year {yr}: RACMO_G_SMB={ann_smb_g:.2f} Gt/yr, Marine_Loss={(ann_gl+ann_cg):.2f} (GL={ann_gl:.2f}, Calv={ann_cg:.2f}), Modeled_dMg={ann_dMg:+.2f} Gt/yr, IMBIE3={imb_mb:+.2f} +/- {imb_unc:.1f} Gt/yr, Unground={tot_unground}, Reground={tot_reground}")
