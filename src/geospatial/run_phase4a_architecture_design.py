"""
Phase 4A: Machine Learning Architecture and Experimental Design
================================================================
Implements Phase 4A accounting and experimental design deliverables:
1. Row-level split manifest for all 184 rows (138 basin-years + 46 Domain A diagnostic rows).
   - Explicitly accounts for the 9 embargo records:
     * 2006 (Hp-I, I-Ipp, Ipp-J): Embargo Buffer 1 (3 records)
     * 2007 (Hp-I, I-Ipp, Ipp-J): Embargo Buffer 1 (3 records)
     * 2015 (Hp-I, I-Ipp, Ipp-J): Embargo Buffer 2 (3 records)
     * Total embargo: 9 records.
     * Evaluated: 81 (Train) + 21 (Validation) + 27 (Test) = 129 records.
     * Basin-year total: 129 + 9 = 138 records.
     * Domain A total: 46 derived diagnostic records.
     * Total rows: 138 + 46 = 184 rows.
2. Task A (Historical Emulation) vs Task B (Future Scenario Prediction) feature matrices.
3. Candidate model architecture comparison (7 models).
4. Basin modeling strategy comparison (Separate vs Pooled vs Multi-Output).

Generates:
- reports/tables/split_manifest_row_level.csv
- reports/tables/task_feature_matrix_design.csv
- reports/tables/model_architecture_comparison.csv
- reports/tables/basin_modeling_strategy_comparison.csv
"""

import os
import sys
import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
TABLES_DIR = os.path.join(REPORTS_DIR, "tables")
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")

TARGET_CSV = os.path.join(TABLES_DIR, "ml_target_dataset.csv")

