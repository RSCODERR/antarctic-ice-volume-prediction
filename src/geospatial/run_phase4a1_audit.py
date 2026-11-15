"""
Phase 4A.1: Methodological Audit and Final ML Design Freeze
============================================================
Generates the 6 required audit and design tables:
1. reports/tables/embargo_justification_audit.csv
2. reports/tables/feature_target_overlap_audit.csv
3. reports/tables/rolling_origin_fold_manifest.csv
4. reports/tables/uncertainty_assumption_audit.csv
5. reports/tables/revised_model_comparison.csv
6. reports/tables/revised_feature_availability_matrix.csv
"""

import os
import sys
import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
TABLES_DIR = os.path.join(REPORTS_DIR, "tables")

MANIFEST_CSV = os.path.join(TABLES_DIR, "split_manifest_row_level.csv")
TARGET_CSV = os.path.join(TABLES_DIR, "ml_target_dataset.csv")

# =========================================================================
# 1. Embargo Justification Audit Table
# =========================================================================
def generate_embargo_justification_audit():
    print("\n--- [1] Generating Embargo Justification Audit Table ---")
    data = [
        {
            "Embargo_Buffer_ID": "EMBARGO_BUFFER_1 (2006–2007)",
            "Calendar_Years": "2006, 2007",
            "Basins_Affected": "Hp-I (Rows 27, 28), I-Ipp (Rows 73, 74), Ipp-J (Rows 119, 120)",
            "Record_Count": "6 basin-year records (4.3% of physical dataset)",
            "Target_Leakage_Assessment": "NO LEAKAGE RISK: Targets are discrete annual calendar integrals (y_t = integral Net_MB dt from Jan 1 to Dec 31). The 2006 and 2007 target intervals strictly terminated on 2007-12-31, prior to the start of the 2008 validation period. Zero temporal overlap between annual target labels.",
            "Autoregressive_Lag_Availability": "LEGITIMATE LAG PREDICTORS: At prediction time (2008-01-01), the 2007 (lag-1) and 2006 (lag-2) observations were already in the past. Quarantining them actually breaks the ability of autoregressive models (AR(1), AR(2)) to predict 2008 and 2009 without imputing synthetic gaps.",
            "Temporal_Dependence_Assessment": "Decadal error autocorrelation (tau = 5 yrs) links adjacent annual errors. However, in standard forward walk-forward time series forecasting, training strictly on t <= t-1 to predict t handles serial correlation naturally. Quarantining 2 years forces an artificial 2-year forecast horizon.",
            "Regime_Shift_Isolation": "2006–2007 was a post-Larsen-B dynamic relaxation transition. While physically distinct, dynamic relaxation is a real physical process that models must learn, not an artifact to be discarded.",
            "Sensor_Discontinuity_Assessment": "Intermediate sensor era (ICESat-1 / Envisat / GRACE RL06). Valid multi-sensor satellite constraints were active throughout 2006–2007.",
            "Audit_Verdict": "SCIENTIFICALLY UNJUSTIFIED DISCARD: Quarantining 2006–2007 from both training and validation discards 6 physical records without preventing target leakage.",
            "Recommended_Correction": "REVISE SPLIT BOUNDARY: Absorb 2006–2007 into the Training set (Train becomes 1979–2007, N=87 basin-years) or use them as active validation targets. Lagged features from 2006–2007 must remain available."
        },
        {
            "Embargo_Buffer_ID": "EMBARGO_BUFFER_2 (2015)",
            "Calendar_Years": "2015",
            "Basins_Affected": "Hp-I (Row 36), I-Ipp (Row 82), Ipp-J (Row 128)",
            "Record_Count": "3 basin-year records (2.2% of physical dataset)",
            "Target_Leakage_Assessment": "NO LEAKAGE RISK: The 2015 annual volume change interval ended on 2015-12-31. The 2016 test period starts on 2016-01-01. Zero label overlap.",
            "Autoregressive_Lag_Availability": "LEGITIMATE LAG PREDICTOR: The 2015 state is the essential lag-1 input for predicting the first test year (2016). Quarantining 2015 makes 1-year persistence prediction for 2016 impossible without referencing 2015.",
            "Temporal_Dependence_Assessment": "Identical to 2006–2007. Standard walk-forward protocol does not require discarding single boundary years.",
            "Regime_Shift_Isolation": "Sentinel-1A launched in April 2014; 2015 was the onset of dense SAR constellation velocity tracking. This is a sensor improvement, not target leakage.",
            "Sensor_Discontinuity_Assessment": "CryoSat-2 and Landsat-8 were continuously active in 2014, 2015, and 2016.",
            "Audit_Verdict": "SCIENTIFICALLY UNJUSTIFIED DISCARD: Discarding 2015 removes 3 observation-rich records from evaluation.",
            "Recommended_Correction": "REVISE SPLIT BOUNDARY: Absorb 2015 into the Validation set (Validation becomes 2008–2015, N=24 basin-years). In the test set, 2015 observations must serve as lag-1 inputs for predicting 2016."
        }
    ]
    df = pd.DataFrame(data)
    out_path = os.path.join(TABLES_DIR, "embargo_justification_audit.csv")
    df.to_csv(out_path, index=False)
    print(f"Saved: {out_path}")
    return df


