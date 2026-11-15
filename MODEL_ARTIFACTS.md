# Antarctic Peninsula Ice Volume Prediction: Model Artifacts Specification

**Audited Stage:** Stage 6.1 Benchmarking & Stage 6.2 Forensic Verification  
**Specification Date:** November 15, 2026  
**Artifact Directory:** `models/` (Mirrored in `reports/stage6_1_model_artifacts/`)  
**Deployment State:** Frozen  

---

## 1. Inventory of Serialized Model Artifacts

| Artifact Filename | Class / Type | Training Set Scope | Size (Bytes) | Input Dimensions | Target Metric |
| :--- | :--- | :--- | :---: | :---: | :--- |
| **`elastic_net_train.joblib`** | `sklearn.linear_model.ElasticNet` | Training Fold (1979–2005, N=81) | 744 | 14 features | Annual Mass Balance ($\mathrm{Gt/yr}$) |
| **`elastic_net_train_val.joblib`** | `sklearn.linear_model.ElasticNet` | Permitted Train+Val (1979–2014, N=102) | 744 | 14 features | Annual Mass Balance ($\mathrm{Gt/yr}$) |
| **`scaler_train.joblib`** | `sklearn.preprocessing.StandardScaler` | Training Fold (1979–2005, N=81) | 1,479 | 14 features | Standardized Features ($\mu=0, \sigma=1$) |
| **`scaler_train_val.joblib`** | `sklearn.preprocessing.StandardScaler` | Permitted Train+Val (1979–2014, N=102) | 1,479 | 14 features | Standardized Features ($\mu=0, \sigma=1$) |
| **`bayesian_ridge_train.joblib`** | `sklearn.linear_model.BayesianRidge` | Training Fold (1979–2005, N=81) | 2,791 | 14 features | Annual Mass Balance ($\mathrm{Gt/yr}$) |
| **`bayesian_ridge_train_val.joblib`** | `sklearn.linear_model.BayesianRidge` | Permitted Train+Val (1979–2014, N=102) | 2,791 | 14 features | Annual Mass Balance ($\mathrm{Gt/yr}$) |
| **`random_forest_train.joblib`** | `sklearn.ensemble.RandomForestRegressor` | Training Fold (1979–2005, N=81) | 36,769 | 14 features | Annual Mass Balance ($\mathrm{Gt/yr}$) |
| **`random_forest_train_val.joblib`** | `sklearn.ensemble.RandomForestRegressor` | Permitted Train+Val (1979–2014, N=102) | 39,505 | 14 features | Annual Mass Balance ($\mathrm{Gt/yr}$) |
| **`gradient_boosting_train.joblib`** | `sklearn.ensemble.GradientBoostingRegressor` | Training Fold (1979–2005, N=81) | 25,129 | 14 features | Annual Mass Balance ($\mathrm{Gt/yr}$) |
| **`gradient_boosting_train_val.joblib`**| `sklearn.ensemble.GradientBoostingRegressor` | Permitted Train+Val (1979–2014, N=102) | 25,128 | 14 features | Annual Mass Balance ($\mathrm{Gt/yr}$) |
| **`historical_basin_means_train.joblib`** | `dict` (Empirical basin averages) | Training Fold (1979–2005, N=81) | 66 | 3 basin keys | Annual Mass Balance Baseline |
| **`historical_basin_means_train_val.joblib`**| `dict` (Empirical basin averages) | Permitted Train+Val (1979–2014, N=102) | 66 | 3 basin keys | Annual Mass Balance Baseline |
| **`model_metadata.json`** | JSON Metadata Specification | Global | 1,075 | N/A | Feature schema, splits, seeds |

---

## 2. Feature Schema & Ordering Specification

Models strictly require the following 14 features in exact sequence:

