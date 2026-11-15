# Phase 5 — Stage 3B: Controlled Physical Parameter Calibration Protocol & Authorization Request
**Authoritative Protocol Specification, Prior Provenance, and Verification Architecture**  
**Project:** Antarctic Ice Volume Prediction — Phase 5 Physical Baseline Model  
**Date:** 2026-11-09  
**Status:** Protocol Submitted for Reviewer Authorization | Calibration Execution Strictly Locked  

---

## Executive Summary

This document submits the formal **Stage 3B Controlled Physical Parameter Calibration Protocol** for independent reviewer authorization. It synthesizes the methodological resolutions achieved in Stages 3A, 3A.1, 3A.2, 3A.3, and 3A.3.1 into a rigorous, well-posed inverse modeling framework.

### Status and Governance Attestation
- **No calibration simulations have been executed.** All physical parameters remain frozen at their Stage 2 baseline values.
- **Previous audits are not restarted**, and the physical solver architecture is fully preserved.
- **Domain A is preserved exactly:** $866,358\text{ cells}$, $216,062.17\text{ km}^2$, $\Delta x = 500\text{ m}$.
- **Machine learning residual training, ISMIP6 tuning, SSP interpolation, and forward projections to 2100 remain strictly prohibited.**
- **Calibration will not commence until explicit, written reviewer authorization is granted.**

---

## 1. Final Methodological Closure Amendment

Prior to establishing the calibration protocol, three final methodological clarifications are formally codified:

### 1.1 Formal Resolution of the Flanders Offset Sign Convention
To eliminate all directional ambiguity, the along-flow coordinate frame and displacement vectors for the Flanders Bay outlet (`FL_IIPP_01_OUTLET`, Leonardo Glacier) are explicitly defined:
- **Coordinate System:** One-dimensional curvilinear distance along the thalweg streamline, with origin $x = 0$ at the ice divide. Downstream direction is $+x$.
- **Observational Gate Location:** Observational flux gate line `GATE_IPP_01` along-flow projection is at $x_\text{obs} = \mathbf{14.08304\text{ km}}$ ($14,083.04\text{ m}$).
- **Model Gate Cell Center:** Finite-volume Cell 28 center is at $x_{28} = \mathbf{14.25000\text{ km}}$ ($14,250.00\text{ m}$).
- **Local Velocity Gradient:** $\frac{\partial u}{\partial x} = \mathbf{-0.56146\text{ yr}^{-1}}$ (ice decelerates downstream into the fjord trough).

#### Explicit Directional Transformations:
1. **Displacement of Observational Gate Relative to Model Cell 28:**
   $$\Delta x_\text{obs \leftarrow cell28} = x_\text{obs} - x_{28} = 14,083.04 - 14,250.00 = \mathbf{-166.96\text{ m}} \quad (\text{UPSTREAM})$$
   Velocity change moving upstream from Cell 28 to the gate:
   $$\Delta u = \frac{\partial u}{\partial x} \cdot \Delta x = (-0.56146\text{ yr}^{-1}) \times (-166.96\text{ m}) = \mathbf{+93.74\text{ m/yr}}$$
   $$u(x_\text{obs}) = u(x_{28}) + \Delta u = 175.85 + 93.74 = \mathbf{269.59\text{ m/yr}}$$

2. **Displacement of Model Cell 28 Relative to Observational Gate:**
   $$\Delta x_\text{cell28 \leftarrow obs} = x_{28} - x_\text{obs} = 14,250.00 - 14,083.04 = \mathbf{+166.96\text{ m}} \quad (\text{DOWNSTREAM})$$
   Velocity change moving downstream from the gate to Cell 28:
   $$\Delta u = \frac{\partial u}{\partial x} \cdot \Delta x = (-0.56146\text{ yr}^{-1}) \times (+166.96\text{ m}) = \mathbf{-93.74\text{ m/yr}}$$
   $$u(x_{28}) = u(x_\text{obs}) + \Delta u = 269.59 - 93.74 = \mathbf{175.85\text{ m/yr}}$$

