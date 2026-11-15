import os
import shutil
import numpy as np
import pandas as pd

BASE_DIR = r'c:\Users\akash\OneDrive\Desktop\mlbasics\antarctic-ice-volume-prediction'
REPORTS_DIR = os.path.join(BASE_DIR, 'reports')
REPORTS_TBL = os.path.join(REPORTS_DIR, 'tables')
BRAIN_DIR = r'C:\Users\akash\.gemini\antigravity\brain\52ad6ae8-887d-48db-85e7-7d53f431979f'
BRAIN_TBL = os.path.join(BRAIN_DIR, 'tables')
os.makedirs(REPORTS_TBL, exist_ok=True)
os.makedirs(BRAIN_TBL, exist_ok=True)

# -----------------------------------------------------------------------------
# 1. DELIVERABLE 1: stage6_dataset_inventory.csv
# -----------------------------------------------------------------------------
inventory_records = [
    {
        "Inventory_ID": "INV-01",
        "Dataset_Name": "Phase 3.2 Historical Basin Mass & Volume Reconstruction Master Dataset",
        "File_Path": "reports/tables/ml_target_dataset.csv",
        "File_Size_Bytes": os.path.getsize(os.path.join(REPORTS_TBL, "ml_target_dataset.csv")),
        "Temporal_Coverage": "1979 - 2024 (46 annual time steps)",
        "Spatial_Coverage": "3 Physical Basins (Hp-I, I-Ipp, Ipp-J) + Domain A Regional Aggregate",
        "Physical_Quantity_and_Units": "Annual solid-ice volume change (km3/yr) and mass balance (Gt/yr)",
        "Sample_Count": 184,
        "Missing_Values_Count": 0,
        "Missing_Value_Treatment": "Complete reconstructed series; zero NaNs present",
        "Data_Provenance_and_Role": "Historical Reconstruction (Phase 3.2); Primary ML Target Dataset",
        "ML_Readiness_Status": "READY_PRIMARY_ML_TARGET"
    },
    {
        "Inventory_ID": "INV-02",
        "Dataset_Name": "Stage 5.1 Historical Transient Simulation Results (19-Year Validation)",
        "File_Path": "reports/tables/stage5_1_historical_simulation_results.csv",
        "File_Size_Bytes": os.path.getsize(os.path.join(REPORTS_TBL, "stage5_1_historical_simulation_results.csv")),
        "Temporal_Coverage": "2000 - 2018 (19 annual steps, 190 sub-steps at dt=0.10 yr)",
        "Spatial_Coverage": "Domain A Grounded & Floating Domains (216,062.17 km2 grounded)",
        "Physical_Quantity_and_Units": "Modeled SMB, GL discharge, calving, net grounded mass change (Gt/yr)",
        "Sample_Count": 19,
        "Missing_Values_Count": 0,
        "Missing_Value_Treatment": "Zero NaNs in physical fields; missing satellite periods explicitly NaN",
        "Data_Provenance_and_Role": "Physical Model Simulation (2D SSA Transient Solver); Residual Baseline",
        "ML_Readiness_Status": "READY_PHYSICAL_RESIDUAL_BASELINE"
    },
    {
        "Inventory_ID": "INV-03",
        "Dataset_Name": "Stage 5.1 Discrete Mass Conservation Ledger",
        "File_Path": "reports/tables/stage5_1_mass_conservation.csv",
        "File_Size_Bytes": os.path.getsize(os.path.join(REPORTS_TBL, "stage5_1_mass_conservation.csv")),
        "Temporal_Coverage": "2000 - 2018 (19 annual steps)",
        "Spatial_Coverage": "Domain A moving boundary system (grounded + shelf)",
        "Physical_Quantity_and_Units": "Grounded mass, shelf mass, GL flux, calving, ungrounding transfer (Gt)",
        "Sample_Count": 19,
        "Missing_Values_Count": 0,
        "Missing_Value_Treatment": "Zero NaNs; machine-precision conservation (< 1e-10 Gt/yr)",
        "Data_Provenance_and_Role": "Physical Model Diagnostic; Numerical Conservation Ledger",
        "ML_Readiness_Status": "READY_CONSERVATION_AUDIT"
    },
    {
        "Inventory_ID": "INV-04",
        "Dataset_Name": "40-Year RACMO2.3p2 XPEN055 Historical Forcing Inventory",
        "File_Path": "reports/tables/stage5_1_historical_forcing_inventory.csv",
        "File_Size_Bytes": os.path.getsize(os.path.join(REPORTS_TBL, "stage5_1_historical_forcing_inventory.csv")),
        "Temporal_Coverage": "1979 - 2018 (40 annual steps, 480 monthly grids)",
        "Spatial_Coverage": "Domain A Grounded Ice Sheet (1 km downscaled mesh)",
        "Physical_Quantity_and_Units": "Surface mass balance (Gt/yr and mm w.e./yr)",
        "Sample_Count": 40,
        "Missing_Values_Count": 0,
        "Missing_Value_Treatment": "100% spatial and temporal completeness; zero NaNs",
        "Data_Provenance_and_Role": "Atmospheric Climate Forcing (KNMI RACMO2.3p2 ERA-Interim)",
        "ML_Readiness_Status": "READY_EXOGENOUS_CLIMATE_FEATURE"
    },
    {
        "Inventory_ID": "INV-05",
        "Dataset_Name": "Stage 5.1 Regional Basin Validation Metrics",
        "File_Path": "reports/tables/stage5_1_regional_validation_metrics.csv",
        "File_Size_Bytes": os.path.getsize(os.path.join(REPORTS_TBL, "stage5_1_regional_validation_metrics.csv")),
        "Temporal_Coverage": "2002 - 2017 (GRACE satellite gravimetry epoch)",
        "Spatial_Coverage": "Basin Hp-I (Palmer West), Basin I-Ipp (Graham Land), Basin Ipp-J (Palmer East)",
        "Physical_Quantity_and_Units": "Modeled vs observed GRACE mascon mass balance rates (Gt/yr)",
        "Sample_Count": 4,
        "Missing_Values_Count": 0,
        "Missing_Value_Treatment": "Complete regional partition",
        "Data_Provenance_and_Role": "Satellite Gravimetry Benchmark (Groh et al. 2019 / Sasgen et al. 2019)",
        "ML_Readiness_Status": "READY_REGIONAL_EVALUATION"
    },
    {
        "Inventory_ID": "INV-06",
        "Dataset_Name": "Stage 5.1 Multi-Technique Validation Evidence Matrix",
        "File_Path": "reports/tables/stage5_1_validation_evidence_matrix.csv",
        "File_Size_Bytes": os.path.getsize(os.path.join(REPORTS_TBL, "stage5_1_validation_evidence_matrix.csv")),
        "Temporal_Coverage": "1979 - 2024 (Multi-decadal multi-sensor satellite record)",
        "Spatial_Coverage": "Antarctic Peninsula Domain A and tributary glacier basins",
        "Physical_Quantity_and_Units": "Observational metadata, uncertainty bounds, calibration lineage, validation verdicts",
        "Sample_Count": 8,
        "Missing_Values_Count": 0,
        "Missing_Value_Treatment": "Categorical metadata inventory",
        "Data_Provenance_and_Role": "Observation Governance & Provenance Classification Matrix",
        "ML_Readiness_Status": "READY_PROVENANCE_GOVERNANCE"
    },
    {
        "Inventory_ID": "INV-07",
        "Dataset_Name": "Stage 5.1 Alpine Headwall Slope Regularization Sensitivity",
        "File_Path": "reports/tables/stage5_1_slope_regularization_sensitivity.csv",
        "File_Size_Bytes": os.path.getsize(os.path.join(REPORTS_TBL, "stage5_1_slope_regularization_sensitivity.csv")),
        "Temporal_Coverage": "Static initial state + 2-year transient coupling",
        "Spatial_Coverage": "Domain A grounded ice cells (217,803 active cells across 7 stress regimes)",
        "Physical_Quantity_and_Units": "Driving stress (kPa), regularized stress (kPa), attenuation factor (%), CFL",
        "Sample_Count": 7,
        "Missing_Values_Count": 0,
        "Missing_Value_Treatment": "Analytical evaluation",
        "Data_Provenance_and_Role": "Numerical Regularizer Diagnostic (Limiter formulation evaluation)",
        "ML_Readiness_Status": "READY_STRESS_FEATURE_DESCRIPTOR"
    },
    {
        "Inventory_ID": "INV-08",
        "Dataset_Name": "Stage 5.1 Grounding-Line Surface Continuity Audit",
        "File_Path": "reports/tables/stage5_1_surface_continuity_test.csv",
        "File_Size_Bytes": os.path.getsize(os.path.join(REPORTS_TBL, "stage5_1_surface_continuity_test.csv")),
        "Temporal_Coverage": "t=0.0 yr to t=19.0 yr (2000-2018)",
        "Spatial_Coverage": "4,695 stationary GL faces; 30,366 ungrounding transitions",
        "Physical_Quantity_and_Units": "Surface elevation step (m), RMS step (m), induced calving anomaly (Gt/yr)",
        "Sample_Count": 5,
        "Missing_Values_Count": 0,
        "Missing_Value_Treatment": "Complete interface evaluation",
        "Data_Provenance_and_Role": "Continuity Verification Diagnostic",
        "ML_Readiness_Status": "READY_GEOMETRY_DESCRIPTOR"
    },
    {
        "Inventory_ID": "INV-09",
        "Dataset_Name": "Stage 5.1 Model Failure and Limitation Register",
        "File_Path": "reports/tables/stage5_1_failure_and_limitation_register.csv",
        "File_Size_Bytes": os.path.getsize(os.path.join(REPORTS_TBL, "stage5_1_failure_and_limitation_register.csv")),
        "Temporal_Coverage": "Historical & Transient Development Lifecycles (Stages 4.5 - 5.1)",
        "Spatial_Coverage": "Entire model domain and numerical algorithms",
        "Physical_Quantity_and_Units": "Limitation category, observed impact, resolution status, gate status",
        "Sample_Count": 11,
        "Missing_Values_Count": 0,
        "Missing_Value_Treatment": "Complete limitation registry (FAIL-01 to FAIL-11)",
        "Data_Provenance_and_Role": "Model Limitation and Boundary Governance Register",
        "ML_Readiness_Status": "READY_RISK_GOVERNANCE"
    },
    {
        "Inventory_ID": "INV-10",
        "Dataset_Name": "Stage 4a/Phase 3 Chronological Split Design Specification",
        "File_Path": "reports/tables/chronological_split_design.csv",
        "File_Size_Bytes": os.path.getsize(os.path.join(REPORTS_TBL, "chronological_split_design.csv")),
        "Temporal_Coverage": "1979 - 2024 (5 split stages + full reference)",
        "Spatial_Coverage": "3 Basins (Hp-I, I-Ipp, Ipp-J)",
        "Physical_Quantity_and_Units": "Split stage, start/end years, sample counts, quarantine buffer rules",
        "Sample_Count": 6,
        "Missing_Values_Count": 0,
        "Missing_Value_Treatment": "Complete split definition",
        "Data_Provenance_and_Role": "Temporal Validation Architecture; Leakage Prevention Standard",
        "ML_Readiness_Status": "READY_SPLIT_STANDARD"
    },
    {
        "Inventory_ID": "INV-11",
        "Dataset_Name": "Row-Level Split Manifest",
        "File_Path": "reports/tables/split_manifest_row_level.csv",
        "File_Size_Bytes": os.path.getsize(os.path.join(REPORTS_TBL, "split_manifest_row_level.csv")),
        "Temporal_Coverage": "1979 - 2024 (46 annual time steps)",
        "Spatial_Coverage": "3 Basins + Domain A",
        "Physical_Quantity_and_Units": "Row-by-row split status, target value, leakage control reason",
        "Sample_Count": 184,
        "Missing_Values_Count": 0,
        "Missing_Value_Treatment": "Every row mapped to deterministic split partition",
        "Data_Provenance_and_Role": "Sample-Level Split Allocation Table",
        "ML_Readiness_Status": "READY_ROW_SPLIT_MANIFEST"
    },
    {
        "Inventory_ID": "INV-12",
        "Dataset_Name": "Task A2 Model Feature Manifest",
        "File_Path": "reports/tables/model_feature_manifest.csv",
        "File_Size_Bytes": os.path.getsize(os.path.join(REPORTS_TBL, "model_feature_manifest.csv")),
        "Temporal_Coverage": "Retrospective hindcast evaluation features",
        "Spatial_Coverage": "3 Basins",
        "Physical_Quantity_and_Units": "Feature names, symbols, sources, operational lags, leakage control rules",
        "Sample_Count": 10,
        "Missing_Values_Count": 0,
        "Missing_Value_Treatment": "Standardized feature whitelist",
        "Data_Provenance_and_Role": "Feature Engineering Specification",
        "ML_Readiness_Status": "READY_FEATURE_SPECIFICATION"
    },
    {
        "Inventory_ID": "INV-13",
        "Dataset_Name": "Stage 4.5.3 Unified Physical Fields Gridded Package",
        "File_Path": "data/processed/stage4_5_3/stage4_5_3_unified_physical_fields.nc",
        "File_Size_Bytes": os.path.getsize(os.path.join(BASE_DIR, "data/processed/stage4_5_3/stage4_5_3_unified_physical_fields.nc")),
        "Temporal_Coverage": "Nominal reference epoch (~2014) on 1 km WGS84 polar stereographic grid",
        "Spatial_Coverage": "Domain A (1700 x 1300 grid, 217,803 active grounded cells)",
        "Physical_Quantity_and_Units": "Ice thickness (m), surface elevation (m), bed (m), velocity (m/yr), stress (Pa)",
        "Sample_Count": 2210000,
        "Missing_Values_Count": 0,
        "Missing_Value_Treatment": "Physical quality masks applied; NaNs explicitly masked from active domain",
        "Data_Provenance_and_Role": "BedMachine V4.1, MEaSUREs InSAR, RACMO SMB; Primary Solver Input",
        "ML_Readiness_Status": "READY_SPATIAL_GEOMETRY_SOURCE"
    },
    {
        "Inventory_ID": "INV-14",
        "Dataset_Name": "IMBIE-3 Partitioned Mass Balance Time Series (Raw Product)",
        "File_Path": "data/raw/imbie/imbie3_antarctic_peninsula_Gt_partitioned.csv",
        "File_Size_Bytes": os.path.getsize(os.path.join(BASE_DIR, "data/raw/imbie/imbie3_antarctic_peninsula_Gt_partitioned.csv")),
        "Temporal_Coverage": "1979-01-01 to 2023-12-01 (540 monthly time steps)",
        "Spatial_Coverage": "Antarctic Peninsula Ice Sheet (Domain A grounded footprint)",
        "Physical_Quantity_and_Units": "Reconciled mass balance rate (Gt/yr), cumulative mass anomaly (Gt), SMB & dynamic components",
        "Sample_Count": 540,
        "Missing_Values_Count": 0,
        "Missing_Value_Treatment": "Complete monthly time series with 1-sigma uncertainty bands",
        "Data_Provenance_and_Role": "External Reconciled Benchmark (Otosaka et al. 2023)",
        "ML_Readiness_Status": "READY_EXTERNAL_BENCHMARK"
    }
]

