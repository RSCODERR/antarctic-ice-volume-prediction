import os
import netCDF4 as nc
import rasterio
import pandas as pd

if not os.path.exists('data') and os.path.exists('antarctic-ice-volume-prediction'):
    os.chdir('antarctic-ice-volume-prediction')

print("--- BedMachine NetCDF Inspection ---")
bm_path = "data/processed/bedmachine_v4.1_peninsula_aligned_to_bedmap3.nc"
if os.path.exists(bm_path):
    ds = nc.Dataset(bm_path, "r")
    print("Variables:", list(ds.variables.keys()))
    print("Dimensions:", {d: len(ds.dimensions[d]) for d in ds.dimensions})
    for v in ['x', 'y', 'bed', 'surface', 'thickness', 'mask']:
        if v in ds.variables:
            var = ds.variables[v]
            print(f"  {v}: shape={var.shape}, dtype={var.dtype}")
    ds.close()

print("\n--- Raw Data Inventory ---")
for root, dirs, files in os.walk('data/raw'):
    for f in files:
        p = os.path.join(root, f)
        sz_mb = os.path.getsize(p) / (1024 * 1024)
        print(f"  {p}: {sz_mb:.2f} MB")

print("\n--- Processed Data Inventory ---")
for root, dirs, files in os.walk('data/processed'):
    for f in files:
        p = os.path.join(root, f)
        sz_mb = os.path.getsize(p) / (1024 * 1024)
        print(f"  {p}: {sz_mb:.2f} MB")

