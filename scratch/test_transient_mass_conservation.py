import netCDF4 as nc
import numpy as np

path_u = "antarctic-ice-volume-prediction/data/processed/stage4_5_3/stage4_5_3_unified_physical_fields.nc"
path_c = "antarctic-ice-volume-prediction/data/processed/stage4_7/stage4_7_calibrated_velocity.nc"

ds_u = nc.Dataset(path_u)
H = ds_u.variables["thickness"][:].astype(np.float64)
bed = ds_u.variables["bed"][:].astype(np.float64)
smb = ds_u.variables["smb"][:].astype(np.float64) # mm w.e. / yr
alpha_g = ds_u.variables["alpha_grounded"][:].astype(np.float64)
alpha_f = ds_u.variables["alpha_floating"][:].astype(np.float64)
alpha_r = ds_u.variables["alpha_rock"][:].astype(np.float64)
cell_area = ds_u.variables["cell_area_wgs84_m2"][:].astype(np.float64)
ds_u.close()

ds_c = nc.Dataset(path_c)
u = ds_c.variables["u_calibrated"][:].astype(np.float64)
v = ds_c.variables["v_calibrated"][:].astype(np.float64)
ds_c.close()

Ny, Nx = H.shape
dx, dy = 1000.0, 1000.0
RHO_ICE = 917.0
RHO_WATER = 1028.0

k_scale = np.sqrt((dx * dy) / cell_area)
ds_x = dy / k_scale
ds_y = dx / k_scale

# Domain classification
grounded = (alpha_g > 0) & (H > 10.0)
floating = (alpha_f > 0) & (H > 10.0)
ice_domain = grounded | floating
ocean = (~ice_domain) & (alpha_r == 0)

# Check flotation thickness: H_flot = -bed * rho_w / rho_i (for bed < 0)
h_flot = np.where(bed < 0, -bed * (RHO_WATER / RHO_ICE), 0.0)
height_above_flot = H - h_flot

print(f"Grounded cells: {np.sum(grounded):,}, Floating cells: {np.sum(floating):,}")
print(f"Height above flotation on grounded: min={np.min(height_above_flot[grounded]):.1f}m, median={np.median(height_above_flot[grounded]):.1f}m")
print(f"Height above flotation on floating: min={np.min(height_above_flot[floating]):.1f}m, median={np.median(height_above_flot[floating]):.1f}m, max={np.max(height_above_flot[floating]):.1f}m")

# Clip velocities
u_c = np.clip(u, -5000.0, 5000.0)
v_c = np.clip(v, -5000.0, 5000.0)

# Face velocities
u_face_x = 0.5 * (u_c[:, :-1] + u_c[:, 1:])
ds_x_face = 0.5 * (ds_x[:, :-1] + ds_x[:, 1:])

v_face_y = 0.5 * (v_c[:-1, :] + v_c[1:, :])
ds_y_face = 0.5 * (ds_y[:-1, :] + ds_y[1:, :])

# Face types in X direction
# 1. Internal grounded: grounded to grounded
fe_gg = grounded[:, :-1] & grounded[:, 1:]
# 2. Grounding line: grounded to floating (east or west)
fe_gf = (grounded[:, :-1] & floating[:, 1:]) | (floating[:, :-1] & grounded[:, 1:])
# 3. Grounded tidewater calving: grounded to ocean (east or west)
fe_go = (grounded[:, :-1] & ocean[:, 1:]) | (ocean[:, :-1] & grounded[:, 1:])
# 4. Floating internal: floating to floating
fe_ff = floating[:, :-1] & floating[:, 1:]
# 5. Floating calving front: floating to ocean
fe_fo = (floating[:, :-1] & ocean[:, 1:]) | (ocean[:, :-1] & floating[:, 1:])

print(f"\nX-faces: gg={np.sum(fe_gg):,}, gf={np.sum(fe_gf):,}, go={np.sum(fe_go):,}, ff={np.sum(fe_ff):,}, fo={np.sum(fe_fo):,}")

# Face types in Y direction
fn_gg = grounded[:-1, :] & grounded[1:, :]
fn_gf = (grounded[:-1, :] & floating[1:, :]) | (floating[:-1, :] & grounded[1:, :])
fn_go = (grounded[:-1, :] & ocean[1:, :]) | (ocean[:-1, :] & grounded[1:, :])
fn_ff = floating[:-1, :] & floating[1:, :]
fn_fo = (floating[:-1, :] & ocean[1:, :]) | (ocean[:-1, :] & floating[1:, :])

print(f"Y-faces: gg={np.sum(fn_gg):,}, gf={np.sum(fn_gf):,}, go={np.sum(fn_go):,}, ff={np.sum(fn_ff):,}, fo={np.sum(fn_fo):,}")
