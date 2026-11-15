"""
Phase 3.4: ML Readiness Audit and Historical Target Preparation
================================================================
Implements Phase 3.4 deliverables:
1. Autocorrelation uncertainty recalculation & sensitivity analysis (tau = 0, 1, 2, 5, 10, 20, inf)
   - Resolves the 142.60 km3 vs 204.82 km3 vs 609.52 km3 relationship.
   - Distinguishes standard deviation increases (+197.6% vs 204.82 km3; +327.4% vs 142.60 km3) from variance increases (+785.6% vs 204.82 km3; +1727% vs 142.60 km3).
   - Explicitly labels correlated uncertainty as a Sensitivity Assumption rather than a measured uncertainty.
2. IMBIE leakage audit & feature provenance classification:
   - Categorizes variables: Independent of IMBIE, Derived from IMBIE, Calibrated against IMBIE, Constrained by IMBIE, Not applicable.
3. Target variable dataset preparation:
   - Basin-indexed annual target dataset (y[b,t] and Delta V[b,t]).
   - Verifies annual changes sum to cumulative changes and basin changes sum to Domain A aggregate.
   - Dual baseline anchors preserved without observation duplication.
4. Chronological validation split design:
   - Train (1979–2005), Embargo Buffer 1 (2006–2007), Validation (2008–2014), Embargo Buffer 2 (2015), Test (2016–2024).
5. Scenario and uncertainty metadata table.

Generates:
- reports/tables/autocorrelation_sensitivity.csv
- reports/tables/ml_feature_provenance.csv
- reports/tables/ml_target_dataset.csv
- reports/tables/chronological_split_design.csv
- reports/tables/scenario_uncertainty_metadata.csv
"""

import os
import sys
import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
TABLES_DIR = os.path.join(REPORTS_DIR, "tables")
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")

TRAJ_CSV = os.path.join(TABLES_DIR, "annual_volume_trajectories.csv")
COMP_CSV = os.path.join(TABLES_DIR, "annual_mass_balance_components.csv")
UNC_CSV = os.path.join(TABLES_DIR, "annual_uncertainty_budget.csv")
RECON_CSV = os.path.join(TABLES_DIR, "domain_and_baseline_reconciliation.csv")

RHO_ICE = 0.917  # Gt / km^3

# Baseline volumes on Domain A (km^3)
BM3_BASE_HP = 100120.11
BM3_BASE_IPP = 11079.71
BM3_BASE_IPJ = 22297.77
BM3_BASE_A = 133497.59

BM4_BASE_HP = 102464.00
BM4_BASE_IPP = 12713.99
BM4_BASE_IPJ = 25524.52
BM4_BASE_A = 140702.51

OFFSET_HP = 2343.89
OFFSET_IPP = 1634.28
OFFSET_IPJ = 3226.75
OFFSET_A = 7204.92


