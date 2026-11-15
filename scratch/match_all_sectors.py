import zipfile
import netCDF4 as nc
import tempfile
import os
import pandas as pd
import geopandas as gpd

zip_path = 'antarctic-ice-volume-prediction/data/raw/ismip6/ComputedScalarsPaper.zip'
with zipfile.ZipFile(zip_path, 'r') as z:
    for name in z.namelist():
        if 'computed_icearea_' in name and 'ctrl_proj_std' in name and 'UCIJPL' in name:
            with tempfile.NamedTemporaryFile(suffix='.nc', delete=False) as tmp:
                tmp.write(z.read(name))
                tmp_path = tmp.name
            ds = nc.Dataset(tmp_path, 'r')
            break

ismip6_areas = {}
for i in range(1, 19):
    var = f'icearea_sector_{i}'
    val = ds.variables[var][0] / 1e6
    ismip6_areas[f'Sector_{i}'] = val
for reg in [1, 2, 3]:
    var = f'icearea_region_{reg}'
    val = ds.variables[var][0] / 1e6
    ismip6_areas[f'Region_{reg}'] = val

ds.close()
os.remove(tmp_path)

shp_path = 'antarctic-ice-volume-prediction/data/raw/imbie_basins/IMBIE_AIS_Regional_Delineations/IMBIE_AIS_Regional_Delineations.shp'
gdf = gpd.read_file(shp_path)
gdf['area_km2'] = gdf.geometry.area / 1e6

print("=== ISMIP6 SECTOR TOTAL ICE AREAS (UCIJPL) ===")
for k, v in ismip6_areas.items():
    print(f"{k:12s}: {v:10.1f} km2")

print("\n=== IMBIE SHAPEFILE BASIN AREAS ===")
piv = gdf.pivot_table(index='Basin', columns='Type', values='area_km2', aggfunc='sum')
piv['Total'] = piv.sum(axis=1)
print(piv.round(1).to_string())

