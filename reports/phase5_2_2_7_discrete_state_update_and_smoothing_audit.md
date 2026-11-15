# Phase 5.2.2.7 — Discrete State-Update Closure and Smoothing Evidence Audit

**Project:** Antarctic Ice Volume Prediction — Hybrid Physical + ML Model  
**Phase:** 5.2.2.7 (Final mathematical and evidence audit before implementation authorization)  
**Date:** 2026-11-09  
**Status:** SUBMITTED FOR REVIEW  
**Spatial Domain (frozen):** 216,062.17 km² | 866,358 grounded cells | 500 m grid  
**Implementation:** LOCKED — no solver code written, executed, or modified in this phase

---

## 1. Executive Summary and Governance Compliance

This phase resolves the three remaining issues from the Phase 5.2.2.6 Conditional Pass review:

| Task | Issue | Resolution |
|------|-------|------------|
| Task 1 | Ambiguous discrete state-update algorithm — exact order of operations, ALE vs Eulerian choice, retreat/advance bookkeeping, multi-cell restriction, double-counting proof | **Fully resolved** — 11-step Fixed-Grid Eulerian algorithm; retreat and advance tables; CFL restriction; 7-point double-counting proof |
| Task 2 | Smoothing sensitivity results not explicitly provenance-labelled | **Fully resolved** — all smoothing statistics labelled ANALYTICAL_ESTIMATE or SPECIFICATION_CHOICE; raster computation classified DATA_UNAVAILABLE pending Stage 1 |
| Task 3 | 1 × 10⁻¹⁴ conservation claim provenance | **Maintained** — classification as Independent Synthetic Arithmetic Accounting Experiment (not a physical solver result) explicitly preserved throughout |

**Governance compliance:** No solver implementation code was written, executed, or modified. No physical parameters were calibrated. No ML models were trained or coupled. No future projections were generated. The Phase 2.6 spatial domain is unchanged. ISMIP6 remains an external benchmark only.

---

## 2. Task 1 — Complete Discrete State-Update Algorithm

### 2.1 Formulation Choice: Fixed-Grid Eulerian + Flotation Remapping

The planned scheme is a **Fixed-Grid Eulerian Finite-Volume scheme with sub-step Flotation Remapping** (hereafter FGE-FR). This choice is made explicitly here and governs all subsequent algorithm design.

**Definition:**  
In FGE-FR, all prognostic updates to ice thickness $H_i^{n+1}$ are performed on a fixed spatial grid with cells of uniform size $\Delta x = 500\ \text{m}$. The grounded/floating domain boundary (grounding-line position $x_\text{GL}$) is determined diagnostically by applying the flotation criterion to the updated thickness field — it does not drive the transport stencil.

**Why FGE-FR and not ALE (Arbitrary Lagrangian–Eulerian)?**

| Criterion | FGE-FR | ALE |
|-----------|--------|-----|
| Moving-mesh velocity in transport equation | **Absent** — no double-count risk | Present — requires careful subtraction of mesh velocity from advective velocity |
| Implementation complexity | Lower | Higher |
| Compatibility with nonlocal 1D SSA | Natural — fixed grid supports nonlocal elliptic BVP directly | Requires remapping of SSA operator at each step |
| Risk of double-counting boundary migration | **Zero by construction** | Non-trivial; depends on exact ALE formulation |
| Sub-cell grounding-line resolution | Achieved via partial-cell fraction $\lambda_g$ | Achieved via node placement |

The FGE-FR choice eliminates the ALE mesh-velocity term from the transport equation. The boundary migration contribution $\dot{\mathcal{M}}_\text{boundary}$ appears **only** in the diagnostic conservation residual — not in the prognostic thickness update.

---

### 2.2 Master Discrete State-Update Algorithm (11 Steps)