```python
FEATURE_SCHEMA = [
    "Target_Volume_Change_Lag1_km3_yr",  # FEAT-01: Antecedent volume rate (y_{t-1})
    "Target_Volume_Change_Lag2_km3_yr",  # FEAT-02: 2-year antecedent volume rate (y_{t-2})
    "Net_MB_Lag1_Gt_yr",                 # FEAT-03: Preceding year mass balance state
    "SMB_Lag1_Gt_yr",                    # FEAT-04: Antecedent RACMO SMB climate forcing
    "Discharge_Lag1_Gt_yr",              # FEAT-05: Preceding satellite flux gate discharge
    "SMB_Rolling3yr_Gt_yr",              # FEAT-06: 3-year rolling antecedent SMB accumulation
    "SMB_Anomaly_Lag1_Gt_yr",            # FEAT-07: Antecedent SMB anomaly relative to baseline
    "Grounded_Area_km2",                 # FEAT-08: Time-invariant grounded domain mask area
    "Mean_Baseline_Ice_Thickness_m",     # FEAT-09: Time-invariant BedMachine V4.1 ice thickness
    "Bed_Elevation_at_Gates_m",          # FEAT-10: Bedrock elevation at marine grounding line
    "Driving_Stress_Index_kPa",          # FEAT-11: Gravitational driving shear stress proxy
    "is_Hp_I",                           # FEAT-12: Binary indicator for Palmer Land West
    "is_I_Ipp",                          # FEAT-13: Binary indicator for Graham Land
    "is_Ipp_J"                           # FEAT-14: Binary indicator for Palmer Land East
]
```

---

## 3. Selected Primary Model Hyperparameters & Sparsity

**Model:** `ElasticNet(alpha=0.1, l1_ratio=0.9, random_state=42, max_iter=2000)`

### Standardized Model Coefficients (Fitted on Training Fold):
- **Intercept:** $-3.861823\ \mathrm{Gt/yr}$
- `SMB_Anomaly_Lag1_Gt_yr`: **-7.083343** (Strongest climate sensitivity)
- `Target_Volume_Change_Lag1_km3_yr`: **+3.999004** (Autoregressive persistence)
- `Net_MB_Lag1_Gt_yr`: **+3.948183** (Mass balance persistence)
- `Target_Volume_Change_Lag2_km3_yr`: **-0.882251** (2-year mean-reversion)
- `SMB_Rolling3yr_Gt_yr`: **+0.700066** (3-year snowpack buffer memory)
- `Discharge_Lag1_Gt_yr`: **-0.262325** (Marine dynamic drawdown)
- `is_I_Ipp`: **+0.174633** (Graham Land regional intercept offset)
- `SMB_Lag1_Gt_yr`: **0.000000** (Pruned by L1 penalty)
- `Grounded_Area_km2`: **0.000000** (Pruned by L1 penalty)
- `Mean_Baseline_Ice_Thickness_m`: **0.000000** (Pruned by L1 penalty)
- `Bed_Elevation_at_Gates_m`: **0.000000** (Pruned by L1 penalty)
- `Driving_Stress_Index_kPa`: **0.000000** (Pruned by L1 penalty)
- `is_Hp_I`: **0.000000** (Pruned by L1 penalty)
- `is_Ipp_J`: **0.000000** (Pruned by L1 penalty)

---

## 4. Model Loading and Inference Code Contract

```python
import os
import joblib
import pandas as pd

# 1. Define paths
MODELS_DIR = "models"
scaler = joblib.load(os.path.join(MODELS_DIR, "scaler_train.joblib"))
model = joblib.load(os.path.join(MODELS_DIR, "elastic_net_train.joblib"))

# 2. Input features (must conform to 14-feature schema)
# features_df: pd.DataFrame containing the 14 columns
X_scaled = scaler.transform(features_df[FEATURE_SCHEMA])

# 3. Predict Annual Mass Balance (Gt/yr)
pred_mb = model.predict(X_scaled)

# 4. Derive Solid-Ice Equivalent Volume Change (km3/yr)
ICE_DENSITY = 0.917  # Gt / km3
pred_vol = pred_mb / ICE_DENSITY
```
