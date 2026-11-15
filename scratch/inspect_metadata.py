import rasterio
import netCDF4
import os
import hashlib

def get_sha256(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        while c := f.read(65536):
            h.update(c)
    return h.hexdigest()

print('=== BEDMACHINE V4.1 ===')
bm_path = 'data/raw/bedmachine/NSIDC-0756_BedMachineAntarctica_19700101-20191001_V04.1.nc'
with netCDF4.Dataset(bm_path, 'r') as ds:
    print('Dimensions:', {k: v.size for k, v in ds.dimensions.items()})
    print('Variables:', list(ds.variables.keys()))
    print('x range:', ds.variables['x'][:].min(), ds.variables['x'][:].max())
    print('y range:', ds.variables['y'][:].min(), ds.variables['y'][:].max())
    for v in ['thickness', 'bed', 'surface', 'firn', 'mask']:
        var = ds.variables[v]
        units = getattr(var, 'units', 'none')
        nodata = getattr(var, '_FillValue', 'none')
        print(f'  {v}: dtype={var.dtype}, shape={var.shape}, units={units}, nodata={nodata}')

print('\n=== BEDMAP3 ===')
for name in ['bm3_thickness.tif', 'bm3_bed.tif', 'bm3_surface.tif', 'bm3_masks.tif', 'bm3_thickness_uncertainty.tif']:
    p = os.path.join('data/raw/bedmap3', name)
    with rasterio.open(p) as src:
        print(f'{name}: shape={src.shape}, res={src.res}, crs={src.crs}, nodata={src.nodata}, bounds={src.bounds}')

print('\n=== IMBIE BASINS ===')
imbie_path = 'data/raw/imbie_basins/IMBIE_AIS_Regional_Delineations/IMBIE_AIS_Regional_Delineations_1km.nc'
with netCDF4.Dataset(imbie_path, 'r') as ds:
    print('IMBIE 1km dims:', {k: v.size for k, v in ds.dimensions.items()})
    print('IMBIE 1km vars:', list(ds.variables.keys()))
    for v in ds.variables.keys():
        var = ds.variables[v]
        print(f'  {v}: dtype={var.dtype}, shape={var.shape}, attrs={var.ncattrs()}')

