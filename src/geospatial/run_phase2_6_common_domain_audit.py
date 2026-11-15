"""
Phase 2.6: Common-Domain Cross-Product Audit and Baseline Reconciliation
=======================================================================
This script performs an independent, rigorous common-domain comparison between
Bedmap3 and MEaSUREs BedMachine Antarctica V4.1 across the three Antarctic Peninsula
mainland basins (Hp-I, I-Ipp, Ipp-J).

Objectives:
1. Establish three spatial domains:
   - A: Common grounded domain (Bedmap3 grounded & BedMachine grounded)
   - B: Bedmap3-only domain (Bedmap3 grounded & BedMachine NOT grounded)
   - C: BedMachine-only domain (BedMachine grounded & Bedmap3 NOT grounded)
   Verify strict subset relationship and compute overlap metrics (fraction of BM3,
   fraction of BM, Jaccard IoU, Sørensen-Dice).
2. Calculate comparable volumes on the common domain:
   - Bedmap3 geometric volume
   - Bedmap3 ice-equivalent volume (with 2D BedMachine FAC)
   - BedMachine ice-equivalent volume
   - BedMachine geometric volume (thickness + firn)
   - Full statistics (mean, median, std, percentiles, difference stats).
3. Decompose total volume difference:
   - Mask domain difference
   - Common-domain thickness difference
   - Firn treatment difference
   - Zero-floor truncation deficit
4. Investigate the Bedmap3-only cells:
   - What BedMachine classifies them as (ocean, rock, shelf)
   - Thickness and surface elevation statistics
   - Volume contribution
5. Verify FAC arithmetic, coverage, and covariance with cell area.
6. Reconcile baselines and output CSV tables and high-resolution diagnostic maps.
"""

import os
import sys
import numpy as np
import pandas as pd
import xarray as xr
import rasterio
from rasterio.mask import mask as rmask
import geopandas as gpd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

# File paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW_BM3_DIR = os.path.join(BASE_DIR, "data", "raw", "bedmap3")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
BM3_THICK = os.path.join(PROCESSED_DIR, "bedmap3_thickness_peninsula_500m.tif")
BM3_MASK = os.path.join(PROCESSED_DIR, "bedmap3_masks_peninsula_500m.tif")
BM3_SURF = os.path.join(PROCESSED_DIR, "bedmap3_surface_peninsula_500m.tif")
BM3_BED = os.path.join(PROCESSED_DIR, "bedmap3_bed_peninsula_500m.tif")
BM3_UNCERT = os.path.join(PROCESSED_DIR, "bedmap3_uncertainty_peninsula_500m.tif")
IMBIE_SHP = os.path.join(BASE_DIR, "data", "raw", "imbie_basins", "IMBIE_AIS_Regional_Delineations", "IMBIE_AIS_Regional_Delineations.shp")
ALIGNED_NC = os.path.join(PROCESSED_DIR, "bedmachine_v4.1_peninsula_aligned_to_bedmap3.nc")

REPORTS_DIR = os.path.join(BASE_DIR, "reports")
TABLES_DIR = os.path.join(REPORTS_DIR, "tables")
FIGURES_DIR = os.path.join(REPORTS_DIR, "figures")
os.makedirs(TABLES_DIR, exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)

# Ensure local imports work
sys.path.append(os.path.abspath('antarctic-ice-volume-prediction'))
from src.geospatial.audit_distortion import compute_scale_factor_grid

# Configure matplotlib cache directory
os.environ['MPLCONFIGDIR'] = os.path.join(BASE_DIR, 'data', 'processed', '.matplotlib')