# =========================================================================
# 2. Feature-Target Overlap Audit Table
# =========================================================================
def generate_feature_target_overlap_audit():
    print("\n--- [2] Generating Feature-Target Overlap Audit Table ---")
    data = [
        {
            "Feature_Name": "IMBIE_Partitioned_SMB_Anomaly_Gt_yr",
            "Target_Constituent_Relationship": "Direct Same-Year Additive Constituent (SMB_t)",
            "Algebraic_Recoverability_Risk": "FATAL: If fed together with discharge, y_t = (SMB_t - D_t)/0.917 is trivially solved via exact subtraction. Model learns arithmetic, not ice dynamics.",
            "Allowed_in_Experiment_A1_Accounting": "YES: Required to verify physical mass accounting identity.",
            "Allowed_in_Experiment_A2_Prediction": "STRICTLY PROHIBITED as same-year predictor in true prediction task. May only be used as lagged forcing (SMB_{t-1}) or replaced with raw downscaled climate forecasts.",
            "Corrective_Action_Required": "Ban from Task A2 predictive feature matrix. Replace with lagged precipitation and temperature anomalies."
        },
        {
            "Feature_Name": "Glacier_Dynamics_Relaxation_State_D_dyn",
            "Target_Constituent_Relationship": "Direct Same-Year Subtractive Constituent (Discharge D_t)",
            "Algebraic_Recoverability_Risk": "FATAL: D_dyn is the primary component of historical discharge. Feeding D_dyn allows the model to reconstruct the target algebraically.",
            "Allowed_in_Experiment_A1_Accounting": "YES: Required for physical accounting verification.",
            "Allowed_in_Experiment_A2_Prediction": "STRICTLY PROHIBITED as unlagged input. Must be lagged by at least 1 year (D_{dyn, t-1}) or driven by internal differential equation state evolution.",
            "Corrective_Action_Required": "Enforce strict lag-1 structure (D_{dyn, t-1}) in predictive models."
        },
        {
            "Feature_Name": "Annual_Discharge_Central_Gt_yr",
            "Target_Constituent_Relationship": "Exact Same-Year Target Subtrahend (D_t)",
            "Algebraic_Recoverability_Risk": "FATAL: Perfect mathematical overlap. Target is directly constructed from this column.",
            "Allowed_in_Experiment_A1_Accounting": "YES: Accounting identity verification.",
            "Allowed_in_Experiment_A2_Prediction": "STRICTLY PROHIBITED in any predictive ML feature set.",
            "Corrective_Action_Required": "Completely excluded from ML feature matrix."
        },
        {
            "Feature_Name": "RACMO_Precipitation_Snowfall_mm_yr",
            "Target_Constituent_Relationship": "Physical Atmospheric Driver of SMB",
            "Algebraic_Recoverability_Risk": "LOW-TO-MODERATE: Correlated with SMB, but not algebraically identical (SMB = Precip - Sublimation - Runoff + Refreezing).",
            "Allowed_in_Experiment_A1_Accounting": "YES: Informational context.",
            "Allowed_in_Experiment_A2_Prediction": "YES: Legitimate exogenous climate predictor if available from climate model/reanalysis at prediction time.",
            "Corrective_Action_Required": "Allowed as exogenous climate forcing."
        },
        {
            "Feature_Name": "RACMO_Surface_Runoff_Melt_mm_yr",
            "Target_Constituent_Relationship": "Physical Atmospheric Driver of SMB",
            "Algebraic_Recoverability_Risk": "LOW-TO-MODERATE: Correlated with ablation, but non-linearly modulated by firn refreezing.",
            "Allowed_in_Experiment_A1_Accounting": "YES: Informational context.",
            "Allowed_in_Experiment_A2_Prediction": "YES: Legitimate exogenous climate predictor.",
            "Corrective_Action_Required": "Allowed as exogenous climate forcing."
        },
        {
            "Feature_Name": "Regional_Surface_Air_Temperature_2m_K",
            "Target_Constituent_Relationship": "Exogenous Thermodynamic State Variable",
            "Algebraic_Recoverability_Risk": "NONE: Independent meteorological state variable; target cannot be algebraically recovered from temperature.",
            "Allowed_in_Experiment_A1_Accounting": "YES: Informational context.",
            "Allowed_in_Experiment_A2_Prediction": "YES: Primary climate feature.",
            "Corrective_Action_Required": "Standardize (Z-score) inside training folds."
        },
        {
            "Feature_Name": "ITS_LIVE_Flow_Velocity_Lag1_m_yr",
            "Target_Constituent_Relationship": "Lagged Kinematic State Variable (v_{t-1})",
            "Algebraic_Recoverability_Risk": "NONE: Strictly lagged by 1 year. Observed prior to prediction epoch.",
            "Allowed_in_Experiment_A1_Accounting": "YES.",
            "Allowed_in_Experiment_A2_Prediction": "YES: Legitimate autoregressive kinematic predictor for Task A2.",
            "Corrective_Action_Required": "Must enforce lag >= 1 year. Available only for years with historical satellite coverage (>=1986)."
        },
        {
            "Feature_Name": "Target_Annual_Volume_Change_Lag1_km3_yr",
            "Target_Constituent_Relationship": "Autoregressive Lag of Target (y_{t-1})",
            "Algebraic_Recoverability_Risk": "NONE: Strictly lagged. Represents past volume change.",
            "Allowed_in_Experiment_A1_Accounting": "YES.",
            "Allowed_in_Experiment_A2_Prediction": "YES: Primary feature for persistence and AR(1) models.",
            "Corrective_Action_Required": "Cannot be evaluated for 1979 (no 1978 target exists). Must initialize at 1980."
        }
    ]
    df = pd.DataFrame(data)
    out_path = os.path.join(TABLES_DIR, "feature_target_overlap_audit.csv")
    df.to_csv(out_path, index=False)
    print(f"Saved: {out_path}")
    return df