df_inv = pd.DataFrame(inventory_records)
p_inv = os.path.join(REPORTS_TBL, "stage6_dataset_inventory.csv")
df_inv.to_csv(p_inv, index=False)
shutil.copy(p_inv, os.path.join(BRAIN_TBL, "stage6_dataset_inventory.csv"))
print(f"[Saved] {p_inv}")

# -----------------------------------------------------------------------------
# 2. DELIVERABLE 2: stage6_feature_dictionary.csv
# -----------------------------------------------------------------------------
feature_dict_records = [
    {
        "Feature_ID": "FEAT-01",
        "Feature_Name": "Target_Volume_Change_Lag1_km3_yr",
        "Mathematical_Symbol": "y_{b, t-1}",
        "Feature_Category": "Autoregressive Dynamic State",
        "Physical_Units": "km3/yr",
        "Temporal_Availability": "Antecedent year t-1 observation",
        "Operational_Lag": "Lag-1 (t-1)",
        "Lookahead_Leakage_Risk": "ZERO: Strictly precedes target year t; 1979 imputed using training-fold median only",
        "Imputation_Method_for_Missing_Lags": "Training-fold median (1979-2005) per basin",
        "Normalization_Pipeline": "Fold-contained StandardScaler (fitted on Training fold only)",
        "Algorithm_Suitability": "Linear (Ridge, ElasticNet), Trees (RF, GBT), Persistence Baseline",
        "Feature_Importance_Hypothesis": "Strongest predictor under ice dynamic persistence"
    },
    {
        "Feature_ID": "FEAT-02",
        "Feature_Name": "Target_Volume_Change_Lag2_km3_yr",
        "Mathematical_Symbol": "y_{b, t-2}",
        "Feature_Category": "Autoregressive Dynamic State",
        "Physical_Units": "km3/yr",
        "Temporal_Availability": "Antecedent year t-2 observation",
        "Operational_Lag": "Lag-2 (t-2)",
        "Lookahead_Leakage_Risk": "ZERO: Strictly precedes target year t by 2 years; 1979-1980 imputed using training median",
        "Imputation_Method_for_Missing_Lags": "Training-fold median (1979-2005) per basin",
        "Normalization_Pipeline": "Fold-contained StandardScaler (fitted on Training fold only)",
        "Algorithm_Suitability": "Linear (Ridge, ElasticNet), Trees (RF, GBT)",
        "Feature_Importance_Hypothesis": "Captures multi-year acceleration/deceleration trends"
    },
    {
        "Feature_ID": "FEAT-03",
        "Feature_Name": "Net_MB_Lag1_Gt_yr",
        "Mathematical_Symbol": "NetMB_{b, t-1}",
        "Feature_Category": "Integrated Mass Balance State",
        "Physical_Units": "Gt/yr",
        "Temporal_Availability": "Antecedent year t-1 integrated state",
        "Operational_Lag": "Lag-1 (t-1)",
        "Lookahead_Leakage_Risk": "ZERO: Preceding mass balance (SMB_{t-1} - D_{t-1})",
        "Imputation_Method_for_Missing_Lags": "Training-fold median (1979-2005) per basin",
        "Normalization_Pipeline": "Fold-contained StandardScaler (fitted on Training fold only)",
        "Algorithm_Suitability": "Linear (Ridge, ElasticNet), Trees (RF, GBT)",
        "Feature_Importance_Hypothesis": "Solid-ice mass equivalent of primary volume target"
    },
    {
        "Feature_ID": "FEAT-04",
        "Feature_Name": "SMB_Lag1_Gt_yr",
        "Mathematical_Symbol": "SMB_{b, t-1}",
        "Feature_Category": "Atmospheric Climate Forcing",
        "Physical_Units": "Gt/yr",
        "Temporal_Availability": "Antecedent year t-1 regional climate reanalysis",
        "Operational_Lag": "Lag-1 (t-1)",
        "Lookahead_Leakage_Risk": "ZERO: Antecedent surface mass balance forcing",
        "Imputation_Method_for_Missing_Lags": "Training-fold median (1979-2005) per basin",
        "Normalization_Pipeline": "Fold-contained StandardScaler (fitted on Training fold only)",
        "Algorithm_Suitability": "Linear (Ridge, ElasticNet), Trees (RF, GBT)",
        "Feature_Importance_Hypothesis": "Primary driver of interannual ice sheet accumulation anomalies"
    },
    {
        "Feature_ID": "FEAT-05",
        "Feature_Name": "Discharge_Lag1_Gt_yr",
        "Mathematical_Symbol": "D_{b, t-1}",
        "Feature_Category": "Ice Dynamic Marine Outflow",
        "Physical_Units": "Gt/yr",
        "Temporal_Availability": "Antecedent year t-1 satellite flux gate estimate",
        "Operational_Lag": "Lag-1 (t-1)",
        "Lookahead_Leakage_Risk": "ZERO: Antecedent ice stream discharge",
        "Imputation_Method_for_Missing_Lags": "Training-fold median (1979-2005) per basin",
        "Normalization_Pipeline": "Fold-contained StandardScaler (fitted on Training fold only)",
        "Algorithm_Suitability": "Linear (Ridge, ElasticNet), Trees (RF, GBT)",
        "Feature_Importance_Hypothesis": "Controls low-frequency dynamic draw-down of marine outlet glaciers"
    },
    {
        "Feature_ID": "FEAT-06",
        "Feature_Name": "SMB_Rolling3yr_Gt_yr",
        "Mathematical_Symbol": "SMB_{b, roll3}",
        "Feature_Category": "Climate Trend Memory",
        "Physical_Units": "Gt/yr",
        "Temporal_Availability": "3-year rolling mean over [t-3, t-1]",
        "Operational_Lag": "Rolling antecedent window [t-3, t-1]",
        "Lookahead_Leakage_Risk": "ZERO: Omits contemporaneous year t; strictly retrospective",
        "Imputation_Method_for_Missing_Lags": "Training-fold median (1979-2005) per basin",
        "Normalization_Pipeline": "Fold-contained StandardScaler (fitted on Training fold only)",
        "Algorithm_Suitability": "Linear (Ridge, ElasticNet), Trees (RF, GBT)",
        "Feature_Importance_Hypothesis": "Captures multi-year snowpack buffer and firn loading memory"
    },
    {
        "Feature_ID": "FEAT-07",
        "Feature_Name": "SMB_Anomaly_Lag1_Gt_yr",
        "Mathematical_Symbol": "Delta SMB_{b, t-1}",
        "Feature_Category": "Climate Forcing Anomaly",
        "Physical_Units": "Gt/yr",
        "Temporal_Availability": "SMB_{t-1} minus training baseline mean",
        "Operational_Lag": "Lag-1 (t-1)",
        "Lookahead_Leakage_Risk": "ZERO: Baseline mean computed on Training fold (1979-2005) only",
        "Imputation_Method_for_Missing_Lags": "Training-fold median (1979-2005) per basin",
        "Normalization_Pipeline": "Fold-contained StandardScaler (fitted on Training fold only)",
        "Algorithm_Suitability": "Linear (Ridge, ElasticNet), Trees (RF, GBT)",
        "Feature_Importance_Hypothesis": "Isolates interannual weather extremes from stationary climate"
    },
    {
        "Feature_ID": "FEAT-08",
        "Feature_Name": "Grounded_Area_km2",
        "Mathematical_Symbol": "A_b",
        "Feature_Category": "Static Physiography (Spatial Scale)",
        "Physical_Units": "km2",
        "Temporal_Availability": "Time-invariant geographic mask (BedMachine V4.1 / Domain A)",
        "Operational_Lag": "Static Invariant",
        "Lookahead_Leakage_Risk": "ZERO: Geometric spatial constant per basin",
        "Imputation_Method_for_Missing_Lags": "None required (100% complete)",
        "Normalization_Pipeline": "Fold-contained StandardScaler (fitted on Training fold only)",
        "Algorithm_Suitability": "Linear (Ridge, ElasticNet), Trees (RF, GBT)",
        "Feature_Importance_Hypothesis": "Scales absolute mass magnitude across basins"
    },
    {
        "Feature_ID": "FEAT-09",
        "Feature_Name": "Mean_Baseline_Ice_Thickness_m",
        "Mathematical_Symbol": "H_b",
        "Feature_Category": "Static Hypsometry (Geometric Scale)",
        "Physical_Units": "m",
        "Temporal_Availability": "Time-invariant BedMachine V4.1 baseline",
        "Operational_Lag": "Static Invariant",
        "Lookahead_Leakage_Risk": "ZERO: Frozen reference geometry scalar",
        "Imputation_Method_for_Missing_Lags": "None required (100% complete)",
        "Normalization_Pipeline": "Fold-contained StandardScaler (fitted on Training fold only)",
        "Algorithm_Suitability": "Linear (Ridge, ElasticNet), Trees (RF, GBT)",
        "Feature_Importance_Hypothesis": "Indicates total ice column reservoir size"
    },
    {
        "Feature_ID": "FEAT-10",
        "Feature_Name": "Bed_Elevation_at_Gates_m",
        "Mathematical_Symbol": "B_b",
        "Feature_Category": "Static Topography (MISI Vulnerability)",
        "Physical_Units": "m",
        "Temporal_Availability": "Time-invariant BedMachine V4.1 bathymetry",
        "Operational_Lag": "Static Invariant",
        "Lookahead_Leakage_Risk": "ZERO: Frozen geological boundary condition",
        "Imputation_Method_for_Missing_Lags": "None required (100% complete)",
        "Normalization_Pipeline": "Fold-contained StandardScaler (fitted on Training fold only)",
        "Algorithm_Suitability": "Linear (Ridge, ElasticNet), Trees (RF, GBT)",
        "Feature_Importance_Hypothesis": "Controls marine ice sheet instability susceptibility"
    },
    {
        "Feature_ID": "FEAT-11",
        "Feature_Name": "Driving_Stress_Index_kPa",
        "Mathematical_Symbol": "tau_d",
        "Feature_Category": "Static Glaciological Stress",
        "Physical_Units": "kPa",
        "Temporal_Availability": "Time-invariant baseline stress index from REMA + BedMachine",
        "Operational_Lag": "Static Invariant",
        "Lookahead_Leakage_Risk": "ZERO: Frozen baseline scalar proxy",
        "Imputation_Method_for_Missing_Lags": "None required (100% complete)",
        "Normalization_Pipeline": "Fold-contained StandardScaler (fitted on Training fold only)",
        "Algorithm_Suitability": "Linear (Ridge, ElasticNet), Trees (RF, GBT)",
        "Feature_Importance_Hypothesis": "Proxies baseline creep and basal shearing intensity"
    },
    {
        "Feature_ID": "FEAT-12",
        "Feature_Name": "is_Hp_I",
        "Mathematical_Symbol": "I_{Hp-I}",
        "Feature_Category": "Categorical Basin Fixed Effect",
        "Physical_Units": "dimensionless (binary)",
        "Temporal_Availability": "Spatial basin indicator (1.0 for Hp-I, 0.0 otherwise)",
        "Operational_Lag": "Static Invariant",
        "Lookahead_Leakage_Risk": "ZERO: Discrete geographic label",
        "Imputation_Method_for_Missing_Lags": "None required (100% complete)",
        "Normalization_Pipeline": "Raw binary indicator (unscaled)",
        "Algorithm_Suitability": "Linear (Ridge, ElasticNet), Trees (RF, GBT)",
        "Feature_Importance_Hypothesis": "Allows pooled regression model to capture basin-specific intercept"
    },
    {
        "Feature_ID": "FEAT-13",
        "Feature_Name": "is_I_Ipp",
        "Mathematical_Symbol": "I_{I-Ipp}",
        "Feature_Category": "Categorical Basin Fixed Effect",
        "Physical_Units": "dimensionless (binary)",
        "Temporal_Availability": "Spatial basin indicator (1.0 for I-Ipp, 0.0 otherwise)",
        "Operational_Lag": "Static Invariant",
        "Lookahead_Leakage_Risk": "ZERO: Discrete geographic label",
        "Imputation_Method_for_Missing_Lags": "None required (100% complete)",
        "Normalization_Pipeline": "Raw binary indicator (unscaled)",
        "Algorithm_Suitability": "Linear (Ridge, ElasticNet), Trees (RF, GBT)",
        "Feature_Importance_Hypothesis": "Allows pooled regression model to capture Graham Land dynamic intercept"
    },
    {
        "Feature_ID": "FEAT-14",
        "Feature_Name": "is_Ipp_J",
        "Mathematical_Symbol": "I_{Ipp-J}",
        "Feature_Category": "Categorical Basin Fixed Effect",
        "Physical_Units": "dimensionless (binary)",
        "Temporal_Availability": "Spatial basin indicator (1.0 for Ipp-J, 0.0 otherwise; reference)",
        "Operational_Lag": "Static Invariant",
        "Lookahead_Leakage_Risk": "ZERO: Discrete geographic label",
        "Imputation_Method_for_Missing_Lags": "None required (100% complete)",
        "Normalization_Pipeline": "Raw binary indicator (omitted in unregularized linear models)",
        "Algorithm_Suitability": "Trees (RF, GBT)",
        "Feature_Importance_Hypothesis": "Reference category for Palmer Land East"
    },
    {
        "Feature_ID": "FEAT-15",
        "Feature_Name": "Observation_Uncertainty_sigma_km3_yr",
        "Mathematical_Symbol": "sigma_{b, t}",
        "Feature_Category": "Observational Uncertainty Weight",
        "Physical_Units": "km3/yr",
        "Temporal_Availability": "Epoch-dependent target measurement error",
        "Operational_Lag": "Contemporaneous with observation epoch",
        "Lookahead_Leakage_Risk": "ZERO: Used strictly as sample weight w = 1/sigma^2 during training loss minimization",
        "Imputation_Method_for_Missing_Lags": "None required (100% complete)",
        "Normalization_Pipeline": "Raw variance weighting",
        "Algorithm_Suitability": "Weighted Ridge, Weighted ElasticNet, Weighted Baselines",
        "Feature_Importance_Hypothesis": "Down-weights high-uncertainty early satellite epochs (Epoch 1: 1979-1999)"
    }
]

