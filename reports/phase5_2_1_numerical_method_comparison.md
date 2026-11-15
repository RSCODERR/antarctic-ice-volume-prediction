# Phase 5.2.1 — Numerical Method Selection and Comparative Analysis Report (Final Numerical & Constitutive Corrections Edition)

**Author:** Antigravity Cryospheric Modeling & Computational Physics Group  
**Date:** 2026-11-08 (Final Numerical & Constitutive Corrections Edition)  
**Project:** Antarctic Peninsula Grounded-Ice Volume Change Prediction  
**Basins Evaluated:** `Hp-I`, `I-Ipp`, `Ipp-J`, and Regional `Domain A`  
**Governing Protocol:** Authoritative Phase 5.1.2 Authorization Correction & Two-Pillar Independence Protocol  
**Phase Status:** Complete Numerical Design, Matrix Discretization & Stencil Specification  
**Determination:** **PASS — ready for a separate implementation authorization review (Phase 5.2.2 Implementation Remains Locked)**  

---

## 1. Executive Summary & Objective

The objective of this analysis is to evaluate and select the optimal numerical integration method for the **Phase 5.2 Pure Physical Dynamic Backbone (Pillar 1)**. The solver integrates the 1D width-integrated flowline continuity equation:

$$\frac{\partial}{\partial t}\Big(W(x) H(x, t)\Big) + \frac{\partial}{\partial x}\Big(W(x) H(x, t) \bar{u}(x, t)\Big) = W(x) \dot{a}_i(x, t) = W(x) \left(\frac{\rho_{\text{water}}}{\rho_i}\right) \dot{a}_{\text{we}}(x, t)$$

coupled to the 1D Shallow Shelf Equation with regularized basal and lateral drag:

$$2 \frac{\partial}{\partial x} \left( W(x) H(x, t) \bar{\nu} \frac{\partial \bar{u}}{\partial x} \right) - W(x) \tau_{b, \text{reg}}(x) - 2 H(x, t) \tau_{\text{wall}, \text{reg}}(x) = \rho_i g W(x) H(x, t) \frac{\partial s}{\partial x}$$

and the authoritative buttressed grounding-line boundary flux:

$$q_{\text{GL}}(h_{\text{GL}}, \theta_{\text{buttress}}) = q_{\text{unbuttressed}}(h_{\text{GL}}) \cdot \Big[ 1 - \omega_b \cdot \theta_{\text{buttress}}(t) \Big]^\mu$$

over decadal-to-centennial timescales ($1979\text{--}2100$).

### Key Scientific & Numerical Principles:
1. **Dimensional Consistency in Continuity Source Term:** The fresh water reference density $\rho_{\text{water}} = 1000.0\text{ kg m}^{-3}$ is explicitly accounted for when converting water-equivalent SMB $\dot{a}_{\text{we}}$ into solid-ice thickness accumulation rate: $\dot{a}_i = \frac{1000}{917} \dot{a}_{\text{we}} = 1.09051 \times \dot{a}_{\text{we}}$. Both sides of the continuity equation have exact SI units of $\mathbf{\text{m}^2 \text{s}^{-1}}$.
2. **Boundary Classification at Divide ($x = 0$):** Pinned at the upstream face by a **homogeneous Dirichlet condition on velocity** ($\bar{u}_{1/2} = 0.0\text{ m s}^{-1}$), complemented by a **homogeneous Neumann condition on surface elevation** ($s_0 = s_1$).
3. **Control-Volume Finite-Volume Discretization:** Integrating the momentum equation across a finite-volume cell of length $\Delta x$ yields exact discrete forces in **Newtons $[\text{N}]$** (Form 1) or length-averaged forces in **$[\text{N m}^{-1}]$** (Form 2).
4. **Smooth Drag Regularization & Arithmetic:** Non-linear basal and lateral drag coefficients are regularized with threshold $u_{\text{reg}} = 10^{-4}\text{ m yr}^{-1} \approx 3.17 \times 10^{-12}\text{ m s}^{-1}$. Recalculated in consistent SI units: $\beta_{b, \text{reg}}(0) = C_{\text{bed}} u_{\text{reg}}^{-2/3} = \mathbf{4.6352 \times 10^{14}\text{ Pa s m}^{-1}}$ (correcting earlier $4.64 \times 10^{10}$ draft slip).
5. **Exact Lateral Drag Shear-Stress Resolution:** The tensorial factor of $1/2$ in Glen's flow law ($\dot{\varepsilon}_{xy} = \frac{1}{2} |\partial u/\partial y| = A \tau_{xy}^n$) cancels identically with the factor of 10 in the parabolic wall velocity gradient ($|\partial u/\partial y|_{\text{wall}} = 10 \bar{u}/W$), rigorously yielding $\tau_{\text{wall}} = (5 \bar{u} / (A W))^{1/n}$. Explicitly qualified as a reduced-order scalar shear approximation uncoupled from longitudinal strain.
6. **Separation of Stability Properties:** Matrix non-singularity and Thomas algorithm pivot safety do not imply blanket unconditional stability for the non-linear coupled physical model; Picard iteration convergence and time-dependent advective CFL constraints dictate conditional stability.

