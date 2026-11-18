/**
 * CryoPredict TypeScript API Type Definitions
 * Strictly adhering to backend schemas and frozen research payloads.
 */

export interface HealthResponse {
  status: 'healthy' | 'degraded';
  version: string;
  timestamp: string;
  environment: string;
  models_loaded: boolean;
  loaded_models_count: number;
  primary_model_status: string;
}

export interface BasinMetadata {
  basin_id: string;
  name: string;
  grounded_area_km2: number;
  description: string;
}

export interface OverviewResponse {
  project_title: string;
  research_scope: string;
  spatial_coverage: string;
  temporal_coverage: string;
  total_grounded_area_km2: number;
  total_ice_volume_km3: number;
  solid_ice_density_kg_m3: number;
  physical_solver: string;
  ml_benchmark_status: string;
  basins: BasinMetadata[];
  scientific_disclosures: string[];
}

export interface ModelSummary {
  model_id: string;
  model_name: string;
  model_class: string;
  hyperparameters: string;
  validation_rmse_gt_yr: number;
  validation_mae_gt_yr: number;
  validation_bias_gt_yr: number;
  validation_r2: number;
  val_mae_improvement_pct: number;
  test_refit_mae_gt_yr: number;
  test_trainonly_rmse_gt_yr: number;
  test_trainonly_mae_gt_yr: number;
  test_trainonly_r2: number;
  test_mae_improvement_pct: number;
  model_status: string;
  supports_interactive_inference: boolean;
}

export interface BasinPerformanceDetail {
  evaluation_fold: string;
  fitting_protocol: string;
  basin_id: string;
  basin_name: string;
  sample_count: number;
  true_mean_gt_yr: number;
  pred_mean_gt_yr: number;
  rmse_gt_yr: number;
  mae_gt_yr: number;
  mean_bias_gt_yr: number;
  r2: number;
  mae_improvement_pct: number;
}

export interface ModelDetailResponse {
  model_id: string;
  model_name: string;
  model_class: string;
  hyperparameters: string;
  model_status: string;
  supports_interactive_inference: boolean;
  summary_metrics: Record<string, any>;
  basin_performance: BasinPerformanceDetail[];
  feature_coefficients: Record<string, number> | null;
  feature_importances: Record<string, number> | null;
}

export interface HistoricalModelPrediction {
  pred_mb_gt_yr: number;
  pred_vol_km3_yr: number;
  residual_mb_gt_yr: number;
  uncertainty_std_gt_yr: number | null;
}

export interface HistoricalPredictionItem {
  row_id: number;
  year: number;
  basin_id: string;
  basin_name: string;
  epoch: string;
  split_status: string;
  observed_mass_balance_gt_yr: number;
  observed_volume_change_km3_yr: number;
  model_predictions: {
    Historical_Basin_Mean?: HistoricalModelPrediction;
    Persistence?: HistoricalModelPrediction;
    Bayesian_Ridge?: HistoricalModelPrediction;
    ElasticNet?: HistoricalModelPrediction;
    Random_Forest?: HistoricalModelPrediction;
    Gradient_Boosting?: HistoricalModelPrediction;
    [key: string]: HistoricalModelPrediction | undefined;
  };
}

export interface FeaturePayload {
  Target_Volume_Change_Lag1_km3_yr: number;
  Target_Volume_Change_Lag2_km3_yr: number;
  Net_MB_Lag1_Gt_yr: number;
  SMB_Lag1_Gt_yr: number;
  Discharge_Lag1_Gt_yr: number;
  SMB_Rolling3yr_Gt_yr: number;
  SMB_Anomaly_Lag1_Gt_yr: number;
  Grounded_Area_km2: number;
  Mean_Baseline_Ice_Thickness_m: number;
  Bed_Elevation_at_Gates_m: number;
  Driving_Stress_Index_kPa: number;
  is_Hp_I: number;
  is_I_Ipp: number;
  is_Ipp_J: number;
}

export interface InferenceRequest {
  model_id: string;
  basin_id: string;
  features: FeaturePayload;
  target_year?: number;
  forecast_year?: number;
  inference_mode?: 'historical' | 'manual';
}

export interface HistoricalFeaturesResponse {
  basin_id: string;
  basin_name: string;
  year: number;
  split_status: string;
  epoch: string;
  is_available: boolean;
  features: FeaturePayload;
  observed_mass_balance_gt_yr: number;
  observed_volume_change_km3_yr: number;
  temporal_explanation: string;
}

export interface InferenceResponse {
  prediction_id: string;
  timestamp: string;
  model_id: string;
  model_name: string;
  model_class: string;
  basin_id: string;
  basin_name: string;
  target_year: number | null;
  forecast_year: number | null;
  inference_mode: string;
  input_features: Record<string, number>;
  predicted_mass_balance_gt_yr: number;
  predicted_volume_change_km3_yr: number;
  density_conversion_used: string;
  uncertainty_std_gt_yr: number | null;
  uncertainty_std_km3_yr: number | null;
  prediction_type: string;
  scientific_disclosure: string;
}