Both transformations are mathematically identical and physically consistent: moving downstream decreases velocity; moving upstream increases velocity.

### 1.2 Distinction Between Theoretical Bounds and Sensitivity Assumptions for $\mu$
The buttressing exponent $\mu$ enters the grounding-line flux reduction factor via $\mathcal{R}_\text{buttress} = [1 - \omega_b \theta]^\mu$. A strict epistemological boundary is established between its theoretical basis and numerical sensitivity testing:
1. **Theoretically Derived Boundary-Layer Exponent ($\mu = 1.583$):**  
   Derived by Schoof (2007, *J. Geophys. Res.*, Eq. 32) from boundary-layer matched asymptotics for 1D ice flow across a grounding line over a sloping bed with Weertman-type sliding ($m = 1/3$):
   $$\mu_\text{Schoof} = \frac{m+1}{m+2} \times \frac{n+1}{n} = \frac{4/3}{7/3} \times \frac{4}{3} \times \dots = \mathbf{1.5833} \quad (19/12)$$
   This value represents the authoritative physical invariant for laminar power-law ice sliding.
2. **General Thin-Film Theoretical Bounds ($\mu \in [1.0, 2.0]$):**  
   Gudmundsson (2013) and Pegler (2018) demonstrate that for general lateral shear geometry, the effective exponent ranges from $\mu = 1.0$ (pure membrane back-stress in wide embayments) to $\mu = 2.0$ (quadratic lateral wall friction in parabolic channels).
3. **Analyst Sensitivity Exploration Range ($\mu \in [2.0, 2.25]$):**  
   The range $\mu \in [2.0, 2.25]$ is an **analyst sensitivity assumption**, evaluated strictly to test model response under extreme channel lateral confinement. It is **not a physical invariant** and will not be treated as a prior parameter distribution during calibration.
   - **Calibration Decision:** The buttressing exponent will be held fixed at its authoritative theoretical invariant $\mu = 1.583$ during Stage 3B.

### 1.3 Preservation of the Flanders Calibration Exclusion
Because finite-volume cell centers on the frozen 500 m grid cannot resolve the sub-grid ice-fall transition without sub-grid line integration:
- The Flanders Bay gate velocity (`GATE_IPP_01`, $210 \pm 12\text{ m/yr}$) is **STRICTLY EXCLUDED** from the Stage 3B calibration target set.
- Tuning basal friction $C_\text{bed}$ against Flanders Bay observations is **STRICTLY PROHIBITED**.
- Flanders Bay is reserved exclusively as a forward structural benchmark once sub-grid numerical integration is implemented.

---

## 2. Proposed Stage 3B Calibration Scope & Sequential Hierarchy

To guarantee well-posedness and avoid simultaneous parameter trade-offs, Stage 3B adopts a **strict sequential decoupling hierarchy**:

```
[Step 1: Basal Friction Inversion]
    Invert for log10(C_bed) on Ryder & Crane using profile InSAR velocities.
    Keep C_schoof fixed at benchmark (0.61) and theta_buttress fixed.
          │
          ▼
[Step 2: Basal Friction Parameter Freeze]
    Freeze accepted C_bed,HpI* and C_bed,IppJ*.
    Verify convergence, condition number, and posterior variance.
          │
          ▼
[Step 3: Grounding-Line Flux Identifiability]
    Evaluate if C_schoof in [0.30, 1.50] can be uniquely identified 
    using independent regional discharge constraints (Rignot 2019).
          │
          ▼
[Step 4: Buttressing Parameter Constraint]
    Hold theta_buttress fixed at known physical limits (Crane=0.0, Ryder=1.0).
    Simultaneous multi-parameter optimization is strictly banned.
```

