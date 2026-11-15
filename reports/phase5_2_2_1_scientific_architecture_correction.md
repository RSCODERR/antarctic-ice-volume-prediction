# Phase 5.2.2.1 — Scientific Architecture & Numerical Consistency Correction

**Author:** Antigravity Cryospheric Modeling & Computational Physics Group  
**Date:** 2026-11-08  
**Project:** Antarctic Peninsula Grounded-Ice Volume Change Prediction  
**Basins Covered:** `Hp-I` (Palmer Land West), `I-Ipp` (Graham Land West), `Ipp-J` (Graham Land East), and Regional `Domain A`  
**Governing Protocol:** Authoritative Phase 5.1.2 Authorization Correction & Two-Pillar Independence Protocol  
**Phase Status:** ARCHITECTURAL CORRECTION ONLY (Strictly Planning-Only)  
**Implementation Gate:** **PHASE 5.2.2 IMPLEMENTATION REMAINS STRICTLY LOCKED**  

---

## Executive Summary & Strict Governance Adherence

This document provides the formal scientific and numerical architecture corrections required prior to the authorization of the **Phase 5.2 Pure Physical Dynamic Backbone (Pillar 1)**.

### Strict Governance Restrictions
* **Zero Implementation Code:** No solver source code is written or modified in `src/`.
* **Zero Simulations:** No forward model executions are conducted.
* **Zero Parameter Calibration:** No parameters are tuned against historical altimetry, InSAR, or projection datasets.
* **Zero Machine Learning Coupling:** No ML models are trained, evaluated, or coupled.
* **Zero Forward Projections:** No simulations forward to 2100 are generated.
* **Zero ISMIP6 Calibration:** The Two-Pillar Independence Protocol is strictly enforced: Pillar 1 calibration sources are restricted to independent observational constraints (BedMachine, RACMO, InSAR, Phase 3.2 historical reconstruction). ISMIP6 projection models serve strictly as an external comparison benchmark (Pillar 2).
* **Implementation Gate Status:** **Phase 5.2.2 implementation is NOT authorized by this document.** Implementation requires separate explicit authorization by the user following independent review.

---

## 1. Issue 1 — Initial Geometry and Firn Conventions

### 1.1 Metadata and Phase 2 Provenance Audit
In the Phase 2.5 forensic audit of MEaSUREs BedMachine Antarctica V4.1 NetCDF files (`BedMachineAntarctica-v4.1.nc`), the actual variables were evaluated across all 47,996,988 continental grounded cells:
* **`thickness` (`float32`, $[\text{m}]$):** Explicitly defined as **solid ice-equivalent thickness** ($\rho_i = 917.0\text{ kg m}^{-3}$). Firn air pore space is **ALREADY SUBTRACTED**.
* **`surface` (`float32`, $[\text{m}]$):** Explicitly defined as **ice-equivalent surface elevation** (meters above EIGEN-6C4 geoid). It is **ALREADY DEPRESSED** below the physical snow surface by the firn air depth.
* **`bed` (`float32`, $[\text{m}]$):** Bedrock topography and sub-shelf bathymetry.
* **`firn` (`float32`, $[\text{m}]$):** Firn Air Content ($\text{FAC}$), modeled by IMAU-FDM driven by RACMO2.3p2, representing the cumulative meters of air pore space.

### 1.2 The BedMachine Array Identity Proof
As proven in Phase 2.5 (Section 2.2), the raw BedMachine NetCDF array satisfies:
$$\Delta \equiv (\text{surface}_{\text{BM}} - \text{bed}_{\text{BM}}) - \text{thickness}_{\text{BM}} \equiv 0$$
across $99.9995\%$ of all grounded cells (mean discrepancy $2.19 \times 10^{-10}\text{ m}$, bounded by IEEE 754 single-precision float epsilon).

Therefore:
$$\mathbf{\text{surface}_{\text{BM}} \equiv z_b + H}$$
**BedMachine's supplied `surface` variable is already the ice-equivalent surface!**

### 1.3 Resolution of the Double-Subtraction Error
The previously drafted initialization equation:
$$H_0 = s_0 - z_b - \text{FAC}_0$$
is **scientifically ambiguous and prone to double-counting**:
1. **If $s_0$ is BedMachine's supplied `surface` variable:**
   Since $\text{surface}_{\text{BM}} = z_b + H$, evaluating $s_0 - z_b$ yields $H$ directly. Subtracting $\text{FAC}_0$ from this quantity would subtract firn air a second time, erroneously shrinking ice thickness by an artificial $15\text{--}25\text{ m}$ across Palmer Land!
2. **If $s_0$ is the physical geometric snow surface ($S_{\text{snow}}$ from REMA DEM or altimetry):**
   Then $S_{\text{snow}} = z_b + H + \text{FAC}$, and subtracting $z_b$ and $\text{FAC}$ is mathematically correct.

