"""
Feature Engineering and Whitelist Builder
=========================================
Implements leakage-controlled retrospective hindcast features for Task A2.
Ensures zero contemporaneous target reconstruction and fold-contained transformations.
"""

import os
import pandas as pd
import numpy as np

STATIC_DESCRIPTORS = {
    "Hp-I": {
        "Grounded_Area_km2": 53883.0,
        "Mean_Baseline_Ice_Thickness_m": 1482.4,
        "Bed_Elevation_at_Gates_m": -185.4,
        "Driving_Stress_Index_kPa": 112.5
    },
    "I-Ipp": {
        "Grounded_Area_km2": 23178.0,
        "Mean_Baseline_Ice_Thickness_m": 1195.1,
        "Bed_Elevation_at_Gates_m": -124.2,
        "Driving_Stress_Index_kPa": 98.4
    },
    "Ipp-J": {
        "Grounded_Area_km2": 26898.0,
        "Mean_Baseline_Ice_Thickness_m": 1220.8,
        "Bed_Elevation_at_Gates_m": -165.8,
        "Driving_Stress_Index_kPa": 105.2
    }
}

ANNUAL_BASIN_UNCERTAINTY = {
    "Hp-I": {
        "Epoch 1 (1979–1999)": 20.37,
        "Epoch 2 (2000–2013)": 17.89,
        "Epoch 3 (2014–2024)": 17.52
    },
    "I-Ipp": {
        "Epoch 1 (1979–1999)": 9.50,
        "Epoch 2 (2000–2013)": 7.88,
        "Epoch 3 (2014–2024)": 7.30
    },
    "Ipp-J": {
        "Epoch 1 (1979–1999)": 9.18,
        "Epoch 2 (2000–2013)": 8.08,
        "Epoch 3 (2014–2024)": 7.70
    }
}

def build_feature_dataset(base_dir):
    """
    Constructs the feature dataset from reports/tables/ml_target_dataset.csv
    applying strict lag-1 and lag-2 structures.
    """
    tables_dir = os.path.join(base_dir, "reports", "tables")
    target_path = os.path.join(tables_dir, "ml_target_dataset.csv")
    raw_df = pd.read_csv(target_path)
    
    # Filter physical basins only
    df = raw_df[raw_df["Basin_ID"] != "Domain_A"].copy()
    df.sort_values(by=["Basin_ID", "Year"], inplace=True)
    df.reset_index(drop=True, inplace=True)
    
    # Construct lagged features basin-by-basin
    df["Target_Volume_Change_Lag1_km3_yr"] = df.groupby("Basin_ID")["Target_Annual_Volume_Change_Central_km3_yr"].shift(1)
    df["Target_Volume_Change_Lag2_km3_yr"] = df.groupby("Basin_ID")["Target_Annual_Volume_Change_Central_km3_yr"].shift(2)
    df["SMB_Lag1_Gt_yr"] = df.groupby("Basin_ID")["Annual_SMB_Gt_yr"].shift(1)
    df["Discharge_Lag1_Gt_yr"] = df.groupby("Basin_ID")["Annual_Discharge_Central_Gt_yr"].shift(1)
    df["Net_MB_Lag1_Gt_yr"] = df.groupby("Basin_ID")["Annual_Net_MB_Central_Gt_yr"].shift(1)
    
    # Add verified static descriptors
    df["Grounded_Area_km2"] = df["Basin_ID"].apply(lambda b: STATIC_DESCRIPTORS[b]["Grounded_Area_km2"])
    df["Mean_Baseline_Ice_Thickness_m"] = df["Basin_ID"].apply(lambda b: STATIC_DESCRIPTORS[b]["Mean_Baseline_Ice_Thickness_m"])
    df["Bed_Elevation_at_Gates_m"] = df["Basin_ID"].apply(lambda b: STATIC_DESCRIPTORS[b]["Bed_Elevation_at_Gates_m"])
    df["Driving_Stress_Index_kPa"] = df["Basin_ID"].apply(lambda b: STATIC_DESCRIPTORS[b]["Driving_Stress_Index_kPa"])
    
    # Add basin indicator features
    df["is_Hp_I"] = (df["Basin_ID"] == "Hp-I").astype(float)
    df["is_I_Ipp"] = (df["Basin_ID"] == "I-Ipp").astype(float)
    df["is_Ipp_J"] = (df["Basin_ID"] == "Ipp-J").astype(float)
    
    # Add annual observation rate uncertainty sigma_y and weight w = 1 / sigma_y^2
    def get_sigma(row):
        b = row["Basin_ID"]
        epoch = row["Epoch"]
        return ANNUAL_BASIN_UNCERTAINTY[b][epoch]
        
    df["Observation_Uncertainty_sigma_km3_yr"] = df.apply(get_sigma, axis=1)
    df["Observation_Weight"] = 1.0 / (df["Observation_Uncertainty_sigma_km3_yr"] ** 2)
    
    # Target variable alias
    df["y_target"] = df["Target_Annual_Volume_Change_Central_km3_yr"]
    
    return df

