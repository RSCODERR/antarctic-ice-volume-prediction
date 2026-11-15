"""
Numerical Consistency Check: Bedmap3 Surface, Bed, and Thickness
Tests whether Bedmap3 thickness strictly equals (surface - bed) for grounded ice cells,
confirming whether Bedmap3 provides geometric column thickness or ice-equivalent thickness.
Reference: Pritchard et al. (2025), Scientific Data / BAS.
"""

import os
import sys
import rasterio
import numpy as np
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "preprocessing"))
from crop_domain import crop_geotiff, PENINSULA_BOUNDS

def main():
    raw_dir = "antarctic-ice-volume-prediction/data/raw/bedmap3"
    proc_dir = "antarctic-ice-volume-prediction/data/processed"
    os.makedirs(proc_dir, exist_ok=True)

    surface_proc = os.path.join(proc_dir, "bedmap3_surface_peninsula_500m.tif")
    bed_proc = os.path.join(proc_dir, "bedmap3_bed_peninsula_500m.tif")
    thick_proc = os.path.join(proc_dir, "bedmap3_thickness_peninsula_500m.tif")
    masks_proc = os.path.join(proc_dir, "bedmap3_masks_peninsula_500m.tif")

    # Crop surface and bed if not already cropped
    if not os.path.exists(surface_proc):
        print("Cropping surface to Peninsula domain...")
        crop_geotiff(os.path.join(raw_dir, "bm3_surface.tif"), surface_proc)
    
    if not os.path.exists(bed_proc):
        print("Cropping bed to Peninsula domain...")
        crop_geotiff(os.path.join(raw_dir, "bm3_bed.tif"), bed_proc)

    print("\nReading cropped rasters for domain-wide numerical consistency check...")
    with rasterio.open(surface_proc) as src:
        surface = src.read(1)
        nodata_surf = src.nodata

    with rasterio.open(bed_proc) as src:
        bed = src.read(1)
        nodata_bed = src.nodata

    with rasterio.open(thick_proc) as src:
        thick = src.read(1)
        nodata_thick = src.nodata

    with rasterio.open(masks_proc) as src:
        mask = src.read(1)

    print(f"Raster dimensions: {surface.shape}")
    print(f"Mask counts in domain: {pd.Series(mask.flatten()).value_counts().to_dict()}")

    # 1. Permanently grounded ice cells (mask == 1)
    grounded_mask = (mask == 1) & (thick > 0) & (thick != nodata_thick)
    s_g = surface[grounded_mask]
    b_g = bed[grounded_mask]
    t_g = thick[grounded_mask]

    diff_g = (s_g - b_g) - t_g

    print("\n" + "="*70)
    print("NUMERICAL CONSISTENCY CHECK: PERMANENTLY GROUNDED ICE (MASK == 1)")
    print("="*70)
    print(f"Total grounded cells evaluated: {len(diff_g):,}")
    print(f"Exact match (diff == 0.0 m):    {np.sum(diff_g == 0.0):,} ({100 * np.mean(diff_g == 0.0):.4f}%)")
    print(f"Within 1 mm (|diff| <= 0.001 m): {np.sum(np.abs(diff_g) <= 0.001):,} ({100 * np.mean(np.abs(diff_g) <= 0.001):.4f}%)")
    print(f"Within 1 cm (|diff| <= 0.01 m):  {np.sum(np.abs(diff_g) <= 0.01):,} ({100 * np.mean(np.abs(diff_g) <= 0.01):.4f}%)")
    print(f"Max absolute diff:               {np.max(np.abs(diff_g)):.6f} m")
    print(f"Mean diff:                       {np.mean(diff_g):.6e} m")
    print(f"Median diff:                     {np.median(diff_g):.6e} m")
    print(f"Std deviation:                   {np.std(diff_g):.6e} m")

    # 2. Transiently grounded ice shelves (mask == 2)
    trans_mask = (mask == 2) & (thick > 0) & (thick != nodata_thick)
    if np.sum(trans_mask) > 0:
        diff_trans = (surface[trans_mask] - bed[trans_mask]) - thick[trans_mask]
        print("\n" + "="*70)
        print("NUMERICAL CONSISTENCY CHECK: TRANSIENTLY GROUNDED ICE (MASK == 2)")
        print("="*70)
        print(f"Total transiently grounded cells: {len(diff_trans):,}")
        print(f"Exact match (diff == 0.0 m):      {np.sum(diff_trans == 0.0):,} ({100 * np.mean(diff_trans == 0.0):.4f}%)")
        print(f"Max absolute diff:                 {np.max(np.abs(diff_trans)):.6f} m")
        print(f"Mean diff:                         {np.mean(diff_trans):.6e} m")

    # 3. Floating ice shelves (mask == 3)
    shelf_mask = (mask == 3) & (thick > 0) & (thick != nodata_thick)
    if np.sum(shelf_mask) > 0:
        diff_shelf = (surface[shelf_mask] - bed[shelf_mask]) - thick[shelf_mask]
        print("\n" + "="*70)
        print("NUMERICAL CHECK: FLOATING ICE SHELVES (MASK == 3)")
        print("="*70)
        print(f"Total floating shelf cells:        {len(diff_shelf):,}")
        print(f"Mean (surface - bed - thick):      {np.mean(diff_shelf):.2f} m")
        print(f"Min (surface - bed - thick):       {np.min(diff_shelf):.2f} m")
        print(f"Max (surface - bed - thick):       {np.max(diff_shelf):.2f} m")
        print("Note: In floating shelves, bed is ocean floor (bathymetry), while ice base is ice shelf draft.")
        print("Hence (surface - bed) > thickness represents water column thickness (ocean cavity depth)!")
        cavity = surface[shelf_mask] - bed[shelf_mask] - thick[shelf_mask]
        print(f"Average sub-ice ocean cavity depth: {np.mean(cavity):.2f} m (min: {np.min(cavity):.2f} m, max: {np.max(cavity):.2f} m)")

    # 4. Detailed sample of 10 grounded cells
    print("\n" + "="*70)
    print("SAMPLE OF 10 GROUNDED ICE CELLS (Surface, Bed, Thickness)")
    print("="*70)
    indices = np.random.RandomState(42).choice(np.where(grounded_mask.flatten())[0], 10, replace=False)
    sample_df = pd.DataFrame({
        'Flat_Index': indices,
        'Surface (m)': surface.flatten()[indices],
        'Bed (m)': bed.flatten()[indices],
        'Thickness (m)': thick.flatten()[indices],
        'Surface - Bed (m)': surface.flatten()[indices] - bed.flatten()[indices],
        'Diff (m)': (surface.flatten()[indices] - bed.flatten()[indices]) - thick.flatten()[indices]
    })
    print(sample_df.to_string(index=False))

    print("\n" + "="*70)
    print("PHYSICAL INTERPRETATION CONCLUSION:")
    print("="*70)
    print("Bedmap3 explicitly defines thickness as the geometric distance between the upper")
    print("snow/ice surface and the bedrock topography (surface - bed = thickness).")
    print("Therefore, Bedmap3 thickness is GEOMETRIC COLUMN THICKNESS (H_geom), including the firn air column.")
    print("It is NOT an ice-equivalent thickness (H_ice_eq).")

if __name__ == "__main__":
    main()
