#!/usr/bin/env python
"""
Export Website Assets Script
Compiles lightweight JSON summaries for the research website frontend.
"""

import os
import sys
import json
import pandas as pd

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, REPO_ROOT)

def export():
    print("=== Exporting Interactive Website Assets ===")
    web_dir = os.path.join(REPO_ROOT, 'reports', 'website_assets')
    os.makedirs(web_dir, exist_ok=True)
    
    # 1. Model comparison table
    df_comp = pd.read_csv(os.path.join(REPO_ROOT, 'reports', 'tables', 'stage6_1_model_comparison.csv'))
    df_comp.to_json(os.path.join(web_dir, 'model_comparison.json'), orient='records', indent=2)
    
    # 2. Basin performance table
    df_basin = pd.read_csv(os.path.join(REPO_ROOT, 'reports', 'tables', 'stage6_1_basin_performance.csv'))
    df_basin.to_json(os.path.join(web_dir, 'basin_performance.json'), orient='records', indent=2)
    
    # 3. Predictions time series
    df_preds = pd.read_csv(os.path.join(REPO_ROOT, 'reports', 'tables', 'stage6_1_predictions.csv'))
    df_preds.to_json(os.path.join(web_dir, 'predictions_timeseries.json'), orient='records', indent=2)
    
    # 4. Feature importance
    df_feat = pd.read_csv(os.path.join(REPO_ROOT, 'reports', 'tables', 'stage6_1_feature_importance.csv'))
    df_feat.to_json(os.path.join(web_dir, 'feature_importance.json'), orient='records', indent=2)
    
    print(f"Exported 4 JSON assets to {web_dir}")

if __name__ == '__main__':
    export()
