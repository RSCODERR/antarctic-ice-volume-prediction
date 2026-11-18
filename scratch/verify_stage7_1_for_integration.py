import os
import json
import joblib
import pandas as pd
import numpy as np

def run_pre_integration_verification():
    base_dir = "antarctic-ice-volume-prediction"
    proj_csv = os.path.join(base_dir, "data/projections/stage7_1_future_projections_2015_2100.csv")
    train_csv = os.path.join(base_dir, "reports/tables/stage7_1_training_dataset.csv")
    meta_json = os.path.join(base_dir, "models/stage7_1_future_models/future_model_metadata.json")
    model_dir = os.path.join(base_dir, "models/stage7_1_future_models")
    comp_csv = os.path.join(base_dir, "reports/tables/stage7_1_model_comparison.csv")
    lomfo_csv = os.path.join(base_dir, "reports/tables/stage7_1_lomfo_validation.csv")

    print("================================================================================")
    print("STAGE 7.2 PRE-INTEGRATION VERIFICATION AUDIT")
    print("================================================================================")

    # 1. Inspect Projection Manifest
    print("\n--- 1. PROJECTION MANIFEST INSPECTION ---")
    df_proj = pd.read_csv(proj_csv)
    print(f"File: {proj_csv}")
    print(f"Total Rows: {len(df_proj)}")
    print(f"Columns: {list(df_proj.columns)}")
    
    # Check nulls
    null_counts = df_proj.isnull().sum()
    print(f"Null values per column:\n{null_counts[null_counts > 0] if (null_counts > 0).any() else 'None (0 nulls)'}")

    # Check unique combinations of Year, Scenario, Basin_ID
    combo_count = len(df_proj.groupby(['Year', 'Scenario', 'Basin_ID']))
    print(f"Unique (Year, Scenario, Basin_ID) combinations: {combo_count}")
    duplicates = df_proj.duplicated(subset=['Year', 'Scenario', 'Basin_ID']).sum()
    print(f"Duplicate records: {duplicates}")

    # Check basins
    basins = df_proj['Basin_ID'].unique().tolist()
    print(f"Basin IDs present: {basins}")
    expected_basins = ['Hp-I', 'I-Ipp', 'Ipp-J', 'Domain_A']
    assert set(basins) == set(expected_basins), f"Basins mismatch: {basins} vs {expected_basins}"

    # Check scenarios and watermarks
    scenarios = df_proj['Scenario'].unique().tolist()
    print(f"Scenarios present: {scenarios}")
    scenario_types = df_proj.groupby(['Scenario', 'Scenario_Type']).size().reset_index(name='Count')
    print("Scenario Watermarks:")
    print(scenario_types.to_string(index=False))

    # Check years
    years = sorted(df_proj['Year'].unique().tolist())
    print(f"Years range: {min(years)} to {max(years)} (Total: {len(years)} years)")
    expected_years = list(range(2015, 2101))
    assert years == expected_years, f"Years mismatch: {len(years)} vs {len(expected_years)}"
    
    expected_total_rows = len(expected_basins) * len(scenarios) * len(expected_years)
    print(f"Expected total rows: {len(expected_basins)} basins * {len(scenarios)} scenarios * {len(expected_years)} years = {expected_total_rows}")
    assert len(df_proj) == expected_total_rows, f"Row count mismatch: {len(df_proj)} vs {expected_total_rows}"

    # Check Quantile Ordering
    print("\n--- 2. QUANTILE ORDERING AUDIT ---")
    # For VAF: q10 <= q16 <= q50 <= q84 <= q90
    vaf_violations = []
    for idx, row in df_proj.iterrows():
        q10 = row['Delta_VAF_10th_km3']
        q16 = row['Delta_VAF_16th_km3']
        q50 = row['Delta_VAF_Median_km3']
        q84 = row['Delta_VAF_84th_km3']
        q90 = row['Delta_VAF_90th_km3']
        if not (q10 <= q16 <= q50 <= q84 <= q90):
            vaf_violations.append((row['Year'], row['Scenario'], row['Basin_ID'], q10, q16, q50, q84, q90))
    print(f"VAF Quantile Ordering (q10 <= q16 <= q50 <= q84 <= q90) violations: {len(vaf_violations)}")
    if vaf_violations:
        print(f"Sample violation: {vaf_violations[0]}")

    # Check SLE arithmetic: SLE = - (Delta_VAF * 0.917) / 361.8
    # Note: What about SLE quantiles?
    # When VAF decreases (e.g. -100 km3), ice is lost, so SLE is positive: -(-100 * 0.917) / 361.8 = +0.253 mm.
    # Let's inspect the relationship between Delta_SLE columns and Delta_VAF columns in the manifest.
    print("\n--- 3. SLE ARITHMETIC AND CONVENTIONS ---")
    rho_i = 0.917
    A_ocean = 361.8
    sle_diff_median = np.abs(df_proj['Delta_SLE_Median_mm'] - (-df_proj['Delta_VAF_Median_km3'] * rho_i / A_ocean)).max()
    print(f"Max absolute discrepancy for Delta_SLE_Median_mm vs -Delta_VAF_Median * 0.917 / 361.8: {sle_diff_median:.6f} mm")

    # Let's check Delta_SLE_16th_mm and Delta_SLE_84th_mm in the manifest
    # Is Delta_SLE_16th_mm = -Delta_VAF_16th_km3 * rho_i / A_ocean or is it -Delta_VAF_84th_km3 * rho_i / A_ocean?
    # Let's check both formulas
    diff_direct_16 = np.abs(df_proj['Delta_SLE_16th_mm'] - (-df_proj['Delta_VAF_16th_km3'] * rho_i / A_ocean)).max()
    diff_direct_84 = np.abs(df_proj['Delta_SLE_84th_mm'] - (-df_proj['Delta_VAF_84th_km3'] * rho_i / A_ocean)).max()
    diff_invert_16 = np.abs(df_proj['Delta_SLE_16th_mm'] - (-df_proj['Delta_VAF_84th_km3'] * rho_i / A_ocean)).max()
    diff_invert_84 = np.abs(df_proj['Delta_SLE_84th_mm'] - (-df_proj['Delta_VAF_16th_km3'] * rho_i / A_ocean)).max()
    print(f"Formula check Delta_SLE_16th_mm:")
    print(f"  Direct from Delta_VAF_16th (max diff): {diff_direct_16:.6f} mm")
    print(f"  Inverted from Delta_VAF_84th (max diff): {diff_invert_16:.6f} mm")
    print(f"Formula check Delta_SLE_84th_mm:")
    print(f"  Direct from Delta_VAF_84th (max diff): {diff_direct_84:.6f} mm")
    print(f"  Inverted from Delta_VAF_16th (max diff): {diff_invert_84:.6f} mm")

    # Sample rows for inspection
    print("\nSample projection rows (Year=2100, Basin=I-Ipp):")
    sample_rows = df_proj[(df_proj['Year'] == 2100) & (df_proj['Basin_ID'] == 'I-Ipp')]
    print(sample_rows[['Scenario', 'Delta_VAF_10th_km3', 'Delta_VAF_16th_km3', 'Delta_VAF_Median_km3', 'Delta_VAF_84th_km3', 'Delta_VAF_90th_km3', 'Delta_SLE_16th_mm', 'Delta_SLE_Median_mm', 'Delta_SLE_84th_mm']].to_string())

    # 4. Investigate 63,920 rows in stage7_1_training_dataset.csv
    print("\n--- 4. TRAINING DATASET COUNT INVESTIGATION (63,920 ROWS) ---")
    df_train = pd.read_csv(train_csv)
    print(f"Total rows in training dataset: {len(df_train)}")
    print(f"Columns: {list(df_train.columns)}")
    print(f"Unique Basins: {df_train['Basin_ID'].unique().tolist()} ({len(df_train['Basin_ID'].unique())} basins)")
    print(f"Unique Scenarios: {df_train['Climate_Scenario'].unique().tolist()} ({len(df_train['Climate_Scenario'].unique())} scenarios)")
    print(f"Unique Model Configurations: {len(df_train['Model_Name'].unique())} models: {sorted(df_train['Model_Name'].unique().tolist())}")
    print(f"Unique Experiments: {len(df_train['Experiment_ID'].unique())} experiments: {sorted(df_train['Experiment_ID'].unique().tolist())}")
    print(f"Unique Model Families: {len(df_train['Model_Family'].unique())} families: {sorted(df_train['Model_Family'].unique().tolist())}")
    print(f"Calendar Years: {df_train['Calendar_Year'].min()} to {df_train['Calendar_Year'].max()} ({len(df_train['Calendar_Year'].unique())} years)")
    
    # Group by (Model_Name, Experiment_ID)
    model_exp_groups = df_train.groupby(['Model_Name', 'Experiment_ID']).size()
    print(f"Number of unique (Model_Name, Experiment_ID) runs: {len(model_exp_groups)}")
    print("Breakdown of records per (Model_Name, Experiment_ID):")
    print(model_exp_groups.value_counts())

    # Let's see: how does 63,920 factor?
    # 63,920 / 4 basins = 15,980
    # 15,980 / 85 years (2015..2099 or 2016..2100) or 86 years?
    # Let's check how many years per run
    years_per_run = df_train.groupby(['Model_Name', 'Experiment_ID'])['Calendar_Year'].nunique()
    print("Years per run distribution:")
    print(years_per_run.value_counts())

    basins_per_run = df_train.groupby(['Model_Name', 'Experiment_ID'])['Basin_ID'].nunique()
    print("Basins per run distribution:")
    print(basins_per_run.value_counts())
    
    # 5. Inspect Model Artifacts & Metadata
    print("\n--- 5. MODEL ARTIFACTS & METADATA VERIFICATION ---")
    with open(meta_json, "r") as f:
        meta = json.load(f)
    print(f"Metadata stage: {meta.get('stage')}")
    print(f"Features: {meta.get('feature_names')}")
    print(f"Quantiles: {meta.get('quantiles_evaluated')}")
    print(f"OOF R2: {meta.get('oof_overall_r2')}")
    print(f"OOF RMSE: {meta.get('oof_overall_rmse_km3')}")
    print(f"OOF MAE: {meta.get('oof_overall_mae_km3')}")

    model_files = [
        "qgb_quantile_10.joblib",
        "qgb_quantile_16.joblib",
        "qgb_quantile_50.joblib",
        "qgb_quantile_84.joblib",
        "qgb_quantile_90.joblib"
    ]
    for mf in model_files:
        mp = os.path.join(model_dir, mf)
        exists = os.path.exists(mp)
        size = os.path.getsize(mp) if exists else 0
        loaded = False
        if exists:
            try:
                m = joblib.load(mp)
                loaded = hasattr(m, 'predict')
            except Exception as e:
                loaded = f"Error: {e}"
        print(f"Model artifact {mf}: exists={exists}, size={size:,} bytes, can_predict={loaded}")

    print("\n================================================================================")
    print("PRE-INTEGRATION AUDIT COMPLETE")
    print("================================================================================")

if __name__ == "__main__":
    run_pre_integration_verification()
