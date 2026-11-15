# Phase 4C.1 — Independent Held-Out Test Results Forensic Audit

**Document Status:** Authoritative Independent Scientific Audit Report  
**Phase:** 4C.1 (Held-Out Test Results Forensic Verification)  
**Evaluated Epoch:** 2016–2024 Held-Out Test Period ($N = 27$ Physical Basin-Years, $N = 9$ Domain A Regional Diagnostic Records)  
**Lead Auditor:** Independent Verification Agent (Pair Programming with Scientific Directorate)  
**Evaluation Date:** November 2026  
**Final Determination:** **DECISION B — CONDITIONAL PASS** (Results numerically verified, protocol compliant, baseline superiority confirmed, documented scientific limitations accepted)

---

## Executive Summary & Audit Determination

This independent scientific audit performs a strict, read-only forensic examination of the completed **Phase 4C Held-Out Test Evaluation** for the Antarctic Peninsula Grounded-Ice Volume Change Prediction system. The historical target dataset encompasses three mainland drainage basins: **Hp-I** (Palmer Land West), **I-Ipp** (Graham Land West), and **Ipp-J** (Graham Land East / Larsen Coast), spanning 1979–2024 (138 physical basin-year observations and 46 derived Domain A regional diagnostic records).

The audit operated under strict scope boundaries:
1. **Zero Retraining or Re-tuning:** No models were retrained, no hyperparameters were altered, and no feature sets were modified.
2. **Zero Post-Hoc Prediction Generation:** No new test predictions were generated; all audits evaluated the exact, unsealed 288-row test prediction artifact (`reports/tables/test_predictions.csv`).
3. **Zero 2100 Projections:** No extrapolative forward simulations beyond 2024 were executed.
4. **Complete Numerical Verification:** All 8 evaluated model configurations and 288 test prediction records were independently recomputed and compared against the Phase 4B.2 frozen protocol manifest, Phase 4C execution logs, and published leaderboards.

```
========================================================================================================
FINAL AUDIT DETERMINATION: DECISION B (CONDITIONAL PASS)
========================================================================================================
1. Numerical Correctness:       PASS (100% exact reproduction across all metrics to < 1e-14 precision)
2. Protocol Compliance:         PASS (All 8 evaluated models pre-registered in Phase 4B.2 Manifest)
3. Scientific Honesty:          PASS (Phase 4C explicitly and honestly reported Historical Mean superiority)
4. Baseline Construction:       PASS (M0_Historical_Mean strictly uses 1979–2014 pre-test data; zero leakage)
5. Physical Attribution:        CONDITIONAL PASS (Missing buttressing variables identified as plausible 
                                 mechanism; correlation vs causation explicitly demarcated)
6. Uncertainty Calibration:     CONDITIONAL PASS (Bayesian Ridge homoscedasticity and GPR latent-only 
                                 noise documented; small-sample N=9 limitations formally accepted)
========================================================================================================
```

### High-Level Summary of the Eight Investigations

| Investigation | Core Subject | Primary Finding | Compliance / Audit Verdict |
| :--- | :--- | :--- | :--- |
| **Investigation 1** | **Frozen Protocol Compliance** | Evaluated 8 models (`M2_Bayesian_Ridge_Weighted`, `M2_Bayesian_Ridge`, `M0_Persistence`, `M0_Historical_Mean`, `M3_ElasticNet`, `M4_Random_Forest`, `M5_Gradient_Boosting`, `M6_Gaussian_Process`). All 8 were explicitly authorized in Rows 1–3 of the Phase 4B.2 Protocol Manifest. | **STRICTLY COMPLIANT** (Pre-registered comparison; zero post-unsealing additions) |
| **Investigation 2** | **Metric Recalculation** | Recomputed pooled RMSE, MAE, Mean Bias, $R^2$, basin-specific metrics, Domain A rate RMSE, endpoint cumulative drift, and max path drift across 288 rows. Exact match to machine precision ($< 10^{-14}$). | **VERIFIED NUMERICAL PRECISION** (Sign convention: positive bias = under-prediction of loss) |
| **Investigation 3** | **Historical Mean Construction** | `M0_Historical_Mean` strictly derived from 1979–2014 pre-test records ($N=36$ years/basin). $Hp-I: -5.23$, $I-Ipp: -5.42$, $Ipp-J: -9.28\text{ km}^3/\text{yr}$ (Sum: $-19.92\text{ km}^3/\text{yr}$). Zero test leakage. | **VERIFIED CLEAN BASELINE** (No future data, no test normalization) |
| **Investigation 4** | **Statistical Significance** | Reproduced paired $t$-tests and Wilcoxon signed-rank tests across $N=9$ annual 3-basin clusters. `M0_Historical_Mean` is statistically significantly superior to unweighted Bayesian Ridge ($p = 0.0077$) and GPR ($p = 0.0077$). | **STATISTICALLY VERIFIED** (Documented low power of $N=9$ clusters; $df=8$) |
| **Investigation 5** | **Regional Error Decomposition** | Historical Mean Domain A endpoint drift ($+3.98\text{ km}^3$) decomposes exactly: $Hp-I$ ($-44.37$) $+ I-Ipp$ ($-4.79$) $+ Ipp-J$ ($+53.14\text{ km}^3$). "97.8% mass loss capture" is an artifact of compensating spatial errors. | **VERIFIED CANCELLATION** (Spatial errors mask regional aggregate accuracy) |
| **Investigation 6** | **Persistence Telescoping Audit** | Proved algebraic identity: $\sum_{t=2016}^{2024} e_t \equiv y_{2015} - y_{2024} = -40.81 - (-33.59) = -7.22\text{ km}^3$. Persistence has disastrous annual RMSE ($59.62\text{ km}^3/\text{yr}$) and path drift ($87.14\text{ km}^3$). | **VERIFIED IDENTITY** (Endpoint cancellation does not imply dynamic predictive skill) |
| **Investigation 7** | **Prediction Interval Audit** | Bayesian Ridge exhibits homoscedastic predictive variance ($\sigma \approx 12.31\text{ to }14.31\text{ km}^3/\text{yr}$ across all basins). Gaussian Process under-covers (0%–33%) due to modeling only latent function variance without observation noise. | **VERIFIED CALIBRATION LIMITATION** (Documented discrete granularity $\Delta = 11.1\%$ for $N=9$) |
| **Investigation 8** | **Physical Interpretation** | Larsen B post-2002 collapse explains persistent $Ipp-J$ under-prediction ($+52$ to $+77\text{ km}^3$ drift). Palmer Land accumulation surge explains $Hp-I$ over-prediction. Key dynamic variables absent. | **VERIFIED PHYSICAL ATTRIBUTION** (Identified 7 missing dynamic state variables) |

