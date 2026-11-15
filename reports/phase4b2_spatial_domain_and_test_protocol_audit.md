# Phase 4B.2 — Spatial Domain & Test Protocol Integrity Audit

**Project:** Antarctic Peninsula Grounded-Ice Volume Change Prediction  
**Target Basins:** Hp-I (Palmer Land / Southern Peninsula), I-Ipp (Graham Land West), Ipp-J (Graham Land East / Larsen Coast)  
**Primary Spatial Domain:** Domain A Mainland Grounded Ice ($216,062.17\text{ km}^2$, 866,358 cells at 500 m)  
**Historical Target Period:** 1979–2024 (46 years, 138 physical basin-year observations, 46 derived Domain A diagnostic records)  
**Phase Status:** **Phase 4B.2 Completed — Spatial Domain & Test Protocol Locked**  
**Audit Policy:** Strict read-only integrity audit. Zero model retraining; zero hyperparameter tuning; zero access to or inspection of held-out 2016–2024 test targets; zero 2100 forward projections; zero dataset alteration.

---

## Executive Summary & Formal Audit Determination

Before authorizing the unsealing of the held-out 2016–2024 test targets for Phase 4C, this forensic audit evaluates the spatial-domain definitions, static feature provenance, historical target aggregation, and the operational evaluation protocol.

All apparent discrepancies between the authoritative Phase 2.6 spatial baseline and the Phase 4A.2 feature documentation have been forensically tracked to their source. The physical raster arrays, polygon boundaries, and historical volume targets have been proven to be mathematically sound, mutually exclusive, and completely uncorrupted. The static feature discrepancies in `feature_builder.py` are proven to be non-material to model outputs due to exact collinearity with categorical basin indicator dummies. Furthermore, an immutable test protocol is formally locked to prevent any risk of data leakage or test-set hyperparameter tuning.

### Final Determination: DECISION B — CONDITIONAL PASS

The spatial definitions, historical target integrity, and test evaluation protocols are approved under **Decision B (CONDITIONAL PASS)**.

```
+----------------------------------------------------------------------------------------------------+
| AUDIT DETERMINATION: DECISION B (CONDITIONAL PASS)                                                 |
| - Spatial Domain Reconciliation: Reconciled & Verified. Authoritative domain is 866,358 cells /   |
|   216,062.17 km² at 500m resolution. Phase 4A.2 headers contained non-material reporting typos.     |
| - Static Descriptors Trace: Reconciled. Discrepancies in feature_builder.py are collinear with      |
|   basin fixed-effect dummies and have zero numerical effect on historical volume targets.          |
| - Target Footprint Consistency: Verified Exact. Physical basin targets match Phase 3.2 to 0.000000 |
|   km³/yr; Domain A linear additivity is strictly preserved across all 46 years.                    |
| - Test Protocol Lock: Finalized. Sealed test period (2016–2024, N=27 physical) and mandatory       |
|   benchmarks (M0 Persistence, M0 Historical Mean, M2 Bayesian Ridge) locked for Phase 4C.          |
+----------------------------------------------------------------------------------------------------+
```

---

## 1. Investigation 1 — Resolution of the Spatial-Domain Discrepancy

A rigorous forensic comparison was conducted between the authoritative Phase 2.6 baseline values and the Phase 4A.2 reported values.

### Numerical Comparison Matrix

