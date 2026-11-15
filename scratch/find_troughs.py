import numpy as np
import netCDF4 as nc
import sys
import os

nc_path = 'data/processed/bedmachine_v4.1_peninsula_aligned_to_bedmap3.nc'
ds = nc.Dataset(nc_path, 'r')

xs = ds.variables['x'][:]
ys = ds.variables['y'][:]
dx = xs[1] - xs[0]
dy = ys[1] - ys[0]

# Let's inspect GATE_HP_01 (Ryder): lon=-68.45, lat=-71.25 -> x=-1911235.0, y=754782.8
gx, gy = -1911235.0, 754782.8
col = int(round((gx - xs[0]) / dx))
row = int(round((gy - ys[0]) / dy))

print(f"Gate row={row}, col={col}")
# Look at a 100x100 window around the gate
window_thick = ds.variables['thickness'][row-50:row+50, col-50:col+50]
window_mask = ds.variables['mask'][row-50:row+50, col-50:col+50]
window_bed = ds.variables['bed'][row-50:row+50, col-50:col+50]
window_surf = ds.variables['surface'][row-50:row+50, col-50:col+50]

print("Window thickness shape:", window_thick.shape)
print("Masks in window:", np.unique(window_mask, return_counts=True))
print("Max thickness in window:", np.nanmax(window_thick))
# Find thickest point in window (glacier trough)
max_idx = np.unravel_index(np.nanargmax(window_thick), window_thick.shape)
r_trough = row - 50 + max_idx[0]
c_trough = col - 50 + max_idx[1]
print(f"Glacier trunk trough at row={r_trough}, col={c_trough}: H={window_thick[max_idx]:.1f}m, mask={window_mask[max_idx]}, bed={window_bed[max_idx]:.1f}m, surf={window_surf[max_idx]:.1f}m")
print(f"EPSG:3031 coordinates: x={xs[c_trough]}, y={ys[r_trough]}")

ds.close()