---

## Investigation 1 — Frozen Protocol Compliance Audit

### Pre-Registration vs. Execution Reconciliation

A primary question for Phase 4C.1 is whether the eight models reported in the Phase 4C leaderboard represent a pre-registered scientific protocol or an unapproved, post-hoc exploratory fishing exercise following unsealing of the test data.

We performed a line-by-line audit comparing the pre-test frozen protocol manifest ([`phase4c_protocol_manifest.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/phase4c_protocol_manifest.csv)) against the test evaluation pipeline ([`test_evaluator.py`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/src/pipelines/test_evaluator.py)) and execution outputs.

```
+--------------------------------------------------------------------------------------------------------+
| PROTOCOL PRE-REGISTRATION AUDIT: phase4c_protocol_manifest.csv                                         |
+--------------------------------------------------------------------------------------------------------+
| Row 1: Candidate Model Portfolio Selection                                                             |
|   "Primary Candidate: M2_Bayesian_Ridge_Weighted; Secondary Candidates: M2_Bayesian_Ridge (Unweighted),|
|    M3_ElasticNet, M4_Random_Forest, M5_Gradient_Boosting, M6_Gaussian_Process."                       |
|                                                                                                        |
| Row 2: Required Benchmarks Designation                                                                 |
|   "M0_Persistence (Lag-1 baseline), M0_Historical_Mean (Pre-test climatological mean)."               |
|                                                                                                        |
| Row 3: Test Window & Evaluation Protocol                                                               |
|   "Test Window: 2016–2024 (9 years, 27 physical basin-years, 9 Domain A diagnostics).                 |
|    All 8 models evaluated simultaneously across the identical 9-year window."                          |
+--------------------------------------------------------------------------------------------------------+
```

### Forensic Reconciliation Findings

1. **Authorization Status:** All eight evaluated models were explicitly pre-registered in Rows 1 and 2 of [`phase4c_protocol_manifest.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/phase4c_protocol_manifest.csv), compiled during Phase 4B.2 prior to unsealing the 2016–2024 test partition.
2. **Post-Unsealing Modifications:** Execution timestamps confirm that [`test_evaluator.py`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/src/pipelines/test_evaluator.py) executed a single-pass run evaluating all 8 pre-registered configurations in a single automated loop. No models were added, removed, re-weighted, or hyperparameter-tuned after unsealing test data.
3. **Exploratory vs Pre-Registered Classification:** The evaluation constitutes a **fully pre-registered evaluation**. The reporting of the secondary models (`M6_Gaussian_Process`, `M3_ElasticNet`, `M5_Gradient_Boosting`, `M4_Random_Forest`) alongside the primary candidate (`M2_Bayesian_Ridge_Weighted`) and mandatory benchmarks is directly compliant with the pre-registered portfolio.

The complete compliance verification table is saved in [`reports/tables/frozen_protocol_compliance.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/frozen_protocol_compliance.csv) and reproduced below:

| Model Name | Pre-Registered Role | Listed in Phase 4B.2 Manifest | Pre-Test Pipeline Frozen | Test Evaluation Timing | Post-Unsealing Modifications | Protocol Compliance Status |
| :--- | :--- | :---: | :---: | :--- | :--- | :--- |
| **M2_Bayesian_Ridge_Weighted** | Primary Candidate Model | True | True | Single-pass execution in `test_evaluator.py` | None (Zero hyperparameter/feature modification) | **STRICTLY COMPLIANT** |
| **M0_Persistence** | Mandatory Dynamic Benchmark | True | True | Single-pass execution in `test_evaluator.py` | None (Fixed algebraic lag-1 predictor) | **STRICTLY COMPLIANT** |
| **M0_Historical_Mean** | Mandatory Climatological Benchmark | True | True | Single-pass execution in `test_evaluator.py` | None (Fixed pre-test historical training mean) | **STRICTLY COMPLIANT** |
| **M2_Bayesian_Ridge** | Mandatory Reference Benchmark | True | True | Single-pass execution in `test_evaluator.py` | None (Unweighted Bayesian Ridge formulation) | **STRICTLY COMPLIANT** |
| **M3_ElasticNet** | Secondary Candidate Model | True | True | Single-pass execution in `test_evaluator.py` | None (Identical pipeline to Phase 4B) | **STRICTLY COMPLIANT** |
| **M4_Random_Forest** | Secondary Candidate Model | True | True | Single-pass execution in `test_evaluator.py` | None (Identical shallow RF configuration) | **STRICTLY COMPLIANT** |
| **M5_Gradient_Boosting** | Secondary Candidate Model | True | True | Single-pass execution in `test_evaluator.py` | None (Identical constrained GBDT configuration) | **STRICTLY COMPLIANT** |
| **M6_Gaussian_Process** | Secondary Candidate Model | True | True | Single-pass execution in `test_evaluator.py` | None (Identical low-dim GPR configuration) | **STRICTLY COMPLIANT** |

---

## Investigation 2 — Independent Metric Recalculation & Leaderboard Verification

### Mathematical Formulation & Sign Convention

We independently recomputed every summary metric from the raw 288-row test prediction table ([`test_predictions.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/test_predictions.csv)).

Let $y_{t,b}$ denote the reconstructed historical volume rate of change ($\text{km}^3/\text{year}$) for year $t \in \{2016, \dots, 2024\}$ and basin $b \in \{Hp-I, I-Ipp, Ipp-J\}$. Let $\hat{y}_{t,b}$ denote the model prediction.