# =========================================================================
# 1. Autocorrelation Sensitivity Table
# =========================================================================
def generate_autocorrelation_sensitivity():
    print("\n--- [1] Generating Autocorrelation Sensitivity Table ---")
    df_unc = pd.read_csv(UNC_CSV)
    sig_rates = df_unc['Total_Annual_Rate_Uncertainty_km3_yr'].values
    N = len(sig_rates)  # 46 years (1979 to 2024)

    # Audited uncorrelated cumulative variance and standard deviation
    var_indep = np.sum(sig_rates**2)
    sigma_indep = np.sqrt(var_indep)

    # Historical transcription baseline: Phase 3.2 reported value
    sigma_reported_142 = 142.6031  # Originates from Delta_H_MAE_m (142.60 m)
    var_reported_142 = sigma_reported_142**2

    cases = [
        {
            "label": "tau = 0 (Audited Uncorrelated)",
            "tau": 0.0,
            "kernel": "Independent White Noise: Cov(e_i, e_j) = sigma_i^2 * delta_ij",
            "interpretation": "Assumes zero temporal error persistence across annual satellite and RCM cycles.",
            "status": "Audited Empirical Baseline (Standard IPCC Error Propagation)"
        },
        {
            "label": "tau = 1 year (Short-Term Persistence)",
            "tau": 1.0,
            "kernel": "Exponential: Cov(e_i, e_j) = sigma_i * sigma_j * exp(-|i-j|/1.0)",
            "interpretation": "Represents 1-year inter-annual memory in firn densification and surface melt refreezing.",
            "status": "Sensitivity Assumption"
        },
        {
            "label": "tau = 2 years (Inter-Annual Climatology)",
            "tau": 2.0,
            "kernel": "Exponential: Cov(e_i, e_j) = sigma_i * sigma_j * exp(-|i-j|/2.0)",
            "interpretation": "Captures biennial climate oscillations (ENSO/SAM teleconnections) influencing Antarctic precipitation.",
            "status": "Sensitivity Assumption"
        },
        {
            "label": "tau = 5 years (Decadal Persistence - Phase 3.3)",
            "tau": 5.0,
            "kernel": "Exponential: Cov(e_i, e_j) = sigma_i * sigma_j * exp(-|i-j|/5.0)",
            "interpretation": "Captures multi-year systematic biases in RACMO2.4p1 precipitation and Nield slab-window GIA mantle viscosity.",
            "status": "Sensitivity Assumption (Primary Decadal Benchmark)"
        },
        {
            "label": "tau = 10 years (Multi-Decadal Persistence)",
            "tau": 10.0,
            "kernel": "Exponential: Cov(e_i, e_j) = sigma_i * sigma_j * exp(-|i-j|/10.0)",
            "interpretation": "Represents persistent satellite sensor calibration offsets (e.g. ERS-1/2 vs Envisat radar altimetry drift).",
            "status": "Sensitivity Assumption"
        },
        {
            "label": "tau = 20 years (Long-Term Systemic Bias)",
            "tau": 20.0,
            "kernel": "Exponential: Cov(e_i, e_j) = sigma_i * sigma_j * exp(-|i-j|/20.0)",
            "interpretation": "Simulates structural multi-decadal divergence in low-frequency regional atmospheric circulation.",
            "status": "Sensitivity Assumption"
        },
        {
            "label": "tau = inf (Fully Correlated Systematic Bias)",
            "tau": np.inf,
            "kernel": "Constant Covariance: Cov(e_i, e_j) = sigma_i * sigma_j",
            "interpretation": "Theoretical upper bound: all 46 annual errors act as an identical, perfectly correlated linear offset.",
            "status": "Theoretical Upper Bound"
        }
    ]

    records = []
    for c in cases:
        tau = c["tau"]
        cov = np.zeros((N, N))
        for i in range(N):
            for j in range(N):
                if tau == 0.0:
                    cov[i, j] = sig_rates[i]**2 if i == j else 0.0
                elif np.isinf(tau):
                    cov[i, j] = sig_rates[i] * sig_rates[j]
                else:
                    cov[i, j] = sig_rates[i] * sig_rates[j] * np.exp(-abs(i - j) / tau)
        
        var_c = np.sum(cov)
        sig_c = np.sqrt(var_c)

        pct_sig_vs_indep = (sig_c / sigma_indep - 1.0) * 100.0
        pct_sig_vs_142 = (sig_c / sigma_reported_142 - 1.0) * 100.0
        pct_var_vs_indep = (var_c / var_indep - 1.0) * 100.0
        pct_var_vs_142 = (var_c / var_reported_142 - 1.0) * 100.0

        records.append({
            "Evaluation_Case": c["label"],
            "Timescale_tau_years": tau if not np.isinf(tau) else "inf",
            "Covariance_Kernel": c["kernel"],
            "Cumulative_Variance_km6": round(var_c, 2),
            "Cumulative_Sigma_km3": round(sig_c, 2),
            "Sigma_Increase_%_vs_Audited_Uncorr_204km3": round(pct_sig_vs_indep, 2),
            "Sigma_Increase_%_vs_Phase3_2_Reported_142km3": round(pct_sig_vs_142, 2),
            "Variance_Increase_%_vs_Audited_Uncorr": round(pct_var_vs_indep, 2),
            "Variance_Increase_%_vs_Phase3_2_Reported": round(pct_var_vs_142, 2),
            "Physical_Interpretation": c["interpretation"],
            "Scientific_Status": c["status"]
        })

    df_sens = pd.DataFrame(records)
    out_path = os.path.join(TABLES_DIR, "autocorrelation_sensitivity.csv")
    df_sens.to_csv(out_path, index=False)
    print(f"Saved: {out_path}")
    print(df_sens[["Evaluation_Case", "Cumulative_Sigma_km3", "Sigma_Increase_%_vs_Audited_Uncorr_204km3", "Sigma_Increase_%_vs_Phase3_2_Reported_142km3", "Variance_Increase_%_vs_Audited_Uncorr"]].to_string())
    return df_sens


