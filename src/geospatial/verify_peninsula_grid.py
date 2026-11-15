import xarray as xr
import numpy as np

nc_path = "antarctic-ice-volume-prediction/data/raw/imbie_basins/IMBIE_AIS_Regional_Delineations/IMBIE_AIS_Regional_Delineations_1km.nc"
ds = xr.open_dataset(nc_path)

x = ds['x'].values
y = ds['y'].values
mask_region = ds['mask_region'].values
mask_surface = ds['mask_surface'].values
mask_basin = ds['mask_basin'].values

# Peninsula region flag is 3
peninsula_idx = np.where(mask_region == 3)
print(f"Total Peninsula pixels (1 km grid): {len(peninsula_idx[0])}")

y_indices, x_indices = peninsula_idx
min_x, max_x = x[x_indices].min(), x[x_indices].max()
min_y, max_y = y[y_indices].min(), y[y_indices].max()

print(f"Peninsula Bounding Box on 1 km grid:")
print(f"  X: [{min_x:.0f}, {max_x:.0f}] meters")
print(f"  Y: [{min_y:.0f}, {max_y:.0f}] meters")

# Break down by surface type
ice_sheet_pixels = np.sum((mask_region == 3) & (mask_surface == 1))
island_pixels = np.sum((mask_region == 3) & (mask_surface == 2))
print(f"  Ice Sheet Grounded+Shelf Area: {ice_sheet_pixels:,} km²")
print(f"  Islands / Periphery Area:      {island_pixels:,} km²")
print(f"  Total Peninsula Area:          {ice_sheet_pixels + island_pixels:,} km²")

# Check basin flags in Peninsula
basins_in_pen = np.unique(mask_basin[mask_region == 3])
basin_names = [s.strip() for s in ds['mask_basin'].attrs['flag meaning'].split(',')]
print("\nBasins in Peninsula:")
for b in basins_in_pen:
    b_name = basin_names[b]
    count = np.sum((mask_region == 3) & (mask_basin == b))
    sheet_c = np.sum((mask_region == 3) & (mask_basin == b) & (mask_surface == 1))
    isl_c = np.sum((mask_region == 3) & (mask_basin == b) & (mask_surface == 2))
    print(f"  Flag {b:2d} ({b_name:6s}): Total {count:6d} km² | Ice_sheet {sheet_c:6d} km² | Islands {isl_c:6d} km²")

