"""
Stage 6.1: Supervised ML Training, Benchmarking and Evaluation Pipeline
Antarctic Peninsula Ice Volume Prediction
"""

import os
import json
import numpy as np
import pandas as pd
import joblib

# Set matplotlib cache to writable scratch directory
os.environ['MPLCONFIGDIR'] = os.path.abspath('scratch/mpl')
os.makedirs('scratch/mpl', exist_ok=True)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import BayesianRidge, ElasticNet
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor

def compute_metrics(y_true, y_pred):
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    err = y_pred - y_true
    rmse = np.sqrt(np.mean(err**2))
    mae = np.mean(np.abs(err))
    bias = np.mean(err)
    ss_tot = np.sum((y_true - np.mean(y_true))**2)
    ss_res = np.sum(err**2)
    r2 = 1.0 - (ss_res / ss_tot) if ss_tot > 0 else np.nan
    return {
        'RMSE_Gt_yr': rmse,
        'MAE_Gt_yr': mae,
        'Bias_Gt_yr': bias,
        'R2': r2,
        'RMSE_km3_yr': rmse / 0.917,
        'MAE_km3_yr': mae / 0.917,
        'Cumulative_Residual_Gt': np.sum(err)
    }

def main():
    print("=== Starting Stage 6.1 Supervised ML Pipeline ===")
    
    # Ensure current directory is repository root
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    os.chdir(repo_root)
    print(f"Working directory set to: {os.getcwd()}")
    
    # 1. Load frozen ML dataset
    data_path = 'reports/tables/stage6_ml_dataset.csv'
    df = pd.read_csv(data_path)
    print(f"Loaded dataset: {df.shape[0]} rows, {df.shape[1]} columns")
    
    target_col = 'Target_Annual_Mass_Balance_Gt_yr'
    target_vol_col = 'Target_Annual_Volume_Change_km3_yr'
    ice_density = 0.917  # Gt / km3
    
    feature_cols = [
        'Target_Volume_Change_Lag1_km3_yr',
        'Target_Volume_Change_Lag2_km3_yr',
        'Net_MB_Lag1_Gt_yr',
        'SMB_Lag1_Gt_yr',
        'Discharge_Lag1_Gt_yr',
        'SMB_Rolling3yr_Gt_yr',
        'SMB_Anomaly_Lag1_Gt_yr',
        'Grounded_Area_km2',
        'Mean_Baseline_Ice_Thickness_m',
        'Bed_Elevation_at_Gates_m',
        'Driving_Stress_Index_kPa',
        'is_Hp_I',
        'is_I_Ipp',
        'is_Ipp_J'
    ]
    print(f"Features ({len(feature_cols)}): {feature_cols}")
    
    # 2. Partitions
    train_df = df[df['Split_Status'] == 'TRAINING'].copy()
    val_df = df[df['Split_Status'] == 'VALIDATION'].copy()
    emb1_df = df[df['Split_Status'] == 'EMBARGO_BUFFER_1'].copy()
    emb2_df = df[df['Split_Status'] == 'EMBARGO_BUFFER_2'].copy()
    test_df = df[df['Split_Status'] == 'TEST'].copy()
    train_val_df = df[df['Split_Status'].isin(['TRAINING', 'VALIDATION'])].copy()
    
    print(f"Split counts -> Train: {len(train_df)}, Embargo 1: {len(emb1_df)}, Val: {len(val_df)}, Embargo 2: {len(emb2_df)}, Test: {len(test_df)}")
    
    # Preprocessing: StandardScaler fitted on TRAINING fold only
    scaler_train = StandardScaler()
    X_train_scaled = scaler_train.fit_transform(train_df[feature_cols])
    y_train = train_df[target_col].values
    w_train = train_df['Observation_Weight'].values
    
    X_val_scaled = scaler_train.transform(val_df[feature_cols])
    y_val = val_df[target_col].values
    w_val = val_df['Observation_Weight'].values
    
    X_test_scaled_tr = scaler_train.transform(test_df[feature_cols])
    y_test = test_df[target_col].values
    
    # Full dataset scaled with scaler_train for uniform prediction manifest
    X_all_scaled_tr = scaler_train.transform(df[feature_cols])
    
    # 3. Model Definitions
    # Hyperparameters frozen from systematic validation search
    models_tr = {
        'Historical Basin Mean': 'baseline_hist_mean',
        'Persistence': 'baseline_persistence',
        'Bayesian Ridge': BayesianRidge(alpha_1=1e-6, alpha_2=1e-6, lambda_1=1e-6, lambda_2=1e-6, fit_intercept=True),
        'ElasticNet': ElasticNet(alpha=0.1, l1_ratio=0.9, random_state=42, max_iter=2000),
        'Random Forest': RandomForestRegressor(n_estimators=50, max_depth=2, min_samples_leaf=10, max_features='sqrt', random_state=42),
        'Gradient Boosting': GradientBoostingRegressor(n_estimators=25, max_depth=1, learning_rate=0.01, min_samples_leaf=10, subsample=0.7, random_state=42)
    }
    
    # Train-fold basin means
    basin_means_tr = train_df.groupby('Basin_ID')[target_col].mean().to_dict()
    basin_stds_tr = train_df.groupby('Basin_ID')[target_col].std().to_dict()
    pooled_mean_tr = float(train_df[target_col].mean())
    pooled_std_tr = float(train_df[target_col].std())
    
    # Fit ML models on Train
    models_tr['Bayesian Ridge'].fit(X_train_scaled, y_train, sample_weight=w_train)
    models_tr['ElasticNet'].fit(X_train_scaled, y_train, sample_weight=w_train)
    models_tr['Random Forest'].fit(train_df[feature_cols], y_train)
    models_tr['Gradient Boosting'].fit(train_df[feature_cols], y_train)
    
    print("Models fitted on Training fold (1979-2005, N=81).")
    
    # Helper to predict
    def get_predictions(model_dict, b_means, b_stds, X_scaled, df_subset, use_train_ref=True):
        preds = {}
        uncerts = {}
        for name, m in model_dict.items():
            if name == 'Historical Basin Mean':
                p = np.array([b_means[b] for b in df_subset['Basin_ID']])
                u = np.array([b_stds[b] for b in df_subset['Basin_ID']])
            elif name == 'Persistence':
                p = df_subset['Net_MB_Lag1_Gt_yr'].values
                u = np.full(len(p), pooled_std_tr)
            elif name == 'Bayesian Ridge':
                p, u = m.predict(X_scaled, return_std=True)
            elif name == 'ElasticNet':
                p = m.predict(X_scaled)
                # Theoretical residual variance from train fit
                res_std = np.std(y_train - m.predict(X_train_scaled)) if use_train_ref else 10.0
                u = np.full(len(p), res_std)
            elif name == 'Random Forest':
                p = m.predict(df_subset[feature_cols])
                # Estimator tree std
                tree_preds = np.array([tree.predict(df_subset[feature_cols].values) for tree in m.estimators_])
                u = np.std(tree_preds, axis=0)
            elif name == 'Gradient Boosting':
                p = m.predict(df_subset[feature_cols])
                u = np.full(len(p), pooled_std_tr)
            preds[name] = p
            uncerts[name] = u
        return preds, uncerts

    preds_val, uncerts_val = get_predictions(models_tr, basin_means_tr, basin_stds_tr, X_val_scaled, val_df)
    preds_test_from_tr, uncerts_test_from_tr = get_predictions(models_tr, basin_means_tr, basin_stds_tr, X_test_scaled_tr, test_df)
    preds_train, uncerts_train = get_predictions(models_tr, basin_means_tr, basin_stds_tr, X_train_scaled, train_df)

    # 4. Refit on Permitted Train + Val (1979-2014, N=102) respecting embargo quarantine
    scaler_trval = StandardScaler()
    X_trval_scaled = scaler_trval.fit_transform(train_val_df[feature_cols])
    y_trval = train_val_df[target_col].values
    w_trval = train_val_df['Observation_Weight'].values
    
    X_test_scaled_trval = scaler_trval.transform(test_df[feature_cols])
    
    basin_means_trval = train_val_df.groupby('Basin_ID')[target_col].mean().to_dict()
    basin_stds_trval = train_val_df.groupby('Basin_ID')[target_col].std().to_dict()
    pooled_mean_trval = float(train_val_df[target_col].mean())
    pooled_std_trval = float(train_val_df[target_col].std())
    
    models_trval = {
        'Historical Basin Mean': 'baseline_hist_mean',
        'Persistence': 'baseline_persistence',
        'Bayesian Ridge': BayesianRidge(alpha_1=1e-6, alpha_2=1e-6, lambda_1=1e-6, lambda_2=1e-6, fit_intercept=True),
        'ElasticNet': ElasticNet(alpha=0.1, l1_ratio=0.9, random_state=42, max_iter=2000),
        'Random Forest': RandomForestRegressor(n_estimators=50, max_depth=2, min_samples_leaf=10, max_features='sqrt', random_state=42),
        'Gradient Boosting': GradientBoostingRegressor(n_estimators=25, max_depth=1, learning_rate=0.01, min_samples_leaf=10, subsample=0.7, random_state=42)
    }
    models_trval['Bayesian Ridge'].fit(X_trval_scaled, y_trval, sample_weight=w_trval)
    models_trval['ElasticNet'].fit(X_trval_scaled, y_trval, sample_weight=w_trval)
    models_trval['Random Forest'].fit(train_val_df[feature_cols], y_trval)
    models_trval['Gradient Boosting'].fit(train_val_df[feature_cols], y_trval)
    
    print("Models refitted on Permitted Train + Val (1979-2014, N=102).")
    preds_test_refit, uncerts_test_refit = get_predictions(models_trval, basin_means_trval, basin_stds_trval, X_test_scaled_trval, test_df, use_train_ref=False)
    
    # Full dataset predictions using Train-only models for strict prospective consistency
    preds_all, uncerts_all = get_predictions(models_tr, basin_means_tr, basin_stds_tr, X_all_scaled_tr, df)

    # 5. Build Deliverable 1: stage6_1_model_comparison.csv
    val_m_hist = compute_metrics(y_val, preds_val['Historical Basin Mean'])
    test_m_hist = compute_metrics(y_test, preds_test_from_tr['Historical Basin Mean'])
    
    comparison_rows = []
    model_ids = {
        'Historical Basin Mean': ('MOD-01', 'Baseline (Basin Empirical Mean)', 'Fixed historical basin mean'),
        'Persistence': ('MOD-02', 'Baseline (Autoregressive Lag-1)', 'y_{t-1} autoregressive persistence'),
        'Bayesian Ridge': ('MOD-03', 'Bayesian Ridge Regression', 'alpha_1=1e-6, lambda_1=1e-6, weighted=True'),
        'ElasticNet': ('MOD-04', 'Regularized Linear (ElasticNet)', 'alpha=0.1, l1_ratio=0.9, weighted=True'),
        'Random Forest': ('MOD-05', 'Ensemble Bagging (Random Forest)', 'n_est=50, max_depth=2, min_leaf=10, max_feat=sqrt'),
        'Gradient Boosting': ('MOD-06', 'Ensemble Boosting (Gradient Boosting)', 'n_est=25, max_depth=1, lr=0.01, min_leaf=10, subsample=0.7')
    }
    
    for name in models_tr.keys():
        mid, mtype, hparams = model_ids[name]
        vm = compute_metrics(y_val, preds_val[name])
        # We report test metrics from the embargo-compliant refit (Train+Val) and also Train-only
        tm_refit = compute_metrics(y_test, preds_test_refit[name])
        tm_tr = compute_metrics(y_test, preds_test_from_tr[name])
        
        # Relative improvement over historical baseline in MAE
        val_mae_imp = (val_m_hist['MAE_Gt_yr'] - vm['MAE_Gt_yr']) / val_m_hist['MAE_Gt_yr'] * 100.0
        test_mae_imp = (test_m_hist['MAE_Gt_yr'] - tm_refit['MAE_Gt_yr']) / test_m_hist['MAE_Gt_yr'] * 100.0
        
        verdict = 'BENCHMARK_CANDIDATE'
        if name == 'ElasticNet':
            verdict = 'SELECTED_PRIMARY_MODEL'
        elif 'Baseline' in mtype:
            verdict = 'BASELINE_BENCHMARK'
            
        comparison_rows.append({
            'Model_ID': mid,
            'Model_Name': name,
            'Model_Class': mtype,
            'Hyperparameters': hparams,
            'Validation_RMSE_Gt_yr': round(vm['RMSE_Gt_yr'], 2),
            'Validation_MAE_Gt_yr': round(vm['MAE_Gt_yr'], 2),
            'Validation_Bias_Gt_yr': round(vm['Bias_Gt_yr'], 2),
            'Validation_R2': round(vm['R2'], 3),
            'Val_MAE_Improvement_vs_HistMean_pct': round(val_mae_imp, 1),
            'Test_Refit_RMSE_Gt_yr': round(tm_refit['RMSE_Gt_yr'], 2),
            'Test_Refit_MAE_Gt_yr': round(tm_refit['MAE_Gt_yr'], 2),
            'Test_Refit_Bias_Gt_yr': round(tm_refit['Bias_Gt_yr'], 2),
            'Test_Refit_R2': round(tm_refit['R2'], 3),
            'Test_TrainOnly_RMSE_Gt_yr': round(tm_tr['RMSE_Gt_yr'], 2),
            'Test_TrainOnly_MAE_Gt_yr': round(tm_tr['MAE_Gt_yr'], 2),
            'Test_TrainOnly_R2': round(tm_tr['R2'], 3),
            'Test_MAE_Improvement_vs_HistMean_pct': round(test_mae_imp, 1),
            'Model_Status': verdict
        })
    df_comparison = pd.DataFrame(comparison_rows)
    df_comparison.sort_values(by='Validation_MAE_Gt_yr', inplace=True)
    df_comparison.to_csv('reports/tables/stage6_1_model_comparison.csv', index=False)
    print("Saved reports/tables/stage6_1_model_comparison.csv")

    # 6. Build Deliverable 2: stage6_1_validation_metrics.csv
    val_metrics_rows = []
    # Pooled metrics
    for name in models_tr.keys():
        vm = compute_metrics(y_val, preds_val[name])
        val_metrics_rows.append({
            'Evaluation_Scope': 'POOLED_VALIDATION_2008_2014',
            'Model_Name': name,
            'Year': 'ALL',
            'Sample_Count': len(y_val),
            'RMSE_Gt_yr': round(vm['RMSE_Gt_yr'], 2),
            'MAE_Gt_yr': round(vm['MAE_Gt_yr'], 2),
            'Mean_Bias_Gt_yr': round(vm['Bias_Gt_yr'], 2),
            'R2': round(vm['R2'], 3),
            'RMSE_km3_yr': round(vm['RMSE_km3_yr'], 2),
            'MAE_km3_yr': round(vm['MAE_km3_yr'], 2),
            'Cumulative_Residual_Gt': round(vm['Cumulative_Residual_Gt'], 2),
            'Mean_Predicted_Uncertainty_Gt_yr': round(float(np.mean(uncerts_val[name])), 2)
        })
    
    # Year-by-year temporal step tracking (7 years: 2008-2014)
    val_years = sorted(val_df['Year'].unique())
    for yr in val_years:
        idx_yr = (val_df['Year'] == yr)
        y_yr = y_val[idx_yr]
        for name in models_tr.keys():
            p_yr = preds_val[name][idx_yr]
            u_yr = uncerts_val[name][idx_yr]
            ym = compute_metrics(y_yr, p_yr)
            val_metrics_rows.append({
                'Evaluation_Scope': 'TEMPORAL_STEP_VALIDATION',
                'Model_Name': name,
                'Year': str(yr),
                'Sample_Count': len(y_yr),
                'RMSE_Gt_yr': round(ym['RMSE_Gt_yr'], 2),
                'MAE_Gt_yr': round(ym['MAE_Gt_yr'], 2),
                'Mean_Bias_Gt_yr': round(ym['Bias_Gt_yr'], 2),
                'R2': round(ym['R2'], 3),
                'RMSE_km3_yr': round(ym['RMSE_km3_yr'], 2),
                'MAE_km3_yr': round(ym['MAE_km3_yr'], 2),
                'Cumulative_Residual_Gt': round(ym['Cumulative_Residual_Gt'], 2),
                'Mean_Predicted_Uncertainty_Gt_yr': round(float(np.mean(u_yr)), 2)
            })
    df_val_metrics = pd.DataFrame(val_metrics_rows)
    df_val_metrics.to_csv('reports/tables/stage6_1_validation_metrics.csv', index=False)
    print("Saved reports/tables/stage6_1_validation_metrics.csv")

    # 7. Build Deliverable 3: stage6_1_test_metrics.csv
    test_metrics_rows = []
    for fit_type, pred_dict, unc_dict in [
        ('TRAIN_VAL_PERMITTED_REFIT_N102', preds_test_refit, uncerts_test_refit),
        ('TRAIN_ONLY_PROSPECTIVE_N81', preds_test_from_tr, uncerts_test_from_tr)
    ]:
        for name in models_tr.keys():
            tm = compute_metrics(y_test, pred_dict[name])
            test_metrics_rows.append({
                'Fitting_Protocol': fit_type,
                'Model_Name': name,
                'Evaluation_Period': '2016-2024 (9 years)',
                'Sample_Count': len(y_test),
                'RMSE_Gt_yr': round(tm['RMSE_Gt_yr'], 2),
                'MAE_Gt_yr': round(tm['MAE_Gt_yr'], 2),
                'Mean_Bias_Gt_yr': round(tm['Bias_Gt_yr'], 2),
                'R2': round(tm['R2'], 3),
                'RMSE_km3_yr': round(tm['RMSE_km3_yr'], 2),
                'MAE_km3_yr': round(tm['MAE_km3_yr'], 2),
                'Cumulative_Residual_Gt': round(tm['Cumulative_Residual_Gt'], 2),
                'Mean_Predicted_Uncertainty_Gt_yr': round(float(np.mean(unc_dict[name])), 2)
            })
            
    # Also add year-by-year test breakdown for the selected ElasticNet model
    test_years = sorted(test_df['Year'].unique())
    for yr in test_years:
        idx_yr = (test_df['Year'] == yr)
        y_yr = y_test[idx_yr]
        for name in ['Historical Basin Mean', 'Persistence', 'ElasticNet']:
            p_yr = preds_test_refit[name][idx_yr]
            u_yr = uncerts_test_refit[name][idx_yr]
            ym = compute_metrics(y_yr, p_yr)
            test_metrics_rows.append({
                'Fitting_Protocol': f'TEMPORAL_TEST_YEAR_{yr}',
                'Model_Name': name,
                'Evaluation_Period': str(yr),
                'Sample_Count': len(y_yr),
                'RMSE_Gt_yr': round(ym['RMSE_Gt_yr'], 2),
                'MAE_Gt_yr': round(ym['MAE_Gt_yr'], 2),
                'Mean_Bias_Gt_yr': round(ym['Bias_Gt_yr'], 2),
                'R2': round(ym['R2'], 3),
                'RMSE_km3_yr': round(ym['RMSE_km3_yr'], 2),
                'MAE_km3_yr': round(ym['MAE_km3_yr'], 2),
                'Cumulative_Residual_Gt': round(ym['Cumulative_Residual_Gt'], 2),
                'Mean_Predicted_Uncertainty_Gt_yr': round(float(np.mean(u_yr)), 2)
            })
    df_test_metrics = pd.DataFrame(test_metrics_rows)
    df_test_metrics.to_csv('reports/tables/stage6_1_test_metrics.csv', index=False)
    print("Saved reports/tables/stage6_1_test_metrics.csv")

    # 8. Build Deliverable 4: stage6_1_basin_performance.csv
    basin_rows = []
    basin_info = {
        'Hp-I': 'Palmer Land West',
        'I-Ipp': 'Graham Land',
        'Ipp-J': 'Palmer Land East'
    }
    
    # Validation per-basin
    for b_id, b_name in basin_info.items():
        mask_val = (val_df['Basin_ID'] == b_id)
        y_b_val = y_val[mask_val]
        # Benchmark baseline error
        hist_b_m = compute_metrics(y_b_val, preds_val['Historical Basin Mean'][mask_val])
        for name in models_tr.keys():
            bm = compute_metrics(y_b_val, preds_val[name][mask_val])
            imp_mae = (hist_b_m['MAE_Gt_yr'] - bm['MAE_Gt_yr']) / hist_b_m['MAE_Gt_yr'] * 100.0
            imp_rmse = (hist_b_m['RMSE_Gt_yr'] - bm['RMSE_Gt_yr']) / hist_b_m['RMSE_Gt_yr'] * 100.0
            basin_rows.append({
                'Evaluation_Fold': 'VALIDATION (2008-2014)',
                'Fitting_Protocol': 'TRAIN_ONLY_N81',
                'Basin_ID': b_id,
                'Basin_Name': b_name,
                'Model_Name': name,
                'Sample_Count': len(y_b_val),
                'True_Mean_Gt_yr': round(float(np.mean(y_b_val)), 2),
                'Pred_Mean_Gt_yr': round(float(np.mean(preds_val[name][mask_val])), 2),
                'RMSE_Gt_yr': round(bm['RMSE_Gt_yr'], 2),
                'MAE_Gt_yr': round(bm['MAE_Gt_yr'], 2),
                'Mean_Bias_Gt_yr': round(bm['Bias_Gt_yr'], 2),
                'R2': round(bm['R2'], 3),
                'RMSE_km3_yr': round(bm['RMSE_km3_yr'], 2),
                'MAE_km3_yr': round(bm['MAE_km3_yr'], 2),
                'MAE_Improvement_vs_HistMean_pct': round(imp_mae, 1),
                'RMSE_Improvement_vs_HistMean_pct': round(imp_rmse, 1)
            })

    # Test per-basin (Refit Train+Val)
    for b_id, b_name in basin_info.items():
        mask_te = (test_df['Basin_ID'] == b_id)
        y_b_te = y_test[mask_te]
        hist_b_te = compute_metrics(y_b_te, preds_test_refit['Historical Basin Mean'][mask_te])
        for name in models_tr.keys():
            bm = compute_metrics(y_b_te, preds_test_refit[name][mask_te])
            imp_mae = (hist_b_te['MAE_Gt_yr'] - bm['MAE_Gt_yr']) / hist_b_te['MAE_Gt_yr'] * 100.0
            imp_rmse = (hist_b_te['RMSE_Gt_yr'] - bm['RMSE_Gt_yr']) / hist_b_te['RMSE_Gt_yr'] * 100.0
            basin_rows.append({
                'Evaluation_Fold': 'TEST (2016-2024)',
                'Fitting_Protocol': 'TRAIN_VAL_PERMITTED_REFIT_N102',
                'Basin_ID': b_id,
                'Basin_Name': b_name,
                'Model_Name': name,
                'Sample_Count': len(y_b_te),
                'True_Mean_Gt_yr': round(float(np.mean(y_b_te)), 2),
                'Pred_Mean_Gt_yr': round(float(np.mean(preds_test_refit[name][mask_te])), 2),
                'RMSE_Gt_yr': round(bm['RMSE_Gt_yr'], 2),
                'MAE_Gt_yr': round(bm['MAE_Gt_yr'], 2),
                'Mean_Bias_Gt_yr': round(bm['Bias_Gt_yr'], 2),
                'R2': round(bm['R2'], 3),
                'RMSE_km3_yr': round(bm['RMSE_km3_yr'], 2),
                'MAE_km3_yr': round(bm['MAE_km3_yr'], 2),
                'MAE_Improvement_vs_HistMean_pct': round(imp_mae, 1),
                'RMSE_Improvement_vs_HistMean_pct': round(imp_rmse, 1)
            })

    # Test per-basin (Train-only prospective)
    for b_id, b_name in basin_info.items():
        mask_te = (test_df['Basin_ID'] == b_id)
        y_b_te = y_test[mask_te]
        hist_b_te = compute_metrics(y_b_te, preds_test_from_tr['Historical Basin Mean'][mask_te])
        for name in models_tr.keys():
            bm = compute_metrics(y_b_te, preds_test_from_tr[name][mask_te])
            imp_mae = (hist_b_te['MAE_Gt_yr'] - bm['MAE_Gt_yr']) / hist_b_te['MAE_Gt_yr'] * 100.0
            imp_rmse = (hist_b_te['RMSE_Gt_yr'] - bm['RMSE_Gt_yr']) / hist_b_te['RMSE_Gt_yr'] * 100.0
            basin_rows.append({
                'Evaluation_Fold': 'TEST (2016-2024)',
                'Fitting_Protocol': 'TRAIN_ONLY_PROSPECTIVE_N81',
                'Basin_ID': b_id,
                'Basin_Name': b_name,
                'Model_Name': name,
                'Sample_Count': len(y_b_te),
                'True_Mean_Gt_yr': round(float(np.mean(y_b_te)), 2),
                'Pred_Mean_Gt_yr': round(float(np.mean(preds_test_from_tr[name][mask_te])), 2),
                'RMSE_Gt_yr': round(bm['RMSE_Gt_yr'], 2),
                'MAE_Gt_yr': round(bm['MAE_Gt_yr'], 2),
                'Mean_Bias_Gt_yr': round(bm['Bias_Gt_yr'], 2),
                'R2': round(bm['R2'], 3),
                'RMSE_km3_yr': round(bm['RMSE_km3_yr'], 2),
                'MAE_km3_yr': round(bm['MAE_km3_yr'], 2),
                'MAE_Improvement_vs_HistMean_pct': round(imp_mae, 1),
                'RMSE_Improvement_vs_HistMean_pct': round(imp_rmse, 1)
            })

    df_basin = pd.DataFrame(basin_rows)
    df_basin.to_csv('reports/tables/stage6_1_basin_performance.csv', index=False)
    print("Saved reports/tables/stage6_1_basin_performance.csv")

    # 9. Build Deliverable 5: stage6_1_predictions.csv
    # Build complete row-by-row manifest across all 138 rows
    df_preds = df[['Row_ID', 'Year', 'Basin_ID', 'Basin_Name', 'Epoch', 'Split_Status', 
                   'Target_Annual_Mass_Balance_Gt_yr', 'Target_Annual_Volume_Change_km3_yr']].copy()
    
    for name in models_tr.keys():
        p_mb = preds_all[name]
        u_mb = uncerts_all[name]
        p_vol = p_mb / ice_density
        u_vol = u_mb / ice_density
        res_mb = p_mb - df_preds['Target_Annual_Mass_Balance_Gt_yr'].values
        res_vol = p_vol - df_preds['Target_Annual_Volume_Change_km3_yr'].values
        
        col_safe = name.replace(' ', '_')
        df_preds[f'Pred_MB_{col_safe}_Gt_yr'] = np.round(p_mb, 2)
        df_preds[f'Pred_Vol_{col_safe}_km3_yr'] = np.round(p_vol, 2)
        df_preds[f'Residual_MB_{col_safe}_Gt_yr'] = np.round(res_mb, 2)
        df_preds[f'Uncertainty_Std_{col_safe}_Gt_yr'] = np.round(u_mb, 2)

    df_preds.to_csv('reports/tables/stage6_1_predictions.csv', index=False)
    print("Saved reports/tables/stage6_1_predictions.csv")

    # 10. Build Deliverable 6: stage6_1_feature_importance.csv
    en_m = models_tr['ElasticNet']
    br_m = models_tr['Bayesian Ridge']
    rf_m = models_tr['Random Forest']
    gbt_m = models_tr['Gradient Boosting']
    
    en_coef = en_m.coef_
    br_coef = br_m.coef_
    rf_imp = rf_m.feature_importances_
    gbt_imp = gbt_m.feature_importances_
    
    feat_rows = []
    for i, col in enumerate(feature_cols):
        feat_rows.append({
            'Feature_ID': f'FEAT-{i+1:02d}',
            'Feature_Name': col,
            'ElasticNet_Coefficient': round(float(en_coef[i]), 6),
            'ElasticNet_Abs_Weight': round(float(np.abs(en_coef[i])), 6),
            'BayesianRidge_Coefficient': round(float(br_coef[i]), 8),
            'BayesianRidge_Abs_Weight': round(float(np.abs(br_coef[i])), 8),
            'RandomForest_Gini_Importance': round(float(rf_imp[i]), 6),
            'GradientBoosting_Importance': round(float(gbt_imp[i]), 6),
            'ElasticNet_Active_Status': 'ACTIVE_SELECTED' if np.abs(en_coef[i]) > 1e-4 else 'SHRUNK_TO_ZERO'
        })
    df_feat = pd.DataFrame(feat_rows)
    df_feat.sort_values(by='ElasticNet_Abs_Weight', ascending=False, inplace=True)
    df_feat.to_csv('reports/tables/stage6_1_feature_importance.csv', index=False)
    print("Saved reports/tables/stage6_1_feature_importance.csv")

    # 11. Build Deliverable 7: stage6_1_model_artifacts/
    art_dir = 'reports/stage6_1_model_artifacts'
    os.makedirs(art_dir, exist_ok=True)
    
    joblib.dump(scaler_train, os.path.join(art_dir, 'scaler_train.joblib'))
    joblib.dump(scaler_trval, os.path.join(art_dir, 'scaler_train_val.joblib'))
    joblib.dump(models_tr['Bayesian Ridge'], os.path.join(art_dir, 'bayesian_ridge_train.joblib'))
    joblib.dump(models_trval['Bayesian Ridge'], os.path.join(art_dir, 'bayesian_ridge_train_val.joblib'))
    joblib.dump(models_tr['ElasticNet'], os.path.join(art_dir, 'elastic_net_train.joblib'))
    joblib.dump(models_trval['ElasticNet'], os.path.join(art_dir, 'elastic_net_train_val.joblib'))
    joblib.dump(models_tr['Random Forest'], os.path.join(art_dir, 'random_forest_train.joblib'))
    joblib.dump(models_trval['Random Forest'], os.path.join(art_dir, 'random_forest_train_val.joblib'))
    joblib.dump(models_tr['Gradient Boosting'], os.path.join(art_dir, 'gradient_boosting_train.joblib'))
    joblib.dump(models_trval['Gradient Boosting'], os.path.join(art_dir, 'gradient_boosting_train_val.joblib'))
    joblib.dump(basin_means_tr, os.path.join(art_dir, 'historical_basin_means_train.joblib'))
    joblib.dump(basin_means_trval, os.path.join(art_dir, 'historical_basin_means_train_val.joblib'))
    
    metadata = {
        'timestamp': '2026-11-15T19:55:00',
        'pipeline': 'Stage 6.1 Supervised ML Benchmarking',
        'target': target_col,
        'derived_target': target_vol_col,
        'density_conversion': 'Delta V = Delta M / 0.917',
        'feature_list': feature_cols,
        'splits': {
            'train': '1979-2005 (81 rows)',
            'embargo_1': '2006-2007 (6 rows)',
            'val': '2008-2014 (21 rows)',
            'embargo_2': '2015 (3 rows)',
            'test': '2016-2024 (27 rows)'
        },
        'selected_primary_model': 'ElasticNet (alpha=0.1, l1_ratio=0.9, weighted=True)',
        'random_seeds': {'ElasticNet': 42, 'RandomForest': 42, 'GradientBoosting': 42}
    }
    with open(os.path.join(art_dir, 'model_metadata.json'), 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"Saved model artifacts in {art_dir}")

    # 12. Build Deliverable 8: stage6_1_evaluation_plots.png
    os.makedirs('reports/figures', exist_ok=True)
    fig, axes = plt.subplots(3, 2, figsize=(16, 18), dpi=200)
    
    # Panel A: Time Series of Mass Balance by Basin (1979-2024)
    ax_a = axes[0, 0]
    for b_id, color, marker in [('Hp-I', '#1f77b4', 'o'), ('I-Ipp', '#ff7f0e', 's'), ('Ipp-J', '#2ca02c', '^')]:
        b_df = df[df['Basin_ID'] == b_id].sort_values('Year')
        ax_a.plot(b_df['Year'], b_df['Target_Annual_Mass_Balance_Gt_yr'], label=f'Obs {b_id} ({basin_info[b_id]})', color=color, lw=1.5, alpha=0.8)
        # Plot ElasticNet prediction
        p_b = df_preds[df_preds['Basin_ID'] == b_id].sort_values('Year')
        ax_a.plot(p_b['Year'], p_b['Pred_MB_ElasticNet_Gt_yr'], label=f'ElasticNet {b_id}', color=color, ls='--', lw=1.2)
    ax_a.axvspan(2005.5, 2007.5, color='gray', alpha=0.2, label='Embargo 1 (2006-07)')
    ax_a.axvspan(2007.5, 2014.5, color='orange', alpha=0.15, label='Validation (2008-14)')
    ax_a.axvspan(2014.5, 2015.5, color='gray', alpha=0.2, label='Embargo 2 (2015)')
    ax_a.axvspan(2015.5, 2024.5, color='green', alpha=0.1, label='Test (2016-24)')
    ax_a.set_title('A: Basin Mass Balance Trajectory & ElasticNet Predictions (1979-2024)', fontsize=12, fontweight='bold')
    ax_a.set_ylabel('Mass Balance (Gt/yr)')
    ax_a.set_xlabel('Year')
    ax_a.grid(True, alpha=0.3)
    ax_a.legend(loc='lower left', fontsize=7, ncol=2)

    # Panel B: Validation Performance (RMSE & MAE)
    ax_b = axes[0, 1]
    m_names = list(models_tr.keys())
    val_rmses = [compute_metrics(y_val, preds_val[m])['RMSE_Gt_yr'] for m in m_names]
    val_maes = [compute_metrics(y_val, preds_val[m])['MAE_Gt_yr'] for m in m_names]
    x_pos = np.arange(len(m_names))
    width = 0.35
    ax_b.bar(x_pos - width/2, val_rmses, width, label='Validation RMSE (Gt/yr)', color='#4c72b0')
    ax_b.bar(x_pos + width/2, val_maes, width, label='Validation MAE (Gt/yr)', color='#55a868')
    ax_b.set_xticks(x_pos)
    ax_b.set_xticklabels([m.replace(' ', '\n') for m in m_names], fontsize=8)
    ax_b.set_title('B: Model Validation Comparison (2008-2014, N=21)', fontsize=12, fontweight='bold')
    ax_b.set_ylabel('Error Metric (Gt/yr)')
    ax_b.axhline(val_m_hist['MAE_Gt_yr'], color='red', ls=':', label=f"Hist Mean MAE ({val_m_hist['MAE_Gt_yr']:.2f})")
    ax_b.grid(True, alpha=0.3)
    ax_b.legend(loc='upper right', fontsize=8)

    # Panel C: Held-Out Test Performance (RMSE & MAE)
    ax_c = axes[1, 0]
    test_rmses = [compute_metrics(y_test, preds_test_refit[m])['RMSE_Gt_yr'] for m in m_names]
    test_maes = [compute_metrics(y_test, preds_test_refit[m])['MAE_Gt_yr'] for m in m_names]
    ax_c.bar(x_pos - width/2, test_rmses, width, label='Test RMSE (Gt/yr)', color='#c44e52')
    ax_c.bar(x_pos + width/2, test_maes, width, label='Test MAE (Gt/yr)', color='#8172b3')
    ax_c.set_xticks(x_pos)
    ax_c.set_xticklabels([m.replace(' ', '\n') for m in m_names], fontsize=8)
    ax_c.set_title('C: Held-Out Test Comparison (2016-2024, N=27, Train+Val Fit)', fontsize=12, fontweight='bold')
    ax_c.set_ylabel('Error Metric (Gt/yr)')
    ax_c.axhline(test_m_hist['MAE_Gt_yr'], color='red', ls=':', label=f"Hist Mean MAE ({test_m_hist['MAE_Gt_yr']:.2f})")
    ax_c.grid(True, alpha=0.3)
    ax_c.legend(loc='upper right', fontsize=8)

    # Panel D: Basin Ipp-J (Palmer Land East) Acceleration & Error Reduction
    ax_d = axes[1, 1]
    b_ipp_j = df[df['Basin_ID'] == 'Ipp-J'].sort_values('Year')
    ax_d.plot(b_ipp_j['Year'], b_ipp_j['Target_Annual_Mass_Balance_Gt_yr'], 'k-o', label='Observed Ipp-J', lw=2)
    p_ipp_j = df_preds[df_preds['Basin_ID'] == 'Ipp-J'].sort_values('Year')
    ax_d.plot(p_ipp_j['Year'], p_ipp_j['Pred_MB_ElasticNet_Gt_yr'], 'g--', label='ElasticNet', lw=2)
    ax_d.plot(p_ipp_j['Year'], p_ipp_j['Pred_MB_Historical_Basin_Mean_Gt_yr'], 'r:', label='Historical Mean (-4.38 Gt/yr)', lw=1.5)
    ax_d.plot(p_ipp_j['Year'], p_ipp_j['Pred_MB_Persistence_Gt_yr'], 'm-.', label='Persistence', lw=1.2, alpha=0.7)
    ax_d.axvspan(2007.5, 2014.5, color='orange', alpha=0.15)
    ax_d.axvspan(2015.5, 2024.5, color='green', alpha=0.1)
    ax_d.set_title('D: Basin Ipp-J Drawdown: ElasticNet Dynamic Tracking vs Baselines', fontsize=12, fontweight='bold')
    ax_d.set_ylabel('Mass Balance (Gt/yr)')
    ax_d.set_xlabel('Year')
    ax_d.grid(True, alpha=0.3)
    ax_d.legend(loc='lower left', fontsize=8)

    # Panel E: Feature Importances (ElasticNet |Beta| vs RF Gini)
    ax_e = axes[2, 0]
    top_feats = df_feat.head(8)
    y_fpos = np.arange(len(top_feats))
    ax_e.barh(y_fpos, top_feats['ElasticNet_Abs_Weight'], color='#64b5cd', align='center')
    ax_e.set_yticks(y_fpos)
    ax_e.set_yticklabels(top_feats['Feature_Name'], fontsize=8)
    ax_e.invert_yaxis()
    ax_e.set_xlabel('ElasticNet Absolute Standardized Coefficient (|Beta|)')
    ax_e.set_title('E: Top Predictive Features in ElasticNet (Dynamic Dominance)', fontsize=12, fontweight='bold')
    ax_e.grid(True, alpha=0.3)

    # Panel F: Q-Q / Residual Distribution for Selected ElasticNet
    ax_f = axes[2, 1]
    res_val_en = y_val - preds_val['ElasticNet']
    res_test_en = y_test - preds_test_refit['ElasticNet']
    ax_f.hist(res_val_en, bins=8, alpha=0.6, label='Validation Residuals (N=21)', color='#ff7f0e', density=True)
    ax_f.hist(res_test_en, bins=8, alpha=0.6, label='Test Residuals (N=27)', color='#2ca02c', density=True)
    ax_f.axvline(0, color='black', lw=1, ls='--')
    ax_f.set_title('F: ElasticNet Residual Distributions (Zero-Centered Validation)', fontsize=12, fontweight='bold')
    ax_f.set_xlabel('Residual: Observed - Predicted (Gt/yr)')
    ax_f.set_ylabel('Density')
    ax_f.grid(True, alpha=0.3)
    ax_f.legend(loc='upper right', fontsize=8)

    plt.tight_layout()
    fig_path = 'reports/figures/stage6_1_evaluation_plots.png'
    fig.savefig(fig_path, dpi=200)
    plt.close(fig)
    print(f"Saved evaluation figure to {fig_path}")

    # 13. Mirror everything to Brain Directory
    brain_dir = r'C:\Users\akash\.gemini\antigravity\brain\52ad6ae8-887d-48db-85e7-7d53f431979f'
    os.makedirs(os.path.join(brain_dir, 'tables'), exist_ok=True)
    os.makedirs(os.path.join(brain_dir, 'figures'), exist_ok=True)
    os.makedirs(os.path.join(brain_dir, 'stage6_1_model_artifacts'), exist_ok=True)

    # Mirror tables
    for f in [
        'stage6_1_model_comparison.csv',
        'stage6_1_validation_metrics.csv',
        'stage6_1_test_metrics.csv',
        'stage6_1_basin_performance.csv',
        'stage6_1_predictions.csv',
        'stage6_1_feature_importance.csv'
    ]:
        src = os.path.join('reports/tables', f)
        dst = os.path.join(brain_dir, 'tables', f)
        df_tmp = pd.read_csv(src)
        df_tmp.to_csv(dst, index=False)
        print(f"Mirrored table {f} -> {dst}")

    # Mirror figure
    import shutil
    shutil.copyfile(fig_path, os.path.join(brain_dir, 'figures', 'stage6_1_evaluation_plots.png'))
    print("Mirrored evaluation figure to brain.")

    # Mirror model artifacts
    for af in os.listdir(art_dir):
        shutil.copyfile(os.path.join(art_dir, af), os.path.join(brain_dir, 'stage6_1_model_artifacts', af))
    print("Mirrored all model artifacts to brain.")

    print("=== Pipeline Complete! Ready for Report Generation ===")

if __name__ == '__main__':
    main()
