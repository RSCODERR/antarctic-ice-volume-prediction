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

k_scale = np.sqrt((dx * dy) / cell_area)
ds_x = dy / k_scale
ds_y = dx / k_scale

grounded = (alpha_g_init > 0) & (H_init > 10.0)
floating = (alpha_f_init > 0) & (H_init > 10.0)
ice_mask = grounded | floating

# H is zero outside ice domain
H = np.zeros((Ny, Nx), dtype=np.float64)
H[ice_mask] = H_init[ice_mask]

u_sim = np.clip(u_cal, -5000.0, 5000.0)
v_sim = np.clip(v_cal, -5000.0, 5000.0)

# Upwind fluxes across X faces (j between col j and col j+1)
# Eastward velocity
u_fx = 0.5 * (u_sim[:, :-1] + u_sim[:, 1:])
h_up_x = np.where(u_fx > 0, H[:, :-1], H[:, 1:])
ds_x_f = 0.5 * (ds_x[:, :-1] + ds_x[:, 1:])
fx = h_up_x * u_fx * ds_x_f # m^3 / yr

# Upwind fluxes across Y faces (i between row i and row i+1)
# Northward velocity (row i+1 to row i)
v_fy = 0.5 * (v_sim[:-1, :] + v_sim[1:, :])
h_up_y = np.where(v_fy > 0, H[1:, :], H[:-1, :])
ds_y_f = 0.5 * (ds_y[:-1, :] + ds_y[1:, :])
fy = h_up_y * v_fy * ds_y_f # m^3 / yr

# Finite volume net outflow per cell:
div_F = np.zeros((Ny, Nx), dtype=np.float64)
div_F[:, :-1] += fx # leaves col j
div_F[:, 1:] -= fx  # enters col j+1
div_F[1:, :] += fy  # leaves row i+1
div_F[:-1, :] -= fy # enters row i

# Algebraic boundary fluxes:
# A face is a boundary face if ONE cell is in the domain and the other is NOT!
# 1. Grounding line flux F_gl: defined as net flux leaving grounded and entering floating
# X faces between grounded and floating:
# If col j grounded, col j+1 floating: flux leaving col j into col j+1 is +fx[:, j]
gl_fx = np.where(grounded[:, :-1] & floating[:, 1:], fx,
                 np.where(floating[:, :-1] & grounded[:, 1:], -fx, 0.0))
# Y faces between grounded and floating:
# If row i+1 grounded, row i floating: flux leaving row i+1 into row i is +fy[i, :]
gl_fy = np.where(grounded[1:, :] & floating[:-1, :], fy,
                 np.where(floating[1:, :] & grounded[:-1, :], -fy, 0.0))

F_gl_vol = np.sum(gl_fx) + np.sum(gl_fy)
F_gl_Gt = F_gl_vol * RHO_ICE * 1e-12

# 2. Grounded calving flux F_calv_g: net flux leaving grounded and entering ocean (non-ice)
calv_g_fx = np.where(grounded[:, :-1] & (~ice_mask[:, 1:]), fx,
                     np.where((~ice_mask[:, :-1]) & grounded[:, 1:], -fx, 0.0))
calv_g_fy = np.where(grounded[1:, :] & (~ice_mask[:-1, :]), fy,
                     np.where((~ice_mask[1:, :]) & grounded[:-1, :], -fy, 0.0))
F_calv_g_vol = np.sum(calv_g_fx) + np.sum(calv_g_fy)
F_calv_g_Gt = F_calv_g_vol * RHO_ICE * 1e-12

# 3. Floating calving flux F_calv_f: net flux leaving floating and entering ocean (non-ice)
calv_f_fx = np.where(floating[:, :-1] & (~ice_mask[:, 1:]), fx,
                     np.where((~ice_mask[:, :-1]) & floating[:, 1:], -fx, 0.0))
calv_f_fy = np.where(floating[1:, :] & (~ice_mask[:-1, :]), fy,
                     np.where((~ice_mask[1:, :]) & floating[:-1, :], -fy, 0.0))
F_calv_f_vol = np.sum(calv_f_fx) + np.sum(calv_f_fy)
F_calv_f_Gt = F_calv_f_vol * RHO_ICE * 1e-12

# Grounded divergence sum
sum_div_g_vol = np.sum(div_F[grounded])
sum_div_g_Gt = sum_div_g_vol * RHO_ICE * 1e-12

# Floating divergence sum
sum_div_f_vol = np.sum(div_F[floating])
sum_div_f_Gt = sum_div_f_vol * RHO_ICE * 1e-12

print("--- Grounded Domain ---")
print(f"Sum of div_F on Grounded: {sum_div_g_Gt:.8f} Gt/yr")
print(f"F_gl + F_calv_g:          {(F_gl_Gt + F_calv_g_Gt):.8f} Gt/yr")
print(f"Residual on Grounded:     {abs(sum_div_g_Gt - (F_gl_Gt + F_calv_g_Gt)):.14e} Gt/yr")

print("\n--- Floating Shelf Domain ---")
print(f"Sum of div_F on Floating: {sum_div_f_Gt:.8f} Gt/yr")
print(f"F_calv_f - F_gl:          {(F_calv_f_Gt - F_gl_Gt):.8f} Gt/yr")
print(f"Residual on Floating:     {abs(sum_div_f_Gt - (F_calv_f_Gt - F_gl_Gt)):.14e} Gt/yr")

print("\n--- Combined System Conservation ---")
print(f"Sum of div_F (G + F):     {(sum_div_g_Gt + sum_div_f_Gt):.8f} Gt/yr")
print(f"Total Calving (g + f):    {(F_calv_g_Gt + F_calv_f_Gt):.8f} Gt/yr")
print(f"Internal Cancellation:    {F_gl_Gt:.8f} - {F_gl_Gt:.8f} = 0.00000000 Gt/yr")
print(f"System Numerical Residual: {abs((sum_div_g_Gt + sum_div_f_Gt) - (F_calv_g_Gt + F_calv_f_Gt)):.14e} Gt/yr")
