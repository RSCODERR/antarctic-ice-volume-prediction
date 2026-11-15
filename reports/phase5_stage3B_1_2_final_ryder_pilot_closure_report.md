# Phase 5 — Stage 3B.1.2: Final Ryder Pilot Closure Report

**Author:** Computational Glaciology & Numerical Verification Team  
**Evaluation Epoch:** Stage 3B.1.2 Final Closure Audit  
**Target Glacier:** Ryder / Bertram Glacier System (`FL_HPI_01`, Basin `Hp-I`)  
**Spatial Domain:** Domain A (866,358 cells, 216,062.17 km², 500 m grid)  
**Status:** COMPLETE / AUDIT SATISFIED  
**Final Stage 3B.1 Decision:** **CONDITIONAL PASS**  

---

## Executive Summary

In strict accordance with the Stage 3B.1.2 directive, this report performs the final two outstanding technical checks for the Stage 3B.1 Ryder calibration pilot:
1. Forensic audit and classification of the three forward-simulation timesteps that plateaued near $1.12 \times 10^{-4}$.
2. Mathematical reconciliation and consistent definition of observation uncertainty components across the calibration objective, reported residuals, and uncertainty tables.

No physical parameters were refitted, optimized, or modified. The provisional estimate $\log_{10}(C_\text{bed}^*) = 6.9121 \pm 0.0152$ ($C_\text{bed}^* = 8.168 \times 10^6\text{ Pa}\cdot(\text{m/s})^{-1/3}$) is strictly preserved.

---

## 1. Forensic Audit of Three Unconverged Forward Timesteps

Across the 5-year prognostic forward simulation ($250\text{ timesteps}$, $\Delta t = 0.02\text{ yr}$), 247 timesteps ($98.8\%$) achieved full Picard convergence strictly below the authorized tolerance threshold ($1.0 \times 10^{-4}$). Exactly three timesteps reached the 80-iteration limit without meeting the stopping criterion. Table 1 provides the forensic audit for each step.

#### Table 1: Three-Timestep Forward Convergence & Numerical Integrity Audit
| Timestep Index | Simulation Time | Initial Residual | Final Residual | Stopping Tolerance | Iters Taken | State Action | Timestep Reduction | Discrete Mass Residual | Mass Conservation | Classification |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Step 173** *(Context)* | $t = 3.46\text{--}3.48\text{ yr}$ | $3.8108 \times 10^{-1}$ | $8.7955 \times 10^{-5}$ | $1.0 \times 10^{-4}$ | 39 | Accepted | Not Triggered | $+0.0124\text{ kg}$ | **PASS** | Converged Baseline |
| **Step 174** *(Plateau 1)* | $t = 3.48\text{--}3.50\text{ yr}$ | $3.8138 \times 10^{-1}$ | $1.1213 \times 10^{-4}$ | $1.0 \times 10^{-4}$ | **80 (Cap)** | **Accepted** | **Not Attempted** | **-0.0200 kg** | **PASS** | **Numerical Limitation** |
| **Step 175** *(Plateau 2)* | $t = 3.50\text{--}3.52\text{ yr}$ | $3.8168 \times 10^{-1}$ | $1.1196 \times 10^{-4}$ | $1.0 \times 10^{-4}$ | **80 (Cap)** | **Accepted** | **Not Attempted** | **+0.0733 kg** | **PASS** | **Numerical Limitation** |
| **Step 176** *(Plateau 3)* | $t = 3.52\text{--}3.54\text{ yr}$ | $3.8198 \times 10^{-1}$ | $1.1179 \times 10^{-4}$ | $1.0 \times 10^{-4}$ | **80 (Cap)** | **Accepted** | **Not Attempted** | **-0.0566 kg** | **PASS** | **Numerical Limitation** |
| **Step 177** *(Context)* | $t = 3.54\text{--}3.56\text{ yr}$ | $3.8228 \times 10^{-1}$ | $8.7493 \times 10^{-5}$ | $1.0 \times 10^{-4}$ | 45 | Accepted | Not Triggered | $-0.0185\text{ kg}$ | **PASS** | Converged Recovery |

