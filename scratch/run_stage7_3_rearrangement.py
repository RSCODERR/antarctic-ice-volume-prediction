import os
import pandas as pd
import numpy as np

def analyze_rearrangement():
    base_dir = "antarctic-ice-volume-prediction"
    orig_path = os.path.join(base_dir, "data/projections/stage7_1_future_projections_2015_2100.csv")
    out_path = os.path.join(base_dir, "data/projections/stage7_3_future_projections_rearranged_2015_2100.csv")
    train_path = os.path.join(base_dir, "reports/tables/stage7_1_training_dataset.csv")

    df_orig = pd.read_csv(orig_path)
    print(f"Loaded {len(df_orig)} rows from {orig_path}")

    # Inspect quantiles in df_orig
    # Columns:
    # Delta_VAF_10th_km3, Delta_VAF_16th_km3, Delta_VAF_Median_km3, Delta_VAF_84th_km3, Delta_VAF_90th_km3
    vaf_cols = [
        "Delta_VAF_10th_km3",
        "Delta_VAF_16th_km3",
        "Delta_VAF_Median_km3",
        "Delta_VAF_84th_km3",
        "Delta_VAF_90th_km3"
    ]

    rho_i = 0.917
    A_ocean = 361.8

    # Identify crossing records before correction
    crossing_mask = []
    max_inversion = 0.0
    for _, row in df_orig.iterrows():
        vals = [row[c] for c in vaf_cols]
        is_crossing = not (vals[0] <= vals[1] <= vals[2] <= vals[3] <= vals[4])
        crossing_mask.append(is_crossing)
        if is_crossing:
            # Measure maximum inversion: max(vals[i] - vals[i+1]) for i=0..3
            inversions = [vals[i] - vals[i+1] for i in range(4) if vals[i] > vals[i+1]]
            if inversions:
                max_inversion = max(max_inversion, max(inversions))

    crossing_mask = np.array(crossing_mask)
    num_crossing = crossing_mask.sum()
    print(f"Total crossing records in original manifest: {num_crossing} / {len(df_orig)} ({num_crossing/len(df_orig)*100:.2f}%)")
    print(f"Maximum pairwise inversion: {max_inversion:.3f} km3")

    # Create the rearranged dataframe
    df_rearranged = df_orig.copy()
    
    # Store adjustments
    adjustments = {c: [] for c in vaf_cols}
    records_modified = 0

    rearranged_vaf = []
    for idx, row in df_orig.iterrows():
        raw_vals = [row[c] for c in vaf_cols]
        sorted_vals = sorted(raw_vals) # Chernozhukov monotone rearrangement
        
        was_changed = (raw_vals != sorted_vals)
        if was_changed:
            records_modified += 1
            
        for i, c in enumerate(vaf_cols):
            diff = abs(sorted_vals[i] - raw_vals[i])
            adjustments[c].append(diff)
            
        rearranged_vaf.append(sorted_vals)

    rearranged_arr = np.array(rearranged_vaf)
    for i, c in enumerate(vaf_cols):
        df_rearranged[c] = np.round(rearranged_arr[:, i], 2)

    # Recompute SLE quantiles rigorously with proper ordering:
    # Notice: SLE = - (Delta_VAF * 0.917) / 361.8
    # Since VAF has q10 <= q16 <= q50 <= q84 <= q90,
    # SLE has:
    # SLE_10th = - (VAF_90th * rho_i) / A_ocean
    # SLE_16th = - (VAF_84th * rho_i) / A_ocean
    # SLE_Median = - (VAF_Median * rho_i) / A_ocean
    # SLE_84th = - (VAF_16th * rho_i) / A_ocean
    # SLE_90th = - (VAF_10th * rho_i) / A_ocean

    df_rearranged["Delta_SLE_Median_mm"] = np.round(- (df_rearranged["Delta_VAF_Median_km3"] * rho_i) / A_ocean, 3)
    df_rearranged["Delta_SLE_16th_mm"] = np.round(- (df_rearranged["Delta_VAF_84th_km3"] * rho_i) / A_ocean, 3)
    df_rearranged["Delta_SLE_84th_mm"] = np.round(- (df_rearranged["Delta_VAF_16th_km3"] * rho_i) / A_ocean, 3)
    df_rearranged["Delta_SLE_10th_mm"] = np.round(- (df_rearranged["Delta_VAF_90th_km3"] * rho_i) / A_ocean, 3)
    df_rearranged["Delta_SLE_90th_mm"] = np.round(- (df_rearranged["Delta_VAF_10th_km3"] * rho_i) / A_ocean, 3)

    # Update metadata columns
    df_rearranged["Quantile_Rearrangement_Applied"] = True
    df_rearranged["Rearrangement_Method"] = "Chernozhukov_2010_Isotonic_Sorting"

    # Verify all 1,032 records have strict monotonic ordering for both VAF and SLE
    vaf_post_violations = 0
    sle_post_violations = 0
    for _, row in df_rearranged.iterrows():
        v10 = row["Delta_VAF_10th_km3"]
        v16 = row["Delta_VAF_16th_km3"]
        v50 = row["Delta_VAF_Median_km3"]
        v84 = row["Delta_VAF_84th_km3"]
        v90 = row["Delta_VAF_90th_km3"]
        if not (v10 <= v16 <= v50 <= v84 <= v90):
            vaf_post_violations += 1

        s10 = row["Delta_SLE_10th_mm"]
        s16 = row["Delta_SLE_16th_mm"]
        s50 = row["Delta_SLE_Median_mm"]
        s84 = row["Delta_SLE_84th_mm"]
        s90 = row["Delta_SLE_90th_mm"]
        if not (s10 <= s16 <= s50 <= s84 <= s90):
            sle_post_violations += 1

    print(f"\n--- Post-Correction Monotonicity Verification ---")
    print(f"Records modified: {records_modified} / {len(df_rearranged)}")
    print(f"Post-correction VAF violations: {vaf_post_violations} / {len(df_rearranged)}")
    print(f"Post-correction SLE violations: {sle_post_violations} / {len(df_rearranged)}")

    # Report adjustment statistics
    print(f"\n--- Adjustment Magnitude Statistics (km3) ---")
    all_diffs = []
    for c in vaf_cols:
        diffs = np.array(adjustments[c])
        all_diffs.extend(diffs[diffs > 0])
        print(f"  {c}: Max change = {diffs.max():.2f} km3, Mean change (where changed) = {diffs[diffs > 0].mean() if (diffs > 0).any() else 0.0:.2f} km3")
    all_diffs = np.array(all_diffs)
    print(f"Pooled non-zero adjustments count: {len(all_diffs)}")
    print(f"Pooled mean adjustment: {all_diffs.mean():.2f} km3")
    print(f"Pooled median adjustment: {np.median(all_diffs):.2f} km3")
    print(f"Pooled 95th percentile adjustment: {np.percentile(all_diffs, 95):.2f} km3")
    print(f"Pooled maximum adjustment: {all_diffs.max():.2f} km3")

    # Save to new versioned file
    df_rearranged.to_csv(out_path, index=False)
    print(f"\nSaved rearranged dataset to: {out_path}")

    # Reassess Empirical Coverage on Training Dataset
    print(f"\n--- Reassessing Empirical Quantile Coverage on Out-of-Family Folds ---")
    # Let's inspect LOMFO coverage before and after rearrangement on held-out predictions
    # We can load the fold predictions or evaluate the models on the LOMFO folds
    return df_rearranged

if __name__ == "__main__":
    analyze_rearrangement()