# =========================================================================
# 2. IMBIE Leakage & Feature Provenance Table
# =========================================================================
def generate_feature_provenance():
    print("\n--- [2] Generating IMBIE Leakage & Feature Provenance Table ---")
    data = [
        {
            "Variable_Name": "Annual_Volume_Change_Central_km3_yr",
            "Physical_Domain": "Target Variable (Dynamic Ice Loss)",
            "Raw_Data_Source": "Physics-based IOM reconstruction (RACMO SMB + Gate Flux)",
            "Provenance_Classification": "Constrained by IMBIE",
            "Usable_as_ML_Predictor": "NO (Ground-Truth Target)",
            "Usable_for_Independent_Validation": "NO (Emulation, not independent validation)",
            "Leakage_Prevention_Requirement": "Primary prediction target y[b,t]. Must be shielded from input feature matrix."
        },
        {
            "Variable_Name": "Cum_Volume_Anomaly_Central_km3",
            "Physical_Domain": "Target Variable (Integrated Loss)",
            "Raw_Data_Source": "Integrated annual volume increments from 1979 reference",
            "Provenance_Classification": "Constrained by IMBIE",
            "Usable_as_ML_Predictor": "NO (Cumulative Target)",
            "Usable_for_Independent_Validation": "NO (Directly coupled to IMBIE consensus)",
            "Leakage_Prevention_Requirement": "Cumulative evaluation target Delta V[b,t]. Must not be provided as a predictor."
        },
        {
            "Variable_Name": "IMBIE_Surface_Mass_Balance_Anomaly_Gt_yr",
            "Physical_Domain": "Atmospheric Forcing",
            "Raw_Data_Source": "IMBIE-3 Otosaka et al. (2026) Table / RACMO downscaled",
            "Provenance_Classification": "Derived from IMBIE",
            "Usable_as_ML_Predictor": "YES (Climate Input Feature)",
            "Usable_for_Independent_Validation": "NO (Input to both reconstruction and IMBIE)",
            "Leakage_Prevention_Requirement": "Exogenous forcing. Cannot be used to test whether the ML model independently discovered IMBIE's mass balance."
        },
        {
            "Variable_Name": "Historical_Discharge_Transitions",
            "Physical_Domain": "Glacier Dynamics",
            "Raw_Data_Source": "Literature collapse dates (Wordie 1989, Larsen A 1995, Larsen B 2002)",
            "Provenance_Classification": "Calibrated against IMBIE",
            "Usable_as_ML_Predictor": "NO (Reconstruction Parameter)",
            "Usable_for_Independent_Validation": "NO (Tuned against satellite mass trends)",
            "Leakage_Prevention_Requirement": "Parameters were tuned to reproduce regional satellite balance. Exclude from input features."
        },
        {
            "Variable_Name": "IMBIE_Reconciled_Cumulative_Mass_Balance_Gt",
            "Physical_Domain": "Regional Benchmark",
            "Raw_Data_Source": "IMBIE-3 Antarctic Peninsula Sector Time Series",
            "Provenance_Classification": "Derived from IMBIE",
            "Usable_as_ML_Predictor": "NO (Benchmark Series)",
            "Usable_for_Independent_Validation": "NO (Contained in calibration loop)",
            "Leakage_Prevention_Requirement": "STRICTLY EXCLUDED from ML pipeline. Comparing ML output to IMBIE evaluates emulation fidelity, NOT physical prediction."
        },
        {
            "Variable_Name": "RACMO_Precipitation_Snowfall_mm_yr",
            "Physical_Domain": "Atmospheric Physics",
            "Raw_Data_Source": "RACMO2.3p2 / RACMO2.4p1 regional climate model output",
            "Provenance_Classification": "Independent of IMBIE",
            "Usable_as_ML_Predictor": "YES (Primary Climate Feature)",
            "Usable_for_Independent_Validation": "YES (Atmospheric component independent of gravimetry/altimetry)",
            "Leakage_Prevention_Requirement": "Must be partitioned cleanly along chronological train/validation/test splits."
        },
        {
            "Variable_Name": "RACMO_Surface_Melt_Runoff_mm_yr",
            "Physical_Domain": "Atmospheric Physics",
            "Raw_Data_Source": "RACMO2.3p2 / RACMO2.4p1 regional climate model output",
            "Provenance_Classification": "Independent of IMBIE",
            "Usable_as_ML_Predictor": "YES (Surface Ablation Feature)",
            "Usable_for_Independent_Validation": "YES (Independent process model)",
            "Leakage_Prevention_Requirement": "Chronological split required to prevent temporal interpolation leakage."
        },
        {
            "Variable_Name": "Bedmap3_Ice_Thickness_m",
            "Physical_Domain": "Static Subglacial Topography",
            "Raw_Data_Source": "BAS Bedmap3 500 m Gridded Product (Pritchard 2025)",
            "Provenance_Classification": "Independent of IMBIE",
            "Usable_as_ML_Predictor": "YES (Static Topographic Feature)",
            "Usable_for_Independent_Validation": "YES (Independent geophysical survey)",
            "Leakage_Prevention_Requirement": "Static baseline realization A. Preserved as baseline anchor constant."
        },
        {
            "Variable_Name": "BedMachine_Ice_Thickness_m",
            "Physical_Domain": "Static Subglacial Topography",
            "Raw_Data_Source": "NASA MEaSUREs BedMachine Antarctica V4.1 (Morlighem 2025)",
            "Provenance_Classification": "Independent of IMBIE",
            "Usable_as_ML_Predictor": "YES (Static Topographic Feature)",
            "Usable_for_Independent_Validation": "YES (Independent mass conservation)",
            "Leakage_Prevention_Requirement": "Static baseline realization B. Preserved as baseline anchor constant."
        },
        {
            "Variable_Name": "Firn_Air_Content_FAC_m",
            "Physical_Domain": "Firn Densification",
            "Raw_Data_Source": "IMAU-FDM Firn Compaction Model (BedMachine V4.1 layer)",
            "Provenance_Classification": "Independent of IMBIE",
            "Usable_as_ML_Predictor": "YES (Volume-to-Mass Feature)",
            "Usable_for_Independent_Validation": "YES (Independent densification physics)",
            "Leakage_Prevention_Requirement": "Already incorporated into ice-equivalent conversion."
        },
        {
            "Variable_Name": "ITS_LIVE_Surface_Ice_Velocity_m_yr",
            "Physical_Domain": "Glacier Dynamics",
            "Raw_Data_Source": "NASA JPL autoRIFT optical & radar feature tracking (1985–2024)",
            "Provenance_Classification": "Independent of IMBIE",
            "Usable_as_ML_Predictor": "YES (Dynamic Kinematic Feature)",
            "Usable_for_Independent_Validation": "YES (Sensor-level feature tracking)",
            "Leakage_Prevention_Requirement": "Raw annual velocity mosaics. Epoch 3 (2014–2024) velocities strictly held out for Test period."
        },
        {
            "Variable_Name": "CryoSat_2_Surface_Elevation_Rate_dhdt",
            "Physical_Domain": "Satellite Radar Altimetry",
            "Raw_Data_Source": "ESA CryoSat-2 SARIn Mode Gridded Elevation Rates (2010–2024)",
            "Provenance_Classification": "Independent of IMBIE",
            "Usable_as_ML_Predictor": "YES (Validation Benchmark)",
            "Usable_for_Independent_Validation": "YES (Independent geodetic observation)",
            "Leakage_Prevention_Requirement": "Reserve as independent evaluation dataset for 2010–2024; do not blend into training target."
        },
        {
            "Variable_Name": "ICESat_2_ATL15_Elevation_Rate_dhdt",
            "Physical_Domain": "Satellite Laser Altimetry",
            "Raw_Data_Source": "NASA ICESat-2 Land Ice Height Change (Smith et al. 2021, 2018–2024)",
            "Provenance_Classification": "Independent of IMBIE",
            "Usable_as_ML_Predictor": "YES (Validation Benchmark)",
            "Usable_for_Independent_Validation": "YES (Highest-precision independent benchmark)",
            "Leakage_Prevention_Requirement": "Strictly held out for independent test set validation (2018–2024)."
        },
        {
            "Variable_Name": "Nield_2014_GIA_Uplift_Rate_mm_yr",
            "Physical_Domain": "Solid Earth Geophysics",
            "Raw_Data_Source": "Nield et al. (2014) Regional Viscoelastic Slab-Window Model",
            "Provenance_Classification": "Independent of IMBIE",
            "Usable_as_ML_Predictor": "YES (Geophysical Context Feature)",
            "Usable_for_Independent_Validation": "YES (Independent rheological model)",
            "Leakage_Prevention_Requirement": "Confirmed excluded from mass budget; isolated to altimetric rate correction."
        },
        {
            "Variable_Name": "Candidate_Nunatak_Mask_and_Volume",
            "Physical_Domain": "Geomorphological Boundary",
            "Raw_Data_Source": "Bedmap3 rock classification (18,628 cells, 620.32 km3)",
            "Provenance_Classification": "Not applicable",
            "Usable_as_ML_Predictor": "NO (Decoupled Domain B1)",
            "Usable_for_Independent_Validation": "NO (Topographic mask)",
            "Leakage_Prevention_Requirement": "Completely excluded from ML training targets to prevent static rock contamination."
        },
        {
            "Variable_Name": "Structural_Baseline_Gap_7204km3",
            "Physical_Domain": "Product Inter-comparison",
            "Raw_Data_Source": "BedMachine V4.1 vs Bedmap3 Domain A geometric subtraction",
            "Provenance_Classification": "Independent of IMBIE",
            "Usable_as_ML_Predictor": "NO (Constant Offset)",
            "Usable_for_Independent_Validation": "NO (Invariant scalar)",
            "Leakage_Prevention_Requirement": "Maintained as a constant metadata scalar (+7,204.92 km3). Never added as a predictive sample."
        }
    ]

    df_prov = pd.DataFrame(data)
    out_path = os.path.join(TABLES_DIR, "ml_feature_provenance.csv")
    df_prov.to_csv(out_path, index=False)
    print(f"Saved: {out_path}")
    print(df_prov[["Variable_Name", "Provenance_Classification", "Usable_as_ML_Predictor", "Usable_for_Independent_Validation"]].to_string())
    return df_prov


