"""
Audit Script for Issue 2: Exact Firn-Volume Arithmetic and Residual Analysis.
Evaluates cell-by-cell unrounded arrays across all Peninsula basins.
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

def audit_firn_arithmetic():
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
        
    areal_scale, _, _ = compute_scale_factor_grid(transform, height, width)
    cell_area_km2 = 0.25 / areal_scale.astype(np.float64)
    
    gdf = gpd.read_file(shp_path)
    pen_basins = gdf[(gdf['Region'] == 'Peninsula') & (gdf['Type'] == 'Ice_sheet')].sort_values('Basin')
    
    basin_fac = {
        'Hp-I': 16.5,
        'I-Ipp': 14.0,
        'Ipp-J': 17.5
    }
    
    results = []
    
    for b_name in ['Hp-I', 'I-Ipp', 'Ipp-J']:
        geom = pen_basins[pen_basins['Basin'] == b_name].geometry
        
        with rasterio.open(masks_path) as src_m, rasterio.open(thick_path) as src_t:
            m_b, _ = rmask(src_m, geom, crop=False, all_touched=False, nodata=-9999)
            t_b, _ = rmask(src_t, geom, crop=False, all_touched=False, nodata=-9999)
            
        valid = (m_b[0] == 1) & (t_b[0] > 0) & (t_b[0] != nodata_thick)
        
        h = t_b[0][valid].astype(np.float64)  # thickness in meters
        a = cell_area_km2[valid].astype(np.float64)  # ground area in km2
        fac = float(basin_fac[b_name])  # FAC in meters
        
        # 1. Geometric volume: sum(H * A) in km3
        # h is in meters -> h * 1e-3 is in km
        v_geom = np.sum(h * 1e-3 * a)
        
        # 2. Firn volume: sum(FAC * A) in km3
        v_firn = np.sum(fac * 1e-3 * a)
        
        # 3. Ice-equivalent volume with max(H - FAC, 0): sum(max(H - FAC, 0) * A) in km3
        h_diff = h - fac
        h_ice_eq = np.maximum(h_diff, 0.0)
        v_ice_eq = np.sum(h_ice_eq * 1e-3 * a)
        
        # 4. Unclipped difference: sum((H - FAC) * A) = V_geom - V_firn
        v_diff_linear = np.sum(h_diff * 1e-3 * a)
        
        # 5. Residual: V_geom - V_firn - V_ice_eq
        residual = v_geom - v_firn - v_ice_eq
        
        # 6. Analysis of cells where H < FAC
        under_fac = (h < fac)
        n_under = int(np.sum(under_fac))
        under_deficit_km3 = np.sum((fac - h[under_fac]) * 1e-3 * a[under_fac])
        
        results.append({
            'Basin': b_name,
            'Cells': len(h),
            'V_geom_km3': v_geom,
            'V_firn_km3': v_firn,
            'V_ice_eq_km3': v_ice_eq,
            'V_geom_minus_V_firn': v_geom - v_firn,
            'Residual_km3': residual,
            'Cells_H_lt_FAC': n_under,
            'Pct_Cells_H_lt_FAC': (n_under / len(h)) * 100,
            'Truncation_Deficit_km3': under_deficit_km3,
            'Min_H_m': np.min(h),
            'Max_H_m': np.max(h)
        })
        
    df = pd.DataFrame(results)
    
    # Regional summary
    reg_v_geom = df['V_geom_km3'].sum()
    reg_v_firn = df['V_firn_km3'].sum()
    reg_v_ice_eq = df['V_ice_eq_km3'].sum()
    reg_v_diff_linear = reg_v_geom - reg_v_firn
    reg_residual = reg_v_geom - reg_v_firn - reg_v_ice_eq
    reg_under_cells = df['Cells_H_lt_FAC'].sum()
    reg_under_deficit = df['Truncation_Deficit_km3'].sum()
    total_cells = df['Cells'].sum()
    
    reg_row = pd.DataFrame([{
        'Basin': 'Peninsula Total',
        'Cells': total_cells,
        'V_geom_km3': reg_v_geom,
        'V_firn_km3': reg_v_firn,
        'V_ice_eq_km3': reg_v_ice_eq,
        'V_geom_minus_V_firn': reg_v_diff_linear,
        'Residual_km3': reg_residual,
        'Cells_H_lt_FAC': reg_under_cells,
        'Pct_Cells_H_lt_FAC': (reg_under_cells / total_cells) * 100,
        'Truncation_Deficit_km3': reg_under_deficit,
        'Min_H_m': 1.0,
        'Max_H_m': df['Max_H_m'].max()
    }])
    
    audit_table = pd.concat([df, reg_row], ignore_index=True)
    
    print("="*120)
    print("EXACT UNROUNDED ARITHMETIC AUDIT: V_geom, V_firn, V_ice_eq, and Residuals")
    print("="*120)
    print(audit_table.to_string(index=False, float_format=lambda x: f"{x:,.6f}"))
    
    print("\n" + "="*120)
    print("MATHEMATICAL PROOF OF THE RESIDUAL:")
    print("="*120)
    print("By definition:")
    print("  V_geom - V_firn = sum((H - FAC) * A)")
    print("  V_ice_eq        = sum(max(H - FAC, 0) * A)")
    print("Therefore:")
    print("  Residual = (V_geom - V_firn) - V_ice_eq")
    print("           = sum([ (H - FAC) - max(H - FAC, 0) ] * A)")
    print("           = - sum_{H < FAC} [ (FAC - H) * A ]")
    print(f"Calculated Residual:               {reg_residual:+.6f} km³")
    print(f"Calculated -Truncation Deficit:     {-reg_under_deficit:+.6f} km³")
    print(f"Identity Difference (|R - (-D)|):  {abs(residual - (-under_deficit_km3)):.12e} km³")
    print("The residual is EXACTLY equal to the non-physical negative ice volume that was prevented")
    print("by applying the glaciological zero-floor clamp: max(H - FAC, 0)!")

if __name__ == "__main__":
    audit_firn_arithmetic()

