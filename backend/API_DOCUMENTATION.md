# CryoPredict REST API Documentation

**Version:** 1.0.0  
**Base URL:** `http://localhost:8000` (development) or configured production origin  
**OpenAPI Specification:** Available at `/openapi.json`, with interactive UIs at `/docs` (Swagger) and `/redoc` (ReDoc).

---

## 1. General Principles & Glaciological Disclosures

1. **Research Baseline:** Exposes frozen Stage 6.1 / 6.2 machine-learning benchmarks and Stage 5.1 transient physical modeling diagnostics for the Antarctic Peninsula.
2. **Two-Tier Prediction System:**
   - **Historical Manifest:** `/api/predictions/historical` serves pre-computed, verified 1979–2024 annual predictions across all 3 drainage basins.
   - **Live Inference Engine:** `/api/predictions/run` executes actual saved scikit-learn models (`models/elastic_net_train.joblib`, etc.) on dynamically submitted 14-feature payloads.
3. **Glaciological Density Conversion:** Annual solid-ice mass balance ($\Delta M$, in Gt/year) is translated into equivalent ice volume change ($\Delta V$, in $\text{km}^3/\text{year}$) using the frozen constant:
   $$\Delta V = \frac{\Delta M}{\rho_{\text{ice}}} = \frac{\Delta M}{0.917\text{ Gt/km}^3}$$
4. **Centennial Forecasting Restriction:** Requests specifying a `forecast_year >= 2100` are strictly rejected with HTTP 422. The ML candidates are historical 1-year ahead autoregressive benchmarks, not century-scale climate projection engines.

---

## 2. API Endpoints

### 2.1 System & Health

#### `GET /`
Returns platform identity, version, available endpoints, and scientific disclosures.

**Response Example (`200 OK`):**
```json
{
  "platform": "CryoPredict API",
  "version": "1.0.0",
  "status": "online",
  "documentation": "/docs",
  "health": "/api/health",
  "overview": "/api/overview",
  "models": "/api/models",
  "scientific_notice": "CryoPredict is an academic research platform for the Antarctic Peninsula. ML models are historical basin-level annual predictors, NOT 2100 climate projection engines."
}
```

#### `GET /api/health`
Returns backend service health, timestamp, and machine-learning model loading status.

