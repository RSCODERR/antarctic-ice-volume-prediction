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
ocean_mask = ~ice_mask

H = np.where(ice_mask, H_init, 0.0)
u_sim = np.clip(u_cal, -5000.0, 5000.0)
v_sim = np.clip(v_cal, -5000.0, 5000.0)

# Face fluxes
u_fx = 0.5 * (u_sim[:, :-1] + u_sim[:, 1:])
h_up_x = np.where(u_fx > 0, H[:, :-1], H[:, 1:])
ds_x_f = 0.5 * (ds_x[:, :-1] + ds_x[:, 1:])
fx = h_up_x * u_fx * ds_x_f

v_fy = 0.5 * (v_sim[:-1, :] + v_sim[1:, :])
h_up_y = np.where(v_fy > 0, H[1:, :], H[:-1, :])
ds_y_f = 0.5 * (ds_y[:-1, :] + ds_y[1:, :])
fy = h_up_y * v_fy * ds_y_f

# Divergence
div_F = np.zeros((Ny, Nx), dtype=np.float64)
div_F[:, :-1] += fx
div_F[:, 1:] -= fx
div_F[1:, :] += fy
div_F[:-1, :] -= fy

# Separate sums
div_g_vol = np.sum(div_F[grounded])
div_f_vol = np.sum(div_F[floating])

div_g_Gt = div_g_vol * RHO_ICE * 1e-12
div_f_Gt = div_f_vol * RHO_ICE * 1e-12

# Explicit boundary face fluxes:
# 1. Grounding line: grounded to floating (leaving grounded, entering floating)
# X: col j grounded, col j+1 floating, fx > 0 (leaves col j, enters col j+1)
gl_x_e = fx * (grounded[:, :-1] & floating[:, 1:] & (u_fx > 0))
# X: col j floating, col j+1 grounded, fx < 0 (ice moves west, leaves col j+1, enters col j)
gl_x_w = -fx * (floating[:, :-1] & grounded[:, 1:] & (u_fx < 0))
# Y: row i floating, row i+1 grounded, fy > 0 (moves north, leaves row i+1, enters row i)
gl_y_n = fy * (floating[:-1, :] & grounded[1:, :] & (v_fy > 0))
# Y: row i grounded, row i+1 floating, fy < 0 (moves south, leaves row i, enters row i+1)
gl_y_s = -fy * (grounded[:-1, :] & floating[1:, :] & (v_fy < 0))

f_gl_vol = np.sum(gl_x_e) + np.sum(gl_x_w) + np.sum(gl_y_n) + np.sum(gl_y_s)
f_gl_Gt = f_gl_vol * RHO_ICE * 1e-12

# 2. Grounded calving (grounded to ocean)
calv_g_x_e = fx * (grounded[:, :-1] & ocean_mask[:, 1:] & (u_fx > 0))
calv_g_x_w = -fx * (ocean_mask[:, :-1] & grounded[:, 1:] & (u_fx < 0))
calv_g_y_n = fy * (ocean_mask[:-1, :] & grounded[1:, :] & (v_fy > 0))
calv_g_y_s = -fy * (grounded[:-1, :] & ocean_mask[1:, :] & (v_fy < 0))
f_calv_g_vol = np.sum(calv_g_x_e) + np.sum(calv_g_x_w) + np.sum(calv_g_y_n) + np.sum(calv_g_y_s)
f_calv_g_Gt = f_calv_g_vol * RHO_ICE * 1e-12

# 3. Floating calving (floating to ocean)
calv_f_x_e = fx * (floating[:, :-1] & ocean_mask[:, 1:] & (u_fx > 0))
calv_f_x_w = -fx * (ocean_mask[:, :-1] & floating[:, 1:] & (u_fx < 0))
calv_f_y_n = fy * (ocean_mask[:-1, :] & floating[1:, :] & (v_fy > 0))
calv_f_y_s = -fy * (floating[:-1, :] & ocean_mask[1:, :] & (v_fy < 0))
f_calv_f_vol = np.sum(calv_f_x_e) + np.sum(calv_f_x_w) + np.sum(calv_f_y_n) + np.sum(calv_f_y_s)
f_calv_f_Gt = f_calv_f_vol * RHO_ICE * 1e-12

print(f"Grounded Domain Divergence: {div_g_Gt:.6f} Gt/yr")
print(f"  Expected (GL + Calv_g):  {(f_gl_Gt + f_calv_g_Gt):.6f} Gt/yr")
print(f"  Residual on Grounded:    {abs(div_g_Gt - (f_gl_Gt + f_calv_g_Gt)):.12e} Gt/yr")

print(f"\nFloating Domain Divergence: {div_f_Gt:.6f} Gt/yr")
print(f"  Expected (Calv_f - GL):  {(f_calv_f_Gt - f_gl_Gt):.6f} Gt/yr")
print(f"  Residual on Floating:    {abs(div_f_Gt - (f_calv_f_Gt - f_gl_Gt)):.12e} Gt/yr")

print(f"\nSystem Combined Divergence: {div_g_Gt + div_f_Gt:.6f} Gt/yr")
print(f"  Total Calving (g + f):   {f_calv_g_Gt + f_calv_f_Gt:.6f} Gt/yr")
print(f"  Internal Cancellation:   {f_gl_Gt:.6f} - {f_gl_Gt:.6f} = 0.000000 Gt/yr")
print(f"  System Residual:         {abs((div_g_Gt + div_f_Gt) - (f_calv_g_Gt + f_calv_f_Gt)):.12e} Gt/yr")