---

## 2. Demonstration of the Actual SSA Staggered-Grid Discretization

The 1D SSA momentum equation is discretized on a staggered finite-volume mesh:

### 2.1 Staggered-Grid Architecture
* **Grid Cells:** $N$ cells indexed $i = 1, 2, \dots, N$.
* **Cell Centers ($x_i$):** Store ice thickness $H_i$, firn air content $\text{FAC}_i$, width $W_i$, bedrock elevation $z_{b,i}$, surface elevation $s_i = z_{b,i} + H_i + \text{FAC}_i$, and effective viscosity $\bar{\nu}_i$.
* **Cell Faces ($x_{i+1/2}$):** Store depth-averaged velocity unknowns $u_{i+1/2}$ and mass fluxes $Q_{i+1/2}$.

### 2.2 Regularized Linearization of Non-Linear Terms
At each non-linear Picard iteration $k \to k+1$:
1. **Effective Viscosity at Cell Centers:**
   $$\left(\frac{\partial \bar{u}}{\partial x}\right)_i^k = \frac{u_{i+1/2}^k - u_{i-1/2}^k}{\Delta x}$$
   $$\bar{\nu}_i^k = \frac{1}{2} A_i^{-1/n} \left[ \left(\left(\frac{\partial \bar{u}}{\partial x}\right)_i^k\right)^2 + \dot{\varepsilon}_0^2 \right]^{\frac{1-n}{2n}} \quad [\text{Pa s}]$$
   where $\dot{\varepsilon}_0 = 10^{-10}\text{ s}^{-1} \approx 3.15 \times 10^{-3}\text{ yr}^{-1}$ regularizes the divide strain rate.
2. **Smooth Basal Drag Linearization:**
   $$\beta_{b, \text{reg}, i+1/2}^k = C_{\text{bed}, i+1/2} \left[ (u_{i+1/2}^k)^2 + u_{\text{reg}}^2 \right]^{\frac{m-1}{2}} \quad [\text{Pa (m s}^{-1})^{-1} = \text{N s m}^{-3}]$$
   $$\tau_{b, \text{reg}, i+1/2}^{k+1} = \beta_{b, \text{reg}, i+1/2}^k \cdot u_{i+1/2}^{k+1} \quad [\text{Pa} = \text{N m}^{-2}]$$
   At $u = 0$, $\beta_{b, \text{reg}}(0) = C_{\text{bed}} u_{\text{reg}}^{-2/3} = \mathbf{4.6352 \times 10^{14}\text{ Pa s m}^{-1}}$.
3. **Smooth Lateral Drag Linearization (Factor-of-2 Resolved):**
   $$\beta_{\text{wall}, \text{reg}, i+1/2}^k = \left( \frac{5}{A_{i+1/2} W_{i+1/2}} \right)^{1/n} \left[ (u_{i+1/2}^k)^2 + u_{\text{reg}}^2 \right]^{\frac{1-n}{2n}} \quad [\text{Pa (m s}^{-1})^{-1} = \text{N s m}^{-3}]$$
   $$\tau_{\text{wall}, \text{reg}, i+1/2}^{k+1} = \beta_{\text{wall}, \text{reg}, i+1/2}^k \cdot u_{i+1/2}^{k+1} \quad [\text{Pa} = \text{N m}^{-2}]$$

---

### 2.3 Interior Stencil Formulations

#### Form 1: Control-Volume Integrated in Newtons $[\text{N}]$ (Primary Formulation)
Integrating the momentum conservation equation across the face control volume $x \in [x_i, x_{i+1}]$ of length $\Delta x$:

$$\int_{x_i}^{x_{i+1}} \left[ 2 \frac{\partial}{\partial x}\left( W H \bar{\nu} \frac{\partial \bar{u}}{\partial x} \right) - W \tau_b - 2 H \tau_{\text{wall}} \right] dx = \int_{x_i}^{x_{i+1}} \rho_i g W H \frac{\partial s}{\partial x} dx$$

