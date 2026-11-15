# Phase 4A.1 Technical Report: Methodological Audit and Final ML Design Freeze

**Project:** Antarctic Peninsula Ice-Volume Prediction to 2100  
**Phase:** Phase 4A.1 — Methodological Audit and Final ML Design Freeze  
**Status:** Audit Completed — Methodology Formally Corrected & Locked  
**Date:** November 2026  

---

## Executive Summary & Scope Charter

This methodological audit rigorously scrutinizes the Phase 4A machine-learning design for modeling annual grounded ice-equivalent volume changes across the Antarctic Peninsula mainland basins (`Hp-I`, `I-Ipp`, and `Ipp-J`).

In strict compliance with project directives:
- **No machine-learning models have been trained.**
- **No hyperparameters have been evaluated against the held-out test set.**
- **No 2100 forecasts have been generated.**
- **Existing manifests and raw datasets have not been silently modified.**
- **All conceptual confusions (quarantines vs lag availability, physical accounting vs ML prediction, cumulative vs annual rate uncertainty) have been forensically resolved.**

### Final Audit Determination:
> ### **Decision: Approved with Corrections.**
> The machine-learning architecture is approved for Phase 4B implementation subject to six mandatory methodological corrections:
> 1. The 9 "embargo" records are recognized as **unnecessary data discards**; lagged features from 2006–2007 and 2015 must remain available, and a revised non-discarding split is established.
> 2. Physical accounting reproduction (**Experiment A1**) is decoupled from actual machine learning prediction (**Experiment A2**), with same-year target constituents ($\text{SMB}_t, D_t$) strictly banned from predictive feature matrices.
> 3. The cumulative $\pm 204.82\text{ km}^3$ uncertainty is **banned from annual model likelihoods** and replaced with the true partitioned annual rate noise floor ($\pm 5.0\text{ to }\pm 12.0\text{ km}^3/\text{yr}$ per basin).
> 4. Ordinary Ridge regression is clarified as deterministic; Bayesian Ridge is required for analytical predictive variance.
> 5. A 20-fold rolling-origin walk-forward cross-validation protocol is established with preprocessing fit strictly inside training folds.
> 6. Regional Domain A volume change is enforced strictly as $\hat{y}_{\text{Domain A}, t} \equiv \sum_{b} \hat{y}_{b, t}$, ensuring exact mass conservation by construction.

---

## 1. Audit of the Nine Embargo Records

Phase 4A identified 9 records in [`reports/tables/split_manifest_row_level.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/split_manifest_row_level.csv) as "embargo buffers" (6 records in 2006–2007; 3 records in 2015). We audited whether their exclusion is scientifically justified across five distinct criteria:

### Table 1: Embargo Justification & Methodological Audit

| Audit Dimension | 2006–2007 Quarantine (Embargo 1, 6 records) | 2015 Quarantine (Embargo 2, 3 records) | Scientific Verdict & Rule |
| :--- | :--- | :--- | :--- |
| **1. Target Leakage Prevention** | **NO LEAKAGE RISK:** Targets are discrete annual calendar integrals ($y_t = \int_{\text{Jan 1}}^{\text{Dec 31}} \frac{\text{Net MB}}{0.917} dt$). The 2006 and 2007 intervals strictly ended on 2007-12-31, prior to the start of the 2008 validation period. Zero temporal overlap between annual target labels. | **NO LEAKAGE RISK:** The 2015 annual volume change interval ended on 2015-12-31. The 2016 test period starts on 2016-01-01. Zero label overlap. | Target leakage only occurs if target labels overlap in time (e.g. multi-year forward rolling averages). Single-year discrete targets have zero label leakage. |
| **2. Autoregressive Lag Availability** | **LEGITIMATE LAG PREDICTORS:** At prediction time (2008-01-01), 2007 (lag-1) and 2006 (lag-2) observations were already in the past. Quarantining them breaks the ability of autoregressive models to predict 2008 without imputing synthetic gaps. | **LEGITIMATE LAG PREDICTOR:** The 2015 state is the essential lag-1 input for predicting the first test year (2016). Quarantining 2015 makes 1-year persistence prediction for 2016 impossible without referencing 2015. | **Crucial Glaciological Principle:** If 2006–2007 observations were already observed at prediction time (2008-01-01), using them as lag features to predict 2008 is standard, legitimate time-series forecasting. |
| **3. Temporal Dependence** | Decadal error persistence ($\tau = 5\text{ yrs}$) links adjacent annual errors. In forward walk-forward time-series forecasting, training strictly on $t \le t-1$ to predict $t$ handles serial correlation naturally. Quarantining 2 years forces an artificial 2-year forecast horizon. | Identical to 2006–2007. Standard walk-forward protocol does not require discarding single boundary years. | Discarding boundary years creates an artificial multi-year lead time rather than evaluating 1-year ahead forecasting. |
| **4. Regime-Shift Isolation** | 2006–2007 was a post-Larsen-B dynamic relaxation transition. While physically distinct, dynamic relaxation is a real physical process that models must learn, not an artifact to be discarded. | Sentinel-1A launched in April 2014; 2015 was the onset of dense SAR constellation velocity tracking. This is a sensor improvement, not target leakage. | Regime shifts and sensor improvements are physical realities, not valid reasons to discard 6.5% of a small dataset. |
| **5. Data Efficiency Consequence** | Discards 6 physical basin-year records from a dataset of only 138 rows (4.3% data loss). | Discards 3 physical basin-year records from an already tiny test boundary (2.2% data loss). | **6.5% of all physical historical observations are thrown away.** |
| **Audit Conclusion** | **SCIENTIFICALLY UNJUSTIFIED DISCARD** | **SCIENTIFICALLY UNJUSTIFIED DISCARD** | **Revised Split Recommended.** |

*Full audit matrix saved in [`reports/tables/embargo_justification_audit.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/embargo_justification_audit.csv).*