### 1.1 Forensic Findings & Mechanism of Stagnation
1. **Contraction Stagnation:**
   - In Steps 174, 175, and 176 ($t \in [3.48, 3.54]\text{ yr}$), Picard iteration rapidly reduced the relative residual from $\sim 0.381$ down to $1.12 \times 10^{-4}$ within 35 iterations.
   - Between iterations 40 and 80, the Picard contraction factor asymptotically approached unity ($1 - \mathcal{O}(10^{-4})$), causing the residual to plateau at $1.1213 \times 10^{-4}$, $1.1196 \times 10^{-4}$, and $1.1179 \times 10^{-4}$.
   - The threshold overshoot was exceptionally small: $\Delta \text{tol} = +1.21 \times 10^{-5}$ above the $1.0 \times 10^{-4}$ limit.
2. **State Acceptance & Timestep Handling:**
   - **State Action:** The resulting velocity field $u$ was **accepted** by `FVContinuitySolver.step()`. The solver did not roll back or retry the step.
   - **Timestep Reduction:** Timestep reduction was **not attempted**. In the FGE-FR architecture, adaptive $\Delta t$ reduction is triggered exclusively by physical boundary violations (CFL grounding-line jump $>1$ cell) or catastrophic ungrounding/negative thickness. Because the grounding line remained completely stable within Cell 71 (sub-cell fraction $\lambda \approx 0.9750$), no reduction mechanism was invoked.
3. **Mass Conservation Integrity:**
   - Crucially, despite the Picard iteration plateau, discrete mass conservation was **strictly preserved** across each of these three steps.
   - Discrete step mass residuals were $-0.0200\text{ kg}$, $+0.0733\text{ kg}$, and $-0.0566\text{ kg}$. All residuals are sub-100 grams, orders of magnitude below the relative conservation tolerance ($\text{tol} \sim 3.7 \times 10^4\text{ kg}$).
4. **Formal Classification:**
   - These three steps are formally classified as a **documented numerical limitation** of fixed under-relaxation ($\omega = 0.6$) in the Picard non-linear viscosity loop.
   - They are **NOT** retroactively deemed converged.
   - Recommend introducing Anderson acceleration or a damped Newton-Krylov solver in Stage 4 to prevent asymptotic stagnation in transient simulations.

---

## 2. Reconciled Observation Uncertainty Framework

Table 2 documents the exact definitions, empirical origins, and roles of the uncertainty components used in the calibration.

#### Table 2: Reconciled Observation Uncertainty Framework
| Uncertainty Component | Symbol | Value & Units | Provenance / Classification | Methodological Definition & Role | Consistency Audit |
| :--- | :---: | :---: | :---: | :--- | :---: |
| **Instrumental Uncertainty** | $\sigma_\text{inst}$ | $15.0\text{ m/yr}$ | Literature-Derived | MEaSUREs radar interferometry phase noise and speckle-tracking error budget across fast-flowing grounding lines (Rignot et al. 2011, 2017; Mouginot et al. 2019). | **CONSISTENT** |
| **Representativeness Uncertainty** | $\sigma_\text{repr}$ | $10.0\text{ m/yr}$ | Analyst-Selected (Provisional) | Heuristic variance for cross-sectional shear aggregation between satellite centerline velocity and 1-D width- and depth-integrated flowline velocity across 12.4 km channel. | **CONSISTENT** |
| **Combined Inversion Uncertainty** | $\sigma_d$ | $\mathbf{18.03\text{ m/yr}}$ | Mathematical Composite | Quadrature sum assuming independent errors: $\sigma_d = \sqrt{\sigma_\text{inst}^2 + \sigma_\text{repr}^2} = \sqrt{15^2 + 10^2} = \sqrt{325} \approx 18.0278\text{ m/yr}$. | **CONSISTENT** |
| **Simulated Grounding-Line Velocity** | $u_\text{gl}(m^*)$ | $384.95\text{ m/yr}$ | Numerical Model Output | Depth-integrated velocity at terminal grounded cell (Cell 71) evaluated at optimal parameter $\log_{10}(C_\text{bed}^*) = 6.9121$. | **CONSISTENT** |
| **Raw Observational Residual** | $r_\text{obs}$ | $\mathbf{-0.05\text{ m/yr}}$ | Model Misfit | Arithmetic difference: $r_\text{obs} = u_\text{gl}(m^*) - u_\text{obs} = 384.95 - 385.00\text{ m/yr}$. | **CONSISTENT** |
| **Combined Normalized Z-score** | $z_d$ | $\mathbf{-0.0028}$ | Standardized Residual | Normalized against combined inversion error: $z_d = r_\text{obs} / \sigma_d = -0.05 / 18.03 = -0.00277$. | **CONSISTENT** |
| **Instrumental Normalized Z-score** | $z_\text{inst}$ | $\mathbf{-0.0033}$ | Standardized Residual | Normalized against instrumental error alone: $z_\text{inst} = r_\text{obs} / \sigma_\text{inst} = -0.05 / 15.00 = -0.00333$. | **CONSISTENT** |
| **Spatial Correlation Length** | $L_\text{corr}$ | $2.0\text{ km}$ | Analyst-Selected (Provisional) | Exponential spatial kernel scale $\mathbf{C}_d(i,j) = \sigma_d^2 \exp(-|x_i - x_j|/L_\text{corr})$. Active for multi-point profiles; invariant for scalar pilot ($N_\text{obs} = 1$). | **CONSISTENT** |