Yields the discrete linear algebraic system:
$$\mathbf{- A_{i+1/2} u_{i-1/2}^{k+1} + B_{i+1/2} u_{i+1/2}^{k+1} - C_{i+1/2} u_{i+3/2}^{k+1} = F_{i+1/2}}$$

Where:
* **Lower Band Conductance:** $A_{i+1/2} = \frac{2 (W H \bar{\nu})_i^k}{\Delta x} \quad [\text{N s m}^{-1} = \text{kg s}^{-1}]$
* **Upper Band Conductance:** $C_{i+1/2} = \frac{2 (W H \bar{\nu})_{i+1}^k}{\Delta x} \quad [\text{N s m}^{-1} = \text{kg s}^{-1}]$
* **Drag Dissipation Coefficient:** $D_{i+1/2}^k = \left( W_{i+1/2} \beta_{b, \text{reg}, i+1/2}^k + 2 H_{i+1/2} \beta_{\text{wall}, \text{reg}, i+1/2}^k \right) \Delta x \quad [\text{N s m}^{-1} = \text{kg s}^{-1}]$
* **Main Diagonal Coefficient:** $B_{i+1/2} = A_{i+1/2} + C_{i+1/2} + D_{i+1/2}^k \quad [\text{N s m}^{-1} = \text{kg s}^{-1}]$
* **Right-Hand Side Driving Force:** $F_{i+1/2} = \rho_i g (W H)_{i+1/2} (s_i - s_{i+1}) \quad [\text{N}]$

**Dimensional Verification for Form 1:**
$$[A_{i+1/2} u] = [\text{N s m}^{-1}] \times [\text{m s}^{-1}] = \mathbf{\text{N}}, \quad [B_{i+1/2} u] = \mathbf{\text{N}}, \quad [F_{i+1/2}] = \mathbf{\text{N}}$$

---

#### Form 2: Divided by Grid Spacing $\Delta x$ in Force per Unit Length $[\text{N m}^{-1}]$
Dividing Form 1 through by $\Delta x$:
$$\mathbf{- A'_{i+1/2} u_{i-1/2}^{k+1} + B'_{i+1/2} u_{i+1/2}^{k+1} - C'_{i+1/2} u_{i+3/2}^{k+1} = F'_{i+1/2}}$$

Where:
* $A'_{i+1/2} = \frac{2 (W H \bar{\nu})_i^k}{\Delta x^2} \in \mathbf{[\text{N s m}^{-2} = \text{Pa s}]}$
* $C'_{i+1/2} = \frac{2 (W H \bar{\nu})_{i+1}^k}{\Delta x^2} \in \mathbf{[\text{N s m}^{-2} = \text{Pa s}]}$
* $D'_{i+1/2}^k = W_{i+1/2} \beta_{b, \text{reg}, i+1/2}^k + 2 H_{i+1/2} \beta_{\text{wall}, \text{reg}, i+1/2}^k \in \mathbf{[\text{N s m}^{-2} = \text{Pa s}]}$
* $B'_{i+1/2} = A'_{i+1/2} + C'_{i+1/2} + D'_{i+1/2}^k \in \mathbf{[\text{N s m}^{-2} = \text{Pa s}]}$
* $F'_{i+1/2} = \rho_i g (W H)_{i+1/2} \left(\frac{s_i - s_{i+1}}{\Delta x}\right) \in \mathbf{[\text{N m}^{-1}]}$

---

### 2.4 Boundary Stencils
1. **Divide Boundary ($i = 0$, Face $x_{1/2} = 0$):**
   Homogeneous Dirichlet condition: $u_{1/2}^{k+1} = 0.0$.
   Row 1 of the tridiagonal matrix: $A_{1/2} = 0, B_{1/2} = 1.0, C_{1/2} = 0, F_{1/2} = 0.0$.
2. **Grounding-Line Boundary (Face $x_{N+1/2} = x_{\text{GL}}$):**
   Dirichlet velocity condition: $u_{N+1/2}^{k+1} = u_{\text{GL}}^t = \frac{q_{\text{GL}}(h_{\text{GL}}^t, \theta_{\text{buttress}}^t)}{h_{\text{GL}}^t}$.
   Row $N+1$ of the tridiagonal matrix: $A_{N+1/2} = 0, B_{N+1/2} = 1.0, C_{N+1/2} = 0, F_{N+1/2} = u_{\text{GL}}^t$.

---

### 2.5 Rigorous Delineation of Stability Properties

