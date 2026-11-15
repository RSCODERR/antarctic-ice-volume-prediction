import numpy as np
import netCDF4 as nc
import sys
import os

sys.path.insert(0, os.path.abspath('src'))
from physics.constants import CONST
from physics.domain import FlowlineDomain

nc_path = 'data/processed/bedmachine_v4.1_peninsula_aligned_to_bedmap3.nc'
ds = nc.Dataset(nc_path, 'r')

r_start, c_start = 2250, 1700
r_end, c_end = 2436, 1585
N = 180

rows = np.round(np.linspace(r_start, r_end, N)).astype(int)
cols = np.round(np.linspace(c_start, c_end, N)).astype(int)

r_min, r_max = rows.min(), rows.max()
c_min, c_max = cols.min(), cols.max()

sub_thick = ds.variables['thickness'][r_min:r_max+1, c_min:c_max+1]
sub_bed = ds.variables['bed'][r_min:r_max+1, c_min:c_max+1]
thick = sub_thick[rows - r_min, cols - c_min].astype(np.float64)
bed = sub_bed[rows - r_min, cols - c_min].astype(np.float64)
ds.close()

kernel = np.ones(5) / 5.0
bed_s = np.convolve(bed, kernel, mode='same')
thick_s = np.convolve(thick, kernel, mode='same')
thick_s = np.maximum(thick_s, 20.0)

s = bed_s + thick_s
dx = CONST.domain_dx
ds_dx = np.gradient(s, dx)

print(f"Surface elevation s: min={s.min():.1f}m, max={s.max():.1f}m")
print(f"Bed elevation z_b: min={bed_s.min():.1f}m, max={bed_s.max():.1f}m")
print(f"Thickness H: min={thick_s.min():.1f}m, max={thick_s.max():.1f}m")
print(f"ds_dx: min={ds_dx.min():.4f}, max={ds_dx.max():.4f}")

bad_pts = np.where(np.abs(ds_dx) > 0.05)[0]
print(f"Points where |ds/dx| > 0.05: {len(bad_pts)} / {len(s)}")
for idx in bad_pts[:10]:
    print(f"  idx {idx}: s={s[idx]:.1f}m, H={thick_s[idx]:.1f}m, z_b={bed_s[idx]:.1f}m, ds_dx={ds_dx[idx]:.4f}")
