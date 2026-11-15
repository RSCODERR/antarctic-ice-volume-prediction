"""
Phase 4C: Held-Out Test Evaluation Pipeline (2016–2024)
======================================================
Executes the locked out-of-sample evaluation on the 2016–2024 test period.
Strictly enforces:
1. Frozen training partition: 1979–2014 (N = 108 physical observations; 2015 embargo preserved).
2. Sealed test partition: 2016–2024 (N = 27 physical observations: 3 basins x 9 years; 9 Domain A diagnostics).
3. Exact linear mass conservation: y_hat_{DomainA, t} == sum_b y_hat_{b, t}.
4. Preprocessing fitted strictly on training partition (StandardScaler parameters frozen).
5. Comprehensive evaluation of point metrics, probabilistic calibration, cumulative drift,
   and cluster-paired statistical hypothesis testing.
"""

import os
import sys
import numpy as np
import pandas as pd
from datetime import datetime
import warnings
from scipy.stats import ttest_rel, wilcoxon
from sklearn.exceptions import ConvergenceWarning

warnings.filterwarnings("ignore", category=ConvergenceWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

from src.feature_engineering.feature_builder import build_feature_dataset, get_feature_subsets
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
FIGURES_DIR = os.path.join(BASE_DIR, "reports", "figures")
os.makedirs(TABLES_DIR, exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)

def run_test_evaluation():
    print("=" * 80)
    print("PHASE 4C: HELD-OUT TEST EVALUATION PIPELINE (2016–2024)")
    print("=" * 80)
    
    # 1. Build Feature Dataset
    print("\n[Step 1] Loading master feature dataset...")
    df = build_feature_dataset(BASE_DIR)
    feature_subsets = get_feature_subsets()
    full_feats = feature_subsets["full_features"]
    gp_feats = feature_subsets["gp_features"]
    
    # 2. Delineate Training and Test Partitions
    print("\n[Step 2] Delineating chronological partitions...")
    # Training: 1979–2014 (N = 108 physical basin-years)
    # Embargo Buffer 2: 2015 (quarantined; used only as lag for 2016)
    # Test: 2016–2024 (N = 27 physical basin-years)
    train_df = df[df["Year"] <= 2014].copy()
    test_df = df[(df["Year"] >= 2016) & (df["Year"] <= 2024)].copy()
    embargo_df = df[df["Year"] == 2015].copy()
    
    print(f"  Training partition rows (1979–2014): {len(train_df)} physical basin-years")
    print(f"  Embargo buffer rows (2015):         {len(embargo_df)} physical basin-years (quarantined)")
    print(f"  Test partition rows (2016–2024):     {len(test_df)} physical basin-years")
    
    assert len(train_df) == 108, f"Expected 108 training rows, got {len(train_df)}"
    assert len(test_df) == 27, f"Expected 27 test rows, got {len(test_df)}"
    
    # 3. Model Portfolio Configuration
    model_configs = [
        ("M0_Persistence", BasinPersistenceModel()),
        ("M0_Historical_Mean", BasinHistoricalMeanModel()),
        ("M2_Bayesian_Ridge", BayesianRidgeModel(full_feats)),
        ("M2_Bayesian_Ridge_Weighted", BayesianRidgeModel(full_feats)),
        ("M3_ElasticNet", ElasticNetModel(full_feats)),
        ("M4_Random_Forest", ShallowRandomForestModel(full_feats)),
        ("M5_Gradient_Boosting", ConstrainedGradientBoostingModel(full_feats)),
        ("M6_Gaussian_Process", LowDimGaussianProcessModel(gp_feats))
    ]
    
    prediction_records = []
    
    # 4. Train Models Once on Frozen Training Partition & Predict on Test Partition
    print("\n[Step 3] Training models on 1979–2014 and generating 2016–2024 test predictions...")
    
    for model_name, model in model_configs:
        print(f"  Fitting and evaluating {model_name}...")
        
        # Fit model
        if model_name == "M2_Bayesian_Ridge_Weighted":
            model.fit(train_df, train_df["y_target"].values, sample_weight=train_df["Observation_Weight"].values)
        elif model_name in ["M0_Persistence", "M0_Historical_Mean"]:
            model.fit(train_df, train_df["y_target"].values)
        else:
            model.fit(train_df, train_df["y_target"].values)
            
        # Predict on test set
        if model.is_probabilistic:
            preds, stds = model.predict(test_df, return_std=True)
        else:
            preds = model.predict(test_df, return_std=False)
            stds = np.zeros_like(preds)
            
        # Record physical predictions
        for idx, (_, row) in enumerate(test_df.iterrows()):
            y_true_val = float(row["y_target"])
            y_pred_val = float(preds[idx])
            y_std_val = float(stds[idx])
            res_val = y_pred_val - y_true_val
            
            prediction_records.append({
                "Test_Stage": "Held_Out_Test",
                "Evaluation_Year": int(row["Year"]),
                "Basin_ID": row["Basin_ID"],
                "Model_Name": model_name,
                "y_true": y_true_val,
                "y_pred": y_pred_val,
                "y_std": y_std_val,
                "Residual": res_val,
                "Observation_Uncertainty_sigma_km3_yr": float(row["Observation_Uncertainty_sigma_km3_yr"]),
                "Observation_Weight": float(row["Observation_Weight"])
            })
            
        # Formulate Domain A Regional Aggregation by exact linear summation
        # y_hat_{DomainA, t} = sum_b y_hat_{b, t}
        for year in range(2016, 2025):
            sub_year = [r for r in prediction_records if r["Model_Name"] == model_name and r["Evaluation_Year"] == year and r["Basin_ID"] != "Domain_A"]
            
            y_true_doma = sum(r["y_true"] for r in sub_year)
            y_pred_doma = sum(r["y_pred"] for r in sub_year)
            # Propagate predictive variance: sigma_doma^2 = sum_b sigma_b^2
            y_std_doma = np.sqrt(sum(r["y_std"] ** 2 for r in sub_year))
            res_doma = y_pred_doma - y_true_doma
            
            # Domain A observation uncertainty: sigma_doma = sqrt(sum_b sigma_b^2)
            obs_unc_doma = np.sqrt(sum(r["Observation_Uncertainty_sigma_km3_yr"] ** 2 for r in sub_year))
            obs_weight_doma = 1.0 / (obs_unc_doma ** 2)
            
            prediction_records.append({
                "Test_Stage": "Derived_Regional_Diagnostic",
                "Evaluation_Year": year,
                "Basin_ID": "Domain_A",
                "Model_Name": model_name,
                "y_true": y_true_doma,
                "y_pred": y_pred_doma,
                "y_std": y_std_doma,
                "Residual": res_doma,
                "Observation_Uncertainty_sigma_km3_yr": obs_unc_doma,
                "Observation_Weight": obs_weight_doma
            })
            
    df_preds = pd.DataFrame(prediction_records)
    preds_csv = os.path.join(TABLES_DIR, "test_predictions.csv")
    df_preds.to_csv(preds_csv, index=False)
    print(f"\n[Step 4] Master test predictions saved: {preds_csv} ({len(df_preds)} rows)")
    
    # Verify exact row composition: 8 models x (27 physical + 9 Domain A) = 288 rows
    assert len(df_preds) == 288, f"Expected 288 rows, got {len(df_preds)}"
    
    # 5. Compute Metrics
    print("\n[Step 5] Computing test evaluation metrics...")
    
    # A. Pooled Physical Metrics (N = 27)
    pooled_rows = []
    for model_name, _ in model_configs:
        sub = df_preds[(df_preds["Model_Name"] == model_name) & (df_preds["Basin_ID"] != "Domain_A")]
        pt = calculate_point_metrics(sub["y_true"], sub["y_pred"])
        
        # Probabilistic metrics if std > 0
        if sub["y_std"].sum() > 0:
            prob = calculate_probabilistic_calibration(sub["y_true"], sub["y_pred"], sub["y_std"])
            cov = prob["coverage_95"]
            sharp = prob["mean_interval_width"]
            crps = prob["crps"]
        else:
            cov = np.nan
            sharp = np.nan
            crps = np.nan
            
        # Domain A cumulative drift
        sub_dom = df_preds[(df_preds["Model_Name"] == model_name) & (df_preds["Basin_ID"] == "Domain_A")].sort_values("Evaluation_Year")
        cum_true_dom = sub_dom["y_true"].sum()
        cum_pred_dom = sub_dom["y_pred"].sum()
        endpoint_drift_dom = cum_pred_dom - cum_true_dom
        pct_loss_captured = (cum_pred_dom / cum_true_dom * 100.0) if abs(cum_true_dom) > 1e-6 else np.nan
        
        pooled_rows.append({
            "Model_Name": model_name,
            "Physical_N": len(sub),
            "RMSE_km3_yr": pt["rmse"],
            "MAE_km3_yr": pt["mae"],
            "Mean_Bias_km3_yr": pt["bias"],
            "R2_Score": pt["r2"],
            "CRPS_km3_yr": crps,
            "Empirical_Coverage_95%": cov,
            "Mean_Interval_Width_km3_yr": sharp,
            "DomainA_Cumulative_True_Loss_km3": cum_true_dom,
            "DomainA_Cumulative_Pred_Loss_km3": cum_pred_dom,
            "DomainA_Cumulative_Drift_km3": endpoint_drift_dom,
            "Pct_Cumulative_Loss_Captured": pct_loss_captured
        })
        
    df_pooled = pd.DataFrame(pooled_rows).sort_values("RMSE_km3_yr")
    pooled_csv = os.path.join(TABLES_DIR, "test_metrics_pooled.csv")
    df_pooled.to_csv(pooled_csv, index=False)
    print(f"  Pooled metrics saved: {pooled_csv}")
    
    # B. Basin-Specific Metrics (N = 9 each)
    basin_rows = []
    for model_name, _ in model_configs:
        for b in ["Hp-I", "I-Ipp", "Ipp-J", "Domain_A"]:
            sub = df_preds[(df_preds["Model_Name"] == model_name) & (df_preds["Basin_ID"] == b)].sort_values("Evaluation_Year")
            pt = calculate_point_metrics(sub["y_true"], sub["y_pred"])
            
            if sub["y_std"].sum() > 0:
                prob = calculate_probabilistic_calibration(sub["y_true"], sub["y_pred"], sub["y_std"])
                cov = prob["coverage_95"]
                sharp = prob["mean_interval_width"]
                crps = prob["crps"]
            else:
                cov = np.nan
                sharp = np.nan
                crps = np.nan
                
            cum_true = sub["y_true"].sum()
            cum_pred = sub["y_pred"].sum()
            drift = cum_pred - cum_true
            
            # Max absolute path drift along the 9-year trajectory
            path_drifts = np.abs(np.cumsum(sub["y_pred"].values) - np.cumsum(sub["y_true"].values))
            max_path_drift = float(np.max(path_drifts))
            
            basin_rows.append({
                "Model_Name": model_name,
                "Basin_ID": b,
                "Test_Years_N": len(sub),
                "RMSE_km3_yr": pt["rmse"],
                "MAE_km3_yr": pt["mae"],
                "Mean_Bias_km3_yr": pt["bias"],
                "R2_Score": pt["r2"],
                "CRPS_km3_yr": crps,
                "Coverage_95%": cov,
                "Interval_Width_km3_yr": sharp,
                "Cumulative_True_Loss_km3": cum_true,
                "Cumulative_Pred_Loss_km3": cum_pred,
                "Cumulative_Endpoint_Drift_km3": drift,
                "Max_Absolute_Path_Drift_km3": max_path_drift
            })
            
    df_basin = pd.DataFrame(basin_rows)
    basin_csv = os.path.join(TABLES_DIR, "test_metrics_by_basin.csv")
    df_basin.to_csv(basin_csv, index=False)
    print(f"  Basin-specific metrics saved: {basin_csv}")
    
    # C. Cumulative Trajectory Table
    cum_rows = []
    for model_name, _ in model_configs:
        sub = df_preds[(df_preds["Model_Name"] == model_name) & (df_preds["Basin_ID"] == "Domain_A")].sort_values("Evaluation_Year")
        cum_pred_series = np.cumsum(sub["y_pred"].values)
        cum_true_series = np.cumsum(sub["y_true"].values)
        errors = cum_pred_series - cum_true_series
        
        cum_rows.append({
            "Model_Name": model_name,
            "DomainA_True_Cumulative_Loss_2024_km3": cum_true_series[-1],
            "DomainA_Pred_Cumulative_Loss_2024_km3": cum_pred_series[-1],
            "DomainA_Cumulative_Endpoint_Drift_km3": errors[-1],
            "Max_Absolute_Path_Drift_km3": float(np.max(np.abs(errors))),
            "Pct_Mass_Loss_Captured": (cum_pred_series[-1] / cum_true_series[-1] * 100.0)
        })
    df_cum = pd.DataFrame(cum_rows).sort_values("DomainA_Cumulative_Endpoint_Drift_km3")
    cum_csv = os.path.join(TABLES_DIR, "test_cumulative_drift.csv")
    df_cum.to_csv(cum_csv, index=False)
    print(f"  Cumulative drift table saved: {cum_csv}")
    
    # D. Year-Blocked Errors (9 years x 8 models)
    yb_rows = []
    for model_name, _ in model_configs:
        for year in range(2016, 2025):
            sub = df_preds[(df_preds["Model_Name"] == model_name) & (df_preds["Evaluation_Year"] == year) & (df_preds["Basin_ID"] != "Domain_A")]
            pt = calculate_point_metrics(sub["y_true"], sub["y_pred"])
            
            sub_dom = df_preds[(df_preds["Model_Name"] == model_name) & (df_preds["Evaluation_Year"] == year) & (df_preds["Basin_ID"] == "Domain_A")].iloc[0]
            
            yb_rows.append({
                "Model_Name": model_name,
                "Evaluation_Year": year,
                "Annual_Cluster_RMSE_km3_yr": pt["rmse"],
                "Annual_Cluster_MAE_km3_yr": pt["mae"],
                "Annual_Cluster_Bias_km3_yr": pt["bias"],
                "DomainA_True_Rate_km3_yr": sub_dom["y_true"],
                "DomainA_Pred_Rate_km3_yr": sub_dom["y_pred"],
                "DomainA_Rate_Error_km3_yr": sub_dom["Residual"]
            })
    df_yb = pd.DataFrame(yb_rows)
    yb_csv = os.path.join(TABLES_DIR, "test_year_blocked_errors.csv")
    df_yb.to_csv(yb_csv, index=False)
    print(f"  Year-blocked error table saved: {yb_csv}")
    
    # E. Persistence Telescoping Audit on Test Window
    print("\n[Step 6] Auditing persistence telescoping identity on test period...")
    # sum_{t=2016}^{2024} (y_hat_t - y_t) == y_{2015} - y_{2024}
    # Load 2015 target from raw ml_target_dataset
    raw_df = pd.read_csv(os.path.join(TABLES_DIR, "ml_target_dataset.csv"))
    
    telescope_rows = []
    for b in ["Hp-I", "I-Ipp", "Ipp-J", "Domain_A"]:
        y_2015 = raw_df[(raw_df["Year"] == 2015) & (raw_df["Basin_ID"] == b)]["Target_Annual_Volume_Change_Central_km3_yr"].values[0]
        y_2024 = raw_df[(raw_df["Year"] == 2024) & (raw_df["Basin_ID"] == b)]["Target_Annual_Volume_Change_Central_km3_yr"].values[0]
        theoretical_drift = y_2015 - y_2024
        
        # Actual sum of residuals for Persistence
        sub_p = df_preds[(df_preds["Model_Name"] == "M0_Persistence") & (df_preds["Basin_ID"] == b)]
        actual_sum_res = sub_p["Residual"].sum()
        
        pt = calculate_point_metrics(sub_p["y_true"], sub_p["y_pred"])
        
        path_drifts = np.abs(np.cumsum(sub_p["y_pred"].values) - np.cumsum(sub_p["y_true"].values))
        max_path = float(np.max(path_drifts))
        
        telescope_rows.append({
            "Basin_ID": b,
            "Initialization_Target_y2015_km3_yr": y_2015,
            "Final_Target_y2024_km3_yr": y_2024,
            "Theoretical_Telescoping_Drift_km3": theoretical_drift,
            "Actual_Sum_of_Test_Residuals_km3": actual_sum_res,
            "Discrepancy": abs(actual_sum_res - theoretical_drift),
            "Annual_Rate_RMSE_km3_yr": pt["rmse"],
            "Max_Absolute_Path_Drift_km3": max_path
        })
        
    df_tele = pd.DataFrame(telescope_rows)
    tele_csv = os.path.join(TABLES_DIR, "test_persistence_telescoping_audit.csv")
    df_tele.to_csv(tele_csv, index=False)
    print(f"  Persistence telescoping audit saved: {tele_csv}")
    
    # F. Cluster-Paired Statistical Hypothesis Testing vs Historical Mean
    print("\n[Step 7] Conducting cluster-paired statistical hypothesis tests...")
    # Form 9 annual clusters (2016–2024)
    sig_rows = []
    
    # Historical Mean annual cluster MSEs
    sub_hm = df_preds[(df_preds["Model_Name"] == "M0_Historical_Mean") & (df_preds["Basin_ID"] != "Domain_A")]
    hm_cluster_mse = sub_hm.groupby("Evaluation_Year").apply(lambda g: np.mean(g["Residual"] ** 2))
    
    for model_name, _ in model_configs:
        if model_name == "M0_Historical_Mean":
            continue
            
        sub_m = df_preds[(df_preds["Model_Name"] == model_name) & (df_preds["Basin_ID"] != "Domain_A")]
        m_cluster_mse = sub_m.groupby("Evaluation_Year").apply(lambda g: np.mean(g["Residual"] ** 2))
        
        diff = hm_cluster_mse.values - m_cluster_mse.values # Positive means model has lower MSE than Historical Mean
        mean_diff = float(np.mean(diff))
        std_diff = float(np.std(diff, ddof=1))
        
        t_stat, p_val_t = ttest_rel(hm_cluster_mse.values, m_cluster_mse.values)
        w_stat, p_val_w = wilcoxon(hm_cluster_mse.values, m_cluster_mse.values)
        
        sig_rows.append({
            "Comparison": f"{model_name} vs M0_Historical_Mean",
            "Clusters_N_Years": len(diff),
            "Mean_Cluster_MSE_Reduction_km6_yr2": mean_diff,
            "Std_Cluster_MSE_Reduction_km6_yr2": std_diff,
            "Paired_t_Statistic": float(t_stat),
            "Paired_t_p_value": float(p_val_t),
            "Wilcoxon_W_Statistic": float(w_stat),
            "Wilcoxon_p_value": float(p_val_w),
            "Statistically_Significant_at_5%": (p_val_t < 0.05)
        })
        
    df_sig = pd.DataFrame(sig_rows)
    sig_csv = os.path.join(TABLES_DIR, "test_significance_testing.csv")
    df_sig.to_csv(sig_csv, index=False)
    print(f"  Statistical significance table saved: {sig_csv}")
    
    # G. Regional Mass Conservation Check
    print("\n[Step 8] Verifying regional mass conservation...")
    cons_rows = []
    for model_name, _ in model_configs:
        for year in range(2016, 2025):
            sub_b = df_preds[(df_preds["Model_Name"] == model_name) & (df_preds["Evaluation_Year"] == year) & (df_preds["Basin_ID"] != "Domain_A")]
            sub_d = df_preds[(df_preds["Model_Name"] == model_name) & (df_preds["Evaluation_Year"] == year) & (df_preds["Basin_ID"] == "Domain_A")].iloc[0]
            
            sum_b_pred = sub_b["y_pred"].sum()
            sum_b_true = sub_b["y_true"].sum()
            
            diff_pred = abs(sum_b_pred - sub_d["y_pred"])
            diff_true = abs(sum_b_true - sub_d["y_true"])
            
            cons_rows.append({
                "Model_Name": model_name,
                "Evaluation_Year": year,
                "Sum_Basins_y_pred_km3_yr": sum_b_pred,
                "DomainA_y_pred_km3_yr": sub_d["y_pred"],
                "Pred_Discrepancy_km3_yr": diff_pred,
                "Sum_Basins_y_true_km3_yr": sum_b_true,
                "DomainA_y_true_km3_yr": sub_d["y_true"],
                "True_Discrepancy_km3_yr": diff_true,
                "Is_Conserved": (diff_pred < 1e-9 and diff_true < 1e-9)
            })
            
    df_cons = pd.DataFrame(cons_rows)
    cons_csv = os.path.join(TABLES_DIR, "test_regional_mass_conservation.csv")
    df_cons.to_csv(cons_csv, index=False)
    print(f"  Regional mass conservation audit saved: {cons_csv}")
    
    # H. Prediction Interval Calibration Audit by Basin
    int_rows = []
    for model_name in ["M2_Bayesian_Ridge_Weighted", "M2_Bayesian_Ridge", "M6_Gaussian_Process"]:
        for b in ["Hp-I", "I-Ipp", "Ipp-J", "Domain_A"]:
            sub = df_preds[(df_preds["Model_Name"] == model_name) & (df_preds["Basin_ID"] == b)]
            prob = calculate_probabilistic_calibration(sub["y_true"], sub["y_pred"], sub["y_std"])
            
            # Count covered
            z_crit = 1.95996
            covered = np.sum((sub["y_true"].values >= (sub["y_pred"].values - z_crit * sub["y_std"].values)) & 
                             (sub["y_true"].values <= (sub["y_pred"].values + z_crit * sub["y_std"].values)))
            
            int_rows.append({
                "Model_Name": model_name,
                "Basin_ID": b,
                "Test_N": len(sub),
                "Covered_Count": int(covered),
                "Uncovered_Count": int(len(sub) - covered),
                "Empirical_Coverage_%": prob["coverage_95"],
                "Mean_Predictive_Std_km3_yr": float(np.mean(sub["y_std"])),
                "Mean_Interval_Width_km3_yr": prob["mean_interval_width"],
                "CRPS_km3_yr": prob["crps"]
            })
    df_int = pd.DataFrame(int_rows)
    int_csv = os.path.join(TABLES_DIR, "test_prediction_intervals.csv")
    df_int.to_csv(int_csv, index=False)
    print(f"  Prediction interval calibration table saved: {int_csv}")
    
    print("\n" + "="*80)
    print("PHASE 4C TEST EVALUATION COMPLETED SUCCESSFULLY")
    print("="*80)
    return df_preds, df_pooled, df_basin, df_cum, df_sig, df_tele

if __name__ == "__main__":
    run_test_evaluation()
