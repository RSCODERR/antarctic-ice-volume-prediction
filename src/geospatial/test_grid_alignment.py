"""
Grid Alignment & Resampling Verification between Bedmap3 and BedMachine V4.1.
Audits the exact coordinate registration, half-pixel shift, and resampling methods.
"""

import os
import rasterio
from rasterio.warp import reproject, Resampling
import xarray as xr
import numpy as np

def audit_alignment():
    bm3_thick_path = "antarctic-ice-volume-prediction/data/processed/bedmap3_thickness_peninsula_500m.tif"
    bm_nc_path = "antarctic-ice-volume-prediction/data/raw/bedmachine/NSIDC-0756_BedMachineAntarctica_19700101-20191001_V04.1.nc"
    
    with rasterio.open(bm3_thick_path) as src:
        bm3_meta = src.meta.copy()
        bm3_transform = src.transform
        bm3_bounds = src.bounds
        bm3_crs = src.crs
        bm3_shape = src.shape
        
    print("="*80)
    print("BEDMAP3 ANALYSIS GRID SPECIFICATION")
    print("="*80)
    print(f"CRS:       {bm3_crs}")
    print(f"Shape:     {bm3_shape} (rows x cols)")
    print(f"Transform: {bm3_transform}")
    print(f"Bounds:    {bm3_bounds}")
    print(f"Col 0 center X: {bm3_transform[2] + 0.5 * bm3_transform[0]}")
    print(f"Row 0 center Y: {bm3_transform[5] + 0.5 * bm3_transform[4]}")
    
    ds = xr.open_dataset(bm_nc_path)
    print("\n" + "="*80)
    print("BEDMACHINE V4.1 NETCDF SPECIFICATION")
    print("="*80)
    print(f"X coordinate range: [{ds.x.values[0]}, {ds.x.values[-1]}], step: {ds.x.values[1] - ds.x.values[0]}")
    print(f"Y coordinate range: [{ds.y.values[0]}, {ds.y.values[-1]}], step: {ds.y.values[1] - ds.y.values[0]}")
    print(f"Global bounds: {ds.attrs.get('geospatial_bounds')}")
    
    # Check shift
    shift_x = (bm3_transform[2] + 0.5 * bm3_transform[0]) - ds.x.sel(x=-2700000, method='nearest').values
    shift_y = (bm3_transform[5] + 0.5 * bm3_transform[4]) - ds.y.sel(y=1950000, method='nearest').values
    print(f"\nCoordinate shift between pixel centers:")
    print(f"  Delta X: {shift_x} m (relative to nearest BedMachine cell)")
    print(f"  Delta Y: {shift_y} m (relative to nearest BedMachine cell)")

if __name__ == "__main__":
    audit_alignment()

