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

grounded = (alpha_g_init > 0) & (H_init > 10.0)
floating = (alpha_f_init > 0) & (H_init > 10.0)
ice_mask = grounded | floating

H = np.zeros((Ny, Nx), dtype=np.float64)
H[ice_mask] = H_init[ice_mask]

# Flotation thickness
h_flot = np.where(bed < 0, -bed * (RHO_WATER / RHO_ICE), 0.0)

u_sim = np.clip(u_cal, -5000.0, 5000.0)
v_sim = np.clip(v_cal, -5000.0, 5000.0)

# Upwind fluxes across X faces
u_fx = 0.5 * (u_sim[:, :-1] + u_sim[:, 1:])
h_up_x = np.where(u_fx > 0, H[:, :-1], H[:, 1:])
ds_x_f = 0.5 * (ds_x[:, :-1] + ds_x[:, 1:])
fx = h_up_x * u_fx * ds_x_f

# Upwind fluxes across Y faces
v_fy = 0.5 * (v_sim[:-1, :] + v_sim[1:, :])
h_up_y = np.where(v_fy > 0, H[1:, :], H[:-1, :])
ds_y_f = 0.5 * (ds_y[:-1, :] + ds_y[1:, :])
fy = h_up_y * v_fy * ds_y_f

# Finite volume divergence
div_F = np.zeros((Ny, Nx), dtype=np.float64)
div_F[:, :-1] += fx
div_F[:, 1:] -= fx
div_F[1:, :] += fy
div_F[:-1, :] -= fy

# Boundary fluxes
# 1. Grounding line flux F_gl:
gl_fx = np.where(grounded[:, :-1] & floating[:, 1:], fx,
                 np.where(floating[:, :-1] & grounded[:, 1:], -fx, 0.0))
gl_fy = np.where(grounded[1:, :] & floating[:-1, :], fy,
                 np.where(floating[1:, :] & grounded[:-1, :], -fy, 0.0))
F_gl_vol = np.sum(gl_fx) + np.sum(gl_fy)
F_gl_Gt = F_gl_vol * RHO_ICE * 1e-12

# 2. Grounded calving flux F_calv_g (grounded to outside grounded & floating):
not_ice = ~ice_mask
calv_g_fx = np.where(grounded[:, :-1] & not_ice[:, 1:], fx,
                     np.where(not_ice[:, :-1] & grounded[:, 1:], -fx, 0.0))
calv_g_fy = np.where(grounded[1:, :] & not_ice[:-1, :], fy,
                     np.where(not_ice[1:, :] & grounded[:-1, :], -fy, 0.0))
F_calv_g_vol = np.sum(calv_g_fx) + np.sum(calv_g_fy)
F_calv_g_Gt = F_calv_g_vol * RHO_ICE * 1e-12

# 3. Floating calving flux F_calv_f (floating to outside grounded & floating):
calv_f_fx = np.where(floating[:, :-1] & not_ice[:, 1:], fx,
                     np.where(not_ice[:, :-1] & floating[:, 1:], -fx, 0.0))
calv_f_fy = np.where(floating[1:, :] & not_ice[:-1, :], fy,
                     np.where(not_ice[1:, :] & floating[:-1, :], -fy, 0.0))
F_calv_f_vol = np.sum(calv_f_fx) + np.sum(calv_f_fy)
F_calv_f_Gt = F_calv_f_vol * RHO_ICE * 1e-12

# Time step dt = 0.1 yr
dt = 0.1
smb_g_step = np.sum(smb[grounded] * cell_area[grounded]) * 1e-12 * dt
smb_f_step = np.sum(smb[floating] * cell_area[floating]) * 1e-12 * dt

# Initial masses
M_g_init = np.sum(H[grounded] * cell_area[grounded]) * RHO_ICE * 1e-12
M_f_init = np.sum(H[floating] * cell_area[floating]) * RHO_ICE * 1e-12

