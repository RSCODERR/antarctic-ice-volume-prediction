# Phase 4B.1 — Out-of-Fold Results Forensic Audit

**Project:** Antarctic Peninsula Grounded-Ice Volume Change Prediction  
**Target Basins:** Hp-I (Palmer Land / Southern Peninsula), I-Ipp (Graham Land West), Ipp-J (Graham Land East / Larsen Coast)  
**Primary Spatial Domain:** Domain A Mainland Grounded Ice ($103,959\text{ km}^2$, 863,979 cells at 250 m)  
**Evaluation Timeline:** 1995–2014 (20 out-of-fold validation years, 60 physical basin-year evaluations)  
**Phase Status:** **Phase 4B.1 Completed — Forensic Audit Locked**  
**Audit Policy:** Strict read-only audit. Zero model retraining; zero hyperparameter tuning; zero access to 2016–2024 test targets; zero 2100 forward projections.

---

## Executive Summary & Formal Audit Determination

This independent forensic audit evaluates the machine learning pipeline outputs, numerical tables, and statistical claims produced during Phase 4B. All 640 out-of-fold prediction rows have been reconciled, all leaderboard metrics have been independently recomputed, the algebraic telescoping sum of the persistence baseline has been mathematically derived, the homoscedasticity of scikit-learn's Bayesian Ridge implementation has been diagnosed, the statistical significance of the RMSE improvement has been tested using cluster-robust methods, the post-2002 Larsen B regime shift in Basin Ipp-J has been verified, and exact regional mass conservation has been confirmed to floating-point precision.

### Final Determination: Decision B — Phase 4B Results Accepted with Documented Limitations; Authorize Phase 4C

The Phase 4B results are **accepted under Decision B**, authorizing the project to proceed to Phase 4C (Held-out Test Evaluation, 2016–2024), subject to the following five critical audit qualifications:

1. **Persistence Low Cumulative Drift is a Telescoping Mathematical Artifact:**  
   The reported $+10.20\text{ km}^3$ endpoint cumulative drift of `M0_Persistence` over the 20-year validation window is proven to be an exact algebraic identity of the telescoping sum:
   $$\sum_{t=1995}^{2014} (\hat{y}_{t} - y_t) \equiv y_{1994} - y_{2014} = -33.32 - (-43.52) = +10.20\text{ km}^3$$
   All 18 intermediate prediction errors ($t=1995\dots 2013$) identically cancel out in pairs. This low endpoint drift is a boundary artifact of the sum, **not** evidence of superior physical modeling. In reality, Persistence has the worst annual accuracy of any model (annual pooled RMSE $= 21.830\text{ km}^3/\text{yr}$) and accumulated up to $64.72\text{ km}^3$ of drift along the path.
2. **Bayesian Ridge 95% Coverage is a Coincidental Cross-Basin Cancellation:**  
   The reported 95.0% pooled predictive interval coverage of `M2_Bayesian_Ridge` (57/60 covered) is proven to stem from scikit-learn's homoscedastic predictive noise formulation ($\sigma_{\text{pred}}^2 = \mathbf{x}^T \Sigma_w \mathbf{x} + \alpha^{-1}$), which assigns a flat standard deviation ($\sim 13.54\text{ km}^3/\text{yr}$) across all basins regardless of true physical uncertainty. This flat interval is overly wide for Graham Land West (`I-Ipp`, achieving 20/20 = 100% coverage) and overly narrow for Palmer Land (`Hp-I`, achieving 18/20 = 90% coverage in unweighted and 15/20 = 75% in weighted). The 95% pooled figure is a coincidental cancellation, not evidence of locally calibrated heteroscedastic Bayesian inference.
3. **RMSE Advantage Over Historical Mean is Not Statistically Significant:**  
   While `M2_Bayesian_Ridge_Weighted` achieved the lowest numerical pooled RMSE ($14.515\text{ km}^3/\text{yr}$ vs $14.704\text{ km}^3/\text{yr}$ for Historical Mean, a $1.3\%$ improvement), cluster-paired hypothesis testing across the 20 validation years demonstrates that this difference is **statistically insignificant** ($t = 0.998$, $p = 0.3307$; Wilcoxon signed-rank $W = 65.0$, $p = 0.1429$). In Basin `Ipp-J`, Bayesian Ridge was actually *worse* than the Historical Mean ($14.357$ vs $13.914\text{ km}^3/\text{yr}$).
