"""
Unit tests for Machine Learning artifacts, preprocessing pipelines, and prediction services.
"""

import os
import sys
import json
import joblib
import unittest
import numpy as np
import pandas as pd

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
MODELS_DIR = os.path.join(REPO_ROOT, 'models')
DATA_PATH = os.path.join(REPO_ROOT, 'reports', 'tables', 'stage6_ml_dataset.csv')
PREDS_PATH = os.path.join(REPO_ROOT, 'reports', 'tables', 'stage6_1_predictions.csv')

class TestMLArtifacts(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.meta_path = os.path.join(MODELS_DIR, 'model_metadata.json')
        with open(cls.meta_path, 'r', encoding='utf-8') as f:
            cls.metadata = json.load(f)
            
        cls.scaler = joblib.load(os.path.join(MODELS_DIR, 'scaler_train.joblib'))
        cls.elastic_net = joblib.load(os.path.join(MODELS_DIR, 'elastic_net_train.joblib'))
        cls.bayesian_ridge = joblib.load(os.path.join(MODELS_DIR, 'bayesian_ridge_train.joblib'))
        cls.random_forest = joblib.load(os.path.join(MODELS_DIR, 'random_forest_train.joblib'))
        cls.gradient_boosting = joblib.load(os.path.join(MODELS_DIR, 'gradient_boosting_train.joblib'))
        cls.hist_means = joblib.load(os.path.join(MODELS_DIR, 'historical_basin_means_train.joblib'))
        
        cls.df = pd.read_csv(DATA_PATH)
        cls.preds_df = pd.read_csv(PREDS_PATH)

    def test_artifact_loadability(self):
        """Verify all six model artifacts and preprocessing pipelines load properly."""
        self.assertIsNotNone(self.scaler)
        self.assertIsNotNone(self.elastic_net)
        self.assertIsNotNone(self.bayesian_ridge)
        self.assertIsNotNone(self.random_forest)
        self.assertIsNotNone(self.gradient_boosting)
        self.assertIsInstance(self.hist_means, dict)

    def test_feature_schema(self):
        """Verify that exactly 14 features are preserved in the metadata schema."""
        features = self.metadata['feature_list']
        self.assertEqual(len(features), 14)
        self.assertEqual(features[0], 'Target_Volume_Change_Lag1_km3_yr')
        self.assertEqual(features[-1], 'is_Ipp_J')
        self.assertIn('SMB_Anomaly_Lag1_Gt_yr', features)
        self.assertIn('Discharge_Lag1_Gt_yr', features)

    def test_elasticnet_test_reproducibility(self):
        """Verify ElasticNet reproduces the reported test-fold metrics."""
        test_df = self.df[self.df['Split_Status'] == 'TEST']
        features = self.metadata['feature_list']
        X_test = self.scaler.transform(test_df[features])
        y_test = test_df['Target_Annual_Mass_Balance_Gt_yr'].values
        
        y_pred = self.elastic_net.predict(X_test)
        err = y_pred - y_test
        rmse = np.sqrt(np.mean(err**2))
        mae = np.mean(np.abs(err))
        ss_tot = np.sum((y_test - np.mean(y_test))**2)
        r2 = 1.0 - (np.sum(err**2) / ss_tot)
        
        self.assertAlmostEqual(round(rmse, 2), 13.56, places=2)
        self.assertAlmostEqual(round(mae, 2), 9.61, places=2)
        self.assertAlmostEqual(round(r2, 3), 0.069, places=3)

    def test_volume_conversion_consistency(self):
        """Verify that volume change equals mass balance divided by 0.917."""
        mb = self.preds_df['Pred_MB_ElasticNet_Gt_yr'].values
        vol = self.preds_df['Pred_Vol_ElasticNet_km3_yr'].values
        expected_vol = np.round(mb / 0.917, 2)
        np.testing.assert_allclose(vol, expected_vol, atol=0.02)

    def test_prediction_manifest_exact_match(self):
        """Verify predictions in stage6_1_predictions.csv match loaded model output."""
        features = self.metadata['feature_list']
        X_all = self.scaler.transform(self.df[features])
        direct_preds = np.round(self.elastic_net.predict(X_all), 2)
        manifest_preds = self.preds_df['Pred_MB_ElasticNet_Gt_yr'].values
        np.testing.assert_allclose(direct_preds, manifest_preds, atol=1e-4)

    def test_api_service(self):
        """Verify AntarcticPredictionService facade produces identical predictions."""
        from src.api import AntarcticPredictionService
        service = AntarcticPredictionService(models_dir=MODELS_DIR)
        mb_preds = service.predict_mass_balance(self.df)
        self.assertEqual(len(mb_preds), 138)
        self.assertEqual(service.get_basin_baseline('Hp-I'), self.hist_means['Hp-I'])

if __name__ == '__main__':
    unittest.main()