1. **Residual Sign Convention:**
   $$e_{t,b} = \hat{y}_{t,b} - y_{t,b}$$
   *Glaciological Meaning:* In glaciological mass balance, net loss of ice is represented by negative volume rates ($y < 0$, e.g., $-20\text{ km}^3/\text{yr}$). If a model predicts $\hat{y} = -10\text{ km}^3/\text{yr}$, the residual is:
   $$e = -10 - (-20) = +10\text{ km}^3/\text{year}$$
   **A positive residual/bias represents under-prediction of ice loss (over-prediction of ice retention).** Conversely, a negative residual/bias represents over-prediction of ice loss.
2. **Mean Squared Error (MSE) & Root Mean Squared Error (RMSE):**
   $$\text{MSE} = \frac{1}{N} \sum_{i=1}^N (\hat{y}_i - y_i)^2, \quad \text{RMSE} = \sqrt{\text{MSE}}$$
3. **Mean Absolute Error (MAE):**
   $$\text{MAE} = \frac{1}{N} \sum_{i=1}^N |\hat{y}_i - y_i|$$
4. **Mean Bias Error:**
   $$\text{Bias} = \frac{1}{N} \sum_{i=1}^N (\hat{y}_i - y_i)$$
5. **Coefficient of Determination ($R^2$):**
   $$R^2 = 1 - \frac{\sum_{i=1}^N (\hat{y}_i - y_i)^2}{\sum_{i=1}^N (y_i - \bar{y}_{\text{test}})^2}$$
   where $\bar{y}_{\text{test}} = \frac{1}{N} \sum_{i=1}^N y_i$ is the empirical mean of the held-out test observations.
6. **Cumulative Path & Endpoint Drift:**
   $$\Delta V_{\text{drift}}(t) = \sum_{\tau=2016}^t (\hat{y}_{\tau} - y_{\tau}), \quad \text{Endpoint Drift} = \Delta V_{\text{drift}}(2024), \quad \text{Max Path Drift} = \max_{t \in [2016, 2024]} |\Delta V_{\text{drift}}(t)|$$

### Master Leaderboard Verification Table

All recalculated metrics match the published Phase 4C leaderboard to machine precision (maximum discrepancy $< 10^{-14}$). The recomputed master table is archived in [`reports/tables/test_metric_recalculation.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/test_metric_recalculation.csv):

| Model Name | Phys. $N$ | Recalc. RMSE ($\text{km}^3/\text{yr}$) | Recalc. MAE ($\text{km}^3/\text{yr}$) | Recalc. Bias ($\text{km}^3/\text{yr}$) | Recalc. $R^2$ | Domain A Rate RMSE | Domain A Endpoint Drift ($\text{km}^3$) | Domain A Max Path Drift ($\text{km}^3$) | Rank |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **M0_Historical_Mean** | 27 | **14.690** | **10.894** | **+0.147** | **+0.0806** | 38.943 | **+3.982** | 66.252 | **1** |
| **M6_Gaussian_Process** | 27 | 15.318 | 11.387 | +0.146 | +0.0004 | 38.941 | +3.938 | 66.253 | 2 |
| **M2_Bayesian_Ridge** | 27 | 15.321 | 11.389 | +0.148 | -0.0001 | 38.947 | +3.988 | 66.258 | 3 |
| **M2_Bayesian_Ridge_Weighted** | 27 | 15.355 | 11.254 | -1.035 | -0.0046 | 39.064 | -27.957 | 81.996 | 4 |
| **M3_ElasticNet** | 27 | 15.588 | 11.420 | +0.150 | -0.0353 | 40.277 | +4.061 | 68.016 | 5 |
| **M5_Gradient_Boosting** | 27 | 15.664 | 12.282 | -0.294 | -0.0453 | 41.447 | -7.932 | 79.083 | 6 |
| **M4_Random_Forest** | 27 | 16.414 | 12.744 | -0.255 | -0.1479 | 43.499 | -6.872 | 78.488 | 7 |
| **M0_Persistence** | 27 | 21.452 | 18.379 | -0.267 | -0.9608 | 59.623 | -7.220 | 87.140 | 8 |

### Basin-Specific Recalculation Breakdown

| Model Name | $Hp-I$ RMSE | $Hp-I$ MAE | $Hp-I$ Bias | $I-Ipp$ RMSE | $I-Ipp$ MAE | $I-Ipp$ Bias | $Ipp-J$ RMSE | $Ipp-J$ MAE | $Ipp-J$ Bias |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **M0_Historical_Mean** | **20.611** | **14.971** | -4.929 | **11.508** | 8.839 | **-0.533** | **9.493** | **8.872** | **+5.904** |
| **M6_Gaussian_Process** | 20.989 | 15.125 | -6.337 | 11.630 | 8.702 | -1.759 | 11.317 | 10.334 | +8.533 |
| **M2_Bayesian_Ridge** | 20.994 | 15.128 | -6.339 | 11.630 | 8.703 | -1.755 | 11.320 | 10.336 | +8.537 |
| **M2_Bayesian_Ridge_Weighted** | 21.381 | 15.467 | -7.527 | 11.866 | **8.615** | -2.938 | 10.460 | 9.680 | +7.358 |
| **M3_ElasticNet** | 21.516 | 15.243 | -5.865 | 11.999 | 8.802 | -1.621 | 11.048 | 10.215 | +7.937 |
| **M5_Gradient_Boosting** | 21.371 | 17.072 | -3.933 | 13.048 | 9.915 | -2.717 | 10.443 | 9.859 | +5.768 |
| **M4_Random_Forest** | 22.193 | 17.040 | **-3.608** | 13.277 | 10.416 | -3.401 | 11.810 | 10.775 | +6.245 |
| **M0_Persistence** | 30.707 | 28.402 | -0.467 | 17.590 | 16.264 | -0.227 | 11.326 | 10.469 | -0.109 |

---

## Investigation 3 — Historical Mean and Benchmark Construction Forensic Audit

### Training Partition & Calculation Integrity

We conducted a forensic examination into the origin and calculation of the `M0_Historical_Mean` baseline.

1. **Temporal Definition:** The historical mean was computed strictly over the pre-test training window **1979–2014** ($N = 36$ physical years per basin, 108 total basin-years).
2. **Quarantine Compliance:** The 2015 embargo buffer ($N = 3$ physical basin-years) and the 2016–2024 held-out test set ($N = 27$ physical basin-years) were completely excluded from the mean.
3. **Basin-Specific Formulation:** The model assigns a constant basin-specific mean $\bar{y}_b$ to each basin for all test years $t \in \{2016, \dots, 2024\}$:
   $$\bar{y}_{Hp-I} = \frac{1}{36} \sum_{t=1979}^{2014} y_{t,Hp-I} = -5.226111\text{ km}^3/\text{year}$$
   $$\bar{y}_{I-Ipp} = \frac{1}{36} \sum_{t=1979}^{2014} y_{t,I-Ipp} = -5.418056\text{ km}^3/\text{year}$$
   $$\bar{y}_{Ipp-J} = \frac{1}{36} \sum_{t=1979}^{2014} y_{t,Ipp-J} = -9.277778\text{ km}^3/\text{year}$$
   $$\bar{y}_{\text{Domain A}} = \sum_{b} \bar{y}_b = -19.921944\text{ km}^3/\text{year}$$
4. **Target Leakage Check:** An exact numerical diff between `test_predictions.csv` and the pre-test training partition in [`ml_target_dataset.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/ml_target_dataset.csv) confirmed that:
   $$\max_{t \in [2016, 2024]} |\hat{y}_{t,b}(\text{Historical Mean}) - \bar{y}_b(\text{1979–2014})| \equiv 0.0$$
   There was zero post-2014 information leakage, zero test-set standardization leakage, and zero feature contamination.
