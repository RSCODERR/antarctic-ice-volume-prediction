import netCDF4 as nc
import numpy as np

path_u = "antarctic-ice-volume-prediction/data/processed/stage4_5_3/stage4_5_3_unified_physical_fields.nc"
path_c = "antarctic-ice-volume-prediction/data/processed/stage4_7/stage4_7_calibrated_velocity.nc"

ds_u = nc.Dataset(path_u)
H_init = ds_u.variables["thickness"][:].astype(np.float64)
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

k_scale = np.sqrt((dx * dy) / cell_area)
ds_x = dy / k_scale
ds_y = dx / k_scale

# Mutually exclusive partition:
grounded = (alpha_g_init >= alpha_f_init) & (alpha_g_init > 0) & (H_init > 10.0)
floating = (alpha_f_init > alpha_g_init) & (alpha_f_init > 0) & (H_init > 10.0)
ice_mask = grounded | floating

print(f"Mutually exclusive cells: Grounded={np.sum(grounded):,}, Floating={np.sum(floating):,}, Total={np.sum(ice_mask):,}")
print(f"Overlap (must be 0): {np.sum(grounded & floating)}")

H = np.zeros((Ny, Nx), dtype=np.float64)
H[ice_mask] = H_init[ice_mask]

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

# Cell divergence
div_F = np.zeros((Ny, Nx), dtype=np.float64)
div_F[:, :-1] += fx
div_F[:, 1:] -= fx
div_F[1:, :] += fy
div_F[:-1, :] -= fy

sum_div_g = np.sum(div_F[grounded]) * RHO_ICE * 1e-12
sum_div_f = np.sum(div_F[floating]) * RHO_ICE * 1e-12
sum_div_tot = np.sum(div_F[ice_mask]) * RHO_ICE * 1e-12

print(f"\nsum_div_g:   {sum_div_g:.8f} Gt/yr")
print(f"sum_div_f:   {sum_div_f:.8f} Gt/yr")
print(f"sum_div_tot: {sum_div_tot:.8f} Gt/yr")
print(f"sum_div_g + sum_div_f == sum_div_tot? Difference = {abs((sum_div_g + sum_div_f) - sum_div_tot):.14e}")

# Exact boundary face fluxes:
# 1. Grounding line flux: faces between grounded and floating
flx_gl_x = np.sum(fx[grounded[:, :-1] & floating[:, 1:]]) - np.sum(fx[floating[:, :-1] & grounded[:, 1:]])
flx_gl_y = np.sum(fy[grounded[1:, :] & floating[:-1, :]]) - np.sum(fy[floating[1:, :] & grounded[:-1, :]])
F_gl_Gt = (flx_gl_x + flx_gl_y) * RHO_ICE * 1e-12

# 2. Grounded calving flux: faces between grounded and outside ice_mask
flx_calv_g_x = np.sum(fx[grounded[:, :-1] & (~ice_mask[:, 1:])]) - np.sum(fx[(~ice_mask[:, :-1]) & grounded[:, 1:]])
flx_calv_g_y = np.sum(fy[grounded[1:, :] & (~ice_mask[:-1, :])]) - np.sum(fy[(~ice_mask[1:, :]) & grounded[:-1, :]])
F_calv_g_Gt = (flx_calv_g_x + flx_calv_g_y) * RHO_ICE * 1e-12

# 3. Floating calving flux: faces between floating and outside ice_mask
flx_calv_f_x = np.sum(fx[floating[:, :-1] & (~ice_mask[:, 1:])]) - np.sum(fx[(~ice_mask[:, :-1]) & floating[:, 1:]])
flx_calv_f_y = np.sum(fy[floating[1:, :] & (~ice_mask[:-1, :])]) - np.sum(fy[(~ice_mask[1:, :]) & floating[:-1, :]])
F_calv_f_Gt = (flx_calv_f_x + flx_calv_f_y) * RHO_ICE * 1e-12

print(f"\n--- Grounded Ledger ---")
print(f"  Divergence on Grounded: {sum_div_g:.8f} Gt/yr")
print(f"  F_gl + F_calv_g:        {(F_gl_Gt + F_calv_g_Gt):.8f} Gt/yr")
print(f"  Residual:               {abs(sum_div_g - (F_gl_Gt + F_calv_g_Gt)):.14e} Gt/yr")

print(f"\n--- Floating Shelf Ledger ---")
print(f"  Divergence on Floating: {sum_div_f:.8f} Gt/yr")
print(f"  F_calv_f - F_gl:        {(F_calv_f_Gt - F_gl_Gt):.8f} Gt/yr")
print(f"  Residual:               {abs(sum_div_f - (F_calv_f_Gt - F_gl_Gt)):.14e} Gt/yr")

print(f"\n--- Combined System Ledger ---")
print(f"  Sum of Divergence:      {(sum_div_g + sum_div_f):.8f} Gt/yr")
print(f"  Total Calving:          {(F_calv_g_Gt + F_calv_f_Gt):.8f} Gt/yr")
print(f"  Internal Cancellation:  {F_gl_Gt:.8f} - {F_gl_Gt:.8f} = 0.00000000 Gt/yr")
print(f"  System Residual:        {abs((sum_div_g + sum_div_f) - (F_calv_g_Gt + F_calv_f_Gt)):.14e} Gt/yr")
