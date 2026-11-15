import numpy as np
import netCDF4 as nc

nc_path = 'data/processed/bedmachine_v4.1_peninsula_aligned_to_bedmap3.nc'
ds = nc.Dataset(nc_path, 'r')

r_start, c_start = 2250, 1700
r_end, c_end = 2436, 1585
N = 180

rows = np.round(np.linspace(r_start, r_end, N)).astype(int)
cols = np.round(np.linspace(c_start, c_end, N)).astype(int)

r_min, r_max = rows.min(), rows.max()
c_min, c_max = cols.min(), cols.max()

sub_surf = ds.variables['surface'][r_min:r_max+1, c_min:c_max+1]
sub_thick = ds.variables['thickness'][r_min:r_max+1, c_min:c_max+1]
sub_bed = ds.variables['bed'][r_min:r_max+1, c_min:c_max+1]
sub_mask = ds.variables['mask'][r_min:r_max+1, c_min:c_max+1]

surf = sub_surf[rows - r_min, cols - c_min].astype(np.float64)
thick = sub_thick[rows - r_min, cols - c_min].astype(np.float64)
bed = sub_bed[rows - r_min, cols - c_min].astype(np.float64)
mask = sub_mask[rows - r_min, cols - c_min].astype(np.int32)
ds.close()

print(f"BedMachine surface: min={np.nanmin(surf):.1f}m, max={np.nanmax(surf):.1f}m")
print(f"BedMachine bed: min={np.nanmin(bed):.1f}m, max={np.nanmax(bed):.1f}m")
print(f"BedMachine thick: min={np.nanmin(thick):.1f}m, max={np.nanmax(thick):.1f}m")
print("First 10 surface values:", surf[:10])
print("Last 10 surface values:", surf[-10:])