# =========================================================================
# 1. Row-Level Split Manifest (184 Rows)
# =========================================================================
def generate_row_level_split_manifest():
    print("\n--- [1] Generating Row-Level Split Manifest ---")
    df_target = pd.read_csv(TARGET_CSV)
    N_total = len(df_target)
    print(f"Loaded target dataset with {N_total} rows.")

    manifest_records = []
    
    # Counter trackers
    counts = {
        "TRAINING": 0,
        "EMBARGO_BUFFER_1": 0,
        "VALIDATION": 0,
        "EMBARGO_BUFFER_2": 0,
        "TEST": 0,
        "DERIVED_REGIONAL_DIAGNOSTIC": 0
    }

    for idx, row in df_target.iterrows():
        y = int(row['Year'])
        b_id = str(row['Basin_ID'])
        b_name = str(row['Basin_Name'])
        epoch = str(row['Epoch'])
        ann_vol = float(row['Target_Annual_Volume_Change_Central_km3_yr'])
        cum_vol = float(row['Target_Cum_Volume_Anomaly_Central_km3'])

        if b_id == "Domain_A":
            status = "DERIVED_REGIONAL_DIAGNOSTIC"
            is_sample = False
            reason = "Regional aggregate Domain A (Hp-I + I-Ipp + Ipp-J). NOT an independent training sample; preserved strictly as a derived regional diagnostic to verify spatial mass conservation."
            allowed_ops = "Diagnostic evaluation & mass conservation checking. NEVER included in model fitting loss functions."
            leakage_risk = "High if included in training (would duplicate basin mass signals and violate independent observation assumptions)."
        else:
            if 1979 <= y <= 2005:
                status = "TRAINING"
                is_sample = True
                reason = "Epoch 1 & Early Epoch 2 (1979–2005). Historical baseline, Wordie collapse (1989), Larsen A (1995), and Larsen B (2002) initial dynamic adjustments. Chronologically strictly precedes validation and test sets."
                allowed_ops = "Feature training, loss minimization, internal walk-forward time-series CV, coefficient fitting."
                leakage_risk = "None. Chronologically isolated from future validation/test regimes."
            elif 2006 <= y <= 2007:
                status = "EMBARGO_BUFFER_1"
                is_sample = False
                reason = "Post-Larsen B surge relaxation transition (2006–2007). 2-year temporal quarantine buffer deliberately isolating Training (<=2005) from Validation (>=2008) to prevent autoregressive feature lags (AR(1), AR(2), 2-year rolling climate averages) in the validation set from peering into training target labels."
                allowed_ops = "STRICTLY EXCLUDED from training loss and validation scoring. Used only to initialize autoregressive lag buffers for the start of the validation window."
                leakage_risk = "Quarantined buffer preventing backward-looking lag leakage."
            elif 2008 <= y <= 2014:
                status = "VALIDATION"
                is_sample = True
                reason = "Mid-to-Late Epoch 2 (2008–2014). Multi-sensor satellite constraint era (GRACE RL06 mascons, ICESat-1, Envisat, early CryoSat-2). Chronologically isolated from training by Embargo 1."
                allowed_ops = "Hyperparameter tuning, regularization penalty selection (alpha, lambda), model selection, early stopping, feature subset ranking."
                leakage_risk = "Protected from training leakage by Embargo Buffer 1 (2006–2007)."
            elif y == 2015:
                status = "EMBARGO_BUFFER_2"
                is_sample = False
                reason = "Transition year (2015) between multi-sensor constrained era and modern Sentinel-1 SAR constellation velocity tracking era. 1-year temporal quarantine buffer isolating Validation (<=2014) from Test (>=2016) to prevent 1-year lag features in test set from referencing validation targets."
                allowed_ops = "STRICTLY EXCLUDED from parameter tuning and final scoring. Used only to populate 1-year lag features for the start of the test window."
                leakage_risk = "Quarantined buffer preventing sensor transition boundary leakage."
            elif 2016 <= y <= 2024:
                status = "TEST"
                is_sample = True
                reason = "Epoch 3 (2016–2024). Modern observation-rich era (Sentinel-1 SAR velocity tracking, CryoSat-2 SARIn, ICESat-2 ATL15 laser altimetry). Highest observational density. Strictly held out."
                allowed_ops = "One-time final benchmark evaluation of finalized candidate models. Primary metrics: RMSE, MAE, R^2, and cumulative mass conservation error."
                leakage_risk = "Protected from validation leakage by Embargo Buffer 2 (2015). Strictly blind during model development."
            else:
                status = "UNKNOWN"
                is_sample = False
                reason = "Out of range."
                allowed_ops = "None"
                leakage_risk = "Unknown"

        counts[status] += 1

        manifest_records.append({
            "Row_ID": idx,
            "Year": y,
            "Basin_ID": b_id,
            "Basin_Name": b_name,
            "Observational_Epoch": epoch,
            "Split_Status": status,
            "Is_Independent_Training_Sample": is_sample,
            "Target_Annual_Volume_Change_km3_yr": ann_vol,
            "Target_Cum_Volume_Anomaly_km3": cum_vol,
            "Documented_Reason": reason,
            "Permitted_ML_Operations": allowed_ops,
            "Leakage_Protection_Mechanism": leakage_risk
        })

    df_manifest = pd.DataFrame(manifest_records)
    out_path = os.path.join(TABLES_DIR, "split_manifest_row_level.csv")
    df_manifest.to_csv(out_path, index=False)
    print(f"Saved: {out_path}")
    print("\n--- Manifest Row Accounting Summary ---")
    for k, v in counts.items():
        print(f"  {k:30s}: {v:3d} rows")
    total_basin_years = counts["TRAINING"] + counts["EMBARGO_BUFFER_1"] + counts["VALIDATION"] + counts["EMBARGO_BUFFER_2"] + counts["TEST"]
    total_evaluated = counts["TRAINING"] + counts["VALIDATION"] + counts["TEST"]
    total_embargo = counts["EMBARGO_BUFFER_1"] + counts["EMBARGO_BUFFER_2"]
    print(f"  {'Total Basin-Years (3 basins x 46 yrs)':30s}: {total_basin_years:3d} rows")
    print(f"  {'Total Evaluated Basin-Years':30s}: {total_evaluated:3d} rows (81 + 21 + 27 = 129)")
    print(f"  {'Total Quarantined Embargo Records':30s}: {total_embargo:3d} rows (6 + 3 = 9)")
    print(f"  {'Derived Domain A Diagnostic Rows':30s}: {counts['DERIVED_REGIONAL_DIAGNOSTIC']:3d} rows")
    print(f"  {'GRAND TOTAL ROWS':30s}: {len(df_manifest):3d} rows (138 + 46 = 184)")

    # Assertions to ensure 100% bookkeeping precision
    assert total_basin_years == 138, "Error: Basin years must equal 138"
    assert counts["DERIVED_REGIONAL_DIAGNOSTIC"] == 46, "Error: Domain A rows must equal 46"
    assert total_evaluated == 129, "Error: Evaluated rows must equal 129"
    assert total_embargo == 9, "Error: Embargo rows must equal 9"
    assert len(df_manifest) == 184, "Error: Grand total rows must equal 184"
    print("ALL ACCOUNTING ASSERTIONS PASSED TO EXACT PRECISION.")
    return df_manifest