### Revised Split Recommendation (Without Overwriting Manifest):
- **Phase 4A Manifest Retained (Status Quo with Clarification):**  
  If the existing manifest [`split_manifest_row_level.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/split_manifest_row_level.csv) is maintained, the 9 embargo records are treated as quarantined from model training loss and validation scoring, **BUT their lagged values must remain available as input features** when predicting subsequent years.
- **Recommended Revised Split (Optimal Data Efficiency):**  
  - **Train:** 1979–2007 (29 years $\times$ 3 basins = **87 basin-years**)
  - **Validation:** 2008–2015 (8 years $\times$ 3 basins = **24 basin-years**)
  - **Test:** 2016–2024 (9 years $\times$ 3 basins = **27 basin-years**)
  - *Total Evaluated:* $87 + 24 + 27 = \mathbf{138\text{ basin-years}}$ (0 physical observations discarded).

---

## 2. Separation of Physical Accounting from ML Prediction

The target variable is defined as:
$$y_{b,t} = \frac{\text{SMB}_{b,t} - D_{b,t}}{0.917} \quad (\text{km}^3/\text{yr})$$

### 2.1 The Fatal Feature-Target Constituent Overlap
In Phase 4A Table 2, both `IMBIE_Partitioned_SMB_Anomaly_Gt_yr` and `Glacier_Dynamics_Relaxation_State_D_dyn` were listed as available features for Task A.  
Our audit reveals a **fatal target constituent overlap**:
> If unlagged same-year $\text{SMB}_{b,t}$ and same-year discharge $D_{b,t}$ (or $D_{\text{dyn}}$) are supplied simultaneously to a regression model, the model does not learn glacier dynamics. It simply solves the trivial algebraic subtraction:
> $$\hat{y} = 1.0905 \cdot \text{SMB}_t - 1.0905 \cdot D_t$$
> Fitting a linear model to this is not machine learning; it is **numerical accounting reproduction**.

### 2.2 Formal Separation: Experiment A1 vs Experiment A2

We establish two strictly separated experimental tracks:

### Table 2: Experimental Track Partitioning

| Parameter | Experiment A1: Physical Accounting Reproduction | Experiment A2: True Historical ML Prediction |
| :--- | :--- | :--- |
| **Scientific Purpose** | Numerical verification of mass budget continuity and Input-Output Method integration. | Genuine predictive machine learning: forecasting annual volume change from past state and exogenous climate. |
| **Model Nature** | Exact physical identity check: $\hat{y} \equiv \frac{\text{SMB} - D}{0.917}$. Not an ML experiment. | Statistical and machine learning models (Persistence, Ridge, ElasticNet, GPR). |
| **Permitted Features** | Same-year $\text{SMB}_{b,t}$, same-year gate discharge $D_{b,t}$. | **ONLY features available at prediction cutoff ($t-1$ or exogenous climate forecast $t$).** |
| **Prohibited Features** | None (used for physical verification). | **STRICTLY PROHIBITED:** Same-year observed discharge $D_{b,t}$, unlagged dynamic surge state, same-year IMBIE reconciled mass balance, unlagged target values. |
| **Prediction Cutoff** | December 31 of year $t$. | **December 31 of year $t-1$** (for 1-year ahead forecasting $t-1 \rightarrow t$). |
| **Lag Structure** | Unlagged contemporaneous mass flux. | Strictly lagged kinematics ($v_{b, t-1}$), lagged volume change ($y_{b, t-1}$), and exogenous climate forcing (RACMO precipitation/temperature at $t$). |
| **Expected $R^2$ / RMSE** | $R^2 \equiv 1.0000$, $\text{RMSE} \le 0.01\text{ km}^3/\text{yr}$ (machine precision). | Realistic empirical skill: $R^2 \approx 0.40\text{–}0.75$, $\text{RMSE} \approx 2.0\text{–}4.0\text{ km}^3/\text{yr}$. |

*Full feature-target overlap audit cataloged in [`reports/tables/feature_target_overlap_audit.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/feature_target_overlap_audit.csv) and [`reports/tables/revised_feature_availability_matrix.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/revised_feature_availability_matrix.csv).*

---

## 3. Forensic Audit of Uncertainty Claims

Phase 4A proposed using cumulative uncertainty, Gaussian Process predictive variance, Ridge uncertainty, and multi-output covariance. We audit the mathematical validity of each:

### Table 3: Uncertainty Mechanism Audit & Mathematical Guardrails

| Uncertainty Mechanism | Proposed Use in Phase 4A | True Mathematical Quantity | Validity for Annual Basin Likelihood | Required Mathematical Correction |
| :--- | :--- | :--- | :---: | :--- |
| **$\pm 204.82\text{ km}^3$ Reconstruction Uncertainty** | Proposed as observation noise floor $\sigma_n^2$ in ML models. | **Cumulative 46-year integrated volume variance on Domain A:** $\text{Var} = \sum_{i=1}^{46} \sigma_{\text{rate}, i}^2$. | **STRICTLY INVALID** | **BANNED FROM ANNUAL LIKELIHOODS:** Annual basin volume changes range from $-1$ to $-25\text{ km}^3/\text{yr}$. Using $\pm 204.82\text{ km}^3$ assumes noise is $10\text{–}40\times$ larger than the physical signal. Use **annual basin rate uncertainty** ($\pm 5.0\text{ to }\pm 12.0\text{ km}^3/\text{yr}$). |
| **Gaussian Process Predictive Variance** | Proposed as Bayesian predictive distribution. | Analytical posterior variance: $\sigma_*^2 = k(x_*, x_*) - k_*^T (K + \alpha I)^{-1} k_*$. | **VALID WITH CONDITIONS** | Set noise hyperparameter $\alpha = (\sigma_{\text{annual\_basin}})^2 \approx 25\text{–}100\text{ km}^6/\text{yr}^2$. Bound lengthscales in $[0.5, 5.0]$ to prevent lengthscale collapse on $N=81$. |
| **Ridge Regression "Uncertainty"** | Proposed as providing analytical predictive variance. | Ordinary Ridge is a **deterministic point estimator** with zero probabilistic likelihood or predictive intervals. | **INVALID FOR ORDINARY RIDGE** | Must explicitly implement **Bayesian Ridge Regression** (MacKay evidence framework), which provides analytical posterior variance: $\text{Var}(\hat{y}) = \lambda^{-1} + x^T \Sigma_{\text{post}} x$. |
| **Multi-Output Basin Covariance** | Claimed to estimate full $3 \times 3$ cross-basin error covariance. | Standard `MultiOutputRegressor` fits **independent single-target models** and completely ignores cross-target residual correlation. | **INVALID FOR STANDARD MULTI-OUTPUT** | Do not claim standard multi-output exploits covariance. To capture cross-basin error dependence, implement **Seemingly Unrelated Regression (SUR)** or compute the empirical validation residual covariance $\Sigma_e = \frac{1}{N} \sum e_t e_t^T$. |

*Full audit matrix documented in [`reports/tables/uncertainty_assumption_audit.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/uncertainty_assumption_audit.csv).*

