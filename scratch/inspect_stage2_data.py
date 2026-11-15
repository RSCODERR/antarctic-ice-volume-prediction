import os
import netCDF4 as nc
import numpy as np

nc_path = 'data/processed/bedmachine_v4.1_peninsula_aligned_to_bedmap3.nc'
if not os.path.exists(nc_path):
    nc_path = os.path.join('antarctic-ice-volume-prediction', nc_path)

print(f"Opening: {nc_path}")
ds = nc.Dataset(nc_path, 'r')
print("Dimensions:", {d: len(ds.dimensions[d]) for d in ds.dimensions})
print("Variables:")
for v in ds.variables:
    var = ds.variables[v]
    print(f"  {v}: shape={var.shape}, dtype={var.dtype}")
    for a in var.ncattrs():
        print(f"    attr: {a} = {getattr(var, a)}")

x = ds.variables['x'][:]
y = ds.variables['y'][:]
print(f"x range: [{x.min()}, {x.max()}], dx = {x[1] - x[0] if len(x) > 1 else 'N/A'}")
print(f"y range: [{y.min()}, {y.max()}], dy = {y[1] - y[0] if len(y) > 1 else 'N/A'}")

mask = ds.variables['mask'][:]
print(f"Mask unique values and counts:")
vals, counts = np.unique(mask, return_counts=True)
for v, c in zip(vals, counts):
    print(f"  val {v}: count {c} ({c * 0.25:.2f} km^2)")

ds.close()