### 1.4 Authoritative Geometry Transformation Protocol
To eliminate ambiguity, all transformations are formalized (cataloged in [`phase5_2_2_1_geometry_firn_transformations.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/phase5_2_2_1_geometry_firn_transformations.csv)):

```
========================================================================================================
EXACT GEOMETRIC TRANSFORMATION RELATIONS
========================================================================================================
1. Solid Ice-Equivalent Thickness:     H = thickness_BM = surface_BM - bed_BM                   [m]
2. Geometric Column Thickness:         H_geom = H + FAC = thickness_BM + firn_BM                [m]
3. Bedrock Elevation:                  z_b = bed_BM                                             [m]
4. Ice-Equivalent Surface Elevation:   s_ice_eq = surface_BM = z_b + H                          [m]
5. Physical Snow Surface Elevation:    s_geom = surface_BM + firn_BM = z_b + H + FAC            [m]
========================================================================================================
```

* **Implementation Rule:** In `src/physics/geometry.py`, the initial solid ice thickness is ingested directly from BedMachine as:
  $$H_0(x) = \text{thickness}_{\text{BM}}(x)$$
  **$\text{FAC}$ is NOT subtracted from BedMachine `thickness` or $(\text{surface}_{\text{BM}} - \text{bed}_{\text{BM}})$.**
* Firn air content $\text{FAC}(x, t)$ is preserved as an independent structural diagnostic variable strictly used to reconstruct the physical snow surface elevation $s_{\text{geom}}(x, t) = z_b(x) + H(x, t) + \text{FAC}(x, t)$ when comparing model output against satellite laser/radar altimetry.

---

## 2. Issue 2 — SMB and Continuity Units

### 2.1 Unified Solver Unit System (Pure Canonical SI)
To eradicate unit conversion discrepancies between empirical rates ($\text{m w.e. yr}^{-1}$) and physical fluxes ($\text{m}^3\text{ s}^{-1}$), the internal numerical solver operates in **strict canonical SI base units**:
* Length / Coordinates: $x, W, H, z_b, s \in [\mathbf{\text{m}}]$
* Time: $t_{\text{sec}}, \Delta t_{\text{sec}} \in [\mathbf{\text{s}}]$
* Mass: $M \in [\mathbf{\text{kg}}]$
* Velocity: $\bar{u} \in [\mathbf{\text{m s}^{-1}}]$
* Volumetric Cross-Sectional Flux: $Q = W H \bar{u} \in [\mathbf{\text{m}^3 \text{s}^{-1}}]$
* Flux per Unit Width: $q = H \bar{u} \in [\mathbf{\text{m}^2 \text{s}^{-1}}]$
* Solid-Ice Accumulation Rate: $\dot{a}_i \in [\mathbf{\text{m s}^{-1}}]$
* Surface Mass Flux Density: $\dot{a}_s \in [\mathbf{\text{kg m}^{-2} \text{s}^{-1}}]$
* Dynamic Viscosity: $\bar{\nu} \in [\mathbf{\text{Pa s}}]$
* Basal Drag Coefficient: $\beta_{b, \text{reg}} \in [\mathbf{\text{Pa s m}^{-1} = \text{N s m}^{-3}}]$
* Driving Forces / Discrete Stencil: $[\mathbf{\text{N}}]$

### 2.2 Derivation of the Exact SI Continuity Equation
Integrating the 3D incompressibility condition $\nabla \cdot \mathbf{u} = 0$ over ice thickness $H(x, t)$ and channel width $W(x)$ yields:
$$\mathbf{\frac{\partial}{\partial t_{\text{sec}}}\Big(W(x) H(x, t)\Big) + \frac{\partial}{\partial x}\Big(W(x) H(x, t) \bar{u}(x, t)\Big) = W(x) \dot{a}_i(x, t)}$$

**Dimensional Reduction:**
* Term 1 (Area Change): $\frac{[W][H]}{[t]} = \frac{\text{m} \cdot \text{m}}{\text{s}} = \mathbf{\text{m}^2 \text{s}^{-1}}$
* Term 2 (Flux Divergence): $\frac{\partial (W H \bar{u})}{\partial x} = \frac{[\text{m}] [\text{m}] [\text{m s}^{-1}]}{[\text{m}]} = \mathbf{\text{m}^2 \text{s}^{-1}}$
* Term 3 (Source Term): $W \dot{a}_i = [\text{m}] \times [\text{m s}^{-1}] = \mathbf{\text{m}^2 \text{s}^{-1}}$
Every continuous term evaluates strictly to $\mathbf{\text{m}^2 \text{s}^{-1}}$.

**Discrete Finite-Volume Stencil:**
On a staggered grid where cell $i$ has length $\Delta x = x_{i+1/2} - x_{i-1/2}$:
$$\mathbf{H_i^{t+\Delta t} = H_i^t + \frac{\Delta t_{\text{sec}}}{W_i \Delta x} \Big( Q_{i-1/2}^t - Q_{i+1/2}^t \Big) + \Delta t_{\text{sec}} \dot{a}_{i}^t \quad [\text{m}]}$$

**Dimensional Check:**
$$[\Delta t_{\text{sec}}] \frac{[Q]}{[W][\Delta x]} = [\text{s}] \frac{\text{m}^3 \text{s}^{-1}}{\text{m} \cdot \text{m}} = \mathbf{\text{m}}, \qquad [\Delta t_{\text{sec}}] [\dot{a}_i] = [\text{s}] [\text{m s}^{-1}] = \mathbf{\text{m}}$$
The discrete update produces exact solid-ice thickness in **meters $[\text{m}]$**.

### 2.3 SMB Input Staging & Single Conversion Rule
The model receives the **net annual surface mass balance** $\dot{a}_{\text{we}}$ in $\text{m w.e. yr}^{-1}$ from RACMO2.3p2.
To prevent mixed-unit contamination, the input is converted **EXACTLY ONCE** upon staging into solid-ice thickness rate $\dot{a}_i$ in SI units:
$$\mathbf{\dot{a}_i(x, t) = \left(\frac{\rho_{\text{water}}}{\rho_i}\right) \frac{\dot{a}_{\text{we}}(x, t)}{\text{SecondsPerYear}} = \left(\frac{1000.0\text{ kg m}^{-3}}{917.0\text{ kg m}^{-3}}\right) \frac{\dot{a}_{\text{we}}(x, t)}{31,557,600.0\text{ s}} \approx 3.455625 \times 10^{-8} \times \dot{a}_{\text{we}}(x, t) \quad [\text{m s}^{-1}]}$$

### 2.4 Physical Disclaimer on Firn and Hydrofracture
* **Net Climate Forcing:** While RACMO2.3p2 internally calculates snowfall, sublimation, drift, melt, refreezing, and runoff, our 1D dynamic flowline model receives only the **net integrated annual surface mass balance**.
* **Zero Evolving Firn Layer Kinetics:** The model does NOT simulate time-dependent firn pore closure, liquid water percolation, or densification mechanics. $\text{FAC}(x, t)$ is ingested as a prescribed boundary field.
* **Zero Hydrofracture Fracture Mechanics:** The model does NOT solve linear elastic fracture mechanics (LEFM) or water-filled crevasse penetration equations. Embayment buttressing loss is parameterised strictly through the scenario indicator $\theta_{\text{buttress}}(t) \in [0, 1]$.

---

## 3. Issue 3 — Grounding-Line Discrete Coupling Derivation

### 3.1 Asymptotic Matched Boundary-Layer Formulation
From Schoof (2007, Eq. 32), the solid ice volume flux per unit width crossing the grounding line transition is:
$$q_{\text{unbuttressed}} = \left( \frac{\rho_i g (1 - \rho_i / \rho_{\text{ocean}})}{4^n A} \right)^{\frac{1}{m+1}} C_{\text{bed}}^{-\frac{1}{m+1}} h_{\text{GL}}^{\frac{m+n+3}{m+1}} \quad [\text{m}^2\text{ s}^{-1}]$$
where $h_{\text{GL}} = - (\rho_{\text{ocean}} / \rho_i) z_b(x_{\text{GL}})$ is the flotation thickness, with $\rho_{\text{ocean}} = 1028.0\text{ kg m}^{-3}$ and $\rho_i = 917.0\text{ kg m}^{-3}$.

Under dynamic embayment buttressing:
$$\mathbf{q_{\text{GL}}(h_{\text{GL}}, \theta_{\text{buttress}}) = q_{\text{unbuttressed}}(h_{\text{GL}}) \cdot \Big[ 1 - \omega_b \cdot \theta_{\text{buttress}}(t) \Big]^\mu \quad [\text{m}^2\text{ s}^{-1}]}$$

### 3.2 Coupling into the Staggered SSA Momentum Solver
On the staggered finite-volume mesh, the grounded domain at time $t$ terminates at continuous coordinate $x_{\text{GL}}(t)$ residing in cell $k$: $x_{\text{GL}} \in [x_{k-1/2}, x_{k+1/2}]$.

The terminal grounded velocity unknown resides on cell face $x_{k+1/2}$. In the momentum equation, the downstream boundary condition is enforced as an **essential Dirichlet condition on velocity**:
$$\mathbf{u_{k+1/2} = u_{\text{GL}} \equiv \frac{q_{\text{GL}}(h_{\text{GL}}, \theta_{\text{buttress}})}{h_{\text{GL}}} \quad [\text{m s}^{-1}]}$$

#### Mathematical Well-Posedness Proof (No Over-Constraining)
1. The 1D Shallow Shelf Approximation (SSA) is a second-order elliptic differential equation in velocity $\bar{u}(x)$:
   $$2 \frac{\partial}{\partial x} \left( W H \bar{\nu} \frac{\partial \bar{u}}{\partial x} \right) - W \tau_b - 2 H \tau_{\text{wall}} = \rho_i g W H \frac{\partial s}{\partial x}$$
2. A second-order elliptic boundary value problem requires **exactly two boundary conditions** to achieve a unique, well-posed solution:
   * Upstream boundary (Divide, $x = 0$): Dirichlet condition $\bar{u}(0) = 0.0\text{ m s}^{-1}$.
   * Downstream boundary ($x = x_{\text{GL}}$): Dirichlet condition $\bar{u}(x_{\text{GL}}) = u_{\text{GL}}$.
3. **No Over-Constraining:** The downstream boundary does NOT simultaneously prescribe longitudinal membrane stress $\partial \bar{u}/\partial x$. Membrane stress divergence inside the grounded sheet adjusts freely to satisfy internal equilibrium. The linear system is tridiagonal, irreducibly diagonally dominant, and has a unique non-singular solution.

#### Glaciological Assumptions Governing the Dirichlet Condition
The application of the Schoof Dirichlet velocity condition is valid under the following specific assumptions:
1. **Narrow Boundary Layer ($\ell_{\text{BL}} \ll \Delta x$):** The transition zone where basal drag drops to zero is narrower than the numerical grid spacing ($\ell_{\text{BL}} \sim \mathcal{O}(10\text{--}100\text{ m})$ vs $\Delta x \ge 500\text{ m}$).
2. **Hydrostatic Flotation Downstream:** The floating ice shelf immediately seaward of $x_{\text{GL}}$ satisfies Archimedean flotation.
3. **Submarine Bedrock ($z_b(x_{\text{GL}}) < 0$):** Bedrock is below sea level, ensuring positive flotation thickness $h_{\text{GL}} > 0$.
4. **Coarse-Grid Regularization:** As proven by Vieli & Payne (2005), attempting to solve coarse-grid SSA with a pure Neumann stress condition causes unphysical numerical pinning. Schoof flux matching regularizes this numerical breakdown.

### 3.3 Face-Centered Advective Mass Flux
At internal fully grounded cell faces ($j = 1/2, \dots, k-1/2$), advective volumetric flux is:
$$Q_j = W_j H_j^{\text{upwind}} u_j \quad [\text{m}^3 \text{s}^{-1}]$$
At the terminal grounding line face $k+1/2$:
$$Q_{k+1/2} = W_{\text{GL}} h_{\text{GL}} u_{\text{GL}} = W_{\text{GL}} h_{\text{GL}} \left( \frac{q_{\text{GL}}}{h_{\text{GL}}} \right) = \mathbf{W_{\text{GL}} q_{\text{GL}} \quad [\text{m}^3 \text{s}^{-1}]}$$
Advective face flux matches the Schoof discharge identically.

### 3.4 Moving Grounding-Line Position and Grounded Mass Accounting
1. **Flotation Root Finding:** At time $t+\Delta t$, updated thickness $H_i^{t+\Delta t}$ defines the flotation residual $\Delta z_{\text{flot}}(x) = H(x) + (\rho_{\text{ocean}} / \rho_i) z_b(x)$. Sub-grid root finding identifies the new continuous grounding-line position $x_{\text{GL}}^{t+\Delta t}$.
2. **Terminal Cell Friction Weighting:** The grounded cell fraction is $\lambda_{\text{GL}} = (x_{\text{GL}} - x_{k-1/2}) / \Delta x \in [0, 1]$. Basal drag in cell $k$ is scaled as $\tau_{b, k} = \lambda_{\text{GL}} \cdot \beta_b(u_k) u_k$.
3. **Discrete Eulerian Grounded Mass Accounting:**
   $$\mathbf{M_g(t) = \rho_i \left( \sum_{i=1}^{k-1} W_i H_i(t) \Delta x + \lambda_{\text{GL}}(t) W_k H_k(t) \Delta x \right) \quad [\text{kg}]}$$
4. **Analytical Audit & Zero Double-Counting Proof:**
   The continuous Reynolds Transport identity:
   $$\frac{d M_g}{dt} = \text{SMB}_g(t) - D_{\text{GL}}(t) - M_{\text{ungrounding}}(t) \quad [\text{kg s}^{-1}]$$
   where $D_{\text{GL}} = \rho_i W_{\text{GL}} q_{\text{GL}}$ and $M_{\text{ungrounding}} = - \rho_i W_{\text{GL}} h_{\text{GL}} v_{\text{GL}}$, is evaluated as an analytical verification check.
   **Double-Counting Prevention:** In the discrete numerical solver, grounded volume is calculated strictly by summing active grounded cell columns. $M_{\text{ungrounding}}$ is NOT subtracted from the cell volume, ensuring zero double-subtraction.

---

## 4. Issue 4 — Embayment Buttressing Parameterization

### 4.1 Explicit Phenomenological Classification
The parameterization:
$$q_{\text{GL}} = q_{\text{unbuttressed}} \cdot \Big[ 1 - \omega_b \cdot \theta_{\text{buttress}}(t) \Big]^\mu$$
is **strictly an empirical reduced-order parameterization**, NOT a fundamental physical law. It collapses complex 2D/3D viscoelastic ice-shelf backstress, shear-margin drag, and pinning point contact into a single scalar efficiency factor.

### 4.2 Full Mathematical Parameter Space & Surge-Ratio Sensitivity
The post-collapse surge ratio $R_{\text{surge}}$ represents the acceleration of grounding-line flux following complete buttressing loss ($\theta_{\text{buttress}} \to 0$ from $\theta_{\text{buttress}} = 1$):
$$R_{\text{surge}} = \frac{q_{\text{collapse}}}{q_{\text{buttressed}}} = \frac{1}{\Big( 1 - \omega_b \Big)^\mu}$$

Evaluating across the full theoretical parameter space $\omega_b \in [0.40, 0.85]$ and $\mu \in [1.0, 3.0]$:

| Maximum Buttressing Fraction ($\omega_b$) | Exponent $\mu = 1.0$ (Linear) | Exponent $\mu = 1.5$ (Square-Root Non-Linear) | Exponent $\mu = 2.0$ (Quadratic) | Exponent $\mu = 3.0$ (Cubic) |
| :---: | :---: | :---: | :---: | :---: |
| **$0.40$** | $1.67\times$ | $2.15\times$ | $2.78\times$ | $4.63\times$ |
| **$0.50$** | $2.00\times$ | $2.83\times$ | $4.00\times$ | $8.00\times$ |
| **$0.60$** | $2.50\times$ | $3.95\times$ | $6.25\times$ | $15.63\times$ |
| **$0.70$** | $3.33\times$ | $6.09\times$ | $11.11\times$ | $37.04\times$ |
| **$0.80$** | $5.00\times$ | $11.18\times$ | $25.00\times$ | $125.00\times$ |
| **$0.85$** | $6.67\times$ | $17.21\times$ | $44.44\times$ | **$296.30\times$** |

### 4.3 Scientific Analysis of the 2.5–6.0× Range
* **Observational Origin:** The $2.5\times\text{--}6.0\times$ acceleration range was observed by satellite radar interferometry following the 2002 Larsen B Ice Shelf collapse (Rignot et al. 2004; Scambos et al. 2004) for tributary glaciers (Crane, Jorum, Flask, Leppard).
* **Scientific Qualification:** This range is an **observational case study from one specific sector** (East Graham Land). It is NOT a universal physical constant.
* **Sensitivity Interval vs. Law:** Restricting $\omega_b \in [0.45, 0.70]$ with $\mu = 1.5$ reproduces the $2.5\times\text{--}6.0\times$ acceleration, but this is an **analyst-selected sensitivity interval**, not a proven law. Combinations such as $\omega_b = 0.85$ and $\mu = 3.0$ produce a theoretical surge of $296.3\times$, which is uncalibrated and unsupported by Peninsula observations.
* **Limitations:** The parameterization assumes instantaneous viscous adjustment, neglects transitional ice-shelf thinning, and cannot capture buttressing redistribution between adjacent embayments.
* **Independent Evidence Required Before Calibration:** In Stage 1 calibration (Phase 5.3), $\omega_b$ and $\mu$ must be constrained independently using:
  1. Satellite InSAR pre- and post-collapse velocity changes (Larsen A in 1995, Larsen B in 2002, Wordie in 1989).
  2. Diagnostic 2D backstress fields from Antarctic-wide ice-shelf inversions (Fürst et al. 2016; Reese et al. 2018).
  **Zero parameter tuning is permitted in this phase.**

---

## 5. Issue 5 — Flowline Representativeness & Glacier-to-Basin Aggregation

### 5.1 Assessment of Single-Flowline Representativeness
A single 1D flowline per basin **CANNOT scientifically represent an entire $60,000\text{--}110,000\text{ km}^2$ drainage basin**:
* **`Hp-I` (Palmer Land West, $110,265\text{ km}^2$):** Contains 8--12 major ice streams draining into George VI Sound and Marguerite Bay. A single flowline cannot resolve asynchronous retreat between the northern Dyer/Millett glaciers and southern George VI tributaries.
* **`I-Ipp` (Graham Land West, $61,053\text{ km}^2$):** Characterized by extreme alpine topography with over 30 isolated fjord catchments. Valleys have completely distinct bedrock sills, widths, and orographic precipitation rates.
* **`Ipp-J` (Graham Land East, $61,360\text{ km}^2$):** Spans Larsen A, B, and C embayments. Collapse histories are highly asynchronous (Larsen A collapsed in 1995, Larsen B in 2002, while Larsen C remains intact).

### 5.2 Multi-Flowline Ensemble Architecture
To achieve scientific representativeness without overlapping catchments, the architecture adopts a **Multi-Flowline Catchment Ensemble** (cataloged in [`phase5_2_2_1_flowline_representativeness_matrix.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/phase5_2_2_1_flowline_representativeness_matrix.csv)):