### Potential Calibration Sequence:
1. **Sequence Step 1 — Basal Friction Parameter ($C_\text{bed}$):**
   - Calibrate $C_\text{bed}$ using only independently supported, spatially matched velocity profiles from ITS_LIVE / MEaSUREs on unconfined flowlines (`FL_HPI_01` and `FL_IPPJ_02`).
   - Treat Palmer Land West (`Hp-I`) and Graham Land East (`Ipp-J`) as distinct lithological domains:
     - Hypothesis A: Single regional $C_\text{bed}$ across Graham Land.
     - Hypothesis B: Domain-specific $C_\text{bed,HpI}$ and $C_\text{bed,IppJ}$.
2. **Sequence Step 2 — Basal Friction Parameter Freeze:**
   - Formally freeze calibrated $C_\text{bed}^*$ values. Basal parameters are never re-adjusted during subsequent steps.
3. **Sequence Step 3 — Grounding-Line Bulk Parameter ($C_\text{schoof}$):**
   - Evaluate whether $C_\text{schoof}$ can be uniquely identified from regional ice discharge constraints ($D_\text{basin} \pm \sigma$) under frozen $C_\text{bed}^*$.
4. **Sequence Step 4 — Buttressing State ($\theta_\text{buttress}$):**
   - Keep $\theta_\text{buttress}$ fixed at known boundary states ($\theta = 0.0$ on unbuttressed Crane; $\theta = 1.0$ on intact Ryder). Simultaneous optimization of $(C_\text{bed}, C_\text{schoof}, \theta_\text{buttress})$ is strictly prohibited.

The observation-to-parameter mapping is compiled in [`phase5_stage3B_observation_mapping.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/phase5_stage3B_observation_mapping.csv).

---

## 3. Parameter Bounds and Prior Provenance

All calibration parameters are governed by literature-derived physical bounds, nominal priors, and documented uncertainties:

| Parameter | Symbol | Units | Lower Bound | Prior Mode | Upper Bound | Prior Distribution | Primary Literature Citations | Glaciological Role |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- | :--- |
| **Basal Friction** | $\log_{10} C_\text{bed}$ | $\log_{10}(\text{Pa}\cdot(\text{m/s})^{-1/3})$ | $5.0$ ($10^5$) | $7.0$ ($10^7$) | $8.0$ ($10^8$) | $\mathcal{N}(7.0, 0.5^2)$ | Cuffey & Paterson (2010); Morlighem et al. (2010); Pattyn et al. (2012) | Spans lubricated till ($10^5$) to hard crystalline bed ($10^8$) |
| **Grounding-Line Flux** | $C_\text{schoof}$ | Dimensionless | $0.30$ | $0.61$ | $1.50$ | $\ln C_\text{schoof} \sim \mathcal{N}(\ln(0.61), 0.35^2)$ | Pattyn et al. (2012, MISMIP); Gladstone et al. (2012); Pattyn (2013) | Empirical 1D bulk flux factor accommodating channel shear |
| **Buttressing State** | $\theta_\text{buttress}$ | Dimensionless | $0.00$ | $0.0$ / $1.0$ | $1.00$ | Fixed discrete boundary state | Rignot et al. (2004); Scambos et al. (2004); Rott et al. (2011) | $0.0 = \text{unbuttressed post-collapse}$; $1.0 = \text{intact shelf}$ |
| **Back-Stress Fraction** | $\omega_b$ | Dimensionless | $0.40$ | $0.75$ | $0.85$ | Fixed nominal constant ($0.75$) | Pegler (2018); Reese et al. (2018); Gudmundsson (2013) | Embayment lateral back-stress transfer fraction |
| **Buttressing Exponent**| $\mu$ | Dimensionless | $1.00$ | $1.583$ | $2.00$ | Fixed analytical invariant ($1.583$) | Schoof (2007, Eq. 32); Gudmundsson (2013) | Asymptotic boundary-layer matched power ($m=1/3$) |

The complete parameter ledger is documented in [`phase5_stage3B_parameter_bounds.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/phase5_stage3B_parameter_bounds.csv).

---

