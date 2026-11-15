"""
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