5. **Reconciliation of Historical Numbers:** During earlier exploratory discussions, alternative epoch means (e.g. 1995–2014 or full 1979–2024 means of $-15.81\text{ km}^3/\text{yr}$ for $Hp-I$ and $-38.14\text{ km}^3/\text{yr}$ for Domain A) were discussed. The audit confirms that the Phase 4C pipeline strictly adhered to the scientifically defensible pre-registered decision: **only the pre-test training partition (1979–2014) was used to construct the historical mean.**

---

## Investigation 4 — Statistical Significance and Cluster-Level Hypothesis Testing

### Cluster-Level Formulation ($N = 9$ Annual Clusters)

Because the test dataset consists of 3 spatial basins observed across 9 calendar years, treating the 27 physical observations as independent and identically distributed ($i.i.d.$) violates temporal exchangeability. In accordance with the pre-registered protocol, hypothesis testing was conducted on **annual cluster-level Mean Squared Errors**.

For calendar year $t \in \{2016, \dots, 2024\}$, the cluster loss for model $M$ is defined as:
$$L_t(M) = \frac{1}{3} \sum_{b \in \{Hp-I, I-Ipp, Ipp-J\}} (\hat{y}_{t,b}(M) - y_{t,b})^2$$
The paired difference relative to the reference baseline `M0_Historical_Mean` is:
$$D_t = L_t(\text{Historical Mean}) - L_t(M)$$
Under $H_0: \mathbb{E}[D_t] = 0$. A negative mean difference ($\bar{D} < 0$) indicates that `M0_Historical_Mean` achieved lower MSE (superior performance) than model $M$.

### Parametric & Non-Parametric Test Reproduction

We independently reproduced the paired $t$-test (8 degrees of freedom) and the exact Wilcoxon signed-rank test across all 7 model pairs. The full results are archived in [`reports/tables/significance_test_reproduction.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/significance_test_reproduction.csv):

| Candidate Model $M$ | Reference Baseline | Mean Cluster MSE Diff ($\text{km}^6/\text{yr}^2$) | Standard Error ($SE$) | 95% Confidence Interval | Effect Size (Cohen's $d$) | Paired $t$-stat ($df=8$) | $p$-value ($t$-test) | Wilcoxon $W$ | $p$-value (Wilcoxon) | Significant ($\alpha=0.05$) | Bonferroni ($\alpha=0.00714$) | Superior Model |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **M0_Persistence** | Historical Mean | -244.42 | 98.94 | [-472.58, -16.27] | -0.823 | -2.470 | **0.0387** | 0.0 | **0.0039** | Yes | Yes (Wilcoxon) | **Historical Mean** |
| **M2_Bayesian_Ridge** | Historical Mean | -18.94 | 5.36 | [-31.31, -6.57] | -1.177 | -3.530 | **0.0077** | 0.0 | **0.0039** | Yes | Yes (Wilcoxon) | **Historical Mean** |
| **M6_Gaussian_Process** | Historical Mean | -18.84 | 5.33 | [-31.14, -6.54] | -1.177 | -3.532 | **0.0077** | 0.0 | **0.0039** | Yes | Yes (Wilcoxon) | **Historical Mean** |
| **M3_ElasticNet** | Historical Mean | -27.21 | 11.72 | [-54.24, -0.18] | -0.774 | -2.322 | **0.0488** | 5.0 | **0.0391** | Yes | No | **Historical Mean** |
| **M4_Random_Forest** | Historical Mean | -53.64 | 24.77 | [-110.76, +3.47] | -0.722 | -2.166 | 0.0622 | 6.0 | 0.0547 | No | No | Historical Mean (trend) |
| **M5_Gradient_Boosting** | Historical Mean | -29.57 | 23.86 | [-84.59, +25.46] | -0.413 | -1.239 | 0.2505 | 11.0 | 0.2031 | No | No | Indeterminate ($p>0.2$) |
| **M2_BR_Weighted** | Historical Mean | -20.00 | 16.22 | [-57.41, +17.41] | -0.411 | -1.233 | 0.2527 | 15.0 | 0.4258 | No | No | Indeterminate ($p>0.2$) |

### Methodological & Statistical Power Limitations

1. **Low Statistical Power:** With only $N = 9$ temporal clusters ($df = 8$), the minimum detectable effect size at $\beta = 0.20$ is large ($d > 0.95$). While `M0_Historical_Mean` achieves statistical superiority over `M2_Bayesian_Ridge` and `M6_Gaussian_Process` ($p = 0.0077$, Cohen's $d = -1.18$), its failure to reach raw $p < 0.05$ against `M2_Bayesian_Ridge_Weighted` ($p = 0.2527$) is driven by high interannual variance in cluster differences ($\sigma = 48.67\text{ km}^6/\text{yr}^2$), not by model equivalence.
2. **Multiple Comparison Corrections:** Applying a Bonferroni correction for the 7 family-wise comparisons requires an adjusted significance threshold of $\alpha_{\text{Bonf}} = 0.05 / 7 = 0.00714$. Under the parametric paired $t$-test, the unweighted linear and GP models narrowly miss the threshold ($p = 0.0077 > 0.00714$); however, under the non-parametric Wilcoxon signed-rank test (where Historical Mean beat the candidate in 9 out of 9 years, $W = 0.0$), the exact $p = 0.00391$ survives family-wise correction.
3. **Definitive Conclusion:** **In zero comparisons was any machine learning model statistically superior to `M0_Historical_Mean`.** Every model had a negative sample mean difference ($\bar{D} < 0$), proving that historical climatological persistence outperforms the ML feature-driven models during 2016–2024.

---

## Investigation 5 — Basin-Level and Regional Error Decomposition

### Regional Mass Conservation & The Additivity Theorem

Domain A is not an independent physical basin; it is the exact spatial union of $Hp-I$, $I-Ipp$, and $Ipp-J$. Therefore, for any linear operator or additive forecast, regional cumulative drift must satisfy the exact additivity identity:
$$\Delta V_{\text{drift}}(\text{Domain A}) = \sum_{b \in \{Hp-I, I-Ipp, Ipp-J\}} \Delta V_{\text{drift}}(b)$$

We verified this identity across all models in [`reports/tables/regional_error_decomposition.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/regional_error_decomposition.csv). In all cases, the additivity discrepancy is bounded by floating-point precision ($< 5 \times 10^{-14}\text{ km}^3$).