# =========================================================================
# 2. Task Feature Matrix Design (Task A vs Task B)
# =========================================================================
def generate_task_feature_matrix_design():
    print("\n--- [2] Generating Task A vs Task B Feature Matrix Design Table ---")
    data = [
        {
            "Feature_Name": "RACMO_Precipitation_Snowfall_mm_yr",
            "Physical_Domain": "Atmospheric Accumulation",
            "Task_A_Availability_Historical": "YES: RACMO2.3p2 / 2.4p1 historical downscaled grids (1979–2024)",
            "Task_B_Availability_Future": "YES: CMIP6 / ISMIP6 regional climate projections (SSP1-2.6, SSP2-4.5, SSP5-8.5 downscaled by RACMO/MAR to 2100)",
            "IMBIE_Provenance_Status": "Independent of IMBIE (direct atmospheric model output)",
            "Feature_Role_Task_A": "Primary climate driver of surface mass accumulation",
            "Feature_Role_Task_B": "Exogenous climate forcing driving future snowfall trends",
            "Extrapolation_Limits_to_2100": "Projected precipitation increases under atmospheric warming (~5–7% per deg C); must be bound by physical thermodynamic limits (Clausius-Clapeyron)."
        },
        {
            "Feature_Name": "RACMO_Surface_Runoff_Melt_mm_yr",
            "Physical_Domain": "Atmospheric Ablation",
            "Task_A_Availability_Historical": "YES: RACMO2.3p2 / 2.4p1 historical melt/runoff grids (1979–2024)",
            "Task_B_Availability_Future": "YES: CMIP6 / ISMIP6 regional climate projections under SSP scenarios to 2100",
            "IMBIE_Provenance_Status": "Independent of IMBIE (direct atmospheric model output)",
            "Feature_Role_Task_A": "Direct surface ablation loss; hydrofracture triggering proxy",
            "Feature_Role_Task_B": "Exponential surface ablation driver and ice shelf melt ponding indicator",
            "Extrapolation_Limits_to_2100": "Non-linear positive feedback: warming shifts hypsometry from accumulation to ablation; runoff expands exponentially above regional freezing thresholds."
        },
        {
            "Feature_Name": "Regional_Surface_Air_Temperature_2m_K",
            "Physical_Domain": "Atmospheric Thermodynamics",
            "Task_A_Availability_Historical": "YES: ERA5 reanalysis downscaled via RACMO (1979–2024)",
            "Task_B_Availability_Future": "YES: CMIP6 ESM ensemble projections (SSP1-2.6, SSP2-4.5, SSP5-8.5)",
            "IMBIE_Provenance_Status": "Independent of IMBIE (reanalysis/ESM forcing)",
            "Feature_Role_Task_A": "Melt degree-day and firn warming proxy",
            "Feature_Role_Task_B": "Primary scenario trajectory discriminator",
            "Extrapolation_Limits_to_2100": "Extreme warming (>+4 deg C under SSP5-8.5) exceeds all historical observational analogues across Graham Land."
        },
        {
            "Feature_Name": "Circumpolar_Deep_Water_CDW_Thermal_Anomaly_C",
            "Physical_Domain": "Ocean Thermal Forcing",
            "Task_A_Availability_Historical": "YES: EN4 / ECCO ocean state reanalysis subsurface temperatures (1979–2024)",
            "Task_B_Availability_Future": "YES: CMIP6 ocean sub-surface potential temperature projections at continental shelf edge",
            "IMBIE_Provenance_Status": "Independent of IMBIE (ocean hydrographic data)",
            "Feature_Role_Task_A": "Basal melt forcing for George VI and Palmer Land tidewater glaciers",
            "Feature_Role_Task_B": "Sub-surface marine heat flux forcing submarine calving and grounding line retreat",
            "Extrapolation_Limits_to_2100": "Intrusion of CDW onto Palmer Land shelf exhibits non-linear threshold dynamics; linear historical regression cannot capture sudden thermocline shoaling."
        },
        {
            "Feature_Name": "Southern_Annular_Mode_SAM_Index",
            "Physical_Domain": "Large-Scale Atmospheric Mode",
            "Task_A_Availability_Historical": "YES: Marshall (2003) station-based observational index (1979–2024)",
            "Task_B_Availability_Future": "YES: Projected SAM index from CMIP6 sea-level pressure fields",
            "IMBIE_Provenance_Status": "Independent of IMBIE (barometric observations)",
            "Feature_Role_Task_A": "Modulates westerly wind strength, foehn warming events, and Larsen shelf melt",
            "Feature_Role_Task_B": "Controls frequency of future foehn-driven collapse episodes",
            "Extrapolation_Limits_to_2100": "Positive SAM trend is heavily ozone recovery- and GHG-dependent; past relationship with foehn storms may saturate if summer sea ice disappears entirely."
        },
        {
            "Feature_Name": "Grounded_Basin_Ice_Thickness_Mean_m",
            "Physical_Domain": "Static Subglacial Topography",
            "Task_A_Availability_Historical": "YES: Bedmap3 (Pritchard 2025) and BedMachine V4.1 (Morlighem 2025)",
            "Task_B_Availability_Future": "YES: Baseline anchor constants, evolving dynamically via mass continuity",
            "IMBIE_Provenance_Status": "Independent of IMBIE (geophysical sounding / mass conservation)",
            "Feature_Role_Task_A": "Static basin geometric scale and driving stress baseline",
            "Feature_Role_Task_B": "Determines ice volume capacity ceiling; mass continuity constraint: H(t) >= 0",
            "Extrapolation_Limits_to_2100": "Ice volume exhaustion: as low-elevation trunks melt completely, thinning rate must decay to zero rather than continuing linearly."
        },
        {
            "Feature_Name": "Grounded_Basin_Area_km2",
            "Physical_Domain": "Static Spatial Geography",
            "Task_A_Availability_Historical": "YES: IMBIE mainland basin polygons (108,946; 49,758; 57,359 km2)",
            "Task_B_Availability_Future": "YES: Static geographical spatial reference; grounding line retreat tracker",
            "IMBIE_Provenance_Status": "Independent of IMBIE mass balance (standard coastline/drainage boundary)",
            "Feature_Role_Task_A": "Area scaling for mass-to-volume integration",
            "Feature_Role_Task_B": "Boundary polygon for spatial integration",
            "Extrapolation_Limits_to_2100": "Grounding line retreat may reduce grounded area over multi-decadal timescales (~1–3% by 2100); models assuming static area slightly overestimate future grounded area."
        },
        {
            "Feature_Name": "ITS_LIVE_Glacier_Flow_Velocity_m_yr",
            "Physical_Domain": "Satellite Kinematics",
            "Task_A_Availability_Historical": "YES: NASA JPL autoRIFT satellite velocity mosaics (1985–2024)",
            "Task_B_Availability_Future": "NO: FUTURE SATELLITE VELOCITY OBSERVATIONS DO NOT EXIST",
            "IMBIE_Provenance_Status": "Independent of IMBIE (raw optical/radar feature tracking)",
            "Feature_Role_Task_A": "Kinematic state feature informing historical gate discharge",
            "Feature_Role_Task_B": "PROHIBITED AS A FUTURE PREDICTOR. Must be replaced by dynamic state-variable evolution or empirical relaxation functions.",
            "Extrapolation_Limits_to_2100": "FATAL LEAKAGE if assumed available post-2024. Future velocity must be an internal state variable or parameterized response, not an input."
        },
        {
            "Feature_Name": "Satellite_Altimetry_Elevation_Rate_dhdt",
            "Physical_Domain": "Satellite Geodesy",
            "Task_A_Availability_Historical": "YES: CryoSat-2 (2010–2024) and ICESat-2 ATL15 (2018–2024)",
            "Task_B_Availability_Future": "NO: FUTURE ALTIMETRY OBSERVATIONS DO NOT EXIST",
            "IMBIE_Provenance_Status": "Independent of IMBIE (raw radar/laser altimetry)",
            "Feature_Role_Task_A": "Independent validation benchmark for modern historical period",
            "Feature_Role_Task_B": "PROHIBITED AS A FUTURE PREDICTOR. Cannot be observed in advance.",
            "Extrapolation_Limits_to_2100": "FATAL LEAKAGE if assumed available post-2024. Altimetry is an observational diagnostic, never a predictive forcing."
        },
        {
            "Feature_Name": "IMBIE_Partitioned_SMB_Anomaly_Gt_yr",
            "Physical_Domain": "Atmospheric Calibration Series",
            "Task_A_Availability_Historical": "YES: Extracted from IMBIE-3 CSV (1979–2023)",
            "Task_B_Availability_Future": "NO: IMBIE HISTORICAL BENCHMARK ENDS IN 2023",
            "IMBIE_Provenance_Status": "Derived from IMBIE (direct table column)",
            "Feature_Role_Task_A": "Atmospheric forcing in reconstruction emulation",
            "Feature_Role_Task_B": "PROHIBITED AS FUTURE FORCING. Extrapolating historical IMBIE anomalies into 2100 is physically invalid; must use climate model projections.",
            "Extrapolation_Limits_to_2100": "Historical IMBIE anomaly series has zero future coverage. Autoregressive extrapolation of IMBIE creates synthetic noise without physical climate forcing."
        },
        {
            "Feature_Name": "Glacier_Dynamics_Relaxation_State_D_dyn",
            "Physical_Domain": "Dynamic Glacier Memory",
            "Task_A_Availability_Historical": "YES: Calibrated post-collapse exponential decay functions (Wuite 2015, Rott 2011)",
            "Task_B_Availability_Future": "YES: Modeled as an internal state variable: dD/dt = -gamma * D_dyn + F_climate",
            "IMBIE_Provenance_Status": "Calibrated against IMBIE satellite epochs historically",
            "Feature_Role_Task_A": "Represents transient surge acceleration and post-collapse relaxation",
            "Feature_Role_Task_B": "Enforces physical post-collapse relaxation and prevents unconstrained linear acceleration to 2100",
            "Extrapolation_Limits_to_2100": "Decay timescale gamma (~10–15 years) is calibrated from Larsen B; future collapses (e.g. Larsen C) may exhibit different rheological timescales."
        }
    ]

    df_task = pd.DataFrame(data)
    out_path = os.path.join(TABLES_DIR, "task_feature_matrix_design.csv")
    df_task.to_csv(out_path, index=False)
    print(f"Saved: {out_path}")
    print(df_task[["Feature_Name", "Task_A_Availability_Historical", "Task_B_Availability_Future", "IMBIE_Provenance_Status"]].to_string())
    return df_task


