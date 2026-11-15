import netCDF4 as nc
import numpy as np
from scipy.ndimage import binary_dilation

nc_path = 'data/processed/bedmachine_v4.1_peninsula_aligned_to_bedmap3.nc'
ds = nc.Dataset(nc_path, 'r')
xs = ds.variables['x'][:]
ys = ds.variables['y'][:]

y_min, y_max = 1280000, 1320000
x_min, x_max = -2490000, -2440000

# Since ys is descending:
r_min = int(round((ys[0] - y_max) / 500.0))
r_max = int(round((ys[0] - y_min) / 500.0))
c_min = int(round((x_min - xs[0]) / 500.0))
c_max = int(round((x_max - xs[0]) / 500.0))

surf = ds.variables['surface'][r_min:r_max, c_min:c_max]
thick = ds.variables['thickness'][r_min:r_max, c_min:c_max]
bed = ds.variables['bed'][r_min:r_max, c_min:c_max]
mask = ds.variables['mask'][r_min:r_max, c_min:c_max]

print(f"Flanders region: shape={surf.shape}, rows [{r_min}:{r_max}], cols [{c_min}:{c_max}]")
grounded_thick = np.where(mask == 2, thick, 0)
print(f"Max grounded thickness: {grounded_thick.max():.1f} m")

ocean_mask = (mask == 0) | (mask == 3)
coastal_ice = (mask == 2) & binary_dilation(ocean_mask, iterations=2)
coastal_thick = np.where(coastal_ice, thick, 0)

max_coastal_idx = np.unravel_index(np.argsort(coastal_thick.ravel())[-15:], coastal_thick.shape)

print("\nTop coastal outlet cells in Flanders Bay:")
for r_idx, c_idx in zip(max_coastal_idx[0], max_coastal_idx[1]):
    r_abs = r_min + r_idx
    c_abs = c_min + c_idx
    print(f"x={xs[c_abs]:.1f}, y={ys[r_abs]:.1f}, H={thick[r_idx, c_idx]:.1f}m, s={surf[r_idx, c_idx]:.1f}m, b={bed[r_idx, c_idx]:.1f}m")
