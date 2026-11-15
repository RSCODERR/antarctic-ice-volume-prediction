import netCDF4 as nc
import numpy as np

nc_path = 'data/processed/bedmachine_v4.1_peninsula_aligned_to_bedmap3.nc'
ds = nc.Dataset(nc_path, 'r')
xs = ds.variables['x'][:]
ys = ds.variables['y'][:]

# Let's inspect the thalweg from the plateau into Flanders Bay
# Leonardo glacier heads near (-2450000, 1315000) and flows toward (-2475000, 1315000) or similar
# Let's search lines across y = 1300000 to 1320000
for y_test in range(1300000, 1325000, 5000):
    r = int(round((ys[0] - y_test) / 500.0))
    # find where bed is lowest and thickness > 100m
    row_b = ds.variables['bed'][r, :]
    row_t = ds.variables['thickness'][r, :]
    row_s = ds.variables['surface'][r, :]
    row_m = ds.variables['mask'][r, :]
    
    # filter for flanders longitudes: x in [-2490000, -2440000]
    c_start = int(round((-2490000 - xs[0]) / 500.0))
    c_end = int(round((-2440000 - xs[0]) / 500.0))
    
    seg_b = row_b[c_start:c_end]
    seg_t = row_t[c_start:c_end]
    seg_s = row_s[c_start:c_end]
    seg_m = row_m[c_start:c_end]
    
    valid = (seg_m == 2) & (seg_t > 50)
    if np.any(valid):
        min_b_idx = np.argmin(np.where(valid, seg_b, 9999))
        c_min = c_start + min_b_idx
        print(f"y={y_test/1e3:.1f} km: thalweg at x={xs[c_min]/1e3:.1f} km, b={row_b[c_min]:.1f}m, s={row_s[c_min]:.1f}m, H={row_t[c_min]:.1f}m, mask={row_m[c_min]}")