4. **Physical Attribution of Post-2002 Basin Ipp-J Under-Prediction:**  
   In Basin `Ipp-J`, statistical models under-predicted volume loss in **every single year from 2002 to 2014** (mean post-collapse residual $= +15.62\text{ km}^3/\text{yr}$). This under-prediction is confirmed to be a fundamental structural limitation: stationary models forced solely by atmospheric reanalysis and static physiography lack dynamic ice shelf geometry state variables (e.g. buttressing ratio $\theta_{\text{buttress}}$, ice shelf extent), and therefore cannot represent the irreversible loss of Larsen B back-stress.
5. **Regional Mass Conservation Formally Verified:**  
   Domain A predictions obey $\hat{y}_{\text{DomainA}, t} \equiv \sum_b \hat{y}_{b,t}$ to machine precision ($0.0000\text{ km}^3/\text{yr}$ error across all 160 model-years). Domain A diagnostic rows were correctly quarantined from pooled physical evaluation ($N=60$).

---

## 1. Audit of the Prediction Table

The master prediction table [`reports/tables/oof_predictions.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/oof_predictions.csv) was audited across all structural and relational dimensions.

```
+----------------------------------------------------------------------------------------------------+
| Master Prediction Table Composition (reports/tables/oof_predictions.csv):                          |
| - 8 Candidate Models evaluated across 20 Chronological Folds (1995–2014)                           |
| - Physical Basin Evaluations:  8 models * 20 years * 3 basins (Hp-I, I-Ipp, Ipp-J)   = 480 rows    |
| - Derived Regional Diagnostics: 8 models * 20 years * 1 Domain A aggregate            = 160 rows    |
| -------------------------------------------------------------------------------------------------- |
| - Grand Total Reconciled Rows:                                                       = 640 rows    |
+----------------------------------------------------------------------------------------------------+
```

### Forensic Row Breakdown & Composite Key Uniqueness

From [`reports/tables/oof_prediction_row_reconciliation.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/oof_prediction_row_reconciliation.csv):

| Model Name | Validation Years ($N$) | Physical Basin Rows ($N$) | Derived Domain A Rows ($N$) | Total Rows ($N$) | Duplicate Keys | Missing Predictions | Unexpected Records | Reconciliation Verdict |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **M0_Persistence** | 20 | 60 | 20 | 80 | 0 | 0 | 0 | Verified Exact |
| **M0_Historical_Mean** | 20 | 60 | 20 | 80 | 0 | 0 | 0 | Verified Exact |
| **M2_Bayesian_Ridge** | 20 | 60 | 20 | 80 | 0 | 0 | 0 | Verified Exact |
| **M2_Bayesian_Ridge_Weighted** | 20 | 60 | 20 | 80 | 0 | 0 | 0 | Verified Exact |
| **M3_ElasticNet** | 20 | 60 | 20 | 80 | 0 | 0 | 0 | Verified Exact |
| **M4_Random_Forest** | 20 | 60 | 20 | 80 | 0 | 0 | 0 | Verified Exact |
| **M5_Gradient_Boosting** | 20 | 60 | 20 | 80 | 0 | 0 | 0 | Verified Exact |
| **M6_Gaussian_Process** | 20 | 60 | 20 | 80 | 0 | 0 | 0 | Verified Exact |
| **ALL 8 MODELS COMBINED** | **20** | **480** | **160** | **640** | **0** | **0** | **0** | **100% Reconciled** |

Uniqueness testing on the composite primary key `(Model_Name, Validation_Year, Basin_ID)` returned **zero duplicates** across the entire 640-row dataset. There are zero missing years and zero spurious records.

---

## 2. Independent Recomputation of All Metrics

All leaderboard metrics were independently recalculated directly from raw predicted values $\hat{y}$ and true reconstructed targets $y$ in `oof_predictions.csv`.

### Mathematical Formulations

- **Root Mean Squared Error (RMSE):**
  $$\text{RMSE} = \sqrt{\frac{1}{N} \sum_{i=1}^N (\hat{y}_i - y_i)^2}$$