**Response Example (`200 OK`):**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-11-15T15:20:00.123456+00:00",
  "environment": "production",
  "models_loaded": true,
  "loaded_models_count": 4,
  "primary_model_status": "READY"
}
```

---

### 2.2 Project Overview & Glaciological Domain

#### `GET /api/overview`
Provides high-level scientific metadata, total grounded ice domain geometry, density constants, and drainage basin specifications.

**Response Example (`200 OK`):**
```json
{
  "project_title": "CryoPredict: Antarctic Peninsula Ice Volume & Mass Balance Benchmark",
  "research_scope": "Physics-informed cryospheric modeling and supervised ML historical benchmarking.",
  "spatial_coverage": "Antarctic Peninsula Domain A (866,358 grounded cells)",
  "temporal_coverage": "1979 - 2024 (46 continuous calendar years)",
  "total_grounded_area_km2": 216062.17,
  "total_ice_volume_km3": 140702.51,
  "solid_ice_density_kg_m3": 917.0,
  "physical_solver": "2D Shallow Shelf Approximation (SSA) Finite-Volume Solver (Stage 5.1)",
  "ml_benchmark_status": "Stage 6.1 Supervised Historical Evaluation Complete & Frozen (ElasticNet Selected)",
  "basins": [
    {
      "basin_id": "Hp-I",
      "name": "Palmer Land West",
      "grounded_area_km2": 108945.63,
      "description": "Palmer Land West: dynamic marine-terminating ice streams facing Bellingshausen Sea."
    },
    {
      "basin_id": "I-Ipp",
      "name": "Graham Land",
      "grounded_area_km2": 38616.54,
      "description": "Graham Land: narrow alpine ridge with collapsed Larsen A & B tributary glaciers."
    },
    {
      "basin_id": "Ipp-J",
      "name": "Palmer Land East",
      "grounded_area_km2": 68500.0,
      "description": "Palmer Land East: massive ice discharge into Larsen C and Weddell Sea embayment."
    }
  ],
  "scientific_disclosures": [
    "Models are historical basin-level annual predictors regularized on 1979-2024 observations.",
    "These models are NOT 2100 climate projection engines and must not be extrapolated to century-scale forecasting.",
    "CryoSat-2 altimetry (+60.52 Gt/yr offset) remains on formal HOLD pending firn compaction corrections."
  ]
}
```

---

### 2.3 Model Catalog & Benchmark Diagnostics

#### `GET /api/models`
Returns a summary list of all six evaluated candidate models, including hyperparameters, validation metrics, test metrics, and baseline improvement percentages.

**Response Example (`200 OK`):**
```json
[
  {
    "model_id": "MOD-04",
    "model_name": "ElasticNet",
    "model_class": "Regularized Linear (L1 + L2)",
    "hyperparameters": "alpha=0.10, l1_ratio=0.50, max_iter=2000, tol=1e-4",
    "validation_rmse_gt_yr": 14.77,
    "validation_mae_gt_yr": 12.09,
    "validation_bias_gt_yr": 0.81,
    "validation_r2": -0.061,
    "val_mae_improvement_pct": 1.2,
    "test_refit_mae_gt_yr": 9.52,
    "test_trainonly_rmse_gt_yr": 13.56,
    "test_trainonly_mae_gt_yr": 9.61,
    "test_trainonly_r2": 0.069,
    "test_mae_improvement_pct": 21.0,
    "model_status": "SELECTED_PRIMARY_MODEL",
    "supports_interactive_inference": true
  }
]
```

#### `GET /api/models/comparison`
Returns the raw comparison matrix across all candidate models, matching `model_comparison.json`.

#### `GET /api/models/{model_id}`
Returns detailed specifications for an individual model identified by ID (e.g. `MOD-04`) or name (e.g. `ElasticNet`), including per-basin evaluation breakdowns and learned feature coefficients or importances.

**Path Parameters:**
- `model_id` (string, required): Canonical identifier (`MOD-01` to `MOD-06`) or common model name.

**Response Example (`200 OK` for `MOD-04`):**
```json
{
  "model_id": "MOD-04",
  "model_name": "ElasticNet",
  "model_class": "Regularized Linear (L1 + L2)",
  "hyperparameters": "alpha=0.10, l1_ratio=0.50, max_iter=2000, tol=1e-4",
  "model_status": "SELECTED_PRIMARY_MODEL",
  "supports_interactive_inference": true,
  "summary_metrics": { ... },
  "basin_performance": [
    {
      "evaluation_fold": "Validation (2008-2014)",
      "fitting_protocol": "Train-Only (1979-2005)",
      "basin_id": "Hp-I",
      "basin_name": "Palmer Land West",
      "sample_count": 7,
      "true_mean_gt_yr": -16.53,
      "pred_mean_gt_yr": -7.78,
      "rmse_gt_yr": 17.65,
      "mae_gt_yr": 15.65,
      "mean_bias_gt_yr": 8.75,
      "r2": -0.211,
      "mae_improvement_pct": -4.2
    }
  ],
  "feature_coefficients": {
    "Target_Volume_Change_Lag1_km3_yr": -0.835496,
    "Target_Volume_Change_Lag2_km3_yr": -0.0,
    "Net_MB_Lag1_Gt_yr": -0.32049,
    "SMB_Lag1_Gt_yr": 0.0,
    "Discharge_Lag1_Gt_yr": -0.0,
    "SMB_Rolling3yr_Gt_yr": -0.0,
    "SMB_Anomaly_Lag1_Gt_yr": -7.083343,
    "Grounded_Area_km2": -0.0,
    "Mean_Baseline_Ice_Thickness_m": -0.0,
    "Bed_Elevation_at_Gates_m": -0.0,
    "Driving_Stress_Index_kPa": -0.0,
    "is_Hp_I": 0.0,
    "is_I_Ipp": 1.269098,
    "is_Ipp_J": -0.0
  },
  "feature_importances": null
}
```

---

### 2.4 Predictions & Live Interactive Inference

#### `GET /api/predictions/historical`
Retrieves pre-computed historical timeseries (1979–2024, 138 basin-year entries) with observed mass balance, observed volume change, and individual model predictions.

**Query Parameters:**
- `basin_id` (optional, string): Filter by basin (`Hp-I`, `I-Ipp`, `Ipp-J`).
- `year` (optional, integer): Filter by calendar year (1979–2024).
- `split_status` (optional, string): Filter by chronological split (`TRAINING`, `EMBARGO`, `VALIDATION`, `TEST`).

**Response Example (`200 OK`):**
```json
[
  {
    "row_id": 1,
    "year": 1979,
    "basin_id": "Hp-I",
    "basin_name": "Palmer Land West",
    "epoch": "PRE_SATELLITE",
    "split_status": "TRAINING",
    "observed_mass_balance_gt_yr": -10.42,
    "observed_volume_change_km3_yr": -11.36,
    "model_predictions": {
      "ElasticNet": {
        "pred_mb_gt_yr": -8.12,
        "pred_vol_km3_yr": -8.85,
        "residual_mb_gt_yr": -2.30,
        "uncertainty_std_gt_yr": 11.35
      }
    }
  }
]
```

#### `POST /api/predictions/run`
Executes real-time inference using the verified saved machine-learning models.

**Request Headers:** `Content-Type: application/json`

**Request Body Schema (`InferenceRequest`):**
- `model_id` (string, default: `"MOD-04"`): Candidate model to execute (`MOD-01` to `MOD-06` or model name).
- `basin_id` (string, required): Target drainage basin (`"Hp-I"`, `"I-Ipp"`, `"Ipp-J"`).
- `forecast_year` (integer, optional): Prediction year. **Must be strictly < 2100.**
- `features` (object, required): Exactly 14 finite numerical features adhering to Stage 6.0 schema:
  - `Target_Volume_Change_Lag1_km3_yr` (float)
  - `Target_Volume_Change_Lag2_km3_yr` (float)
  - `Net_MB_Lag1_Gt_yr` (float)
  - `SMB_Lag1_Gt_yr` (float)
  - `Discharge_Lag1_Gt_yr` (float)
  - `SMB_Rolling3yr_Gt_yr` (float)
  - `SMB_Anomaly_Lag1_Gt_yr` (float)
  - `Grounded_Area_km2` (float)
  - `Mean_Baseline_Ice_Thickness_m` (float)
  - `Bed_Elevation_at_Gates_m` (float)
  - `Driving_Stress_Index_kPa` (float)
  - `is_Hp_I` (float: 0.0 or 1.0)
  - `is_I_Ipp` (float: 0.0 or 1.0)
  - `is_Ipp_J` (float: 0.0 or 1.0)

**Curl Request Example:**
```bash
curl -X POST "http://localhost:8000/api/predictions/run" \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": "MOD-04",
    "basin_id": "Hp-I",
    "forecast_year": 2025,
    "features": {
      "Target_Volume_Change_Lag1_km3_yr": -42.42,
      "Target_Volume_Change_Lag2_km3_yr": -4.09,
      "Net_MB_Lag1_Gt_yr": -3.76,
      "SMB_Lag1_Gt_yr": 67.24,
      "Discharge_Lag1_Gt_yr": 71.00,
      "SMB_Rolling3yr_Gt_yr": 68.50,
      "SMB_Anomaly_Lag1_Gt_yr": -1.26,
      "Grounded_Area_km2": 108945.63,
      "Mean_Baseline_Ice_Thickness_m": 1482.40,
      "Bed_Elevation_at_Gates_m": -124.20,
      "Driving_Stress_Index_kPa": 105.40,
      "is_Hp_I": 1.0,
      "is_I_Ipp": 0.0,
      "is_Ipp_J": 0.0
    }
  }'
