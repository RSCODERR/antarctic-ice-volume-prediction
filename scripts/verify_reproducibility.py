#!/usr/bin/env python
"""
Standalone Reproducibility Verification Script
Verifies model loading, feature schema, and test-set reproduction.
"""

import os
import sys
import json
import joblib
import numpy as np
import pandas as pd

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, REPO_ROOT)

def verify():
    print("=== Running Standalone Reproducibility Verification ===")
    models_dir = os.path.join(REPO_ROOT, 'models')
    data_path = os.path.join(REPO_ROOT, 'reports', 'tables', 'stage6_ml_dataset.csv')
    
    with open(os.path.join(models_dir, 'model_metadata.json')) as f:
        meta = json.load(f)
        
    scaler = joblib.load(os.path.join(models_dir, 'scaler_train.joblib'))
    model = joblib.load(os.path.join(models_dir, 'elastic_net_train.joblib'))
    df = pd.read_csv(data_path)
    
    test_df = df[df['Split_Status'] == 'TEST']
    features = meta['feature_list']
    X_test = scaler.transform(test_df[features])
    y_test = test_df['Target_Annual_Mass_Balance_Gt_yr'].values
    
    y_pred = model.predict(X_test)
    err = y_pred - y_test
    rmse = np.sqrt(np.mean(err**2))
    mae = np.mean(np.abs(err))
    ss_tot = np.sum((y_test - np.mean(y_test))**2)
    r2 = 1.0 - (np.sum(err**2) / ss_tot)
    
    print(f"Test RMSE : {rmse:.4f} Gt/yr (Target: 13.56)")
    print(f"Test MAE  : {mae:.4f} Gt/yr (Target: 9.61)")
    print(f"Test R2   : {r2:.4f} (Target: +0.069)")
    
    assert abs(round(rmse, 2) - 13.56) < 1e-3, "RMSE mismatch"
    assert abs(round(mae, 2) - 9.61) < 1e-3, "MAE mismatch"
    assert abs(round(r2, 3) - 0.069) < 1e-3, "R2 mismatch"
    print(">>> All test reproducibility checks PASSED! <<<")

if __name__ == '__main__':
    verify()
