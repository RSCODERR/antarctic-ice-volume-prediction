"""
Pydantic schemas for CryoPredict future projections (Stage 7.1/7.2).
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class ScenarioItem(BaseModel):
    id: str = Field(..., description="Scenario identifier (e.g. 'RCP8.5', 'RCP2.6', 'SSP2-4.5')")
    name: str = Field(..., description="Human-readable scenario title")
    scenario_type: str = Field(..., description="Provenance category ('NATIVE_ISMIP6' or 'SCALED_EMULATOR_SYNTHESIS')")
    scenario_watermark: str = Field(..., description="Exact scenario watermark label")
    tier: str = Field(..., description="ISMIP6 simulation tier or 'Derived'")
    scaling_coefficient_alpha: Optional[float] = Field(None, description="Radiative forcing pattern scaling coefficient if derived")
    description: str = Field(..., description="Brief scenario overview")
    provenance_note: str = Field(..., description="Detailed provenance and simulation methodology note")

class CandidateModelComparison(BaseModel):
    candidate_model_name: str
    model_type: str
    oof_rmse_km3: float
    oof_mae_km3: float
    oof_bias_km3: float
    oof_r2: float
    mae_2050_km3: float
    mae_2100_km3: float
    supports_non_gaussian_quantiles: bool
    recommendation: str

class LOMFOFoldResult(BaseModel):
    fold_index: int
    held_out_family: str
    member_models_count: int
    member_models_list: str
    test_records_count: int
    rmse_km3: float
    mae_km3: float
    bias_km3: float
    r2: float
    empirical_coverage_68pct: float
    mean_interval_width_km3: float
    mae_2050_km3: float
    mae_2100_km3: float
    validation_gate_status: str

class FutureModelInfoResponse(BaseModel):
    model_id: str
    model_name: str
    model_class: str
    target_variable: str
    density_constant_gt_km3: float
    gmsl_conversion_gt_mm: float
    quantiles_evaluated: List[float]
    features: List[str]
    supported_scenarios: List[str]
    supported_basins: List[str]
    validation_protocol: str
    overall_metrics: Dict[str, Any]
    candidate_comparisons: List[CandidateModelComparison]
    lomfo_folds: List[LOMFOFoldResult]
    scientific_notices: List[str]

class SpatialUnitInfo(BaseModel):
    id: str
    name: str
    type: str
    sector_id: Optional[int]
    description: str

class AvailabilityResponse(BaseModel):
    start_year: int
    end_year: int
    total_years: int
    spatial_units: List[SpatialUnitInfo]
    scenarios: List[str]
    metrics: List[str]
    total_records: int

class TrajectoryPoint(BaseModel):
    year: int
    delta_vaf_median_km3: float
    delta_vaf_16th_km3: float
    delta_vaf_84th_km3: float
    delta_vaf_10th_km3: float
    delta_vaf_90th_km3: float
    delta_sle_median_mm: float
    delta_sle_16th_mm: float
    delta_sle_84th_mm: float
    delta_sle_10th_mm: float
    delta_sle_90th_mm: float

class ProjectionTrajectoryResponse(BaseModel):
    scenario: str
    scenario_type: str
    scenario_watermark: str
    spatial_unit: str
    spatial_unit_name: str
    start_year: int
    end_year: int
    point_count: int
    target_variable: str
    target_disclaimer: str
    sle_formula: str
    summary_2050: Optional[Dict[str, Any]] = None
    summary_2100: Optional[Dict[str, Any]] = None
    trajectory: List[TrajectoryPoint]