> **Full specification:** [`phase5_2_2_7_discrete_state_update_algorithm.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/phase5_2_2_7_discrete_state_update_algorithm.csv)

The following is the complete, unambiguous ordered sequence of operations for one timestep $[t_n, t_{n+1}]$:

#### Steps 1a–1d: State Load

Load from memory: $H_i^n$ (all grounded cells), $x_\text{GL}^n$, $\lambda_g^n$, $g(n)$. Read-only; no state modification.

#### Step 2: SSA Elliptic BVP (Diagnostic)

Solve:
$$\frac{d}{dx}\left[2H\nu_\text{eff}\frac{du}{dx}\right] - \tau_b(u) - \tau_\text{lat}(u) = \rho_i g H \frac{ds}{dx}$$

with stress-free calving-front boundary condition and inflow/divide condition at the upstream end.  
This is a **diagnostic** step — it computes the velocity field $u_{i+1/2}^n$ from the current geometry. No state variable is updated.

#### Steps 3a–3b: Effective Viscosity and Picard Iteration

$$\nu_\text{eff,i} = \frac{B_i}{2\left(\sqrt{\left(\tfrac{du}{dx}\right)^2 + \varepsilon_\text{reg}^2}\right)^{(n-1)/n}}, \quad \varepsilon_\text{reg} = 10^{-15}\ \text{s}^{-1}$$

Picard acceptance criterion (empirical engineering limit — not mathematically guaranteed):
$$\text{Res}_\text{Picard} = \frac{\|u^{(k+1)} - u^{(k)}\|}{\|u^{(k)}\| + u_\text{scale}} \leq 10^{-5}, \quad u_\text{scale} = 10\ \text{m yr}^{-1}, \quad k_\text{max} = 25$$

If not converged: flag RSK_NUM_07; halve $\Delta t$; retry.

#### Steps 4a–4b: Schoof Grounding-Line Flux (Advective Discharge)

$$q_\text{GL}^n = C_\text{Schoof}\left(\frac{\rho_i g}{4B}\right)^n \left[(1 - \tfrac{\rho_i}{\rho_w})\rho_i g\right]^n H_\text{GL}^{n+1}$$
$$Q_\text{GL}^n = W_\text{GL}^n \cdot q_\text{GL}^n \quad [\text{m}^3\ \text{s}^{-1}]$$

$Q_\text{GL}^n$ is the **pure advective** grounding-line mass discharge. It is applied once as the outflow boundary condition for the FV transport in Step 5d.  
> **Anti-double-count note:** $Q_\text{GL}$ is **not** applied again in Steps 7–9. The boundary-migration term in Step 8 is computed from geometry change — a distinct quantity.

#### Steps 5a–5d: Eulerian FV Transport (Interior and Terminal Cells)

Face fluxes (first-order upwind):
$$Q_{i+1/2}^n = W_{i+1/2} \cdot H_{i+1/2}^\text{upwind} \cdot u_{i+1/2}^n$$

Interior cell update ($i < g(n)$):
$$H_i^{n+1,*} = H_i^n + \frac{\Delta t}{W_i \Delta x}\left[Q_{i-1/2}^n - Q_{i+1/2}^n + S_i^n\right]$$

Terminal partial cell ($i = g(n)$), effective volume $= W_g \lambda_g^n \Delta x$:
$$H_g^{n+1,*} = H_g^n + \frac{\Delta t}{W_g \lambda_g^n \Delta x}\left[Q_{g-1/2}^n - Q_\text{GL}^n + S_g^n\right]$$

The superscript ${}^*$ denotes the **pre-remapping intermediate state** — no grounded/floating reclassification has occurred yet. No mesh-velocity term appears in either stencil.

#### Step 6: SMB Mass Accumulation (Diagnostic Accumulator)

$$\dot{\mathcal{M}}_\text{SMB}^n = \rho_i \sum_{i=1}^{g(n)} S_i^n \quad [\text{kg s}^{-1}]$$

This feeds the diagnostic residual (Step 11); it does not update any state variable.

#### Steps 7a–7b: Flotation Remapping (Domain Reclassification)

For each cell $i$, apply the flotation criterion:
$$\text{float}_i = \begin{cases} \text{True} & \text{if } H_i^{n+1,*} < \frac{\rho_w}{\rho_i}\max(0,\ z_\text{sl} - z_{b,i}) \\ \text{False} & \text{otherwise} \end{cases}$$

Determine $x_\text{GL}^{n+1}$ by linear sub-cell interpolation at the last cell satisfying `float = False`:
$$\lambda_g^{n+1} = \frac{H_{g}^* - H_\text{crit,g}}{H_{g}^* - H_{g+1}^*}, \quad H_\text{crit,g} = \frac{\rho_w}{\rho_i}(z_\text{sl} - z_{b,g}), \quad \lambda_g^{n+1} \in [0,1]$$

> **Critical:** This step reclassifies cells — it does **not** modify $H_i^{n+1,*}$. No mass is added or removed by the flotation criterion itself.

#### Step 8: Boundary Migration Velocity and Boundary Mass Term

$$v_\text{GL}^n = \frac{x_\text{GL}^{n+1} - x_\text{GL}^n}{\Delta t} \quad [\text{m s}^{-1}]$$
$$\Delta\mathcal{M}_\text{boundary}^n = \rho_i W_\text{GL}^n H_\text{GL}^n v_\text{GL}^n \Delta t \quad [\text{kg}]$$

> **Anti-double-count note:** $\Delta\mathcal{M}_\text{boundary}$ is derived **solely** from the geometric change $\Delta x_\text{GL}$. It appears **only** in the diagnostic residual (Step 11), not in the prognostic thickness update. The advective flux $Q_\text{GL}$ (Step 4) and the boundary migration $\Delta\mathcal{M}_\text{boundary}$ (Step 8) are computed from physically distinct velocities ($u_\text{GL}$ vs $v_\text{GL}$) and are mutually exclusive in the prognostic update.

#### Steps 9a–9c: Retreat and Advance Bookkeeping

Bilateral ledger updates that reclassify ice between grounded and floating reservoirs. Full specification in §2.3 (retreat) and §2.4 (advance). Key invariants:

- Mass is **never created or destroyed** in Steps 9a–9c — only the grounded/floating designation changes.
- $M_\text{gr} + \text{Floating\_ledger} = \text{const}$ (excluding SMB and calving fluxes).

#### Step 10: Prognostic Grounded Mass

$$M_\text{gr}(t_{n+1}) = \rho_i \sum_{i=1}^{g(n+1)-1} W_i \Delta x\, H_i^{n+1} + \rho_i W_g \lambda_g^{n+1} \Delta x\, H_g^{n+1}$$

This is computed from direct cell-volume summation — the primary prognostic state.

#### Step 11: Diagnostic Conservation Residual

$$\Delta M_\text{cons}(t_{n+1}) = M_\text{gr}(t_{n+1}) - M_\text{gr}(t_n) - \Delta t\,\dot{\mathcal{M}}_\text{SMB}^n + \Delta t\,\rho_i Q_\text{GL}^n - \Delta\mathcal{M}_\text{boundary}^n \equiv 0$$

If $|\Delta M_\text{cons}| > \varepsilon_\text{mach} \cdot M_\text{gr}$: flag error; halt; report. This is a **bookkeeping integrity check** — not a physical validation.

---

### 2.3 Retreat Bookkeeping Algorithm

> **Full specification:** [`phase5_2_2_7_retreat_algorithm.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/phase5_2_2_7_retreat_algorithm.csv)

