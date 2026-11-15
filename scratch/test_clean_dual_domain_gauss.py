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

div_F = np.zeros((Ny, Nx), dtype=np.float64)
div_F[:, :-1] += fx
div_F[:, 1:] -= fx
div_F[1:, :] += fy
div_F[:-1, :] -= fy

# Let's check: on the grounded domain:
# The sum of div_F over grounded is:
sum_div_g = np.sum(div_F[grounded]) * RHO_ICE * 1e-12
# The sum of div_F over floating is:
sum_div_f = np.sum(div_F[floating]) * RHO_ICE * 1e-12
# The sum of div_F over ice_mask is:
sum_div_tot = np.sum(div_F[ice_mask]) * RHO_ICE * 1e-12

print(f"sum_div_g:   {sum_div_g:.8f} Gt/yr")
print(f"sum_div_f:   {sum_div_f:.8f} Gt/yr")
print(f"sum_div_tot: {sum_div_tot:.8f} Gt/yr")
print(f"sum_div_g + sum_div_f == sum_div_tot? {abs((sum_div_g + sum_div_f) - sum_div_tot):.14e}")

# Now what boundary faces cross between grounded and outside grounded?
# Any face between a grounded cell and a non-grounded cell!
# 1. East/West:
# If col j is grounded and col j+1 is NOT grounded: flux leaving col j is +fx[:, j]
# If col j is NOT grounded and col j+1 is grounded: flux entering col j+1 is -fx[:, j], so flux leaving grounded is -fx[:, j]!
outflow_g_x = np.sum(fx[grounded[:, :-1] & (~grounded[:, 1:])]) - np.sum(fx[(~grounded[:, :-1]) & grounded[:, 1:]])
outflow_g_y = np.sum(fy[grounded[1:, :] & (~grounded[:-1, :])]) - np.sum(fy[(~grounded[1:, :]) & grounded[:-1, :]])

outflow_g_Gt = (outflow_g_x + outflow_g_y) * RHO_ICE * 1e-12
print(f"True boundary outflow from Grounded: {outflow_g_Gt:.8f} Gt/yr")
print(f"Difference |sum_div_g - outflow_g|:   {abs(sum_div_g - outflow_g_Gt):.14e} Gt/yr")

# Now split outflow_g into:
# (a) faces entering floating ice (Grounding line flux F_gl)
# (b) faces entering non-ice (calving / margin flux F_calv_g)
flx_gl_x = np.sum(fx[grounded[:, :-1] & floating[:, 1:]]) - np.sum(fx[floating[:, :-1] & grounded[:, 1:]])
flx_gl_y = np.sum(fy[grounded[1:, :] & floating[:-1, :]]) - np.sum(fy[floating[1:, :] & grounded[:-1, :]])
F_gl_Gt = (flx_gl_x + flx_gl_y) * RHO_ICE * 1e-12

flx_calv_g_x = np.sum(fx[grounded[:, :-1] & (~ice_mask[:, 1:])]) - np.sum(fx[(~ice_mask[:, :-1]) & grounded[:, 1:]])
flx_calv_g_y = np.sum(fy[grounded[1:, :] & (~ice_mask[:-1, :])]) - np.sum(fy[(~ice_mask[1:, :]) & grounded[:-1, :]])
F_calv_g_Gt = (flx_calv_g_x + flx_calv_g_y) * RHO_ICE * 1e-12

print(f"\nBreakdown of Grounded Outflow:")
print(f"  F_gl (to floating):     {F_gl_Gt:.8f} Gt/yr")
print(f"  F_calv_g (to non-ice):  {F_calv_g_Gt:.8f} Gt/yr")
print(f"  F_gl + F_calv_g:        {(F_gl_Gt + F_calv_g_Gt):.8f} Gt/yr")
print(f"  Difference:             {abs(outflow_g_Gt - (F_gl_Gt + F_calv_g_Gt)):.14e} Gt/yr")

# Floating domain outflow:
outflow_f_x = np.sum(fx[floating[:, :-1] & (~floating[:, 1:])]) - np.sum(fx[(~floating[:, :-1]) & floating[:, 1:]])
outflow_f_y = np.sum(fy[floating[1:, :] & (~floating[:-1, :])]) - np.sum(fy[(~floating[1:, :]) & floating[:-1, :]])
outflow_f_Gt = (outflow_f_x + outflow_f_y) * RHO_ICE * 1e-12

flx_calv_f_x = np.sum(fx[floating[:, :-1] & (~ice_mask[:, 1:])]) - np.sum(fx[(~ice_mask[:, :-1]) & floating[:, 1:]])
flx_calv_f_y = np.sum(fy[floating[1:, :] & (~ice_mask[:-1, :])]) - np.sum(fy[(~ice_mask[1:, :]) & floating[:-1, :]])
F_calv_f_Gt = (flx_calv_f_x + flx_calv_f_y) * RHO_ICE * 1e-12

print(f"\nFloating Domain Outflow:")
print(f"  Total outflow:          {outflow_f_Gt:.8f} Gt/yr")
print(f"  Calving (to non-ice):   {F_calv_f_Gt:.8f} Gt/yr")
print(f"  Inflow from GL (-F_gl): {-F_gl_Gt:.8f} Gt/yr")
print(f"  F_calv_f - F_gl:        {(F_calv_f_Gt - F_gl_Gt):.8f} Gt/yr")
print(f"  Difference:             {abs(outflow_f_Gt - (F_calv_f_Gt - F_gl_Gt)):.14e} Gt/yr")

print(f"\nSum of Outflows: outflow_g + outflow_f = {(outflow_g_Gt + outflow_f_Gt):.8f} Gt/yr")
print(f"Total Calving:   F_calv_g + F_calv_f  = {(F_calv_g_Gt + F_calv_f_Gt):.8f} Gt/yr")
print(f"Internal Cancellation: F_gl - F_gl     = 0.00000000000000 Gt/yr")
print(f"Numerical Difference:                  {abs((outflow_g_Gt + outflow_f_Gt) - (F_calv_g_Gt + F_calv_f_Gt)):.14e} Gt/yr")
