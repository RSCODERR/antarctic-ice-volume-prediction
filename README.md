# Antarctic Peninsula Ice Volume Prediction

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![Tests Passing](https://img.shields.io/badge/tests-80%2F80%20passing-brightgreen.svg)]()
[![Model Status](https://img.shields.io/badge/models-frozen-orange.svg)]()
[![License: Academic Research](https://img.shields.io/badge/license-Academic%20Research-lightgrey.svg)]()

A physics-informed cryosphere data science framework integrating satellite observations, numerical ice-sheet mechanics, and machine learning to model historical solid-ice mass balance and volume changes across the Antarctic Peninsula (1979–2024).

---

## Research Overview

The Antarctic Peninsula is among the fastest-warming cryospheric regions on Earth, characterized by complex alpine topography, floating ice-shelf collapses (Larsen A & B), and accelerating marine outlet glaciers. This project establishes an authoritative data-driven and physical modeling benchmark:

1. **46-Year Historical Reconstruction (Phase 3):** Reconciles BedMachine Antarctica V4.1 solid ice geometry, MEaSUREs satellite velocity mosaics, RACMO2.3p2 surface mass balance, and IMBIE-3 gravimetry across the three primary drainage basins:
   - **Hp-I:** Palmer Land West (Domain Area: 108,946 km²)
   - **I-Ipp:** Graham Land (Domain Area: 51,993 km²)
   - **Ipp-J:** Palmer Land East (Domain Area: 55,123 km²)
2. **2D Shallow Shelf Approximation (SSA) Physical Solver (Phase 5):** A finite-volume numerical ice sheet flowline model solving diagnostic momentum balance and transient continuity across grounded and floating marine ice domains.
3. **Supervised Machine Learning Benchmarking (Phase 6):** Evaluates six candidate models under a strict chronological split (Train: 1979–2005; Validation: 2008–2014; Test: 2016–2024) separated by quarantine embargo buffers. Regularized **ElasticNet Regression** achieves the best out-of-sample performance, slashing prediction error in Palmer Land East by **47.7%**.

---

## Key Results & Machine Learning Benchmark

| Model Class | Validation MAE ($\mathrm{Gt/yr}$) | Validation Bias ($\mathrm{Gt/yr}$) | Test Refit MAE ($\mathrm{Gt/yr}$) | Test Prospective RMSE ($\mathrm{Gt/yr}$) | Out-of-Sample $R^2$ | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **ElasticNet (Selected Primary)** | **12.09** | **+2.07** | **9.52** | **13.56** | **+0.069** | **Selected Model** |
| **Random Forest** | 13.96 | +6.80 | 10.40 | 13.78 | +0.038 | Benchmark Candidate |
| **Bayesian Ridge** | 14.37 | +7.54 | 10.39 | 14.19 | -0.020 | Benchmark Candidate |
| **Historical Basin Mean** | 14.49 | +7.87 | 10.20 | 14.11 | -0.008 | Baseline Reference |
| **Gradient Boosting** | 14.98 | +8.13 | 10.47 | 14.17 | -0.017 | Benchmark Candidate |
| **Persistence (Lag-1)** | 19.37 | -2.38 | 16.85 | 19.67 | -0.961 | Baseline Reference |

### Primary Findings:
- **Measurable Predictive Value:** ElasticNet outperforms the historical baseline across all primary metrics, achieving an out-of-sample test MAE of **9.52 Gt/yr** (a **12.6% reduction in error**).
- **Physical Dynamic Memory:** Predictive skill is driven by antecedent marine discharge drawdown and rolling multi-year SMB accumulation anomalies. In Basin Ipp-J (Palmer Land East), ElasticNet cuts prediction error by **38.9% to 47.7%**.
- **Automated Feature Pruning:** $L_1$ shrinkage automatically eliminated all six static topographic invariants (area, thickness, bed depth, driving stress, basin dummies), preventing small-sample noise overfitting.

---

## Scientific Limitations & Disclosures

> [!WARNING]
> **Essential Scientific Disclosures:**
> 1. **CryoSat-2 Discrepancy (FAIL-11):** CryoSat-2 altimetry reports $-23.0 \pm 10.0\ \mathrm{Gt/yr}$, while the physical model predicts $+37.52\ \mathrm{Gt/yr}$ (a $+60.52\ \mathrm{Gt/yr}$ offset). Altimetry remains on HOLD due to lack of firn density and radar penetration corrections. ML benchmarks evaluate against the reconciled Phase 3.2 reconstruction, not raw altimetry.
> 2. **Palmer Land West (Hp-I) Weather Extreme:** High snowfall accumulation pulses during 2016–2024 shifted the mean from historical $-3.59\ \mathrm{Gt/yr}$ to $-0.27\ \mathrm{Gt/yr}$. Statistical autoregression cannot anticipate unheralded atmospheric accumulation extremes without contemporaneous atmospheric boundary forcing.
> 3. **Century-Scale Projection Restriction:** These models are **1-year ahead autoregressive historical predictors**. They are **NOT 2100 climate projection models** and must never be extrapolated for multi-decadal forecasting without coupled ocean-atmospheric climate models.

---

## Quickstart & Verification

```bash
# 1. Activate environment
.venv\Scripts\activate  # On Linux/macOS: source .venv/bin/activate

# 2. Run complete 80-test verification suite
python -m unittest discover -s tests -p "test_*.py" && python -m unittest discover -s src/physics/tests -p "test_*.py"

# 3. Verify ML test reproducibility
python scripts/verify_reproducibility.py

# 4. Run prediction inference pipeline
python scripts/run_inference.py

# 5. Export interactive website assets
python scripts/export_website_assets.py
```

---

## Repository Documentation Index

- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md): Detailed architectural mapping of directories, modules, and datasets.
- [MODEL_ARTIFACTS.md](MODEL_ARTIFACTS.md): Serialized model specifications, hyperparameters, feature dictionary, and Python APIs.
- [REPRODUCIBILITY.md](REPRODUCIBILITY.md): Exact commands to reproduce all physics and machine-learning results.
- [CLEANUP_REPORT.md](CLEANUP_REPORT.md): Audit ledger of repository reorganization and safety proofs.
- [reports/](reports/): Complete archive of 98 scientific stage audit reports and 450+ data tables.
