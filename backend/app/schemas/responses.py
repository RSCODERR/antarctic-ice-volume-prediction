"""
Pydantic response models for CryoPredict API endpoints.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class HealthResponse(BaseModel):
    status: str = Field(..., description="Application health status (e.g. 'healthy')")
    version: str = Field(..., description="API software version")
    timestamp: str = Field(..., description="Current ISO 8601 UTC timestamp")
    environment: str = Field(..., description="Runtime environment")
    models_loaded: bool = Field(..., description="Whether model artifacts are successfully loaded")
    loaded_models_count: int = Field(..., description="Count of loaded model objects")
    primary_model_status: str = Field(..., description="Status of the primary ElasticNet model")

class BasinOverview(BaseModel):
    basin_id: str
    name: str
    grounded_area_km2: float
    description: str

class OverviewResponse(BaseModel):
    project_title: str
    research_scope: str
    spatial_coverage: str
    temporal_coverage: str
    total_grounded_area_km2: float
    total_ice_volume_km3: float
    solid_ice_density_kg_m3: float
    physical_solver: str
    ml_benchmark_status: str
    basins: List[BasinOverview]
    scientific_disclosures: List[str]

class ModelSummary(BaseModel):
    model_id: str
    model_name: str
    model_class: str
    hyperparameters: str
    validation_rmse_gt_yr: float
    validation_mae_gt_yr: float
    validation_bias_gt_yr: float
    validation_r2: float
    val_mae_improvement_pct: float
    test_refit_mae_gt_yr: float
    test_trainonly_rmse_gt_yr: float
    test_trainonly_mae_gt_yr: float
    test_trainonly_r2: float
    test_mae_improvement_pct: float
    model_status: str
    supports_interactive_inference: bool

class BasinPerformanceDetail(BaseModel):
    evaluation_fold: str
    fitting_protocol: str
    basin_id: str
    basin_name: str
    sample_count: int
    true_mean_gt_yr: float
    pred_mean_gt_yr: float
    rmse_gt_yr: float
    mae_gt_yr: float
    mean_bias_gt_yr: float
    r2: float
    mae_improvement_pct: float

class ModelDetailResponse(BaseModel):
    model_id: str
    model_name: str
    model_class: str
    hyperparameters: str
    model_status: str
    supports_interactive_inference: bool
    summary_metrics: Dict[str, Any]
    basin_performance: List[BasinPerformanceDetail]
    feature_coefficients: Optional[Dict[str, float]] = None
    feature_importances: Optional[Dict[str, float]] = None

class HistoricalPredictionItem(BaseModel):
    row_id: int
    year: int
    basin_id: str
    basin_name: str
    epoch: str
    split_status: str
    observed_mass_balance_gt_yr: float
    observed_volume_change_km3_yr: float
    model_predictions: Dict[str, Dict[str, Any]]

class DatasetItem(BaseModel):
    inventory_id: str
    dataset_name: str
    temporal_coverage: str
    spatial_coverage: str
    physical_quantity_and_units: str
    sample_count: int
    missing_values_count: int
    provenance_and_role: str
    ml_readiness_status: str

class FeatureItem(BaseModel):
    feature_id: str
    feature_name: str
    mathematical_symbol: str
    feature_category: str
    physical_units: str
    temporal_availability: str
    operational_lag: str
    imputation_method: str
    algorithm_suitability: str
    feature_importance_hypothesis: str
    elasticnet_coefficient: Optional[float] = None
    elasticnet_status: Optional[str] = None