```mermaid
flowchart TD
    subgraph "Basin Grounded Area Partitioning (Phase 2.6 Boundary)"
        P1["Sub-Catchment 1 (Major Trunk)<br>Area: A_1, Flowline 1"]
        P2["Sub-Catchment 2 (Tributary / Fjord)<br>Area: A_2, Flowline 2"]
        P3["Sub-Catchment 3 (Embayment / Secondary)<br>Area: A_3, Flowline 3"]
        PAS["Passive Divide / Plateau Remainder<br>Area: A_rem = A_basin - sum(A_k)"]
    end

    subgraph "Independent 1D Dynamic Solvers"
        FL1["1D SSA Solver 1<br>Delta V_1(t)"]
        FL2["1D SSA Solver 2<br>Delta V_2(t)"]
        FL3["1D SSA Solver 3<br>Delta V_3(t)"]
        SMB_REM["Passive Column Integration<br>Delta V_rem(t) = Integral(a_dot_i) dt * A_rem"]
    end

    subgraph "Basin Volume Aggregation"
        BASIN["Complete Basin Grounded Volume Anomaly<br>Delta V_basin(t) = sum(Delta V_k) + Delta V_rem(t)"]
    end

    P1 --> FL1
    P2 --> FL2
    P3 --> FL3
    PAS --> SMB_REM

    FL1 --> BASIN
    FL2 --> BASIN
    FL3 --> BASIN
    SMB_REM --> BASIN

    style P1 fill:#e6f2ff,stroke:#1f77b4,stroke-width:2px;
    style FL1 fill:#e6ffe6,stroke:#2ca02c,stroke-width:2px;
    style BASIN fill:#f3e5f5,stroke:#9c27b0,stroke-width:2px;
```