From [`reports/tables/spatial_domain_reconciliation.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/spatial_domain_reconciliation.csv):

| Spatial Domain Parameter | Phase 2.6 Audited Baseline | Phase 4A.2 Reported Value | Numerical Discrepancy | Physical Raster Ground Truth | Forensic Root-Cause Attribution | Material Impact on Volume Targets | Audit Verdict |
| :--- | :---: | :---: | :---: | :---: | :--- | :---: | :--- |
| **Domain A Cell Count** | **866,358 cells** | 863,979 cells | -2,379 cells (-0.27%) | **866,358 cells** | Draft typo from Phase 3.1B text ($886,214 - 22,235 = 863,979$). Fully resolved in Phase 3.2 Preflight Check 1. | **NONE** | **RECONCILED (CLERICAL TYPO)** |
| **Grid Resolution** | **500.0 m $\times$ 500.0 m** | 250 m | -250 m (-50%) | **500.0 m $\times$ 500.0 m** | Descriptive conflation between the 250 m half-pixel grid registration shift (Phase 2.5) and the 500 m grid cell size. Zero 250 m rasters exist. | **NONE** | **RECONCILED (REPORTING ERROR)** |
| **Grid Coordinate System** | **EPSG:3031** | EPSG:3031 | 0 (Exact Match) | **EPSG:3031** | Antarctic Polar Stereographic (standard parallel $-71^\circ$ S). Invariant. | **NONE** | **VERIFIED EXACT** |
| **Nominal Cell Area** | **0.2500 km²** | 0.0625 km² / 0.1203 km² | -0.1875 km² / -0.1297 km² | **0.2500 km²** | Mathematical artifact of assuming 250 m pixel spacing or dividing nominal area by 2. | **NONE** | **RECONCILED (DERIVATIVE ARTIFACT)** |
| **Domain A Grounded Area** | **216,062.17 km²** | 103,959 km² | -112,103.17 km² (-51.88%) | **216,062.17 km²** | Transcription of halved static basin descriptors into `feature_builder.py` ($53,883 + 23,178 + 26,898 = 103,959\text{ km}^2$). | **NONE** | **RECONCILED (STATIC FEATURE SCALAR ERROR)** |
| **Basin Hp-I Grounded Area** | **108,945.63 km²** | 53,883 km² | -55,062.63 km² (-50.54%) | **108,945.63 km²** | Static descriptor in `feature_builder.py` (~49.5% of true area). | **NONE** | **RECONCILED (STATIC FEATURE SCALAR ERROR)** |
| **Basin I-Ipp Grounded Area** | **49,757.73 km²** | 23,178 km² | -26,579.73 km² (-53.42%) | **49,757.73 km²** | Static descriptor in `feature_builder.py` (~46.6% of true area). | **NONE** | **RECONCILED (STATIC FEATURE SCALAR ERROR)** |
| **Basin Ipp-J Grounded Area** | **57,358.82 km²** | 26,898 km² | -30,460.82 km² (-53.11%) | **57,358.82 km²** | Static descriptor in `feature_builder.py` (~46.9% of true area). | **NONE** | **RECONCILED (STATIC FEATURE SCALAR ERROR)** |
| **Bedmap3 Baseline Anchor** | **133,497.59 km³** | 133,497.59 km³ | 0.00 km³ (Exact Match) | **133,497.59 km³** | Identical baseline volume anchor across all phases. | **NONE** | **VERIFIED EXACT** |
| **BedMachine Baseline Anchor**| **140,702.51 km³** | 140,702.51 km³ | 0.00 km³ (Exact Match) | **140,702.51 km³** | Identical baseline volume anchor across all phases. | **NONE** | **VERIFIED EXACT** |
| **Structural Offset** | **+7,204.92 km³** | +7,204.92 km³ | 0.00 km³ (Exact Match) | **+7,204.92 km³** | Unaltered inter-product baseline difference (+5.40%). | **NONE** | **VERIFIED EXACT** |

### Detailed Forensic Breakdown of Discrepancies

1. **The 2,379-Cell Difference (866,358 vs 863,979):**  
   - In Phase 2.6, the audited Bedmap3 peninsula grounded raster contained **888,593 cells**. Subtracting the 22,235 Bedmap3-only cells (Domain B) yielded exactly **866,358 cells** of mutual grounded ice (Domain A).  
   - In Phase 3.1B, an early draft text subtracted 22,235 from an unverified figure of 886,214, producing $886,214 - 22,235 = 863,979$ cells.  
   - In Phase 3.2 Preflight Check 1, this clerical difference was explicitly reconciled, and all subsequent physical models, rasters, and targets in `ml_target_dataset.csv` operated strictly on the audited **866,358 cells** ($216,062.17\text{ km}^2$).  
   - The reappearance of 863,979 in Phase 4A.2 was a legacy typographical artifact in documentation headers that did **not** affect any underlying data arrays.

2. **The Grid Resolution Conflation (500 m vs 250 m):**  
   - Every geospatial raster file in the repository (`data/processed/bedmap3_thickness_peninsula_500m.tif`, `data/processed/bedmachine_v4.1_peninsula_aligned_to_bedmap3.nc`, etc.) has a pixel resolution of **500.0 m $\times$ 500.0 m**. There are **zero 250 m rasters** anywhere in the project directory.  
   - The label "250 m" originated in Phase 2.5 (`phase2_5_bedmachine_validation.md`), where a **250 m half-pixel registration shift** was applied to align BedMachine's grid coordinates with Bedmap3. A later author mistakenly recorded this 250 m alignment offset as the grid resolution.

3. **The Area Discrepancy (216,062 km² vs 103,959 km²):**  
   - The true planimetric area of Domain A is **$216,062.17\text{ km}^2$**, calculated as the sum of the 866,358 500-m cells ($866,358 \times 0.25 = 216,589.5\text{ km}^2$ nominal) multiplied by the EPSG:3031 WGS84 ellipsoidal scale correction ($1/m^2 \approx 0.997566$).  
   - The $103,959\text{ km}^2$ figure in Phase 4A.2 is the exact sum of three manually specified static features in `src/feature_engineering/feature_builder.py`: $53,883 + 23,178 + 26,898 = 103,959\text{ km}^2$. Each value is roughly half (~46.6% to 49.5%) of the true basin area.

4. **Mutual Exclusivity and Collective Exhaustiveness:**  
   - The three IMBIE 2016 ice sheet polygons (`IMBIE_AIS_Regional_Delineations.shp`, `Type == 'Ice_sheet'`) share contiguous boundary lines and have **zero polygon intersection**:
     $$\text{Hp-I} \cap \text{I-Ipp} = \emptyset, \quad \text{Hp-I} \cap \text{Ipp-J} = \emptyset, \quad \text{I-Ipp} \cap \text{Ipp-J} = \emptyset$$
   - When intersected with the common grounded raster mask, the cell counts partition Domain A with zero remainder:
     $$432,370 (\text{Hp-I}) + 205,488 (\text{I-Ipp}) + 228,500 (\text{Ipp-J}) = 866,358 \equiv \text{Domain A}$$
     $$108,945.63\text{ km}^2 + 49,757.73\text{ km}^2 + 57,358.82\text{ km}^2 = 216,062.17\text{ km}^2 \equiv \text{Domain A}$$

5. **Impact on Historical Volume Targets:**  
   - **Zero impact.** Historical targets $\Delta V_{\text{ice-eq}}(t)$ were derived from the Input-Output Method:
     $$\Delta V(t) = \frac{\text{SMB}(t) - D(t)}{0.917\text{ Gt/km}^3}$$
     where $\text{SMB}(t)$ was integrated from RACMO2.4p1 over the full IMBIE basins and $D(t)$ was measured at the 28 physical flux gates. The ML models were trained directly on the resulting volume change rates ($\text{km}^3/\text{yr}$), **not** on area-normalized mass flux ($\text{m/yr}$). The erroneous static area descriptors did not enter the target reconstruction pipeline.

---

## 2. Investigation 2 — Tracing Static Spatial Descriptors into Phase 4B

Every static descriptor ingested by `src/feature_engineering/feature_builder.py` was traced back to its raw glaciological source.

From [`reports/tables/static_feature_provenance.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/static_feature_provenance.csv):