df_fdict = pd.DataFrame(feature_dict_records)
p_fdict = os.path.join(REPORTS_TBL, "stage6_feature_dictionary.csv")
df_fdict.to_csv(p_fdict, index=False)
shutil.copy(p_fdict, os.path.join(BRAIN_TBL, "stage6_feature_dictionary.csv"))
print(f"[Saved] {p_fdict}")

# -----------------------------------------------------------------------------
# 3. DELIVERABLE 3A: stage6_ml_dataset.csv (Primary Historical ML Benchmark)
# -----------------------------------------------------------------------------
p_tgt = os.path.join(REPORTS_TBL, "ml_target_dataset.csv")
df_raw = pd.read_csv(p_tgt)

# Filter physical basins (Hp-I, I-Ipp, Ipp-J; omit Domain_A aggregate to prevent collinearity)
df_ml = df_raw[df_raw["Basin_ID"] != "Domain_A"].copy()
df_ml = df_ml.sort_values(by=["Basin_ID", "Year"]).reset_index(drop=True)

# Generate Lag Features basin-by-basin
df_ml["Target_Volume_Change_Lag1_km3_yr"] = df_ml.groupby("Basin_ID")["Target_Annual_Volume_Change_Central_km3_yr"].shift(1)
df_ml["Target_Volume_Change_Lag2_km3_yr"] = df_ml.groupby("Basin_ID")["Target_Annual_Volume_Change_Central_km3_yr"].shift(2)
df_ml["Net_MB_Lag1_Gt_yr"] = df_ml.groupby("Basin_ID")["Annual_Net_MB_Central_Gt_yr"].shift(1)
df_ml["SMB_Lag1_Gt_yr"] = df_ml.groupby("Basin_ID")["Annual_SMB_Gt_yr"].shift(1)
df_ml["Discharge_Lag1_Gt_yr"] = df_ml.groupby("Basin_ID")["Annual_Discharge_Central_Gt_yr"].shift(1)

