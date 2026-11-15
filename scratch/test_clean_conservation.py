import netCDF4 as nc
import numpy as np

path_u = "antarctic-ice-volume-prediction/data/processed/stage4_5_3/stage4_5_3_unified_physical_fields.nc"
path_c = "antarctic-ice-volume-prediction/data/processed/stage4_7/stage4_7_calibrated_velocity.nc"

ds_u = nc.Dataset(path_u)
H_init = ds_u.variables["thickness"][:].astype(np.float64)
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

k_scale = np.sqrt((dx * dy) / cell_area)
ds_x = dy / k_scale
ds_y = dx / k_scale

grounded = (alpha_g_init > 0) & (H_init > 10.0)
floating = (alpha_f_init > 0) & (H_init > 10.0)
ice_mask = grounded | floating

# Ensure H is zero outside ice domain
H = np.where(ice_mask, H_init, 0.0)
u_sim = np.clip(u_cal, -5000.0, 5000.0)
v_sim = np.clip(v_cal, -5000.0, 5000.0)

# Upwind fluxes across X faces (interface j is between col j and col j+1)
# Positive fx means ice flows from col j to col j+1 (eastward)
u_fx = 0.5 * (u_sim[:, :-1] + u_sim[:, 1:])
h_up_x = np.where(u_fx > 0, H[:, :-1], H[:, 1:])
ds_x_f = 0.5 * (ds_x[:, :-1] + ds_x[:, 1:])
fx = h_up_x * u_fx * ds_x_f # m^3 / yr

# Upwind fluxes across Y faces (interface i is between row i and row i+1)
# Positive v means ice flows northward, which is from row i+1 to row i!
# So let's define fy as NORTHWARD flux: positive fy flows from row i+1 into row i
v_fy = 0.5 * (v_sim[:-1, :] + v_sim[1:, :])
h_up_y = np.where(v_fy > 0, H[1:, :], H[:-1, :])
ds_y_f = 0.5 * (ds_y[:-1, :] + ds_y[1:, :])
fy = h_up_y * v_fy * ds_y_f # m^3 / yr (northward)

# Finite volume net outflow divergence per cell:
div_F = np.zeros((Ny, Nx), dtype=np.float64)
# X contribution:
# fx[:, j] leaves col j (outflow), enters col j+1 (inflow)
div_F[:, :-1] += fx # leaves col j
div_F[:, 1:] -= fx  # enters col j+1

# Y contribution:
# fy[i, :] is northward flux: leaves row i+1 (outflow), enters row i (inflow)
div_F[1:, :] += fy  # leaves row i+1
div_F[:-1, :] -= fy # enters row i

# Now let's calculate boundary calving fluxes exiting ice_mask:
# 1. East boundary: col j is ice, col j+1 is not ice, fx > 0
calv_x_east = fx * (ice_mask[:, :-1] & (~ice_mask[:, 1:]) & (u_fx > 0))
# 2. West boundary: col j is not ice, col j+1 is ice, fx < 0 (ice moves west from col j+1 to col j)
calv_x_west = -fx * ((~ice_mask[:, :-1]) & ice_mask[:, 1:] & (u_fx < 0))

# 3. North boundary: row i is not ice, row i+1 is ice, fy > 0 (ice moves north from row i+1 to row i)
calv_y_north = fy * ((~ice_mask[:-1, :]) & ice_mask[1:, :] & (v_fy > 0))
# 4. South boundary: row i is ice, row i+1 is not ice, fy < 0 (ice moves south from row i to row i+1)
calv_y_south = -fy * (ice_mask[:-1, :] & (~ice_mask[1:, :]) & (v_fy < 0))

boundary_calving_vol = (np.sum(calv_x_east) + np.sum(calv_x_west) + 
                        np.sum(calv_y_north) + np.sum(calv_y_south))
boundary_calving_Gt = boundary_calving_vol * RHO_ICE * 1e-12

sum_div_ice_vol = np.sum(div_F[ice_mask])
sum_div_ice_Gt = sum_div_ice_vol * RHO_ICE * 1e-12

print(f"Boundary Calving Outflow: {boundary_calving_vol:.4f} m^3/yr ({boundary_calving_Gt:.6f} Gt/yr)")
print(f"Sum of div_F on ice domain: {sum_div_ice_vol:.4f} m^3/yr ({sum_div_ice_Gt:.6f} Gt/yr)")
print(f"Difference |Sum(div_F) - Boundary Outflow|: {abs(sum_div_ice_vol - boundary_calving_vol):.10e} m^3/yr")

# Check time-stepping mass conservation:
dt = 0.1 # yr
smb_tot_Gt = np.sum(smb[ice_mask] * cell_area[ice_mask]) * 1e-12
predicted_dM_Gt = (smb_tot_Gt - boundary_calving_Gt) * dt

# Time step update:
dH = dt * (smb / RHO_ICE - div_F / cell_area)
# Thickness update strictly on ice cells:
H_next = H + dH
actual_dM_Gt = np.sum(RHO_ICE * (H_next[ice_mask] - H[ice_mask]) * cell_area[ice_mask]) * 1e-12

print(f"\nTime step dt = {dt} yr:")
print(f"  SMB input: {smb_tot_Gt * dt:.6f} Gt")
print(f"  Calving loss: {boundary_calving_Gt * dt:.6f} Gt")
print(f"  Predicted dM: {predicted_dM_Gt:.6f} Gt")
print(f"  Actual dM:    {actual_dM_Gt:.6f} Gt")
print(f"  Mass residual |Actual - Pred|: {abs(actual_dM_Gt - predicted_dM_Gt):.14e} Gt")
