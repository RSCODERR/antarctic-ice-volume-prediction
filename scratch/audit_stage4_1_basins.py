import os, netCDF4 as nc, numpy as np, pandas as pd

if not os.path.exists('data') and os.path.exists('antarctic-ice-volume-prediction'):
    os.chdir('antarctic-ice-volume-prediction')

bm_proc = 'data/processed/bedmachine_v4.1_peninsula_500m.nc'
if os.path.exists(bm_proc):
    ds = nc.Dataset(bm_proc)
    mask = ds.variables['mask'][:]
    thick = ds.variables['thickness'][:]
    surf = ds.variables['surface'][:]
    bed = ds.variables['bed'][:]
    firn = ds.variables['firn'][:]
    
    print("BedMachine Peninsula Processed NC Summary:")
    print("Mask unique values and counts:")
    unq, counts = np.unique(mask, return_counts=True)
    for u, c in zip(unq, counts):
        labels = {0: 'Ocean', 1: 'Ice-Free Rock', 2: 'Grounded Ice', 3: 'Floating Ice'}
        print(f"  Mask {u} ({labels.get(u, 'Unknown')}): {c:,} cells ({c * 0.25:,.2f} km^2)")
        
    grounded_mask = (mask == 2)
    print(f"\nTotal Grounded Cells in Cropped Raster: {np.sum(grounded_mask):,}")
    
    # Floating ice stats
    floating_mask = (mask == 3)
    print(f"Total Floating Shelf Cells in Cropped Raster: {np.sum(floating_mask):,} ({np.sum(floating_mask)*0.25:,.2f} km^2)")
    if np.sum(floating_mask) > 0:
        fl_thick = thick[floating_mask]
        print(f"  Floating Shelf Thickness: Mean = {np.nanmean(fl_thick):.1f} m, Median = {np.nanmedian(fl_thick):.1f} m, Min = {np.nanmin(fl_thick):.1f} m, Max = {np.nanmax(fl_thick):.1f} m")
    
    ds.close()
else:
    print("Processed NetCDF not found!")

