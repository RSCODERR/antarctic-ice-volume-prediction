import netCDF4 as nc
import numpy as np
import time

path_u = "antarctic-ice-volume-prediction/data/processed/stage4_5_3/stage4_5_3_unified_physical_fields.nc"
path_c = "antarctic-ice-volume-prediction/data/processed/stage4_7/stage4_7_calibrated_velocity.nc"

ds_u = nc.Dataset(path_u)
H_init = ds_u.variables["thickness"][:].astype(np.float64)
surface_init = ds_u.variables["surface"][:].astype(np.float64)
bed = ds_u.variables["bed"][:].astype(np.float64)
smb_clim = ds_u.variables["smb"][:].astype(np.float64) # mm w.e. / yr
alpha_g_init = ds_u.variables["alpha_grounded"][:].astype(np.float64)
alpha_f_init = ds_u.variables["alpha_floating"][:].astype(np.float64)
alpha_r = ds_u.variables["alpha_rock"][:].astype(np.float64)
cell_area = ds_u.variables["cell_area_wgs84_m2"][:].astype(np.float64)
vx_0761 = ds_u.variables["vx_0761"][:].astype(np.float64)
vy_0761 = ds_u.variables["vy_0761"][:].astype(np.float64)
ds_u.close()

ds_c = nc.Dataset(path_c)
u_cal = ds_c.variables["u_calibrated"][:].astype(np.float64) # m/yr
v_cal = ds_c.variables["v_calibrated"][:].astype(np.float64) # m/yr
ds_c.close()

Ny, Nx = H_init.shape
dx, dy = 1000.0, 1000.0
RHO_ICE = 917.0
RHO_WATER = 1028.0

k_scale = np.sqrt((dx * dy) / cell_area)
ds_x = dy / k_scale
ds_y = dx / k_scale

# Construct combined velocity field:
# On grounded: use calibrated SSA velocity (clipped to 5000 m/yr)
# On floating: use observed NSIDC-0761 velocity where valid, filled with border velocity
u_sim = np.where(alpha_g_init > 0, np.clip(u_cal, -5000.0, 5000.0), np.nan_to_num(vx_0761, nan=0.0))
v_sim = np.where(alpha_g_init > 0, np.clip(v_cal, -5000.0, 5000.0), np.nan_to_num(vy_0761, nan=0.0))

# Test transient integration over 1 year with dt = 0.1 yr (10 steps)
dt = 0.1 # years
n_steps = 10

H_curr = H_init.copy()
alpha_g = (alpha_g_init > 0) & (H_init > 10.0)
alpha_f = (alpha_f_init > 0) & (H_init > 10.0)

# Flotation threshold
h_flot = np.where(bed < 0, -bed * (RHO_WATER / RHO_ICE), 0.0)

mass_log = []