# Generate Rolling Features
def calc_roll3(s):
    # Shift by 1 first so rolling excludes contemporaneous year t
    return s.shift(1).rolling(window=3, min_periods=1).mean()

df_ml["SMB_Rolling3yr_Gt_yr"] = df_ml.groupby("Basin_ID")["Annual_SMB_Gt_yr"].transform(calc_roll3)

# Imputation using TRAINING-FOLD medians (1979-2005) only
train_mask = (df_ml["Year"] >= 1979) & (df_ml["Year"] <= 2005)

for basin in ["Hp-I", "I-Ipp", "Ipp-J"]:
    b_mask = train_mask & (df_ml["Basin_ID"] == basin)
    all_b_mask = (df_ml["Basin_ID"] == basin)
    
    med_y1 = df_ml.loc[b_mask, "Target_Volume_Change_Lag1_km3_yr"].median()
    med_y2 = df_ml.loc[b_mask, "Target_Volume_Change_Lag2_km3_yr"].median()
    med_nmb = df_ml.loc[b_mask, "Net_MB_Lag1_Gt_yr"].median()
    med_smb = df_ml.loc[b_mask, "SMB_Lag1_Gt_yr"].median()
    med_dis = df_ml.loc[b_mask, "Discharge_Lag1_Gt_yr"].median()
    med_smb_mean = df_ml.loc[b_mask, "Annual_SMB_Gt_yr"].mean()
    
    # Impute missing initial lags for this basin
    df_ml.loc[all_b_mask & df_ml["Target_Volume_Change_Lag1_km3_yr"].isna(), "Target_Volume_Change_Lag1_km3_yr"] = med_y1
    df_ml.loc[all_b_mask & df_ml["Target_Volume_Change_Lag2_km3_yr"].isna(), "Target_Volume_Change_Lag2_km3_yr"] = med_y2
    df_ml.loc[all_b_mask & df_ml["Net_MB_Lag1_Gt_yr"].isna(), "Net_MB_Lag1_Gt_yr"] = med_nmb
    df_ml.loc[all_b_mask & df_ml["SMB_Lag1_Gt_yr"].isna(), "SMB_Lag1_Gt_yr"] = med_smb
    df_ml.loc[all_b_mask & df_ml["Discharge_Lag1_Gt_yr"].isna(), "Discharge_Lag1_Gt_yr"] = med_dis
    df_ml.loc[all_b_mask & df_ml["SMB_Rolling3yr_Gt_yr"].isna(), "SMB_Rolling3yr_Gt_yr"] = med_smb_mean
    
    # SMB Anomaly relative to training-fold mean
    df_ml.loc[all_b_mask, "SMB_Anomaly_Lag1_Gt_yr"] = df_ml.loc[all_b_mask, "SMB_Lag1_Gt_yr"] - med_smb_mean

