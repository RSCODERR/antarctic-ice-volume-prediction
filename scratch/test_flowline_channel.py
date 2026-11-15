import numpy as np
import netCDF4 as nc

nc_path = 'data/processed/bedmachine_v4.1_peninsula_aligned_to_bedmap3.nc'
ds = nc.Dataset(nc_path, 'r')

xs = ds.variables['x'][:]
ys = ds.variables['y'][:]

# In Palmer Land (Hp-I):
# Ryder Glacier / Bertram Glacier channel
# Let's inspect along a true flow-path from the interior plateau (high elevation)
# down along the fast-flowing ice stream trunk to the grounding line.
# Let's check a set of coordinates that follow the ice stream trough:
# High divide: (x=-1820000, y=820000), surface ~ 1800m
# Mid trunk: (x=-1870000, y=780000), surface ~ 1200m
# Terminus gate: (x=-1910000, y=750000), surface ~ 400m

pts = [
    (-1820000.0, 820000.0),
    (-1860000.0, 785000.0),
    (-1907000.0, 745000.0)
]

# Interpolate spline or piecewise linear between waypoints
N_total = 200
t_pts = np.linspace(0, 1, len(pts))
t_eval = np.linspace(0, 1, N_total)

x_eval = np.interp(t_eval, t_pts, [p[0] for p in pts])
y_eval = np.interp(t_eval, t_pts, [p[1] for p in pts])

dx = xs[1] - xs[0]
dy = ys[1] - ys[0]

cols = np.clip(np.round((x_eval - xs[0]) / dx).astype(int), 0, len(xs)-1)
rows = np.clip(np.round((y_eval - ys[0]) / dy).astype(int), 0, len(ys)-1)

r_min, r_max = rows.min(), rows.max()
c_min, c_max = cols.min(), cols.max()

sub_surf = ds.variables['surface'][r_min:r_max+1, c_min:c_max+1]
sub_thick = ds.variables['thickness'][r_min:r_max+1, c_min:c_max+1]
sub_bed = ds.variables['bed'][r_min:r_max+1, c_min:c_max+1]
sub_mask = ds.variables['mask'][r_min:r_max+1, c_min:c_max+1]
sub_firn = ds.variables['firn'][r_min:r_max+1, c_min:c_max+1]

surf = sub_surf[rows - r_min, cols - c_min].astype(np.float64)
thick = sub_thick[rows - r_min, cols - c_min].astype(np.float64)
bed = sub_bed[rows - r_min, cols - c_min].astype(np.float64)
mask = sub_mask[rows - r_min, cols - c_min].astype(np.int32)
firn = sub_firn[rows - r_min, cols - c_min].astype(np.float64)
ds.close()

print(f"Waypointed Ryder flowline: N={N_total}, Length={N_total*0.5:.1f} km")
print(f"Mask values: {np.unique(mask, return_counts=True)}")
print(f"Surface: start={surf[0]:.1f}m, end={surf[-1]:.1f}m, min={surf.min():.1f}m, max={surf.max():.1f}m")
print(f"Bed: start={bed[0]:.1f}m, end={bed[-1]:.1f}m, min={bed.min():.1f}m, max={bed.max():.1f}m")
print(f"Thick: start={thick[0]:.1f}m, end={thick[-1]:.1f}m, min={thick.min():.1f}m, max={thick.max():.1f}m")
print(f"Firn: min={firn.min():.1f}m, mean={firn.mean():.1f}m, max={firn.max():.1f}m")
ds_dx = np.gradient(surf, 500.0)
print(f"ds/dx: min={ds_dx.min():.5f}, max={ds_dx.max():.5f}, mean={ds_dx.mean():.5f}")

