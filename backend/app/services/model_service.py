"""
Model Service for loading serialized research models and running verified inference pipelines.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
import numpy as np
import pandas as pd
import joblib

from app.config import settings

logger = logging.getLogger(__name__)

class ModelService:
    """Manages frozen model artifacts and execution of verified inference pipelines."""

    def __init__(self):
        self.models_dir: Path = settings.PATH_MODELS_DIR
        self.is_loaded: bool = False
        
        # Artifact placeholders
        self.metadata: Dict[str, Any] = {}
        self.feature_list: list = []
        self.scaler = None
        
        self.models: Dict[str, Any] = {}
        self.hist_means: Dict[str, float] = {}
        
        # Model identifier mapping
        self.id_to_key = {
            "mod-01": "historical_basin_mean",
            "historical_basin_mean": "historical_basin_mean",
            "mod-02": "persistence",
            "persistence": "persistence",
            "mod-03": "bayesian_ridge",
            "bayesian_ridge": "bayesian_ridge",
            "mod-04": "elasticnet",
            "elasticnet": "elasticnet",
            "elastic_net": "elasticnet",
            "mod-05": "random_forest",
            "random_forest": "random_forest",
            "mod-06": "gradient_boosting",
            "gradient_boosting": "gradient_boosting"
        }
        
        self.load_artifacts()

    def load_artifacts(self):
        """Loads model artifacts and metadata once at startup."""
        try:
            # 1. Load model metadata
            meta_path = self.models_dir / "model_metadata.json"
            if not meta_path.exists():
                logger.error(f"Metadata file not found: {meta_path}")
                self.is_loaded = False
                return

            with open(meta_path, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)
            self.feature_list = self.metadata.get("feature_list", [])
            logger.info(f"Loaded metadata with {len(self.feature_list)} features.")

            # 2. Load Scaler
            scaler_path = self.models_dir / "scaler_train.joblib"
            if scaler_path.exists():
                self.scaler = joblib.load(scaler_path)
            else:
                logger.error(f"Scaler artifact not found: {scaler_path}")

            # 3. Load Primary ElasticNet Model
            en_path = self.models_dir / "elastic_net_train.joblib"
            if en_path.exists():
                self.models["elasticnet"] = joblib.load(en_path)
            else:
                logger.error(f"ElasticNet artifact not found: {en_path}")

            # 4. Load Bayesian Ridge
            br_path = self.models_dir / "bayesian_ridge_train.joblib"
            if br_path.exists():
                self.models["bayesian_ridge"] = joblib.load(br_path)

            # 5. Load Random Forest
            rf_path = self.models_dir / "random_forest_train.joblib"
            if rf_path.exists():
                self.models["random_forest"] = joblib.load(rf_path)

            # 6. Load Gradient Boosting
            gbt_path = self.models_dir / "gradient_boosting_train.joblib"
            if gbt_path.exists():
                self.models["gradient_boosting"] = joblib.load(gbt_path)

            # 7. Load Historical Basin Means
            means_path = self.models_dir / "historical_basin_means_train.joblib"
            if means_path.exists():
                self.hist_means = joblib.load(means_path)

            self.is_loaded = ("elasticnet" in self.models and self.scaler is not None)
            logger.info(f"ModelService loaded {len(self.models)} active ML models. Status: {self.is_loaded}")
        except Exception as e:
            logger.error(f"Failed to load model artifacts: {str(e)}", exc_info=True)
            self.is_loaded = False

    def validate_features(self, feature_dict: Dict[str, float]) -> pd.DataFrame:
        """
        Converts feature dictionary to DataFrame adhering strictly to feature_list order.
        Raises ValueError if any required feature is missing or non-finite.
        """
        vals = []
        for feat in self.feature_list:
            if feat not in feature_dict:
                raise ValueError(f"Missing required feature: '{feat}'")
            val = feature_dict[feat]
            if val is None or not np.isfinite(val):
                raise ValueError(f"Feature '{feat}' must be a finite numerical value, got {val}")
            vals.append(float(val))
        return pd.DataFrame([vals], columns=self.feature_list)

    def predict(
        self,
        model_identifier: str,
        basin_id: str,
        features_dict: Dict[str, float]
    ) -> Tuple[float, float, Optional[float], str, str]:
        """
        Executes verified live inference for a given model and basin.
        Returns:
            (predicted_mb_gt_yr, predicted_vol_km3_yr, uncertainty_std_gt_yr, model_id, model_name)
        """
        canonical_key = self.id_to_key.get(model_identifier.lower())
        if not canonical_key:
            raise ValueError(
                f"Invalid model_id '{model_identifier}'. Supported models: "
                "MOD-01 (Historical Basin Mean), MOD-02 (Persistence), "
                "MOD-03 (Bayesian Ridge), MOD-04 (ElasticNet), "
                "MOD-05 (Random Forest), MOD-06 (Gradient Boosting)"
            )

        # Build feature vector
        X_raw = self.validate_features(features_dict)
        pred_mb = 0.0
        uncert_std = None
        model_id_str = ""
        model_name_str = ""

        if canonical_key == "historical_basin_mean":
            model_id_str = "MOD-01"
            model_name_str = "Historical Basin Mean"
            if basin_id not in self.hist_means:
                raise ValueError(f"Unknown basin_id '{basin_id}' for historical baseline.")
            pred_mb = float(self.hist_means[basin_id])
            # Historical empirical std per basin
            basin_stds = {"Hp-I": 16.72, "I-Ipp": 9.40, "Ipp-J": 7.76}
            uncert_std = basin_stds.get(basin_id, 11.8)

        elif canonical_key == "persistence":
            model_id_str = "MOD-02"
            model_name_str = "Persistence (Lag-1)"
            # Persistence returns preceding net mass balance state
            pred_mb = float(features_dict.get("Net_MB_Lag1_Gt_yr", 0.0))
            uncert_std = 11.8

        elif canonical_key == "bayesian_ridge":
            model_id_str = "MOD-03"
            model_name_str = "Bayesian Ridge"
            if "bayesian_ridge" not in self.models:
                raise RuntimeError("Bayesian Ridge model artifact is not loaded.")
            X_scaled = self.scaler.transform(X_raw)
            p, s = self.models["bayesian_ridge"].predict(X_scaled, return_std=True)
            pred_mb = float(p[0])
            uncert_std = float(s[0])

        elif canonical_key == "elasticnet":
            model_id_str = "MOD-04"
            model_name_str = "ElasticNet (Selected Primary)"
            if "elasticnet" not in self.models:
                raise RuntimeError("ElasticNet model artifact is not loaded.")
            X_scaled = self.scaler.transform(X_raw)
            p = self.models["elasticnet"].predict(X_scaled)
            pred_mb = float(p[0])
            # Residual standard deviation on training set
            uncert_std = 11.35

        elif canonical_key == "random_forest":
            model_id_str = "MOD-05"
            model_name_str = "Random Forest"
            if "random_forest" not in self.models:
                raise RuntimeError("Random Forest model artifact is not loaded.")
            # Random forest was fitted on unscaled features DataFrame/array
            p = self.models["random_forest"].predict(X_raw)
            pred_mb = float(p[0])
            # Ensemble tree prediction standard deviation
            tree_preds = [t.predict(X_raw.to_numpy())[0] for t in self.models["random_forest"].estimators_]
            uncert_std = float(np.std(tree_preds))

        elif canonical_key == "gradient_boosting":
            model_id_str = "MOD-06"
            model_name_str = "Gradient Boosting"
            if "gradient_boosting" not in self.models:
                raise RuntimeError("Gradient Boosting model artifact is not loaded.")
            p = self.models["gradient_boosting"].predict(X_raw)
            pred_mb = float(p[0])
            uncert_std = 11.8

        # Derive solid-ice equivalent volume change using frozen density conversion:
        # Delta V = Delta M / 0.917 km3/yr
        ice_density = settings.SOLID_ICE_DENSITY_GT_KM3  # 0.917 Gt / km3
        pred_vol = pred_mb / ice_density

        return pred_mb, pred_vol, uncert_std, model_id_str, model_name_str

model_service = ModelService()