def get_feature_subsets():
    """
    Returns feature column lists for different model candidate architectures.
    """
    # Primary full feature set (p=10)
    full_features = [
        "Target_Volume_Change_Lag1_km3_yr",
        "Target_Volume_Change_Lag2_km3_yr",
        "SMB_Lag1_Gt_yr",
        "Discharge_Lag1_Gt_yr",
        "Net_MB_Lag1_Gt_yr",
        "Grounded_Area_km2",
        "Mean_Baseline_Ice_Thickness_m",
        "Bed_Elevation_at_Gates_m",
        "Driving_Stress_Index_kPa",
        "is_Hp_I",
        "is_I_Ipp"
    ]
    
    # GPR restricted low-dimensional feature set (p <= 4)
    gp_features = [
        "Target_Volume_Change_Lag1_km3_yr",
        "SMB_Lag1_Gt_yr",
        "Discharge_Lag1_Gt_yr",
        "Mean_Baseline_Ice_Thickness_m"
    ]
    
    return {
        "full_features": full_features,
        "gp_features": gp_features
    }

def generate_model_feature_manifest(base_dir):
    """
    Generates reports/tables/model_feature_manifest.csv documenting provenance,
    observation period, and availability status.
    """
    tables_dir = os.path.join(base_dir, "reports", "tables")
    manifest_records = [
        {
            "Feature_Name": "Target_Volume_Change_Lag1_km3_yr",
            "Mathematical_Symbol": "y_{b, t-1}",
            "Source_Dataset": "Reconstructed historical volume change series (Phase 3.2)",
            "Product_Version": "Phase 3.2 Central Realization",
            "Physical_Observation_Period": "Calendar year t-1",
            "Publication_Status": "Retrospective Research Product (Hindcast Emulation)",
            "Operational_Lag": "Lag-1 (t-1)",
            "Feature_Type": "Autoregressive Dynamic State",
            "Transformation_Pipeline": "Training fold median imputation for 1979; fold-contained StandardScaler",
            "Task_A2_Classification": "RETROSPECTIVE_HINDCAST_EMULATION",
            "Leakage_Control_Verification": "Strictly precedes prediction year t; 1979 missing lag imputed using training median"
        },
        {
            "Feature_Name": "Target_Volume_Change_Lag2_km3_yr",
            "Mathematical_Symbol": "y_{b, t-2}",
            "Source_Dataset": "Reconstructed historical volume change series (Phase 3.2)",
            "Product_Version": "Phase 3.2 Central Realization",
            "Physical_Observation_Period": "Calendar year t-2",
            "Publication_Status": "Retrospective Research Product (Hindcast Emulation)",
            "Operational_Lag": "Lag-2 (t-2)",
            "Feature_Type": "Autoregressive Dynamic State",
            "Transformation_Pipeline": "Training fold median imputation for 1979–1980; fold-contained StandardScaler",
            "Task_A2_Classification": "RETROSPECTIVE_HINDCAST_EMULATION",
            "Leakage_Control_Verification": "Strictly precedes prediction year t by 2 years"
        },
        {
            "Feature_Name": "SMB_Lag1_Gt_yr",
            "Mathematical_Symbol": "SMB_{b, t-1}",
            "Source_Dataset": "RACMO2.4p1 11km Regional Climate Model (ERA5-forced)",
            "Product_Version": "RACMO2.4p1 (Zenodo DOI: 10.5281/zenodo.10519398)",
            "Physical_Observation_Period": "Calendar year t-1",
            "Publication_Status": "Retrospective Reanalysis (Published Nov 2023)",
            "Operational_Lag": "Lag-1 (t-1)",
            "Feature_Type": "Atmospheric Climate Forcing",
            "Transformation_Pipeline": "Training fold median imputation; fold-contained StandardScaler",
            "Task_A2_Classification": "RETROSPECTIVE_HINDCAST_EMULATION",
            "Leakage_Control_Verification": "Strict lag-1 prevents algebraic recovery of same-year net mass balance"
        },
        {
            "Feature_Name": "Discharge_Lag1_Gt_yr",
            "Mathematical_Symbol": "D_{b, t-1}",
            "Source_Dataset": "Satellite flux gate compilation (ITS_LIVE v2 / MEaSUREs)",
            "Product_Version": "ITS_LIVE v2 / BedMachine V4.1",
            "Physical_Observation_Period": "Calendar year t-1",
            "Publication_Status": "Retrospective Satellite Compilation (6-18 mo latency)",
            "Operational_Lag": "Lag-1 (t-1)",
            "Feature_Type": "Glacier Dynamics Flux",
            "Transformation_Pipeline": "Training fold median imputation; fold-contained StandardScaler",
            "Task_A2_Classification": "RETROSPECTIVE_HINDCAST_EMULATION",
            "Leakage_Control_Verification": "Strict lag-1 prevents contemporaneous target reconstruction"
        },
        {
            "Feature_Name": "Net_MB_Lag1_Gt_yr",
            "Mathematical_Symbol": "Net_MB_{b, t-1}",
            "Source_Dataset": "Derived mass balance state (SMB_{t-1} - D_{t-1})",
            "Product_Version": "Phase 3.2 Derived State",
            "Physical_Observation_Period": "Calendar year t-1",
            "Publication_Status": "Retrospective Derived State",
            "Operational_Lag": "Lag-1 (t-1)",
            "Feature_Type": "Integrated Mass Balance State",
            "Transformation_Pipeline": "Training fold median imputation; fold-contained StandardScaler",
            "Task_A2_Classification": "RETROSPECTIVE_HINDCAST_EMULATION",
            "Leakage_Control_Verification": "Strict lag-1 preceding observation"
        },
        {
            "Feature_Name": "Grounded_Area_km2",
            "Mathematical_Symbol": "A_b",
            "Source_Dataset": "MEaSUREs Antarctic Boundaries IPY 2007–2009 / IMBIE 2016",
            "Product_Version": "NSIDC-0709 Version 2",
            "Physical_Observation_Period": "2007–2009 IPY baseline",
            "Publication_Status": "Published Static Boundary (2017)",
            "Operational_Lag": "Static Invariant",
            "Feature_Type": "Static Physiography (Scale Descriptor)",
            "Transformation_Pipeline": "Fold-contained StandardScaler",
            "Task_A2_Classification": "RETROSPECTIVE_HINDCAST_EMULATION",
            "Leakage_Control_Verification": "Time-invariant geographic mask; zero dynamic look-ahead leakage"
        },
        {
            "Feature_Name": "Mean_Baseline_Ice_Thickness_m",
            "Mathematical_Symbol": "H_b",
            "Source_Dataset": "MEaSUREs BedMachine Antarctica V4.1 / Bedmap3",
            "Product_Version": "NSIDC-0756 V04.1 (2026) / Bedmap3 (2025)",
            "Physical_Observation_Period": "Composite assimilation epoch (~1970–2019)",
            "Publication_Status": "Published Static Grids",
            "Operational_Lag": "Static Invariant",
            "Feature_Type": "Static Hypsometry (Geometric Scale)",
            "Transformation_Pipeline": "Fold-contained StandardScaler",
            "Task_A2_Classification": "RETROSPECTIVE_HINDCAST_EMULATION",
            "Leakage_Control_Verification": "Frozen baseline scalar; time-invariant"
        },
        {
            "Feature_Name": "Bed_Elevation_at_Gates_m",
            "Mathematical_Symbol": "B_b",
            "Source_Dataset": "BedMachine Antarctica V4.1 Bed Topography",
            "Product_Version": "NSIDC-0756 V04.1",
            "Physical_Observation_Period": "Geological bedrock compilation",
            "Publication_Status": "Published Static Grid",
            "Operational_Lag": "Static Invariant",
            "Feature_Type": "Static Topography (MISI Vulnerability)",
            "Transformation_Pipeline": "Fold-contained StandardScaler",
            "Task_A2_Classification": "RETROSPECTIVE_HINDCAST_EMULATION",
            "Leakage_Control_Verification": "Time-invariant geological boundary condition"
        },
        {
            "Feature_Name": "Driving_Stress_Index_kPa",
            "Mathematical_Symbol": "tau_d",
            "Source_Dataset": "REMA 100m DEM V1.1 + BedMachine V4.1",
            "Product_Version": "REMA V1.1 / NSIDC-0756 V04.1",
            "Physical_Observation_Period": "2011–2017 composite stereophotogrammetry",
            "Publication_Status": "Published Static Index",
            "Operational_Lag": "Static Invariant",
            "Feature_Type": "Static Glaciological Stress (Dynamic Sensitivity)",
            "Transformation_Pipeline": "Fold-contained StandardScaler",
            "Task_A2_Classification": "RETROSPECTIVE_HINDCAST_EMULATION",
            "Leakage_Control_Verification": "Frozen baseline scalar proxy"
        },
        {
            "Feature_Name": "Basin_Identity_Flags",
            "Mathematical_Symbol": "is_Hp_I, is_I_Ipp, is_Ipp_J",
            "Source_Dataset": "Drainage basin categorical delineation",
            "Product_Version": "Discrete indicator variables",
            "Physical_Observation_Period": "Stationary spatial unit",
            "Publication_Status": "Categorical Indicator",
            "Operational_Lag": "Static Invariant",
            "Feature_Type": "Categorical Basin Fixed Effect",
            "Transformation_Pipeline": "One-hot indicator (is_Hp_I, is_I_Ipp; reference = Ipp-J)",
            "Task_A2_Classification": "RETROSPECTIVE_HINDCAST_EMULATION",
            "Leakage_Control_Verification": "Enables pooled basin-aware regression without target leakage"
        }
    ]
    manifest_df = pd.DataFrame(manifest_records)
    out_path = os.path.join(tables_dir, "model_feature_manifest.csv")
    manifest_df.to_csv(out_path, index=False)
    print(f"Saved: {out_path} ({len(manifest_df)} rows)")
    return manifest_df

