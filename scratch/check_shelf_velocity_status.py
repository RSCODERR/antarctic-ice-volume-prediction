import netCDF4 as nc
import numpy as np

p_u = "antarctic-ice-volume-prediction/data/processed/stage4_5_3/stage4_5_3_unified_physical_fields.nc"
p_c = "antarctic-ice-volume-prediction/data/processed/stage4_7/stage4_7_calibrated_velocity.nc"

ds_u = nc.Dataset(p_u)
alpha_g = ds_u.variables["alpha_grounded"][:]
alpha_f = ds_u.variables["alpha_floating"][:]
H = ds_u.variables["thickness"][:]
spd_0761 = ds_u.variables["speed_0761"][:]
vx_0761 = ds_u.variables["vx_0761"][:]
vy_0761 = ds_u.variables["vy_0761"][:]
ds_u.close()

ds_c = nc.Dataset(p_c)
u_cal = ds_c.variables["u_calibrated"][:]
v_cal = ds_c.variables["v_calibrated"][:]
spd_cal = ds_c.variables["speed_calibrated"][:]
ds_c.close()

grounded = (alpha_g > 0) & (H > 10.0)
floating = (alpha_f > 0) & (H > 10.0)

print(f"Calibrated speed on grounded: mean={np.mean(spd_cal[grounded]):.2f}, max={np.max(spd_cal[grounded]):.2f}")
print(f"Calibrated speed on floating: non-zero count={np.sum(spd_cal[floating] > 0)}, mean={np.mean(spd_cal[floating]):.2f}")
print(f"Observed NSIDC-0761 speed on floating: valid count={np.sum(~np.isnan(spd_0761[floating]))}/{np.sum(floating)}, mean={np.nanmean(spd_0761[floating]):.2f}")
