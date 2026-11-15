"""
Audit all datasets currently on disk in data/raw/.
"""
import os
import hashlib
import xarray as xr
import geopandas as gpd

print("=== RAW DATASET INVENTORY AUDIT ===")

for root, dirs, files in os.walk("data/raw"):
    for fn in files:
        if fn.endswith(('.nc', '.tif', '.gpkg', '.shp', '.csv')):
            fp = os.path.join(root, fn)
            sz = os.path.getsize(fp)
            with open(fp, "rb") as fl:
                hdr = fl.read(16)
                fl.seek(0)
                sha = hashlib.sha256(fl.read()).hexdigest()
            print(f"File: {fn}")
            print(f"  Path: {fp}")
            print(f"  Size: {sz:,} bytes ({sz/(1024*1024):.2f} MB)")
            print(f"  Header: {hdr[:4]}")
            print(f"  SHA-256: {sha}")
            
            # Metadata inspection
            if fn.endswith('.nc'):
                try:
                    ds = xr.open_dataset(fp)
                    print(f"  NetCDF Dims: {dict(ds.dims)}")
                    print(f"  NetCDF Vars: {list(ds.data_vars.keys())}")
                    ds.close()
                except Exception as e:
                    print(f"  NetCDF Open Error: {e}")
            elif fn.endswith('.gpkg'):
                try:
                    gdf = gpd.read_file(fp)
                    print(f"  GeoPackage Layers/Rows: {len(gdf)} rows, CRS: {gdf.crs}")
                    print(f"  GeoPackage Columns: {list(gdf.columns)}")
                except Exception as e:
                    print(f"  GeoPackage Open Error: {e}")
            print()