1. **Diagonal Dominance & Linear Non-Singularity:**
   - In every interior row $i+1/2$:
     $$|B_{i+1/2}| - \Big( |A_{i+1/2}| + |C_{i+1/2}| \Big) = D_{i+1/2}^k \ge 0$$
   - When basal or lateral drag is active ($D_i > 0$), the interior row is **strictly diagonally dominant**.
   - If an ungrounded or frictionless section has $D_i = 0$, the row is **weakly diagonally dominant** ($|B| = |A| + |C|$).
   - Because both boundary rows are fixed by Dirichlet conditions ($|B_{1/2}| = 1 > 0$, $|B_{N+1/2}| = 1 > 0$), the global matrix is **irreducibly diagonally dominant**.
   - By Taussky's Theorem (1949), the matrix is guaranteed to be **nonsingular**.
2. **Symmetric Positive Definiteness (SPD):**
   - Irreducible diagonal dominance alone does not imply positive definiteness.
   - When Dirichlet boundary values are partitioned into the RHS, the reduced $(N-1) \times (N-1)$ interior operator $\tilde{M}$ is strictly symmetric ($\tilde{M}_{i, i-1} \equiv \tilde{M}_{i-1, i}$) with strictly positive eigenvalues ($\lambda_i > 0$), proving SPD.
3. **Thomas Algorithm Pivot Safety & Backward Stability:**
   - For irreducibly diagonally dominant tridiagonal matrices with $A_i, C_i > 0$ and $B_i \ge A_i + C_i$, Gaussian elimination without pivoting (the Thomas algorithm) has strictly positive elimination pivots $d_i > C_i > 0$, guaranteeing zero pivot failure in exact arithmetic.
   - Higham (2002) proves that the algorithm is **backward stable**: $\|\delta M\|_\infty \le 3 \epsilon_{\text{mach}} \|M\|_\infty$.
4. **Condition Number & Forward Error Scaling:**
   - As $\Delta x \to 0$, the condition number scales as:
     $$\kappa(M) \approx \mathcal{O}\left( N^2 \cdot \frac{\max B_i}{\min B_i} \right)$$
   - With $N = 100$ and coefficient contrast $\approx 10^4$, $\kappa(M) \approx 10^8$. In double-precision arithmetic, this causes a precision loss of $\approx 8$ digits, leaving $\approx 8$ reliable digits (relative error $\approx 10^{-8}$).
5. **Picard Non-Linear Convergence & Operational Defaults:**
   - Solving the linear matrix at step $k$ does NOT guarantee Picard convergence for non-linear power-law rheologies ($n=3$).
   - `max_iter = 25` and $\omega_{\text{relax}} = 0.60$ are **operational defaults/heuristics**, not universal mathematical constants.
   - If Picard iterations fail to converge within 25 iterations, the emergency controller triggers adaptive timestep halving ($\Delta t \leftarrow \Delta t / 2$), which reduces incremental deformation and restores convergence.
6. **Coupled Time-Dependent Stability (Conditional Stability):**
   - The overall physical ice flow model is **conditionally stable**, bounded by the advective Courant-Friedrichs-Lewy (CFL) limit:
     $$\Delta t \le C_{\text{CFL}} \frac{\Delta x}{u_{\text{max}}}, \quad C_{\text{CFL}} = 0.50$$
   - All blanket claims of "unconditional stability" are formally revoked.

---

## 3. Qualification of the Lateral-Drag Approximation

The lateral drag parameterization:
$$\tau_{\text{wall}} = \left( \frac{5 \bar{u}}{A(T) W} \right)^{\frac{1}{n}} \quad [\text{Pa}], \qquad F_{\text{lat}} = 2 H \tau_{\text{wall}} \quad [\text{N m}^{-1}]$$
is explicitly classified as a **reduced-order geometry-dependent approximation** with the following glaciological limitations:
1. **Rectangular Trough Assumption:** Assumes vertical rock sidewalls; real alpine valleys in Graham Land are parabolic or trapezoidal.
2. **Prescribed Power-Law Shear:** Assumes $u(y) = u_c [1 - |2y/W|^{n+1}]$; does not resolve shear-margin damage or localized strain heating.
3. **No-Slip Wall Boundaries:** Assumes $u(\pm W/2) = 0$; subglacial water may permit lateral slippage.
4. **Channel Confinement Validity Limit ($W/H \le 10$):** Valid in narrow alpine valleys (Basin `I-Ipp`, $W \approx 2\text{--}5\text{ km}$). In wide unconfined ice streams (Basin `Hp-I`, $W > 20\text{--}50\text{ km}$), lateral drag decays naturally as $(2H/W) \to 0$. Universal validity across all Peninsula glaciers is **NOT claimed**. A dedicated sensitivity suite (Test 14) evaluates alternative trough geometries and aspect ratios.