#### Normal Partial Retreat ($0 < \lambda_g^{n+1} < \lambda_g^n$; pointer unchanged)

1. Compute new fraction: $\lambda_g^{n+1} = (x_\text{GL}^{n+1} - i_g \Delta x) / \Delta x$
2. Volume ungrounded: $\Delta\text{Vol} = W_g H_g^{n+1,*} (\lambda_g^n - \lambda_g^{n+1}) \Delta x$
3. Mass transferred: $\Delta M_\text{unground} = \rho_i \Delta\text{Vol}$
4. Floating ledger $+= \Delta M_\text{unground}$; $g(n+1) = g(n)$

#### Full Ungrounding ($\lambda_g^{n+1} \leq 0$; pointer decrements)

1. Transfer entire terminal cell: $\Delta M_\text{unground} = \rho_i W_g H_g^{n+1,*} \Delta x$
2. Floating ledger $+= \Delta M_\text{unground}$
3. $g(n+1) = g(n) - 1$; $\lambda_{g(n+1)}^{n+1} = 1.0$

**CFL guard:** If $|g(n+1) - g(n)| > 1$: flag RSK_NUM_08; halve $\Delta t$; redo timestep.

**Bilateral mass check:**
$$M_\text{gr,before} = M_\text{gr,after} + \Delta M_\text{unground}$$

---

### 2.4 Advance Bookkeeping Algorithm

