# Antarctic Peninsula Ice Volume Prediction: Project Structure

**Governing Specification:** Stage 6.2 Pre-Deployment Repository Organization  
**Audited Date:** November 15, 2026  
**Repository State:** Frozen & Ready for Interactive Research Website Integration  

---

## 1. Directory Tree Architecture

```
antarctic-ice-volume-prediction/
├── .env                                  # Environment credentials (e.g. Earthdata token)
├── .gitignore                            # Git exclusion rules for large datasets, caches
├── README.md                             # High-level project research overview and quickstart
├── PROJECT_STRUCTURE.md                  # Comprehensive structural mapping (this document)
├── MODEL_ARTIFACTS.md                    # Serialized model specifications, schemas & loading APIs
├── REPRODUCIBILITY.md                    # Verification instructions, test commands & scripts
├── CLEANUP_REPORT.md                     # Forensic cleanup audit, safety proofs & freeze status
├── dataset_sources.md                    # Provenance and source URLs for cryosphere datasets
├── requirements.txt                      # Frozen Python dependencies
│
├── data/                                 # Cryosphere observations and spatial grids
│   ├── raw/                              # Original immutable datasets
│   │   ├── bedmachine/                   # BedMachine Antarctica V4.1 NetCDF grids
│   │   ├── bedmap3/                      # Bedmap3 ice thickness point measurements
│   │   ├── imbie/                        # IMBIE-3 peninsula mass balance reconciliation
│   │   ├── imbie_basins/                 # MEaSUREs & IMBIE drainage basin shapefiles
│   │   ├── ismip6/                       # ISMIP6 ocean and atmospheric forcing
│   │   ├── measures/                     # MEaSUREs ice velocity mosaics
│   │   ├── measures_gl/                  # MEaSUREs grounding line vectors
│   │   └── racmo/                        # RACMO2.3p2 surface mass balance (SMB)
│   ├── processed/                        # Quality-masked, solver-ready NetCDF & CSV files
│   │   ├── stage4_5_2/                   # Calibrated basal friction parameter rasters
│   │   ├── stage4_5_3/                   # Unified physical fields & observation quality masks
│   │   ├── stage4_7/                     # Regional basal friction inversion grids
│   │   ├── stage5_1/                     # Stage 5.1 historical transient simulation grids
│   │   └── ismip6/                       # Regridded climate anomaly forcing
│   └── features/                         # Feature matrices and glaciological indices
│
├── models/                               # Serialized ML model artifacts & preprocessing pipelines
│   ├── elastic_net_train.joblib          # Selected primary ElasticNet model (Train fit, N=81)
│   ├── elastic_net_train_val.joblib      # Primary ElasticNet model (Train+Val refit, N=102)
│   ├── scaler_train.joblib               # StandardScaler fitted on Training fold (1979-2005)
│   ├── scaler_train_val.joblib           # StandardScaler fitted on Train+Val fold (1979-2014)
│   ├── bayesian_ridge_train.joblib       # Bayesian Ridge model (Train fit)
│   ├── bayesian_ridge_train_val.joblib   # Bayesian Ridge model (Train+Val refit)
│   ├── random_forest_train.joblib        # Random Forest Regressor (Train fit)
│   ├── random_forest_train_val.joblib    # Random Forest Regressor (Train+Val refit)
│   ├── gradient_boosting_train.joblib    # Gradient Boosting Regressor (Train fit)
│   ├── gradient_boosting_train_val.joblib# Gradient Boosting Regressor (Train+Val refit)
│   ├── historical_basin_means_train.joblib     # Empirical training-fold basin baseline means
│   ├── historical_basin_means_train_val.joblib # Empirical train+val basin baseline means
│   └── model_metadata.json               # Model hyperparameters, feature list & split boundaries
│
├── figures/                              # High-resolution publication & website figures
│   ├── stage6_1_evaluation_plots.png     # 6-panel ML validation, test & feature diagnostics
│   ├── stage5_1_transient_diagnostics.png# 19-year physical transient simulation diagnostics
│   ├── stage4_8_mass_balance_diagnostics.png # Grounded/floating mass ledger diagnostics
│   └── ...                               # Complete catalog of 63 spatial and diagnostic plots
│
├── reports/                              # Formal stage audit reports, metrics & data tables
│   ├── stage6_2_final_verification.md    # Stage 6.2 independent forensic reproducibility report
│   ├── stage6_1_training_report.md       # Stage 6.1 machine learning benchmarking report
│   ├── stage6_0_ml_readiness_report.md   # Stage 6.0 ML dataset feasibility audit
│   ├── stage5_1_closure_report.md        # Stage 5.1 physical historical transient closure
│   ├── tables/                           # 450+ authoritative scientific CSV tables
│   │   ├── stage6_ml_dataset.csv         # Master ML dataset (138 rows, 46 years, 3 basins)
│   │   ├── stage6_temporal_split_manifest.csv # Deterministic chronological split mapping
│   │   ├── stage6_feature_dictionary.csv # 15 documented static and dynamic predictors
│   │   ├── stage6_1_model_comparison.csv # Comprehensive comparison across 6 models
│   │   ├── stage6_1_basin_performance.csv# Per-basin validation and test metrics
│   │   ├── stage6_1_predictions.csv      # Complete 138-row predictions & volume equivalents
│   │   ├── stage6_1_feature_importance.csv# Standardized coefficients and importance rankings
│   │   ├── stage6_2_reproducibility_check.csv # Clean-slate 27-check audit verification ledger
│   │   └── ...                           # Historical phase audits (Phase 1 through Stage 5.1)
│   └── website_assets/                   # Clean JSON exports for interactive website frontend
│       ├── model_comparison.json         # High-level model comparison matrix
│       ├── basin_performance.json        # Basin-specific validation and test metrics
│       ├── predictions_timeseries.json   # 46-year time series predictions & residuals
│       └── feature_importance.json       # Feature rankings and L1 sparsity weights
│
├── scripts/                              # Standalone CLI tools & deployment utilities
│   ├── verify_reproducibility.py         # Automated test-fold reproducibility checker
│   ├── run_inference.py                  # Standalone prediction pipeline CLI
│   └── export_website_assets.py          # Script to export website JSON payloads
│
├── src/                                  # Modular scientific Python library
│   ├── api/                              # Lightweight inference service for website frontend
│   │   ├── __init__.py                   # Exposes AntarcticPredictionService
│   │   └── inference_service.py          # Service wrapper for mass balance & volume forecasting
│   ├── ml/                               # ML module facade
│   │   └── __init__.py                   # Re-exports baseline, linear, and tree model classes
│   ├── data/                             # Data loading facade
│   │   └── __init__.py                   # Dataset loaders for ML and split manifests
│   ├── physics/                          # 2D SSA physical ice sheet numerical solver
│   │   ├── ssa_2d/                       # 2D Shallow Shelf Approximation finite volume solver
│   │   │   ├── assembly.py               # Sparse momentum matrix assembly
│   │   │   ├── solver.py                 # Picard & Newton-Raphson non-linear solvers
│   │   │   ├── continuity.py             # Conservative 2D finite-volume thickness updater
│   │   │   ├── rheology.py               # Glen flow law effective viscosity tensor
│   │   │   ├── friction.py               # Weertman basal friction & flotation fraction
│   │   │   ├── grid.py                   # 2D curvilinear/Cartesian spatial grid geometry
│   │   │   └── boundary.py               # Calving front water pressure & lateral drag
│   │   ├── basal_drag.py                 # Regional basal friction formulations
│   │   ├── grounding_line.py             # Schoof (2007) marine ice sheet boundary condition
│   │   ├── lateral_drag.py               # MacAyeal & Thomas (1986) embayment shear stress
│   │   ├── smb.py                        # RACMO surface mass balance accumulation converter
│   │   ├── constants.py                  # Physical constants (rho_i, rho_w, Glen n=3, A)
│   │   └── tests/                        # Physics unit tests (52 tests, 100% pass)
│   ├── models/                           # Core model definitions (baselines, GP, Ridge, Trees)
│   ├── geospatial/                       # Polar stereographic (EPSG:3031) projection & regridding
│   ├── evaluation/                       # Statistical metrics, CRPS, bias & calibration checks
│   ├── feature_engineering/              # Lag generation, climate anomalies & rolling windows
│   └── data_acquisition/                 # Earthdata downloaders, IMBIE scrapers & format parsers
│
└── tests/                                # Repository test suite
    ├── test_ml_artifacts.py              # ML model loading, schema & reproducibility (6 tests)
    ├── test_ssa_2d_mismip.py             # MISMIP+ benchmark verification
    ├── test_ssa_2d_synthetic.py          # Synthetic slab mass conservation tests
    ├── test_ssa_2d_unit.py               # SSA momentum balance operator unit tests
    └── test_stage4_4_2_synthetic_conservation.py # Finite volume state transition conservation
```

---

## 2. Component Roles & Separation of Concerns

1. **`models/` vs `reports/stage6_1_model_artifacts/`:**
   - Both directories contain identical, bit-for-bit serialized `.joblib` files and `model_metadata.json`.
   - `models/` is the canonical deployment directory for downstream application serving (e.g. `src/api`).
   - `reports/stage6_1_model_artifacts/` is preserved to guarantee zero broken links in historical audit reports.

2. **`src/ml/`, `src/data/`, `src/api/` Facades:**
   - Designed to provide a clean, modern interface for the interactive research website without altering legacy module paths.
   - Legacy imports (`from src.models import ...`, `from src.physics import ...`) remain 100% backward-compatible.

3. **`reports/website_assets/`:**
   - Houses lightweight, web-optimized JSON payloads for client-side rendering (Chart.js / Plotly / D3) of the model comparison matrix, 46-year time series, basin breakdowns, and feature importances.