export interface DatasetItem {
  inventory_id: string;
  dataset_name: string;
  temporal_coverage: string;
  spatial_coverage: string;
  physical_quantity_and_units: string;
  sample_count: number;
  missing_values_count: number;
  provenance_and_role: string;
  ml_readiness_status: string;
}

export interface FeatureItem {
  feature_id: string;
  feature_name: string;
  mathematical_symbol: string;
  feature_category: string;
  physical_units: string;
  temporal_availability: string;
  operational_lag: string;
  imputation_method: string;
  algorithm_suitability: string;
  feature_importance_hypothesis: string;
  elasticnet_coefficient: number | null;
  elasticnet_status: string | null;
}

// Stage 7.1 / 7.2 Future Projection Types

export interface ScenarioItem {
  id: string;
  name: string;
  scenario_type: 'NATIVE_ISMIP6' | 'SCALED_EMULATOR_SYNTHESIS' | string;
  scenario_watermark: string;
  tier: string;
  scaling_coefficient_alpha: number | null;
  description: string;
  provenance_note: string;
}

export interface CandidateModelComparison {
  candidate_model_name: string;
  model_type: string;
  oof_rmse_km3: number;
  oof_mae_km3: number;
  oof_bias_km3: number;
  oof_r2: number;
  mae_2050_km3: number;
  mae_2100_km3: number;
  supports_non_gaussian_quantiles: boolean;
  recommendation: string;
}

export interface LOMFOFoldResult {
  fold_index: number;
  held_out_family: string;
  member_models_count: number;
  member_models_list: string;
  test_records_count: number;
  rmse_km3: number;
  mae_km3: number;
  bias_km3: number;
  r2: number;
  empirical_coverage_68pct: number;
  mean_interval_width_km3: number;
  mae_2050_km3: number;
  mae_2100_km3: number;
  validation_gate_status: string;
}

export interface FutureModelInfoResponse {
  model_id: string;
  model_name: string;
  model_class: string;
  target_variable: string;
  density_constant_gt_km3: number;
  gmsl_conversion_gt_mm: number;
  quantiles_evaluated: number[];
  features: string[];
  supported_scenarios: string[];
  supported_basins: string[];
  validation_protocol: string;
  overall_metrics: {
    oof_r2: number;
    oof_rmse_km3: number;
    oof_mae_km3: number;
    oof_bias_km3: number;
    nominal_coverage_pct: number;
    empirical_coverage_pct: number;
    mean_interval_width_km3: number;
    mae_at_2050_km3: number;
    mae_at_2100_km3: number;
  };
  candidate_comparisons: CandidateModelComparison[];
  lomfo_folds: LOMFOFoldResult[];
  scientific_notices: string[];
}

export interface SpatialUnitInfo {
  id: string;
  name: string;
  type: string;
  sector_id: number | null;
  description: string;
}

export interface AvailabilityResponse {
  start_year: number;
  end_year: number;
  total_years: number;
  spatial_units: SpatialUnitInfo[];
  scenarios: string[];
  metrics: string[];
  total_records: number;
}

export interface TrajectoryPoint {
  year: number;
  delta_vaf_median_km3: number;
  delta_vaf_16th_km3: number;
  delta_vaf_84th_km3: number;
  delta_vaf_10th_km3: number;
  delta_vaf_90th_km3: number;
  delta_sle_median_mm: number;
  delta_sle_16th_mm: number;
  delta_sle_84th_mm: number;
  delta_sle_10th_mm: number;
  delta_sle_90th_mm: number;
}

export interface ProjectionTrajectoryResponse {
  scenario: string;
  scenario_type: string;
  scenario_watermark: string;
  spatial_unit: string;
  spatial_unit_name: string;
  start_year: number;
  end_year: number;
  point_count: number;
  target_variable: string;
  target_disclaimer: string;
  sle_formula: string;
  summary_2050?: {
    year: number;
    delta_vaf_16th_km3: number;
    delta_vaf_median_km3: number;
    delta_vaf_84th_km3: number;
    delta_vaf_10th_km3: number;
    delta_vaf_90th_km3: number;
    sle_16th_mm: number;
    sle_median_mm: number;
    sle_84th_mm: number;
    sle_10th_mm: number;
    sle_90th_mm: number;
    scenario_watermark: string;
    validation_status: string;
  };
  summary_2100?: {
    year: number;
    delta_vaf_16th_km3: number;
    delta_vaf_median_km3: number;
    delta_vaf_84th_km3: number;
    delta_vaf_10th_km3: number;
    delta_vaf_90th_km3: number;
    sle_16th_mm: number;
    sle_median_mm: number;
    sle_84th_mm: number;
    sle_10th_mm: number;
    sle_90th_mm: number;
    scenario_watermark: string;
    validation_status: string;
  };
  trajectory: TrajectoryPoint[];
}
