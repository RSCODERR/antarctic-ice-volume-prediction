import netCDF4 as nc
import numpy as np

path_u = "antarctic-ice-volume-prediction/data/processed/stage4_5_3/stage4_5_3_unified_physical_fields.nc"
path_c = "antarctic-ice-volume-prediction/data/processed/stage4_7/stage4_7_calibrated_velocity.nc"

ds_u = nc.Dataset(path_u)
H_init = ds_u.variables["thickness"][:].astype(np.float64)
bed = ds_u.variables["bed"][:].astype(np.float64)
smb = ds_u.variables["smb"][:].astype(np.float64)
alpha_g_init = ds_u.variables["alpha_grounded"][:].astype(np.float64)
alpha_f_init = ds_u.variables["alpha_floating"][:].astype(np.float64)
cell_area = ds_u.variables["cell_area_wgs84_m2"][:].astype(np.float64)
ds_u.close()

ds_c = nc.Dataset(path_c)
u_cal = ds_c.variables["u_calibrated"][:].astype(np.float64)
v_cal = ds_c.variables["v_calibrated"][:].astype(np.float64)
ds_c.close()

Ny, Nx = H_init.shape
dx, dy = 1000.0, 1000.0
RHO_ICE = 917.0
RHO_WATER = 1028.0

k_scale = np.sqrt((dx * dy) / cell_area)
ds_x = dy / k_scale
ds_y = dx / k_scale

# Mutually exclusive partition
grounded = (alpha_g_init >= alpha_f_init) & (alpha_g_init > 0) & (H_init > 10.0)
floating = (alpha_f_init > alpha_g_init) & (alpha_f_init > 0) & (H_init > 10.0)
ice_mask = grounded | floating

H = np.zeros((Ny, Nx), dtype=np.float64)
H[ice_mask] = H_init[ice_mask]

# Flotation thickness
h_flot = np.where(bed < 0, -bed * (RHO_WATER / RHO_ICE), 0.0)

u_sim = np.clip(u_cal, -5000.0, 5000.0)
v_sim = np.clip(v_cal, -5000.0, 5000.0)

# Run 10 time steps with dt = 0.1 yr (1 full year)
dt = 0.1 # yr
n_steps = 10

H_curr = H.copy()
grd_curr = grounded.copy()
flt_curr = floating.copy()

print(f"Initial State: Grounded={np.sum(grd_curr):,}, Floating={np.sum(flt_curr):,}, Total={np.sum(grd_curr | flt_curr):,}")
M_g_curr = np.sum(H_curr[grd_curr] * cell_area[grd_curr]) * RHO_ICE * 1e-12
M_f_curr = np.sum(H_curr[flt_curr] * cell_area[flt_curr]) * RHO_ICE * 1e-12
print(f"Initial Mass: Grounded={M_g_curr:.4f} Gt, Floating={M_f_curr:.4f} Gt, Total={M_g_curr + M_f_curr:.4f} Gt")

cum_res = 0.0

