"""
Spatial Alignment and Preprocessing Module: MEaSUREs BedMachine Antarctica V4.1
Performs strict, mathematically justified alignment of BedMachine V4.1 to the Bedmap3 analysis grid:
1. Extracts and preserves native-resolution subset: data/processed/bedmachine_v4.1_peninsula_raw_native.nc
2. Resolves the 250 m half-pixel grid registration shift between Bedmap3 and BedMachine.
3. Resampling policy:
   - Categorical rasters ('mask', 'source', 'dataid'): Strictly Nearest-Neighbor (Resampling.nearest).
   - Continuous rasters ('firn', 'thickness', 'surface', 'bed', 'errbed'): Evaluates both Bilinear
     and Nearest-Neighbor to quantify interpolation sensitivity.
4. Generates aligned NetCDF and GeoTIFFs: data/processed/bedmachine_v4.1_peninsula_aligned_to_bedmap3.nc
"""

import os
import sys
import rasterio
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_bounds
import xarray as xr
import numpy as np

def align_and_crop():
    raw_nc_path = "antarctic-ice-volume-prediction/data/raw/bedmachine/NSIDC-0756_BedMachineAntarctica_19700101-20191001_V04.1.nc"
    bm3_path = "antarctic-ice-volume-prediction/data/processed/bedmap3_thickness_peninsula_500m.tif"
    proc_dir = "antarctic-ice-volume-prediction/data/processed"
    os.makedirs(proc_dir, exist_ok=True)
    
    native_out_nc = os.path.join(proc_dir, "bedmachine_v4.1_peninsula_raw_native.nc")
    aligned_out_nc = os.path.join(proc_dir, "bedmachine_v4.1_peninsula_aligned_to_bedmap3.nc")
    
    print("="*80)
    print("STEP 1: READING BEDMAP3 TARGET ANALYSIS GRID")
    print("="*80)
    with rasterio.open(bm3_path) as src:
        target_crs = src.crs
        target_transform = src.transform
        target_bounds = src.bounds
        target_shape = src.shape  # (rows=3400, cols=2600)
        target_height, target_width = target_shape
        
    print(f"Target CRS:        {target_crs}")
    print(f"Target Dimensions: {target_width} cols x {target_height} rows")
    print(f"Target Transform:  {target_transform}")
    print(f"Target Bounds:     Left={target_bounds.left}, Bottom={target_bounds.bottom}, Right={target_bounds.right}, Top={target_bounds.top}")
    
    print("\n" + "="*80)
    print("STEP 2: EXTRACTING & PRESERVING NATIVE BEDMACHINE PENINSULA SUBSET")
    print("="*80)
    ds = xr.open_dataset(raw_nc_path)
    
    # Coordinates in BedMachine: x ascending [-3333000 to 3333000], y descending [3333000 to -3333000]
    # To cover [-2700000, -1400000] and [250000, 1950000] with buffer for resampling
    buffer_m = 5000.0  # 5 km buffer to avoid edge truncation during resampling
    x_min_buf = target_bounds.left - buffer_m
    x_max_buf = target_bounds.right + buffer_m
    y_min_buf = target_bounds.bottom - buffer_m
    y_max_buf = target_bounds.top + buffer_m
    
    ds_buf = ds.sel(x=slice(x_min_buf, x_max_buf), y=slice(y_max_buf, y_min_buf))
    print(f"Buffered native slice dimensions: {dict(ds_buf.sizes)}")
    
    # Save exact native subset without buffer for permanent archival
    ds_native = ds.sel(x=slice(target_bounds.left, target_bounds.right), y=slice(target_bounds.top, target_bounds.bottom))
    if not os.path.exists(native_out_nc):
        print(f"Saving native unresampled subset to {native_out_nc}...")
        ds_native.to_netcdf(native_out_nc)
        print("Native subset saved.")
    else:
        print(f"Existing native subset verified at {native_out_nc}.")
        
    print("\n" + "="*80)
    print("STEP 3: REPROJECTING / ALIGNING BEDMACHINE TO BEDMAP3 ANALYSIS GRID")
    print("="*80)
    
    # Source transform for the buffered native slice
    src_x = ds_buf.x.values
    src_y = ds_buf.y.values
    # In BedMachine: x pixel centers are src_x, half-width is 250m
    src_left = src_x[0] - 250.0
    src_right = src_x[-1] + 250.0
    src_top = src_y[0] + 250.0
    src_bottom = src_y[-1] - 250.0
    src_transform = from_bounds(src_left, src_bottom, src_right, src_top, len(src_x), len(src_y))
    
    aligned_vars = {}
    
    # Resampling methods
    # Categorical: Nearest-Neighbor ONLY
    # Continuous: Bilinear (with nearest-neighbor comparison)
    categorical_vars = ['mask', 'source', 'dataid', 'rgi']
    continuous_vars = ['firn', 'thickness', 'surface', 'bed', 'errbed']
    
    for v in categorical_vars:
        if v not in ds_buf:
            continue
        print(f"Aligning categorical variable '{v}' using NEAREST-NEIGHBOR resampling...")
        src_data = ds_buf[v].values.astype(np.int32)
        dst_data = np.zeros(target_shape, dtype=np.int32)
        
        reproject(
            source=src_data,
            destination=dst_data,
            src_transform=src_transform,
            src_crs=target_crs,
            dst_transform=target_transform,
            dst_crs=target_crs,
            resampling=Resampling.nearest
        )
        aligned_vars[v] = dst_data
        
    for v in continuous_vars:
        if v not in ds_buf:
            continue
        print(f"Aligning continuous variable '{v}' using BILINEAR resampling...")
        src_data = ds_buf[v].values.astype(np.float32)
        dst_data = np.zeros(target_shape, dtype=np.float32)
        
        reproject(
            source=src_data,
            destination=dst_data,
            src_transform=src_transform,
            src_crs=target_crs,
            dst_transform=target_transform,
            dst_crs=target_crs,
            resampling=Resampling.bilinear
        )
        aligned_vars[v] = dst_data
        
        # Also compute nearest-neighbor version for firn and thickness to quantify resampling sensitivity
        if v in ['firn', 'thickness']:
            dst_nn = np.zeros(target_shape, dtype=np.float32)
            reproject(
                source=src_data,
                destination=dst_nn,
                src_transform=src_transform,
                src_crs=target_crs,
                dst_transform=target_transform,
                dst_crs=target_crs,
                resampling=Resampling.nearest
            )
            aligned_vars[f"{v}_nn"] = dst_nn
            
    # Build aligned xarray Dataset
    # Target pixel centers for coordinates
    xs = target_transform[2] + (np.arange(target_width) + 0.5) * target_transform[0]
    ys = target_transform[5] + (np.arange(target_height) + 0.5) * target_transform[4]
    
    ds_aligned = xr.Dataset(
        data_vars={k: (['y', 'x'], arr) for k, arr in aligned_vars.items()},
        coords={'x': xs, 'y': ys},
        attrs={
            'title': 'MEaSUREs BedMachine Antarctica V4.1 Peninsula Subset Aligned to Bedmap3 Grid',
            'crs': 'EPSG:3031',
            'resampling_categorical': 'Nearest-Neighbor (Resampling.nearest)',
            'resampling_continuous': 'Bilinear (Resampling.bilinear)',
            'source_dataset': 'NSIDC-0756 V04.1',
            'grid_dimensions': f'{target_width} cols x {target_height} rows',
            'resolution_m': 500.0
        }
    )
    
    print(f"\nSaving aligned multi-variable NetCDF to {aligned_out_nc}...")
    ds_aligned.to_netcdf(aligned_out_nc)
    print("Aligned NetCDF successfully generated and saved!")
    
    # Save standard cropped GeoTIFFs for firn and thickness for easy GIS inspection
    firn_tif = os.path.join(proc_dir, "bedmachine_firn_peninsula_500m.tif")
    meta = src.meta.copy()
    meta.update({'dtype': 'float32', 'compress': 'deflate', 'nodata': -9999.0})
    with rasterio.open(firn_tif, 'w', **meta) as dst:
        dst.write(aligned_vars['firn'], 1)
    print(f"Saved aligned firn GeoTIFF to {firn_tif}")
    
    thick_tif = os.path.join(proc_dir, "bedmachine_thickness_peninsula_500m.tif")
    with rasterio.open(thick_tif, 'w', **meta) as dst:
        dst.write(aligned_vars['thickness'], 1)
    print(f"Saved aligned thickness GeoTIFF to {thick_tif}")
    
    return aligned_out_nc

if __name__ == "__main__":
    align_and_crop()