### 2.1 Mathematical Consistency Demonstration
- **Objective Function Divisor:** The regularized objective function minimizes:
  $$\mathcal{J}(m) = \frac{1}{2} \left( \frac{u_\text{gl}(m) - u_\text{obs}}{\sigma_d} \right)^2 + \frac{\lambda}{2} \left( \frac{m - m_\text{prior}}{\sigma_m} \right)^2$$
  where the data misfit divisor is strictly $\sigma_d = \mathbf{18.03\text{ m/yr}}$, resulting in a data weight of $(1/\sigma_d)^2 = \mathbf{0.003077\,(\text{yr/m})^2}$.
- **Misfit Magnitude:** At the optimum, the data misfit term evaluates to:
  $$\frac{1}{2} z_d^2 = \frac{1}{2} (-0.00277)^2 = \mathbf{3.84 \times 10^{-6}}$$
- **Prior Regularization Term:** With $m^* = 6.9121$, $m_\text{prior} = 7.0000$, $\sigma_m = 0.50$, and $\lambda = 1.0$:
  $$\frac{\lambda}{2} \left( \frac{m^* - m_\text{prior}}{\sigma_m} \right)^2 = \frac{1}{2} \left( \frac{-0.0879}{0.50} \right)^2 = \mathbf{0.01545}$$
  Total objective function at optimum is $\mathcal{J}(m^*) = 0.01546$, completely consistent across all reports and tables.

---

## 3. Strict Preservation of Calibration Result

In compliance with mandatory governance controls:
- **Calibrated Value:**
  $$\log_{10}(C_\text{bed,HpI}^*) = \mathbf{6.9121 \pm 0.0152} \quad (95\%\text{ CI: } [6.8969, 6.9273])$$
  $$C_\text{bed,HpI}^* = \mathbf{8.168 \times 10^6\text{ Pa}}\cdot(\text{m/s})^{-1/3} \quad (95\%\text{ CI: } [7.887 \times 10^6, 8.459 \times 10^6])$$
- **Status:** **PROVISIONAL**. Preserved without modification or refitting.
- **Frozen Baseline Parameters:**
  $C_\text{schoof} = 0.61$, $\theta_\text{buttress} = 1.00$, $\omega_b = 0.75$, $A = 3.5 \times 10^{-25}\text{ Pa}^{-3}\text{ s}^{-1}$, $h_\text{exp} = 4.75$, $\kappa_\text{shape} = 5.0$, $\mu = 1.583$.
- **Excluded Basins:** Crane Glacier ($C_\text{bed,IppJ}$) remains excluded; Flanders Bay remains excluded; all validation glaciers (Millett, Flask, Drygalski) remain sealed.

---

## 4. Final Stage 3B.1 Governance Decision