## 4. Objective Function & Uncertainty Methodology

### 4.1 Dimensionally Consistent Objective Function
The inverse problem is formulated as a regularized non-linear generalized least-squares minimization:
$$\mathcal{J}(\mathbf{m}) = \frac{1}{2} \left[ \mathbf{d}_\text{obs} - \mathcal{F}(\mathbf{m}) \right]^T \mathbf{C}_d^{-1} \left[ \mathbf{d}_\text{obs} - \mathcal{F}(\mathbf{m}) \right] + \frac{\lambda}{2} \left[ \mathbf{m} - \mathbf{m}_\text{prior} \right]^T \mathbf{C}_m^{-1} \left[ \mathbf{m} - \mathbf{m}_\text{prior} \right]$$

- **Dimensionality:** Both misfit and regularization terms are normalized by covariance, rendering $\mathcal{J}(\mathbf{m})$ **strictly dimensionless** ($\chi^2$-statistic).
- **Inversion Space:** $\mathbf{m} = \log_{10}(C_\text{bed})$. Log-transformation enforces strict positivity ($C_\text{bed} > 0$) and stabilizes numerical optimization across 3 orders of magnitude.
- **Forward Operator:** $\mathcal{F}(\mathbf{m})$ solves the non-linear 1D SSA momentum equation to compute depth-integrated horizontal ice velocity $u(x)$ $[\text{m/yr}]$.

### 4.2 Observation-Error Covariance Model ($\mathbf{C}_d$)
The data covariance matrix is diagonal, with individual observation variance defined by:
$$\sigma_{d,i}^2 = \sigma_\text{inst,i}^2 + \sigma_\text{repr,i}^2$$
- **Instrumental Radar Phase Uncertainty ($\sigma_\text{inst,i}$):** $\pm 15.0\text{ m/yr}$ (InSAR speckle tracking and bedrock tie-point drift from ITS_LIVE / MEaSUREs).
- **Grid Representativeness Uncertainty ($\sigma_\text{repr,i}$):** $\pm 10.0\text{ m/yr}$ (cross-sectional velocity shear across finite-volume cell width $W$).
- **Combined Standard Error:** $\sigma_{d,i} = \sqrt{15^2 + 10^2} = \mathbf{18.03\text{ m/yr}}$.

### 4.3 Prior Covariance ($\mathbf{C}_m$) and Regularization Parameter ($\lambda$)
- Prior standard deviation: $\sigma_m = 0.50$ in $\log_{10}$ space (representing an allowable half-order of magnitude prior variation).
- Regularization weighting $\lambda$ is chosen via the **Discrepancy Principle** such that the reduced chi-squared statistic satisfies:
  $$\frac{\chi^2}{N_\text{obs}} = \frac{1}{N_\text{obs}} \left[ \mathbf{d}_\text{obs} - \mathcal{F}(\mathbf{m}^*) \right]^T \mathbf{C}_d^{-1} \left[ \mathbf{d}_\text{obs} - \mathcal{F}(\mathbf{m}^*) \right] \approx 1.0 \pm \sqrt{\frac{2}{N_\text{obs}}}$$

### 4.4 Posterior Uncertainty & Identifiability Quantification
At the optimal parameter $\mathbf{m}^*$, the posterior covariance is evaluated from the sensitivity Jacobian $\mathbf{J} = \frac{\partial \mathcal{F}}{\partial \mathbf{m}}$:
$$\mathbf{C}_\text{post} = \left( \mathbf{J}^T \mathbf{C}_d^{-1} \mathbf{J} + \lambda \mathbf{C}_m^{-1} \right)^{-1}$$
Posterior $95\%$ confidence intervals are formally reported as:
$$\mathbf{m}^* \pm 1.96 \sqrt{\operatorname{diag}(\mathbf{C}_\text{post})}$$