# =========================================================================
# 3. Uncertainty Assumption Audit Table
# =========================================================================
def generate_uncertainty_assumption_audit():
    print("\n--- [3] Generating Uncertainty Assumption Audit Table ---")
    data = [
        {
            "Uncertainty_Term": "Cumulative Reconstruction Uncertainty (+/- 204.82 km3)",
            "What_It_Actually_Describes": "Integrated 46-year variance of Domain A solid ice loss: Var = sum(sigma_rate^2). Represents the cumulative uncertainty of the entire 1979–2024 total volume loss across the whole peninsula.",
            "Appropriate_for_Annual_Basin_Likelihood": "STRICTLY INAPPROPRIATE: Annual basin volume changes range from -1.0 to -25.0 km3/yr. Injecting +/- 204.82 km3 as observation noise variance (41,950 km6) assumes observation noise is 10 to 40 times larger than the physical signal, destroying all model likelihoods.",
            "Required_Covariance_Assumptions": "Assumes zero temporal autocorrelation across 46 years (white noise rate errors). Under decadal autocorrelation (tau=5 yrs), cumulative uncertainty expands to +/- 609.52 km3.",
            "Required_Mathematical_Correction": "Use the ANNUAL BASIN-LEVEL RATE UNCERTAINTY: sigma_{basin, b, t} = sigma_{DomainA, t} * sqrt(Area_b / Area_total) / rho_ice, which yields +/- 5.0 to +/- 12.0 km3/yr per basin."
        },
        {
            "Uncertainty_Term": "Gaussian Process Predictive Variance (sigma^2_pred)",
            "What_It_Actually_Describes": "Analytical posterior variance combining epistemic uncertainty (distance from training points in kernel feature space) and aleatoric observation noise (alpha = sigma_noise^2).",
            "Appropriate_for_Annual_Basin_Likelihood": "APPROPRIATE ONLY IF NOISE FLOOR IS SET TO ANNUAL RATE SIGMA: Valid if alpha is set to the annual basin rate variance (~25 to 100 km6/yr2). Incompatible with cumulative +/- 204.82 km3.",
            "Required_Covariance_Assumptions": "Assumes Gaussian process prior on f(x) with Matérn or RBF covariance. Assumes homoscedastic Gaussian likelihood noise. If noise is heteroscedastic across satellite epochs (1979 vs 2020), standard GPR underestimates historical noise.",
            "Required_Mathematical_Correction": "Set GPR noise hyperparameter alpha = (sigma_{annual_basin})^2. Bound kernel lengthscales in [0.5, 5.0] to prevent lengthscale collapse on N=81 samples."
        },
        {
            "Uncertainty_Term": "Ordinary Ridge Regression 'Uncertainty'",
            "What_It_Actually_Describes": "Ordinary Ridge regression is a deterministic penalized least squares estimator (min ||y - Xb||^2 + alpha ||b||^2). It produces a SINGLE POINT ESTIMATE with ZERO native probabilistic uncertainty.",
            "Appropriate_for_Annual_Basin_Likelihood": "NOT APPLICABLE TO STANDARD RIDGE: Ordinary Ridge has no likelihood distribution or parameter standard errors.",
            "Required_Covariance_Assumptions": "Requires Bayesian reformulation (Bayesian Ridge Regression) assuming Gaussian prior on weights p(beta) = N(0, gamma^-1 I) and Gaussian noise p(y|beta) = N(X beta, lambda^-1 I).",
            "Required_Mathematical_Correction": "Explicitly implement BayesianRidge (MacKay 1992 evidence framework) to compute analytical posterior predictive variance: Var(y_hat) = 1/lambda + x^T Sigma_post x."
        },
        {
            "Uncertainty_Term": "Multi-Output Cross-Basin Covariance (Sigma_basin)",
            "What_It_Actually_Describes": "The 3x3 contemporaneous error covariance matrix between basins at the same time step t: Sigma_{b1, b2} = Cov(e_{b1, t}, e_{b2, t}).",
            "Appropriate_for_Annual_Basin_Likelihood": "APPROPRIATE FOR JOINT VECTOR LIKELIHOOD: Captures simultaneous peninsula-wide climate shocks (e.g. extreme warm foehn year affecting both Graham Land basins).",
            "Required_Covariance_Assumptions": "Standard scikit-learn MultiOutputRegressor DOES NOT estimate cross-target covariance (it fits 3 separate single-target models). A full error covariance matrix requires Seemingly Unrelated Regression (SUR) or Multi-Task Gaussian Process.",
            "Required_Mathematical_Correction": "Do not claim MultiOutputRegressor exploits residual covariance. Use empirical sample covariance of validation residuals: Sigma_e = (1/N) * sum e_t e_t^T to evaluate cross-basin error dependence."
        }
    ]
    df = pd.DataFrame(data)
    out_path = os.path.join(TABLES_DIR, "uncertainty_assumption_audit.csv")
    df.to_csv(out_path, index=False)
    print(f"Saved: {out_path}")
    return df