for step in range(1, n_steps + 1):
    t_start = (step - 1) * dt
    t_end = step * dt

    m_g_init = np.sum(alpha_g * H_curr * cell_area) * RHO_ICE * 1e-12 # Gt
    m_f_init = np.sum(alpha_f * H_curr * cell_area) * RHO_ICE * 1e-12 # Gt

    # Upwind face flux
    # X interfaces
    u_fx = 0.5 * (u_sim[:, :-1] + u_sim[:, 1:])
    h_up_x = np.where(u_fx > 0, H_curr[:, :-1], H_curr[:, 1:])
    ds_x_f = 0.5 * (ds_x[:, :-1] + ds_x[:, 1:])
    fx = h_up_x * u_fx * ds_x_f # m^3 / yr

    # Y interfaces (v > 0 is northward, from row 1 to row 0)
    v_fy = 0.5 * (v_sim[:-1, :] + v_sim[1:, :])
    h_up_y = np.where(v_fy > 0, H_curr[1:, :], H_curr[:-1, :])
    ds_y_f = 0.5 * (ds_y[:-1, :] + ds_y[1:, :])
    fy = h_up_y * v_fy * ds_y_f # m^3 / yr

    # Divergence
    div_F = np.zeros((Ny, Nx), dtype=np.float64)
    div_F[:, 1:] += fx
    div_F[:, :-1] -= fx
    div_F[1:, :] += fy
    div_F[:-1, :] -= fy

    # SMB in m / yr
    a_dot = smb_clim / RHO_ICE

    # Update thickness on ice domain (grounded and floating)
    active_ice = alpha_g | alpha_f
    dH = np.zeros((Ny, Nx), dtype=np.float64)
    dH[active_ice] = dt * (a_dot[active_ice] - div_F[active_ice] / cell_area[active_ice])

    H_next = np.maximum(0.0, H_curr + dH)

    # Flotation condition update (moving grounding line)
    hf_next = H_next - h_flot
    grounded_next = (hf_next > 0) & (H_next > 10.0)
    floating_next = (hf_next <= 0) & (bed < 0) & (H_next > 10.0)

    # Track migration
    un_grounded = alpha_g & floating_next
    re_grounded = alpha_f & grounded_next

    m_ungrounded = np.sum(un_grounded * H_next * cell_area) * RHO_ICE * 1e-12 # Gt
    m_regrounded = np.sum(re_grounded * H_next * cell_area) * RHO_ICE * 1e-12 # Gt

    m_g_final = np.sum(grounded_next * H_next * cell_area) * RHO_ICE * 1e-12
    m_f_final = np.sum(floating_next * H_next * cell_area) * RHO_ICE * 1e-12

    # Mass inputs/outputs during step:
    smb_g_step = np.sum(alpha_g * smb_clim * cell_area) * 1e-12 * dt
    smb_f_step = np.sum(alpha_f * smb_clim * cell_area) * 1e-12 * dt

    # Boundary fluxes across grounding line & calving fronts
    # 1. Grounding line flux (grounded to floating)
    fe_gl = (alpha_g[:, :-1] & alpha_f[:, 1:]) & (u_fx > 0)
    fw_gl = (alpha_f[:, :-1] & alpha_g[:, 1:]) & (u_fx < 0)
    fn_gl = (alpha_f[:-1, :] & alpha_g[1:, :]) & (v_fy > 0)
    fs_gl = (alpha_g[:-1, :] & alpha_f[1:, :]) & (v_fy < 0)
    f_gl_step = (np.sum(fx[fe_gl]) + np.sum(-fx[fw_gl]) + np.sum(fy[fn_gl]) + np.sum(-fy[fs_gl])) * RHO_ICE * 1e-12 * dt

    # 2. Grounded calving flux (grounded to ocean)
    ocean_cell = (~active_ice) & (alpha_r == 0)
    fe_go = (alpha_g[:, :-1] & ocean_cell[:, 1:]) & (u_fx > 0)
    fw_go = (ocean_cell[:, :-1] & alpha_g[:, 1:]) & (u_fx < 0)
    fn_go = (ocean_cell[:-1, :] & alpha_g[1:, :]) & (v_fy > 0)
    fs_go = (alpha_g[:-1, :] & ocean_cell[1:, :]) & (v_fy < 0)
    f_calv_g_step = (np.sum(fx[fe_go]) + np.sum(-fx[fw_go]) + np.sum(fy[fn_go]) + np.sum(-fy[fs_go])) * RHO_ICE * 1e-12 * dt

    # 3. Floating calving flux (floating to ocean)
    fe_fo = (alpha_f[:, :-1] & ocean_cell[:, 1:]) & (u_fx > 0)
    fw_fo = (ocean_cell[:, :-1] & alpha_f[:, 1:]) & (u_fx < 0)
    fn_fo = (ocean_cell[:-1, :] & alpha_f[1:, :]) & (v_fy > 0)
    fs_fo = (alpha_f[:-1, :] & ocean_cell[1:, :]) & (v_fy < 0)
    f_calv_f_step = (np.sum(fx[fe_fo]) + np.sum(-fx[fw_fo]) + np.sum(fy[fn_fo]) + np.sum(-fy[fs_fo])) * RHO_ICE * 1e-12 * dt

    # Mass balance ledger checks:
    # Grounded: dMg = SMB_g - F_gl - F_calv_g - M_ungrounded + M_regrounded
    pred_dMg = smb_g_step - f_gl_step - f_calv_g_step - m_ungrounded + m_regrounded
    actual_dMg = m_g_final - m_g_init
    res_g = actual_dMg - pred_dMg

    # Floating: dMf = SMB_f + F_gl - F_calv_f + M_ungrounded - M_regrounded
    pred_dMf = smb_f_step + f_gl_step - f_calv_f_step + m_ungrounded - m_regrounded
    actual_dMf = m_f_final - m_f_init
    res_f = actual_dMf - pred_dMf

    # System total: dM_sys = actual_dMg + actual_dMf
    actual_dM_sys = actual_dMg + actual_dMf
    pred_dM_sys = (smb_g_step + smb_f_step) - (f_calv_g_step + f_calv_f_step)
    res_sys = actual_dM_sys - pred_dM_sys

    mass_log.append({
        "step": step,
        "m_g_init": m_g_init,
        "m_g_final": m_g_final,
        "actual_dMg": actual_dMg,
        "pred_dMg": pred_dMg,
        "res_g": res_g,
        "actual_dMf": actual_dMf,
        "pred_dMf": pred_dMf,
        "res_f": res_f,
        "actual_dM_sys": actual_dM_sys,
        "pred_dM_sys": pred_dM_sys,
        "res_sys": res_sys,
        "un_grounded_cells": np.sum(un_grounded),
        "re_grounded_cells": np.sum(re_grounded)
    })

    # Advance state
    H_curr = H_next
    alpha_g = grounded_next
    alpha_f = floating_next

for r in mass_log:
    print(f"Step {r['step']:2d}: dM_sys={r['actual_dM_sys']:+.4f} Gt, pred={r['pred_dM_sys']:+.4f} Gt, "
          f"res_sys={r['res_sys']:.6f} Gt, ungrd={r['un_grounded_cells']}, regrd={r['re_grounded_cells']}")