#### Catchment Delineation and Non-Overlap Guarantee
1. **Hydrological Partitioning:** Each representative flowline $k$ is assigned a non-overlapping catchment polygon $\Omega_k$ delineated from BedMachine surface topography using standard D8 flow-routing.
2. **Disjoint Polygons:** $\Omega_j \cap \Omega_k = \emptyset$ for $j \ne k$, guaranteeing zero double-counting of ice area or volume.
3. **Passive Remainder Partition:** High-altitude, slow-moving ice divides not draining into the selected flowlines are aggregated into a passive ice-divide partition $\Omega_{\text{rem}} = \Omega_{\text{basin}} \setminus \bigcup \Omega_k$. In this partition, dynamics are negligible ($u \approx 0$), and volume evolves strictly through surface accumulation:
   $$\Delta V_{\text{rem}}(t) = \int_0^t \left( \int_{\Omega_{\text{rem}}} \dot{a}_i(x, y, \tau) \, dA \right) d\tau$$

#### Glacier-to-Basin Aggregation Formula
The total grounded volume change of basin $B$ is:
$$\mathbf{\Delta V_B(t) = \sum_{k=1}^{K_B} \Delta V_k(t) + \Delta V_{\text{rem}, B}(t) \quad [\text{km}^3]}$$
where $\Delta V_k(t)$ is the volume change simulated by the 1D dynamic flowline in sub-catchment $k$.

