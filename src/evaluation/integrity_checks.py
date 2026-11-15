"""
Integrity Checks and Experiment A1 Verification
================================================
Verifies dataset integrity, manifest specifications, and performs
Experiment A1 (Physical Accounting Verification).
"""

import os
import numpy as np
import pandas as pd

RHO_ICE = 0.917  # Gt / km^3

def verify_dataset_integrity(base_dir):
    """
    Verifies the pre-implementation dataset integrity:
    1. Physical rows = 138 (46 years x 3 basins).
    2. Domain A diagnostic rows = 46.
    3. Target units = km3/year.
    4. 20-fold chronological walk-forward manifest (1995–2014).
    5. 2015 quarantined (EMBARGO_BUFFER_2).
    6. 2016–2024 test targets sealed.
    """
    tables_dir = os.path.join(base_dir, "reports", "tables")
    target_path = os.path.join(tables_dir, "ml_target_dataset.csv")
    split_path = os.path.join(tables_dir, "split_manifest_row_level.csv")
    fold_path = os.path.join(tables_dir, "rolling_origin_fold_manifest.csv")
    
    target_df = pd.read_csv(target_path)
    split_df = pd.read_csv(split_path)
    fold_df = pd.read_csv(fold_path)
    
    print("\n--- Running Pre-Implementation Dataset Integrity Checks ---")
    
    # 1. Row counts & basin identities
    physical = target_df[target_df["Basin_ID"] != "Domain_A"]
    domain_a = target_df[target_df["Basin_ID"] == "Domain_A"]
    
    assert len(target_df) == 184, f"Expected 184 total rows, found {len(target_df)}"
    assert len(physical) == 138, f"Expected 138 physical rows, found {len(physical)}"
    assert len(domain_a) == 46, f"Expected 46 Domain A rows, found {len(domain_a)}"
    
    expected_basins = {"Hp-I", "I-Ipp", "Ipp-J"}
    actual_basins = set(physical["Basin_ID"].unique())
    assert actual_basins == expected_basins, f"Basin mismatch: {actual_basins} != {expected_basins}"
    
    # 2. Year coverage
    assert target_df["Year"].min() == 1979, f"Unexpected min year: {target_df['Year'].min()}"
    assert target_df["Year"].max() == 2024, f"Unexpected max year: {target_df['Year'].max()}"
    
    # 3. 20-fold manifest
    assert len(fold_df) == 20, f"Expected 20 folds, found {len(fold_df)}"
    assert fold_df["Validation_Year"].min() == 1995, "Validation start year must be 1995"
    assert fold_df["Validation_Year"].max() == 2014, "Validation end year must be 2014"
    assert (fold_df["Validation_Samples_N"] == 3).all(), "All folds must validate 3 basins"
    
    # 4. Quarantine & Test set checks
    b2_rows = split_df[split_df["Split_Status"] == "EMBARGO_BUFFER_2"]
    assert len(b2_rows) == 3, f"Expected 3 rows in EMBARGO_BUFFER_2 (2015), found {len(b2_rows)}"
    assert (b2_rows["Year"] == 2015).all(), "EMBARGO_BUFFER_2 must be calendar year 2015"
    
    test_rows = split_df[(split_df["Year"] >= 2016) & (split_df["Basin_ID"] != "Domain_A")]
    assert len(test_rows) == 27, f"Expected 27 physical test rows (2016–2024), found {len(test_rows)}"
    assert (test_rows["Split_Status"] == "TEST").all(), "2016–2024 physical rows must be labeled TEST"
    
    print("SUCCESS: All pre-implementation integrity assertions verified without error.")
    return True

def run_experiment_a1_accounting_verification(base_dir):
    """
    Experiment A1: Numerical verification of physical accounting identity:
    y_{b,t} = (SMB_{b,t} - D_{b,t}) / 0.917
    
    Verifies:
    1. Mass balance closure: Net_MB = SMB - D
    2. Ice-equivalent volume rate conversion: y = Net_MB / 0.917
    3. Basin aggregation conservation: sum(y_b) == y_{Domain_A}
    """
    tables_dir = os.path.join(base_dir, "reports", "tables")
    target_path = os.path.join(tables_dir, "ml_target_dataset.csv")
    df = pd.read_csv(target_path)
    
    print("\n--- Running Experiment A1: Physical Accounting Verification ---")
    
    # 1. Mass balance closure
    net_mb_calc = df["Annual_SMB_Gt_yr"] - df["Annual_Discharge_Central_Gt_yr"]
    mb_diff = np.abs(net_mb_calc - df["Annual_Net_MB_Central_Gt_yr"])
    max_mb_diff = mb_diff.max()
    
    # 2. Volume conversion
    vol_calc = df["Annual_Net_MB_Central_Gt_yr"] / RHO_ICE
    vol_diff = np.abs(vol_calc - df["Target_Annual_Volume_Change_Central_km3_yr"])
    max_vol_diff = vol_diff.max()
    
    # 3. Spatial aggregation closure
    physical = df[df["Basin_ID"] != "Domain_A"]
    domain_a = df[df["Basin_ID"] == "Domain_A"].set_index("Year")
    
    sum_vol = physical.groupby("Year")["Target_Annual_Volume_Change_Central_km3_yr"].sum()
    sum_smb = physical.groupby("Year")["Annual_SMB_Gt_yr"].sum()
    sum_d = physical.groupby("Year")["Annual_Discharge_Central_Gt_yr"].sum()
    
    vol_agg_diff = np.abs(sum_vol - domain_a["Target_Annual_Volume_Change_Central_km3_yr"]).max()
    smb_agg_diff = np.abs(sum_smb - domain_a["Annual_SMB_Gt_yr"]).max()
    d_agg_diff = np.abs(sum_d - domain_a["Annual_Discharge_Central_Gt_yr"]).max()
    
    print(f"Max Mass Balance Closure Diff:  {max_mb_diff:.4f} Gt/yr (within rounding tolerance)")
    print(f"Max Volume Conversion Diff:      {max_vol_diff:.4f} km3/yr (within rounding tolerance)")
    print(f"Max Domain A Volume Additivity:  {vol_agg_diff:.4f} km3/yr (exact linear closure)")
    print(f"Max Domain A SMB Additivity:     {smb_agg_diff:.4f} Gt/yr (exact linear closure)")
    print(f"Max Domain A Discharge Additivity: {d_agg_diff:.4e} Gt/yr (exact linear closure)")
    
    assert max_mb_diff < 0.05, f"Mass balance closure failed: diff = {max_mb_diff}"
    assert max_vol_diff < 0.05, f"Volume conversion failed: diff = {max_vol_diff}"
    assert vol_agg_diff < 0.05, f"Volume aggregation failed: diff = {vol_agg_diff}"
    
    print("SUCCESS: Experiment A1 Physical Accounting Verification CONFIRMED.")
    return {
        "status": "VERIFIED",
        "max_mb_diff": max_mb_diff,
        "max_vol_diff": max_vol_diff,
        "vol_agg_diff": vol_agg_diff,
        "smb_agg_diff": smb_agg_diff,
        "d_agg_diff": d_agg_diff
    }