# =========================================================================
# 4. Rolling-Origin Fold Manifest Table
# =========================================================================
def generate_rolling_origin_fold_manifest():
    print("\n--- [4] Generating Rolling-Origin Fold Manifest Table ---")
    # Total historical years: 1979 to 2024 (46 years)
    # Training window: 1979 to 2005 (or 2007)
    # Validation window: 2008 to 2014 (or 2015)
    # Test window: 2016 to 2024 (9 years, strictly held out)

    # We design walk-forward folds within the historical development set (1979–2014)
    # Minimum training window: 16 years (1979–1994, 48 basin-years)
    # This leaves 1995–2014 (20 years) for progressive rolling-origin evaluation.

    folds = []
    min_train_end = 1994
    max_dev_year = 2014

    for fold_idx, val_year in enumerate(range(min_train_end + 1, max_dev_year + 1), start=1):
        train_start = 1979
        train_end = val_year - 1
        n_train_years = train_end - train_start + 1
        n_train_samples = n_train_years * 3  # 3 basins per year

        # Check if val_year is in embargo periods of Phase 4A
        if val_year in [2006, 2007]:
            split_regime = "Quarantined in Phase 4A (Embargo 1); Active in Revised Walk-Forward"
        elif val_year == 2015:
            split_regime = "Quarantined in Phase 4A (Embargo 2); Active in Revised Walk-Forward"
        elif val_year <= 2005:
            split_regime = "Internal Training Walk-Forward Fold"
        else:
            split_regime = "Phase 4A Formal Validation Window Fold"

        folds.append({
            "Fold_ID": f"Fold_{fold_idx:02d}",
            "Train_Period": f"{train_start}–{train_end}",
            "Train_Years_Count": n_train_years,
            "Train_Basin_Samples_N": n_train_samples,
            "Validation_Year": val_year,
            "Validation_Basins_Evaluated": "Hp-I, I-Ipp, Ipp-J (All 3 basins)",
            "Validation_Samples_N": 3,
            "Split_Regime_Classification": split_regime,
            "Preprocessing_Enforcement": "Scalers, imputers, and feature selectors fit STRICTLY on 1979–{0} slice; zero transform leakage into {1}".format(train_end, val_year),
            "Persistence_Benchmark_Generation": f"Predicted using y[b, {train_end}] (lag-1 value from preceding active year)",
            "Cross_Basin_Integration": f"Validation evaluate all 3 basins simultaneously; compute Domain A sum: y_hat_DomainA = sum_b y_hat_b"
        })

    df = pd.DataFrame(folds)
    out_path = os.path.join(TABLES_DIR, "rolling_origin_fold_manifest.csv")
    df.to_csv(out_path, index=False)
    print(f"Saved: {out_path} (Total Folds: {len(df)})")
    return df


