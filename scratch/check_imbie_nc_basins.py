import zipfile
import netCDF4 as nc
import tempfile
import os
import numpy as np

zip_path = 'antarctic-ice-volume-prediction/data/raw/imbie_basins/IMBIE_AIS_Regional_Delineations.zip'
with zipfile.ZipFile(zip_path, 'r') as z:
    with tempfile.NamedTemporaryFile(suffix='.nc', delete=False) as tmp:
        tmp.write(z.read('IMBIE_AIS_Regional_Delineations/IMBIE_AIS_Regional_Delineations_5km.nc'))
        tmp_path = tmp.name

ds = nc.Dataset(tmp_path, 'r')
reg = ds.variables['mask_region'][:]
bas = ds.variables['mask_basin'][:]
surf = ds.variables['mask_surface'][:]

print("Unique regions:", np.unique(reg))
print("Unique basins in Region 3 (Peninsula):", np.unique(bas[reg == 3]))

cell_area = 25.0 # 5km x 5km = 25 km2
for b_val in np.unique(bas[reg == 3]):
    count_all = np.sum((bas == b_val) & (reg == 3))
    count_ice = np.sum((bas == b_val) & (reg == 3) & (surf == 1))
    count_isl = np.sum((bas == b_val) & (reg == 3) & (surf == 2))
    print(f"Basin {b_val}: Total={count_all*cell_area:.1f} km2 (Ice_sheet={count_ice*cell_area:.1f}, Island={count_isl*cell_area:.1f})")

ds.close()
os.remove(tmp_path)