The objective function formulation is documented in [`phase5_stage3B_objective_formulation.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/phase5_stage3B_objective_formulation.csv).

---

## 5. Strict Calibration / Validation Separation

To maintain strict scientific integrity, calibration observations are **NEVER reused for validation**:

```
CALIBRATION DATASET (Inversion Only)
├── FL_HPI_01 (Ryder Glacier Trunk Velocity Profile) ──> Invert for C_bed,HpI*
└── FL_IPPJ_02 (Crane Glacier Post-Collapse Profile) ──> Invert for C_bed,IppJ*

INDEPENDENT VALIDATION DATASET (Blind Forward Evaluation Only)
├── FL_HPI_02 (Millett / Dyer Glacier, Basin Hp-I)  ──> Blind Spatial Transfer
├── FL_IPPJ_03 (Flask / Leppard Glacier, Larsen C)  ──> Blind Buttressed Transfer
├── FL_IPPJ_01 (Drygalski Glacier, Larsen A)        ──> Blind Unbuttressed Transfer
└── Regional Mass Budget (IMBIE3 / Rignot 2019)     ──> Regional Mass Closure

STRICT EXCLUSION BENCHMARK (Locked Out of Both Sets at 500 m Resolution)
└── FL_IIPP_01 (Flanders Bay Gate Velocity 210 m/yr) ──> Sub-grid Integration Required
```

### Partitioning Rules:
1. **Calibration Flowlines:** Only `FL_HPI_01` and `FL_IPPJ_02` enter the objective function.
2. **Blind Validation Flowlines:** `FL_HPI_02`, `FL_IPPJ_03`, and `FL_IPPJ_01` are simulated using optimal parameters $C_\text{bed}^*$ without any tuning. Validation metrics (RMSE, mean bias, Nash-Sutcliffe efficiency) are computed independently.
3. **Regional Mass Budget Closure:** Simulated grounding-line discharge across all 8 flowlines is compared against independent regional discharge observations ($D_\text{basin} \pm \sigma$).
4. **Flanders Bay:** Formally excluded from both calibration and validation scorecards at 500 m grid resolution.

The data partitioning ledger is compiled in [`phase5_stage3B_calibration_validation_split.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/phase5_stage3B_calibration_validation_split.csv).

---

## 6. Mandatory Controls & Stop Conditions

The calibration routine will immediately abort execution if any of the following mandatory control thresholds are triggered:

1. **Parameter Boundary Pegging:** If any parameter reaches within $1\%$ of its allowable bounds ($\log_{10} C_\text{bed} \le 5.01$ or $\ge 7.99$; $C_\text{schoof} \le 0.31$ or $\ge 1.49$).
2. **Severe Ill-Conditioning:** If the Hessian matrix condition number exceeds $\kappa(\mathbf{H}) > 100.0$, indicating strong parameter degeneracy.
3. **Non-Convergence of Momentum Solver:** If the non-linear Picard SSA solver fails to achieve relative residual $< 1.0 \times 10^{-4}$ within 80 iterations.
4. **Mass Conservation Violation:** If the finite-volume continuity solver relative mass balance error exceeds $|\Delta M - (\text{SMB} - Q_\text{GL})| / M_\text{init} > 1.0 \times 10^{-4}$.
5. **Physical Flotation Violation:** If simulated ice thickness drops below zero ($H \le 0$) or violates hydrostatic flotation at marine grounding-line cells.
6. **Lack of Independent Authorization:** Execution will not commence without explicit reviewer approval of this protocol.