# =========================================================================
# 5. Revised Model Comparison Table
# =========================================================================
def generate_revised_model_comparison():
    print("\n--- [5] Generating Revised Model Comparison Table ---")
    data = [
        {
            "Model_ID": "M0",
            "Model_Name": "Basin-Specific Persistence Baseline",
            "Intended_Task": "Task A2 (Historical Prediction Floor) & Task B (Static Drift Reference)",
            "Minimum_Data_Requirements": "Requires y[b, t-1] (1-year preceding target observation per basin).",
            "Feature_Assumptions": "Assumes glacier volume change follows a random walk: E[y_t | y_{t-1}] = y_{t-1}.",
            "Complexity_Controls": "Zero learnable parameters. No regularization needed.",
            "Uncertainty_Interpretation": "Empirical standard deviation of historical inter-annual increments: sigma = std(y_t - y_{t-1}) ~ +/- 3.5 km3/yr per basin.",
            "Evaluation_Metrics": "RMSE, MAE, NSE (NSE = 0.0 by definition relative to itself), Cumulative Drift Delta V_drift.",
            "Critical_Methodological_Reassessment": "MANDATORY PERFORMANCE FLOOR: Any trained statistical or machine learning model that cannot beat M0 RMSE in walk-forward validation must be rejected."
        },
        {
            "Model_ID": "M1",
            "Model_Name": "OLS Linear Reference (Climate Forcing Baseline)",
            "Intended_Task": "Task A1 (Accounting Verification) & Task A2 (Linear Reference)",
            "Minimum_Data_Requirements": "Requires N >= p + 1. For p=4 features, requires >= 5 training years.",
            "Feature_Assumptions": "Assumes linear, non-saturating relationship between climate anomalies and annual volume change.",
            "Complexity_Controls": "None. Ordinary least squares closed-form solution.",
            "Uncertainty_Interpretation": "Classical parameter variance: Var(b) = s^2 (X^T X)^-1.",
            "Evaluation_Metrics": "RMSE, MAE, R^2, AIC, BIC, F-statistic.",
            "Critical_Methodological_Reassessment": "BENCHMARK ONLY: Vulnerable to multicollinearity between temperature, melt, and runoff. Unregularized weights will destabilize if p > 5."
        },
        {
            "Model_ID": "M2",
            "Model_Name": "Ridge / Bayesian Ridge Regression",
            "Intended_Task": "Task A2 (Primary Linear Predictor) & Task B (Robust Future Extrapolation)",
            "Minimum_Data_Requirements": "N >= 30 samples. Exceptionally stable on small sample sizes (N=81).",
            "Feature_Assumptions": "Linear response with zero-mean Gaussian prior on weights: beta ~ N(0, alpha^-1 I).",
            "Complexity_Controls": "L2 regularization penalty alpha tuned via rolling-origin walk-forward CV.",
            "Uncertainty_Interpretation": "Bayesian Ridge provides exact analytical posterior predictive variance: Var(y_hat) = 1/lambda + x^T Sigma_post x.",
            "Evaluation_Metrics": "Walk-forward RMSE, MAE, R^2, Negative Log-Likelihood (NLL), Cumulative Mass Drift.",
            "Critical_Methodological_Reassessment": "PRIMARY RECOMMENDED LINEAR ARCHITECTURE: Extremely robust to climate feature collinearity; cannot overfit when alpha is tuned; well-behaved linear extrapolation to 2100."
        },
        {
            "Model_ID": "M3",
            "Model_Name": "ElasticNet Regression",
            "Intended_Task": "Task A2 (Feature Selection & Regularized Regression) & Task B",
            "Minimum_Data_Requirements": "N >= 30 samples. Effective when p is moderately large (p ~ 6–10 candidate features).",
            "Feature_Assumptions": "Sparsity prior (Laplace) on irrelevant features; grouping prior (Gaussian) on collinear climate variables.",
            "Complexity_Controls": "Dual regularization: alpha (penalty magnitude) and l1_ratio (mixing parameter between L1 and L2).",
            "Uncertainty_Interpretation": "Residual bootstrap resampling or Bayesian posterior intervals.",
            "Evaluation_Metrics": "Walk-forward RMSE, MAE, R^2, Feature Sparsity Count, Cumulative Mass Drift.",
            "Critical_Methodological_Reassessment": "PRIMARY RECOMMENDED REGULARIZED ARCHITECTURE: Automatically eliminates redundant atmospheric features while preserving grouped climate drivers."
        },
        {
            "Model_ID": "M4",
            "Model_Name": "Shallow Random Forest Regressor",
            "Intended_Task": "Task A2 (Non-Linear Interaction Exploration)",
            "Minimum_Data_Requirements": "Requires >= 50 samples to populate leaves. High risk of leaf starvation with N=81.",
            "Feature_Assumptions": "Non-parametric piecewise constant response surface; no linearity assumption.",
            "Complexity_Controls": "STRICT CONSTRAINT MANDATORY: max_depth <= 3, min_samples_leaf >= 6, max_features <= 0.6, n_estimators = 50.",
            "Uncertainty_Interpretation": "Variance across individual decision tree predictions: Var(y_hat) = (1/B) sum (T_b - y_hat)^2.",
            "Evaluation_Metrics": "Walk-forward RMSE, MAE, R^2, OOB Score.",
            "Critical_Methodological_Reassessment": "HIGH OVERFITTING RISK: Standard default RF will memorize 81 training samples. Cannot extrapolate beyond historical feature extremes (Task B limitation)."
        },
        {
            "Model_ID": "M5",
            "Model_Name": "Shallow Gradient Boosting (XGBoost / LightGBM)",
            "Intended_Task": "Task A2 (Exploratory Gradient Boosting)",
            "Minimum_Data_Requirements": "Generally requires N >= 500 for robust gradient estimation. N=81 is severely sample-starved.",
            "Feature_Assumptions": "Additive boosted decision stumps fitting pseudo-residuals.",
            "Complexity_Controls": "STRICT CONSTRAINTS MANDATORY: max_depth = 2, learning_rate = 0.02, n_estimators <= 40, reg_lambda >= 10.0, subsample = 0.8.",
            "Uncertainty_Interpretation": "Quantile regression loss (alpha = 0.05, 0.5, 0.95) or NGBoost.",
            "Evaluation_Metrics": "Walk-forward RMSE, MAE, Pinball Loss.",
            "Critical_Methodological_Reassessment": "DOUBTFUL SCIENTIFIC JUSTIFICATION: On N=81 samples, gradient boosting easily creates brittle step-functions. Complexity is not justified unless it decisively outperforms ElasticNet by >15% on validation folds."
        },
        {
            "Model_ID": "M6",
            "Model_Name": "Gaussian Process Regressor (GPR with Physics Kernel)",
            "Intended_Task": "Task A2 (Probabilistic Benchmark) & Task B (Uncertainty Quantified Projections)",
            "Minimum_Data_Requirements": "N in [30, 200] is the ideal mathematical operating window for exact GP inference (O(N^3) is trivial).",
            "Feature_Assumptions": "Smooth non-linear latent function f(x) with Matérn 3/2 or 5/2 spatial-temporal covariance.",
            "Complexity_Controls": "Marginal likelihood optimization over lengthscales; lengthscale bounds bounded in [0.5, 5.0]; noise variance alpha fixed to annual basin rate error.",
            "Uncertainty_Interpretation": "Exact analytical posterior predictive distribution: y_* ~ N(mu_*, sigma_*^2).",
            "Evaluation_Metrics": "Walk-forward RMSE, MAE, Negative Log Marginal Likelihood, Coverage Probability of 95% Interval.",
            "Critical_Methodological_Reassessment": "JUSTIFIED ONLY WITH LOW-DIMENSIONAL FEATURE SPACE (p <= 4): If p > 5, kernel lengthscales collapse. Must use PCA or core physical features (Precip, Runoff, Temp, Area)."
        }
    ]
    df = pd.DataFrame(data)
    out_path = os.path.join(TABLES_DIR, "revised_model_comparison.csv")
    df.to_csv(out_path, index=False)
    print(f"Saved: {out_path}")
    return df


