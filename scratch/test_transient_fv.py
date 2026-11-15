import netCDF4 as nc
import numpy as np
import time

path_u = "antarctic-ice-volume-prediction/data/processed/stage4_5_3/stage4_5_3_unified_physical_fields.nc"
path_c = "antarctic-ice-volume-prediction/data/processed/stage4_7/stage4_7_calibrated_velocity.nc"

ds_u = nc.Dataset(path_u)
H = ds_u.variables["thickness"][:].astype(np.float64)
bed = ds_u.variables["bed"][:].astype(np.float64)
smb = ds_u.variables["smb"][:].astype(np.float64) # mm w.e. / yr
alpha_g = ds_u.variables["alpha_grounded"][:].astype(np.float64)
alpha_f = ds_u.variables["alpha_floating"][:].astype(np.float64)
cell_area = ds_u.variables["cell_area_wgs84_m2"][:].astype(np.float64)
ds_u.close()

ds_c = nc.Dataset(path_c)
u = ds_c.variables["u_calibrated"][:].astype(np.float64) # m/yr
v = ds_c.variables["v_calibrated"][:].astype(np.float64) # m/yr
ds_c.close()

Ny, Nx = H.shape
dx, dy = 1000.0, 1000.0
RHO_ICE = 917.0
RHO_WATER = 1028.0

k_scale = np.sqrt((dx * dy) / cell_area)
ds_x = dy / k_scale
ds_y = dx / k_scale

# Clip velocity to CFL max 5000 m/yr on cliffs
u_clipped = np.clip(u, -5000.0, 5000.0)
v_clipped = np.clip(v, -5000.0, 5000.0)

t0 = time.perf_counter()

# Face velocities
# East face of cell (i, j): u_{i, j+1/2} = 0.5 * (u[i, j] + u[i, j+1])
u_face_x = 0.5 * (u_clipped[:, :-1] + u_clipped[:, 1:])
# Upwind thickness for x faces
h_upwind_x = np.where(u_face_x > 0, H[:, :-1], H[:, 1:])
# Face flux in m^3 / yr (using ds_x at interface)
ds_x_face = 0.5 * (ds_x[:, :-1] + ds_x[:, 1:])
flux_x = h_upwind_x * u_face_x * ds_x_face # (Ny, Nx-1)

# North face of cell (i, j): v_{i+1/2, j} = 0.5 * (v[i, j] + v[i+1, j])
# Note: y index increases southward in raster (dy negative in geographic, or grid orientation)
# In our grid: v > 0 is southward (+y index) or northward?
# Let's check: in Step 2 of Stage 4.7:
# ds_dy_smooth, ds_dx_smooth = np.gradient(surface_smooth, -dy, dx)
# bu = -rho g H ds_dx, bv = -rho g H ds_dy
# So v > 0 is northward (decreasing i) or southward?
# In Stage 4.7:
# fn: (~grounded[:-1, :]) & grounded[1:, :], un_out = max(0, v[1:, :]) -> northward exit from row 1 into row 0!
# So v > 0 points northward (from row i to row i-1)!
# fs: grounded[:-1, :] & (~grounded[1:, :]), us_out = max(0, -v[:-1, :]) -> southward exit from row i to row i+1!
# So -v points southward!
# That means: v is northward velocity. Interface between row i-1 and row i:
v_face_y = 0.5 * (v_clipped[:-1, :] + v_clipped[1:, :])
# If v_face_y > 0 (northward, moving from row i to row i-1): upwind is row i (index 1)
# If v_face_y < 0 (southward, moving from row i-1 to row i): upwind is row i-1 (index 0)
h_upwind_y = np.where(v_face_y > 0, H[1:, :], H[:-1, :])
ds_y_face = 0.5 * (ds_y[:-1, :] + ds_y[1:, :])
flux_y = h_upwind_y * v_face_y * ds_y_face # (Ny-1, Nx)

# Net divergence per cell (in m^3 / yr)
div_flux = np.zeros((Ny, Nx), dtype=np.float64)
# X contribution: outflow through east (+x) minus inflow through west
div_flux[:, 1:] += flux_x
div_flux[:, :-1] -= flux_x
# Y contribution: outflow through north (+v, row i-1) minus inflow from south
# Flux northward from row i to row i-1: leaves row i (+div), enters row i-1 (-div)
div_flux[1:, :] += flux_y
div_flux[:-1, :] -= flux_y

# dH / dt from divergence: -div_flux / cell_area
dH_dt_dyn = -div_flux / cell_area # m / yr
# SMB contribution in m / yr
smb_m_yr = smb / RHO_ICE # mm w.e. / yr -> m ice / yr

dH_dt_tot = dH_dt_dyn + smb_m_yr

t1 = time.perf_counter()
print(f"Vectorized flux calculation time: {(t1 - t0)*1000:.2f} ms")
print(f"dH_dt_dyn stats on grounded: min={np.min(dH_dt_dyn[alpha_g > 0]):.2f}, mean={np.mean(dH_dt_dyn[alpha_g > 0]):.2f}, max={np.max(dH_dt_dyn[alpha_g > 0]):.2f} m/yr")
print(f"dH_dt_tot stats on grounded: min={np.min(dH_dt_tot[alpha_g > 0]):.2f}, mean={np.mean(dH_dt_tot[alpha_g > 0]):.2f}, max={np.max(dH_dt_tot[alpha_g > 0]):.2f} m/yr")

# Total mass change rate: sum(rho_i * dH_dt_tot * cell_area)
net_dM_dt = np.sum(RHO_ICE * dH_dt_tot[alpha_g > 0] * cell_area[alpha_g > 0]) * 1e-12
print(f"Net grounded dM/dt: {net_dM_dt:.2f} Gt/yr")
