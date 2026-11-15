import numpy as np
import netCDF4 as nc

nc_path = 'data/processed/bedmachine_v4.1_peninsula_aligned_to_bedmap3.nc'
ds = nc.Dataset(nc_path, 'r')

xs = ds.variables['x'][:]
ys = ds.variables['y'][:]
dx = xs[1] - xs[0]
dy = ys[1] - ys[0]

# Waypoints along the Ryder glacier trunk in Palmer Land
pts = [
    (-1820000.0, 820000.0),
    (-1860000.0, 785000.0),
    (-1907000.0, 745000.0)
]

N_total = 150
t_pts = np.linspace(0, 1, len(pts))
t_eval = np.linspace(0, 1, N_total)

x_eval = np.interp(t_eval, t_pts, [p[0] for p in pts])
y_eval = np.interp(t_eval, t_pts, [p[1] for p in pts])

cols = np.clip(np.round((x_eval - xs[0]) / dx).astype(int), 0, len(xs)-1)
rows = np.clip(np.round((y_eval - ys[0]) / dy).astype(int), 0, len(ys)-1)

r_min = max(0, rows.min() - 20)
r_max = min(len(ys)-1, rows.max() + 20)
c_min = max(0, cols.min() - 20)
c_max = min(len(xs)-1, cols.max() + 20)

sub_surf = ds.variables['surface'][r_min:r_max+1, c_min:c_max+1]
sub_thick = ds.variables['thickness'][r_min:r_max+1, c_min:c_max+1]
sub_bed = ds.variables['bed'][r_min:r_max+1, c_min:c_max+1]
sub_mask = ds.variables['mask'][r_min:r_max+1, c_min:c_max+1]
sub_firn = ds.variables['firn'][r_min:r_max+1, c_min:c_max+1]

# Snap each waypoint to local maximum ice thickness within a +/- 10 cell (5 km) cross-section
thalweg_rows = []
thalweg_cols = []
search_radius = 8

for r_target, c_target in zip(rows, cols):
    r_local = r_target - r_min
    c_local = c_target - c_min
    
    # search window
    r0 = max(0, r_local - search_radius)
    r1 = min(sub_thick.shape[0], r_local + search_radius + 1)
    c0 = max(0, c_local - search_radius)
    c1 = min(sub_thick.shape[1], c_local + search_radius + 1)
    
    window_thick = np.array(sub_thick[r0:r1, c0:c1])
    window_mask = np.array(sub_mask[r0:r1, c0:c1])
    # Prefer grounded ice (mask==2), else any ice
    window_thick[window_mask == 1] = -1.0 # suppress rock
    
    max_idx = np.unravel_index(np.nanargmax(window_thick), window_thick.shape)
    best_r = r_min + r0 + max_idx[0]
    best_c = c_min + c0 + max_idx[1]
    thalweg_rows.append(best_r)
    thalweg_cols.append(best_c)

thalweg_rows = np.array(thalweg_rows)
thalweg_cols = np.array(thalweg_cols)

# Extract along thalweg
rel_r = thalweg_rows - r_min
rel_c = thalweg_cols - c_min

thick = sub_thick[rel_r, rel_c].astype(np.float64)
bed = sub_bed[rel_r, rel_c].astype(np.float64)
surf = sub_surf[rel_r, rel_c].astype(np.float64)
mask = sub_mask[rel_r, rel_c].astype(np.int32)
firn = sub_firn[rel_r, rel_c].astype(np.float64)
ds.close()

print(f"Thalweg Ryder flowline: N={N_total}, Length={N_total*0.5:.1f} km")
print(f"Mask values: {np.unique(mask, return_counts=True)}")
print(f"Thickness: min={np.nanmin(thick):.1f}m, mean={np.nanmean(thick):.1f}m, max={np.nanmax(thick):.1f}m")
print(f"Surface: start={surf[0]:.1f}m, end={surf[-1]:.1f}m, min={surf.min():.1f}m, max={surf.max():.1f}m")
print(f"Bed: start={bed[0]:.1f}m, end={bed[-1]:.1f}m, min={bed.min():.1f}m, max={bed.max():.1f}m")
print(f"Firn: min={firn.min():.1f}m, mean={firn.mean():.1f}m, max={firn.max():.1f}m")

# Now check slope
kernel = np.ones(5) / 5.0
surf_s = np.convolve(surf, kernel, mode='same')
ds_dx = np.gradient(surf_s, 500.0)
print(f"Smoothed ds/dx: min={ds_dx.min():.5f}, max={ds_dx.max():.5f}, mean={ds_dx.mean():.5f}")

