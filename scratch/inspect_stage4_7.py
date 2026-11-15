import netCDF4 as nc
import numpy as np

ds = nc.Dataset("data/processed/stage4_7/stage4_7_calibrated_velocity.nc")
print("Variables:", ds.variables.keys())
u = ds.variables["u_calibrated"]
print("u attributes:", {k: u.getncattr(k) for k in u.ncattrs()})
u_arr = u[:]
print("u min, max, mean:", float(np.nanmin(u_arr)), float(np.nanmax(u_arr)), float(np.nanmean(u_arr)))
v = ds.variables["v_calibrated"]
print("v min, max, mean:", float(np.nanmin(v[:])), float(np.nanmax(v[:])), float(np.nanmean(v[:])))
ds.close()
