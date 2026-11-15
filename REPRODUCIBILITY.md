# Antarctic Peninsula Ice Volume Prediction: Reproducibility Guide

**Audited Milestone:** Stage 6.2 Final Results Verification  
**Date:** November 15, 2026  
**Governing Standard:** 100% Deterministic Reproducibility Across Physics and ML Pipelines  

---

## 1. Quickstart Environment Setup

### Prerequisites
- OS: Windows 10/11, macOS, or Linux
- Python: Version 3.12.x (Tested on Python 3.12.5)

### Setup Commands
```bash
# Clone repository
git clone <repo-url>
cd antarctic-ice-volume-prediction

# Initialize virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install frozen dependencies
pip install -r requirements.txt
```

---

## 2. Test Suite Execution (80 / 80 Tests Passing)

The project includes an end-to-end 80-test verification suite covering momentum balance, non-linear ice rheology, finite-volume conservation, MISMIP+ benchmarking, ML artifact loading, and prediction reproducibility:

```bash
# 1. Run full unit test suite (28 base & ML tests)
python -m unittest discover -s tests -p "test_*.py"

# 2. Run physics unit tests (52 physics tests)
python -m unittest discover -s src/physics/tests -p "test_*.py"

# Combined command
python -m unittest discover -s tests -p "test_*.py" && python -m unittest discover -s src/physics/tests -p "test_*.py"
```

Expected Output:
```
Ran 28 tests in 12.16s ... OK
Ran 52 tests in 0.13s  ... OK
Total: 80 / 80 tests passing (100% pass rate)
```

---

## 3. Standalone ML Reproducibility Verification

To independently verify that the serialized ElasticNet model reproduces the reported held-out test metrics without rerunning training:

```bash
python scripts/verify_reproducibility.py
```

Expected Output:
```
=== Running Standalone Reproducibility Verification ===
Test RMSE : 13.5582 Gt/yr (Target: 13.56)
Test MAE  : 9.6095 Gt/yr (Target: 9.61)
Test R2   : 0.0686 (Target: +0.069)
>>> All test reproducibility checks PASSED! <<<
```

---

## 4. Standalone Prediction Pipeline Execution

To generate predictions across the full 46-year record (1979–2024) across all three drainage basins:

```bash
python scripts/run_inference.py
```
Output:
- Saves predictions to `reports/tables/interactive_inference_sample.csv`.
- Confirms $\Delta V = \Delta M / 0.917\ \mathrm{km^3/yr}$ exact density conversion.

---

## 5. Exporting Interactive Website Assets

To compile the latest lightweight JSON datasets for the web frontend:

```bash
python scripts/export_website_assets.py
```
Generated Payloads:
- `reports/website_assets/model_comparison.json`
- `reports/website_assets/basin_performance.json`
- `reports/website_assets/predictions_timeseries.json`
- `reports/website_assets/feature_importance.json`

---

## 6. Scientific Limitations & Disclosure Notice

1. **CryoSat-2 Observation Discrepancy (FAIL-11):**
   - CryoSat-2 altimetry reports $-23.0 \pm 10.0\ \mathrm{Gt/yr}$, while the physical model predicts $+37.52\ \mathrm{Gt/yr}$ (an offset of $+60.52\ \mathrm{Gt/yr}$).
   - CryoSat-2 altimetry remains on formal **HOLD** due to lack of firn compaction and radar penetration depth corrections. The ML test evaluations reflect the Phase 3.2 master reconciliation benchmark, NOT raw altimetry truth.

2. **Centennial Forecasting Non-Capability:**
   - The trained machine learning models are **1-year ahead autoregressive basin-level predictors**, regularized on historical observations (1979–2024).
   - They are **NOT validated 2100 climate projection models** and must never be extrapolated for century-scale forecasting under IPCC SSP scenarios without coupled ocean-atmospheric boundary forcing.