# =========================================================================
# 3. Model Architecture Comparison (7 Candidate Models)
# =========================================================================
def generate_model_architecture_comparison():
    print("\n--- [3] Generating Model Architecture Comparison Table ---")
    data = [
        {
            "Model_ID": "M0_PERSISTENCE",
            "Model_Name": "Persistence Baseline (Lag-1 / Rolling Mean)",
            "Mathematical_Form": "y_hat[b, t] = y[b, t-1]  (or 3-year rolling mean: y_hat[b, t] = mean(y[b, t-3:t-1]))",
            "Dataset_Suitability": "Essential baseline benchmark. Establishes the performance floor that any trained ML model must beat.",
            "Expected_Overfitting_Risk": "Zero overfitting risk (zero learnable parameters).",
            "Feature_Requirements": "Requires only preceding target volume change y[b, t-1].",
            "Hyperparameters_to_Evaluate": "Lag window length: k in {1, 2, 3 years}.",
            "Uncertainty_Representation": "Empirical standard deviation of historical inter-annual residuals: sigma = std(y[t] - y[t-1]).",
            "Primary_Limitations": "Completely incapable of anticipating climate-driven regime shifts or sudden glacier surges. Suffers lag delay during dynamic transitions.",
            "Recommendation_Status": "Mandatory Baseline Benchmark (Model M0)"
        },
        {
            "Model_ID": "M1_OLS_LINEAR",
            "Model_Name": "Ordinary Least Squares (OLS) Linear Regression",
            "Mathematical_Form": "y_hat[b, t] = beta_0 + sum_j beta_j * X_j[b, t]",
            "Dataset_Suitability": "Provides maximum parameter transparency and baseline interpretability of physical feature sensitivities.",
            "Expected_Overfitting_Risk": "Moderate-to-high risk when feature count p > 5 due to multicollinearity among climate variables (e.g. temperature vs runoff vs melt). Unregularized weights can destabilize with N=81.",
            "Feature_Requirements": "Normalized exogenous climate anomalies (Precipitation, Runoff, Temperature) + static basin area/thickness.",
            "Hyperparameters_to_Evaluate": "None (closed-form normal equation: beta = (X^T X)^(-1) X^T y). Feature selection via forward stepwise.",
            "Uncertainty_Representation": "Classical analytical OLS covariance: Var(y_hat) = sigma^2 * (1 + x_0^T (X^T X)^(-1) x_0).",
            "Primary_Limitations": "Zero capacity for non-linear threshold dynamics (e.g. melt onset at 0 deg C). Vulnerable to multicollinearity inflation.",
            "Recommendation_Status": "Linear Reference Model (Model M1)"
        },
        {
            "Model_ID": "M2_RIDGE",
            "Model_Name": "Ridge Regression (L2-Regularized Linear)",
            "Mathematical_Form": "min_beta ||y - X beta||_2^2 + alpha * ||beta||_2^2",
            "Dataset_Suitability": "Highly suitable for small sample sizes (N=81). Shrinks correlated climate features, prevents weight explosion, and ensures stable matrix inversion even with collinear predictors.",
            "Expected_Overfitting_Risk": "Low when regularization penalty alpha is properly tuned on the chronological validation split.",
            "Feature_Requirements": "Standardized climate features (Z-score normalized) + lagged glacier dynamic terms.",
            "Hyperparameters_to_Evaluate": "L2 penalty alpha in logspace(-3, 3) (e.g. [1e-3, 1e-2, 0.1, 1.0, 10.0, 100.0]).",
            "Uncertainty_Representation": "Bayesian Ridge formulation provides analytical posterior predictive variance: sigma^2_pred(x) = 1/alpha_noise + x^T Sigma_post x.",
            "Primary_Limitations": "Preserves all features (no automatic sparsity/variable selection); strictly linear feature response.",
            "Recommendation_Status": "Primary Candidate Linear Architecture (Model M2)"
        },
        {
            "Model_ID": "M3_ELASTICNET",
            "Model_Name": "ElasticNet Regression (L1 + L2 Regularization)",
            "Mathematical_Form": "min_beta ||y - X beta||_2^2 + alpha * [l1_ratio * ||beta||_1 + 0.5 * (1 - l1_ratio) * ||beta||_2^2]",
            "Dataset_Suitability": "Exceptional fit for climate feature matrices where predictors are grouped and collinear. L1 promotes sparse physical feature selection while L2 maintains stability across grouped variables.",
            "Expected_Overfitting_Risk": "Very low. Dual regularization aggressively suppresses spurious weights on N=81 sample size.",
            "Feature_Requirements": "Standardized climate anomalies, static basin parameters, ocean thermal indices, and atmospheric circulation proxies.",
            "Hyperparameters_to_Evaluate": "alpha in logspace(-3, 2); l1_ratio in [0.1, 0.3, 0.5, 0.7, 0.9, 0.99].",
            "Uncertainty_Representation": "Bootstrap residual resampling or Bayesian credible intervals.",
            "Primary_Limitations": "Piecewise linear response; cannot model non-linear saturation curves without explicit polynomial/interaction features.",
            "Recommendation_Status": "Primary Candidate Regularized Architecture (Model M3)"
        },
        {
            "Model_ID": "M4_SHALLOW_RF",
            "Model_Name": "Shallow Random Forest Regressor",
            "Mathematical_Form": "y_hat[b, t] = (1 / B) * sum_{b=1}^B T_b(X; theta_b) with max_depth <= 3",
            "Dataset_Suitability": "Captures non-linear thresholds (e.g., runoff triggering, collapse surge initiation) without requiring parametric form specification.",
            "Expected_Overfitting_Risk": "Severe risk if unconstrained. Standard deep random forests will memorize the 81 training instances. Must strictly enforce shallow depth (max_depth in [2, 3]) and large leaf size (min_samples_leaf >= 5).",
            "Feature_Requirements": "Raw or normalized climate features; handles mixed continuous and categorical basin identifiers natively.",
            "Hyperparameters_to_Evaluate": "n_estimators in [50, 100]; max_depth in [2, 3]; min_samples_leaf in [4, 6, 8]; max_features in ['sqrt', 0.5, 0.7].",
            "Uncertainty_Representation": "Ensemble variance across tree predictions: Var(y_hat) = (1 / B) * sum (T_b - y_hat)^2.",
            "Primary_Limitations": "Cannot extrapolate outside the training feature domain (predicts constant value beyond historical max/min climate forcings).",
            "Recommendation_Status": "Primary Candidate Non-Linear Architecture (Model M4)"
        },
        {
            "Model_ID": "M5_SHALLOW_GBDT",
            "Model_Name": "Shallow Gradient Boosted Decision Trees (XGBoost / LightGBM)",
            "Mathematical_Form": "y_hat_m = y_hat_{m-1} + eta * f_m(X) with depth <= 2 and L2 leaf regularization",
            "Dataset_Suitability": "Highly capable of fitting subtle residual patterns in atmospheric forcing and non-linear threshold responses.",
            "Expected_Overfitting_Risk": "Extremely high if learning rate is too large or trees are deep. Must constrain to shallow depth (max_depth = 2), small learning rate (eta in [0.01, 0.05]), high subsampling (0.8), and heavy L2 leaf regularization (reg_lambda >= 5.0).",
            "Feature_Requirements": "Standardized or unscaled features; robust to monotonic feature transformations.",
            "Hyperparameters_to_Evaluate": "n_estimators in [30, 60, 100]; max_depth in [2, 3]; learning_rate in [0.01, 0.03, 0.05]; subsample in [0.7, 0.8]; reg_lambda in [1.0, 5.0, 10.0].",
            "Uncertainty_Representation": "Quantile regression loss (pinball loss at 0.05, 0.5, 0.95 quantiles) or natural gradient boosting (NGBoost) for parametric distribution output.",
            "Primary_Limitations": "Prone to step-function artifacts in extrapolation; high sensitivity to hyperparameter tuning on small validation sets.",
            "Recommendation_Status": "Secondary Candidate Non-Linear Architecture (Model M5)"
        },
        {
            "Model_ID": "M6_GPR",
            "Model_Name": "Gaussian Process Regressor (GPR with Physics-Informed Kernel)",
            "Mathematical_Form": "y ~ GP(m(x), k(x, x') + sigma_noise^2 * delta_ij) with Matérn 3/2 + Exponential kernel",
            "Dataset_Suitability": "Ideal mathematical match for small datasets (N=81 training points, well within O(N^3) computational feasibility limit of N~1000). Provides exact analytical predictive distributions and native Bayesian uncertainty.",
            "Expected_Overfitting_Risk": "Low-to-moderate. Regularized by the marginal likelihood objective. Lengthscale bounds prevent fitting high-frequency noise.",
            "Feature_Requirements": "Low-dimensional standardized feature space (p <= 5 features; e.g. PCA components or core physical features: Precipitation, Runoff, Temperature, Basin_ID).",
            "Hyperparameters_to_Evaluate": "Kernel selection (Matérn 3/2 vs Matérn 5/2 vs RBF + WhiteKernel); lengthscale bounds [0.5, 10.0]; noise level fixed to audited uncorrelated measurement error (alpha = sigma_noise^2).",
            "Uncertainty_Representation": "Exact analytical posterior predictive variance: Var(y_hat_*) = k(x_*, x_*) - k_*^T (K + sigma_noise^2 I)^(-1) k_*.",
            "Primary_Limitations": "Requires compact feature space (vulnerable to curse of dimensionality if p > 8); kernel matrix inversion sensitive to identical input coordinates.",
            "Recommendation_Status": "Primary Candidate Probabilistic Architecture (Model M6)"
        }
    ]

    df_models = pd.DataFrame(data)
    out_path = os.path.join(TABLES_DIR, "model_architecture_comparison.csv")
    df_models.to_csv(out_path, index=False)
    print(f"Saved: {out_path}")
    print(df_models[["Model_ID", "Model_Name", "Expected_Overfitting_Risk", "Recommendation_Status"]].to_string())
    return df_models