### 5.3 Explicit Statement of 1D Architecture Limitations
A 1D width-integrated flowline network is a **reduced-complexity physical proxy**, NOT a 3D thermomechanical ice-sheet model:
* It collapses 3D stress tensors into along-flow membrane tension, basal shear, and parameterized wall drag.
* It cannot resolve lateral tributary junctions, transverse ice transfer between valleys, or complex 2D grounding-line embayments.
* It represents the primary dynamic response of fast-flowing ice streams to climate forcing and buttressing loss, which provides a scientifically defensible dynamic backbone for Pillar 1, but its geometric limitations are acknowledged and will be evaluated in sensitivity tests.

---

## 6. Issue 6 — Bedrock Topography Smoothing Hypothesis

### 6.1 Formulation as an Unverified Numerical Hypothesis
Applying spatial Gaussian filtering to subglacial bedrock topography $z_b(x)$ is **strictly an unverified numerical hypothesis**:
* **Glaciological Risk:** Subglacial bedrock sills, peaks, and overdeepening ridges are real physical features that pin grounding lines and arrest Marine Ice Sheet Instability (MISI). Smoothing the bedrock erodes these pinning sills, which may induce artificial, unphysical runaway grounding-line retreat!
* **Numerical Counter-Risk:** Unsmoothed raw bedrock profiles interpolated from radar grids may contain sub-kilometer step artifacts or interpolation noise that can cause local surface slope kinks and slow down Picard iteration convergence.

