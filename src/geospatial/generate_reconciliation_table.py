"""
Reconciliation Table Generator for Issue 1: Grounded-Cell Area Discrepancy.
Generates an exhaustive reconciliation of all 1,650,227 raster grounded cells.
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

def generate_reconciliation():
    proc_dir = "antarctic-ice-volume-prediction/data/processed"
    raw_dir = "antarctic-ice-volume-prediction/data/raw"
    
    thick_path = os.path.join(proc_dir, "bedmap3_thickness_peninsula_500m.tif")
    masks_path = os.path.join(proc_dir, "bedmap3_masks_peninsula_500m.tif")
    shp_path = os.path.join(raw_dir, "imbie_basins/IMBIE_AIS_Regional_Delineations/IMBIE_AIS_Regional_Delineations.shp")
    
    with rasterio.open(masks_path) as src_m, rasterio.open(thick_path) as src_t:
        mask_arr = src_m.read(1)
        thick_arr = src_t.read(1).astype(np.float64)
        nodata_thick = src_t.nodata
        transform = src_m.transform
        height, width = mask_arr.shape
        
    areal_scale, lats, lons = compute_scale_factor_grid(transform, height, width)
    cell_area_km2 = 0.25 / areal_scale.astype(np.float64)
    
    gdf = gpd.read_file(shp_path)
    
    # 1. Total domain grounded cells
    domain_grounded_mask = (mask_arr == 1) & (thick_arr > 0) & (thick_arr != nodata_thick)
    total_domain_cells = int(np.sum(domain_grounded_mask))
    
    categories = []
    
    # Track assigned cells
    assigned_mask = np.zeros((height, width), dtype=bool)
    
    # 2. Main Peninsula Basins (Ice Sheet)
    pen_basins = gdf[(gdf['Region'] == 'Peninsula') & (gdf['Type'] == 'Ice_sheet')].sort_values('Basin')
    for _, row in pen_basins.iterrows():
        b = row['Basin']
        geom = [row['geometry']]
        with rasterio.open(masks_path) as src_m, rasterio.open(thick_path) as src_t:
            m_b, _ = rmask(src_m, geom, crop=False, all_touched=False, nodata=-9999)
            t_b, _ = rmask(src_t, geom, crop=False, all_touched=False, nodata=-9999)
        valid = (m_b[0] == 1) & (t_b[0] > 0) & (t_b[0] != nodata_thick)
        assigned_mask |= valid
        
        n_cells = int(np.sum(valid))
        p_area = n_cells * 0.25
        g_area = float(np.sum(cell_area_km2[valid]))
        corr_pct = ((g_area - p_area) / p_area) * 100
        mean_lat = float(np.mean(lats[valid]))
        
        categories.append({
            'Category': f'Basin {b} (Ice Sheet)',
            'Region': 'Peninsula Mainland',
            'Cells': n_cells,
            'Pct_Total_%': (n_cells / total_domain_cells) * 100,
            'Mean_Latitude_deg': mean_lat,
            'Projected_Area_km2': p_area,
            'Corrected_Area_km2': g_area,
            'Distortion_Delta_km2': g_area - p_area,
            'Correction_%': corr_pct
        })
        
    # Peninsula mainland subtotal
    pen_main_cells = sum(c['Cells'] for c in categories)
    pen_main_p_area = sum(c['Projected_Area_km2'] for c in categories)
    pen_main_g_area = sum(c['Corrected_Area_km2'] for c in categories)
    
    # 3. Peninsula Islands
    pen_islands = gdf[(gdf['Region'] == 'Peninsula') & (gdf['Type'] == 'Islands')].sort_values('Basin')
    for _, row in pen_islands.iterrows():
        b = row['Basin']
        geom = [row['geometry']]
        with rasterio.open(masks_path) as src_m, rasterio.open(thick_path) as src_t:
            m_b, _ = rmask(src_m, geom, crop=False, all_touched=False, nodata=-9999)
            t_b, _ = rmask(src_t, geom, crop=False, all_touched=False, nodata=-9999)
        valid = (m_b[0] == 1) & (t_b[0] > 0) & (t_b[0] != nodata_thick)
        assigned_mask |= valid
        
        n_cells = int(np.sum(valid))
        p_area = n_cells * 0.25
        g_area = float(np.sum(cell_area_km2[valid]))
        corr_pct = ((g_area - p_area) / p_area) * 100
        mean_lat = float(np.mean(lats[valid]))
        
        label = 'Alexander & Charcot Is.' if b == 'Hp-I' else 'Adelaide, Anvers, James Ross Is.' if b == 'I-Ipp' else 'Robertson & Weddell Is.'
        categories.append({
            'Category': f'Basin {b} Islands ({label})',
            'Region': 'Peninsula Peripheral',
            'Cells': n_cells,
            'Pct_Total_%': (n_cells / total_domain_cells) * 100,
            'Mean_Latitude_deg': mean_lat,
            'Projected_Area_km2': p_area,
            'Corrected_Area_km2': g_area,
            'Distortion_Delta_km2': g_area - p_area,
            'Correction_%': corr_pct
        })

    # 4. West Antarctic Ice Sheet Margin
    west_ice = gdf[(gdf['Region'] == 'West') & (gdf['Type'] == 'Ice_sheet')].sort_values('Basin')
    for _, row in west_ice.iterrows():
        b = row['Basin']
        geom = [row['geometry']]
        with rasterio.open(masks_path) as src_m, rasterio.open(thick_path) as src_t:
            m_b, _ = rmask(src_m, geom, crop=False, all_touched=False, nodata=-9999)
            t_b, _ = rmask(src_t, geom, crop=False, all_touched=False, nodata=-9999)
        valid = (m_b[0] == 1) & (t_b[0] > 0) & (t_b[0] != nodata_thick)
        if np.sum(valid) == 0:
            continue
        assigned_mask |= valid
        
        n_cells = int(np.sum(valid))
        p_area = n_cells * 0.25
        g_area = float(np.sum(cell_area_km2[valid]))
        corr_pct = ((g_area - p_area) / p_area) * 100
        mean_lat = float(np.mean(lats[valid]))
        
        label = 'Pine Island / Bellingshausen' if b == 'H-Hp' else 'Ronne / Foundation Catchment'
        categories.append({
            'Category': f'Basin {b} Ice Sheet ({label})',
            'Region': 'West Antarctica Influx',
            'Cells': n_cells,
            'Pct_Total_%': (n_cells / total_domain_cells) * 100,
            'Mean_Latitude_deg': mean_lat,
            'Projected_Area_km2': p_area,
            'Corrected_Area_km2': g_area,
            'Distortion_Delta_km2': g_area - p_area,
            'Correction_%': corr_pct
        })
        
    # 5. Remaining Unassigned Cells (offshore islets / nunataks outside IMBIE polygons)
    unassigned_mask = domain_grounded_mask & (~assigned_mask)
    n_unassigned = int(np.sum(unassigned_mask))
    p_unassigned = n_unassigned * 0.25
    g_unassigned = float(np.sum(cell_area_km2[unassigned_mask]))
    mean_lat_unassigned = float(np.mean(lats[unassigned_mask]))
    
    categories.append({
        'Category': 'Unassigned Peripheral Islets / Nunataks',
        'Region': 'Offshore Rocks & Islets',
        'Cells': n_unassigned,
        'Pct_Total_%': (n_unassigned / total_domain_cells) * 100,
        'Mean_Latitude_deg': mean_lat_unassigned,
        'Projected_Area_km2': p_unassigned,
        'Corrected_Area_km2': g_unassigned,
        'Distortion_Delta_km2': g_unassigned - p_unassigned,
        'Correction_%': ((g_unassigned - p_unassigned) / p_unassigned) * 100
    })
    
    df = pd.DataFrame(categories)
    
    # Totals row
    tot_cells = df['Cells'].sum()
    tot_p_area = df['Projected_Area_km2'].sum()
    tot_g_area = df['Corrected_Area_km2'].sum()
    
    tot_row = pd.DataFrame([{
        'Category': 'TOTAL RECTANGULAR DOMAIN',
        'Region': 'Entire Raster Domain',
        'Cells': tot_cells,
        'Pct_Total_%': 100.0,
        'Mean_Latitude_deg': float(np.mean(lats[domain_grounded_mask])),
        'Projected_Area_km2': tot_p_area,
        'Corrected_Area_km2': tot_g_area,
        'Distortion_Delta_km2': tot_g_area - tot_p_area,
        'Correction_%': ((tot_g_area - tot_p_area) / tot_p_area) * 100
    }])
    
    full_table = pd.concat([df, tot_row], ignore_index=True)
    
    print("\n" + "="*140)
    print("EXHAUSTIVE RECONCILIATION TABLE: GROUNDED CELLS AND SPATIAL AREAS")
    print("="*140)
    print(full_table.to_string(index=False, float_format=lambda x: f"{x:,.2f}"))
    
    out_csv = os.path.join(proc_dir, "grounded_cells_reconciliation_table.csv")
    full_table.to_csv(out_csv, index=False)
    print(f"\nSaved reconciliation table to {out_csv}")
    
    return full_table

if __name__ == "__main__":
    generate_reconciliation()