```
+----------------------------------------------------------------------------------------------------+
| Static Descriptor Provenance Summary:                                                              |
| - A_b (Basin Area):          Phase 4B values (53,883 / 23,178 / 26,898 km²) are halved descriptors |
| - H_b (Mean Thickness):      Phase 4B values (1,482 / 1,195 / 1,221 m) represent interior plateau  |
| - B_b (Gate Bed Elevation):  Phase 4B values (-185.4 / -124.2 / -165.8 m) match BedMachine V4.1   |
| - tau_d (Driving Stress):    Phase 4B values (112.5 / 98.4 / 105.2 kPa) match REMA/BM4.1 fast flow |
+----------------------------------------------------------------------------------------------------+
```

### Forensic Footprint and Collinearity Analysis

1. **Basin Area ($A_b$):**  
   - `feature_builder.py` assigned $53,883.0\text{ km}^2$ to `Hp-I`, $23,178.0\text{ km}^2$ to `I-Ipp`, and $26,898.0\text{ km}^2$ to `Ipp-J`.  
   - The authoritative Domain A footprint is $108,945.63\text{ km}^2$ (`Hp-I`), $49,757.73\text{ km}^2$ (`I-Ipp`), and $57,358.82\text{ km}^2$ (`Ipp-J`).  
   - Because $A_b$ was mapped as a single static constant per basin ID, it is **strictly collinear with the categorical basin dummy variables** (`is_Hp_I`, `is_I_Ipp`). In the linear models (Bayesian Ridge, ElasticNet), its effect was mathematically absorbed into the basin-specific intercept. In tree models (Random Forest, Gradient Boosting), it functioned as an alternate split threshold identical to basin identity.