```

**Response Example (`200 OK`):**
```json
{
  "prediction_id": "b3e0e7a2-f542-4f0e-b81b-5633a647038a",
  "timestamp": "2026-11-15T15:25:00.123456+00:00",
  "model_id": "MOD-04",
  "model_name": "ElasticNet (Selected Primary)",
  "model_class": "Regularized Supervised Benchmark",
  "basin_id": "Hp-I",
  "basin_name": "Palmer Land West",
  "forecast_year": 2025,
  "predicted_mass_balance_gt_yr": -4.78,
  "predicted_volume_change_km3_yr": -5.21,
  "density_conversion_used": "Delta V = Delta M / 0.917 Gt/km3 (Solid ice density: 917 kg/m3)",
  "uncertainty_std_gt_yr": 11.35,
  "uncertainty_std_km3_yr": 12.38,
  "prediction_type": "live_inference",
  "scientific_disclosure": "Historical basin-level annual prediction regularized on 1979-2024 observations. This is NOT a validated 2100 climate projection and must not be used for multi-decadal sea-level forecasting."
}
```

---

### 2.5 Catalog & Feature Metadata

#### `GET /api/datasets`
Returns the complete dataset inventory matching `stage6_dataset_inventory.csv` (14 inventory items including BedMachine V4.1, RACMO2.3p2 SMB, Stage 5.1 transient physical modeling runs, and IMBIE-3 baselines).

#### `GET /api/features`
Returns the frozen 14-feature dictionary (`stage6_feature_dictionary.csv`) complete with mathematical symbols, physical units, operational lags, imputation strategies, and ElasticNet sparsity weights.

---

### 2.6 Future Projections (Stage 7.1 / 7.2 Multi-Model Emulator)

Pillar 2 provides multi-decadal future projections from 2015 to 2100 across 3 drainage basins (`Hp-I`, `I-Ipp`, `Ipp-J`) and aggregate `Domain_A` (Region 3).
The projection engine is a **Quantile Gradient Boosting (QGB)** ensemble trained on 63,920 harmonized basin-year records from the Seroussi et al. (2020) ISMIP6 archive and evaluated via Leave-One-Model-Family-Out (LOMFO) cross-validation across 10 independent ice sheet model families.

> **Target Variable Disclosure:**
> Projections model **Volume Above Flotation change ($\Delta\text{VAF}$, $\text{km}^3$)** and derived **Sea-Level Equivalent ($\text{SLE}$, $\text{mm}$)**.
> They do **NOT** represent total grounded solid-ice volume ($V_g$).
> Conversion Formula:
> $$\text{SLE} = -\frac{\Delta\text{VAF} \times 0.917\text{ Gt/km}^3}{361.8\text{ Gt/mm}}$$

#### `GET /api/projections/scenarios`
Enumerates supported climate scenarios and their provenance categories.
- Native ISMIP6 scenarios (`RCP8.5`, `RCP2.6`) carry `scenario_watermark: "NATIVE_ISMIP6"`.
- Synthesized intermediate scenario (`SSP2-4.5`) carries `scenario_watermark: "SCALED_EMULATOR_SYNTHESIS"` and pattern scaling coefficient $\alpha = 0.35$.

**Response Example (`200 OK`):**
```json
[
  {
    "id": "RCP8.5",
    "name": "RCP 8.5 (High Emissions)",
    "scenario_type": "NATIVE_ISMIP6",
    "scenario_watermark": "NATIVE_ISMIP6",
    "tier": "Tier-1",
    "scaling_coefficient_alpha": null,
    "description": "High radiative forcing pathway reaching +8.5 W/m² by 2100. Primary ISMIP6 multi-model experiment.",
    "provenance_note": "Directly simulated across 16 ice-sheet model configurations..."
  },
  {
    "id": "SSP2-4.5",
    "name": "SSP2-4.5 (Scaled Synthesis)",
    "scenario_type": "SCALED_EMULATOR_SYNTHESIS",
    "scenario_watermark": "SCALED_EMULATOR_SYNTHESIS",
    "tier": "Derived",
    "scaling_coefficient_alpha": 0.35,
    "description": "Intermediate stabilization pathway synthesized via cumulative radiative forcing pattern scaling (alpha=0.35). Not native to ISMIP6.",
    "provenance_note": "Synthesized via cumulative radiative pattern scaling..."
  }
]
```

#### `GET /api/projections/models`
Returns comprehensive metadata on the Quantile Gradient Boosting future projection emulator, candidate model comparisons, and 10-fold LOMFO validation evidence.

**Response Fields:**
- `model_id`: `"STAGE7_1_QGB_ENSEMBLE"`
- `quantiles_evaluated`: `[0.10, 0.16, 0.50, 0.84, 0.90]`
- `overall_metrics`: `oof_r2` (0.4843), `oof_rmse_km3` (567.18), `oof_mae_km3` (256.85), `empirical_coverage_pct` (62.6% vs 68.0% nominal)
- `candidate_comparisons`: Evaluation metrics for QGB vs Random Forest vs Ridge vs Zero Persistence.
- `lomfo_folds`: Detailed fold-by-fold results across all 10 withheld model families.
- `scientific_notices`: Formal disclaimers and validation caveats.

#### `GET /api/projections/availability`
Returns available years (2015–2100, 86 annual steps), spatial units (`Hp-I`, `I-Ipp`, `Ipp-J`, `Domain_A`), scenarios, and manifest record counts (1,032 records).

#### `GET /api/projections/trajectory`
Retrieves precomputed annual multi-quantile trajectory for a specified scenario and spatial unit.

**Query Parameters:**
- `scenario` (required): `"RCP8.5"`, `"RCP2.6"`, or `"SSP2-4.5"`
- `spatial_unit` (optional, default `"Domain_A"`): `"Hp-I"`, `"I-Ipp"`, `"Ipp-J"`, or `"Domain_A"`
- `basin_id` (optional): Alias for `spatial_unit`
- `start_year` (optional, default 2015): Range 2015–2100
- `end_year` (optional, default 2100): Range 2015–2100

**Response Example (`200 OK`):**
```json
{
  "scenario": "RCP8.5",
  "scenario_type": "NATIVE_ISMIP6",
  "scenario_watermark": "NATIVE_ISMIP6",
  "spatial_unit": "I-Ipp",
  "spatial_unit_name": "Graham Land West (Sector 17)",
  "start_year": 2015,
  "end_year": 2100,
  "point_count": 86,
  "target_variable": "Delta_VAF_Climate_km3",
  "target_disclaimer": "These projections represent changes in Volume Above Flotation (ΔVAF) and derived Sea-Level Equivalent (SLE). They do not represent total grounded solid-ice volume.",
  "sle_formula": "SLE (mm) = - (Delta_VAF (km³) * 0.917) / 361.8",
  "summary_2050": {
    "year": 2050,
    "delta_vaf_median_km3": -55.82,
    "delta_vaf_16th_km3": -186.24,
    "delta_vaf_84th_km3": 43.25,
    "sle_median_mm": 0.141,
    "sle_16th_mm": -0.110,
    "sle_84th_mm": 0.472,
    "scenario_watermark": "NATIVE_ISMIP6",
    "validation_status": "CONDITIONAL_PASS"
  },
  "summary_2100": {
    "year": 2100,
    "delta_vaf_median_km3": -240.02,
    "delta_vaf_16th_km3": -846.82,
    "delta_vaf_84th_km3": 82.57,
    "sle_median_mm": 0.608,
    "sle_16th_mm": -0.209,
    "sle_84th_mm": 2.146,
    "scenario_watermark": "NATIVE_ISMIP6",
    "validation_status": "CONDITIONAL_PASS"
  },
  "trajectory": [
    {
      "year": 2015,
      "delta_vaf_median_km3": 0.0,
      "delta_vaf_16th_km3": 0.0,
      "delta_vaf_84th_km3": 0.0,
      "delta_vaf_10th_km3": 0.0,
      "delta_vaf_90th_km3": 0.0,
      "delta_sle_median_mm": 0.0,
      "delta_sle_16th_mm": 0.0,
      "delta_sle_84th_mm": 0.0,
      "delta_sle_10th_mm": 0.0,
      "delta_sle_90th_mm": 0.0
    }
  ]
}
```

---

## 3. Error Handling & HTTP Status Codes

The CryoPredict API adheres to standard HTTP status codes:

| Code | Meaning | Circumstance | Response Body |
| :--- | :--- | :--- | :--- |
| **`200 OK`** | Success | Request succeeded | Typed JSON response |
| **`400 Bad Request`** | Client Logic Error | Unsupported model identifier or basin parameter | `{"detail": "..."}` |
| **`404 Not Found`** | Resource Missing | Non-existent model ID or endpoint path | `{"detail": "..."}` |
| **`422 Unprocessable Entity`** | Validation Error | Missing feature, non-finite float (NaN/Inf), or year $\ge 2100$ | `{"detail": [...]}` |
| **`500 Internal Error`** | Server Error | Unhandled runtime exception (stack traces suppressed) | `{"detail": "An internal server error occurred..."}` |
| **`503 Service Unavailable`** | Degraded State | Model artifact file missing on disk | `{"detail": "Model artifact is not loaded."}` |
