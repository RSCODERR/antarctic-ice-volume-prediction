import os, hashlib, json, netCDF4 as nc, rasterio, geopandas as gpd

if not os.path.exists('data') and os.path.exists('antarctic-ice-volume-prediction'):
    os.chdir('antarctic-ice-volume-prediction')

def get_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(1048576):
            h.update(chunk)
    return h.hexdigest()

files_to_audit = [
    ('BedMachine v4.1 Raw NetCDF', 'data/raw/bedmachine/NSIDC-0756_BedMachineAntarctica_19700101-20191001_V04.1.nc'),
    ('BedMachine v4.1 Peninsula Processed NetCDF', 'data/processed/bedmachine_v4.1_peninsula_500m.nc'),
    ('Bedmap3 Bed GeoTIFF', 'data/raw/bedmap3/bm3_bed.tif'),
    ('Bedmap3 Surface GeoTIFF', 'data/raw/bedmap3/bm3_surface.tif'),
    ('Bedmap3 Thickness GeoTIFF', 'data/raw/bedmap3/bm3_thickness.tif'),
    ('Bedmap3 Masks GeoTIFF', 'data/raw/bedmap3/bm3_masks.tif'),
    ('Bedmap3 Uncertainty GeoTIFF', 'data/raw/bedmap3/bm3_thickness_uncertainty.tif'),
    ('Bedmap3 Peninsula Masks Processed', 'data/processed/bedmap3_masks_peninsula_500m.tif'),
    ('Bedmap3 Peninsula Thickness Processed', 'data/processed/bedmap3_thickness_peninsula_500m.tif'),
    ('IMBIE Basins Shapefile', 'data/raw/imbie_basins/IMBIE_AIS_Regional_Delineations.shp'),
    ('IMBIE 3 Mass Balance CSV', 'data/raw/imbie/imbie3_antarctic_peninsula_Gt_partitioned.csv')
]

results = []

for name, path in files_to_audit:
    if os.path.exists(path):
        size = os.path.getsize(path)
        print(f"Hashing {name} ({size:,} bytes)...")
        sha = get_sha256(path)
        
        info = {'name': name, 'path': path, 'size': size, 'sha256': sha}
        
        # Spatial metadata
        if path.endswith('.nc'):
            try:
                ds = nc.Dataset(path)
                info['variables'] = list(ds.variables.keys())
                info['dimensions'] = {k: len(v) for k, v in ds.dimensions.items()}
                ds.close()
            except Exception as e:
                info['nc_err'] = str(e)
        elif path.endswith('.tif'):
            try:
                with rasterio.open(path) as src:
                    info['width'] = src.width
                    info['height'] = src.height
                    info['crs'] = str(src.crs)
                    info['bounds'] = [src.bounds.left, src.bounds.bottom, src.bounds.right, src.bounds.top]
                    info['transform'] = list(src.transform)
            except Exception as e:
                info['tif_err'] = str(e)
        elif path.endswith('.shp'):
            try:
                gdf = gpd.read_file(path)
                info['crs'] = str(gdf.crs)
                info['features_count'] = len(gdf)
                info['columns'] = list(gdf.columns)
            except Exception as e:
                info['shp_err'] = str(e)
        elif path.endswith('.csv'):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    lines = [f.readline() for _ in range(5)]
                info['header'] = lines[0].strip()
                info['sample_rows'] = len(lines) - 1
            except Exception as e:
                info['csv_err'] = str(e)
                
        results.append(info)
    else:
        results.append({'name': name, 'path': path, 'status': 'NOT FOUND'})

with open('scratch/existing_data_audit_results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2)

print("\nAudit completed. Results saved to scratch/existing_data_audit_results.json")