### 6.2 Experimental Sensitivity Design (Test 16)
To resolve this trade-off objectively, bedrock filtering is formulated as an explicit experimental test suite (cataloged in [`phase5_2_2_1_bedrock_smoothing_experiment_design.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/phase5_2_2_1_bedrock_smoothing_experiment_design.csv)):

1. **Reference Baseline ($\sigma = 0\text{ km}$):** Unsmoothed BedMachine V4.1 bedrock interpolated directly onto the flowline mesh. All dynamic simulations will run on this unsmoothed profile by default.
2. **Candidate Filter Scales:**
   * $\sigma = 0.5 \Delta x = 0.5\text{ km}$ (minimal sub-grid spike damping).
   * $\sigma = 1.0 \Delta x = 1.0\text{ km}$ (grid-scale filter).
   * $\sigma = 2.0 \Delta x = 2.0\text{ km}$ (macro-scale valley smoothing).
3. **Objective Evaluation Criteria in Test 16:**
   * **Sill Preservation Metric:** $\max |z_{b, \text{filtered}} - z_{b, \text{raw}}|$ at local bathymetric maxima must be documented.
   * **Grounding-Line Displacement:** Shift in steady-state position $|x_{\text{GL}}(\sigma) - x_{\text{GL}}(0)|$.
   * **Picard Convergence:** Average iteration count per time step across filter scales.
* **Implementation Protocol:** **No universal smoothing scale will be imposed.** The raw profile remains the authoritative reference. A smoothing filter will only be adopted if Test 16 proves that raw topography causes Picard divergence AND that the filter preserves critical pinning sills.

---

## 7. Issue 7 — Reassessment of Numerical Verification Thresholds

The numerical acceptance thresholds are rigorously defined with scientific and numerical justifications (cataloged in [`phase5_2_2_1_verification_threshold_justifications.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/phase5_2_2_1_verification_threshold_justifications.csv)):