---

## 4. Timestep Specifications & Adaptive Controller Protocol

To reconcile operational routines, test protocols, and stability limits:

| Timestep Specification | Value / Range | Operational Role & Governing Mechanics |
| :--- | :---: | :--- |
| **Operational Adaptive Range** | $\Delta t_{\text{oper}} \in [0.01, 0.10]\text{ yr}$ | Production forward simulation window. Driven by adaptive Courant controller. |
| **Reference Benchmark Step** | $\Delta t_{\text{ref}} = 0.005\text{ yr}$ | Dedicated high-resolution validation step strictly used in Test 12. |
| **Minimum Permitted Floor** | $\Delta t_{\text{min}} = 0.001\text{ yr} \approx 8.76\text{ h}$ | Lower boundary floor permitted under adaptive step halving. |
| **Maximum Permitted Ceiling** | $\Delta t_{\text{max}} = 0.25\text{ yr}$ | Upper bound capped by CFL condition ($C_{\text{CFL}} \le 0.50$) and grounding line speed. |

### Emergency Divergence Protocol:
If the Picard non-linear solver fails to reach convergence ($\epsilon_{\text{Picard}} < 10^{-5}$) within 25 iterations:
1. The timestep is halved: $\Delta t \leftarrow \Delta t / 2$.
2. If $\Delta t < \Delta t_{\text{min}} = 0.001\text{ yr}$, the solver **halts execution immediately**, raises `NonlinearConvergenceError`, generates a full diagnostic state dump (residual norms, geometry, velocities), and exits with non-zero status.

---

## 5. Sub-Grid Grounding Line Migration & Friction Smoothing

* Continuous flotation root: $x_{\text{GL}} = x_k + \Delta x \left( \frac{\Delta z_{\text{flot}}(x_k)}{\Delta z_{\text{flot}}(x_k) - \Delta z_{\text{flot}}(x_{k+1})} \right)$.
* Sub-grid friction smoothing: $\tau_{b, \text{cell } k} = \lambda_{\text{GL}} \cdot C_{\text{bed}} [u_k^2 + u_{\text{reg}}^2]^{\frac{m-1}{2}} u_k$, where $\lambda_{\text{GL}} = (x_{\text{GL}} - x_k)/\Delta x \in [0, 1]$.
* **Evidence-Based Qualification:** Rather than claiming categorical eradication of numerical ringing on paper, this scheme is formulated as a computational hypothesis to mitigate cell-pinning shocks, and will be rigorously tested against the 6-case validation criteria in Test 13.

---

## 6. Final Architecture Specification

```
========================================================================================================
FINAL NUMERICAL ARCHITECTURE SPECIFICATION
========================================================================================================
1. Spatial Discretization:   1D Width-Integrated Finite-Volume on Staggered Grid.
2. Stencil Structure:        Irreducibly Diagonally Dominant Tridiagonal SSA Matrix in Newtons [N].
3. Linear Solver:            Thomas Algorithm (TDMA) executing in O(N) operations without pivoting.
4. Non-Linear Solver:        Picard Iteration with Under-Relaxation (omega in [0.4, 0.7], tol = 1e-5).
5. Drag Regularization:      u_reg = 1e-4 m/yr (3.17e-12 m/s); beta_b(0) = 4.6352e14 Pa s m^-1 in SI units.
6. Lateral Drag Formula:     tau_wall = (5 * u_bar / (A * W))^(1/n); reduced-order pure-shear approximation.
7. Continuity Source Term:   W(x) * a_dot_i = W(x) * (rho_water / rho_i) * a_dot_we = 1.09051 * W * a_dot_we.
8. Divide Boundary:          Homogeneous Dirichlet on Velocity (u_1/2 = 0); Homogeneous Neumann on Surface.
9. Grounding-Line Boundary:  Dirichlet Velocity: u_GL = q_GL / h_GL from Buttressed Schoof Flux.
                             Discrete Eulerian cell divergence prevents double-counting with ungrounding.
10. Sub-Grid Tracking:       Continuous Flotation Root + Friction Smoothing lambda_GL (Test 13 validation).
11. Timestep Hierarchy:      Operational [0.01, 0.10] yr; Ref 0.005 yr; Floor 0.001 yr; Ceiling 0.25 yr.
12. Stability Class:         CONDITIONALLY STABLE (Governed by Picard convergence & CFL limits).
========================================================================================================
```