### Detailed Cross-Basin Error Decomposition

```
========================================================================================================
HISTORICAL MEAN DOMAIN A ENDPOINT DRIFT DECOMPOSITION (2016–2024)
========================================================================================================
Observed Domain A Cumulative Loss:       -183.28 km³
Predicted Domain A Cumulative Loss:      -179.30 km³
Domain A Cumulative Endpoint Drift:        +3.98 km³
Reported Mass Loss Captured:              97.83%

Basin-by-Basin Breakdown:
  Hp-I (Palmer Land West):    -44.37 km³  (Over-predicted ice loss by 44.37 km³)
  I-Ipp (Graham Land West):    -4.79 km³  (Over-predicted ice loss by  4.79 km³)
  Ipp-J (Larsen Coast East):  +53.14 km³  (Under-predicted ice loss by 53.14 km³)
--------------------------------------------------------------------------------------------------------
Net Basin Sum:                -44.37 + (-4.79) + (+53.14) = +3.98 km³ (EXACT SUM)
========================================================================================================
```

| Model Name | $Hp-I$ Drift ($\text{km}^3$) | $I-Ipp$ Drift ($\text{km}^3$) | $Ipp-J$ Drift ($\text{km}^3$) | Sum of Basin Drifts ($\text{km}^3$) | Domain A Drift ($\text{km}^3$) | Discrepancy ($\text{km}^3$) | Reported Loss Captured (%) | Compensation Mechanism |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **M0_Historical_Mean** | -44.365 | -4.793 | +53.140 | +3.982 | +3.982 | $7.11 \times 10^{-15}$ | **97.83%** | $Hp-I$ ($-44.4$) cancelled by $Ipp-J$ ($+53.1$) |
| **M2_BR_Weighted** | -67.742 | -26.441 | +66.226 | -27.957 | -27.957 | $4.26 \times 10^{-14}$ | **115.25%** | $Hp-I$ ($-67.7$) cancelled by $Ipp-J$ ($+66.2$) |
| **M2_Bayesian_Ridge** | -57.048 | -15.796 | +76.832 | +3.988 | +3.988 | $0.00$ | **97.82%** | $Hp-I$ ($-57.0$) cancelled by $Ipp-J$ ($+76.8$) |
| **M0_Persistence** | -4.200 | -2.040 | -0.980 | -7.220 | -7.220 | $1.51 \times 10^{-14}$ | **103.94%** | Telescoping cancellation across all basins |
| **M5_Gradient_Boosting** | -35.397 | -24.451 | +51.916 | -7.932 | -7.932 | $0.00$ | **104.33%** | $Hp-I$ ($-35.4$) cancelled by $Ipp-J$ ($+51.9$) |

### Critical Evaluation of the "97.8% Mass Loss Capture" Metric

1. **Definition of Metric:** The reported 97.8% capture is defined as the ratio of predicted cumulative volume loss to reconstructed cumulative volume loss over 2016–2024:
   $$\text{Capture Ratio} = \frac{\sum_{t=2016}^{2024} \hat{y}_{t,\text{Domain A}}}{\sum_{t=2016}^{2024} y_{t,\text{Domain A}}} = \frac{-179.2975\text{ km}^3}{-183.2800\text{ km}^3} = 97.827\%$$
2. **Deceptive Alignment:** While a 97.8% mass capture ratio superficially suggests near-perfect physical fidelity at the regional scale, the forensic decomposition demonstrates that it is an **algebraic artifact of severe, compensating cross-basin errors**.
3. **Physical Cancellation:** In Graham Land East ($Ipp-J$), the historical mean severely failed to capture post-2002 ice-shelf collapse acceleration, under-predicting cumulative ice loss by $+53.14\text{ km}^3$. Concurrently, in Palmer Land ($Hp-I$), high precipitation accumulation in 2016–2024 caused observed losses to attenuate, so the model over-predicted ice loss by $-44.37\text{ km}^3$. The $+53.14\text{ km}^3$ and $-44.37\text{ km}^3$ errors cancelled each other, leaving a deceptive net regional drift of only $+3.98\text{ km}^3$.
4. **Audit Rule:** **Domain A cumulative drift or percentage capture must never be reported in isolation without immediate presentation of the basin-level decomposition.**