### 7.1 Mass Conservation Relative Residual: $\le 1.0 \times 10^{-7}$
* **Mathematical Definition:**
  $$\epsilon_{\text{mass}} = \frac{\left| M_g(t) - M_g(0) - \int_0^t \Big( \text{SMB}_g(\tau) - D_{\text{GL}}(\tau) - M_{\text{ungrounding}}(\tau) \Big) d\tau \right|}{M_g(0)}$$
* **Scientific Justification:** Conservation of mass is an exact physical law. Over a forward simulation, grounded mass change must equal net boundary mass exchange.
* **Numerical Justification:** Under finite-volume staggered differencing, internal fluxes cancel telescopically to machine precision ($\approx 10^{-15}$). Across $10^4$ timesteps in double precision ($\epsilon_{\text{mach}} \approx 1.11 \times 10^{-16}$), roundoff error accumulates as $\sqrt{N} \epsilon_{\text{mach}} \approx 10^{-14}$. When combined with sub-grid linear boundary tracking for $M_{\text{ungrounding}}$, truncation residuals remain $\le 1.0 \times 10^{-7}$.
* **Measurement Procedure:** Cumulative mass and boundary fluxes logged at every time step; residual evaluated at $t = 100\text{ yr}$.
* **Classification:** **Hard Acceptance Criterion.**

### 7.2 Spatial Mesh Convergence: $\le 2.0\%$ (1 km to 0.5 km) and $\le 1.0\%$ (0.5 km to 0.25 km)
* **Mathematical Definition:**
  $$\epsilon_{\text{spatial}} = \frac{\| V_{\Delta x}(t) - V_{\Delta x/2}(t) \|_2}{\| V_{\Delta x/2}(t) \|_2}$$
* **Scientific Justification:** Model projections must reflect climate forcing, not spatial grid resolution artifacts.
* **Numerical Justification:** Central finite differencing for the elliptic SSA is second-order accurate $\mathcal{O}(\Delta x^2)$, while upwind continuity is first-order accurate $\mathcal{O}(\Delta x)$. Refining $\Delta x$ from $1.0\text{ km}$ to $0.5\text{ km}$ reduces truncation error by a factor of 2 to 4. In complex alpine valleys, standard glaciological discretization discrepancies range between $1\%\text{ and } 3\%$ (Pattyn et al. 2012 ISMIP-HOM).
* **Measurement Procedure:** Identical 100-year forward runs executed at $\Delta x \in \{2.0, 1.0, 0.5, 0.25\}\text{ km}$.
* **Classification:** **Initial Target Metric** (Classified as a target pending empirical convergence testing in Phase 5.2.2).

### 7.3 Temporal Timestep Convergence: $\le 0.5\%$
* **Mathematical Definition:**
  $$\epsilon_{\text{temporal}} = \frac{| V_{\Delta t}(t) - V_{\Delta t_{\text{ref}}}(t) |}{V_{\Delta t_{\text{ref}}}(t)}$$
* **Scientific Justification:** Timestep size must not alter decadal mass loss trajectories or dynamic retreat timing.
* **Numerical Justification:** Forward Euler time-stepping is first-order accurate $\mathcal{O}(\Delta t)$. With reference step $\Delta t_{\text{ref}} = 0.005\text{ yr}$ ($\approx 1.83\text{ d}$) and operational steps $\Delta t \in [0.01, 0.05]\text{ yr}$, temporal error is small compared to spatial truncation error when Courant $C_{\text{CFL}} \le 0.50$ is enforced.
* **Measurement Procedure:** Forward volume at operational step $\Delta t = 0.05\text{ yr}$ compared against reference step $\Delta t_{\text{ref}} = 0.005\text{ yr}$ at $t = 50\text{ yr}$.
* **Classification:** **Hard Acceptance Criterion.**

