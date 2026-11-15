import zipfile
import netCDF4 as nc
import tempfile
import os
import numpy as np

zip_path = 'antarctic-ice-volume-prediction/data/raw/ismip6/ComputedScalarsPaper.zip'
with zipfile.ZipFile(zip_path, 'r') as z:
    for name in z.namelist():
        if 'computed_icearea_' in name and 'ctrl_proj_std' in name and 'UCIJPL' in name:
            with tempfile.NamedTemporaryFile(suffix='.nc', delete=False) as tmp:
                tmp.write(z.read(name))
                tmp_path = tmp.name
            ds = nc.Dataset(tmp_path, 'r')
            break

sector_vals = [ds.variables[f'icearea_sector_{i}'][0] / 1e6 for i in range(1, 19)]
r1 = ds.variables['icearea_region_1'][0] / 1e6
r2 = ds.variables['icearea_region_2'][0] / 1e6
r3 = ds.variables['icearea_region_3'][0] / 1e6
tot = ds.variables['icearea'][0] / 1e6

print(f"Total Ice Area: {tot:.1f} km2")
print(f"Region 1 (West): {r1:.1f} km2")
print(f"Region 2 (East): {r2:.1f} km2")
print(f"Region 3 (Peninsula): {r3:.1f} km2")
print(f"Sum of R1+R2+R3: {r1+r2+r3:.1f} km2 (diff: {tot - (r1+r2+r3):.3f})")

# Now check which sectors sum to R3
s16_18 = sum(sector_vals[15:18])
print(f"Sum of Sectors 16+17+18: {s16_18:.1f} km2 (diff from R3: {r3 - s16_18:.3f})")

# Let's find which sectors sum to R1 and R2
# Let's test combinations
import itertools
indices = list(range(1, 19))
for r in range(1, 10):
    for combo in itertools.combinations(range(1, 16), r):
        s = sum(sector_vals[c-1] for c in combo)
        if abs(s - r1) < 1.0:
            print(f"Region 1 matches combo: {combo} (sum={s:.1f})")
            other = [c for c in range(1, 16) if c not in combo]
            s_other = sum(sector_vals[c-1] for c in other)
            print(f"Remaining sectors for Region 2: {other} (sum={s_other:.1f}, diff from R2: {r2 - s_other:.3f})")
            break

ds.close()
os.remove(tmp_path)