# =========================================================================
# 3. Target Variable Dataset Preparation
# =========================================================================
def generate_target_dataset():
    print("\n--- [3] Generating Basin-Indexed ML Target Dataset ---")
    df_traj = pd.read_csv(TRAJ_CSV)
    df_comp = pd.read_csv(COMP_CSV)
    df_unc = pd.read_csv(UNC_CSV)

    years = df_traj['Year'].values
    N = len(years)

    # Reconstruct annual volume changes from first differences of reported cumulative trajectories
    # This guarantees cumsum(y[b,t]) == Cum_Volume_Change exactly to machine precision!
    diff_hp_cent = np.diff(np.insert(df_traj['Cum_Volume_Change_Hp_I_km3'].values, 0, 0.0))
    diff_ipp_cent = np.diff(np.insert(df_traj['Cum_Volume_Change_I_Ipp_km3'].values, 0, 0.0))
    diff_ipj_cent = np.diff(np.insert(df_traj['Cum_Volume_Change_Ipp_J_km3'].values, 0, 0.0))
    diff_tot_cent = np.diff(np.insert(df_traj['Cum_Volume_Change_DomainA_Central_km3'].values, 0, 0.0))

    # Low and High first differences for Domain A
    diff_tot_low = np.diff(np.insert(df_traj['Cum_Volume_Change_DomainA_Low_km3'].values, 0, 0.0))
    diff_tot_high = np.diff(np.insert(df_traj['Cum_Volume_Change_DomainA_High_km3'].values, 0, 0.0))

    # Verification: sum of basin diffs vs total diff
    max_diff_sum = np.max(np.abs((diff_hp_cent + diff_ipp_cent + diff_ipj_cent) - diff_tot_cent))
    print(f"Target Check 1 (Basin Rate Sum vs Total Rate): Max diff = {max_diff_sum:.4f} km3/yr")

    # Verification: cumsum matches cumulative anomaly
    print(f"Target Check 2 (Cumsum Hp-I): Max diff = {np.max(np.abs(np.cumsum(diff_hp_cent) - df_traj['Cum_Volume_Change_Hp_I_km3'].values)):.4f} km3")
    print(f"Target Check 2 (Cumsum I-Ipp): Max diff = {np.max(np.abs(np.cumsum(diff_ipp_cent) - df_traj['Cum_Volume_Change_I_Ipp_km3'].values)):.4f} km3")
    print(f"Target Check 2 (Cumsum Ipp-J): Max diff = {np.max(np.abs(np.cumsum(diff_ipj_cent) - df_traj['Cum_Volume_Change_Ipp_J_km3'].values)):.4f} km3")
    print(f"Target Check 2 (Cumsum Domain A): Max diff = {np.max(np.abs(np.cumsum(diff_tot_cent) - df_traj['Cum_Volume_Change_DomainA_Central_km3'].values)):.4f} km3")

    # Build basin-indexed records
    basin_defs = [
        {
            "id": "Hp-I",
            "name": "Palmer Land West",
            "diff_cent": diff_hp_cent,
            "cum_cent": df_traj['Cum_Volume_Change_Hp_I_km3'].values,
            "smb": df_comp['SMB_Hp_I_Gt_yr'].values,
            "d_cent": df_comp['Discharge_Hp_I_Gt_yr'].values,
            "mb_cent": df_comp['Net_MB_Hp_I_Gt_yr'].values,
            "bm3_base": BM3_BASE_HP,
            "bm4_base": BM4_BASE_HP,
            "offset": OFFSET_HP,
            "area_km2": 108945.63,
            "cells": 432370
        },
        {
            "id": "I-Ipp",
            "name": "Graham Land West",
            "diff_cent": diff_ipp_cent,
            "cum_cent": df_traj['Cum_Volume_Change_I_Ipp_km3'].values,
            "smb": df_comp['SMB_I_Ipp_Gt_yr'].values,
            "d_cent": df_comp['Discharge_I_Ipp_Gt_yr'].values,
            "mb_cent": df_comp['Net_MB_I_Ipp_Gt_yr'].values,
            "bm3_base": BM3_BASE_IPP,
            "bm4_base": BM4_BASE_IPP,
            "offset": OFFSET_IPP,
            "area_km2": 49757.73,
            "cells": 205488
        },
        {
            "id": "Ipp-J",
            "name": "Graham Land East",
            "diff_cent": diff_ipj_cent,
            "cum_cent": df_traj['Cum_Volume_Change_Ipp_J_km3'].values,
            "smb": df_comp['SMB_Ipp_J_Gt_yr'].values,
            "d_cent": df_comp['Discharge_Ipp_J_Gt_yr'].values,
            "mb_cent": df_comp['Net_MB_Ipp_J_Gt_yr'].values,
            "bm3_base": BM3_BASE_IPJ,
            "bm4_base": BM4_BASE_IPJ,
            "offset": OFFSET_IPJ,
            "area_km2": 57358.82,
            "cells": 228500
        },
        {
            "id": "Domain_A",
            "name": "Antarctic Peninsula Domain A (Aggregate)",
            "diff_cent": diff_tot_cent,
            "cum_cent": df_traj['Cum_Volume_Change_DomainA_Central_km3'].values,
            "smb": df_comp['SMB_Total_Gt_yr'].values,
            "d_cent": df_comp['Discharge_Total_Gt_yr'].values,
            "mb_cent": df_comp['Net_MB_Total_Gt_yr'].values,
            "bm3_base": BM3_BASE_A,
            "bm4_base": BM4_BASE_A,
            "offset": OFFSET_A,
            "area_km2": 216062.17,
            "cells": 866358
        }
    ]

    records = []
    for b in basin_defs:
        b_id = b["id"]
        cum_mb = 0.0
        for i, y in enumerate(years):
            epoch = df_traj['Epoch'].values[i]
            y_vol_cent = b["diff_cent"][i]
            cum_vol_cent = b["cum_cent"][i]
            smb_val = b["smb"][i]
            d_cent_val = b["d_cent"][i]
            mb_cent_val = b["mb_cent"][i]
            cum_mb += mb_cent_val

            # Low and High volume change (explicitly available at Domain A; partitioned at basins)
            if b_id == "Domain_A":
                y_vol_low = diff_tot_low[i]
                cum_vol_low = df_traj['Cum_Volume_Change_DomainA_Low_km3'].values[i]
                y_vol_high = diff_tot_high[i]
                cum_vol_high = df_traj['Cum_Volume_Change_DomainA_High_km3'].values[i]
            else:
                # Basins track central trajectory; Low/High bounds are evaluated at regional scale
                # To prevent arbitrary unconstrained disaggregation, basin-level Low/High are noted as regional bounds
                y_vol_low = np.nan
                cum_vol_low = np.nan
                y_vol_high = np.nan
                cum_vol_high = np.nan

            ann_rate_unc = df_unc['Total_Annual_Rate_Uncertainty_km3_yr'].values[i]
            
            # Target spatial description
            spatial_desc = "Basin-aggregated integrated volume rate (NOT gridded spatial field)" if b_id != "Domain_A" else "Regional aggregate Domain A (NOT gridded spatial field)"

            records.append({
                "Year": y,
                "Basin_ID": b_id,
                "Basin_Name": b["name"],
                "Epoch": epoch,
                "Target_Annual_Volume_Change_Central_km3_yr": round(y_vol_cent, 2),
                "Target_Cum_Volume_Anomaly_Central_km3": round(cum_vol_cent, 2),
                "Scenario_Annual_Volume_Change_Low_km3_yr": round(y_vol_low, 2) if not np.isnan(y_vol_low) else "DomainA_Only",
                "Scenario_Cum_Volume_Anomaly_Low_km3": round(cum_vol_low, 2) if not np.isnan(cum_vol_low) else "DomainA_Only",
                "Scenario_Annual_Volume_Change_High_km3_yr": round(y_vol_high, 2) if not np.isnan(y_vol_high) else "DomainA_Only",
                "Scenario_Cum_Volume_Anomaly_High_km3": round(cum_vol_high, 2) if not np.isnan(cum_vol_high) else "DomainA_Only",
                "Annual_SMB_Gt_yr": round(smb_val, 2),
                "Annual_Discharge_Central_Gt_yr": round(d_cent_val, 2),
                "Annual_Net_MB_Central_Gt_yr": round(mb_cent_val, 2),
                "Cum_Net_MB_Central_Gt": round(cum_mb, 2),
                "Bedmap3_Baseline_Anchor_km3": b["bm3_base"],
                "BedMachine_Baseline_Anchor_km3": b["bm4_base"],
                "Baseline_Structural_Offset_km3": b["offset"],
                "Grounded_Area_km2": b["area_km2"],
                "Grounded_Cell_Count": b["cells"],
                "Annual_Rate_Uncertainty_DomainA_km3_yr": round(ann_rate_unc, 2),
                "Target_Spatial_Resolution": spatial_desc,
                "Candidate_Nunatak_Status": "Decoupled (Outside Primary Target Domain)"
            })

    df_target = pd.DataFrame(records)
    out_path = os.path.join(TABLES_DIR, "ml_target_dataset.csv")
    df_target.to_csv(out_path, index=False)
    print(f"Saved: {out_path} (Total Rows: {len(df_target)})")
    return df_target