# =========================================================================
# 4. Basin Modeling Strategy Comparison
# =========================================================================
def generate_basin_modeling_strategy_comparison():
    print("\n--- [4] Generating Basin Modeling Strategy Comparison Table ---")
    data = [
        {
            "Strategy_ID": "STRAT_1_SEPARATE",
            "Strategy_Name": "Separate Basin Models (3 Dedicated Independent Models)",
            "Model_Structure": "Model_Hp(X_hp) -> y_hp;  Model_Ipp(X_ipp) -> y_ipp;  Model_Ipj(X_ipj) -> y_ipj",
            "Sample_Efficiency": "POOR: Divides the N=81 training records into 3 micro-datasets of only N=27 samples each. Severe sample starvation.",
            "Physical_Fidelity": "HIGH for basin-specific dynamics: Allows completely independent coefficients for Larsen B post-surge relaxation in Ipp-J vs tidewater retreat in I-Ipp.",
            "Shared_Climate_Signal_Handling": "POOR: Re-estimates common climate sensitivity (e.g. precipitation response to atmospheric warming) independently three times on tiny samples.",
            "Cross_Basin_Covariance": "IGNORED: Assumes zero statistical correlation between basin prediction errors.",
            "Regional_Sum_Consistency": "UNCONSTRAINED: Sum of separate predictions y_hp + y_ipp + y_ipj is not structurally constrained to match regional physical mass balance.",
            "Overfitting_Risk": "EXTREME: Fitting multiple parameters on N=27 data points carries severe risk of memorizing observational noise.",
            "Evaluation_Verdict": "REJECTED as primary strategy due to sample starvation (N=27 per model)."
        },
        {
            "Strategy_ID": "STRAT_2_POOLED_BASIN_ID",
            "Strategy_Name": "Pooled Model with Basin Identity & Static Descriptors",
            "Model_Structure": "Model_Unified(X_climate, Static_Basin_Descriptors, Basin_ID_OneHot) -> y[b, t]",
            "Sample_Efficiency": "EXCELLENT: Pools all 3 basins to create N=81 training instances and N=21 validation instances. Maximizes training sample efficiency.",
            "Physical_Fidelity": "HIGH: Shares learning of peninsula-wide climate forcing sensitivities (snowfall, melt, temperature) while distinguishing basins via static physical descriptors (area, mean thickness, bed slope at flux gates) and basin indicator intercepts.",
            "Shared_Climate_Signal_Handling": "EXCELLENT: Explicitly pools regional atmospheric forcing across the peninsula.",
            "Cross_Basin_Covariance": "MODERATE: Residual correlation across basins at the same time step t can be handled via clustered standard errors or generalized estimating equations (GEE).",
            "Regional_Sum_Consistency": "NATURAL: Sum of predictions directly forms the derived regional Domain A diagnostic.",
            "Overfitting_Risk": "LOW-TO-MODERATE: Strong regularization on N=81 instances provides robust generalization.",
            "Evaluation_Verdict": "RECOMMENDED PRIMARY STRATEGY for linear, tree-based, and gradient boosting architectures."
        },
        {
            "Strategy_ID": "STRAT_3_MULTI_OUTPUT",
            "Strategy_Name": "Multi-Output Vector Regression Architecture",
            "Model_Structure": "Model_Vector(X_shared_climate) -> [y_hp, y_ipp, y_ipj]^T in R^3",
            "Sample_Efficiency": "MODERATE: Operates on N=27 temporal time steps, but predicts a 3-dimensional vector simultaneously.",
            "Physical_Fidelity": "EXCELLENT: Explicitly models the full 3x3 error covariance matrix across basins: Sigma_basin = Cov(e_hp, e_ipp, e_ipj).",
            "Shared_Climate_Signal_Handling": "EXCELLENT: Directly maps shared regional atmospheric forcing (SAM, regional temp, total snowfall) to the 3 basin outputs.",
            "Cross_Basin_Covariance": "OPTIMAL: Fully models cross-basin dependence and physical co-variability.",
            "Regional_Sum_Consistency": "STRUCTURAL: Can enforce exact regional mass balance via linear constraint: [1, 1, 1] * y_hat = y_hat_DomainA.",
            "Overfitting_Risk": "MODERATE: Requires multi-target regularization (e.g. MultiTaskElasticNet or Multi-Output GPR).",
            "Evaluation_Verdict": "RECOMMENDED ALTERNATIVE STRATEGY for Multi-Task ElasticNet and Multi-Output Gaussian Process Regression."
        }
    ]

    df_strat = pd.DataFrame(data)
    out_path = os.path.join(TABLES_DIR, "basin_modeling_strategy_comparison.csv")
    df_strat.to_csv(out_path, index=False)
    print(f"Saved: {out_path}")
    print(df_strat[["Strategy_ID", "Strategy_Name", "Sample_Efficiency", "Evaluation_Verdict"]].to_string())
    return df_strat


# =========================================================================
# Main Execution Controller
# =========================================================================
def main():
    print("=" * 80)
    print("EXECUTING PHASE 4A: ML ARCHITECTURE AND EXPERIMENTAL DESIGN")
    print("=" * 80)

    generate_row_level_split_manifest()
    generate_task_feature_matrix_design()
    generate_model_architecture_comparison()
    generate_basin_modeling_strategy_comparison()

    print("\nPhase 4A Design Tables Successfully Generated.")

if __name__ == "__main__":
    main()