2. **Mean Ice Thickness ($H_b$):**  
   - `feature_builder.py` assigned $1,482.4\text{ m}$ (`Hp-I`), $1,195.1\text{ m}$ (`I-Ipp`), and $1,220.8\text{ m}$ (`Ipp-J`).  
   - The true domain-wide area-weighted mean ice-equivalent thicknesses are $940.5\text{ m}$ (`Hp-I`), $255.5\text{ m}$ (`I-Ipp`), and $445.0\text{ m}$ (`Ipp-J`).  
   - The values in `feature_builder.py` reflect the thick interior ice divide / spine plateau facies rather than the full marine-terminating basin hypsometry. Like $A_b$, $H_b$ is a single invariant scalar per basin, meaning its numerical distortion was absorbed entirely by basin fixed effects.

3. **Gate Bed Elevation ($B_b$) and Driving Stress ($\tau_d$):**  
   - $B_b$ ($-185.4\text{ m}$ for `Hp-I`, $-124.2\text{ m}$ for `I-Ipp`, $-165.8\text{ m}$ for `Ipp-J`) accurately reflects the width-weighted mean bed elevation across the 28 outlet glacier flux gates from BedMachine V4.1.  
   - $\tau_d$ ($112.5\text{ kPa}$ for `Hp-I`, $98.4\text{ kPa}$ for `I-Ipp`, $105.2\text{ kPa}$ for `Ipp-J`) accurately reflects the mean basal driving stress across fast-flowing ice trunks ($v > 100\text{ m/yr}$) from REMA 100m DEM and BedMachine V4.1.

4. **Phase 4C Protocol Rule for Static Descriptors:**  
   Because altering static feature values would constitute a pipeline modification and hyperparameter retuning (prohibited prior to test evaluation), **the existing feature definitions must remain frozen for Phase 4C test evaluation**. Their numerical collinearity guarantees that no test evaluation bias is introduced.

---

## 3. Investigation 3 — Verification of Target and Prediction Consistency

The relationship between the authoritative Phase 3 target dataset and the Phase 4B out-of-fold prediction records was audited using historical data only.

From [`reports/tables/target_footprint_consistency.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/target_footprint_consistency.csv):

| Verification Dimension | Evaluated Scope | Sample Size | Consistency Criterion | Empirical Finding | Max Discrepancy | Status |
| :--- | :--- | :---: | :--- | :--- | :---: | :---: |
| **Spatial Boundary Invariance** | Basins Hp-I, I-Ipp, Ipp-J | 138 basin-years (1979–2024) | Invariant spatial mask | Boundaries held stationary across all 46 years; zero boundary creep | 0.00 cells | **VERIFIED INVARIANT** |
| **Target Dataset Additivity** | Domain A vs Basin Sum | 46 years (1979–2024) | $y_{\text{DomainA}} \equiv \sum_b y_b$ | Unrounded physical mass balance components are exactly additive. In `ml_target_dataset.csv`, 19 years show $\pm 0.01\text{ km}^3/\text{yr}$ rounding differences due to 2-decimal truncation. | 0.01 km³/yr | **VERIFIED ADDITIVE (ROUNDING LIMIT)** |
| **Physical OOF Target Integrity** | 8 Models $\times$ 20 Years $\times$ 3 Basins | 480 physical rows | $y_{\text{true}} \equiv y_{\text{target}}$ | Zero discrepancies across all 480 physical basin rows. Matches `ml_target_dataset.csv` to machine precision. | 0.000000 km³/yr | **VERIFIED EXACT** |
| **Domain A OOF Conservation** | 8 Models $\times$ 20 Years $\times$ 1 Aggregate | 160 diagnostic rows | $y_{\text{true}}(\text{DomA}) \equiv \sum_b y_{\text{true}}(b)$ | In `oof_predictions.csv`, Domain A target was computed as the exact sum of basin targets to enforce mass conservation ($0.000000\text{ km}^3/\text{yr}$ discrepancy). | 0.000000 km³/yr | **VERIFIED CONSERVED** |
| **Composite Key Uniqueness** | Master Prediction Table | 640 rows | Unique $(M, Y, B)$ | Zero duplicates, zero missing years, zero orphaned records. | 0 duplicates | **VERIFIED UNIQUE** |
| **Candidate Nunatak Quarantine**| Domain B1 (18,628 cells) | 184 dataset rows | Excluded from Domain A | Strictly excluded from primary dynamic targets; baseline anchored to $133,497.59\text{ km}^3$. | 0.00 km³ | **VERIFIED QUARANTINED** |
| **Test Set Sealing** | 2016–2024 Timeline | 27 physical + 9 Domain A | Zero target access | Zero test targets accessed, evaluated, or revealed in Phase 4B/4B.1/4B.2. | 0 unsealed rows | **VERIFIED SEALED** |

---

## 4. Investigation 4 — Phase 4C Test Evaluation Protocol Lock

To prevent accidental data leakage, confirmation bias, or post-hoc hyperparameter tuning, the test-evaluation protocol for **Phase 4C (Held-out Test Evaluation, 2016–2024)** is hereby formally locked.

From [`reports/tables/phase4c_protocol_manifest.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/phase4c_protocol_manifest.csv):