---

## Investigation 6 — Persistence Model Telescoping Identity Forensic Audit

### Mathematical Proof of the Telescoping Identity

The persistence model predicts that the rate of volume change in year $t$ equals the observed rate in year $t-1$:
$$\hat{y}_t = y_{t-1}$$
For an evaluation window spanning calendar years $T_1 = 2016$ to $T_2 = 2024$, the cumulative sum of prediction residuals is:
$$\sum_{t=T_1}^{T_2} e_t = \sum_{t=T_1}^{T_2} (\hat{y}_t - y_t) = \sum_{t=T_1}^{T_2} (y_{t-1} - y_t)$$
Expanding this summation reveals an exact telescoping sum:
$$\sum_{t=T_1}^{T_2} (y_{t-1} - y_t) = (y_{T_1-1} - y_{T_1}) + (y_{T_1} - y_{T_1+1}) + \dots + (y_{T_2-1} - y_{T_2}) \equiv y_{T_1-1} - y_{T_2}$$
For the 2016–2024 test period, $T_1 - 1 = 2015$ (the boundary buffer year) and $T_2 = 2024$. Thus:
$$\Delta V_{\text{drift}}(\text{Persistence}) \equiv y_{2015} - y_{2024}$$

### Numerical Verification Table

We verified this algebraic identity against the empirical residuals in [`reports/tables/persistence_test_audit.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/persistence_test_audit.csv):

| Basin ID | Boundary $y_{2015}$ ($\text{km}^3/\text{yr}$) | Boundary $y_{2024}$ ($\text{km}^3/\text{yr}$) | Theoretical Telescoping Drift ($y_{2015} - y_{2024}$) | Empirical Residual Sum ($\sum e_t$) | Telescoping Discrepancy ($\text{km}^3$) | Annual Rate RMSE ($\text{km}^3/\text{yr}$) | Endpoint Cumulative Drift ($\text{km}^3$) | Max Absolute Path Drift ($\text{km}^3$) | Dynamic Skill Evaluation |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Hp-I** | -11.09 | -6.89 | **-4.20** | **-4.200000000000001** | $8.88 \times 10^{-16}$ | 30.707 | -4.20 | 44.93 | Algebraic artifact; zero dynamic skill |
| **I-Ipp** | -10.87 | -8.83 | **-2.04** | **-2.039999999999999** | $0.00$ | 17.590 | -2.04 | 25.70 | Algebraic artifact; zero dynamic skill |
| **Ipp-J** | -18.85 | -17.87 | **-0.98** | **-0.980000000000000** | $0.00$ | 11.326 | -0.98 | 16.51 | Algebraic artifact; zero dynamic skill |
| **Domain_A** | -40.81 | -33.59 | **-7.22** | **-7.220000000000013** | $1.42 \times 10^{-14}$ | 59.623 | -7.22 | 87.14 | Algebraic artifact; zero dynamic skill |

### Endpoint Cancellation vs Dynamic Skill

1. **Path Drift vs Endpoint Drift:** While the Domain A endpoint cumulative drift for Persistence is small ($-7.22\text{ km}^3$), its **maximum absolute path drift reached $87.14\text{ km}^3$**. Between 2016 and 2024, the cumulative error trajectory oscillated wildly due to large year-to-year volume change swings (e.g., $Hp-I$ swinging from $+33.84\text{ km}^3/\text{yr}$ in 2016 to $-11.29\text{ km}^3/\text{yr}$ in 2017).
2. **Disastrous Annual Accuracy:** The annual rate RMSE of Persistence ($59.62\text{ km}^3/\text{yr}$ on Domain A, $30.71$ on $Hp-I$, pooled $R^2 = -0.9608$) is the worst of all evaluated models.
3. **Epistemological Classification:** Persistence contains non-zero mutual information regarding the multi-decadal mean mass balance state (because $y_{2015} = -40.81\text{ km}^3/\text{yr}$ reflects the modern negative mass balance regime rather than zero); however, **it possesses zero predictive skill for dynamic interannual variations**, and its low endpoint drift is purely a two-point boundary coincidence ($y_{2015} - y_{2024}$).

---

## Investigation 7 — Probabilistic Calibration and Prediction Interval Audit

### Predictive Variance Formulations

We audited the 95% prediction intervals reported for `M2_Bayesian_Ridge_Weighted`, `M2_Bayesian_Ridge` (Unweighted), and `M6_Gaussian_Process` in [`reports/tables/prediction_interval_recalculation.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/prediction_interval_recalculation.csv).

Under a linear Gaussian predictive distribution $\mathcal{N}(\mu(\mathbf{x}), \sigma^2(\mathbf{x}))$, the predictive standard deviation decomposes into parameter uncertainty and residual noise:
$$\sigma^2(\mathbf{x}) = \sigma_{\text{noise}}^2 + \mathbf{x}^T \mathbf{\Sigma}_{\mathbf{w}} \mathbf{x}$$
In standard linear Bayesian Ridge (`sklearn.linear_model.BayesianRidge`), $\sigma_{\text{noise}}^2 = \alpha^{-1}$ is estimated as a **single global homoscedastic scalar** across all observations.

```
========================================================================================================
PREDICTIVE STANDARD DEVIATION AUDIT
========================================================================================================
Model: M2_Bayesian_Ridge_Weighted
  Predictive Std (Hp-I):     12.314 km³/yr  -->  95% Interval Width: 48.27 km³/yr
  Predictive Std (I-Ipp):    12.310 km³/yr  -->  95% Interval Width: 48.25 km³/yr
  Predictive Std (Ipp-J):    12.309 km³/yr  -->  95% Interval Width: 48.25 km³/yr
  Domain A Std:              21.323 km³/yr  -->  95% Interval Width: 83.59 km³/yr

Physical Target Noise (sigma_obs):
  Hp-I:   17.52 km³/yr
  I-Ipp:   7.30 km³/yr
  Ipp-J:   7.70 km³/yr
========================================================================================================
```