### 7.4 Grounding-Line Discrete Flux Jump: $\le 1.0\%$
* **Mathematical Definition:**
  $$\Delta q_{\text{jump}} = \frac{|q_{\text{GL}}(t^+) - q_{\text{GL}}(t^-)|}{q_{\text{GL}}(t^-)}$$
  evaluated as $x_{\text{GL}}(t)$ crosses an integer grid node $x_k$.
* **Scientific Justification:** Discontinuous discharge spikes during node transitions are unphysical artifacts of integer grid snapping.
* **Numerical Justification:** Sub-grid flotation tracking with linear friction smoothing $\lambda_{\text{GL}}$ ensures continuous boundary mobility. Truncation errors across cell faces produce small residual flux jumps. A threshold of $\le 1.0\%$ prevents artificial shock waves from exciting numerical ringing (Feldmann et al. 2014).
* **Measurement Procedure:** Sample $q_{\text{GL}}$ at high frequency ($\Delta t = 0.005\text{ yr}$) during cell boundary crossings in Test 13.
* **Classification:** **Initial Target Metric.**

---

## 8. Summary of Deliverables & Changed Artifacts

| Deliverable Artifact | Path | Scope of Scientific Revisions |
| :--- | :--- | :--- |
| **Scientific Architecture Correction Report** | [`phase5_2_2_1_scientific_architecture_correction.md`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/phase5_2_2_1_scientific_architecture_correction.md) | Master architectural revision resolving all 7 review issues. |
| **Geometry & Firn Transformations Table** | [`phase5_2_2_1_geometry_firn_transformations.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/phase5_2_2_1_geometry_firn_transformations.csv) | Reconciled BedMachine `thickness` vs `surface`; eliminated double-FAC subtraction. |
| **Flowline Representativeness Matrix** | [`phase5_2_2_1_flowline_representativeness_matrix.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/phase5_2_2_1_flowline_representativeness_matrix.csv) | Designed Multi-Flowline Catchment Ensemble; formalized basin volume aggregation formulas. |
| **Verification Threshold Justifications Table** | [`phase5_2_2_1_verification_threshold_justifications.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/phase5_2_2_1_verification_threshold_justifications.csv) | Reassessed 4 thresholds with scientific, numerical, and measurement justifications. |
| **Bedrock Smoothing Experiment Design Table** | [`phase5_2_2_1_bedrock_smoothing_experiment_design.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/phase5_2_2_1_bedrock_smoothing_experiment_design.csv) | Formulated bedrock filtering as Test 16 sensitivity hypothesis with raw profile baseline. |
| **Brain Mirror Directory** | [`brain/52ad6ae8-887d-48db-85e7-7d53f431979f/`](file:///c:/Users/akash/.gemini/antigravity/brain/52ad6ae8-887d-48db-85e7-7d53f431979f/) | Synchronized all architectural markdown reports and data tables. |

---

## 9. Governance & Final Determination

```
========================================================================================================
FINAL FORMAL DETERMINATION: PASS — READY FOR IMPLEMENTATION AUTHORIZATION REVIEW
========================================================================================================
1. Geometry & Firn:              RECONCILED: BedMachine thickness is solid ice; surface is ice-equivalent;
                                 REMA gives geometric snow surface. Zero double-subtraction of FAC.
2. Canonical SI System:          CLOSED: Pure SI units (m, s, kg) enforced internally; SMB converted
                                 exactly once (3.4556e-8 * a_dot_we); firn kinetics/hydrofracture disclaimed.
3. Grounding-Line Coupling:      DERIVED: Schoof flux, SSA solve, Dirichlet velocity, face flux, and
                                 moving boundary position coupled without over-constraining or double-counting.
4. Buttressing Phenomenology:    QUALIFIED: Surge ratio 2.5-6x classified as empirical case-study benchmark;
                                 full parameter space [1.67x, 296.3x] documented; zero tuning in this phase.
5. Flowline Representativeness:  RESOLVED: Multi-flowline catchment ensemble designed with non-overlapping
                                 catchments and explicit passive divide partitioning; 1D limitations documented.
6. Bedrock Smoothing Hypothesis: FORMULATED: Raw profile established as baseline; filtering classified as
                                 unverified hypothesis tested across 4 candidate scales in Test 16.
7. Verification Thresholds:      JUSTIFIED: Mass conservation (1e-7) and temporal (0.5%) classified as Hard
                                 Acceptance Criteria; spatial (1%) and flux jump (1%) as Initial Targets.
8. Implementation Status:        PHASE 5.2.2 IMPLEMENTATION REMAINS STRICTLY LOCKED.
                                 Separate explicit approval required after independent review.
========================================================================================================
```