> **Full specification:** [`phase5_2_2_7_advance_algorithm.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/phase5_2_2_7_advance_algorithm.csv)

#### Source Reservoir (Required Explicit Definition)

The advance algorithm acquires mass from the **floating ice reservoir** at cell $g+1$. The thickness $H_{g+1}^n$ is taken from:
- BedMachine V4.1 floating-ice thickness for cells not yet visited by the floating ledger, **or**
- The floating ledger record for cells previously ungrounded.

> **Critical:** Ice is **not created from vacuum**. If $H_{g+1}^n = 0$ (no floating ice at the advance cell): $\Delta M_\text{ground} = 0$; flag RSK_DATA_02.

#### Normal Partial Advance ($\lambda_g^{n+1} > \lambda_g^n$; $\lambda_g^{n+1} < 1$; pointer unchanged)

1. Compute new fraction: $\lambda_g^{n+1} = (x_\text{GL}^{n+1} - i_g \Delta x) / \Delta x$
2. Volume grounded: $\Delta\text{Vol} = W_g H_\text{source} (\lambda_g^{n+1} - \lambda_g^n) \Delta x$
3. Mass transferred: $\Delta M_\text{ground} = \rho_i \Delta\text{Vol}$
4. Floating ledger $-= \Delta M_\text{ground}$; $g(n+1) = g(n)$

#### Full Grounding ($\lambda_g^{n+1} \geq 1$; pointer increments)

1. Ground remaining portion of cell $g$: $\Delta M_1 = \rho_i W_g H_{\text{source},g} (1 - \lambda_g^n) \Delta x$
2. Ground partial fraction of new cell $g+1$: $\lambda_{g+1}^{n+1} = (x_\text{GL}^{n+1} - (i_g+1)\Delta x)/\Delta x$;  $\Delta M_2 = \rho_i W_{g+1} H_{g+1}^n \lambda_{g+1}^{n+1} \Delta x$
3. Floating ledger $-= (\Delta M_1 + \Delta M_2)$; $g(n+1) = g(n) + 1$; $\lambda_{g(n+1)}^{n+1} = \lambda_{g+1}^{n+1}$

**CFL guard:** If $g(n+1) - g(n) > 1$: flag RSK_NUM_08; halve $\Delta t$; redo timestep.

**Bilateral mass check:**
$$M_\text{gr,after} = M_\text{gr,before} + \Delta M_\text{ground}$$

---

### 2.5 CFL-Type Timestep Restriction

> **Full specification:** [`phase5_2_2_7_cfl_timestep_restriction.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/phase5_2_2_7_cfl_timestep_restriction.csv)

The restriction preventing multi-cell grounding-line crossings per timestep:

$$\Delta t \leq \frac{\Delta x}{|v_\text{GL}|_\text{max}} = \frac{500\ \text{m}}{|v_\text{GL}|_\text{max}}$$

| Scenario | $|v_\text{GL}|_\text{max}$ | $\Delta t_\text{max}$ | Safety margin at $\Delta t = 0.05\ \text{yr}$ |
|----------|--------------------------|----------------------|----------------------------------------------|
| Slow retreat | 50 m yr⁻¹ | 10.0 yr | ×200 |
| Moderate retreat | 500 m yr⁻¹ | 1.0 yr | ×20 |
| Rapid collapse | 5,000 m yr⁻¹ | 0.1 yr | ×2 (MONITOR) |
| Extreme collapse | 10,000 m yr⁻¹ | 0.05 yr | ×1 — REDUCE $\Delta t$ |

**Governance status:** This is a **provisional engineering limit** — not a mathematically proven stability criterion for the nonlocal 1D SSA. Stage 1 must characterise $v_\text{GL}$ empirically and validate the timestep choice.

---

### 2.6 Double-Counting Proof