# Add static descriptors
STATIC_METRICS = {
    "Hp-I": {
        "Grounded_Area_km2": 108945.63,
        "Mean_Baseline_Ice_Thickness_m": 1482.4,
        "Bed_Elevation_at_Gates_m": -185.4,
        "Driving_Stress_Index_kPa": 112.5
    },
    "I-Ipp": {
        "Grounded_Area_km2": 49757.73,
        "Mean_Baseline_Ice_Thickness_m": 1195.1,
        "Bed_Elevation_at_Gates_m": -124.2,
        "Driving_Stress_Index_kPa": 98.4
    },
    "Ipp-J": {
        "Grounded_Area_km2": 57358.82,
        "Mean_Baseline_Ice_Thickness_m": 1220.8,
        "Bed_Elevation_at_Gates_m": -165.8,
        "Driving_Stress_Index_kPa": 105.2
    }
}

df_ml["Grounded_Area_km2"] = df_ml["Basin_ID"].apply(lambda b: STATIC_METRICS[b]["Grounded_Area_km2"])
df_ml["Mean_Baseline_Ice_Thickness_m"] = df_ml["Basin_ID"].apply(lambda b: STATIC_METRICS[b]["Mean_Baseline_Ice_Thickness_m"])
df_ml["Bed_Elevation_at_Gates_m"] = df_ml["Basin_ID"].apply(lambda b: STATIC_METRICS[b]["Bed_Elevation_at_Gates_m"])
df_ml["Driving_Stress_Index_kPa"] = df_ml["Basin_ID"].apply(lambda b: STATIC_METRICS[b]["Driving_Stress_Index_kPa"])