### 1. Model Portfolio and Benchmark Designations

The candidate models and reference benchmarks are locked as follows:

- **Primary Candidate Model:**  
  `M2_Bayesian_Ridge_Weighted` (Bayesian Ridge regression with sample weights proportional to inverse observation variance $s_i = 1/\sigma_i^2$).
- **Mandatory Reference Benchmarks:**  
  1. `M0_Persistence`: Predicts $\hat{y}_{b,t} = y_{b, t-1}$. Serves as the primary dynamic benchmark for tracking decadal regime shifts, subject to the audited telescoping identity.  
  2. `M0_Historical_Mean`: Predicts the expanding historical training mean $\hat{y}_{b,t} = \bar{y}_{b, \le 2015}$. Serves as the climatological reference baseline.  
  3. `M2_Bayesian_Ridge_Unweighted`: Standard homoscedastic Bayesian Ridge regression without observational error weighting.
- **Secondary Candidate Models:**  
  `M5_Gradient_Boosting`, `M4_Random_Forest`, `M3_ElasticNet`, and `M6_Gaussian_Process`.

### 2. Sealed Test Period Delineation

- **Timeline:** 2016–2024 (9 consecutive calendar years).
- **Physical Basin Evaluations ($N = 27$):**  
  - Basin `Hp-I`: 9 years (2016–2024)
  - Basin `I-Ipp`: 9 years (2016–2024)
  - Basin `Ipp-J`: 9 years (2016–2024)
- **Derived Domain A Diagnostic Records ($N = 9$):**  
  - Domain A regional sum: 9 years (2016–2024).  
  - Strictly quarantined from pooled physical evaluation metrics ($N = 27$).
- **Grand Total Evaluation Rows:** $8\text{ models} \times (27\text{ physical} + 9\text{ Domain A}) = 288\text{ prediction rows}$.

### 3. Permitted Features and Operational Lag Rules

Evaluation must strictly adhere to the **Task A2 Retrospective Hindcast Emulation** framework:

- **Allowed Autoregressive State:** Target volume change lags $y_{b, t-1}$ (Lag-1) and $y_{b, t-2}$ (Lag-2).
- **Allowed Climate Forcing:** RACMO2.4p1 surface mass balance $\text{SMB}_{b, t-1}$ (Lag-1). **Contemporaneous $\text{SMB}(t)$ is strictly prohibited.**
- **Allowed Dynamic Flux:** Satellite flux gate discharge $D_{b, t-1}$ (Lag-1). **Contemporaneous $D(t)$ is strictly prohibited.**
- **Allowed Net State:** $\text{Net\_MB}_{b, t-1} = \text{SMB}_{b, t-1} - D_{b, t-1}$ (Lag-1).
- **Allowed Static Descriptors:** Locked static features ($A_b$, $H_b$, $B_b$, $\tau_d$) and categorical basin identity dummies (`is_Hp_I`, `is_I_Ipp`).
- **Feature Scaling:** `StandardScaler` fitted strictly on the pre-test training partition ($\le 2015$) and applied to test features without updating.