# =========================================================================
# 4. Chronological Validation Split Design Table
# =========================================================================
def generate_chronological_split_design():
    print("\n--- [4] Generating Chronological Validation Split Design Table ---")
    data = [
        {
            "Split_Stage": "Train Period",
            "Start_Year": 1979,
            "End_Year": 2005,
            "Duration_Years": 27,
            "Basins_Included": "Hp-I, I-Ipp, Ipp-J (3 basins)",
            "Sample_Count_N_basin_years": 81,
            "Regional_Aggregate_N": 27,
            "Observational_Regime": "Epoch 1 & Early Epoch 2: Model-assisted RACMO SMB + parameterized discharge; Wordie (1989), Larsen A (1995), Larsen B (2002) collapses.",
            "Temporal_Leakage_Protection": "Chronologically strictly preceding validation/test epochs. No forward information leakage.",
            "Embargo_Buffer_Description": "None needed prior to start (anchored at 1979 reference).",
            "IMBIE_Calibration_Coupling": "Coupled to IMBIE via RACMO SMB anomaly and satellite discharge tuning.",
            "Permitted_ML_Operations": "Model feature training, loss minimization, internal time-series cross-validation (rolling-origin walk-forward).",
            "Recommended_Model_Capacity": "Low-to-moderate capacity regularized models (ElasticNet, Ridge, shallow Gradient Boosted Trees, Physics-Informed Linear Dynamic Systems). Deep networks prohibited due to N=81 sample size."
        },
        {
            "Split_Stage": "Embargo Buffer 1",
            "Start_Year": 2006,
            "End_Year": 2007,
            "Duration_Years": 2,
            "Basins_Included": "Excluded from Train and Validation",
            "Sample_Count_N_basin_years": 6,
            "Regional_Aggregate_N": 2,
            "Observational_Regime": "Post-Larsen B surge relaxation transition.",
            "Temporal_Leakage_Protection": "2-year temporal quarantine buffer. Prevents autoregressive feature lags (AR(1), AR(2), 2-year rolling climate averages) in the validation set from looking backward into training target labels.",
            "Embargo_Buffer_Description": "Mandatory 2-year gap isolating Train (2005) from Validation (2008).",
            "IMBIE_Calibration_Coupling": "Multi-sensor constrained.",
            "Permitted_ML_Operations": "STRICTLY EXCLUDED from training loss and validation scoring. Used only to populate lag features for the start of the validation window.",
            "Recommended_Model_Capacity": "Quarantined buffer."
        },
        {
            "Split_Stage": "Validation Period",
            "Start_Year": 2008,
            "End_Year": 2014,
            "Duration_Years": 7,
            "Basins_Included": "Hp-I, I-Ipp, Ipp-J (3 basins)",
            "Sample_Count_N_basin_years": 21,
            "Regional_Aggregate_N": 7,
            "Observational_Regime": "Mid-to-Late Epoch 2: Multi-sensor satellite constraint (GRACE RL06 mascons, ICESat-1, Envisat, early CryoSat-2).",
            "Temporal_Leakage_Protection": "Chronologically strictly following Train and Embargo 1. No random cross-validation permitted.",
            "Embargo_Buffer_Description": "Protected by Embargo Buffer 1 (2006–2007) on the left.",
            "IMBIE_Calibration_Coupling": "Constrained by IMBIE satellite trends.",
            "Permitted_ML_Operations": "Hyperparameter tuning, regularization penalty selection (alpha, lambda), feature subset selection, early stopping.",
            "Recommended_Model_Capacity": "Validation sample size is small (N=21 basin-years). Evaluate models using rolling-origin walk-forward evaluation within the window."
        },
        {
            "Split_Stage": "Embargo Buffer 2",
            "Start_Year": 2015,
            "End_Year": 2015,
            "Duration_Years": 1,
            "Basins_Included": "Excluded from Validation and Test",
            "Sample_Count_N_basin_years": 3,
            "Regional_Aggregate_N": 1,
            "Observational_Regime": "Onset of Sentinel-1 SAR constellation velocity era.",
            "Temporal_Leakage_Protection": "1-year temporal quarantine buffer. Prevents 1-year lag features in the test set from accessing validation ground truth.",
            "Embargo_Buffer_Description": "Mandatory 1-year gap isolating Validation (2014) from Test (2016).",
            "IMBIE_Calibration_Coupling": "Directly observed velocity era.",
            "Permitted_ML_Operations": "STRICTLY EXCLUDED from parameter tuning and final scoring. Used only to initialize lag features for the test window.",
            "Recommended_Model_Capacity": "Quarantined buffer."
        },
        {
            "Split_Stage": "Test Period (Held-Out Final Evaluation)",
            "Start_Year": 2016,
            "End_Year": 2024,
            "Duration_Years": 9,
            "Basins_Included": "Hp-I, I-Ipp, Ipp-J (3 basins)",
            "Sample_Count_N_basin_years": 27,
            "Regional_Aggregate_N": 9,
            "Observational_Regime": "Epoch 3: Observation-rich era (Sentinel-1 SAR velocity tracking, CryoSat-2 SARIn, ICESat-2 ATL15 laser altimetry). Highest data density.",
            "Temporal_Leakage_Protection": "Strictly held out. Never touched during model development, hyperparameter selection, or feature engineering.",
            "Embargo_Buffer_Description": "Protected by Embargo Buffer 2 (2015) on the left.",
            "IMBIE_Calibration_Coupling": "Independent satellite observations available (ICESat-2, CryoSat-2) for true out-of-sample physical evaluation.",
            "Permitted_ML_Operations": "One-time final evaluation of candidate model architectures. Primary metrics: RMSE, MAE, R^2, and cumulative mass conservation error.",
            "Recommended_Model_Capacity": "Evaluated against held-out ground truth. Must be compared against physics-based baseline."
        },
        {
            "Split_Stage": "Full Historical Trajectory (Reference)",
            "Start_Year": 1979,
            "End_Year": 2024,
            "Duration_Years": 46,
            "Basins_Included": "Hp-I, I-Ipp, Ipp-J (3 basins) + Domain A",
            "Sample_Count_N_basin_years": 138,
            "Regional_Aggregate_N": 46,
            "Observational_Regime": "Full 46-year hybrid reconstruction (Epochs 1, 2, and 3).",
            "Temporal_Leakage_Protection": "Complete master dataset. Split according to the 5-stage chronological protocol above.",
            "Embargo_Buffer_Description": "Total active evaluated years: 43 years (3 years quarantined in embargos).",
            "IMBIE_Calibration_Coupling": "Regional consistency assessed.",
            "Permitted_ML_Operations": "Full sequence target dataset.",
            "Recommended_Model_Capacity": "Dataset total size: 138 basin-year instances (or 46 regional aggregate instances)."
        }
    ]

    df_split = pd.DataFrame(data)
    out_path = os.path.join(TABLES_DIR, "chronological_split_design.csv")
    df_split.to_csv(out_path, index=False)
    print(f"Saved: {out_path}")
    print(df_split[["Split_Stage", "Start_Year", "End_Year", "Duration_Years", "Sample_Count_N_basin_years", "Observational_Regime"]].to_string())
    return df_split