def main():
    print("=" * 80)
    print("PHASE 2.6: COMMON-DOMAIN CROSS-PRODUCT AUDIT & BASELINE RECONCILIATION")
    print("=" * 80)
    
    # 1. Load Bedmap3 Rasters
    print("\n[Step 1] Loading Bedmap3 and BedMachine datasets...")
    with rasterio.open(BM3_THICK) as src_t, rasterio.open(BM3_MASK) as src_m:
        bm3_thick = src_t.read(1).astype(np.float64)
        bm3_mask = src_m.read(1)
        transform = src_t.transform
        height, width = bm3_thick.shape
        crs = src_t.crs
        
    with rasterio.open(BM3_SURF) as src_s, rasterio.open(BM3_BED) as src_b:
        bm3_surface = src_s.read(1).astype(np.float64)
        bm3_bed = src_b.read(1).astype(np.float64)
        
    # 2. Load Aligned BedMachine NetCDF
    ds_bm = xr.open_dataset(ALIGNED_NC)
    bm_thick_ice_eq = ds_bm['thickness'].values.astype(np.float64)
    bm_mask = ds_bm['mask'].values.astype(np.int32)
    bm_firn = ds_bm['firn'].values.astype(np.float64)
    bm_errbed = ds_bm['errbed'].values.astype(np.float64)
    bm_surface = ds_bm['surface'].values.astype(np.float64)
    bm_bed = ds_bm['bed'].values.astype(np.float64)
    bm_source = ds_bm['source'].values.astype(np.int32)
    
    # BedMachine geometric column thickness: H_geom = thickness + firn
    bm_thick_geom = bm_thick_ice_eq + bm_firn
    
    # 3. True cell area grid on WGS84
    areal_scale, lats, lons = compute_scale_factor_grid(transform, height, width)
    true_cell_area_km2 = 0.25 / areal_scale.astype(np.float64)
    
    # 4. Load IMBIE shapefile
    gdf = gpd.read_file(IMBIE_SHP)
    pen_basins = gdf[(gdf['Region'] == 'Peninsula') & (gdf['Type'] == 'Ice_sheet')].sort_values('Basin')
    
    # -------------------------------------------------------------------------
    # PART 1: ESTABLISH THREE SPATIAL DOMAINS & VERIFY STRICT SUBSET RELATIONSHIP
    # -------------------------------------------------------------------------
    print("\n[Part 1] Establishing Spatial Domains & Auditing Overlap Metrics...")
    
    # Compute basin membership masks
    basin_masks = {}
    for _, row in pen_basins.iterrows():
        b_name = row['Basin']
        b_geom = [row['geometry']]
        with rasterio.open(BM3_MASK) as src:
            m3_masked, _ = rmask(src, b_geom, crop=False, all_touched=False, nodata=-9999)
            basin_masks[b_name] = (m3_masked[0] == 1)
            
    # Combine mainland basins
    in_mainland = np.zeros((height, width), dtype=bool)
    for b_mask in basin_masks.values():
        in_mainland |= b_mask
        
    # Grounded masks
    # Bedmap3 grounded: mask == 1 and thickness > 0 and not nodata
    bm3_grounded_full = (bm3_mask == 1) & (bm3_thick > 0) & (bm3_thick != -9999)
    # BedMachine grounded: mask == 2 and thickness > 0 and not nodata
    bm_grounded_full = (bm_mask == 2) & (bm_thick_ice_eq > 0) & (bm_thick_ice_eq != -9999)
    
    # Audit across mainland basins
    mask_recon_rows = []
    basin_domain_masks = {}
    
    basins_to_eval = list(pen_basins['Basin']) + ['Peninsula Total']
    
    for b_name in basins_to_eval:
        if b_name == 'Peninsula Total':
            in_b = in_mainland
        else:
            in_b = basin_masks[b_name]
            
        g_bm3 = in_b & bm3_grounded_full
        g_bm = in_b & bm_grounded_full
        
        # Domain A: Common Grounded
        dom_a = g_bm3 & g_bm
        # Domain B: Bedmap3 Only
        dom_b = g_bm3 & (~g_bm)
        # Domain C: BedMachine Only
        dom_c = g_bm & (~g_bm3)
        
        basin_domain_masks[b_name] = {'A': dom_a, 'B': dom_b, 'C': dom_c, 'BM3': g_bm3, 'BM': g_bm}
        
        n_bm3 = np.sum(g_bm3)
        n_bm = np.sum(g_bm)
        n_a = np.sum(dom_a)
        n_b = np.sum(dom_b)
        n_c = np.sum(dom_c)
        
        area_bm3 = np.sum(true_cell_area_km2[g_bm3])
        area_bm = np.sum(true_cell_area_km2[g_bm])
        area_a = np.sum(true_cell_area_km2[dom_a])
        area_b = np.sum(true_cell_area_km2[dom_b])
        area_c = np.sum(true_cell_area_km2[dom_c])
        
        pct_bm3_covered = (n_a / n_bm3 * 100.0) if n_bm3 > 0 else 0.0
        pct_bm_covered = (n_a / n_bm * 100.0) if n_bm > 0 else 0.0
        jaccard_iou = (n_a / (n_bm3 + n_bm - n_a) * 100.0) if (n_bm3 + n_bm - n_a) > 0 else 0.0
        sorensen_dice = (2.0 * n_a / (n_bm3 + n_bm) * 100.0) if (n_bm3 + n_bm) > 0 else 0.0
        
        mask_recon_rows.append({
            'Basin': b_name,
            'BM3_Grounded_Cells': n_bm3,
            'BM3_Grounded_Area_km2': area_bm3,
            'BM_Grounded_Cells': n_bm,
            'BM_Grounded_Area_km2': area_bm,
            'Common_Cells_DomA': n_a,
            'Common_Area_km2_DomA': area_a,
            'BM3_Only_Cells_DomB': n_b,
            'BM3_Only_Area_km2_DomB': area_b,
            'BM_Only_Cells_DomC': n_c,
            'BM_Only_Area_km2_DomC': area_c,
            'Overlap_Pct_of_BM3': pct_bm3_covered,
            'Overlap_Pct_of_BM': pct_bm_covered,
            'Jaccard_IoU_Pct': jaccard_iou,
            'Sorensen_Dice_Pct': sorensen_dice,
            'Is_Strict_Subset': (n_c == 0)
        })
        
    df_mask_recon = pd.DataFrame(mask_recon_rows)
    mask_recon_csv = os.path.join(TABLES_DIR, "mask_reconciliation.csv")
    df_mask_recon.to_csv(mask_recon_csv, index=False)
    print(f"Saved: {mask_recon_csv}")
    print(df_mask_recon[['Basin', 'Common_Cells_DomA', 'BM3_Only_Cells_DomB', 'BM_Only_Cells_DomC', 'Overlap_Pct_of_BM3', 'Overlap_Pct_of_BM', 'Jaccard_IoU_Pct', 'Is_Strict_Subset']].to_string(index=False))

    # -------------------------------------------------------------------------
    # PART 2: COMMON DOMAIN COMPARABLE VOLUMES & DETAILED THICKNESS STATISTICS
    # -------------------------------------------------------------------------
    print("\n[Part 2] Calculating Comparable Volumes on Common Grounded Domain (Domain A)...")
    
    common_vol_rows = []
    
    # Calculate ice-equivalent Bedmap3 thickness on common domain
    # H_BM3_ice_eq = max(H_BM3_geom - FAC, 0)
    for b_name in basins_to_eval:
        dom_a = basin_domain_masks[b_name]['A']
        area_a = true_cell_area_km2[dom_a]
        
        # Bedmap3 thicknesses on Domain A
        t_bm3_geom = bm3_thick[dom_a]
        fac_a = bm_firn[dom_a]
        t_bm3_ice_eq = np.maximum(t_bm3_geom - fac_a, 0.0)
        
        # BedMachine thicknesses on Domain A
        t_bm_ice_eq = bm_thick_ice_eq[dom_a]
        t_bm_geom = bm_thick_geom[dom_a]
        
        # Volumes on Domain A (km^3)
        v_bm3_geom_a = np.sum(t_bm3_geom * area_a) / 1000.0
        v_bm3_ice_eq_a = np.sum(t_bm3_ice_eq * area_a) / 1000.0
        v_bm_ice_eq_a = np.sum(t_bm_ice_eq * area_a) / 1000.0
        v_bm_geom_a = np.sum(t_bm_geom * area_a) / 1000.0
        
        diff_ice_eq_a = v_bm_ice_eq_a - v_bm3_ice_eq_a
        diff_ice_eq_pct_a = (diff_ice_eq_a / v_bm3_ice_eq_a * 100.0) if v_bm3_ice_eq_a > 0 else 0.0
        
        diff_geom_a = v_bm_geom_a - v_bm3_geom_a
        diff_geom_pct_a = (diff_geom_a / v_bm3_geom_a * 100.0) if v_bm3_geom_a > 0 else 0.0
        
        # Cell-by-cell difference: delta_H = BM_ice_eq - BM3_ice_eq
        delta_h_ice_eq = t_bm_ice_eq - t_bm3_ice_eq
        delta_h_geom = t_bm_geom - t_bm3_geom
        
        common_vol_rows.append({
            'Basin': b_name,
            'Common_Cells': np.sum(dom_a),
            'Common_Area_km2': np.sum(area_a),
            'BM3_Geom_Vol_km3': v_bm3_geom_a,
            'BM3_Ice_Eq_Vol_km3': v_bm3_ice_eq_a,
            'BM_Ice_Eq_Vol_km3': v_bm_ice_eq_a,
            'BM_Geom_Vol_km3': v_bm_geom_a,
            'Ice_Eq_Volume_Diff_km3': diff_ice_eq_a,
            'Ice_Eq_Volume_Diff_%': diff_ice_eq_pct_a,
            'Geom_Volume_Diff_km3': diff_geom_a,
            'Geom_Volume_Diff_%': diff_geom_pct_a,
            # Bedmap3 Ice-Eq Thickness Stats
            'BM3_Ice_Eq_Mean_m': np.mean(t_bm3_ice_eq),
            'BM3_Ice_Eq_Median_m': np.median(t_bm3_ice_eq),
            'BM3_Ice_Eq_Std_m': np.std(t_bm3_ice_eq),
            'BM3_Ice_Eq_P5_m': np.percentile(t_bm3_ice_eq, 5),
            'BM3_Ice_Eq_P25_m': np.percentile(t_bm3_ice_eq, 25),
            'BM3_Ice_Eq_P75_m': np.percentile(t_bm3_ice_eq, 75),
            'BM3_Ice_Eq_P95_m': np.percentile(t_bm3_ice_eq, 95),
            # BedMachine Ice-Eq Thickness Stats
            'BM_Ice_Eq_Mean_m': np.mean(t_bm_ice_eq),
            'BM_Ice_Eq_Median_m': np.median(t_bm_ice_eq),
            'BM_Ice_Eq_Std_m': np.std(t_bm_ice_eq),
            'BM_Ice_Eq_P5_m': np.percentile(t_bm_ice_eq, 5),
            'BM_Ice_Eq_P25_m': np.percentile(t_bm_ice_eq, 25),
            'BM_Ice_Eq_P75_m': np.percentile(t_bm_ice_eq, 75),
            'BM_Ice_Eq_P95_m': np.percentile(t_bm_ice_eq, 95),
            # Delta H Ice-Eq Stats (BM - BM3)
            'Delta_H_Mean_m': np.mean(delta_h_ice_eq),
            'Delta_H_Median_m': np.median(delta_h_ice_eq),
            'Delta_H_Std_m': np.std(delta_h_ice_eq),
            'Delta_H_Min_m': np.min(delta_h_ice_eq),
            'Delta_H_Max_m': np.max(delta_h_ice_eq),
            'Delta_H_MAE_m': np.mean(np.abs(delta_h_ice_eq)),
            'Delta_H_RMSE_m': np.sqrt(np.mean(delta_h_ice_eq**2)),
            'Delta_H_P5_m': np.percentile(delta_h_ice_eq, 5),
            'Delta_H_P25_m': np.percentile(delta_h_ice_eq, 25),
            'Delta_H_P75_m': np.percentile(delta_h_ice_eq, 75),
            'Delta_H_P95_m': np.percentile(delta_h_ice_eq, 95)
        })
        
    df_common_vol = pd.DataFrame(common_vol_rows)
    common_vol_csv = os.path.join(TABLES_DIR, "common_domain_comparison.csv")
    df_common_vol.to_csv(common_vol_csv, index=False)
    print(f"Saved: {common_vol_csv}")
    print(df_common_vol[['Basin', 'Common_Area_km2', 'BM3_Ice_Eq_Vol_km3', 'BM_Ice_Eq_Vol_km3', 'Ice_Eq_Volume_Diff_km3', 'Ice_Eq_Volume_Diff_%', 'Delta_H_Mean_m', 'Delta_H_Median_m', 'Delta_H_RMSE_m']].to_string(index=False))

    # -------------------------------------------------------------------------
    # PART 3: DECOMPOSE TOTAL VOLUME DIFFERENCE
    # -------------------------------------------------------------------------
    print("\n[Part 3] Decomposing Total Reported Volume Difference...")
    # Full domain volumes from Phase 2.5
    # Total Difference = V_BM_ice_eq^full - V_BM3_ice_eq^full
    # Partitioned into:
    # 1. Delta V_thickness^common = V_BM_ice_eq^common - V_BM3_ice_eq^common
    # 2. Delta V_mask_domain = V_BM_ice_eq^(BM_only) - V_BM3_ice_eq^(BM3_only)
    #    Since BM_only = empty, Delta V_mask_domain = - V_BM3_ice_eq^(BM3_only)
    # Note: sum is EXACT: Delta V_thickness^common + Delta V_mask_domain = Total Difference!
    
    decomp_rows = []
    for b_name in basins_to_eval:
        dom_a = basin_domain_masks[b_name]['A']
        dom_b = basin_domain_masks[b_name]['B']
        dom_c = basin_domain_masks[b_name]['C']
        g_bm3 = basin_domain_masks[b_name]['BM3']
        g_bm = basin_domain_masks[b_name]['BM']
        
        # Areas
        a_bm3 = true_cell_area_km2[g_bm3]
        a_bm = true_cell_area_km2[g_bm]
        a_dom_b = true_cell_area_km2[dom_b]
        a_dom_c = true_cell_area_km2[dom_c]
        
        # Full domain ice-equivalent volumes
        v_bm3_full_ice_eq = np.sum(np.maximum(bm3_thick[g_bm3] - bm_firn[g_bm3], 0.0) * a_bm3) / 1000.0
        v_bm_full_ice_eq = np.sum(bm_thick_ice_eq[g_bm] * a_bm) / 1000.0
        total_ice_eq_diff = v_bm_full_ice_eq - v_bm3_full_ice_eq
        
        # Common domain ice-equivalent volumes
        v_bm3_comm_ice_eq = np.sum(np.maximum(bm3_thick[dom_a] - bm_firn[dom_a], 0.0) * true_cell_area_km2[dom_a]) / 1000.0
        v_bm_comm_ice_eq = np.sum(bm_thick_ice_eq[dom_a] * true_cell_area_km2[dom_a]) / 1000.0
        diff_thickness_common = v_bm_comm_ice_eq - v_bm3_comm_ice_eq
        
        # Bedmap3-only ice-equivalent volume (Domain B)
        v_bm3_only_ice_eq = np.sum(np.maximum(bm3_thick[dom_b] - bm_firn[dom_b], 0.0) * a_dom_b) / 1000.0
        # BedMachine-only ice-equivalent volume (Domain C)
        v_bm_only_ice_eq = (np.sum(bm_thick_ice_eq[dom_c] * a_dom_c) / 1000.0) if np.sum(dom_c) > 0 else 0.0
        
        # Net mask effect: V_BM^(C) - V_BM3^(B)
        net_mask_effect = v_bm_only_ice_eq - v_bm3_only_ice_eq
        
        # Verify identity: diff_thickness_common + net_mask_effect == total_ice_eq_diff
        reconstructed_total_diff = diff_thickness_common + net_mask_effect
        discrepancy = np.abs(total_ice_eq_diff - reconstructed_total_diff)
        
        # Geometric comparison and firn treatment decomposition
        v_bm3_full_geom = np.sum(bm3_thick[g_bm3] * a_bm3) / 1000.0
        v_bm_full_geom = np.sum(bm_thick_geom[g_bm] * a_bm) / 1000.0
        total_geom_diff = v_bm_full_geom - v_bm3_full_geom
        
        v_firn_bm3 = np.sum(bm_firn[g_bm3] * a_bm3) / 1000.0
        v_firn_bm = np.sum(bm_firn[g_bm] * a_bm) / 1000.0
        firn_treatment_diff = v_firn_bm - v_firn_bm3
        
        # Zero-floor truncation deficit on BM3 full
        trunc_mask_bm3 = g_bm3 & (bm3_thick < bm_firn)
        trunc_deficit_bm3 = np.sum((bm_firn[trunc_mask_bm3] - bm3_thick[trunc_mask_bm3]) * true_cell_area_km2[trunc_mask_bm3]) / 1000.0
        
        decomp_rows.append({
            'Basin': b_name,
            'Total_Ice_Eq_Diff_km3': total_ice_eq_diff,
            'Common_Domain_Thickness_Diff_km3': diff_thickness_common,
            'Net_Mask_Domain_Effect_km3': net_mask_effect,
            'BM3_Only_Volume_Lost_km3': v_bm3_only_ice_eq,
            'BM_Only_Volume_Gained_km3': v_bm_only_ice_eq,
            'Reconstructed_Total_Diff_km3': reconstructed_total_diff,
            'Decomposition_Discrepancy_km3': discrepancy,
            'Total_Geom_Diff_km3': total_geom_diff,
            'Firn_Volume_Diff_km3': firn_treatment_diff,
            'Truncation_Deficit_km3': trunc_deficit_bm3
        })
        
    df_decomp = pd.DataFrame(decomp_rows)
    decomp_csv = os.path.join(TABLES_DIR, "volume_difference_decomposition.csv")
    df_decomp.to_csv(decomp_csv, index=False)
    print(f"Saved: {decomp_csv}")
    print(df_decomp[['Basin', 'Total_Ice_Eq_Diff_km3', 'Common_Domain_Thickness_Diff_km3', 'Net_Mask_Domain_Effect_km3', 'BM3_Only_Volume_Lost_km3', 'Decomposition_Discrepancy_km3']].to_string(index=False))

    # -------------------------------------------------------------------------
    # PART 4: DETAILED INVESTIGATION OF THE 22,235 BEDMAP3-ONLY CELLS (DOMAIN B)
    # -------------------------------------------------------------------------
    print("\n[Part 4] Investigating the Bedmap3-Only Cells (Domain B)...")
    dom_b_pen = basin_domain_masks['Peninsula Total']['B']
    n_dom_b = np.sum(dom_b_pen)
    area_dom_b = np.sum(true_cell_area_km2[dom_b_pen])
    
    print(f"Total Bedmap3-Only Cells: {n_dom_b:,} ({area_dom_b:,.2f} km^2)")
    
    # What does BedMachine classify these cells as?
    bm_mask_at_b = bm_mask[dom_b_pen]
    bm_mask_classes = {
        0: 'Ocean (open water / coastal fjord)',
        1: 'Ice-Free Land (exposed rock / nunatak)',
        2: 'Grounded Ice (excluded due to H<=0 or NoData)',
        3: 'Floating Ice Shelf',
        4: 'Lake Vostok / Subglacial Water'
    }
    
    bm_classes_in_b = pd.Series(bm_mask_at_b).value_counts().sort_index()
    print("\nBedMachine Classification of Bedmap3-Only Cells:")
    b_class_rows = []
    for cls_val, cnt in bm_classes_in_b.items():
        cls_name = bm_mask_classes.get(cls_val, f"Unknown ({cls_val})")
        cls_mask = dom_b_pen & (bm_mask == cls_val)
        cls_area = np.sum(true_cell_area_km2[cls_mask])
        cls_pct = cnt / n_dom_b * 100.0
        
        # Bedmap3 thickness in these cells
        bm3_t_cls = bm3_thick[cls_mask]
        bm3_s_cls = bm3_surface[cls_mask]
        bm3_b_cls = bm3_bed[cls_mask]
        
        # Volumes
        v_geom_cls = np.sum(bm3_t_cls * true_cell_area_km2[cls_mask]) / 1000.0
        v_ice_eq_cls = np.sum(np.maximum(bm3_t_cls - bm_firn[cls_mask], 0.0) * true_cell_area_km2[cls_mask]) / 1000.0
        
        print(f"  Class {cls_val} [{cls_name}]: {cnt:,} cells ({cls_area:,.1f} km^2, {cls_pct:.2f}%) | Mean H_BM3: {np.mean(bm3_t_cls):.1f} m | Vol Ice-Eq: {v_ice_eq_cls:.1f} km^3")
        b_class_rows.append({
            'BedMachine_Class_Value': cls_val,
            'BedMachine_Class_Name': cls_name,
            'Cell_Count': cnt,
            'Area_km2': cls_area,
            'Percentage_of_BM3_Only': cls_pct,
            'Mean_BM3_Thickness_m': np.mean(bm3_t_cls),
            'Median_BM3_Thickness_m': np.median(bm3_t_cls),
            'Std_BM3_Thickness_m': np.std(bm3_t_cls),
            'Mean_BM3_Surface_m': np.mean(bm3_s_cls),
            'Mean_BM3_Bed_m': np.mean(bm3_b_cls),
            'BM3_Geom_Volume_km3': v_geom_cls,
            'BM3_Ice_Eq_Volume_km3': v_ice_eq_cls
        })
    df_b_class = pd.DataFrame(b_class_rows)
    b_class_csv = os.path.join(TABLES_DIR, "bedmap3_only_cells_classification.csv")
    df_b_class.to_csv(b_class_csv, index=False)
    print(f"Saved: {b_class_csv}")

    # Proximity / Distribution Analysis:
    # Let's inspect where these cells are located per basin
    print("\nBedmap3-Only Cells Distribution per Basin:")
    for b_name in pen_basins['Basin']:
        dom_b_basin = basin_domain_masks[b_name]['B']
        cnt_b = np.sum(dom_b_basin)
        area_b = np.sum(true_cell_area_km2[dom_b_basin])
        v_ice_eq_b = np.sum(np.maximum(bm3_thick[dom_b_basin] - bm_firn[dom_b_basin], 0.0) * true_cell_area_km2[dom_b_basin]) / 1000.0
        print(f"  Basin {b_name}: {cnt_b:,} cells ({area_b:,.1f} km^2) | Lost Ice-Eq Vol: {v_ice_eq_b:,.1f} km^3")

    # -------------------------------------------------------------------------
    # PART 5: VERIFY FIRN AIR CONTENT (FAC) ARITHMETIC AND COVARIANCE
    # -------------------------------------------------------------------------
    print("\n[Part 5] Auditing Firn Air Content Arithmetic, Coverage, and Covariance...")
    
    fac_audit_rows = []
    for b_name in basins_to_eval:
        g_bm3 = basin_domain_masks[b_name]['BM3']
        g_bm = basin_domain_masks[b_name]['BM']
        dom_a = basin_domain_masks[b_name]['A']
        
        # Evaluate for BM3 Full Grounded Domain
        n_cells_bm3 = np.sum(g_bm3)
        fac_vals_bm3 = bm_firn[g_bm3]
        areas_bm3 = true_cell_area_km2[g_bm3]
        
        valid_fac_bm3 = np.isfinite(fac_vals_bm3) & (fac_vals_bm3 >= 0)
        n_valid_fac_bm3 = np.sum(valid_fac_bm3)
        
        mean_fac_bm3 = np.mean(fac_vals_bm3)
        median_fac_bm3 = np.median(fac_vals_bm3)
        
        # Exact integrated volume: sum(FAC_i * Area_i)
        v_fac_exact_bm3 = np.sum(fac_vals_bm3 * areas_bm3) / 1000.0
        
        # Simple naive product: mean(FAC) * sum(Area)
        v_fac_naive_bm3 = mean_fac_bm3 * np.sum(areas_bm3) / 1000.0
        
        # Spatial covariance effect: sum((FAC - mean(FAC)) * (Area - mean(Area)))
        cov_fac_area_bm3 = np.cov(fac_vals_bm3, areas_bm3)[0, 1] if n_cells_bm3 > 1 else 0.0
        cov_volume_diff_bm3 = (n_cells_bm3 * cov_fac_area_bm3) / 1000.0
        
        # Evaluate for BedMachine Full Grounded Domain
        n_cells_bm = np.sum(g_bm)
        fac_vals_bm = bm_firn[g_bm]
        areas_bm = true_cell_area_km2[g_bm]
        mean_fac_bm = np.mean(fac_vals_bm)
        median_fac_bm = np.median(fac_vals_bm)
        v_fac_exact_bm = np.sum(fac_vals_bm * areas_bm) / 1000.0
        v_fac_naive_bm = mean_fac_bm * np.sum(areas_bm) / 1000.0
        
        # Truncation check
        trunc_cells_bm3 = np.sum(g_bm3 & (bm3_thick < bm_firn))
        trunc_deficit_bm3 = np.sum((bm_firn[g_bm3 & (bm3_thick < bm_firn)] - bm3_thick[g_bm3 & (bm3_thick < bm_firn)]) * true_cell_area_km2[g_bm3 & (bm3_thick < bm_firn)]) / 1000.0
        
        fac_audit_rows.append({
            'Basin': b_name,
            'BM3_Grounded_Cells': n_cells_bm3,
            'BM3_Valid_FAC_Cells': n_valid_fac_bm3,
            'BM3_FAC_Coverage_%': (n_valid_fac_bm3 / n_cells_bm3 * 100.0),
            'BM3_Mean_FAC_m': mean_fac_bm3,
            'BM3_Median_FAC_m': median_fac_bm3,
            'BM3_Integrated_FAC_Vol_km3': v_fac_exact_bm3,
            'BM3_Naive_FAC_Vol_km3': v_fac_naive_bm3,
            'BM3_Covariance_Effect_km3': v_fac_exact_bm3 - v_fac_naive_bm3,
            'BM_Grounded_Cells': n_cells_bm,
            'BM_Integrated_FAC_Vol_km3': v_fac_exact_bm,
            'BM_Mean_FAC_m': mean_fac_bm,
            'BM3_Truncation_Cells': trunc_cells_bm3,
            'BM3_Truncation_Deficit_km3': trunc_deficit_bm3
        })
        
    df_fac_audit = pd.DataFrame(fac_audit_rows)
    fac_audit_csv = os.path.join(TABLES_DIR, "firn_air_arithmetic_audit.csv")
    df_fac_audit.to_csv(fac_audit_csv, index=False)
    print(f"Saved: {fac_audit_csv}")
    print(df_fac_audit[['Basin', 'BM3_Mean_FAC_m', 'BM3_Integrated_FAC_Vol_km3', 'BM3_Naive_FAC_Vol_km3', 'BM3_Covariance_Effect_km3', 'BM_Integrated_FAC_Vol_km3']].to_string(index=False))

    # -------------------------------------------------------------------------
    # PART 6: COMPREHENSIVE BASELINE RECONCILIATION TABLE
    # -------------------------------------------------------------------------
    print("\n[Part 6] Generating Master Baseline Reconciliation Table...")
    # Full vs Common Domain comparison for both products
    recon_master_rows = []
    for b_name in basins_to_eval:
        dom_a = basin_domain_masks[b_name]['A']
        g_bm3 = basin_domain_masks[b_name]['BM3']
        g_bm = basin_domain_masks[b_name]['BM']
        
        # Full domain
        v_bm3_full_geom = np.sum(bm3_thick[g_bm3] * true_cell_area_km2[g_bm3]) / 1000.0
        v_bm3_full_ice_eq = np.sum(np.maximum(bm3_thick[g_bm3] - bm_firn[g_bm3], 0.0) * true_cell_area_km2[g_bm3]) / 1000.0
        v_bm_full_geom = np.sum(bm_thick_geom[g_bm] * true_cell_area_km2[g_bm]) / 1000.0
        v_bm_full_ice_eq = np.sum(bm_thick_ice_eq[g_bm] * true_cell_area_km2[g_bm]) / 1000.0
        
        # Common domain
        v_bm3_comm_geom = np.sum(bm3_thick[dom_a] * true_cell_area_km2[dom_a]) / 1000.0
        v_bm3_comm_ice_eq = np.sum(np.maximum(bm3_thick[dom_a] - bm_firn[dom_a], 0.0) * true_cell_area_km2[dom_a]) / 1000.0
        v_bm_comm_geom = np.sum(bm_thick_geom[dom_a] * true_cell_area_km2[dom_a]) / 1000.0
        v_bm_comm_ice_eq = np.sum(bm_thick_ice_eq[dom_a] * true_cell_area_km2[dom_a]) / 1000.0
        
        recon_master_rows.append({
            'Basin': b_name,
            'BM3_Full_Area_km2': np.sum(true_cell_area_km2[g_bm3]),
            'BM_Full_Area_km2': np.sum(true_cell_area_km2[g_bm]),
            'Common_Area_km2': np.sum(true_cell_area_km2[dom_a]),
            'BM3_Full_Geom_km3': v_bm3_full_geom,
            'BM3_Full_Ice_Eq_km3': v_bm3_full_ice_eq,
            'BM_Full_Geom_km3': v_bm_full_geom,
            'BM_Full_Ice_Eq_km3': v_bm_full_ice_eq,
            'BM3_Common_Geom_km3': v_bm3_comm_geom,
            'BM3_Common_Ice_Eq_km3': v_bm3_comm_ice_eq,
            'BM_Common_Geom_km3': v_bm_comm_geom,
            'BM_Common_Ice_Eq_km3': v_bm_comm_ice_eq,
            'Full_Ice_Eq_Diff_km3': v_bm_full_ice_eq - v_bm3_full_ice_eq,
            'Full_Ice_Eq_Diff_%': (v_bm_full_ice_eq - v_bm3_full_ice_eq) / v_bm3_full_ice_eq * 100.0,
            'Common_Ice_Eq_Diff_km3': v_bm_comm_ice_eq - v_bm3_comm_ice_eq,
            'Common_Ice_Eq_Diff_%': (v_bm_comm_ice_eq - v_bm3_comm_ice_eq) / v_bm3_comm_ice_eq * 100.0
        })
    df_recon_master = pd.DataFrame(recon_master_rows)
    recon_master_csv = os.path.join(TABLES_DIR, "baseline_reconciliation_master.csv")
    df_recon_master.to_csv(recon_master_csv, index=False)
    print(f"Saved: {recon_master_csv}")
    print(df_recon_master[['Basin', 'BM3_Full_Ice_Eq_km3', 'BM_Full_Ice_Eq_km3', 'Full_Ice_Eq_Diff_km3', 'Full_Ice_Eq_Diff_%', 'BM3_Common_Ice_Eq_km3', 'BM_Common_Ice_Eq_km3', 'Common_Ice_Eq_Diff_km3', 'Common_Ice_Eq_Diff_%']].to_string(index=False))

    # -------------------------------------------------------------------------
    # PART 7: GENERATE HIGH-RESOLUTION DIAGNOSTIC MAPS
    # -------------------------------------------------------------------------
    print("\n[Part 7] Generating High-Resolution Diagnostic Figures...")
    
    # Coordinates in km for plotting
    xs = (np.arange(width) * transform.a + transform.c) / 1000.0
    ys = (np.arange(height) * transform.e + transform.f) / 1000.0
    extent_km = [xs[0], xs[-1], ys[-1], ys[0]]
    
    # FIGURE 1: Common Grounded-Domain Map
    # Shows Common Grounded (green), Bedmap3-Only (orange), and Non-Grounded Mainland (light gray)
    print("  Generating Map 1: Common Grounded-Domain Map...")
    fig, ax = plt.subplots(figsize=(10, 12), dpi=300)
    
    domain_map = np.zeros((height, width), dtype=np.int8)
    domain_map[in_mainland] = 1 # Non-grounded mainland land
    dom_a_pen = basin_domain_masks['Peninsula Total']['A']
    dom_b_pen = basin_domain_masks['Peninsula Total']['B']
    domain_map[dom_b_pen] = 2   # Bedmap3-Only (Domain B)
    domain_map[dom_a_pen] = 3   # Common Grounded (Domain A)
    
    cmap_domains = mcolors.ListedColormap(['#f8f9fa', '#e2e8f0', '#f97316', '#10b981'])
    bounds_d = [-0.5, 0.5, 1.5, 2.5, 3.5]
    norm_d = mcolors.BoundaryNorm(bounds_d, cmap_domains.N)
    
    im1 = ax.imshow(domain_map, extent=extent_km, cmap=cmap_domains, norm=norm_d, interpolation='nearest')
    
    # Overlay basin boundaries
    pen_basins.to_crs(crs).boundary.plot(ax=ax, color='#1e293b', linewidth=1.5, linestyle='--')
    
    # Add Basin Labels
    basin_label_coords = {
        'Hp-I': (-1650, 450),
        'I-Ipp': (-2200, 1150),
        'Ipp-J': (-1900, 950)
    }
    for b_name, (lx, ly) in basin_label_coords.items():
        ax.text(lx, ly, f"Basin {b_name}", fontsize=12, fontweight='bold', color='#0f172a',
                bbox=dict(boxstyle="round,pad=0.3", fc="#ffffff", ec="#94a3b8", alpha=0.9))
        
    legend_elements1 = [
        Patch(facecolor='#10b981', edgecolor='#059669', label=f'Common Grounded Domain A ({np.sum(dom_a_pen):,} cells, 216,062.2 km²)'),
        Patch(facecolor='#f97316', edgecolor='#ea580c', label=f'Bedmap3-Only Domain B ({np.sum(dom_b_pen):,} cells, 5,491.5 km²)'),
        Patch(facecolor='#e2e8f0', edgecolor='#cbd5e1', label='Mainland Non-Grounded / Shelf / Rock'),
        Line2D([0], [0], color='#1e293b', lw=1.5, linestyle='--', label='IMBIE Basin Boundaries')
    ]
    ax.legend(handles=legend_elements1, loc='upper left', fontsize=9, framealpha=0.95)
    
    ax.set_title("Antarctic Peninsula Spatial Grounded Domains\nCommon Grounded Domain A vs. Bedmap3-Only Domain B", fontsize=14, fontweight='bold', pad=12)
    ax.set_xlabel("Polar Stereographic X (km, EPSG:3031)", fontsize=10)
    ax.set_ylabel("Polar Stereographic Y (km, EPSG:3031)", fontsize=10)
    ax.grid(True, linestyle=':', alpha=0.5, color='#94a3b8')
    plt.tight_layout()
    map1_path = os.path.join(FIGURES_DIR, "map_phase2_6_common_grounded_domain.png")
    fig.savefig(map1_path, dpi=300)
    plt.close(fig)
    print(f"  Saved: {map1_path}")

    # FIGURE 2: Bedmap3-Only Cells Mask Classification Investigation Map
    print("  Generating Map 2: Bedmap3-Only Classification Investigation Map...")
    fig, ax = plt.subplots(figsize=(10, 12), dpi=300)
    
    # Zoom in to the Peninsula where Domain B cells occur
    b_class_map = np.zeros((height, width), dtype=np.int8)
    b_class_map[in_mainland] = 1 # Non-grounded mainland background
    b_class_map[dom_a_pen] = 2   # Common grounded background
    
    # Inside Domain B, assign BedMachine class:
    # 0 -> 3 (Ocean)
    # 1 -> 4 (Ice-Free Land / Rock)
    # 3 -> 5 (Floating Ice Shelf)
    b_ocean = dom_b_pen & (bm_mask == 0)
    b_rock = dom_b_pen & (bm_mask == 1)
    b_shelf = dom_b_pen & (bm_mask == 3)
    
    b_class_map[b_ocean] = 3
    b_class_map[b_rock] = 4
    b_class_map[b_shelf] = 5
    
    cmap_b = mcolors.ListedColormap(['#f8f9fa', '#f1f5f9', '#cbd5e1', '#0284c7', '#d97706', '#06b6d4'])
    bounds_b = [-0.5, 0.5, 1.5, 2.5, 3.5, 4.5, 5.5]
    norm_b = mcolors.BoundaryNorm(bounds_b, cmap_b.N)
    
    im2 = ax.imshow(b_class_map, extent=extent_km, cmap=cmap_b, norm=norm_b, interpolation='nearest')
    pen_basins.to_crs(crs).boundary.plot(ax=ax, color='#1e293b', linewidth=1.2, linestyle=':')
    
    legend_elements2 = [
        Patch(facecolor='#0284c7', edgecolor='#0369a1', label=f'BedMachine Ocean / Coastal Margin ({np.sum(b_ocean):,} cells, {np.sum(b_ocean)/n_dom_b*100:.1f}%)'),
        Patch(facecolor='#d97706', edgecolor='#b45309', label=f'BedMachine Ice-Free Rock / Nunatak ({np.sum(b_rock):,} cells, {np.sum(b_rock)/n_dom_b*100:.1f}%)'),
        Patch(facecolor='#06b6d4', edgecolor='#0891b2', label=f'BedMachine Floating Ice Shelf ({np.sum(b_shelf):,} cells, {np.sum(b_shelf)/n_dom_b*100:.1f}%)'),
        Patch(facecolor='#cbd5e1', edgecolor='#94a3b8', label='Common Grounded Domain A (Background)'),
        Line2D([0], [0], color='#1e293b', lw=1.2, linestyle=':', label='IMBIE Basin Boundaries')
    ]
    ax.legend(handles=legend_elements2, loc='upper left', fontsize=9, framealpha=0.95)
    
    ax.set_title("Classification of the 22,235 Bedmap3-Only Cells\nCategorized by MEaSUREs BedMachine Antarctica V4.1 Mask", fontsize=14, fontweight='bold', pad=12)
    ax.set_xlabel("Polar Stereographic X (km, EPSG:3031)", fontsize=10)
    ax.set_ylabel("Polar Stereographic Y (km, EPSG:3031)", fontsize=10)
    ax.grid(True, linestyle=':', alpha=0.5, color='#94a3b8')
    plt.tight_layout()
    map2_path = os.path.join(FIGURES_DIR, "map_phase2_6_bedmap3_only_investigation.png")
    fig.savefig(map2_path, dpi=300)
    plt.close(fig)
    print(f"  Saved: {map2_path}")

    # FIGURE 3: Common-Domain Thickness Difference Map
    # Strictly evaluates Delta H = H_BM_ice_eq - H_BM3_ice_eq on Common Grounded Domain A
    print("  Generating Map 3: Common-Domain Thickness Difference Map...")
    fig, ax = plt.subplots(figsize=(10, 12), dpi=300)
    
    diff_grid = np.full((height, width), np.nan, dtype=np.float32)
    t_bm3_ice_eq_full = np.maximum(bm3_thick - bm_firn, 0.0)
    diff_grid[dom_a_pen] = (bm_thick_ice_eq[dom_a_pen] - t_bm3_ice_eq_full[dom_a_pen]).astype(np.float32)
    
    cmap_diff = plt.cm.RdBu_r
    norm_diff = mcolors.TwoSlopeNorm(vmin=-500.0, vcenter=0.0, vmax=500.0)
    
    im3 = ax.imshow(diff_grid, extent=extent_km, cmap=cmap_diff, norm=norm_diff, interpolation='bilinear')
    pen_basins.to_crs(crs).boundary.plot(ax=ax, color='#0f172a', linewidth=1.5, linestyle='-')
    
    for b_name, (lx, ly) in basin_label_coords.items():
        ax.text(lx, ly, f"Basin {b_name}", fontsize=11, fontweight='bold', color='#0f172a',
                bbox=dict(boxstyle="round,pad=0.25", fc="#ffffff", ec="#64748b", alpha=0.9))
        
    cbar = fig.colorbar(im3, ax=ax, orientation='vertical', fraction=0.046, pad=0.04, extend='both')
    cbar.set_label("Ice-Equivalent Thickness Difference (m)\n[BedMachine V4.1 − Bedmap3 on Common Grounded Cells]", fontsize=10, fontweight='bold')
    
    ax.set_title("Common-Domain Ice-Equivalent Thickness Discrepancy\nStrictly Masked to Mutual Grounded Cells (Domain A)", fontsize=14, fontweight='bold', pad=12)
    ax.set_xlabel("Polar Stereographic X (km, EPSG:3031)", fontsize=10)
    ax.set_ylabel("Polar Stereographic Y (km, EPSG:3031)", fontsize=10)
    ax.grid(True, linestyle=':', alpha=0.5, color='#94a3b8')
    plt.tight_layout()
    map3_path = os.path.join(FIGURES_DIR, "map_phase2_6_common_thickness_difference.png")
    fig.savefig(map3_path, dpi=300)
    plt.close(fig)
    print(f"  Saved: {map3_path}")

    # FIGURE 4: Basin-Level Comparison & Difference Decomposition Charts
    print("  Generating Figure 4: Basin-Level Comparison & Decomposition Plots...")
    fig, axes = plt.subplots(2, 2, figsize=(14, 12), dpi=300)
    
    # Subplot A: Volume Comparison on Common vs Full Domain
    basins_bar = ['Hp-I', 'I-Ipp', 'Ipp-J', 'Total']
    x_indices = np.arange(len(basins_bar))
    width_b = 0.2
    
    bm3_full_v = [df_recon_master[df_recon_master['Basin']==b]['BM3_Full_Ice_Eq_km3'].values[0] if b!='Total' else df_recon_master[df_recon_master['Basin']=='Peninsula Total']['BM3_Full_Ice_Eq_km3'].values[0] for b in basins_bar]
    bm_full_v = [df_recon_master[df_recon_master['Basin']==b]['BM_Full_Ice_Eq_km3'].values[0] if b!='Total' else df_recon_master[df_recon_master['Basin']=='Peninsula Total']['BM_Full_Ice_Eq_km3'].values[0] for b in basins_bar]
    bm3_comm_v = [df_recon_master[df_recon_master['Basin']==b]['BM3_Common_Ice_Eq_km3'].values[0] if b!='Total' else df_recon_master[df_recon_master['Basin']=='Peninsula Total']['BM3_Common_Ice_Eq_km3'].values[0] for b in basins_bar]
    bm_comm_v = [df_recon_master[df_recon_master['Basin']==b]['BM_Common_Ice_Eq_km3'].values[0] if b!='Total' else df_recon_master[df_recon_master['Basin']=='Peninsula Total']['BM_Common_Ice_Eq_km3'].values[0] for b in basins_bar]
    
    axes[0, 0].bar(x_indices - 1.5*width_b, bm3_full_v, width=width_b, label='Bedmap3 (Full Mask)', color='#3b82f6')
    axes[0, 0].bar(x_indices - 0.5*width_b, bm3_comm_v, width=width_b, label='Bedmap3 (Common Mask)', color='#93c5fd')
    axes[0, 0].bar(x_indices + 0.5*width_b, bm_comm_v, width=width_b, label='BedMachine (Common Mask)', color='#f59e0b')
    axes[0, 0].bar(x_indices + 1.5*width_b, bm_full_v, width=width_b, label='BedMachine (Full Mask)', color='#d97706')
    
    axes[0, 0].set_xticks(x_indices)
    axes[0, 0].set_xticklabels(basins_bar, fontweight='bold')
    axes[0, 0].set_ylabel("Ice-Equivalent Volume (km³)", fontweight='bold')
    axes[0, 0].set_title("A. Ice-Equivalent Volume by Basin & Domain", fontweight='bold')
    axes[0, 0].legend(fontsize=8, framealpha=0.9)
    axes[0, 0].grid(True, linestyle=':', alpha=0.5)
    
    # Subplot B: Common Domain Thickness Difference Boxplots
    diff_data = [
        bm_thick_ice_eq[basin_domain_masks[b]['A']] - t_bm3_ice_eq_full[basin_domain_masks[b]['A']]
        for b in ['Hp-I', 'I-Ipp', 'Ipp-J']
    ]
    diff_data.append(bm_thick_ice_eq[dom_a_pen] - t_bm3_ice_eq_full[dom_a_pen])
    
    bplot = axes[0, 1].boxplot(diff_data, positions=x_indices, patch_artist=True, showfliers=False,
                               medianprops=dict(color='black', linewidth=1.5),
                               boxprops=dict(facecolor='#a7f3d0', edgecolor='#059669', linewidth=1.2))
    axes[0, 1].axhline(0, color='#94a3b8', linestyle='--', linewidth=1)
    axes[0, 1].set_xticks(x_indices)
    axes[0, 1].set_xticklabels(basins_bar, fontweight='bold')
    axes[0, 1].set_ylabel("Δ Thickness: BM − BM3 (m)", fontweight='bold')
    axes[0, 1].set_title("B. Common-Domain Thickness Difference Distribution", fontweight='bold')
    axes[0, 1].grid(True, linestyle=':', alpha=0.5)
    
    # Subplot C: Waterfall Decomposition of Peninsula Total Volume Difference
    decomp_labels = ['Total Diff\n(Reported)', 'Common Dom\nThickness', 'Bedmap3-Only\nMask Lost', 'Net Sum\n(Reconciled)']
    tot_diff = df_decomp[df_decomp['Basin']=='Peninsula Total']['Total_Ice_Eq_Diff_km3'].values[0]
    comm_thick_diff = df_decomp[df_decomp['Basin']=='Peninsula Total']['Common_Domain_Thickness_Diff_km3'].values[0]
    mask_lost = -df_decomp[df_decomp['Basin']=='Peninsula Total']['BM3_Only_Volume_Lost_km3'].values[0]
    reconciled = df_decomp[df_decomp['Basin']=='Peninsula Total']['Reconstructed_Total_Diff_km3'].values[0]
    
    decomp_vals = [tot_diff, comm_thick_diff, mask_lost, reconciled]
    decomp_colors = ['#6366f1', '#10b981', '#ef4444', '#6366f1']
    
    bars = axes[1, 0].bar(np.arange(len(decomp_labels)), decomp_vals, color=decomp_colors, width=0.55, edgecolor='#1e293b')
    for bar, val in zip(bars, decomp_vals):
        y_pos = val + 150 if val >= 0 else val - 450
        axes[1, 0].text(bar.get_x() + bar.get_width()/2.0, y_pos, f"{val:+,.1f}\nkm³", ha='center', va='bottom', fontsize=9, fontweight='bold')
        
    axes[1, 0].axhline(0, color='#94a3b8', linestyle='-', linewidth=0.8)
    axes[1, 0].set_xticks(np.arange(len(decomp_labels)))
    axes[1, 0].set_xticklabels(decomp_labels, fontweight='bold')
    axes[1, 0].set_ylabel("Volume Difference Component (km³)", fontweight='bold')
    axes[1, 0].set_title("C. Peninsula Total Volume Difference Decomposition", fontweight='bold')
    axes[1, 0].grid(True, linestyle=':', alpha=0.5)
    
    # Subplot D: Bedmap3-Only Cells Mask Breakdown
    b_pie_labels = ['Ocean /\nFjord Margin', 'Ice-Free Land\n/ Nunataks', 'Floating\nIce Shelf']
    b_pie_sizes = [np.sum(b_ocean), np.sum(b_rock), np.sum(b_shelf)]
    b_pie_colors = ['#0284c7', '#d97706', '#06b6d4']
    
    axes[1, 1].pie(b_pie_sizes, labels=b_pie_labels, colors=b_pie_colors, autopct='%1.1f%%',
                   startangle=140, textprops=dict(fontweight='bold', fontsize=10),
                   wedgeprops=dict(edgecolor='#ffffff', linewidth=1.5))
    axes[1, 1].set_title(f"D. BedMachine Classification of 22,235 Bedmap3-Only Cells\n({area_dom_b:,.1f} km², {v_bm3_only_ice_eq:,.1f} km³ Ice-Eq Volume)", fontweight='bold')
    
    plt.tight_layout()
    chart4_path = os.path.join(FIGURES_DIR, "chart_phase2_6_basin_comparison.png")
    fig.savefig(chart4_path, dpi=300)
    plt.close(fig)
    print(f"  Saved: {chart4_path}")
    
    print("\n" + "="*80)
    print("PHASE 2.6 AUDIT COMPLETE: ALL TABLES AND FIGURES GENERATED")
    print("="*80)

if __name__ == "__main__":
    main()
