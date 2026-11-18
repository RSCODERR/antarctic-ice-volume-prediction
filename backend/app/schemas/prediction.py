"""
Pydantic schemas for CryoPredict model inference and feature payloads.
"""

from typing import Optional
from pydantic import BaseModel, Field, field_validator
import math

class FeaturePayload(BaseModel):
    """
    14-feature schema strictly conforming to the Stage 6.0 Feature Dictionary (FEAT-01 to FEAT-14).
    All fields are required floats and must be strictly finite (no NaN, no Inf).
    """
    Target_Volume_Change_Lag1_km3_yr: float = Field(
        ..., 
        description="Antecedent year t-1 ice volume change rate (km3/yr)"
    )
    Target_Volume_Change_Lag2_km3_yr: float = Field(
        ..., 
        description="2-year antecedent year t-2 ice volume change rate (km3/yr)"
    )
    Net_MB_Lag1_Gt_yr: float = Field(
        ..., 
        description="Antecedent year t-1 integrated net mass balance state (Gt/yr)"
    )
    SMB_Lag1_Gt_yr: float = Field(
        ..., 
        description="Antecedent year t-1 RACMO2.3p2 surface mass balance accumulation (Gt/yr)"
    )
    Discharge_Lag1_Gt_yr: float = Field(
        ..., 
        description="Antecedent year t-1 satellite flux gate ice discharge outflow (Gt/yr)"
    )
    SMB_Rolling3yr_Gt_yr: float = Field(
        ..., 
        description="3-year rolling antecedent SMB accumulation memory [t-3, t-1] (Gt/yr)"
    )
    SMB_Anomaly_Lag1_Gt_yr: float = Field(
        ..., 
        description="Antecedent SMB anomaly relative to 1979-2005 baseline mean (Gt/yr)"
    )
    Grounded_Area_km2: float = Field(
        ..., 
        description="Time-invariant grounded basin area from BedMachine V4.1 mask (km2)"
    )
    Mean_Baseline_Ice_Thickness_m: float = Field(
        ..., 
        description="Time-invariant baseline mean ice column thickness from BedMachine V4.1 (m)"
    )
    Bed_Elevation_at_Gates_m: float = Field(
        ..., 
        description="Bedrock elevation at marine grounding line flux gates (m)"
    )
    Driving_Stress_Index_kPa: float = Field(
        ..., 
        description="Gravitational driving shear stress proxy from REMA + BedMachine (kPa)"
    )
    is_Hp_I: float = Field(
        ..., 
        ge=0.0, 
        le=1.0, 
        description="Binary indicator for Palmer Land West basin (1.0 or 0.0)"
    )
    is_I_Ipp: float = Field(
        ..., 
        ge=0.0, 
        le=1.0, 
        description="Binary indicator for Graham Land basin (1.0 or 0.0)"
    )
    is_Ipp_J: float = Field(
        ..., 
        ge=0.0, 
        le=1.0, 
        description="Binary indicator for Palmer Land East basin (1.0 or 0.0)"
    )

    @field_validator("*")
    def check_finite(cls, v, info):
        if isinstance(v, (float, int)):
            if math.isnan(v) or math.isinf(v):
                raise ValueError(f"Feature '{info.field_name}' must be a finite numerical value.")
        return v

class InferenceRequest(BaseModel):
    """
    Request model for running live model inference.
    """
    model_id: str = Field(
        default="MOD-04",
        description="Identifier of verified candidate model (e.g. MOD-01 to MOD-06, or ElasticNet)"
    )
    basin_id: str = Field(
        ...,
        description="Antarctic Peninsula physical drainage basin ('Hp-I', 'I-Ipp', 'Ipp-J')"
    )
    features: FeaturePayload = Field(
        ...,
        description="Dictionary of exactly 14 features matching the frozen schema"
    )
    target_year: Optional[int] = Field(
        default=None,
        description="Historical target year (1979-2024 for historical mode). Calendar year is not an input feature to the model."
    )
    forecast_year: Optional[int] = Field(
        default=None,
        description="Backwards-compatible alias for target_year; years >= 2100 are strictly rejected."
    )
    inference_mode: str = Field(
        default="manual",
        description="Inference provenance: 'historical' (features resolved from historical records) or 'manual' (custom feature scenario)"
    )

    @field_validator("basin_id")
    def validate_basin_id(cls, v):
        allowed = {"Hp-I", "I-Ipp", "Ipp-J"}
        if v not in allowed:
            raise ValueError(f"Invalid basin_id '{v}'. Allowed basins: {sorted(allowed)}")
        return v

    @field_validator("forecast_year", "target_year")
    def validate_year_bounds(cls, v):
        if v is not None and v >= 2100:
            raise ValueError(
                "Centennial projections (year >= 2100) are strictly prohibited. "
                "These models are historical 1-year ahead autoregressive benchmarks, "
                "not century-scale climate projection engines."
            )
        return v