for step in range(1, n_steps + 1):
    active_ice = grd_curr | flt_curr
    # Zero H outside active ice
    H_curr[~active_ice] = 0.0

    # Upwind fluxes
    u_fx = 0.5 * (u_sim[:, :-1] + u_sim[:, 1:])
    h_up_x = np.where(u_fx > 0, H_curr[:, :-1], H_curr[:, 1:])
    ds_x_f = 0.5 * (ds_x[:, :-1] + ds_x[:, 1:])
    fx = h_up_x * u_fx * ds_x_f

    v_fy = 0.5 * (v_sim[:-1, :] + v_sim[1:, :])
    h_up_y = np.where(v_fy > 0, H_curr[1:, :], H_curr[:-1, :])
    ds_y_f = 0.5 * (ds_y[:-1, :] + ds_y[1:, :])
    fy = h_up_y * v_fy * ds_y_f

    # Divergence
    div_F = np.zeros((Ny, Nx), dtype=np.float64)
    div_F[:, :-1] += fx
    div_F[:, 1:] -= fx
    div_F[1:, :] += fy
    div_F[:-1, :] -= fy

    # Boundary fluxes
    # Grounding line
    gl_x = np.sum(fx[grd_curr[:, :-1] & flt_curr[:, 1:]]) - np.sum(fx[flt_curr[:, :-1] & grd_curr[:, 1:]])
    gl_y = np.sum(fy[grd_curr[1:, :] & flt_curr[:-1, :]]) - np.sum(fy[flt_curr[1:, :] & grd_curr[:-1, :]])
    F_gl = (gl_x + gl_y) * RHO_ICE * 1e-12 # Gt / yr

    # Calving
    not_ice = ~active_ice
    calv_g_x = np.sum(fx[grd_curr[:, :-1] & not_ice[:, 1:]]) - np.sum(fx[not_ice[:, :-1] & grd_curr[:, 1:]])
    calv_g_y = np.sum(fy[grd_curr[1:, :] & not_ice[:-1, :]]) - np.sum(fy[not_ice[1:, :] & grd_curr[:-1, :]])
    F_calv_g = (calv_g_x + calv_g_y) * RHO_ICE * 1e-12

    calv_f_x = np.sum(fx[flt_curr[:, :-1] & not_ice[:, 1:]]) - np.sum(fx[not_ice[:, :-1] & flt_curr[:, 1:]])
    calv_f_y = np.sum(fy[flt_curr[1:, :] & not_ice[:-1, :]]) - np.sum(fy[not_ice[1:, :] & flt_curr[:-1, :]])
    F_calv_f = (calv_f_x + calv_f_y) * RHO_ICE * 1e-12

    # SMB
    smb_g = np.sum(smb[grd_curr] * cell_area[grd_curr]) * 1e-12 # Gt / yr
    smb_f = np.sum(smb[flt_curr] * cell_area[flt_curr]) * 1e-12

    # Thickness update
    dH = dt * (smb / RHO_ICE - div_F / cell_area)
    H_next = H_curr.copy()
    H_next[active_ice] = H_curr[active_ice] + dH[active_ice]

    # Pre-migration mass
    M_g_post = np.sum(H_next[grd_curr] * cell_area[grd_curr]) * RHO_ICE * 1e-12
    M_f_post = np.sum(H_next[flt_curr] * cell_area[flt_curr]) * RHO_ICE * 1e-12

    # Migration
    hf_next = H_next - h_flot
    unground = grd_curr & (hf_next <= 0) & (bed < 0) & (H_next > 10.0)
    reground = flt_curr & (hf_next > 0) & (H_next > 10.0)

    M_unground = np.sum(H_next[unground] * cell_area[unground]) * RHO_ICE * 1e-12
    M_reground = np.sum(H_next[reground] * cell_area[reground]) * RHO_ICE * 1e-12

    grd_next = (grd_curr & (~unground)) | reground
    flt_next = (flt_curr & (~reground)) | unground

    M_g_final = np.sum(H_next[grd_next] * cell_area[grd_next]) * RHO_ICE * 1e-12
    M_f_final = np.sum(H_next[flt_next] * cell_area[flt_next]) * RHO_ICE * 1e-12

    # System change
    actual_dM = (M_g_final + M_f_final) - (M_g_curr + M_f_curr)
    pred_dM = (smb_g + smb_f - F_calv_g - F_calv_f) * dt
    res = abs(actual_dM - pred_dM)
    cum_res += res

    print(f"Step {step:2d} (t={step*dt:.1f}yr): dM_act={actual_dM:+.4f} Gt, pred={pred_dM:+.4f} Gt, "
          f"res={res:.14e} Gt, ungrd={np.sum(unground)} ({M_unground:.3f}Gt), regrd={np.sum(reground)} ({M_reground:.3f}Gt)")

    # Advance
    H_curr = H_next
    grd_curr = grd_next
    flt_curr = flt_next
    M_g_curr = M_g_final
    M_f_curr = M_f_final

print(f"\nFinal State after 1 year: Grounded={np.sum(grd_curr):,}, Floating={np.sum(flt_curr):,}")
print(f"Final Mass: Grounded={M_g_curr:.4f} Gt, Floating={M_f_curr:.4f} Gt, Total={M_g_curr + M_f_curr:.4f} Gt")
print(f"Cumulative Numerical Mass Residual over 10 steps: {cum_res:.14e} Gt")