# =========================================================================
# 5. Scenario and Uncertainty Metadata Table
# =========================================================================
def generate_scenario_uncertainty_metadata():
    print("\n--- [5] Generating Scenario & Uncertainty Metadata Table ---")
    data = [
        {
            "Metadata_Category": "Candidate ML Training Target",
            "Variable_or_Term": "Central Scenario (Domain A: -941.28 km3 by 2024)",
            "Quantitative_Scope": "Primary ground truth y[b,t] across Hp-I (-201.90), I-Ipp (-249.89), Ipp-J (-489.49 km3).",
            "Statistical_Type": "Deterministic physical consensus trajectory.",
            "Interpretation_Rule": "Trained as the primary dependent variable. Models minimize prediction error relative to Central.",
            "ML_Training_Directive": "Train models on Central. NEVER average Central with Low or High."
        },
        {
            "Metadata_Category": "Dynamic Scenario Sensitivity Bounds",
            "Variable_or_Term": "Low Scenario (Domain A: -627.48 km3) vs High Scenario (Domain A: -1,289.42 km3)",
            "Quantitative_Scope": "661.94 km3 envelope spread by 2024 (Low: balance flux pre-2000; High: accelerated Wordie/Larsen A pre-2000).",
            "Statistical_Type": "Multi-decadal scenario divergence (structural uncertainty in unobserved historical discharge).",
            "Interpretation_Rule": "NOT a Gaussian confidence interval (sigma). Represents discrete bounding hypotheses of unobserved 1979–1999 glacier dynamics.",
            "ML_Training_Directive": "Reserved for sensitivity testing and scenario robustness bounds. Do NOT train on Low or High directly, and NEVER average."
        },
        {
            "Metadata_Category": "Conditional Uncorrelated Statistical Error",
            "Variable_or_Term": "sigma_cum_uncorr = +/- 204.82 km3 (Audited) / +/- 142.60 km3 (Phase 3.2 reported)",
            "Quantitative_Scope": "+/- 204.82 km3 is the true quadrature sum of 46 annual rate sigmas. +/- 142.60 km3 was transcribed from Delta_H_MAE_m (142.60 m).",
            "Statistical_Type": "Conditional white noise variance: Var = sum(sigma_rate^2).",
            "Interpretation_Rule": "Conditional lower bound on statistical error assuming zero temporal correlation across annual measurement and model cycles.",
            "ML_Training_Directive": "Use as lower-bound measurement noise floor in probabilistic ML models (e.g. Gaussian Process likelihood noise)."
        },
        {
            "Metadata_Category": "Decadal Correlated Uncertainty Sensitivity",
            "Variable_or_Term": "sigma_cum_corr = +/- 609.52 km3 (tau = 5 years) [Range: +/- 403.31 (tau=2) to +/- 806.23 km3 (tau=10)]",
            "Quantitative_Scope": "Var = sum_i sum_j sigma_i sigma_j exp(-|i-j|/tau). Expands statistical sigma by +197.6% (vs 204.82) / +327.4% (vs 142.60); variance expands by +785.6%.",
            "Statistical_Type": "Sensitivity assumption incorporating multi-year persistence in atmospheric SMB and GIA viscosity biases.",
            "Interpretation_Rule": "Must be explicitly labeled as a 'Sensitivity Assumption', NOT an empirically measured covariance.",
            "ML_Training_Directive": "Use to set realistic loss tolerance bands. If ML predictions deviate within +/- 609.52 km3 over multi-decadal horizons, they are statistically consistent with input observational uncertainty."
        },
        {
            "Metadata_Category": "Structural Baseline Offset Invariance",
            "Variable_or_Term": "BedMachine V4.1 - Bedmap3 = +7,204.92 km3 (+5.40% on Domain A)",
            "Quantitative_Scope": "+2,343.89 km3 (Hp-I), +1,634.28 km3 (I-Ipp), +3,226.75 km3 (Ipp-J), +7,204.92 km3 (Domain A).",
            "Statistical_Type": "Deterministic time-invariant geometric offset across 866,358 common cells.",
            "Interpretation_Rule": "Structural inter-product gap arising from bed topography mapping and ice thickness algorithms.",
            "ML_Training_Directive": "Store as alternative baseline constants. Future volume projections Delta V(2025–2100) are applied additively to both baselines. NEVER duplicate samples."
        },
        {
            "Metadata_Category": "Topographic Nunatak Mask Decoupling",
            "Variable_or_Term": "Domain B1 Candidate Nunataks (18,628 cells, 620.32 km3)",
            "Quantitative_Scope": "18,628 cells classified as rock outcrop in BedMachine but thin ice in Bedmap3.",
            "Statistical_Type": "Discrete geomorphological mask uncertainty.",
            "Interpretation_Rule": "Maintained outside dynamic Domain A trajectory. Evaluated under discrete hypotheses (H1: 0, H2: atmospheric, H3: static 620.32 km3).",
            "ML_Training_Directive": "Decoupled from ML training targets. Target variable y[b,t] represents Domain A dynamic grounded ice sheet ONLY."
        }
    ]

    df_meta = pd.DataFrame(data)
    out_path = os.path.join(TABLES_DIR, "scenario_uncertainty_metadata.csv")
    df_meta.to_csv(out_path, index=False)
    print(f"Saved: {out_path}")
    print(df_meta[["Metadata_Category", "Variable_or_Term", "Quantitative_Scope", "ML_Training_Directive"]].to_string())
    return df_meta


# =========================================================================
# Main Execution Controller
# =========================================================================
def main():
    print("=" * 80)
    print("EXECUTING PHASE 3.4: ML READINESS AUDIT AND TARGET PREPARATION")
    print("=" * 80)
    
    generate_autocorrelation_sensitivity()
    generate_feature_provenance()
    generate_target_dataset()
    generate_chronological_split_design()
    generate_scenario_uncertainty_metadata()

    print("\nPhase 3.4 Tables Successfully Created.")

if __name__ == "__main__":
    main()