The full risk management and control matrix is documented in [`phase5_stage3B_risk_register.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/phase5_stage3B_risk_register.csv).

---

## 7. Deliverables Manifest & Checksums

All deliverables for the Stage 3B Authorization Request have been compiled and mirrored:

| Deliverable Name | File Type | Workspace File Link | Brain Artifact Link | SHA-256 Checksum |
| :--- | :---: | :--- | :--- | :--- |
| **Stage 3B Calibration Protocol** | Markdown | [`reports/phase5_stage3B_calibration_protocol.md`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/phase5_stage3B_calibration_protocol.md) | [`brain/phase5_stage3B_calibration_protocol.md`](file:///c:/Users/akash/.gemini/antigravity/brain/52ad6ae8-887d-48db-85e7-7d53f431979f/phase5_stage3B_calibration_protocol.md) | *Recorded in `phase5_stage3B_file_hashes.csv`* |
| **Observation Mapping Table** | CSV | [`reports/tables/phase5_stage3B_observation_mapping.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/phase5_stage3B_observation_mapping.csv) | [`brain/tables/phase5_stage3B_observation_mapping.csv`](file:///c:/Users/akash/.gemini/antigravity/brain/52ad6ae8-887d-48db-85e7-7d53f431979f/tables/phase5_stage3B_observation_mapping.csv) | `291f6749cdb49604c71b54d20b4d33911753eba4d72f1d5524184f6b87cf75aa` |
| **Parameter Bounds Ledger** | CSV | [`reports/tables/phase5_stage3B_parameter_bounds.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/phase5_stage3B_parameter_bounds.csv) | [`brain/tables/phase5_stage3B_parameter_bounds.csv`](file:///c:/Users/akash/.gemini/antigravity/brain/52ad6ae8-887d-48db-85e7-7d53f431979f/tables/phase5_stage3B_parameter_bounds.csv) | `8d841e582a18717097ead396a02130a5b2abfdcd2adabb2982beb3d1b3260312` |
| **Objective Formulation Table** | CSV | [`reports/tables/phase5_stage3B_objective_formulation.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/phase5_stage3B_objective_formulation.csv) | [`brain/tables/phase5_stage3B_objective_formulation.csv`](file:///c:/Users/akash/.gemini/antigravity/brain/52ad6ae8-887d-48db-85e7-7d53f431979f/tables/phase5_stage3B_objective_formulation.csv) | `4020ce26890d3003bd1cb96cd2be9ce5fec0be5d905032acc839b7b4deb7c3fe` |
| **Calibration/Validation Split** | CSV | [`reports/tables/phase5_stage3B_calibration_validation_split.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/phase5_stage3B_calibration_validation_split.csv) | [`brain/tables/phase5_stage3B_calibration_validation_split.csv`](file:///c:/Users/akash/.gemini/antigravity/brain/52ad6ae8-887d-48db-85e7-7d53f431979f/tables/phase5_stage3B_calibration_validation_split.csv) | `6679addc643908fe79a4988fbd979316c6e37fb2a7b3fdbacbb4bfce1ab20446` |
| **Updated Risk Register** | CSV | [`reports/tables/phase5_stage3B_risk_register.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/phase5_stage3B_risk_register.csv) | [`brain/tables/phase5_stage3B_risk_register.csv`](file:///c:/Users/akash/.gemini/antigravity/brain/52ad6ae8-887d-48db-85e7-7d53f431979f/tables/phase5_stage3B_risk_register.csv) | `46f0399956220234ddc5cd591a7f4c220c8de01bddbd8b320b26612e3c6988a8` |
| **File Checksums Manifest** | CSV | [`reports/tables/phase5_stage3B_file_hashes.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/phase5_stage3B_file_hashes.csv) | [`brain/tables/phase5_stage3B_file_hashes.csv`](file:///c:/Users/akash/.gemini/antigravity/brain/52ad6ae8-887d-48db-85e7-7d53f431979f/tables/phase5_stage3B_file_hashes.csv) | *Self-Referential Hash Registry* |

---

## 8. Final Certification & Execution Stop Condition

This completes the Stage 3B Controlled Physical Parameter Calibration Authorization Request. 

In strict adherence to instructions:
- **Execution stops immediately upon submission.**
- **No calibration simulations will be executed until explicit, written reviewer authorization is received.**

**Signed:**  
*Lead Glaciological & Numerical Modeling Agent*  
*Project Antarctic Ice Volume Prediction — Phase 5 Physical Baseline Model*  
*Date: 2026-11-09*  