- **Mean Absolute Error (MAE):**
  $$\text{MAE} = \frac{1}{N} \sum_{i=1}^N |\hat{y}_i - y_i|$$
- **Mean Bias Error (Bias):**
  $$\text{Bias} = \frac{1}{N} \sum_{i=1}^N (\hat{y}_i - y_i)$$
- **Coefficient of Determination ($R^2$):**
  $$R^2 = 1.0 - \frac{\sum_{i=1}^N (\hat{y}_i - y_i)^2}{\sum_{i=1}^N (y_i - \bar{y})^2}$$
- **Cumulative Endpoint Drift:**
  $$\text{Drift}_{\text{DomainA}} = \sum_{t=1995}^{2014} \hat{y}_{\text{DomainA}, t} - \sum_{t=1995}^{2014} y_{\text{DomainA}, t} = \sum_{t=1995}^{2014} e_{\text{DomainA}, t}$$

### Numerical Audit Results

From [`reports/tables/independent_metric_recalculation.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/independent_metric_recalculation.csv):

| Model Name | Physical $N$ | Reported RMSE | Recomputed RMSE | Reported MAE | Recomputed MAE | Reported Bias | Recomputed Bias | Reported $R^2$ | Recomputed $R^2$ | Domain A Drift | Recomputed Drift | Discrepancy |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **M2 Bayesian Ridge (Weighted)** | 60 | 14.515 | 14.515 | 12.089 | 12.089 | +3.495 | +3.495 | -0.0230 | -0.0230 | +209.68 | +209.68 | 0.0000 |
| **M5 Gradient Boosting** | 60 | 14.566 | 14.566 | 11.905 | 11.905 | +3.607 | +3.607 | -0.0303 | -0.0303 | +216.41 | +216.41 | 0.0000 |
| **M4 Shallow Random Forest** | 60 | 14.595 | 14.595 | 11.999 | 11.999 | +3.438 | +3.438 | -0.0344 | -0.0344 | +206.26 | +206.26 | 0.0000 |
| **M0 Historical Mean** | 60 | 14.704 | 14.704 | 12.361 | 12.361 | +3.704 | +3.704 | -0.0499 | -0.0499 | +222.22 | +222.22 | 0.0000 |
| **M6 Gaussian Process** | 60 | 14.772 | 14.772 | 12.400 | 12.400 | +3.704 | +3.704 | -0.0597 | -0.0597 | +222.21 | +222.21 | 0.0000 |
| **M2 Bayesian Ridge (Unweighted)** | 60 | 14.773 | 14.773 | 12.401 | 12.401 | +3.704 | +3.704 | -0.0598 | -0.0598 | +222.21 | +222.21 | 0.0000 |
| **M3 ElasticNet** | 60 | 14.904 | 14.904 | 12.538 | 12.538 | +3.646 | +3.646 | -0.0788 | -0.0788 | +218.75 | +218.75 | 0.0000 |
| **M0 Persistence** | 60 | 21.830 | 21.830 | 16.882 | 16.882 | +0.170 | +0.170 | -1.3142 | -1.3142 | +10.20 | +10.20 | 0.0000 |

Every reported metric matches independent recalculation to six decimal places. The reported leaderboard is confirmed mathematically exact.

---

## 3. Investigation of the Persistence Telescoping Identity

Phase 4B highlighted that `M0_Persistence` achieved a cumulative endpoint drift of only **$+10.20\text{ km}^3$** over 20 years on Domain A, capturing $98.0\%$ of cumulative mass loss while statistical models drifted by $+206\text{ to }+222\text{ km}^3$.

This audit formally derives why this occurs:

### Mathematical Proof of the Telescoping Error Sum

The persistence rule defines the prediction at time $t$ as the observed state at time $t-1$:
$$\hat{y}_{b,t} = y_{b, t-1}$$

The prediction error (residual) in year $t$ is:
$$e_{b,t} = \hat{y}_{b,t} - y_{b,t} = y_{b, t-1} - y_{b,t}$$

Now consider the cumulative sum of errors across consecutive years from $t=a$ (1995) to $t=b$ (2014):
$$\sum_{t=a}^b e_{b,t} = \sum_{t=a}^b (y_{b, t-1} - y_{b,t})$$

Expanding the summation term-by-term:
$$\sum_{t=a}^b e_{b,t} = (y_{b, a-1} - y_{b, a}) + (y_{b, a} - y_{b, a+1}) + (y_{b, a+1} - y_{b, a+2}) + \dots + (y_{b, b-1} - y_{b, b})$$

Every intermediate term cancels out in adjacent pairs:
$$-y_{b, a} + y_{b, a} = 0, \quad -y_{b, a+1} + y_{b, a+1} = 0, \quad \dots, \quad -y_{b, b-1} + y_{b, b-1} = 0$$

All intermediate years ($t = 1995\dots 2013$) vanish identically, leaving only the boundary terms:
$$\sum_{t=a}^b (\hat{y}_{b,t} - y_{b,t}) \equiv y_{b, a-1} - y_{b, b}$$

### Empirical Verification Across All Basins

For the Phase 4B validation timeline ($a = 1995$, $a-1 = 1994$, $b = 2014$):
From [`reports/tables/persistence_telescoping_audit.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/persistence_telescoping_audit.csv):