> **Full specification:** [`phase5_2_2_7_double_count_proof.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/phase5_2_2_7_double_count_proof.csv)

Seven independent tests demonstrating that no physical process is counted more than once:

| Test | Mechanism Tested | Result |
|------|-----------------|--------|
| DC_01 | $Q_\text{GL}$ (advective flux) vs $\Delta\mathcal{M}_\text{boundary}$ (boundary migration) | PASS — computed from $u_\text{GL}$ vs $v_\text{GL}$ respectively; physically distinct |
| DC_02 | Fixed-grid Eulerian transport — no ALE mesh-velocity term | PASS — no $v_\text{GL}$ or $dx_\text{GL}/dt$ term in Steps 5c–5d |
| DC_03 | Flotation remapping — domain reclassification only, not mass removal | PASS — Steps 7a–7b do not modify $H_i^{n+1,*}$ |
| DC_04 | Retreat bookkeeping — $Q_\text{GL}$ flux vs $\Delta M_\text{unground}$ refer to different ice parcels | PASS — $Q_\text{GL}$ removes ice that left the cell; $\Delta M_\text{unground}$ reclassifies ice remaining in cell |
| DC_05 | Advance bookkeeping — $\dot{\mathcal{M}}_\text{SMB}$ vs floating-to-grounded reclassification are orthogonal | PASS — different mass reservoirs; no overlap |
| DC_06 | Diagnostic residual — four terms are orthogonal; zero residual is genuine | PASS — exhaustive enumeration shows each process maps to exactly one residual term |
| DC_07 | 1 × 10⁻¹⁴ result classification | PASS — maintained as Independent Synthetic Arithmetic Accounting Experiment; double-counting proofs do not depend on it |

**Central result:** In the FGE-FR scheme, the boundary migration contribution $\Delta\mathcal{M}_\text{boundary}$ appears **exactly once** — in the diagnostic residual identity (Step 11) — and **never** in the prognostic thickness update (Steps 5c–5d). Double counting is structurally impossible by the choice of scheme.

---

## 3. Task 2 — Smoothing Evidence Audit

> **Full specification:** [`phase5_2_2_7_smoothing_evidence_audit.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/phase5_2_2_7_smoothing_evidence_audit.csv)

### 3.1 Global Provenance Classification

> [!IMPORTANT]
> **ALL smoothing sensitivity statistics in Phases 5.2.2.5 and 5.2.2.6 are ANALYTICAL_ESTIMATEs.**  
> No cell-by-cell spatial raster computation has been performed in any audit phase. Full raster computation requires raw InSAR velocity NetCDFs (ITS_LIVE v2 / MEaSUREs v2) which are **NOT AVAILABLE** in the current sandbox.

### 3.2 Explicit Provenance Labels by Result

| Result | Region | Value | Label | Basis |
|--------|--------|-------|-------|-------|
| Baseline filter width $\sigma = 1.5\ \text{km}$ | All | 3 grid cells | SPECIFICATION_CHOICE | Design parameter, not computed |
| Median dynamic ratio | Palmer Land | ~11.1% | ANALYTICAL_ESTIMATE | Published aggregate IMBIE3/Rignot et al. flux values; scalar ratio |
| Passive assumption validity | Palmer Land | VALID | ANALYTICAL_ESTIMATE | Follows from 11.1% < 30% threshold |
| $\sigma$ sensitivity range | Palmer Land | ±2.3 pp | ANALYTICAL_ESTIMATE | Gaussian error propagation on scalar estimate |
| Median dynamic ratio | Graham Land | ~86.9% | ANALYTICAL_ESTIMATE | Published aggregate flux values; scalar ratio |
| Passive assumption validity | Graham Land | INVALID | ANALYTICAL_ESTIMATE | Follows from 86.9% > 30% threshold |
| Median dynamic ratio | Ipp-J | ~43.2% | ANALYTICAL_ESTIMATE | Published aggregate flux values; scalar ratio |
| Passive assumption validity | Ipp-J | BORDERLINE-INVALID | ANALYTICAL_ESTIMATE | Follows from 43.2% > 30%; margin narrow |
| 11.4% high-divergence cell fraction | All | 11.4% | ANALYTICAL_ESTIMATE | Representative scalar model; not raster count |
| 91.5% low-divergence area fraction | All | 91.5% | ANALYTICAL_ESTIMATE | Representative scalar model; not raster count |

### 3.3 Usage Prohibitions

Smoothing statistics classified as ANALYTICAL_ESTIMATE **must NOT be**:
1. Used to calibrate physical solver parameters ($C_\text{bed}$, $A$, $n$, or any other).
2. Presented as raster-computed results in publications or external reports.
3. Used to set passive-remainder boundary conditions without Stage 1 raster verification.

### 3.4 Stage 1 Raster Verification Task (Required)

The following data pipeline must be implemented in Stage 1 (after implementation authorization):

1. Acquire raw ITS_LIVE v2 velocity NetCDFs for the Antarctic Peninsula (Hp-I, I-Ipp, Ipp-J sub-basins).
2. Process to 500 m grid aligned with Phase 2.6 grounded mask (866,358 cells).
3. Compute flux divergence field: $\nabla\cdot\mathbf{q} = \partial_x(W H u)$ at each cell.
4. Apply Gaussian smoothing at $\sigma$ = 1.0, 1.5, 2.0 km; compute area-weighted statistics.
5. Update provenance labels from ANALYTICAL_ESTIMATE to RASTER_COMPUTED where verified.
6. Update passive-assumption validity classifications based on verified dynamic ratios.