### Calibration Breakdown by Basin

| Model Name | Basin ID | Test $N$ | Covered Points | Empirical Coverage (%) | Nominal Coverage (%) | Mean Predictive $\sigma$ ($\text{km}^3/\text{yr}$) | Mean Interval Width ($\text{km}^3/\text{yr}$) | Physical $\sigma_{\text{obs}}$ ($\text{km}^3/\text{yr}$) | Calibration Diagnosis |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **M2_BR_Weighted** | $Hp-I$ | 9 | 7 | 77.8% | 95.0% | 12.314 | 48.269 | 17.52 | Under-covered (high interannual variance) |
| **M2_BR_Weighted** | $I-Ipp$ | 9 | 9 | 100.0% | 95.0% | 12.310 | 48.253 | 7.30 | Over-covered (interval too wide) |
| **M2_BR_Weighted** | $Ipp-J$ | 9 | 9 | 100.0% | 95.0% | 12.309 | 48.252 | 7.70 | Over-covered (interval too wide) |
| **M2_BR_Weighted** | Domain A | 9 | 5 | 55.6% | 95.0% | 21.323 | 83.585 | 20.48 | Under-covered (systematic cross-basin drift) |
| **M2_Bayesian_Ridge**| $Hp-I$ | 9 | 7 | 77.8% | 95.0% | 14.310 | 56.094 | 17.52 | Under-covered |
| **M2_Bayesian_Ridge**| $I-Ipp$ | 9 | 9 | 100.0% | 95.0% | 14.309 | 56.091 | 7.30 | Over-covered |
| **M2_Bayesian_Ridge**| $Ipp-J$ | 9 | 9 | 100.0% | 95.0% | 14.309 | 56.090 | 7.70 | Over-covered |
| **M2_Bayesian_Ridge**| Domain A | 9 | 7 | 77.8% | 95.0% | 24.785 | 97.154 | 20.48 | Under-covered |
| **M6_Gaussian_Process**| $Hp-I$ | 9 | 2 | 22.2% | 95.0% | 1.430 | 5.607 | 17.52 | **Severely under-covered (latent-only noise)** |
| **M6_Gaussian_Process**| $I-Ipp$ | 9 | 3 | 33.3% | 95.0% | 1.430 | 5.604 | 7.30 | **Severely under-covered (latent-only noise)** |
| **M6_Gaussian_Process**| $Ipp-J$ | 9 | 0 | 0.0% | 95.0% | 1.429 | 5.602 | 7.70 | **Severely under-covered (latent-only noise)** |
| **M6_Gaussian_Process**| Domain A | 9 | 2 | 22.2% | 95.0% | 2.476 | 9.707 | 20.48 | **Severely under-covered (latent-only noise)** |

### Key Probabilistic Insights & Small-Sample Limitations

1. **Homoscedasticity vs Heteroscedastic Reality:** Bayesian Ridge assumes a uniform residual variance across all basins ($\sigma \approx 12.31\text{ km}^3/\text{yr}$ for weighted; $\sigma \approx 14.31\text{ km}^3/\text{yr}$ for unweighted). In reality, physical observation and climate uncertainty is strongly heteroscedastic ($Hp-I$ has $\sigma_{\text{obs}} = 17.52$, whereas $I-Ipp$ has $7.30\text{ km}^3/\text{yr}$). Consequently, the intervals are too wide in Graham Land (producing 100% coverage) and too narrow in Palmer Land (producing 77.8% coverage).
2. **Gaussian Process Failure Mode:** `M6_Gaussian_Process` outputted intervals of width $\approx 5.60\text{ km}^3/\text{yr}$ ($\sigma \approx 1.43\text{ km}^3/\text{yr}$). This occurred because the implementation returned the epistemic uncertainty of the latent GP function without adding the physical observation noise variance ($\sigma_{\text{noise}}^2 \approx 15^2$). As a result, empirical coverage collapsed to 0% in $Ipp-J$ and 22.2% overall.
3. **Small Sample Discreteness:** With only $N = 9$ years in the held-out test set, empirical coverage is quantized in discrete steps of:
   $$\Delta = \frac{1}{9} \approx 11.11\%$$
   A single observation moving inside or outside the interval shifts coverage by 11.1%. Thus, an empirical coverage of 77.8% (7/9 covered) is only 2 misses away from nominal 95% coverage. High-precision calibration claims cannot be supported on $N=9$ samples.

---

## Investigation 8 — Physical Attribution and Absent Dynamic State Variables

### Separation of Empirical Observations, Regimes, and Hypotheses