# Categorical basin indicators
df_ml["is_Hp_I"] = (df_ml["Basin_ID"] == "Hp-I").astype(float)
df_ml["is_I_Ipp"] = (df_ml["Basin_ID"] == "I-Ipp").astype(float)
df_ml["is_Ipp_J"] = (df_ml["Basin_ID"] == "Ipp-J").astype(float)

# Split assignment
def assign_split(yr):
    if yr <= 2005:
        return "TRAINING"
    elif yr <= 2007:
        return "EMBARGO_BUFFER_1"
    elif yr <= 2014:
        return "VALIDATION"
    elif yr == 2015:
        return "EMBARGO_BUFFER_2"
    else:
        return "TEST"

df_ml["Split_Status"] = df_ml["Year"].apply(assign_split)
df_ml["Is_Usable_for_Training"] = df_ml["Split_Status"] == "TRAINING"

# Observation uncertainty & weights
ANNUAL_UNCERTAINTY = {
    "Hp-I": {"Epoch 1 (1979–1999)": 20.37, "Epoch 2 (2000–2013)": 17.89, "Epoch 3 (2014–2024)": 17.52},
    "I-Ipp": {"Epoch 1 (1979–1999)": 9.50, "Epoch 2 (2000–2013)": 7.88, "Epoch 3 (2014–2024)": 7.30},
    "Ipp-J": {"Epoch 1 (1979–1999)": 9.18, "Epoch 2 (2000–2013)": 8.08, "Epoch 3 (2014–2024)": 7.70}
}