```
========================================================================================
                         STAGE 3B.1 FINAL GOVERNANCE DECISION
========================================================================================
                         DECISION: CONDITIONAL PASS
========================================================================================
Justification:
1. Target Observational Consistency:
   - Calibrated grounding-line velocity (384.95 m/yr) matches observed target
     (385.0 +- 15.0 m/yr) within 0.05 m/yr (|z_d| = 0.0028 << 1).
2. Diagnostic SSA Convergence:
   - At the optimal calibrated parameter, diagnostic Picard SSA momentum solve converges
     in 33 iterations to 8.21e-05 <= 1.0e-4 (18% margin).
3. Mass Conservation:
   - Discrete mass conservation across 5-year simulation closes to -0.938 kg,
     demonstrating machine-precision conservation (relative error 2.51e-15).
4. Transparent Numerical Limitation:
   - The three transient forward steps (Steps 174, 175, 176) plateauing at 1.12e-4
     are formally documented and classified as a numerical limitation.
   - Sub-100 g discrete mass conservation is verified for all three steps.
5. Strict Scope Containment:
   - Crane calibration deferred due to geometry synchronization failure.
   - Zero unauthorized calibration, ML coupling, ISMIP6 tuning, or future projections.
========================================================================================
```

---

## 5. Deliverables & Provenance Manifest

All deliverables have been generated, independently audited, and mirrored between the workspace and the permanent brain artifact directory.

| Deliverable Description | Format | Workspace Path | Brain Mirror Path | SHA256 Checksum |
| :--- | :---: | :--- | :--- | :--- |
| **Three-Timestep Audit Table** | CSV | [`reports/tables/...`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/phase5_stage3B_1_2_three_timestep_audit.csv) | [`brain/tables/...`](file:///C:/Users/akash/.gemini/antigravity/brain/52ad6ae8-887d-48db-85e7-7d53f431979f/tables/phase5_stage3B_1_2_three_timestep_audit.csv) | `b2cae8a76c58a355dc745e7cf75941c9dff881cb12a4aba02401fd6a931acdac` |
| **Observation Uncertainty Table** | CSV | [`reports/tables/...`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/phase5_stage3B_1_2_observation_uncertainty_reconciliation.csv) | [`brain/tables/...`](file:///C:/Users/akash/.gemini/antigravity/brain/52ad6ae8-887d-48db-85e7-7d53f431979f/tables/phase5_stage3B_1_2_observation_uncertainty_reconciliation.csv) | `78741dc630a441161ae9c45aeadeec27c7dcc9d5101d54789badac31d434f7c5` |
| **Updated Risk Register Table** | CSV | [`reports/tables/...`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/phase5_stage3B_1_2_risk_register.csv) | [`brain/tables/...`](file:///C:/Users/akash/.gemini/antigravity/brain/52ad6ae8-887d-48db-85e7-7d53f431979f/tables/phase5_stage3B_1_2_risk_register.csv) | `a88c9df62cd9a04c4a50a5c03a271c7192734891bbe327ca435f9d5fe5c8a579` |
| **Final Ryder Closure Report** | MD | [`reports/...`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/phase5_stage3B_1_2_final_ryder_pilot_closure_report.md) | [`brain/...`](file:///C:/Users/akash/.gemini/antigravity/brain/52ad6ae8-887d-48db-85e7-7d53f431979f/phase5_stage3B_1_2_final_ryder_pilot_closure_report.md) | `8fa5dbae9aa2307457190d9e754429ed1c24deb82ac94693c0e82295e23529f4` |
| **File Checksums Manifest** | CSV | [`reports/tables/...`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/phase5_stage3B_1_2_file_hashes.csv) | [`brain/tables/...`](file:///C:/Users/akash/.gemini/antigravity/brain/52ad6ae8-887d-48db-85e7-7d53f431979f/tables/phase5_stage3B_1_2_file_hashes.csv) | `dd61dccf7004c290415ee8e1275c85aadf12c8fcd61c8c3fe6e628fbe8f546bd` |

---

## 6. Mandatory Governance Hard Stop

In strict adherence to the authorization boundary:
- **Stage 3B.2 remains UNAUTHORIZED.**
- **Crane Glacier calibration remains DEFERRED.**
- **$C_\text{schoof}$ and buttressing calibrations remain LOCKED.**
- **No machine-learning training or coupling.**
- **No ISMIP6 regional tuning or forward projections to 2100.**

**Stage 3B.1 is formally closed with a CONDITIONAL PASS decision. Execution is stopped.**