---

## 4. Task 3 — Conservation Provenance Maintained

> [!IMPORTANT]
> The 1 × 10⁻¹⁴ conservation result from Phase 5.2.2.4 is classified as an **Independent Synthetic Arithmetic Accounting Experiment**.  
> It is **NOT** a physical solver result, NOT a validation of the discrete algorithm, and NOT evidence that the solver will conserve mass to machine precision.

This classification is **unchanged** in Phase 5.2.2.7. All double-counting proofs in §2.6 are analytical derivations from the scheme definition — they are independent of the 1 × 10⁻¹⁴ result and do not use it as supporting evidence.

---

## 5. Deliverables Inventory

| File | Description | Status |
|------|-------------|--------|
| [`phase5_2_2_7_discrete_state_update_algorithm.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/phase5_2_2_7_discrete_state_update_algorithm.csv) | 11-step master algorithm with Anti_Double_Count_Note column | ✅ Created |
| [`phase5_2_2_7_retreat_algorithm.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/phase5_2_2_7_retreat_algorithm.csv) | 11-row retreat bookkeeping specification | ✅ Created |
| [`phase5_2_2_7_advance_algorithm.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/phase5_2_2_7_advance_algorithm.csv) | 13-row advance bookkeeping specification with explicit source reservoir | ✅ Created |
| [`phase5_2_2_7_cfl_timestep_restriction.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/phase5_2_2_7_cfl_timestep_restriction.csv) | CFL restriction with 5 scenario rows and governance status | ✅ Created |
| [`phase5_2_2_7_double_count_proof.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/phase5_2_2_7_double_count_proof.csv) | 7-test double-counting proof | ✅ Created |
| [`phase5_2_2_7_smoothing_evidence_audit.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/phase5_2_2_7_smoothing_evidence_audit.csv) | 12-row audit with explicit ANALYTICAL_ESTIMATE labels | ✅ Created |
| [`phase5_2_2_7_risk_register.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/phase5_2_2_7_risk_register.csv) | Updated risk register with RSK_NUM_08 and RSK_DATA_01/02 | ✅ Created |
| [`phase5_2_2_7_discrete_state_update_and_smoothing_audit.md`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/phase5_2_2_7_discrete_state_update_and_smoothing_audit.md) | Master report (this file) | ✅ Created |

---

## 6. Revisions from Phase 5.2.2.6

| Issue | Phase 5.2.2.6 State | Phase 5.2.2.7 Resolution |
|-------|---------------------|--------------------------|
| ALE vs Eulerian formulation unspecified | Unresolved — both mentioned ambiguously | **Fixed:** Explicitly selected Fixed-Grid Eulerian + Flotation Remapping; ALE formally excluded |
| Exact order of operations per timestep | Not provided | **Fixed:** 11-step ordered algorithm with explicit sequencing and anti-double-count annotations |
| Retreat bookkeeping undefined | "Mass goes to floating" — vague | **Fixed:** 11-row table with bilateral conservation check; full-ungrounding vs partial-retreat cases |
| Advance source reservoir undefined | Unspecified | **Fixed:** Explicitly defined as floating ledger or BedMachine V4.1 floating thickness; zero-ice case flagged |
| Multi-cell GL crossing — no restriction | Unspecified | **Fixed:** CFL-type restriction $\Delta t \leq \Delta x / |v_\text{GL}|_\text{max}$; dynamic timestep halving protocol |
| Double-counting not formally proven | Heuristic description only | **Fixed:** 7 independent analytical tests, all PASS |
| Smoothing statistics not provenance-labelled | Presented without labels | **Fixed:** All 12 results explicitly labelled ANALYTICAL_ESTIMATE or SPECIFICATION_CHOICE |
| Raster computation availability unclear | Implicit that rasters exist | **Fixed:** Explicitly classified DATA_UNAVAILABLE in sandbox; Stage 1 raster pipeline specified |

---

## 7. Unresolved Limitations and Open Items

The following items are explicitly **not resolved** in this phase and are carried forward to Stage 1:

| Item | Status | Mitigation in Specification |
|------|--------|----------------------------|
| Picard convergence not mathematically guaranteed | OPEN | Empirical criterion specified (RSK_NUM_07); $\omega \in [0.4,0.6]$; 25-iteration limit |
| CFL restriction is a provisional engineering limit, not a proven SSA stability criterion | OPEN | Dynamic timestep reduction protocol specified |
| All smoothing sensitivity statistics are ANALYTICAL_ESTIMATEs — not raster-verified | OPEN | Stage 1 raster pipeline specified; usage prohibitions stated |
| Schoof GL flux applicability for land-terminating or narrow-fjord glaciers | OPEN | Individual glacier classification required at Stage 1 (RSK_NUM_04) |
| Graham Land passive-remainder assumption INVALID — SIA coupling not yet designed | OPEN | EXP-PASSIVE-01 through 03 specified (RSK_NUM_06) |
| SSA adjustment timescale (20–50 yr) revoked — no replacement characterisation available | OPEN | EXP-ADJ-01 specified in Stage 1 calibration plan (RSK_PHY_03) |
| Bilateral ledger conservation at floating boundaries — floating ice calving parameterisation not yet specified | OPEN | Q_calving = 0 assumed for landlocked glaciers pending parameterisation |

---

## 8. Frozen and Accepted Prior Results (Immutable)

The following results from earlier phases are accepted and must not be revisited:

| Result | Accepted In | Status |
|--------|-------------|--------|
| Phase 2.6 spatial domain: 216,062.17 km²; 866,358 cells; 500 m grid | Phase 2.6 | FROZEN |
| Lateral drag formula: $\tau_\text{wall} = (5\bar{u}/(AW))^{1/n}$ (no factor of 2 in denominator) | Phase 5.2.2.5 | ACCEPTED |
| $\rho_i$ factor required in $\rho_i Q_\text{GL}$ terms | Phase 5.2.2.5 | ACCEPTED |
| Relative flux: $Q_\text{relative} = W_\text{GL} H_\text{GL}(u_\text{GL} - v_\text{GL})$ | Phase 5.2.2.6 | ACCEPTED |
| Kinematic wave $c_\text{wave} = (m+1)u$ incompatible with nonlocal 1D SSA — REVOKED | Phase 5.2.2.6 | REVOKED |
| 20–50 year SSA adjustment timescale — REVOKED | Phase 5.2.2.6 | REVOKED |
| Picard convergence "mathematically guaranteed" — REVOKED | Phase 5.2.2.4 | REVOKED |
| $1\times10^{-14}$ result = Independent Synthetic Arithmetic Accounting Experiment | Phase 5.2.2.4 | MAINTAINED |
| InSAR velocity streamlines (not D8) for catchment delineation | Phase 5.2.2.2 | ACCEPTED |
| Raw vector catchment 232,678.32 km² reconciled with grounded mask 216,062.17 km² | Phase 5.2.2.2 | ACCEPTED |

---

## 9. Final Governance Determination

**Phase 5.2.2 implementation status: LOCKED**

This phase has resolved all three issues from the Phase 5.2.2.6 Conditional Pass review:

1. ✅ **Task 1 — Discrete State-Update Closure:** Complete 11-step algorithm; ALE vs Eulerian choice explicitly made (FGE-FR); retreat and advance bookkeeping fully specified with bilateral conservation checks; CFL-type timestep restriction specified; double-counting formally proven by seven independent analytical tests.

2. ✅ **Task 2 — Smoothing Evidence Audit:** All smoothing sensitivity statistics explicitly labelled ANALYTICAL_ESTIMATE; raster computation classified DATA_UNAVAILABLE pending Stage 1; Stage 1 verification pipeline specified; usage prohibitions stated.

3. ✅ **Task 3 — Conservation Provenance:** 1 × 10⁻¹⁴ result classification as Independent Synthetic Arithmetic Accounting Experiment explicitly maintained throughout.

**Submitted as: PASS candidate — awaiting reviewer decision.**

The mathematical specification for the Pillar 1 physical solver backbone is now complete. No implementation code has been written. Stage 1 implementation authorisation requires a separate governance decision by the reviewer.

---

*Phase 5.2.2.7 — Generated 2026-11-09 | Specification-only phase | No solver implementation | No physical parameters calibrated | No ML models trained | No future projections generated*

