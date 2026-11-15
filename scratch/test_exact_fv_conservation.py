import netCDF4 as nc
import numpy as np

path_u = "antarctic-ice-volume-prediction/data/processed/stage4_5_3/stage4_5_3_unified_physical_fields.nc"
path_c = "antarctic-ice-volume-prediction/data/processed/stage4_7/stage4_7_calibrated_velocity.nc"

ds_u = nc.Dataset(path_u)
H_init = ds_u.variables["thickness"][:].astype(np.float64)
bed = ds_u.variables["bed"][:].astype(np.float64)
smb = ds_u.variables["smb"][:].astype(np.float64) # mm w.e. / yr
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

# Active ice mask
grounded = (alpha_g_init > 0) & (H_init > 10.0)
floating = (alpha_f_init > 0) & (H_init > 10.0)
ice_mask = grounded | floating

# Flotation thickness
h_flot = np.where(bed < 0, -bed * (RHO_WATER / RHO_ICE), 0.0)

# Velocity
u_sim = np.clip(u_cal, -5000.0, 5000.0)
v_sim = np.clip(v_cal, -5000.0, 5000.0)

# Let's verify exact discrete conservation:
# Upwind fluxes across all X faces (i, j to i, j+1)
u_fx = 0.5 * (u_sim[:, :-1] + u_sim[:, 1:])
h_up_x = np.where(u_fx > 0, H_init[:, :-1], H_init[:, 1:])
ds_x_f = 0.5 * (ds_x[:, :-1] + ds_x[:, 1:])
fx = h_up_x * u_fx * ds_x_f # m^3 / yr

# Only allow flux across face if at least one cell is ice
# If both cells are not ice, flux is 0
face_x_active = ice_mask[:, :-1] | ice_mask[:, 1:]
fx = np.where(face_x_active, fx, 0.0)

# Same for Y
v_fy = 0.5 * (v_sim[:-1, :] + v_sim[1:, :])
h_up_y = np.where(v_fy > 0, H_init[1:, :], H_init[:-1, :])
ds_y_f = 0.5 * (ds_y[:-1, :] + ds_y[1:, :])
fy = h_up_y * v_fy * ds_y_f
face_y_active = ice_mask[:-1, :] | ice_mask[1:, :]
fy = np.where(face_y_active, fy, 0.0)

# Identify boundary faces where flux leaves the ice domain into ocean:
# X boundaries:
calv_x_east = (ice_mask[:, :-1] & (~ice_mask[:, 1:])) & (u_fx > 0) # leaves east
calv_x_west = ((~ice_mask[:, :-1]) & ice_mask[:, 1:]) & (u_fx < 0) # leaves west
calving_flux_x = np.sum(fx[calv_x_east]) + np.sum(-fx[calv_x_west])

# Y boundaries:
calv_y_north = ((~ice_mask[:-1, :]) & ice_mask[1:, :]) & (v_fy > 0) # leaves north
calv_y_south = (ice_mask[:-1, :] & (~ice_mask[1:, :])) & (v_fy < 0) # leaves south
calving_flux_y = np.sum(fy[calv_y_north]) + np.sum(-fy[calv_y_south])

total_calving_m3 = calving_flux_x + calving_flux_y
total_calving_Gt = total_calving_m3 * RHO_ICE * 1e-12

print(f"Total calving volume flux: {total_calving_m3:.2f} m^3/yr ({total_calving_Gt:.4f} Gt/yr)")

# Finite volume net divergence on ice cells:
div_F = np.zeros((Ny, Nx), dtype=np.float64)
# Internal fluxes and exit fluxes
div_F[:, 1:] += fx
div_F[:, :-1] -= fx
div_F[1:, :] += fy
div_F[:-1, :] -= fy

# Check sum of div_F over ice_mask:
sum_div_ice = np.sum(div_F[ice_mask])
print(f"Sum of div_F on ice cells: {sum_div_ice:.2f} m^3/yr ({sum_div_ice * RHO_ICE * 1e-12:.4f} Gt/yr)")
print(f"Difference between sum(div_F[ice]) and boundary calving flux: {abs(sum_div_ice - total_calving_m3):.8e} m^3/yr")

# Now add SMB:
smb_tot_Gt = np.sum(smb[ice_mask] * cell_area[ice_mask]) * 1e-12
pred_net_dM_Gt = smb_tot_Gt - total_calving_Gt

# Compute cell-by-cell dH:
dt = 0.1 # yr
dH = dt * (smb[ice_mask]/RHO_ICE - div_F[ice_mask] / cell_area[ice_mask])
actual_net_dM_Gt = np.sum(dH * cell_area[ice_mask]) * RHO_ICE * 1e-12 / dt

print(f"Predicted net dM/dt: {pred_net_dM_Gt:.6f} Gt/yr")
print(f"Actual cell-integrated dM/dt: {actual_net_dM_Gt:.6f} Gt/yr")
print(f"Numerical residual |Actual - Pred|: {abs(actual_net_dM_Gt - pred_net_dM_Gt):.10e} Gt/yr")
