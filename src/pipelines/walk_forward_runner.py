"""
Walk-Forward Validation Engine
==============================
Executes the approved 20-fold rolling-origin walk-forward experiment (1995–2014).
Strictly enforces:
1. No looking into 2016–2024 test targets.
2. Fold-contained preprocessing.
3. Grouped 3-basin validation per fold.
4. Exact mass conservation: y_hat_{DomainA, t} = sum_b y_hat_{b, t}.
5. Generation of all 9 required data tables.
"""

import os
import sys
import numpy as np
import pandas as pd
from datetime import datetime
import warnings
from sklearn.exceptions import ConvergenceWarning
warnings.filterwarnings("ignore", category=ConvergenceWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

# Adjust sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

from src.evaluation.integrity_checks import verify_dataset_integrity, run_experiment_a1_accounting_verification
from src.feature_engineering.feature_builder import build_feature_dataset, get_feature_subsets, generate_model_feature_manifest
from src.models import (
    BasinPersistenceModel,
    BasinHistoricalMeanModel,
    BayesianRidgeModel,
    ElasticNetModel,
    ShallowRandomForestModel,
    ConstrainedGradientBoostingModel,
    LowDimGaussianProcessModel
)
from src.evaluation.metrics import calculate_point_metrics, calculate_probabilistic_calibration

TABLES_DIR = os.path.join(BASE_DIR, "reports", "tables")

def run_walk_forward_pipeline():
    print("=" * 80)
    print("PHASE 4B: WALK-FORWARD VALIDATION PIPELINE EXECUTION")
    print("=" * 80)
    
    # 1. Run Pre-Implementation Integrity Checks & Experiment A1
    verify_dataset_integrity(BASE_DIR)
    a1_result = run_experiment_a1_accounting_verification(BASE_DIR)
    
    # 2. Build feature dataset & manifest
    df = build_feature_dataset(BASE_DIR)
    generate_model_feature_manifest(BASE_DIR)
    feature_subsets = get_feature_subsets()
    full_feats = feature_subsets["full_features"]
    gp_feats = feature_subsets["gp_features"]
    
    # 3. Load 20-fold manifest
    fold_manifest_path = os.path.join(TABLES_DIR, "rolling_origin_fold_manifest.csv")
    fold_manifest = pd.read_csv(fold_manifest_path)
    
    # 4. Define candidate models
    # We will instantiate fresh models in each fold to guarantee strict fold containment
    model_definitions = [
        ("M0_Persistence", lambda: BasinPersistenceModel()),
        ("M0_Historical_Mean", lambda: BasinHistoricalMeanModel()),
        ("M2_Bayesian_Ridge", lambda: BayesianRidgeModel(full_feats)),
        ("M2_Bayesian_Ridge_Weighted", lambda: BayesianRidgeModel(full_feats)),
        ("M3_ElasticNet", lambda: ElasticNetModel(full_feats)),
        ("M4_Random_Forest", lambda: ShallowRandomForestModel(full_feats)),
        ("M5_Gradient_Boosting", lambda: ConstrainedGradientBoostingModel(full_feats)),
        ("M6_Gaussian_Process", lambda: LowDimGaussianProcessModel(gp_feats))
    ]
    
    # Data storage containers
    oof_predictions_records = []
    oof_domain_a_predictions = []
    model_run_records = []
    
    start_time = datetime.now()
    
    print("\n--- Starting 20-Fold Chronological Walk-Forward Loop (1995–2014) ---")
    
    for fold_idx, fold_row in fold_manifest.iterrows():
        fold_id = fold_row["Fold_ID"]
        val_year = int(fold_row["Validation_Year"])
        
        # Subsetting: Training strictly precedes validation year
        train_mask = (df["Year"] < val_year) & (df["Basin_ID"] != "Domain_A")
        val_mask = (df["Year"] == val_year) & (df["Basin_ID"] != "Domain_A")
        
        train_df = df[train_mask].copy()
        val_df = df[val_mask].copy()
        
        # Ensure basins are ordered consistently: Hp-I, I-Ipp, Ipp-J
        val_df = val_df.sort_values(by="Basin_ID")
        
        assert len(val_df) == 3, f"Fold {fold_id} validation year {val_year} must have exactly 3 basins"
        assert train_df["Year"].max() == val_year - 1, f"Fold {fold_id} training must terminate at {val_year - 1}"
        
        y_train = train_df["y_target"].values
        w_train = train_df["Observation_Weight"].values
        
        # Loop over candidate models
        for model_name, model_fn in model_definitions:
            model = model_fn()
            
            # Fitting: fold-contained
            if model_name == "M2_Bayesian_Ridge_Weighted":
                model.fit(train_df, y_train, sample_weight=w_train)
            else:
                model.fit(train_df, y_train)
                
            # Predict validation year (3 basins)
            if model.is_probabilistic:
                y_pred, y_std = model.predict(val_df, return_std=True)
            else:
                y_pred = model.predict(val_df)
                y_std = np.zeros_like(y_pred)
                
            # Verify exact mass conservation by computing Domain A strictly as sum of basin predictions
            domain_a_y_pred = float(np.sum(y_pred))
            domain_a_y_true = float(np.sum(val_df["y_target"].values))
            domain_a_y_std = float(np.sqrt(np.sum(y_std ** 2))) if model.is_probabilistic else 0.0
            
            # Record individual basin predictions
            for b_idx, (_, b_row) in enumerate(val_df.iterrows()):
                basin_id = b_row["Basin_ID"]
                y_true_val = float(b_row["y_target"])
                pred_val = float(y_pred[b_idx])
                std_val = float(y_std[b_idx])
                res_val = pred_val - y_true_val
                
                oof_predictions_records.append({
                    "Fold_ID": fold_id,
                    "Validation_Year": val_year,
                    "Basin_ID": basin_id,
                    "Model_Name": model_name,
                    "y_true": y_true_val,
                    "y_pred": pred_val,
                    "y_std": std_val,
                    "Residual": res_val,
                    "Observation_Uncertainty_sigma_km3_yr": float(b_row["Observation_Uncertainty_sigma_km3_yr"]),
                    "Observation_Weight": float(b_row["Observation_Weight"])
                })
                
            # Record Domain A aggregate prediction
            oof_domain_a_predictions.append({
                "Fold_ID": fold_id,
                "Validation_Year": val_year,
                "Basin_ID": "Domain_A",
                "Model_Name": model_name,
                "y_true": domain_a_y_true,
                "y_pred": domain_a_y_pred,
                "y_std": domain_a_y_std,
                "Residual": domain_a_y_pred - domain_a_y_true,
                "Observation_Uncertainty_sigma_km3_yr": np.nan,
                "Observation_Weight": np.nan
            })
            
            # Log model run manifest entry
            model_run_records.append({
                "Fold_ID": fold_id,
                "Validation_Year": val_year,
                "Model_Name": model_name,
                "Train_N": len(train_df),
                "Train_Start_Year": int(train_df["Year"].min()),
                "Train_End_Year": int(train_df["Year"].max()),
                "Val_N": len(val_df),
                "Is_Probabilistic": model.is_probabilistic,
                "Mass_Conservation_Verified": True
            })
            
        if (fold_idx + 1) % 5 == 0 or fold_idx == 0 or fold_idx == 19:
            print(f"Completed {fold_id} (Validation Year {val_year}, Train N={len(train_df)}) across all {len(model_definitions)} models.")
            
    print("\n--- 20 Folds Completed. Compiling Evaluation Tables ---")
    
    # 5. Compile Master OOF Predictions DataFrame
    oof_df = pd.DataFrame(oof_predictions_records)
    oof_dom_df = pd.DataFrame(oof_domain_a_predictions)
    
    # Save oof_predictions.csv (physical basins + domain A)
    master_oof = pd.concat([oof_df, oof_dom_df], ignore_index=True)
    oof_path = os.path.join(TABLES_DIR, "oof_predictions.csv")
    master_oof.to_csv(oof_path, index=False)
    print(f"Saved: {oof_path} ({len(master_oof)} rows)")
    
    # 6. Compile Metrics by Fold
    fold_metrics = []
    for (f_id, v_year, m_name), grp in master_oof.groupby(["Fold_ID", "Validation_Year", "Model_Name"]):
        phys_grp = grp[grp["Basin_ID"] != "Domain_A"]
        dom_grp = grp[grp["Basin_ID"] == "Domain_A"]
        
        pt = calculate_point_metrics(phys_grp["y_true"], phys_grp["y_pred"])
        dom_err = float(dom_grp["Residual"].values[0]) if len(dom_grp) > 0 else np.nan
        
        fold_metrics.append({
            "Fold_ID": f_id,
            "Validation_Year": v_year,
            "Model_Name": m_name,
            "Basin_RMSE": round(pt["rmse"], 3),
            "Basin_MAE": round(pt["mae"], 3),
            "Basin_Mean_Bias": round(pt["bias"], 3),
            "Domain_A_Error": round(dom_err, 3)
        })
    fold_metrics_df = pd.DataFrame(fold_metrics)
    fmet_path = os.path.join(TABLES_DIR, "oof_metrics_by_fold.csv")
    fold_metrics_df.to_csv(fmet_path, index=False)
    print(f"Saved: {fmet_path} ({len(fold_metrics_df)} rows)")
    
    # 7. Compile Metrics by Basin (Across the 20 Validation Years)
    basin_metrics = []
    for (b_id, m_name), grp in master_oof.groupby(["Basin_ID", "Model_Name"]):
        pt = calculate_point_metrics(grp["y_true"], grp["y_pred"])
        basin_metrics.append({
            "Basin_ID": b_id,
            "Model_Name": m_name,
            "Validation_Years_N": len(grp),
            "RMSE": round(pt["rmse"], 3),
            "MAE": round(pt["mae"], 3),
            "Mean_Bias": round(pt["bias"], 3),
            "R2": round(pt["r2"], 4)
        })
    basin_metrics_df = pd.DataFrame(basin_metrics)
    bmet_path = os.path.join(TABLES_DIR, "oof_metrics_by_basin.csv")
    basin_metrics_df.to_csv(bmet_path, index=False)
    print(f"Saved: {bmet_path} ({len(basin_metrics_df)} rows)")
    
    # 8. Compile Pooled Metrics (Across all 60 physical out-of-fold evaluations)
    pooled_metrics = []
    for m_name, grp in oof_df.groupby("Model_Name"):
        pt = calculate_point_metrics(grp["y_true"], grp["y_pred"])
        
        # Domain A aggregate RMSE across 20 validation years
        dom_grp = oof_dom_df[oof_dom_df["Model_Name"] == m_name]
        dom_pt = calculate_point_metrics(dom_grp["y_true"], dom_grp["y_pred"])
        
        pooled_metrics.append({
            "Model_Name": m_name,
            "Physical_Samples_N": len(grp),
            "Pooled_RMSE": round(pt["rmse"], 3),
            "Pooled_MAE": round(pt["mae"], 3),
            "Pooled_Mean_Bias": round(pt["bias"], 3),
            "Pooled_R2": round(pt["r2"], 4),
            "Domain_A_Agg_RMSE": round(dom_pt["rmse"], 3),
            "Domain_A_Agg_MAE": round(dom_pt["mae"], 3),
            "Domain_A_Agg_Bias": round(dom_pt["bias"], 3),
            "Domain_A_Agg_R2": round(dom_pt["r2"], 4)
        })
    pooled_metrics_df = pd.DataFrame(pooled_metrics)
    pooled_metrics_df.sort_values(by="Pooled_RMSE", inplace=True)
    pmet_path = os.path.join(TABLES_DIR, "oof_metrics_pooled.csv")
    pooled_metrics_df.to_csv(pmet_path, index=False)
    print(f"Saved: {pmet_path} ({len(pooled_metrics_df)} rows)")
    
    # 9. Compile Year-Blocked Error Vectors
    year_blocked_records = []
    for (v_year, m_name), grp in oof_df.groupby(["Validation_Year", "Model_Name"]):
        grp_sorted = grp.sort_values(by="Basin_ID")
        e_hp = float(grp_sorted[grp_sorted["Basin_ID"] == "Hp-I"]["Residual"].values[0])
        e_ipp = float(grp_sorted[grp_sorted["Basin_ID"] == "I-Ipp"]["Residual"].values[0])
        e_ipj = float(grp_sorted[grp_sorted["Basin_ID"] == "Ipp-J"]["Residual"].values[0])
        
        e_vec = np.array([e_hp, e_ipp, e_ipj])
        norm_e = float(np.linalg.norm(e_vec))
        
        dom_row = oof_dom_df[(oof_dom_df["Validation_Year"] == v_year) & (oof_dom_df["Model_Name"] == m_name)]
        dom_err = float(dom_row["Residual"].values[0])
        
        year_blocked_records.append({
            "Validation_Year": v_year,
            "Model_Name": m_name,
            "e_Hp_I": round(e_hp, 3),
            "e_I_Ipp": round(e_ipp, 3),
            "e_Ipp_J": round(e_ipj, 3),
            "Euclidean_Norm_L2": round(norm_e, 3),
            "Domain_A_Mass_Error": round(dom_err, 3)
        })
    year_blocked_df = pd.DataFrame(year_blocked_records)
    yb_path = os.path.join(TABLES_DIR, "oof_year_blocked_errors.csv")
    year_blocked_df.to_csv(yb_path, index=False)
    print(f"Saved: {yb_path} ({len(year_blocked_df)} rows)")
    
    # 10. Compile Cumulative Drift Tracking (1995–2014)
    drift_records = []
    for m_name in master_oof["Model_Name"].unique():
        for b_id in ["Hp-I", "I-Ipp", "Ipp-J", "Domain_A"]:
            sub = master_oof[(master_oof["Model_Name"] == m_name) & (master_oof["Basin_ID"] == b_id)].sort_values(by="Validation_Year")
            
            cum_true = np.cumsum(sub["y_true"].values)
            cum_pred = np.cumsum(sub["y_pred"].values)
            drift_series = cum_pred - cum_true
            
            final_drift = float(drift_series[-1])
            max_abs_drift = float(np.max(np.abs(drift_series)))
            mean_drift = float(np.mean(drift_series))
            
            drift_records.append({
                "Model_Name": m_name,
                "Basin_ID": b_id,
                "Evaluation_Span": "1995–2014 (20 yrs)",
                "Total_Observed_Volume_Change_km3": round(float(cum_true[-1]), 2),
                "Total_Predicted_Volume_Change_km3": round(float(cum_pred[-1]), 2),
                "Final_Endpoint_Drift_km3": round(final_drift, 2),
                "Max_Absolute_Drift_km3": round(max_abs_drift, 2),
                "Mean_Cumulative_Drift_km3": round(mean_drift, 2)
            })
    drift_df = pd.DataFrame(drift_records)
    drift_path = os.path.join(TABLES_DIR, "oof_cumulative_drift.csv")
    drift_df.to_csv(drift_path, index=False)
    print(f"Saved: {drift_path} ({len(drift_df)} rows)")
    
    # 11. Compile Prediction Interval Calibration (For Probabilistic Models)
    pi_records = []
    prob_models = ["M2_Bayesian_Ridge", "M2_Bayesian_Ridge_Weighted", "M6_Gaussian_Process"]
    for m_name in prob_models:
        sub = oof_df[oof_df["Model_Name"] == m_name]
        cal = calculate_probabilistic_calibration(sub["y_true"], sub["y_pred"], sub["y_std"])
        
        # Basin-specific coverage
        for b_id in ["Hp-I", "I-Ipp", "Ipp-J"]:
            b_sub = sub[sub["Basin_ID"] == b_id]
            b_cal = calculate_probabilistic_calibration(b_sub["y_true"], b_sub["y_pred"], b_sub["y_std"])
            pi_records.append({
                "Model_Name": m_name,
                "Basin_Scope": b_id,
                "Validation_Samples_N": len(b_sub),
                "Empirical_Coverage_95pct": round(b_cal["coverage_95"] * 100, 1),
                "Mean_Interval_Width_km3_yr": round(b_cal["mean_interval_width"], 2),
                "CRPS_km3_yr": round(b_cal["crps"], 3),
                "Calibration_Assessment": "Calibrated" if abs(b_cal["coverage_95"] - 0.95) <= 0.10 else "Miscalibrated"
            })
            
        pi_records.append({
            "Model_Name": m_name,
            "Basin_Scope": "POOLED_ALL_BASINS",
            "Validation_Samples_N": len(sub),
            "Empirical_Coverage_95pct": round(cal["coverage_95"] * 100, 1),
            "Mean_Interval_Width_km3_yr": round(cal["mean_interval_width"], 2),
            "CRPS_km3_yr": round(cal["crps"], 3),
            "Calibration_Assessment": "Calibrated" if abs(cal["coverage_95"] - 0.95) <= 0.10 else "Miscalibrated"
        })
        
    pi_df = pd.DataFrame(pi_records)
    pi_path = os.path.join(TABLES_DIR, "oof_prediction_intervals.csv")
    pi_df.to_csv(pi_path, index=False)
    print(f"Saved: {pi_path} ({len(pi_df)} rows)")
    
    # 12. Save Model Run Manifest
    run_manifest_df = pd.DataFrame(model_run_records)
    run_path = os.path.join(TABLES_DIR, "model_run_manifest.csv")
    run_manifest_df.to_csv(run_path, index=False)
    print(f"Saved: {run_path} ({len(run_manifest_df)} rows)")
    
    elapsed = datetime.now() - start_time
    print(f"\nPipeline finished successfully in {elapsed.total_seconds():.2f} seconds!")
    print("=" * 80)
    
    return {
        "master_oof": master_oof,
        "pooled_metrics": pooled_metrics_df,
        "basin_metrics": basin_metrics_df,
        "drift_metrics": drift_df,
        "calibration_metrics": pi_df
    }

if __name__ == "__main__":
    run_walk_forward_pipeline()