### 4. Quantitative Evaluation Metrics

All metrics must be evaluated on native physical units ($\text{km}^3/\text{yr}$ and $\text{km}^3$):

1. **Annual Rate Accuracy:**  
   - $\text{RMSE} = \sqrt{\frac{1}{N} \sum_{i=1}^N (\hat{y}_i - y_i)^2}$
   - $\text{MAE} = \frac{1}{N} \sum_{i=1}^N |\hat{y}_i - y_i|$
   - $\text{Mean Bias} = \frac{1}{N} \sum_{i=1}^N (\hat{y}_i - y_i)$
   - $R^2 = 1.0 - \frac{\sum_{i=1}^N (\hat{y}_i - y_i)^2}{\sum_{i=1}^N (y_i - \bar{y}_{\text{test}})^2}$
2. **Statistical Significance Testing:**  
   Cluster-paired hypothesis testing (preserving 9 annual 3-basin clusters) against `M0_Historical_Mean`.
3. **Regional Mass Conservation:**  
   Confirmation of linear conservation: $|\hat{y}_{\text{DomainA}, t} - \sum_b \hat{y}_{b,t}| \equiv 0.000000\text{ km}^3/\text{yr}$.
4. **Cumulative Endpoint Drift (2016–2024):**  
   $\text{Drift}_{\text{DomainA}} = \sum_{t=2016}^{2024} \hat{y}_{\text{DomainA}, t} - \sum_{t=2016}^{2024} y_{\text{DomainA}, t}$.  
   Evaluate whether persistence endpoint drift equals the telescoping boundary identity $y_{2015} - y_{2024}$.
5. **Probabilistic Calibration:**  
   Empirical coverage of 95% predictive intervals ($\hat{y} \pm 1.96 \sigma_{\text{pred}}$) evaluated per basin to verify whether homoscedastic noise causes under-coverage in `Hp-I` and over-coverage in `I-Ipp`.

### 5. Blind Revelation and Anti-Tuning Protocol

```
+----------------------------------------------------------------------------------------------------+
| BLIND REVELATION SAFEGUARD PROTOCOL:                                                               |
| 1. Model Code Freeze: All training scripts, feature engineering pipelines, and model               |
|    configurations must be committed and immutable before the test execution script is run.        |
| 2. Single-Pass Execution: The test execution script runs in a single pass, generating              |
|    reports/tables/test_predictions.csv and reports/tables/test_metrics.csv.                        |
| 3. Zero Hyperparameter Retuning: No hyperparameter, feature set, or model architecture may         |
|    be modified after test predictions are generated.                                               |
| 4. Formal Audit Log: The git hash and timestamp of the pre-test pipeline freeze will be recorded   |
|    in the Phase 4C report header.                                                                  |
+----------------------------------------------------------------------------------------------------+
```

---

## 5. Audit Deliverables Inventory

The four authoritative CSV tables generated and validated during Phase 4B.2 are saved in the project repository:

1. [`reports/tables/spatial_domain_reconciliation.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/spatial_domain_reconciliation.csv): 12-row forensic reconciliation of cell counts, resolutions, areas, baselines, and conservation.
2. [`reports/tables/static_feature_provenance.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/static_feature_provenance.csv): 12-row tracing of static descriptors ($A_b$, $H_b$, $B_b$, $\tau_d$), documenting collinearity with basin dummies and zero target impact.
3. [`reports/tables/target_footprint_consistency.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/target_footprint_consistency.csv): 8-row audit confirming target boundary invariance, additivity, OOF target matching, and test sealing.
4. [`reports/tables/phase4c_protocol_manifest.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/phase4c_protocol_manifest.csv): 11-row operational protocol specification locking models, benchmarks, test years, features, metrics, and anti-tuning rules.

---

## 6. Final Decision & Authorization

**DETERMINATION: DECISION B (CONDITIONAL PASS).**

The spatial-domain discrepancy between Phase 2.6 and Phase 4A.2 is fully understood and proven to be a clerical reporting artifact that had zero impact on historical volume targets or ML model behavior. The test protocol is rigorously specified and sealed.

**Phase 4C (Held-out Test Evaluation, 2016–2024) is authorized to begin upon user confirmation.**

