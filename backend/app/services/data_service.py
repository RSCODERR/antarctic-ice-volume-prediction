"""
Data Service for loading, caching, and querying verified website assets and datasets.
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd

from app.config import settings

logger = logging.getLogger(__name__)

class DataService:
    """Manages verified cryosphere datasets and website JSON payloads."""

    def __init__(self):
        self.website_assets_dir: Path = settings.PATH_WEBSITE_ASSETS
        self.tables_dir: Path = settings.PATH_TABLES
        
        self.model_comparison: List[Dict[str, Any]] = []
        self.basin_performance: List[Dict[str, Any]] = []
        self.predictions_timeseries: List[Dict[str, Any]] = []
        self.feature_importance: List[Dict[str, Any]] = []
        self.datasets_inventory: List[Dict[str, Any]] = []
        self.feature_dictionary: List[Dict[str, Any]] = []
        self.historical_dataset: Dict[tuple, Dict[str, Any]] = {}
        
        self.is_loaded: bool = False
        self.load_all_data()

    def load_all_data(self):
        """Loads and caches all verified assets from disk."""
        try:
            # 1. model_comparison.json
            comp_path = self.website_assets_dir / "model_comparison.json"
            if comp_path.exists():
                with open(comp_path, "r", encoding="utf-8") as f:
                    self.model_comparison = json.load(f)
            else:
                logger.warning(f"File not found: {comp_path}")

            # 2. basin_performance.json
            basin_path = self.website_assets_dir / "basin_performance.json"
            if basin_path.exists():
                with open(basin_path, "r", encoding="utf-8") as f:
                    self.basin_performance = json.load(f)

            # 3. predictions_timeseries.json
            pred_path = self.website_assets_dir / "predictions_timeseries.json"
            if pred_path.exists():
                with open(pred_path, "r", encoding="utf-8") as f:
                    self.predictions_timeseries = json.load(f)

            # 4. feature_importance.json
            feat_imp_path = self.website_assets_dir / "feature_importance.json"
            if feat_imp_path.exists():
                with open(feat_imp_path, "r", encoding="utf-8") as f:
                    self.feature_importance = json.load(f)

            # 5. stage6_dataset_inventory.csv
            inv_csv = self.tables_dir / "stage6_dataset_inventory.csv"
            if inv_csv.exists():
                df_inv = pd.read_csv(inv_csv)
                self.datasets_inventory = df_inv.to_dict(orient="records")

            # 6. stage6_feature_dictionary.csv
            feat_csv = self.tables_dir / "stage6_feature_dictionary.csv"
            if feat_csv.exists():
                df_feat = pd.read_csv(feat_csv)
                self.feature_dictionary = df_feat.to_dict(orient="records")

            # 7. stage6_ml_dataset.csv (138 basin-year legitimate feature vectors)
            ml_csv = self.tables_dir / "stage6_ml_dataset.csv"
            if ml_csv.exists():
                df_ml = pd.read_csv(ml_csv)
                for rec in df_ml.to_dict(orient="records"):
                    self.historical_dataset[(str(rec["Basin_ID"]).upper(), int(rec["Year"]))] = rec

            self.is_loaded = True
            logger.info("Successfully loaded all verified research data and website assets.")
        except Exception as e:
            logger.error(f"Error loading research data: {str(e)}", exc_info=True)
            self.is_loaded = False

    def get_overview(self) -> Dict[str, Any]:
        """Compile verified research overview and glaciological boundaries."""
        basins_list = [
            {
                "basin_id": "Hp-I",
                "name": settings.BASINS["Hp-I"]["name"],
                "grounded_area_km2": settings.BASINS["Hp-I"]["area_km2"],
                "description": "Palmer Land West: dynamic marine-terminating ice streams facing Bellingshausen Sea."
            },
            {
                "basin_id": "I-Ipp",
                "name": settings.BASINS["I-Ipp"]["name"],
                "grounded_area_km2": settings.BASINS["I-Ipp"]["area_km2"],
                "description": "Graham Land: narrow alpine ridge with collapsed Larsen A & B tributary glaciers."
            },
            {
                "basin_id": "Ipp-J",
                "name": settings.BASINS["Ipp-J"]["name"],
                "grounded_area_km2": settings.BASINS["Ipp-J"]["area_km2"],
                "description": "Palmer Land East: massive ice discharge into Larsen C and Weddell Sea embayment."
            }
        ]
        
        return {
            "project_title": "CryoPredict: Antarctic Peninsula Ice Volume & Mass Balance Benchmark",
            "research_scope": "Physics-informed cryospheric modeling and supervised ML historical benchmarking.",
            "spatial_coverage": "Antarctic Peninsula Domain A (866,358 grounded cells)",
            "temporal_coverage": "1979 - 2024 (46 continuous calendar years)",
            "total_grounded_area_km2": settings.DOMAIN_AREA_KM2,
            "total_ice_volume_km3": settings.DOMAIN_VOLUME_KM3,
            "solid_ice_density_kg_m3": settings.SOLID_ICE_DENSITY_GT_KM3 * 1e3,
            "physical_solver": "2D Shallow Shelf Approximation (SSA) Finite-Volume Solver (Stage 5.1)",
            "ml_benchmark_status": "Stage 6.1 Supervised Historical Evaluation Complete & Frozen (ElasticNet Selected)",
            "basins": basins_list,
            "scientific_disclosures": [
                "Models are historical basin-level annual predictors regularized on 1979-2024 observations.",
                "These models are NOT 2100 climate projection engines and must not be extrapolated to century-scale forecasting.",
                "CryoSat-2 altimetry (+60.52 Gt/yr offset) remains on formal HOLD pending firn compaction corrections."
            ]
        }

    def get_models_summary(self) -> List[Dict[str, Any]]:
        """Return standardized summary for all six evaluated candidate models."""
        summaries = []
        for m in self.model_comparison:
            summaries.append({
                "model_id": m.get("Model_ID"),
                "model_name": m.get("Model_Name"),
                "model_class": m.get("Model_Class"),
                "hyperparameters": m.get("Hyperparameters"),
                "validation_rmse_gt_yr": m.get("Validation_RMSE_Gt_yr"),
                "validation_mae_gt_yr": m.get("Validation_MAE_Gt_yr"),
                "validation_bias_gt_yr": m.get("Validation_Bias_Gt_yr"),
                "validation_r2": m.get("Validation_R2"),
                "val_mae_improvement_pct": m.get("Val_MAE_Improvement_vs_HistMean_pct", 0.0),
                "test_refit_mae_gt_yr": m.get("Test_Refit_MAE_Gt_yr"),
                "test_trainonly_rmse_gt_yr": m.get("Test_TrainOnly_RMSE_Gt_yr"),
                "test_trainonly_mae_gt_yr": m.get("Test_TrainOnly_MAE_Gt_yr"),
                "test_trainonly_r2": m.get("Test_TrainOnly_R2"),
                "test_mae_improvement_pct": m.get("Test_MAE_Improvement_vs_HistMean_pct", 0.0),
                "model_status": m.get("Model_Status"),
                "supports_interactive_inference": True
            })
        return summaries

    def get_model_detail(self, model_identifier: str) -> Optional[Dict[str, Any]]:
        """Find model by Model_ID (e.g. MOD-04) or Model_Name (e.g. ElasticNet)."""
        target = None
        for m in self.model_comparison:
            if (m.get("Model_ID", "").lower() == model_identifier.lower() or 
                m.get("Model_Name", "").lower() == model_identifier.lower()):
                target = m
                break
        
        if not target:
            return None

        m_name = target.get("Model_Name")
        m_id = target.get("Model_ID")

        # Extract per-basin performance
        basin_details = []
        for b in self.basin_performance:
            if b.get("Model_Name") == m_name:
                basin_details.append({
                    "evaluation_fold": b.get("Evaluation_Fold"),
                    "fitting_protocol": b.get("Fitting_Protocol"),
                    "basin_id": b.get("Basin_ID"),
                    "basin_name": b.get("Basin_Name"),
                    "sample_count": b.get("Sample_Count"),
                    "true_mean_gt_yr": b.get("True_Mean_Gt_yr"),
                    "pred_mean_gt_yr": b.get("Pred_Mean_Gt_yr"),
                    "rmse_gt_yr": b.get("RMSE_Gt_yr"),
                    "mae_gt_yr": b.get("MAE_Gt_yr"),
                    "mean_bias_gt_yr": b.get("Mean_Bias_Gt_yr"),
                    "r2": b.get("R2"),
                    "mae_improvement_pct": b.get("MAE_Improvement_vs_HistMean_pct", 0.0)
                })

        # Feature coefficients/importances for linear/tree models
        feat_coefs = None
        feat_imps = None
        if m_name == "ElasticNet":
            feat_coefs = {
                f["Feature_Name"]: f["ElasticNet_Coefficient"] 
                for f in self.feature_importance
            }
        elif m_name == "Bayesian Ridge":
            feat_coefs = {
                f["Feature_Name"]: f["BayesianRidge_Coefficient"] 
                for f in self.feature_importance
            }
        elif m_name == "Random Forest":
            feat_imps = {
                f["Feature_Name"]: f["RandomForest_Gini_Importance"] 
                for f in self.feature_importance
            }
        elif m_name == "Gradient Boosting":
            feat_imps = {
                f["Feature_Name"]: f["GradientBoosting_Importance"] 
                for f in self.feature_importance
            }

        return {
            "model_id": m_id,
            "model_name": m_name,
            "model_class": target.get("Model_Class"),
            "hyperparameters": target.get("Hyperparameters"),
            "model_status": target.get("Model_Status"),
            "supports_interactive_inference": True,
            "summary_metrics": target,
            "basin_performance": basin_details,
            "feature_coefficients": feat_coefs,
            "feature_importances": feat_imps
        }

    def get_historical_predictions(
        self,
        basin_id: Optional[str] = None,
        year: Optional[int] = None,
        split_status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Serve the historical prediction timeseries with optional filtering."""
        results = []
        for r in self.predictions_timeseries:
            if basin_id and r.get("Basin_ID", "").upper() != basin_id.upper():
                continue
            if year is not None and r.get("Year") != year:
                continue
            if split_status and r.get("Split_Status", "").upper() != split_status.upper():
                continue
            
            # Format predictions dictionary cleanly
            model_preds = {
                "Historical_Basin_Mean": {
                    "pred_mb_gt_yr": r.get("Pred_MB_Historical_Basin_Mean_Gt_yr"),
                    "pred_vol_km3_yr": r.get("Pred_Vol_Historical_Basin_Mean_km3_yr"),
                    "residual_mb_gt_yr": r.get("Residual_MB_Historical_Basin_Mean_Gt_yr"),
                    "uncertainty_std_gt_yr": r.get("Uncertainty_Std_Historical_Basin_Mean_Gt_yr")
                },
                "Persistence": {
                    "pred_mb_gt_yr": r.get("Pred_MB_Persistence_Gt_yr"),
                    "pred_vol_km3_yr": r.get("Pred_Vol_Persistence_km3_yr"),
                    "residual_mb_gt_yr": r.get("Residual_MB_Persistence_Gt_yr"),
                    "uncertainty_std_gt_yr": r.get("Uncertainty_Std_Persistence_Gt_yr")
                },
                "Bayesian_Ridge": {
                    "pred_mb_gt_yr": r.get("Pred_MB_Bayesian_Ridge_Gt_yr"),
                    "pred_vol_km3_yr": r.get("Pred_Vol_Bayesian_Ridge_km3_yr"),
                    "residual_mb_gt_yr": r.get("Residual_MB_Bayesian_Ridge_Gt_yr"),
                    "uncertainty_std_gt_yr": r.get("Uncertainty_Std_Bayesian_Ridge_Gt_yr")
                },
                "ElasticNet": {
                    "pred_mb_gt_yr": r.get("Pred_MB_ElasticNet_Gt_yr"),
                    "pred_vol_km3_yr": r.get("Pred_Vol_ElasticNet_km3_yr"),
                    "residual_mb_gt_yr": r.get("Residual_MB_ElasticNet_Gt_yr"),
                    "uncertainty_std_gt_yr": r.get("Uncertainty_Std_ElasticNet_Gt_yr")
                },
                "Random_Forest": {
                    "pred_mb_gt_yr": r.get("Pred_MB_Random_Forest_Gt_yr"),
                    "pred_vol_km3_yr": r.get("Pred_Vol_Random_Forest_km3_yr"),
                    "residual_mb_gt_yr": r.get("Residual_MB_Random_Forest_Gt_yr"),
                    "uncertainty_std_gt_yr": r.get("Uncertainty_Std_Random_Forest_Gt_yr")
                },
                "Gradient_Boosting": {
                    "pred_mb_gt_yr": r.get("Pred_MB_Gradient_Boosting_Gt_yr"),
                    "pred_vol_km3_yr": r.get("Pred_Vol_Gradient_Boosting_km3_yr"),
                    "residual_mb_gt_yr": r.get("Residual_MB_Gradient_Boosting_Gt_yr"),
                    "uncertainty_std_gt_yr": r.get("Uncertainty_Std_Gradient_Boosting_Gt_yr")
                }
            }

            results.append({
                "row_id": r.get("Row_ID"),
                "year": r.get("Year"),
                "basin_id": r.get("Basin_ID"),
                "basin_name": r.get("Basin_Name"),
                "epoch": r.get("Epoch"),
                "split_status": r.get("Split_Status"),
                "observed_mass_balance_gt_yr": r.get("Target_Annual_Mass_Balance_Gt_yr"),
                "observed_volume_change_km3_yr": r.get("Target_Annual_Volume_Change_km3_yr"),
                "model_predictions": model_preds
            })
        return results

    def get_datasets(self) -> List[Dict[str, Any]]:
        """Return dataset catalog items."""
        items = []
        for d in self.datasets_inventory:
            items.append({
                "inventory_id": d.get("Inventory_ID", ""),
                "dataset_name": d.get("Dataset_Name", ""),
                "temporal_coverage": d.get("Temporal_Coverage", ""),
                "spatial_coverage": d.get("Spatial_Coverage", ""),
                "physical_quantity_and_units": d.get("Physical_Quantity_and_Units", ""),
                "sample_count": int(d.get("Sample_Count", 0)),
                "missing_values_count": int(d.get("Missing_Values_Count", 0)),
                "provenance_and_role": d.get("Data_Provenance_and_Role", ""),
                "ml_readiness_status": d.get("ML_Readiness_Status", "")
            })
        return items

    def get_features(self) -> List[Dict[str, Any]]:
        """Return 14-feature dictionary with ElasticNet coefficients."""
        en_weights = {
            f["Feature_Name"]: (f.get("ElasticNet_Coefficient"), f.get("ElasticNet_Active_Status"))
            for f in self.feature_importance
        }
        
        items = []
        for f in self.feature_dictionary:
            fname = f.get("Feature_Name")
            coef, status = en_weights.get(fname, (None, None))
            items.append({
                "feature_id": f.get("Feature_ID", ""),
                "feature_name": fname,
                "mathematical_symbol": f.get("Mathematical_Symbol", ""),
                "feature_category": f.get("Feature_Category", ""),
                "physical_units": f.get("Physical_Units", ""),
                "temporal_availability": f.get("Temporal_Availability", ""),
                "operational_lag": f.get("Operational_Lag", ""),
                "imputation_method": f.get("Imputation_Method_for_Missing_Lags", ""),
                "algorithm_suitability": f.get("Algorithm_Suitability", ""),
                "feature_importance_hypothesis": f.get("Feature_Importance_Hypothesis", ""),
                "elasticnet_coefficient": coef,
                "elasticnet_status": status
            })
        return items

    def get_historical_features(self, basin_id: str, year: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve legitimate 14 antecedent features for a given basin and target year from stage6_ml_dataset.csv.
        Enforces strict temporal ordering:
        - Lag-1 (t-1 observation)
        - Lag-2 (t-2 observation)
        - 3-year rolling SMB [t-3, t-1]
        - Static basin indicators and physiographic traits
        Returns None if year is outside the 1979-2024 observational record.
        """
        basin_clean = basin_id.strip()
        for b in ["Hp-I", "I-Ipp", "Ipp-J"]:
            if b.lower() == basin_clean.lower():
                basin_clean = b
                break
        
        row = self.historical_dataset.get((basin_clean.upper(), year))
        if not row:
            return None

        features = {
            "Target_Volume_Change_Lag1_km3_yr": float(row["Target_Volume_Change_Lag1_km3_yr"]),
            "Target_Volume_Change_Lag2_km3_yr": float(row["Target_Volume_Change_Lag2_km3_yr"]),
            "Net_MB_Lag1_Gt_yr": float(row["Net_MB_Lag1_Gt_yr"]),
            "SMB_Lag1_Gt_yr": float(row["SMB_Lag1_Gt_yr"]),
            "Discharge_Lag1_Gt_yr": float(row["Discharge_Lag1_Gt_yr"]),
            "SMB_Rolling3yr_Gt_yr": float(row["SMB_Rolling3yr_Gt_yr"]),
            "SMB_Anomaly_Lag1_Gt_yr": float(row["SMB_Anomaly_Lag1_Gt_yr"]),
            "Grounded_Area_km2": float(row["Grounded_Area_km2"]),
            "Mean_Baseline_Ice_Thickness_m": float(row["Mean_Baseline_Ice_Thickness_m"]),
            "Bed_Elevation_at_Gates_m": float(row["Bed_Elevation_at_Gates_m"]),
            "Driving_Stress_Index_kPa": float(row["Driving_Stress_Index_kPa"]),
            "is_Hp_I": float(row["is_Hp_I"]),
            "is_I_Ipp": float(row["is_I_Ipp"]),
            "is_Ipp_J": float(row["is_Ipp_J"]),
        }

        # Temporal explanation describing antecedent construction
        if year == 1979:
            temp_expl = (
                f"Year {year} is the first observation year. Lag-1 is imputed using the training-fold (1979–2005) "
                f"basin median as documented in FEAT-01. Zero lookahead leakage."
            )
        elif year == 1980:
            temp_expl = (
                f"Year {year}: Lag-1 is from antecedent year 1979. Lag-2 is imputed using training-fold median "
                f"as documented in FEAT-02. Zero lookahead leakage."
            )
        else:
            temp_expl = (
                f"Year {year}: Features constructed strictly from antecedent observations: Lag-1 ({year-1}), "
                f"Lag-2 ({year-2}), and rolling 3-year SMB [{year-3}, {year-1}]. Zero target-year lookahead leakage."
            )

        return {
            "basin_id": basin_clean,
            "basin_name": row.get("Basin_Name", basin_clean),
            "year": year,
            "split_status": row.get("Split_Status", "UNKNOWN"),
            "epoch": row.get("Epoch", "UNKNOWN"),
            "is_available": True,
            "features": features,
            "observed_mass_balance_gt_yr": float(row.get("Target_Annual_Mass_Balance_Gt_yr", 0.0)),
            "observed_volume_change_km3_yr": float(row.get("Target_Annual_Volume_Change_km3_yr", 0.0)),
            "temporal_explanation": temp_expl
        }

data_service = DataService()