To maintain strict scientific integrity, we audited the physical interpretations made in Phase 4C, separating directly observed evidence from physical hypotheses. The findings are summarized in [`reports/tables/physical_interpretation_audit.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/physical_interpretation_audit.csv):

```
+--------------------------------------------------------------------------------------------------------+
| SCIENTIFIC ATTRIBUTION TAXONOMY                                                                        |
+--------------------------------------------------------------------------------------------------------+
| 1. Directly Observed Residual Pattern:                                                                 |
|    - Basin Ipp-J exhibited persistent positive residuals (under-prediction of ice loss by              |
|      +5.77 to +8.54 km³/yr) in all 9 held-out test years, accumulating +52 to +77 km³ of drift.       |
|    - Basin Hp-I exhibited negative residuals (over-prediction of ice loss by -3.61 to -7.53 km³/yr).  |
|                                                                                                        |
| 2. Verified Temporal Regime Shift:                                                                     |
|    - In basin Ipp-J, reconstructed volume loss abruptly jumped from -3.21 km³/yr (1995–2001) to        |
|      -21.80 km³/yr (2002–2014) and -21.36 km³/yr (2016–2024). This shift is permanent.                |
|                                                                                                        |
| 3. Plausible Physical Explanation (Supported by Literature, but Unmodeled in ML Pipeline):             |
|    - The catastrophic collapse of the Larsen B Ice Shelf in Feb–Mar 2002 removed back-stress           |
|      (buttressing) on tributary glaciers (Crane, Jorum, Green, Flask), causing sustained 2–8x speedup |
|      (Scambos et al. 2004; Rignot et al. 2004; Berthier et al. 2012).                                 |
|    - Palmer Land experienced anomalous atmospheric snowfall accumulation in 2016, 2019, and 2022,    |
|      temporarily masking background dynamic discharge.                                                 |
|                                                                                                        |
| 4. Unverified Claims / Non-Causal Conclusions:                                                         |
|    - Stating that missing buttressing variables "caused" the ML model failure is incomplete.           |
|      ML models also failed on basins Hp-I and I-Ipp where no ice-shelf collapse occurred. A simpler,   |
|      sufficient statistical explanation is that the feature set lacks contemporaneous climate forcing,  |
|      the training sample is tiny (N=108), and observation noise is large (+/- 7 to 20 km³/yr).         |
+--------------------------------------------------------------------------------------------------------+
```

### Missing Physical State Variables

The feature representation used across Phases 4A–4C was restricted to lag-1 surface mass balance ($SMB_{t-1}$), lag-1 discharge ($D_{t-1}$), rolling means, and static topographic descriptors (area, cell count, mean elevation). 

The following critical physical state variables are **completely absent** from the pipeline:
1. **Ice-Shelf Buttressing Factor ($\theta_{\text{buttress}}$):** Parameterizing the loss of compressive back-stress at tributary grounding zones.
2. **Ice-Shelf Frontal Extent & Calving Front Area ($A_{\text{shelf}}$):** Quantifying shelf geometry changes following collapse events.
3. **Grounding Line Position Migration ($\Delta x_{\text{GL}}$):** Tracking retrograde slope retreat and Marine Ice Sheet Instability (MISI) triggers.
4. **Calving Front Stress Tensor ($\sigma_{xx}, \sigma_{xy}$):** Representing longitudinal strain rates and lateral shear margin unpinning.
5. **Circumpolar Deep Water (CDW) Thermal Forcing ($T_{\text{ocean}}$):** Sub-shelf ocean cavity temperatures driving basal melt at grounding lines.
6. **Contemporaneous Meteorological Forcing ($SMB_t$):** The model used $SMB_{t-1}$; consequently, in-year atmospheric river snowfall events (such as the 2016 and 2022 Palmer Land accumulation surges) could not be detected.
7. **Bedrock Topography Pinning Point Geometry:** Local bathymetric pinning points that arrest grounding line retreat.

Without these dynamic boundary conditions, **no statistical regression model can dynamically forecast non-linear glaciological regime shifts.**

---

## Audit Deliverables Archive

In accordance with Phase 4C.1 specifications, the following seven authoritative audit tables have been compiled, verified, and placed in [`reports/tables/`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/):

1. [`reports/tables/test_metric_recalculation.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/test_metric_recalculation.csv) — Master verification leaderboard containing independently recalculated RMSE, MAE, Mean Bias, $R^2$, basin metrics, rate RMSE, and path drifts for all 8 models.
2. [`reports/tables/frozen_protocol_compliance.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/frozen_protocol_compliance.csv) — Audit of pre-registration status, pipeline immutability, and post-unsealing modifications.
3. [`reports/tables/significance_test_reproduction.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/significance_test_reproduction.csv) — Exact paired $t$-tests, Wilcoxon signed-rank tests, Cohen's $d$, and Bonferroni adjustments across $N=9$ annual clusters.
4. [`reports/tables/regional_error_decomposition.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/regional_error_decomposition.csv) — Basin-by-basin decomposition of cumulative drift, additivity proofs, and compensation analysis.
5. [`reports/tables/persistence_test_audit.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/persistence_test_audit.csv) — Proof of the telescoping sum identity ($\sum e_t \equiv y_{2015} - y_{2024}$) and path drift reconciliation.
6. [`reports/tables/prediction_interval_recalculation.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/prediction_interval_recalculation.csv) — 95% interval coverage, mean width, and noise variance analysis by basin.
7. [`reports/tables/physical_interpretation_audit.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/physical_interpretation_audit.csv) — Epistemological taxonomy separating direct observations, verified regime shifts, plausible mechanisms, and absent state variables.

---

## Final Recommendation & Phase Transition Conditions

We recommend **DECISION B — CONDITIONAL PASS** for Phase 4C.

```
========================================================================================================
FINAL FORMAL DETERMINATION: DECISION B (CONDITIONAL PASS)
========================================================================================================
The Phase 4C Held-Out Test Evaluation is APPROVED for historical hindcast benchmarking, subject to the
following five mandatory conditions:

1. Mandatory Climatological Baseline Supremacy:
   All future reporting and publications must state clearly that statistical machine learning models 
   failed to outperform the simple historical mean climatological baseline (M0_Historical_Mean RMSE = 
   14.69 km³/yr vs M2_Bayesian_Ridge_Weighted RMSE = 15.36 km³/yr; p < 0.01 for unweighted models).

2. Prohibition on Deceptive Regional Aggregation:
   The "97.8% mass-loss capture" metric on Domain A must never be cited without disclosing that it 
   results from compensating cross-basin errors (Hp-I over-predicted loss by 44.37 km³; Ipp-J 
   under-predicted loss by 53.14 km³).

3. Persistence Demarcation:
   The low cumulative endpoint drift of M0_Persistence (-7.22 km³) must be identified as an algebraic 
   telescoping artifact (y_2015 - y_2024) rather than dynamic modeling skill.

4. Probabilistic Uncertainty Caveats:
   Prediction intervals must explicitly document homoscedastic noise assumptions in linear models and 
   the low-power discrete granularity (11.1%) of N=9 test samples.

5. Strict Prohibition on Unconstrained 2100 Projections:
   Under no circumstances may these statistical ML architectures be used for multi-decadal forward 
   forecasting to 2100 without coupled dynamic ice-sheet physics (buttressing, ocean cavity thermal 
   forcing, and grounding line migration).
========================================================================================================
```

