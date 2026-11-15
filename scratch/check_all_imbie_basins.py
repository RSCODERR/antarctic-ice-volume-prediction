import zipfile
import netCDF4 as nc
import tempfile
import os
import numpy as np
import pandas as pd

zip_path = 'antarctic-ice-volume-prediction/data/raw/imbie_basins/IMBIE_AIS_Regional_Delineations.zip'
with zipfile.ZipFile(zip_path, 'r') as z:
    with tempfile.NamedTemporaryFile(suffix='.nc', delete=False) as tmp:
        tmp.write(z.read('IMBIE_AIS_Regional_Delineations/IMBIE_AIS_Regional_Delineations_5km.nc'))
        tmp_path = tmp.name

ds = nc.Dataset(tmp_path, 'r')
reg = ds.variables['mask_region'][:]
bas = ds.variables['mask_basin'][:]
surf = ds.variables['mask_surface'][:]

names = ['None', 'A-Ap', 'Ap-B', 'B-C', 'C-Cp', 'Cp-D', 'D-Dp', 'Dp-E', 'E-Ep', 
         'Ep-F', 'F-G', 'G-H', 'H-Hp', 'Hp-I', 'I-Ipp', 'Ipp-J', 'J-Jpp', 'Jpp-K', 'K-A']

rows = []
for b in range(1, 19):
    m = (bas == b)
    r_val = np.unique(reg[m])[0] if np.any(m) else 0
    r_name = ['None', 'East', 'West', 'Peninsula'][r_val]
    tot = np.sum(m) * 25.0
    ice = np.sum(m & (surf == 1)) * 25.0
    isl = np.sum(m & (surf == 2)) * 25.0
    rows.append({'IMBIE_Index': b, 'Basin_Name': names[b], 'Region': r_name, 'Ice_sheet_km2': ice, 'Islands_km2': isl, 'Total_km2': tot})

ds.close()
os.remove(tmp_path)

df = pd.DataFrame(rows)
print(df.to_string())