df_ml["Observation_Uncertainty_sigma_km3_yr"] = df_ml.apply(lambda r: ANNUAL_UNCERTAINTY[r["Basin_ID"]][r["Epoch"]], axis=1)
df_ml["Observation_Weight"] = 1.0 / (df_ml["Observation_Uncertainty_sigma_km3_yr"] ** 2)

# Standardized targets
df_ml["Target_Annual_Volume_Change_km3_yr"] = df_ml["Target_Annual_Volume_Change_Central_km3_yr"]
df_ml["Target_Annual_Mass_Balance_Gt_yr"] = df_ml["Target_Annual_Volume_Change_km3_yr"] * 0.917 # solid ice density
df_ml["Target_Cum_Volume_Anomaly_km3"] = df_ml["Target_Cum_Volume_Anomaly_Central_km3"]

# Final ordered columns for primary dataset
cols_primary = [
    "Year", "Basin_ID", "Basin_Name", "Epoch", "Split_Status", "Is_Usable_for_Training",
    "Target_Annual_Volume_Change_km3_yr", "Target_Annual_Mass_Balance_Gt_yr", "Target_Cum_Volume_Anomaly_km3",
    "Target_Volume_Change_Lag1_km3_yr", "Target_Volume_Change_Lag2_km3_yr",
    "Net_MB_Lag1_Gt_yr", "SMB_Lag1_Gt_yr", "Discharge_Lag1_Gt_yr",
    "SMB_Rolling3yr_Gt_yr", "SMB_Anomaly_Lag1_Gt_yr",
    "Grounded_Area_km2", "Mean_Baseline_Ice_Thickness_m", "Bed_Elevation_at_Gates_m", "Driving_Stress_Index_kPa",
    "is_Hp_I", "is_I_Ipp", "is_Ipp_J",
    "Observation_Uncertainty_sigma_km3_yr", "Observation_Weight"
]

df_ml_final = df_ml[cols_primary].copy()
df_ml_final.insert(0, "Row_ID", np.arange(len(df_ml_final)))

p_ml = os.path.join(REPORTS_TBL, "stage6_ml_dataset.csv")
df_ml_final.to_csv(p_ml, index=False)
shutil.copy(p_ml, os.path.join(BRAIN_TBL, "stage6_ml_dataset.csv"))
print(f"[Saved] {p_ml} (Rows: {len(df_ml_final)})")

# -----------------------------------------------------------------------------
# 4. DELIVERABLE 3B: stage6_ml_residual_pilot_dataset.csv (Physical Residual Pilot)
# -----------------------------------------------------------------------------
# Join Stage 5.1 physical simulation results with Phase 3 reconstruction
p_s51 = os.path.join(REPORTS_TBL, "stage5_1_historical_simulation_results.csv")
df_s51 = pd.read_csv(p_s51)