---

## 4. Finalized Pooled Basin Modeling Specification

To address the limited sample size without committing pseudo-replication:

### 4.1 Structural Formulation
The pooled regression model is defined as:
$$\hat{y}[b, t] = \beta_0 + \sum_{k=1}^K \beta_k X_{k, \text{climate}}[b, t] + \sum_{m=1}^M \gamma_m Z_{m, \text{static}}[b] + \sum_{j \in \{\text{I-Ipp, Ipp-J}\}} \delta_j \mathbb{I}(b = j) + \epsilon[b, t]$$

1. **Basin Identity Encoding:** Encoded via static physical descriptors plus one-hot indicator intercepts (with `Hp-I` as reference).
2. **Static Basin Descriptors & Provenance:**
   - Grounded Area ($A_b$): $108,946\text{ km}^2$ (`Hp-I`), $49,758\text{ km}^2$ (`I-Ipp`), $57,359\text{ km}^2$ (`Ipp-J`). Source: IMBIE mainland delineation.
   - Mean Ice Thickness ($H_b$): $918\text{ m}$ (`Hp-I`), $222\text{ m}$ (`I-Ipp`), $389\text{ m}$ (`Ipp-J`). Source: Bedmap3 / BedMachine.
   - Bed Elevation at Gates ($B_b$): Deep marine troughs in `Hp-I` ($-450\text{ m}$) vs shallow alpine sills in `I-Ipp` ($-120\text{ m}$).
