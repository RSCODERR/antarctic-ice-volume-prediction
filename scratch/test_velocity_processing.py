"""
Test script for MEaSUREs NSIDC-0720 (1 km) and NSIDC-0761 (450 m) velocity processing.
"""
import netCDF4 as nc
import numpy as np

# 1. NSIDC-0720 (1 km)
print("=== Processing NSIDC-0720 (1 km annual 2014-2015) ===")
ds_0720 = nc.Dataset("data/raw/measures/Antarctica_ice_velocity_2014_2015_1km_v01.nc")
x_0720 = ds_0720.variables['x'][:] # [-2800000, ..., 2800000]
y_0720 = ds_0720.variables['y'][:] # [2800000, ..., -2800000]

# Peninsula box: x in [-2700000, -1400000], y in [1950000, 250000]
# Indices
ix_start = int(np.where(x_0720 == -2700000)[0][0])
ix_end = int(np.where(x_0720 == -1400000)[0][0]) + 1
iy_start = int(np.where(y_0720 == 1950000)[0][0])
iy_end = int(np.where(y_0720 == 250000)[0][0]) + 1

print(f"NSIDC-0720 crop slice: ix=[{ix_start}:{ix_end}], iy=[{iy_start}:{iy_end}]")
print(f"Crop shape: ({iy_end - iy_start}, {ix_end - ix_start})")

vx_0720 = ds_0720.variables['VX'][iy_start:iy_end, ix_start:ix_end]
vy_0720 = ds_0720.variables['VY'][iy_start:iy_end, ix_start:ix_end]
errx_0720 = ds_0720.variables['ERRX'][iy_start:iy_end, ix_start:ix_end]
erry_0720 = ds_0720.variables['ERRY'][iy_start:iy_end, ix_start:ix_end]
cnt_0720 = ds_0720.variables['CNT'][iy_start:iy_end, ix_start:ix_end]

# Mask missing data (NaN where cnt == 0 or errx == 0 or np.isnan)
valid_0720 = (~np.isnan(vx_0720)) & (~np.isnan(vy_0720)) & (cnt_0720 > 0)
speed_0720 = np.full_like(vx_0720, np.nan, dtype=np.float32)
speed_0720[valid_0720] = np.sqrt(vx_0720[valid_0720]**2 + vy_0720[valid_0720]**2)

print(f"NSIDC-0720 valid cells: {np.sum(valid_0720):,} / {valid_0720.size:,} ({np.sum(valid_0720)/valid_0720.size*100:.1f}%)")
print(f"Speed stats (m/yr): min={np.nanmin(speed_0720):.1f}, mean={np.nanmean(speed_0720):.1f}, max={np.nanmax(speed_0720):.1f}")


# 2. NSIDC-0761 (450 m)
print("\n=== Processing NSIDC-0761 (450 m multi-year reference 2014-2017) ===")
ds_0761 = nc.Dataset("data/raw/measures/antarctica_ice_velocity_2014-2017_450m_v01.1.nc")
x_0761 = ds_0761.variables['x'][:]
y_0761 = ds_0761.variables['y'][:]

# Crop to Peninsula
idx_x_450 = np.where((x_0761 >= -2700000) & (x_0761 <= -1400000))[0]
idx_y_450 = np.where((y_0761 >= 250000) & (y_0761 <= 1950000))[0]
ix_start_450, ix_end_450 = idx_x_450[0], idx_x_450[-1] + 1
iy_start_450, iy_end_450 = idx_y_450[0], idx_y_450[-1] + 1

print(f"NSIDC-0761 crop slice: ix=[{ix_start_450}:{ix_end_450}], iy=[{iy_start_450}:{iy_end_450}]")
print(f"Crop shape: ({iy_end_450 - iy_start_450}, {ix_end_450 - ix_start_450})")

vx_0761 = ds_0761.variables['VX'][iy_start_450:iy_end_450, ix_start_450:ix_end_450]
vy_0761 = ds_0761.variables['VY'][iy_start_450:iy_end_450, ix_start_450:ix_end_450]
mask_0761 = ds_0761.variables['MASK'][iy_start_450:iy_end_450, ix_start_450:ix_end_450]

valid_0761 = (~np.isnan(vx_0761)) & (~np.isnan(vy_0761)) & (mask_0761 > 0)
speed_0761 = np.full_like(vx_0761, np.nan, dtype=np.float32)
speed_0761[valid_0761] = np.sqrt(vx_0761[valid_0761]**2 + vy_0761[valid_0761]**2)

print(f"NSIDC-0761 valid cells: {np.sum(valid_0761):,} / {valid_0761.size:,} ({np.sum(valid_0761)/valid_0761.size*100:.1f}%)")
print(f"Speed stats (m/yr): min={np.nanmin(speed_0761):.1f}, mean={np.nanmean(speed_0761):.1f}, max={np.nanmax(speed_0761):.1f}")

