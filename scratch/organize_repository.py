"""
Script to organize repository directories, populate models/, figures/, scripts/, and create modular facades.
"""

import os
import shutil
import glob

def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    os.chdir(repo_root)
    print(f"Working directory: {os.getcwd()}")

    # 1. Populate models/ with fitted artifacts
    os.makedirs('models', exist_ok=True)
    src_artifacts = 'reports/stage6_1_model_artifacts'
    for f in os.listdir(src_artifacts):
        src_file = os.path.join(src_artifacts, f)
        dst_file = os.path.join('models', f)
        shutil.copy2(src_file, dst_file)
        print(f"Copied model artifact: {f} -> models/{f}")

    # 2. Populate root figures/
    os.makedirs('figures', exist_ok=True)
    src_figures = 'reports/figures'
    for f in os.listdir(src_figures):
        if f.endswith('.png'):
            src_file = os.path.join(src_figures, f)
            dst_file = os.path.join('figures', f)
            shutil.copy2(src_file, dst_file)
    print(f"Copied figures to root figures/ ({len(os.listdir('figures'))} files)")

    # 3. Create src/ml facade
    os.makedirs('src/ml', exist_ok=True)
    ml_init = '''"""
ML module facade for Antarctic Ice Volume Prediction.
Exposes baseline and trained regression models from src.models.
"""

from src.models.baseline_models import BasinHistoricalMeanModel, BasinPersistenceModel
from src.models.linear_models import BayesianRidgeModel, ElasticNetModel
from src.models.tree_models import ShallowRandomForestModel, ConstrainedGradientBoostingModel

__all__ = [
    "BasinHistoricalMeanModel",
    "BasinPersistenceModel",
    "BayesianRidgeModel",
    "ElasticNetModel",
    "ShallowRandomForestModel",
    "ConstrainedGradientBoostingModel"
]
'''
    with open('src/ml/__init__.py', 'w', encoding='utf-8') as f:
        f.write(ml_init)
    print("Created src/ml/__init__.py")

    # 4. Create src/data facade
    os.makedirs('src/data', exist_ok=True)
    data_init = '''"""
Data module facade for Antarctic Ice Volume Prediction.
Provides utilities for accessing raw, processed, and feature datasets.
"""

import os
import pandas as pd

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

def get_ml_dataset() -> pd.DataFrame:
    """Load the frozen Stage 6.0 ML dataset."""
    path = os.path.join(REPO_ROOT, 'reports', 'tables', 'stage6_ml_dataset.csv')
    return pd.read_csv(path)

def get_temporal_splits() -> pd.DataFrame:
    """Load the frozen Stage 6.0 temporal split manifest."""
    path = os.path.join(REPO_ROOT, 'reports', 'tables', 'stage6_temporal_split_manifest.csv')
    return pd.read_csv(path)

def get_feature_dictionary() -> pd.DataFrame:
    """Load the feature dictionary."""
    path = os.path.join(REPO_ROOT, 'reports', 'tables', 'stage6_feature_dictionary.csv')
    return pd.read_csv(path)
'''
    with open('src/data/__init__.py', 'w', encoding='utf-8') as f:
        f.write(data_init)
    print("Created src/data/__init__.py")

    # 5. Create src/api facade
    os.makedirs('src/api', exist_ok=True)
    api_init = '''"""
API module for serving Antarctic Peninsula ice-volume and mass-balance predictions.
Designed for lightweight integration with interactive research websites.
"""

import os
import json
import joblib
import numpy as np
import pandas as pd

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
MODELS_DIR = os.path.join(REPO_ROOT, 'models')

class AntarcticPredictionService:
    """Inference service for the calibrated Antarctic Peninsula ML models."""
    
    def __init__(self, models_dir: str = MODELS_DIR):
        self.models_dir = models_dir
        self.meta_path = os.path.join(models_dir, 'model_metadata.json')
        with open(self.meta_path, 'r', encoding='utf-8') as f:
            self.metadata = json.load(f)
            
        self.feature_list = self.metadata['feature_list']
        self.ice_density = 0.917  # Gt / km3
        
        # Load scaler and primary ElasticNet model
        self.scaler = joblib.load(os.path.join(models_dir, 'scaler_train.joblib'))
        self.elastic_net = joblib.load(os.path.join(models_dir, 'elastic_net_train.joblib'))
        self.hist_means = joblib.load(os.path.join(models_dir, 'historical_basin_means_train.joblib'))

    def predict_mass_balance(self, features_df: pd.DataFrame) -> np.ndarray:
        """Predict annual mass balance in Gt/yr."""
        X_scaled = self.scaler.transform(features_df[self.feature_list])
        return self.elastic_net.predict(X_scaled)

    def predict_volume_change(self, features_df: pd.DataFrame) -> np.ndarray:
        """Predict solid-ice volume change in km3/yr (Delta V = Delta M / 0.917)."""
        mb = self.predict_mass_balance(features_df)
        return mb / self.ice_density

    def get_basin_baseline(self, basin_id: str) -> float:
        """Return historical mean baseline for basin (Hp-I, I-Ipp, Ipp-J)."""
        return self.hist_means.get(basin_id, -3.89)
'''
    with open('src/api/__init__.py', 'w', encoding='utf-8') as f:
        f.write(api_init)
    print("Created src/api/__init__.py")

    # 6. Create scripts directory
    os.makedirs('scripts', exist_ok=True)
    
    # 6a. scripts/verify_reproducibility.py
    script_verify = '''#!/usr/bin/env python
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
'''
    with open('scripts/verify_reproducibility.py', 'w', encoding='utf-8') as f:
        f.write(script_verify)
    print("Created scripts/verify_reproducibility.py")

    # 6b. scripts/run_inference.py
    script_infer = '''#!/usr/bin/env python
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
'''
    with open('scripts/run_inference.py', 'w', encoding='utf-8') as f:
        f.write(script_infer)
    print("Created scripts/run_inference.py")

    # 6c. scripts/export_website_assets.py
    script_export = '''#!/usr/bin/env python
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
'''
    with open('scripts/export_website_assets.py', 'w', encoding='utf-8') as f:
        f.write(script_export)
    print("Created scripts/export_website_assets.py")

    print("=== Organization Pipeline Complete! ===")

if __name__ == '__main__':
    main()
