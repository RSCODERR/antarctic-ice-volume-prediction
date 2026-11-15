#!/usr/bin/env python
"""
Standalone Inference Runner CLI
Loads ElasticNet model and produces mass balance and volume predictions.
"""

import os
import sys
import pandas as pd

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, REPO_ROOT)

from src.api import AntarcticPredictionService

def run():
    service = AntarcticPredictionService()
    data_path = os.path.join(REPO_ROOT, 'reports', 'tables', 'stage6_ml_dataset.csv')
    df = pd.read_csv(data_path)
    
    mb_preds = service.predict_mass_balance(df)
    vol_preds = service.predict_volume_change(df)
    
    out_df = df[['Row_ID', 'Year', 'Basin_ID', 'Split_Status', 'Target_Annual_Mass_Balance_Gt_yr']].copy()
    out_df['Predicted_Mass_Balance_Gt_yr'] = mb_preds.round(2)
    out_df['Predicted_Volume_Change_km3_yr'] = vol_preds.round(2)
    
    out_path = os.path.join(REPO_ROOT, 'reports', 'tables', 'interactive_inference_sample.csv')
    out_df.to_csv(out_path, index=False)
    print(f"Inference complete on {len(out_df)} instances. Sample saved to {out_path}")

if __name__ == '__main__':
    run()
