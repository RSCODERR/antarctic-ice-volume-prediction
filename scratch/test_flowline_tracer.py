import numpy as np
import netCDF4 as nc

nc_path = 'data/processed/bedmachine_v4.1_peninsula_aligned_to_bedmap3.nc'
ds = nc.Dataset(nc_path, 'r')

xs = ds.variables['x'][:]
ys = ds.variables['y'][:]
dx = xs[1] - xs[0]
dy = ys[1] - ys[0]

def trace_flowline_from_trough(r_start, c_start, step_r, step_c, n_steps):
    """Trace along the trunk by stepping along the valley direction."""
    rows = []
    cols = []
    cur_r, cur_c = r_start, c_start
    for i in range(n_steps):
        rows.append(int(round(cur_r)))
        cols.append(int(round(cur_c)))
        cur_r += step_r
        cur_c += step_c
    
    rows = np.array(rows)
    cols = np.array(cols)
    
    # Read bounding box
    r_min, r_max = rows.min(), rows.max()
    c_min, c_max = cols.min(), cols.max()
    
    thick_sub = ds.variables['thickness'][r_min:r_max+1, c_min:c_max+1]
    bed_sub = ds.variables['bed'][r_min:r_max+1, c_min:c_max+1]
    surf_sub = ds.variables['surface'][r_min:r_max+1, c_min:c_max+1]
    mask_sub = ds.variables['mask'][r_min:r_max+1, c_min:c_max+1]
    firn_sub = ds.variables['firn'][r_min:r_max+1, c_min:c_max+1]
    
    rel_r = rows - r_min
    rel_c = cols - c_min
    
    thick = thick_sub[rel_r, rel_c]
    bed = bed_sub[rel_r, rel_c]
    surf = surf_sub[rel_r, rel_c]
    mask = mask_sub[rel_r, rel_c]
    firn = firn_sub[rel_r, rel_c]
    
    return {
        'rows': rows,
        'cols': cols,
        'x': xs[cols],
        'y': ys[rows],
        'thick': thick,
        'bed': bed,
        'surf': surf,
        'mask': mask,
        'firn': firn
    }

# 1. Ryder trunk: trough is near r=2436, c=1585.
# Inland is East/North-East (increasing x -> increasing col, decreasing y -> decreasing row in BedMachine index)
# Terminus is at George VI / Marguerite Bay to the West.
# So from divide (inland) to terminus (marine gate):
# Let's test inland start: r=2250, c=1700 to terminus r=2436, c=1585 (length ~ 100km, 200 cells)
n_cells_ryder = 180
step_r = (2436 - 2250) / n_cells_ryder
step_c = (1585 - 1700) / n_cells_ryder
ryder_prof = trace_flowline_from_trough(2250, 1700, step_r, step_c, n_cells_ryder)

print("--- Ryder Profile ---")
print(f"Cells: {len(ryder_prof['thick'])}, dx=500m, Length={len(ryder_prof['thick'])*0.5:.1f} km")
print(f"Masks: {np.unique(ryder_prof['mask'], return_counts=True)}")
print(f"Thickness: min={np.nanmin(ryder_prof['thick']):.1f}m, mean={np.nanmean(ryder_prof['thick']):.1f}m, max={np.nanmax(ryder_prof['thick']):.1f}m")
print(f"Surface: start={ryder_prof['surf'][0]:.1f}m, end={ryder_prof['surf'][-1]:.1f}m, min={np.nanmin(ryder_prof['surf']):.1f}m, max={np.nanmax(ryder_prof['surf']):.1f}m")
print(f"Bed: start={ryder_prof['bed'][0]:.1f}m, end={ryder_prof['bed'][-1]:.1f}m, min={np.nanmin(ryder_prof['bed']):.1f}m, max={np.nanmax(ryder_prof['bed']):.1f}m")
print(f"Firn: min={np.nanmin(ryder_prof['firn']):.1f}m, mean={np.nanmean(ryder_prof['firn']):.1f}m, max={np.nanmax(ryder_prof['firn']):.1f}m")

ds.close()