# =========================================================================
# 6. Revised Feature Availability Matrix
# =========================================================================
def generate_revised_feature_availability_matrix():
    print("\n--- [6] Generating Revised Feature Availability Matrix Table ---")
    data = [
        {
            "Feature_Identifier": "RACMO_Precipitation_Anomaly_mm_yr",
            "Physical_Domain": "Atmospheric Forcing",
            "Experiment_A1_Accounting": "YES (Informational context)",
            "Experiment_A2_Prediction": "YES: Exogenous climate forcing available from regional climate model at year t",
            "Experiment_B_Future_2100": "YES: Available from CMIP6 / ISMIP6 regional climate model downscaling (SSP1-2.6, SSP2-4.5, SSP5-8.5)",
            "Operational_Lag_Structure": "Unlagged contemporaneous forcing (t) assuming seasonal weather forecasts or RCM reanalysis available",
            "Data_Provenance_Classification": "Independent of IMBIE (direct RCM simulation)",
            "Extrapolation_Guardrail": "Bounded thermodynamically by Clausius-Clapeyron atmospheric moisture capacity (~7%/K)"
        },
        {
            "Feature_Identifier": "RACMO_Surface_Runoff_Melt_mm_yr",
            "Physical_Domain": "Atmospheric Forcing",
            "Experiment_A1_Accounting": "YES (Informational context)",
            "Experiment_A2_Prediction": "YES: Exogenous surface ablation driver",
            "Experiment_B_Future_2100": "YES: Available from CMIP6 downscaling under high-emission warming scenarios",
            "Operational_Lag_Structure": "Unlagged contemporaneous forcing (t)",
            "Data_Provenance_Classification": "Independent of IMBIE (direct RCM simulation)",
            "Extrapolation_Guardrail": "Non-linear exponential hypsometric melt expansion above 0 deg C"
        },
        {
            "Feature_Identifier": "ERA5_Surface_Air_Temperature_Anomaly_2m_K",
            "Physical_Domain": "Thermodynamics",
            "Experiment_A1_Accounting": "YES (Informational context)",
            "Experiment_A2_Prediction": "YES: Core climate anomaly driver",
            "Experiment_B_Future_2100": "YES: Core scenario trajectory discriminator from CMIP6 ESM ensemble",
            "Operational_Lag_Structure": "Unlagged contemporaneous forcing (t)",
            "Data_Provenance_Classification": "Independent of IMBIE (ERA5 reanalysis / CMIP6 projections)",
            "Extrapolation_Guardrail": "Extreme warming (>+4 K) exceeds historical observational envelope; linear extrapolation invalid"
        },
        {
            "Feature_Identifier": "Target_Volume_Change_Lag1_km3_yr",
            "Physical_Domain": "Autoregressive State",
            "Experiment_A1_Accounting": "NO (Accounting identity uses unlagged flux)",
            "Experiment_A2_Prediction": "YES: Core autoregressive feature y[b, t-1] observed prior to prediction year t",
            "Experiment_B_Future_2100": "YES: Recursively predicted from previous projection step y_hat[b, t-1]",
            "Operational_Lag_Structure": "Strict lag-1 (t-1). Banned for 1979 initialization.",
            "Data_Provenance_Classification": "Reconstructed target history",
            "Extrapolation_Guardrail": "Recursive feedback must be bound by autoregressive coefficient |phi| < 1 to prevent runaway drift"
        },
        {
            "Feature_Identifier": "Glacier_Terminus_Retreat_Index_Lag1",
            "Physical_Domain": "Glacier Kinematics",
            "Experiment_A1_Accounting": "NO (Accounting uses flux gate discharge)",
            "Experiment_A2_Prediction": "YES: Cumulative terminus retreat catalog (Cook 2005, 2016) strictly lagged by 1 year",
            "Experiment_B_Future_2100": "YES: Simulated dynamically via ocean-thermal and meltwater calving parameterized functions",
            "Operational_Lag_Structure": "Strict lag-1 (t-1)",
            "Data_Provenance_Classification": "Independent of IMBIE (optical satellite coastline digitization)",
            "Extrapolation_Guardrail": "Retreat stops once grounding line reaches bedrock threshold or headwall"
        },
        {
            "Feature_Identifier": "Grounded_Basin_Ice_Thickness_Baseline_m",
            "Physical_Domain": "Static Topography",
            "Experiment_A1_Accounting": "YES (Flux gate thickness)",
            "Experiment_A2_Prediction": "YES: Static basin-level physical descriptor modulating climate sensitivity",
            "Experiment_B_Future_2100": "YES: Baseline anchor constant (evolves dynamically via cumulative mass loss)",
            "Operational_Lag_Structure": "Static invariant baseline scalar",
            "Data_Provenance_Classification": "Independent of IMBIE (Bedmap3 / BedMachine V4.1)",
            "Extrapolation_Guardrail": "Mass conservation floor: H(t) >= 0; cannot thin below bedrock"
        },
        {
            "Feature_Identifier": "Grounded_Basin_Area_km2",
            "Physical_Domain": "Static Geography",
            "Experiment_A1_Accounting": "YES (Spatial integration)",
            "Experiment_A2_Prediction": "YES: Static basin-level scale descriptor (108,946; 49,758; 57,359 km2)",
            "Experiment_B_Future_2100": "YES: Static spatial reference boundary",
            "Operational_Lag_Structure": "Static invariant boundary scalar",
            "Data_Provenance_Classification": "Independent of IMBIE (IMBIE drainage delineation)",
            "Extrapolation_Guardrail": "Fixed geographical drainage boundary"
        },
        {
            "Feature_Identifier": "Same_Year_Discharge_D_t_Gt_yr",
            "Physical_Domain": "Dynamic Mass Flux",
            "Experiment_A1_Accounting": "YES: Mandatory subtrahend in accounting identity y = (SMB - D)/0.917",
            "Experiment_A2_Prediction": "STRICTLY PROHIBITED: Same-year target constituent overlap causes fatal leakage",
            "Experiment_B_Future_2100": "STRICTLY PROHIBITED: Future gate discharge is unobserved",
            "Operational_Lag_Structure": "Prohibited in prediction tasks",
            "Data_Provenance_Classification": "Reconstruction target component",
            "Extrapolation_Guardrail": "Excluded from all predictive feature matrices"
        },
        {
            "Feature_Identifier": "Same_Year_SMB_Anomaly_Gt_yr",
            "Physical_Domain": "Surface Mass Flux",
            "Experiment_A1_Accounting": "YES: Mandatory addend in accounting identity",
            "Experiment_A2_Prediction": "STRICTLY PROHIBITED: Same-year target constituent overlap causes fatal leakage",
            "Experiment_B_Future_2100": "STRICTLY PROHIBITED: IMBIE historical anomaly terminates in 2023",
            "Operational_Lag_Structure": "Prohibited in prediction tasks",
            "Data_Provenance_Classification": "Derived from IMBIE (reconstruction target component)",
            "Extrapolation_Guardrail": "Excluded from all predictive feature matrices"
        }
    ]
    df = pd.DataFrame(data)
    out_path = os.path.join(TABLES_DIR, "revised_feature_availability_matrix.csv")
    df.to_csv(out_path, index=False)
    print(f"Saved: {out_path}")
    return df


# =========================================================================
# Main Execution Controller
# =========================================================================
def main():
    print("=" * 80)
    print("EXECUTING PHASE 4A.1: METHODOLOGICAL AUDIT AND FINAL ML DESIGN FREEZE")
    print("=" * 80)

    generate_embargo_justification_audit()
    generate_feature_target_overlap_audit()
    generate_uncertainty_assumption_audit()
    generate_rolling_origin_fold_manifest()
    generate_revised_model_comparison()
    generate_revised_feature_availability_matrix()

    print("\nPhase 4A.1 Design Tables Successfully Created.")

if __name__ == "__main__":
    main()