3. **Shared Climate Predictors:** Peninsula-wide climate indices (SAM index, regional 2m temperature anomaly, total snowfall anomaly).
4. **Interaction Terms Justification:**
   - **Permitted Interactions:** $\text{Climate} \times \text{Basin Area}$ or $\text{Climate} \times \text{Basin ID}$ for core precipitation/runoff terms. This allows western Graham Land tidewater glaciers to have different melt sensitivities than eastern Larsen glaciers.
   - **Prohibited Interactions:** Full interaction of all features with basin identity is **strictly barred** because it is mathematically identical to separate basin models, dividing degrees of freedom back down to $N=27$.
5. **Cross-Basin Dependence Handling:**
   - **Crucial Rule:** The 81 training rows must **NEVER be treated as 81 independent observations**. Three basins in the same year share regional atmospheric shocks.
   - Model standard errors must be computed using **Clustered Standard Errors (clustered by year $t$)** or Generalized Estimating Equations (GEE).
6. **Mandatory Basin-Aware Baseline:**
   - Model M0 must include a **Basin-Specific Persistence Baseline**: $\hat{y}[b, t] = y[b, t-1]$, benchmarked against the basin historical mean $\bar{y}_b$.

---

## 5. Chronological Validation Protocol & Exact Fold Manifest

To guarantee zero leakage and provide rigorous walk-forward evaluation, an exact 20-fold rolling-origin cross-validation manifest has been compiled in [`reports/tables/rolling_origin_fold_manifest.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/rolling_origin_fold_manifest.csv).

### 5.1 Protocol Architecture
- **Minimum Training Window:** 16 years (1979–1994; **48 basin-year instances**).  
  *Justification:* Covers the pre-collapse equilibrium through the Wordie collapse (1989), providing the minimum degrees of freedom to fit regularized linear models ($p \le 4$).
- **Progressive Walk-Forward Expansion:** From 1995 to 2014 (**20 contiguous validation folds**).
- **Cluster Integrity:** In every fold, **all three basins (`Hp-I`, `I-Ipp`, `Ipp-J`) for validation year $t$ are kept in the same fold** ($N_{\text{val}} = 3$).
- **Strict Pipeline Containment:** Feature scalers (StandardScaler), imputers, and ElasticNet feature selectors are fit **strictly inside each training fold**. No transform fitted on future years is ever applied backward.
- **First Persistence Prediction Initialization:** In 1979 ($t=1$), $t-1 = 1978$ is unobserved. The persistence baseline begins at year 1980 using $y_{1979}$.
- **Blind Test Period:** The 2016–2024 test period remains strictly untouched.

---

## 6. Revised Candidate Model Architecture Comparison

Documented in [`reports/tables/revised_model_comparison.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/revised_model_comparison.csv):

### Table 4: Revised Model Status & Evaluation Summary