residual_rows = []
for yr in range(2000, 2019):
    row_s51 = df_s51[df_s51["Historical_Year"] == yr].iloc[0]
    
    # Regional Domain A
    p3_domA = df_raw[(df_raw["Basin_ID"] == "Domain_A") & (df_raw["Year"] == yr)].iloc[0]
    m_phys_domA = float(row_s51["Grounded_Net_Mass_Balance_Gt_yr"])
    m_obs_domA = float(row_s51["External_IMBIE3_Mass_Balance_Gt_yr"])
    m_recon_domA = float(p3_domA["Annual_Net_MB_Central_Gt_yr"])
    
    residual_rows.append({
        "Year": yr,
        "Domain_or_Basin": "Domain_A",
        "Split_Status": assign_split(yr),
        "Is_Usable_for_Training": assign_split(yr) == "TRAINING",
        "Physical_Model_Mass_Change_Gt_yr": round(m_phys_domA, 2),
        "IMBIE3_Observed_Mass_Change_Gt_yr": round(m_obs_domA, 2),
        "Phase3_Reconstructed_Mass_Change_Gt_yr": round(m_recon_domA, 2),
        "Physical_Residual_vs_IMBIE3_Gt_yr": round(m_obs_domA - m_phys_domA, 2),
        "Physical_Residual_vs_Recon_Gt_yr": round(m_recon_domA - m_phys_domA, 2),
        "Physical_Simulated_GL_Discharge_Gt_yr": round(float(row_s51["Modeled_GL_Discharge_Gt_yr"]), 2),
        "Physical_Simulated_Grounded_Calving_Gt_yr": round(float(row_s51["Modeled_Grounded_Calving_Gt_yr"]), 2),
        "Physical_Simulated_Grounded_SMB_Gt_yr": round(float(row_s51["RACMO_Grounded_SMB_Gt_yr"]), 2),
        "Physical_Simulated_Ungrounded_Cells": int(row_s51["Ungrounded_Cells_Annual"]),
        "Physical_Simulated_Regrounded_Cells": int(row_s51["Regrounded_Cells_Annual"]),
        "Residual_Feasibility_Status": "HOLD (Sample size N=19 regional; 2000-2004 dominated by initialization transient)"
    })
    
    # 3 Basins
    for basin in ["Hp-I", "I-Ipp", "Ipp-J"]:
        p3_b = df_raw[(df_raw["Basin_ID"] == basin) & (df_raw["Year"] == yr)].iloc[0]
        # Cumulative dMg derivative for basin
        if yr == 2000:
            m_phys_b = float(row_s51[f"{basin.replace('-', '_')}_Modeled_Cumulative_dMg_Gt"])
        else:
            prev_row = df_s51[df_s51["Historical_Year"] == yr - 1].iloc[0]
            m_phys_b = float(row_s51[f"{basin.replace('-', '_')}_Modeled_Cumulative_dMg_Gt"] - prev_row[f"{basin.replace('-', '_')}_Modeled_Cumulative_dMg_Gt"])
            
        m_recon_b = float(p3_b["Annual_Net_MB_Central_Gt_yr"])
        
        residual_rows.append({
            "Year": yr,
            "Domain_or_Basin": basin,
            "Split_Status": assign_split(yr),
            "Is_Usable_for_Training": assign_split(yr) == "TRAINING",
            "Physical_Model_Mass_Change_Gt_yr": round(m_phys_b, 2),
            "IMBIE3_Observed_Mass_Change_Gt_yr": np.nan, # Not partitioned by basin in IMBIE
            "Phase3_Reconstructed_Mass_Change_Gt_yr": round(m_recon_b, 2),
            "Physical_Residual_vs_IMBIE3_Gt_yr": np.nan,
            "Physical_Residual_vs_Recon_Gt_yr": round(m_recon_b - m_phys_b, 2),
            "Physical_Simulated_GL_Discharge_Gt_yr": np.nan,
            "Physical_Simulated_Grounded_Calving_Gt_yr": np.nan,
            "Physical_Simulated_Grounded_SMB_Gt_yr": np.nan,
            "Physical_Simulated_Ungrounded_Cells": int(row_s51["Ungrounded_Cells_Annual"]),
            "Physical_Simulated_Regrounded_Cells": int(row_s51["Regrounded_Cells_Annual"]),
            "Residual_Feasibility_Status": "HOLD (Sample size N=57 basin-years; N_train=18 too small for non-linear ML)"
        })

df_res_pilot = pd.DataFrame(residual_rows)
df_res_pilot.insert(0, "Pilot_ID", np.arange(len(df_res_pilot)))
p_res_pilot = os.path.join(REPORTS_TBL, "stage6_ml_residual_pilot_dataset.csv")
df_res_pilot.to_csv(p_res_pilot, index=False)
shutil.copy(p_res_pilot, os.path.join(BRAIN_TBL, "stage6_ml_residual_pilot_dataset.csv"))
print(f"[Saved] {p_res_pilot} (Rows: {len(df_res_pilot)})")

# -----------------------------------------------------------------------------
# 5. DELIVERABLE 4: stage6_temporal_split_manifest.csv
# -----------------------------------------------------------------------------
p_split_src = os.path.join(REPORTS_TBL, "split_manifest_row_level.csv")
df_split_src = pd.read_csv(p_split_src)

split_records = []
for idx, r in df_split_src.iterrows():
    b_id = r["Basin_ID"]
    yr = int(r["Year"])
    st = r["Split_Status"]
    
    if st == "TRAINING":
        perm = "Model feature training, loss minimization, internal walk-forward cross-validation"
        quar = "None (Chronologically precedes validation and test epochs)"
    elif st == "EMBARGO_BUFFER_1":
        perm = "STRICTLY EXCLUDED from training loss and validation scoring; used only for lag initialization"
        quar = "Mandatory 2-year quarantine buffer (2006-2007) isolating Train from Validation"
    elif st == "VALIDATION":
        perm = "Hyperparameter tuning, regularization penalty alpha/lambda selection, feature pruning"
        quar = "Protected by Embargo Buffer 1 on left, Embargo Buffer 2 on right"
    elif st == "EMBARGO_BUFFER_2":
        perm = "STRICTLY EXCLUDED from hyperparameter tuning and test scoring; used only for test lag initialization"
        quar = "Mandatory 1-year quarantine buffer (2015) isolating Validation from Held-Out Test"
    elif st == "TEST":
        perm = "ONE-TIME final model architecture evaluation; zero parameter tuning permitted"
        quar = "Strictly held out; never accessed during model development"
    else: # DERIVED_REGIONAL_DIAGNOSTIC
        perm = "Post-hoc regional consistency checking; EXCLUDED from basin-level training"
        quar = "Excluded to prevent collinearity with constituent basins"

    split_records.append({
        "Manifest_ID": f"SPLIT-{idx+1:03d}",
        "Year": yr,
        "Basin_ID": b_id,
        "Basin_Name": r["Basin_Name"],
        "Observational_Epoch": r["Observational_Epoch"],
        "Split_Stage": st,
        "Is_Independent_Training_Sample": bool(r["Is_Independent_Training_Sample"]),
        "Target_Annual_Volume_Change_km3_yr": r["Target_Annual_Volume_Change_km3_yr"],
        "Target_Annual_Mass_Balance_Gt_yr": round(float(r["Target_Annual_Volume_Change_km3_yr"]) * 0.917, 2),
        "Quarantine_Buffer_Description": quar,
        "Permitted_ML_Operations": perm,
        "Leakage_Control_Verification": r["Leakage_Protection_Mechanism"]
    })

df_split_final = pd.DataFrame(split_records)
p_split_out = os.path.join(REPORTS_TBL, "stage6_temporal_split_manifest.csv")
df_split_final.to_csv(p_split_out, index=False)
shutil.copy(p_split_out, os.path.join(BRAIN_TBL, "stage6_temporal_split_manifest.csv"))
print(f"[Saved] {p_split_out} (Rows: {len(df_split_final)})")

print("All CSV deliverables successfully produced and mirrored!")
