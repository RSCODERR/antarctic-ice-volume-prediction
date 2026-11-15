import netCDF4 as nc
import numpy as np

nc_path = 'data/processed/bedmachine_v4.1_peninsula_aligned_to_bedmap3.nc'
ds = nc.Dataset(nc_path, 'r')
xs = ds.variables['x'][:]
ys = ds.variables['y'][:]
dx = xs[1] - xs[0]
dy = ys[1] - ys[0]

# GATE_IPP_01 center
x_gate = -2466040.2
y_gate = 1305701.1

col_g = int(round((x_gate - xs[0]) / dx))
row_g = int(round((y_gate - ys[0]) / dy))

print(f"GATE_IPP_01 grid indices: row={row_g}, col={col_g}")
print(f"Surface at gate: {ds.variables['surface'][row_g, col_g]}")
print(f"Bed at gate: {ds.variables['bed'][row_g, col_g]}")
print(f"Thickness at gate: {ds.variables['thickness'][row_g, col_g]}")
print(f"Mask at gate: {ds.variables['mask'][row_g, col_g]}")

# Let's inspect a box around the gate: +/- 30 km
r0 = max(0, row_g - 40)
r1 = min(len(ys), row_g + 41)
c0 = max(0, col_g - 40)
c1 = min(len(xs), col_g + 41)

surf_box = ds.variables['surface'][r0:r1, c0:c1]
bed_box = ds.variables['bed'][r0:r1, c0:c1]
thick_box = ds.variables['thickness'][r0:r1, c0:c1]
mask_box = ds.variables['mask'][r0:r1, c0:c1]

print(f"\nBox around GATE_IPP_01 (40 km x 40 km):")
print(f"Surface min={surf_box.min():.1f}, max={surf_box.max():.1f}")
print(f"Bed min={bed_box.min():.1f}, max={bed_box.max():.1f}")
print(f"Thickness min={thick_box.min():.1f}, max={thick_box.max():.1f}")

