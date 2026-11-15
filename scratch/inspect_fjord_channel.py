import netCDF4 as nc
import numpy as np

nc_path = 'data/processed/bedmachine_v4.1_peninsula_aligned_to_bedmap3.nc'
ds = nc.Dataset(nc_path, 'r')
xs = ds.variables['x'][:]
ys = ds.variables['y'][:]

row_g = 1288
col_g = 467

# Look in +/- 10 cells (5 km) around gate
for dr in range(-6, 7):
    row_str = ""
    for dc in range(-6, 7):
        r = row_g + dr
        c = col_g + dc
        m = ds.variables['mask'][r, c]
        t = ds.variables['thickness'][r, c]
        s = ds.variables['surface'][r, c]
        b = ds.variables['bed'][r, c]
        if m == 2: # grounded ice
            row_str += f"[{t:3.0f}]"
        elif m == 3: # floating ice
            row_str += f"~{t:3.0f}~"
        elif m == 0: # ocean
            row_str += "  ~  "
        else:
            row_str += " ### "
    print(f"dr={dr:+2d} (y={ys[row_g+dr]/1e3:.1f} km): {row_str}")