| Model ID | Model Name | Role in Project | Complexity Control | Likelihood & Uncertainty | Operational Recommendation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **M0** | **Basin Persistence** | Minimal Performance Floor | Zero learnable parameters | Empirical residual $\sigma \approx \pm 3.5\text{ km}^3/\text{yr}$ | **Mandatory Baseline:** Must beat M0 RMSE to justify any ML model. |
| **M1** | **OLS Linear** | Climate Benchmark | Closed-form; no penalty | Classical parameter variance | **Reference Only:** Vulnerable to climate collinearity. |
| **M2** | **Bayesian Ridge** | **Primary Linear Model** | L2 penalty $\alpha$ via evidence procedure | Analytical posterior predictive variance | **PRIMARY CANDIDATE:** Stable on $N=81$; robust linear 2100 extrapolation. |
| **M3** | **ElasticNet** | **Primary Regularized Model** | L1/L2 penalties ($\alpha, \ell_1$) via walk-forward CV | Residual bootstrap intervals | **PRIMARY CANDIDATE:** Performs automated physical feature selection. |
| **M4** | **Shallow RF** | Non-Linear Exploration | `max_depth` $\le 3$, `min_leaf` $\ge 6$ | Ensemble tree variance | **EXPLORATORY:** High risk of memorizing $N=81$; cannot extrapolate extremes. |
| **M5** | **Shallow XGBoost** | Gradient Boosting | `depth` $= 2$, $\eta = 0.02$, $\lambda \ge 10$ | Quantile loss pinball intervals | **DOUBTFUL JUSTIFICATION:** Sample size ($N=81$) is severely starved for boosting. Rejected unless it outperforms ElasticNet by $>15\%$. |
| **M6** | **GPR (Physics Kernel)** | **Primary Probabilistic Model** | Marginal likelihood; Matérn 3/2 | Exact analytical Gaussian distribution | **PRIMARY CANDIDATE (Low-p only):** Excellent for $N=81$ if $p \le 4$; noise fixed to annual rate $\sigma$. |

---

## 7. Exact Regional Mass Conservation by Construction

In response to Section 7:
> **Domain A prediction is defined strictly as a derived sum:**
> $$\hat{y}_{\text{Domain A}, t} \equiv \sum_{b \in \{\text{Hp-I, I-Ipp, Ipp-J}\}} \hat{y}_{b, t}$$
> **Operational Directives:**
> 1. Domain A is **NEVER trained as a fourth independent basin**.
> 2. We do **NOT rely on an approximate penalty term in the loss function**. Exact spatial mass conservation ($\sum_b \hat{y}_b - \hat{y}_{\text{Domain A}} \equiv 0$) is guaranteed by construction.

---

## 8. Final Design Freeze Decision Table

### Table 5: Methodological Audit Decision Table

| Architecture Component | Status | Audited Finding | Required Correction in Phase 4B |
| :--- | :---: | :--- | :--- |
| **1. Target Dataset Integrity** | **Approved without changes** | 138 physical basin-years + 46 Domain A diagnostic rows strictly verified. | Use master target dataset as compiled in Phase 3.4. |
| **2. Embargo Records Allocation** | **Approved with corrections** | 9 embargo records were unnecessarily discarded from training/validation. | Maintain lagged feature availability for subsequent years; adopt revised non-discarding split for model training. |
| **3. Experiment A1 vs A2 Separation** | **Approved with corrections** | Target constituent overlap ($\text{SMB}_t, D_t$) allowed algebraic target recovery. | Separate physical accounting (A1) from true predictive ML (A2); ban same-year $\text{SMB}_t$ and $D_t$ from A2. |
| **4. Uncertainty Specification** | **Approved with corrections** | Cumulative $\pm 204.82\text{ km}^3$ was inappropriately plugged into annual likelihoods. | Replace with annual basin rate uncertainty ($\pm 5\text{ to }\pm 12\text{ km}^3/\text{yr}$). Require Bayesian Ridge for linear uncertainty. |
| **5. Pooled Basin Modeling** | **Approved with corrections** | 81 training rows cannot be treated as 81 independent samples. | Incorporate static basin descriptors and clustered standard errors (clustered by year $t$). |
| **6. Chronological Validation** | **Approved with corrections** | Standard k-fold prohibited; walk-forward protocol lacked explicit fold manifest. | Adopt 20-fold rolling-origin walk-forward manifest with fold-contained preprocessing. |
| **7. Candidate Models (M0–M6)** | **Approved with corrections** | XGBoost unjustified on $N=81$; GPR restricted to low-dimensional feature space ($p \le 4$). | Prioritize M0, M2 (Bayesian Ridge), M3 (ElasticNet), and M6 (low-dim GPR). Demote M5 (XGBoost) to exploratory. |
| **8. Regional Mass Conservation** | **Approved without changes** | Exact conservation by construction: $\hat{y}_{\text{Domain A}} \equiv \sum_b \hat{y}_b$. | Enforce exact summation identity; no loss penalty required. |

---

*In strict accordance with Phase 4A.1 stopping conditions, execution stops here. The methodological audit and design freeze are submitted for your review and approval before beginning Phase 4B model training.*