# Thickness update
dH = dt * (smb / RHO_ICE - div_F / cell_area)
H_next = np.maximum(0.0, H + dH)

# Final mass BEFORE migration
M_g_post = np.sum(H_next[grounded] * cell_area[grounded]) * RHO_ICE * 1e-12
M_f_post = np.sum(H_next[floating] * cell_area[floating]) * RHO_ICE * 1e-12

# Grounded mass change before migration
dM_g_flux = M_g_post - M_g_init
pred_dM_g_flux = smb_g_step - (F_gl_Gt + F_calv_g_Gt) * dt

# Floating mass change before migration
dM_f_flux = M_f_post - M_f_init
pred_dM_f_flux = smb_f_step - (F_calv_f_Gt - F_gl_Gt) * dt

print("--- Pre-Migration Flux Balance ---")
print(f"Grounded: Actual dMg = {dM_g_flux:.8f} Gt, Pred = {pred_dM_g_flux:.8f} Gt, Diff = {abs(dM_g_flux - pred_dM_g_flux):.14e} Gt")
print(f"Floating: Actual dMf = {dM_f_flux:.8f} Gt, Pred = {pred_dM_f_flux:.8f} Gt, Diff = {abs(dM_f_flux - pred_dM_f_flux):.14e} Gt")
print(f"System:   Actual dM  = {dM_g_flux + dM_f_flux:.8f} Gt, Pred = {pred_dM_g_flux + pred_dM_f_flux:.8f} Gt, Diff = {abs((dM_g_flux + dM_f_flux) - (pred_dM_g_flux + pred_dM_f_flux)):.14e} Gt")

# Now apply Grounding Line Flotation Tracking:
# A grounded cell ungrounds if H_next <= h_flot (and bed < 0)
hf_curr = H[grounded] - h_flot[grounded]
# Only check migration on cells that actually cross flotation
ungrounded_cells = grounded.copy()
ungrounded_cells[grounded] = (H_next[grounded] <= h_flot[grounded]) & (bed[grounded] < 0) & (H_next[grounded] > 10.0) & (hf_curr > 0)
M_unground = np.sum(H_next[ungrounded_cells] * cell_area[ungrounded_cells]) * RHO_ICE * 1e-12

# A floating cell grounds if H_next > h_flot
hf_float_curr = H[floating] - h_flot[floating]
regrounded_cells = floating.copy()
regrounded_cells[floating] = (H_next[floating] > h_flot[floating]) & (H_next[floating] > 10.0) & (hf_float_curr <= 0)
M_reground = np.sum(H_next[regrounded_cells] * cell_area[regrounded_cells]) * RHO_ICE * 1e-12

print(f"\nMigration tracking:")
print(f"  Ungrounded cells: {np.sum(ungrounded_cells)} ({M_unground:.4f} Gt)")
print(f"  Regrounded cells: {np.sum(regrounded_cells)} ({M_reground:.4f} Gt)")

# Updated domain masks
grounded_next = (grounded & (~ungrounded_cells)) | regrounded_cells
floating_next = (floating & (~regrounded_cells)) | ungrounded_cells

M_g_final = np.sum(H_next[grounded_next] * cell_area[grounded_next]) * RHO_ICE * 1e-12
M_f_final = np.sum(H_next[floating_next] * cell_area[floating_next]) * RHO_ICE * 1e-12

total_actual_dM = (M_g_final + M_f_final) - (M_g_init + M_f_init)
total_pred_dM = (smb_g_step + smb_f_step) - (F_calv_g_Gt + F_calv_f_Gt) * dt

print("\n--- Post-Migration System Mass Conservation ---")
print(f"Total Actual dM:    {total_actual_dM:.8f} Gt")
print(f"Total Predicted dM: {total_pred_dM:.8f} Gt")
print(f"Numerical Residual: {abs(total_actual_dM - total_pred_dM):.14e} Gt")
