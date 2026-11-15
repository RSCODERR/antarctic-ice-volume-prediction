"""
Spatial Preprocessing Module: Antarctic Peninsula Domain Cropping
Aligns and crops Antarctic baseline grids to the scientifically verified
Antarctic Peninsula domain (EPSG:3031).
Preserves native 500 m pixel resolution without resampling or interpolation.
"""

import os
import rasterio
from rasterio.windows import from_bounds
import geopandas as gpd
import numpy as np

# Verified Domain Coordinates in EPSG:3031
# Bounds derived from IMBIE Basins (Hp-I, I-Ipp, Ipp-J) + 20 km buffer
PENINSULA_BOUNDS = {
    'min_x': -2700000.0,
    'max_x': -1400000.0,
    'min_y':  250000.0,
    'max_y': 1950000.0,
    'crs': 'EPSG:3031',
    'res_m': 500.0
}

def crop_geotiff(input_path: str, output_path: str, bounds: dict = PENINSULA_BOUNDS):
    """
    Crops an EPSG:3031 GeoTIFF to the specified bounds preserving pixel alignment.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Source file not found: {input_path}")
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with rasterio.open(input_path) as src:
        # Verify CRS
        if src.crs.to_string() != bounds['crs']:
            raise ValueError(f"Expected CRS {bounds['crs']}, but got {src.crs}")
        
        # Calculate pixel window
        window = from_bounds(
            bounds['min_x'], bounds['min_y'],
            bounds['max_x'], bounds['max_y'],
            transform=src.transform
        )
        
        # Round window to exact integer pixel coordinates to avoid sub-pixel shifting
        window = window.round_lengths().round_offsets()
        
        # Read data in window
        data = src.read(window=window)
        transform = rasterio.windows.transform(window, src.transform)
        
        meta = src.meta.copy()
        meta.update({
            'driver': 'GTiff',
            'height': data.shape[1],
            'width': data.shape[2],
            'transform': transform,
            'compress': 'deflate'
        })
        
        with rasterio.open(output_path, 'w', **meta) as dst:
            dst.write(data)
            
        print(f"Successfully cropped {os.path.basename(input_path)} -> {output_path}")
        print(f"  Shape: {data.shape[1:]}, Res: {transform[0]:.1f}m, Transform: {transform}")
        print(f"  Bounds: {rasterio.windows.bounds(window, src.transform)}")
        return output_path

if __name__ == "__main__":
    raw_dir = "antarctic-ice-volume-prediction/data/raw/bedmap3"
    proc_dir = "antarctic-ice-volume-prediction/data/processed"
    
    # Crop thickness
    crop_geotiff(
        os.path.join(raw_dir, "bm3_thickness.tif"),
        os.path.join(proc_dir, "bedmap3_thickness_peninsula_500m.tif")
    )
    
    # Crop masks
    crop_geotiff(
        os.path.join(raw_dir, "bm3_masks.tif"),
        os.path.join(proc_dir, "bedmap3_masks_peninsula_500m.tif")
    )