class HistoricalFeaturesResponse(BaseModel):
    """
    Response model for retrieving verified historical antecedent feature vectors.
    """
    basin_id: str = Field(..., description="Drainage basin identifier ('Hp-I', 'I-Ipp', 'Ipp-J')")
    basin_name: str = Field(..., description="Geographic name of drainage basin")
    year: int = Field(..., description="Target historical prediction year")
    split_status: str = Field(..., description="Chronological split ('TRAINING', 'EMBARGO', 'VALIDATION', 'TEST')")
    epoch: str = Field(..., description="Observational epoch")
    is_available: bool = Field(True, description="Whether legitimate historical observations exist")
    features: FeaturePayload = Field(..., description="Resolved 14 antecedent features from stage6_ml_dataset.csv")
    observed_mass_balance_gt_yr: float = Field(..., description="Actual observed target mass balance (Gt/yr)")
    observed_volume_change_km3_yr: float = Field(..., description="Actual observed target volume change (km3/yr)")
    temporal_explanation: str = Field(..., description="Explanation of lag construction and lookahead prevention")

class InferenceResponse(BaseModel):
    """
    Response model for live model inference.
    """
    prediction_id: str = Field(..., description="Unique UUID identifier for this prediction")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp of inference")
    model_id: str = Field(..., description="Canonical model identifier (e.g. MOD-04)")
    model_name: str = Field(..., description="Model common name (e.g. ElasticNet)")
    model_class: str = Field(..., description="Glaciological model architecture class")
    basin_id: str = Field(..., description="Evaluated drainage basin identifier")
    basin_name: str = Field(..., description="Full geographic name of basin")
    target_year: Optional[int] = Field(None, description="Historical target year if provided")
    forecast_year: Optional[int] = Field(None, description="Backwards-compatible alias for target_year")
    inference_mode: str = Field(
        default="manual",
        description="Inference provenance: 'historical' (derived from Stage 6 records) or 'manual' (custom scenario)"
    )
    input_features: dict[str, float] = Field(
        default_factory=dict,
        description="Dictionary of all 14 physical predictors evaluated by the model"
    )
    
    predicted_mass_balance_gt_yr: float = Field(
        ..., 
        description="Predicted annual solid-ice mass balance (Gt/year)"
    )
    predicted_volume_change_km3_yr: float = Field(
        ..., 
        description="Derived solid-ice volume change (km3/year) via Delta V = Delta M / 0.917"
    )
    density_conversion_used: str = Field(
        default="Delta V = Delta M / 0.917 Gt/km3 (Solid ice density: 917 kg/m3)",
        description="Governing physical density conversion formula"
    )
    uncertainty_std_gt_yr: Optional[float] = Field(
        None, 
        description="Predictive standard deviation in Gt/yr where supported by model"
    )
    uncertainty_std_km3_yr: Optional[float] = Field(
        None, 
        description="Predictive standard deviation in km3/yr where supported"
    )
    
    prediction_type: str = Field(
        default="live_inference", 
        description="Indicator distinguishing live model inference from historical recorded data"
    )
    scientific_disclosure: str = Field(
        default=(
            "Historical basin-level annual prediction regularized on 1979-2024 observations. "
            "Calendar year is NOT an input feature to the model; predictions are governed strictly by the 14 physical predictors. "
            "This is NOT a validated 2100 climate projection and must not be used for multi-decadal sea-level forecasting."
        ),
        description="Mandatory glaciological safety and scope disclosure"
    )
