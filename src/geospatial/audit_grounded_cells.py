"""
Audit Script for Issue 1: Grounded-Cell Area Reconciliation and Polygon Masking Audit.
"""

import os
import rasterio
from rasterio.mask import mask as rmask
import geopandas as gpd
import numpy as np
import pandas as pd
import sys

sys.path.append(os.path.abspath('antarctic-ice-volume-prediction'))
from src.geospatial.audit_distortion import compute_scale_factor_grid

def audit_grounded_cells():
    proc_dir = "antarctic-ice-volume-prediction/data/processed"
    raw_dir = "antarctic-ice-volume-prediction/data/raw"
    
    thick_path = os.path.join(proc_dir, "bedmap3_thickness_peninsula_500m.tif")
    masks_path = os.path.join(proc_dir, "bedmap3_masks_peninsula_500m.tif")
    shp_path = os.path.join(raw_dir, "imbie_basins/IMBIE_AIS_Regional_Delineations/IMBIE_AIS_Regional_Delineations.shp")
    
    # 1. Load raster metadata and arrays
    with rasterio.open(masks_path) as src_m, rasterio.open(thick_path) as src_t:
        mask_arr = src_m.read(1)
        thick_arr = src_t.read(1)
        nodata_thick = src_t.nodata
        raster_crs = src_m.crs
        raster_transform = src_m.transform
        raster_bounds = src_m.bounds
        height, width = mask_arr.shape
        
    print("="*80)
    print("1. RASTER DOMAIN SPECIFICATIONS")
    print("="*80)
    print(f"Raster dimensions: {width} cols x {height} rows = {width*height:,} total cells")
    print(f"Raster CRS:        {raster_crs}")
    print(f"Raster Bounds:     Left={raster_bounds.left}, Bottom={raster_bounds.bottom}, Right={raster_bounds.right}, Top={raster_bounds.top}")
    print(f"Resolution:        {raster_transform[0]} m x {-raster_transform[4]} m")
    
    # Scale factor
    areal_scale, lat_grid, lon_grid = compute_scale_factor_grid(raster_transform, height, width)
    true_cell_area_km2 = 0.25 / areal_scale
    
    # Grounded cells in entire raster domain
    total_domain_m1 = (mask_arr == 1)
    total_domain_grounded = (mask_arr == 1) & (thick_arr > 0) & (thick_arr != nodata_thick)
    
    print("\n" + "="*80)
    print("2. TOTAL GROUNDED CELLS IN RECTANGULAR CROPPED DOMAIN")
    print("="*80)
    print(f"Total cells with mask == 1:                  {np.sum(total_domain_m1):,}")
    print(f"Total cells with mask == 1 & thickness > 0:  {np.sum(total_domain_grounded):,}")
    print(f"Total projected area (0.25 km²/cell):        {np.sum(total_domain_grounded) * 0.25:,.2f} km²")
    print(f"Total true ground area:                      {np.sum(true_cell_area_km2[total_domain_grounded]):,.2f} km²")
    
    # 2. Inspect IMBIE Basin Shapefile
    gdf = gpd.read_file(shp_path)
    print("\n" + "="*80)
    print("3. IMBIE BASIN SHAPEFILE AUDIT")
    print("="*80)
    print(f"Shapefile CRS: {gdf.crs}")
    print(f"Total features in shapefile: {len(gdf)}")
    print(f"Regions in shapefile: {gdf['Region'].unique()}")
    print(f"Types in Peninsula:   {gdf[gdf['Region']=='Peninsula']['Type'].unique()}")
    
    # Peninsula ice sheet basins
    pen_basins = gdf[(gdf['Region'] == 'Peninsula') & (gdf['Type'] == 'Ice_sheet')].sort_values('Basin')
    print(f"Peninsula Ice Sheet Basins: {pen_basins['Basin'].tolist()}")
    
    # All Peninsula features (including islands, ice shelves)
    pen_all = gdf[gdf['Region'] == 'Peninsula']
    print(f"All Peninsula Types: {pen_all['Type'].value_counts().to_dict()}")
    
    # Other regions present in domain
    print("\nChecking which shapefile polygons intersect our raster bounding box...")
    from shapely.geometry import box
    domain_geom = box(raster_bounds.left, raster_bounds.bottom, raster_bounds.right, raster_bounds.top)
    intersecting_features = gdf[gdf.intersects(domain_geom)]
    print(f"Features intersecting domain: {len(intersecting_features)}")
    for _, feat in intersecting_features.iterrows():
        print(f"  • Region: {feat['Region']:<15} | Basin: {feat['Basin']:<10} | Type: {feat['Type']}")
        
    # 3. Masking inside each basin using both all_touched=False and all_touched=True
    print("\n" + "="*80)
    print("4. BASIN-BY-BASIN CELL COUNTS (all_touched=False vs all_touched=True)")
    print("="*80)
    
    # Unified peninsula ice sheet mask
    basin_cells_false = {}
    basin_cells_true = {}
    basin_area_proj = {}
    basin_area_ground = {}
    
    combined_mask_false = np.zeros((height, width), dtype=bool)
    combined_mask_true = np.zeros((height, width), dtype=bool)
    
    for b in ['Hp-I', 'I-Ipp', 'Ipp-J']:
        geom = pen_basins[pen_basins['Basin'] == b].geometry
        
        with rasterio.open(masks_path) as src_m, rasterio.open(thick_path) as src_t:
            # all_touched = False (default: center pixel inside polygon)
            m_f, _ = rmask(src_m, geom, crop=False, all_touched=False, nodata=-9999)
            t_f, _ = rmask(src_t, geom, crop=False, all_touched=False, nodata=-9999)
            valid_f = (m_f[0] == 1) & (t_f[0] > 0) & (t_f[0] != nodata_thick)
            
            # all_touched = True (any pixel touching polygon boundary)
            m_t, _ = rmask(src_m, geom, crop=False, all_touched=True, nodata=-9999)
            t_t, _ = rmask(src_t, geom, crop=False, all_touched=True, nodata=-9999)
            valid_t = (m_t[0] == 1) & (t_t[0] > 0) & (t_t[0] != nodata_thick)
            
        basin_cells_false[b] = np.sum(valid_f)
        basin_cells_true[b] = np.sum(valid_t)
        basin_area_proj[b] = np.sum(valid_f) * 0.25
        basin_area_ground[b] = np.sum(true_cell_area_km2[valid_f])
        
        combined_mask_false |= valid_f
        combined_mask_true |= valid_t
        
        print(f"Basin {b:<6}: all_touched=False -> {np.sum(valid_f):,} cells ({np.sum(valid_f)*0.25:,.2f} km² proj, {np.sum(true_cell_area_km2[valid_f]):,.2f} km² ground)")
        print(f"             all_touched=True  -> {np.sum(valid_t):,} cells ({np.sum(valid_t)*0.25:,.2f} km² proj, {np.sum(true_cell_area_km2[valid_t]):,.2f} km² ground)")
        print(f"             Boundary difference: {np.sum(valid_t) - np.sum(valid_f):,} cells (+{(np.sum(valid_t) - np.sum(valid_f))*0.25:,.2f} km²)")

    # Check basin overlap
    sum_individual = sum(basin_cells_false.values())
    combined_count = np.sum(combined_mask_false)
    print(f"\nSum of individual basins (all_touched=False): {sum_individual:,} cells")
    print(f"Union of 3 basins (all_touched=False):         {combined_count:,} cells")
    print(f"Overlap between basins:                        {sum_individual - combined_count} cells")

    # 4. Investigate Grounded Cells Outside the Three Basins
    outside_mask = total_domain_grounded & (~combined_mask_false)
    outside_count = np.sum(outside_mask)
    outside_proj_area = outside_count * 0.25
    outside_ground_area = np.sum(true_cell_area_km2[outside_mask])
    
    print("\n" + "="*80)
    print("5. CELLS OUTSIDE THE THREE MAINLAND ICE SHEET BASINS")
    print("="*80)
    print(f"Total raster grounded cells:               {np.sum(total_domain_grounded):,}")
    print(f"Inside Peninsula Ice Sheet (Hp-I,I-Ipp,Ipp-J): {combined_count:,} ({combined_count/np.sum(total_domain_grounded)*100:.2f}%)")
    print(f"Outside Peninsula Ice Sheet:               {outside_count:,} ({outside_count/np.sum(total_domain_grounded)*100:.2f}%)")
    print(f"Projected area outside:                    {outside_proj_area:,.2f} km²")
    print(f"Corrected ground area outside:             {outside_ground_area:,.2f} km²")
    
    # Where do these outside cells belong?
    print("\nAttributing outside grounded cells to intersecting geographic regions:")
    for _, feat in intersecting_features.iterrows():
        b_name = feat['Basin']
        r_name = feat['Region']
        t_name = feat['Type']
        
        # Skip the 3 ice sheet basins we already counted
        if r_name == 'Peninsula' and t_name == 'Ice_sheet':
            continue
            
        geom = [feat['geometry']]
        with rasterio.open(masks_path) as src_m, rasterio.open(thick_path) as src_t:
            m_sub, _ = rmask(src_m, geom, crop=False, all_touched=False, nodata=-9999)
            t_sub, _ = rmask(src_t, geom, crop=False, all_touched=False, nodata=-9999)
            valid_sub = (m_sub[0] == 1) & (t_sub[0] > 0) & (t_sub[0] != nodata_thick)
            
        c_sub = np.sum(valid_sub)
        if c_sub > 0:
            print(f"  • Region={r_name:<15} | Basin={b_name:<8} | Type={t_name:<12}: {c_sub:>8,d} cells ({c_sub*0.25:>9,.2f} km² proj)")

if __name__ == "__main__":
    audit_grounded_cells()

