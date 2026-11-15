"""
Calculation of Geometric and Ice-Equivalent Grounded Ice Volume across the Antarctic Peninsula.
Incorporates:
1. Strict Bedmap3 mask taxonomy (Mask 1 = Permanently grounded ice sheet, Mask 2 = Transiently grounded ice shelf).
2. Geodesic area distortion correction (EPSG:3031 scale factor m_A).
3. Physical firn-air content (FAC) correction for solid-ice equivalent volume.
"""

import os
import rasterio
import geopandas as gpd
import numpy as np
import pandas as pd
from rasterio.mask import mask as rmask
from audit_distortion import compute_scale_factor_grid

def calculate_volumes():
    proc_dir = "antarctic-ice-volume-prediction/data/processed"
    shp_path = "antarctic-ice-volume-prediction/data/raw/imbie_basins/IMBIE_AIS_Regional_Delineations/IMBIE_AIS_Regional_Delineations.shp"
    
    thick_path = os.path.join(proc_dir, "bedmap3_thickness_peninsula_500m.tif")
    masks_path = os.path.join(proc_dir, "bedmap3_masks_peninsula_500m.tif")
    uncert_path = os.path.join(proc_dir, "bedmap3_uncertainty_peninsula_500m.tif")
    
    # Load rasters
    with rasterio.open(thick_path) as src_t, rasterio.open(masks_path) as src_m, rasterio.open(uncert_path) as src_u:
        thick = src_t.read(1)
        masks = src_m.read(1)
        uncert = src_u.read(1)
        transform = src_t.transform
        meta = src_t.meta.copy()
        
    height, width = thick.shape
    areal_scale, lat_grid, lon_grid = compute_scale_factor_grid(transform, height, width)
    cell_area_km2_corrected = 0.25 / areal_scale
    
    # Load IMBIE shapefile
    gdf = gpd.read_file(shp_path)
    pen_basins = gdf[(gdf['Region'] == 'Peninsula') & (gdf['Type'] == 'Ice_sheet')].sort_values('Basin')
    
    # Literature-based firn air content (FAC) from RACMO2.3p2 / IMAU-FDM (van Wessem et al., 2018; Ligtenberg et al., 2011)
    # Peninsula-wide mean FAC is ~16.5 m (+/- 2.5 m).
    # Graham Land (I-Ipp) has lower elevation/higher melt -> ~14.0 m
    # Palmer Land West (Hp-I) high accumulation -> ~16.5 m
    # Palmer Land East (Ipp-J) cold plateau interior -> ~17.5 m
    basin_fac_mean = {
        'Hp-I': 16.5,
        'I-Ipp': 14.0,
        'Ipp-J': 17.5
    }
    
    results = []
    
    for _, row in pen_basins.iterrows():
        b_name = row['Basin']
        b_geom = [row['geometry']]
        
        # Mask raster with basin polygon
        with rasterio.open(thick_path) as src:
            t_masked, _ = rmask(src, b_geom, crop=False, nodata=-9999)
            t_arr = t_masked[0]
            
        with rasterio.open(masks_path) as src:
            m_masked, _ = rmask(src, b_geom, crop=False, nodata=-9999)
            m_arr = m_masked[0]
            
        with rasterio.open(uncert_path) as src:
            u_masked, _ = rmask(src, b_geom, crop=False, nodata=-9999)
            u_arr = u_masked[0]
            
        # Grounded ice condition: mask == 1, thickness > 0
        g_mask = (m_arr == 1) & (t_arr > 0) & (t_arr != -9999)
        
        # Projected quantities
        proj_area_km2 = np.sum(g_mask) * 0.25
        proj_vol_geom_km3 = np.sum(t_arr[g_mask] * 1e-3 * 0.25)
        
        # True Ground Corrected quantities
        corr_cell_area = cell_area_km2_corrected[g_mask]
        corr_area_km2 = np.sum(corr_cell_area)
        corr_vol_geom_km3 = np.sum(t_arr[g_mask] * 1e-3 * corr_cell_area)
        
        mean_thick_geom = np.sum(t_arr[g_mask] * corr_cell_area) / corr_area_km2
        mean_uncert = np.sum(u_arr[g_mask] * corr_cell_area) / corr_area_km2
        
        # Firn air correction
        fac_m = basin_fac_mean[b_name]
        # Firn air volume
        v_firn_km3 = np.sum((fac_m * 1e-3) * corr_cell_area)
        
        # Ice-equivalent volume: V_ice_eq = sum((H_geom - FAC) * A_ground)
        # Note: (H_geom - FAC) in km:
        h_ice_eq = np.maximum(t_arr[g_mask] - fac_m, 0.0)
        corr_vol_ice_eq_km3 = np.sum(h_ice_eq * 1e-3 * corr_cell_area)
        
        # Also compute with Peninsula uniform FAC = 16.5 m for sensitivity
        corr_vol_ice_eq_uniform165 = np.sum(np.maximum(t_arr[g_mask] - 16.5, 0.0) * 1e-3 * corr_cell_area)
        
        results.append({
            'Basin': b_name,
            'Pixels': int(np.sum(g_mask)),
            'Proj_Area_km2': proj_area_km2,
            'Corr_Area_km2': corr_area_km2,
            'Area_Distortion_%': (proj_area_km2 - corr_area_km2) / corr_area_km2 * 100,
            'Mean_H_geom_m': mean_thick_geom,
            'Mean_Uncert_m': mean_uncert,
            'Proj_Vol_Geom_km3': proj_vol_geom_km3,
            'Corr_Vol_Geom_km3': corr_vol_geom_km3,
            'FAC_Mean_m': fac_m,
            'Firn_Air_Vol_km3': v_firn_km3,
            'Corr_Vol_Ice_Eq_km3': corr_vol_ice_eq_km3,
            'Vol_Ice_Eq_Uniform165_km3': corr_vol_ice_eq_uniform165,
            'Firn_Volume_Reduction_%': (corr_vol_geom_km3 - corr_vol_ice_eq_km3) / corr_vol_geom_km3 * 100
        })
        
    df = pd.DataFrame(results)
    
    # Regional summary row
    reg_pixels = df['Pixels'].sum()
    reg_proj_area = df['Proj_Area_km2'].sum()
    reg_corr_area = df['Corr_Area_km2'].sum()
    reg_proj_geom_vol = df['Proj_Vol_Geom_km3'].sum()
    reg_corr_geom_vol = df['Corr_Vol_Geom_km3'].sum()
    reg_firn_vol = df['Firn_Air_Vol_km3'].sum()
    reg_corr_ice_eq_vol = df['Corr_Vol_Ice_Eq_km3'].sum()
    reg_uniform165_vol = df['Vol_Ice_Eq_Uniform165_km3'].sum()
    
    reg_row = pd.DataFrame([{
        'Basin': 'Peninsula Total',
        'Pixels': reg_pixels,
        'Proj_Area_km2': reg_proj_area,
        'Corr_Area_km2': reg_corr_area,
        'Area_Distortion_%': (reg_proj_area - reg_corr_area) / reg_corr_area * 100,
        'Mean_H_geom_m': reg_corr_geom_vol / reg_corr_area * 1e3,
        'Mean_Uncert_m': (df['Mean_Uncert_m'] * df['Corr_Area_km2']).sum() / reg_corr_area,
        'Proj_Vol_Geom_km3': reg_proj_geom_vol,
        'Corr_Vol_Geom_km3': reg_corr_geom_vol,
        'FAC_Mean_m': reg_firn_vol / reg_corr_area * 1e3,
        'Firn_Air_Vol_km3': reg_firn_vol,
        'Corr_Vol_Ice_Eq_km3': reg_corr_ice_eq_vol,
        'Vol_Ice_Eq_Uniform165_km3': reg_uniform165_vol,
        'Firn_Volume_Reduction_%': (reg_corr_geom_vol - reg_corr_ice_eq_vol) / reg_corr_geom_vol * 100
    }])
    
    summary_df = pd.concat([df, reg_row], ignore_index=True)
    
    print("\n" + "="*120)
    print("ANTARCTIC PENINSULA BASELINE VOLUME SUMMARY (BEDMAP3)")
    print("="*120)
    
    display_cols = [
        'Basin', 'Corr_Area_km2', 'Mean_H_geom_m', 
        'Corr_Vol_Geom_km3', 'FAC_Mean_m', 'Firn_Air_Vol_km3', 
        'Corr_Vol_Ice_Eq_km3', 'Firn_Volume_Reduction_%'
    ]
    print(summary_df[display_cols].to_string(index=False, float_format=lambda x: f"{x:,.1f}"))
    
    # Save CSV
    out_csv = os.path.join(proc_dir, "bedmap3_basin_volumes_geometric_and_ice_equivalent.csv")
    summary_df.to_csv(out_csv, index=False)
    print(f"\nSaved summary to: {out_csv}")
    
    return summary_df

if __name__ == "__main__":
    calculate_volumes()