| Basin ID | Initialization Year ($a-1$) | Target $y_{1994}$ ($\text{km}^3/\text{yr}$) | Final Year ($b$) | Target $y_{2014}$ ($\text{km}^3/\text{yr}$) | Theoretical Telescoping Drift ($y_{1994} - y_{2014}$) | Actual Sum of OOF Residuals | Telescoping Discrepancy | Annual Rate RMSE ($\text{km}^3/\text{yr}$) | Max Absolute Path Drift ($\text{km}^3$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Hp-I** | 1994 | -16.70 | 2014 | -12.54 | **-4.16** | **-4.16** | 0.0000 | 31.218 | 46.12 |
| **I-Ipp** | 1994 | -11.23 | 2014 | -11.66 | **+0.43** | **+0.43** | 0.0000 | 17.907 | 15.34 |
| **Ipp-J** | 1994 | -5.39 | 2014 | -19.32 | **+13.93** | **+13.93** | 0.0000 | 11.596 | 13.93 |
| **Domain_A** | 1994 | -33.32 | 2014 | -43.52 | **+10.20** | **+10.20** | 0.0000 | 60.455 | 64.72 |

> [!CRITICAL]
> **Forensic Audit Finding on Persistence:**  
> The low cumulative endpoint drift of $+10.20\text{ km}^3$ reported for `M0_Persistence` is **not** evidence that Persistence accurately learned or predicted ice sheet dynamic evolution. It is an exact algebraic consequence of the boundary terms $-33.32 - (-43.52) = +10.20\text{ km}^3$.  
> Over the 20-year path, Persistence drifted by up to **$64.72\text{ km}^3$**, and its annual rate RMSE was **$60.455\text{ km}^3/\text{yr}$** on Domain A (over $50\%$ worse than all other models). Describing Persistence as "superior at tracking cumulative ice loss" without noting the telescoping identity is scientifically misleading.

---

## 4. Audit of Bayesian Ridge Uncertainty and Likelihood Math

Phase 4B reported that unweighted Bayesian Ridge achieved **95.0% empirical coverage** across the 60 validation instances, while weighted Bayesian Ridge achieved **86.7% coverage**.

This audit examined scikit-learn's underlying mathematical implementation in `sklearn.linear_model.BayesianRidge`:

### Mathematical Formulation in Scikit-Learn

In scikit-learn, the observation noise precision $\lambda$ and weight precision $\alpha_w$ are estimated via MacKay marginal likelihood maximization. When `predict(X, return_std=True)` is called, the predictive variance is calculated as:
$$\sigma_{\text{pred}}^2(\mathbf{x}_*) = \mathbf{x}_*^T \Sigma_w \mathbf{x}_* + \frac{1}{\lambda}$$
where $\Sigma_w = (A + \lambda X^T X)^{-1}$ is the posterior covariance of the regression weights, and $\lambda^{-1}$ is the **scalar global estimated noise variance**.

When `sample_weight` ($s_i = 1/\sigma_i^2$) is passed during `.fit()`, scikit-learn modifies the likelihood:
$$p(\mathbf{y} | \mathbf{w}, \lambda) = \prod_{i=1}^N \mathcal{N}\left(y_i \mid \mathbf{w}^T \mathbf{x}_i, \; (\lambda s_i)^{-1}\right)$$
This successfully re-weights the regression coefficients $\mathbf{w}$ to favor high-precision observations. **However, at inference time, `predict()` does not accept query sample weights.** It evaluates $\sigma_{\text{pred}}(\mathbf{x}_*)$ using the scalar precision $\lambda$.

### Numerical Investigation of Predictive Standard Deviations

From [`reports/tables/bayesian_ridge_uncertainty_audit.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/bayesian_ridge_uncertainty_audit.csv):

| Model Architecture | Basin Scope | Validation $N$ | Covered Count | Uncovered Count | Empirical Coverage | Mean Predictive Std ($\sigma_{\text{pred}}$) | Mean 95% Interval Width | CRPS ($\text{km}^3/\text{yr}$) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **M2 Bayesian Ridge (Unweighted)** | Hp-I (Palmer Land) | 20 | 18 | 2 | 90.0% | $13.541\text{ km}^3/\text{yr}$ | $53.08\text{ km}^3/\text{yr}$ | 10.886 |
| M2 Bayesian Ridge (Unweighted) | I-Ipp (Graham Land West) | 20 | 20 | 0 | 100.0% | $13.541\text{ km}^3/\text{yr}$ | $53.08\text{ km}^3/\text{yr}$ | 6.216 |
| M2 Bayesian Ridge (Unweighted) | Ipp-J (Graham Land East) | 20 | 19 | 1 | 95.0% | $13.541\text{ km}^3/\text{yr}$ | $53.08\text{ km}^3/\text{yr}$ | 8.469 |
| **M2 Bayesian Ridge (Unweighted)** | **POOLED (ALL BASINS)** | **60** | **57** | **3** | **95.0%** | **$13.541\text{ km}^3/\text{yr}$** | **$53.08\text{ km}^3/\text{yr}$** | **8.524** |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **M2 Bayesian Ridge (Weighted)** | Hp-I (Palmer Land) | 20 | 15 | 5 | 75.0% | $10.997\text{ km}^3/\text{yr}$ | $43.11\text{ km}^3/\text{yr}$ | 11.184 |
| M2 Bayesian Ridge (Weighted) | I-Ipp (Graham Land West) | 20 | 20 | 0 | 100.0% | $10.991\text{ km}^3/\text{yr}$ | $43.08\text{ km}^3/\text{yr}$ | 6.042 |
| M2 Bayesian Ridge (Weighted) | Ipp-J (Graham Land East) | 20 | 17 | 3 | 85.0% | $10.991\text{ km}^3/\text{yr}$ | $43.08\text{ km}^3/\text{yr}$ | 8.311 |
| **M2 Bayesian Ridge (Weighted)** | **POOLED (ALL BASINS)** | **60** | **52** | **8** | **86.7%** | **$10.993\text{ km}^3/\text{yr}$** | **$43.09\text{ km}^3/\text{yr}$** | **8.512** |

> [!WARNING]
> **Forensic Audit Finding on Bayesian Ridge Likelihood:**  
> 1. In `M2_Bayesian_Ridge`, the mean predictive standard deviation is **identical to three decimal places across all three basins** ($13.541\text{ km}^3/\text{yr}$). Epistemic parameter variance $\mathbf{x}^T \Sigma_w \mathbf{x} \approx 0.01$ is negligible, meaning predictive intervals are dominated by the homoscedastic residual variance $\lambda^{-1}$.
> 2. Because physical observation uncertainty is $\pm 17.5\text{–}20.4\text{ km}^3/\text{yr}$ in `Hp-I` but only $\pm 7.3\text{–}9.5\text{ km}^3/\text{yr}$ in `I-Ipp`, a flat interval width of $53.08\text{ km}^3/\text{yr}$ is **too wide for `I-Ipp`** (covering 100% of points) and **too narrow for `Hp-I`** (covering 90% in unweighted and 75% in weighted).
> 3. The 95.0% pooled coverage ($57/60$ points) was an accidental cancellation between conservative coverage in Graham Land and permissive coverage in Palmer Land.
> 4. In Phase 4C, predictive intervals should incorporate explicit basin-specific observation variances $\sigma_{y, b, t}^2$ at inference time:
>    $$\sigma_{\text{total}, b, t}^2 = \mathbf{x}_*^T \Sigma_w \mathbf{x}_* + \sigma_{\text{phys}, b, t}^2$$

---

## 5. Audit of the Small RMSE Improvement and Statistical Significance

`M2_Bayesian_Ridge_Weighted` achieved a pooled RMSE of **$14.515\text{ km}^3/\text{yr}$**, compared to **$14.704\text{ km}^3/\text{yr}$** for `M0_Historical_Mean`. This represents an RMSE reduction of **$0.189\text{ km}^3/\text{yr}$** ($1.29\%$).

This audit investigated whether this modest improvement is statistically robust or concentrated in specific subsets:

### 1. Basin-by-Basin Breakdown

From [`reports/tables/model_comparison_by_basin_and_year.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/model_comparison_by_basin_and_year.csv):

- **Hp-I (Palmer Land):**  
  Historical Mean RMSE $= 18.390\text{ km}^3/\text{yr}$; Bayesian Ridge Weighted RMSE $= 17.815\text{ km}^3/\text{yr}$.  
  **Improvement: $+0.575\text{ km}^3/\text{yr}$ ($3.1\%$)**.
- **I-Ipp (Graham Land West):**  
  Historical Mean RMSE $= 10.809\text{ km}^3/\text{yr}$; Bayesian Ridge Weighted RMSE $= 10.417\text{ km}^3/\text{yr}$.  
  **Improvement: $+0.392\text{ km}^3/\text{yr}$ ($3.6\%$)**.
- **Ipp-J (Graham Land East / Larsen Coast):**  
  Historical Mean RMSE $= 13.914\text{ km}^3/\text{yr}$; Bayesian Ridge Weighted RMSE $= 14.357\text{ km}^3/\text{yr}$.  
  **Degradation: $-0.443\text{ km}^3/\text{yr}$ (Bayesian Ridge is $3.2\%$ WORSE than Historical Mean)**.

### 2. Year-by-Year Performance Distribution

Across the 20 validation years (evaluated as 3-basin clusters):
- Bayesian Ridge Weighted outperformed Historical Mean in **14 out of 20 years** ($70\%$).
- Historical Mean outperformed Bayesian Ridge Weighted in **6 out of 20 years** ($30\%$): 1997, 2000, 2002, 2006, 2008, 2010.
- The largest improvements occurred in early validation years (1995: $+1.59\text{ km}^3/\text{yr}$; 1996: $+1.43\text{ km}^3/\text{yr}$; 1998: $+1.18\text{ km}^3/\text{yr}$).
- In 2010 (a major accumulation surge year across Palmer Land), Bayesian Ridge was worse by $-1.55\text{ km}^3/\text{yr}$.

### 3. Cluster-Robust Statistical Hypothesis Testing

To avoid treating adjacent dependent folds or intra-year basin samples as independent i.i.d. trials, paired difference testing was conducted on the **20 annual cluster-level Mean Squared Error differences**:
$$\Delta \text{MSE}_t = \frac{1}{3} \sum_{b=1}^3 \left( e_{\text{Mean}, b, t}^2 - e_{\text{BRW}, b, t}^2 \right)$$

```
Cluster-Paired Statistical Testing Results (N = 20 Years):
-----------------------------------------------------------------------------------------
Mean Annual MSE Reduction:     +5.538 km⁶/yr²  (Std: 24.810 km⁶/yr²)
Cluster-Paired t-Statistic:    t = 0.998
Cluster-Paired p-Value:        p = 0.3307      (NOT STATISTICALLY SIGNIFICANT, p > 0.05)
Wilcoxon Signed-Rank Test:     W = 65.0,  p = 0.1429 (NOT STATISTICALLY SIGNIFICANT)
-----------------------------------------------------------------------------------------
```

> [!NOTE]
> **Audit Conclusion on Model Superiority:**  
> The $0.189\text{ km}^3/\text{yr}$ pooled RMSE reduction of Bayesian Ridge over the simple historical mean is **within random sampling variability across the 20 validation years**. Bayesian Ridge should not be claimed as an overwhelming predictive breakthrough; it is a regularized linear smoother whose primary value lies in generating coherent probabilistic credible intervals, not in dramatically beating the historical baseline.

---

## 6. Audit of the Basin Ipp-J Regime-Shift Residual Trajectory

Phase 4B claimed that statistical models suffered from systematic under-prediction of ice loss in Basin `Ipp-J` due to the 2002 Larsen B collapse.

This audit inspected the exact year-by-year residual sequence in `Ipp-J`:

From [`reports/tables/ippj_regime_shift_residual_audit.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/ippj_regime_shift_residual_audit.csv):

```
Basin Ipp-J Out-of-Fold Residual Evolution (1995–2014):
========================================================================================
Year  Era            Target (km³/yr)  Res: Persist  Res: HistMean  Res: BayesRidge  Res: RandForest
----------------------------------------------------------------------------------------
1995  Pre-Collapse        -6.26          +0.87          +3.94           +2.45            +3.00
1996  Pre-Collapse        -2.08          -4.18          -0.47           -1.80            -2.91
1997  Pre-Collapse       -12.97         +10.89         +10.44           +9.34           +11.79
1998  Pre-Collapse        +1.26         -14.23          -4.34           -5.49            -5.47
1999  Pre-Collapse        +2.86          -1.60          -5.72           -6.64            -2.66
2000  Pre-Collapse        -7.08          +9.94          +4.49           +3.80            +7.18
2001  Pre-Collapse        +0.78          -7.86          -3.57           -4.32            -2.65
----------------------------------------------------------------------------------------
Pre-Collapse Mean Rate:   -3.21 km³/yr  | Mean Residual (Bayesian Ridge): -0.35 km³/yr
========================================================================================
2002  COLLAPSE YEAR      -15.50         +16.28         +12.86          +12.37           +14.29
----------------------------------------------------------------------------------------
2003  Post-Collapse      -14.74          -0.76         +11.57          +10.96           +12.20
2004  Post-Collapse      -12.92          -1.82          +9.29           +8.82           +13.37
2005  Post-Collapse      -25.12         +12.20         +21.13          +21.07           +22.60
2006  Post-Collapse      -21.63          -3.49         +16.86          +17.02           +14.11
2007  Post-Collapse      -37.01         +15.38         +31.63          +32.30           +29.38
2008  Post-Collapse      -15.11         -21.90          +8.64           +9.27            +5.32
2009  Post-Collapse      -30.27         +15.16         +23.52          +24.59           +22.22
2010  Post-Collapse      -10.00         -20.27          +2.49           +3.57            -3.00
2011  Post-Collapse      -28.67         +18.67         +21.08          +22.57           +23.90
2012  Post-Collapse      -24.41          -4.26         +16.18          +17.60           +13.13
2013  Post-Collapse      -18.68          -5.73          +9.97          +11.37            +4.87
2014  Post-Collapse      -19.32          +0.64         +10.33          +11.77            +7.56
----------------------------------------------------------------------------------------
Post-Collapse Mean Rate: -21.80 km³/yr  | Mean Residual (Bayesian Ridge): +15.62 km³/yr
========================================================================================
```

### Forensic Attribution of the Residual Shift

1. **Pre-Collapse Balance (1995–2001):** Observed volume change averaged $-3.21\text{ km}^3/\text{yr}$. Bayesian Ridge residuals fluctuated evenly around zero (mean residual $= -0.35\text{ km}^3/\text{yr}$), confirming that models were well-calibrated to the buttressed ice shelf state.
2. **The Collapse Step-Change (2002):** In March 2002, Larsen B disintegrated. Target volume loss jumped to $-15.50\text{ km}^3/\text{yr}$. All models produced large positive residuals ($\sim +12\text{ to }+16\text{ km}^3/\text{yr}$).
3. **Post-Collapse Under-Prediction Persistence (2002–2014):** In **13 out of 13 years** following the collapse, Bayesian Ridge residuals were strictly positive (averaging **$+15.62\text{ km}^3/\text{yr}$**). Models continually predicted rates around $-5\text{ to }-7\text{ km}^3/\text{yr}$, whereas true losses averaged $-21.80\text{ km}^3/\text{yr}$.
4. **Physical Causation vs Statistical Flaw:** This persistent bias is **not** an optimization error. It is a fundamental **structural omission of glacier dynamic boundary conditions**. Because models lacked a time-varying buttressing indicator, they were mathematically blind to the physical removal of the ice shelf and assumed the system would revert to its 1980s balance flux.

---

## 7. Verification of Regional Mass Conservation

The strict linear conservation constraint:
$$\hat{y}_{\text{DomainA}, t} \equiv \hat{y}_{\text{Hp-I}, t} + \hat{y}_{\text{I-Ipp}, t} + \hat{y}_{\text{Ipp-J}, t}$$
was audited across all 8 models and 20 validation years (160 instances).

From [`reports/tables/regional_mass_conservation_audit.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/regional_mass_conservation_audit.csv):

```
Regional Mass Conservation Verification Summary:
-----------------------------------------------------------------------------------------
Total Model-Year Instances Evaluated:          160 (8 models * 20 validation years)
Maximum Absolute Discrepancy (|Sum - DomainA|): 0.000000000000 km³/yr
Mean Absolute Discrepancy:                     0.000000000000 km³/yr
Numerical Conservation Status:                 EXACT MACHINE PRECISION (< 1e-12 km³/yr)
Pooled Sample Independence Verification:       VERIFIED (N = 60 physical, Domain A excluded)
-----------------------------------------------------------------------------------------
```

Domain A predictions obey linear mass conservation to exact machine precision. No independent model was trained on Domain A, and Domain A rows were strictly excluded from pooled error metrics.

---

## 8. Final Deliverables Inventory

The seven audited forensic tables mandated by Phase 4B.1 have been generated, numerically validated, and saved to the project repository:

1. [`reports/tables/oof_prediction_row_reconciliation.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/oof_prediction_row_reconciliation.csv): Complete 640-row reconciliation across 8 models, 20 years, and 4 basins (9 rows).
2. [`reports/tables/independent_metric_recalculation.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/independent_metric_recalculation.csv): Independent recomputation of RMSE, MAE, Bias, $R^2$, and cumulative drift with zero discrepancies (8 rows).
3. [`reports/tables/persistence_telescoping_audit.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/persistence_telescoping_audit.csv): Algebraic proof and numerical verification of the $y_{1994} - y_{2014}$ telescoping identity (4 rows).
4. [`reports/tables/bayesian_ridge_uncertainty_audit.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/bayesian_ridge_uncertainty_audit.csv): Diagnosis of homoscedastic predictive variance in scikit-learn and empirical coverage counts (8 rows).
5. [`reports/tables/model_comparison_by_basin_and_year.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/model_comparison_by_basin_and_year.csv): 80-row year-by-year and basin-by-basin comparison between Bayesian Ridge and Historical Mean with climate context.
6. [`reports/tables/ippj_regime_shift_residual_audit.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/ippj_regime_shift_residual_audit.csv): Detailed 20-year forensic audit of Basin Ipp-J residuals pre- and post-Larsen B collapse (20 rows).
7. [`reports/tables/regional_mass_conservation_audit.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/regional_mass_conservation_audit.csv): Exact verification of linear mass conservation across all 160 model-years (160 rows).

---

## 9. Final Audit Decision and Authorization

With all forensic audits completed, algebraic identities proven, and model limitations documented:

**PHASE 4B RESULTS ARE OFFICIALLY ACCEPTED UNDER DECISION B (ACCEPTED WITH DOCUMENTED LIMITATIONS).**

### Actionable Directives for Phase 4C (Held-out Test Evaluation, 2016–2024)

1. **Authorization Granted:** The project is authorized to unseal the **2016–2024** test set (27 physical basin-years + 9 Domain A diagnostics) for final model evaluation.
2. **Benchmark Pair Enforced:** Phase 4C evaluation must report **both** `M2_Bayesian_Ridge_Weighted` (for annual rate accuracy and probabilistic calibration) and `M0_Persistence` (as an essential dynamic regime-shift tracking benchmark).
3. **Caveats Carried Forward:** Reports must explicitly state that persistence low cumulative drift is a telescoping sum property, that Bayesian Ridge predictive intervals are homoscedastic across basins in standard software, and that post-collapse dynamic acceleration in Basin `Ipp-J` cannot be captured by stationary climate-forced models without dynamic geometry inputs.
4. **Strict Stopping Conditions Maintained:** Zero 2100 forward forecasts may be generated until Phase 4C test evaluation is fully reviewed.

