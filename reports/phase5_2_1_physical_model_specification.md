# Phase 5.2.1 — Mathematical Specification of the Reduced-Complexity Physical Model (Final Numerical & Constitutive Corrections Edition)

**Author:** Antigravity Cryospheric Modeling & Computational Physics Group  
**Date:** 2026-11-08 (Final Numerical & Constitutive Corrections Edition)  
**Project:** Antarctic Peninsula Grounded-Ice Volume Change Prediction  
**Basins Evaluated:** `Hp-I`, `I-Ipp`, `Ipp-J`, and Regional `Domain A`  
**Governing Protocol:** Authoritative Phase 5.1.2 Authorization Correction & Two-Pillar Independence Protocol  
**Phase Status:** Mathematical & Numerical Specification Phase (Zero Code Execution Permitted)  
**Determination:** **PASS — ready for a separate implementation authorization review (Phase 5.2.2 Implementation Remains Locked)**  

---

## Revision Log: Final Numerical & Constitutive Corrections

| Revision Item | Previous Working Draft | Corrected Scientific Specification | Mathematical & Physical Justification |
| :--- | :--- | :--- | :--- |
| **1. Basal-Drag Regularization Arithmetic** | Reported $\beta_{b, \text{reg}}(0) = 4.64 \times 10^{10}\text{ Pa s m}^{-1}$. | Recalculated rigorously in SI units: $\beta_{b, \text{reg}}(0) = C_{\text{bed}} u_{\text{reg}}^{-2/3} = \mathbf{4.6352 \times 10^{14}\text{ Pa s m}^{-1}}$ (or $[\text{N s m}^{-3}]$). | Input: $C_{\text{bed}} = 10^7\text{ Pa (m s}^{-1})^{-1/3}$, $u_{\text{reg}} = 10^{-4}\text{ m yr}^{-1} = 3.16881 \times 10^{-12}\text{ m s}^{-1}$. Then $u_{\text{reg}}^{-2/3} = 4.63521 \times 10^7\text{ (m s}^{-1})^{-2/3}$. Product yields $4.6352 \times 10^{14}\text{ Pa s m}^{-1}$. The previous value was an arithmetic error underestimating the coefficient by $10^4$. Assessed conditioning and Picard convergence. |
| **2. Linear-Solver Stability Terminology** | Inferred positive definiteness and "unconditional stability" of Thomas algorithm from diagonal dominance. | Rigorously separated non-singularity (Taussky's theorem on irreducible diagonal dominance), positive definiteness (requires symmetry via Dirichlet boundary partitioning), and Thomas algorithm pivot safety ($d_i > C_i \ge 0$) from condition number $\kappa(M)$ and forward error. | Irreducible diagonal dominance guarantees non-singularity, not positive definiteness (which requires symmetry). Thomas algorithm is backward stable (Higham 2002), but forward error is bounded by $\kappa(M) \sim \mathcal{O}(N^2 \cdot \text{contrast})$. Blanket claims of "unconditional stability" revoked. |
| **3. Lateral Glen-Law Constitutive Derivation** | Presented scalar lateral drag as an exact tensorial equivalence. | Formally derived from Cauchy stress, symmetric strain-rate tensor, second invariants ($\dot{\varepsilon}_e = \sqrt{\frac{1}{2}\dot{\varepsilon}_{ij}\dot{\varepsilon}_{ij}}$, $\tau_e = \sqrt{\frac{1}{2}\tau_{ij}\tau_{ij}}$), and Glen's flow law. Specialised to horizontal pure shear flow $\mathbf{u} = (u(y), 0, 0)$. | In pure shear, $\dot{\varepsilon}_e = \frac{1}{2}|\partial u/\partial y|$ and $\tau_e = |\tau_{xy}|$. Equating gives $\frac{1}{2}|\partial u/\partial y| = A \tau_{xy}^n \implies \tau_{xy} = (\frac{1}{2A}|\partial u/\partial y|)^{1/n}$. Wall gradient $|\partial u/\partial y|_{\text{wall}} = 10 \bar{u}/W$ cancels $1/2$, yielding $\tau_{\text{wall}} = (5 \bar{u} / (AW))^{1/n}$. Explicitly qualified as a **reduced-order scalar pure-shear approximation** uncoupled from longitudinal strain. |
| **4. Grounding-Line Boundary Coupling & Double-Counting** | Prescribed grounding-line velocity without formal coupling derivation or discrete double-counting proof. | Proved that prescribing Dirichlet velocity $u_{\text{GL}} = q_{\text{GL}}/h_{\text{GL}}$ closes the second-order elliptic SSA on coarse grids where boundary layers cannot be resolved. Delineated continuous Reynolds Transport mass budget from discrete Eulerian cell updates. | Continuous identity $\frac{d M_g}{dt} = \text{SMB}_g - D_{\text{GL}} - M_{\text{ungrounding}}$ is an exact moving-boundary integral balance where $D_{\text{GL}}$ (advection) and $M_{\text{ungrounding}}$ (boundary velocity) are mathematically disjoint. In discrete Eulerian models, fixed-grid cell flux updates prevent double-subtraction. |
| **5. Numerical Conditioning & Operational Defaults** | Claimed condition number $\kappa \sim \mathcal{O}(N^2)$, bounded roundoff for $N \le 1000$, guaranteed Picard convergence in 25 iterations, and universal $\omega = 0.60$. | Derived operator condition number $\kappa(M) \sim \mathcal{O}(N^2 \cdot \frac{\max B_i}{\min B_i}) \approx 10^8$. Formally classified 25 iterations and $\omega = 0.60$ as **operational defaults/heuristics**, NOT mathematical guarantees. | Picard iteration has no global analytical convergence guarantee for arbitrary rheological non-linearities. Failure within 25 iterations triggers adaptive timestep halving ($\Delta t \leftarrow \Delta t / 2$), which restores convergence by reducing incremental deformation. |

---

## 1. Executive Summary & Governance Boundaries

### 1.1 Purpose and Scope
This document provides the formal mathematical and numerical specification for the **Phase 5.2 Pure Physical Dynamic Backbone (Pillar 1)**. The objective of Pillar 1 is to simulate grounded ice-volume evolution across three mainland Antarctic Peninsula basins:
* **Hp-I** (Palmer Land West)
* **I-Ipp** (Graham Land West)
* **Ipp-J** (Graham Land East)
* **Domain A** (Combined regional sum: $\Delta V_{\text{Domain A}} \equiv \Delta V_{\text{Hp-I}} + \Delta V_{\text{I-Ipp}} + \Delta V_{\text{Ipp-J}}$)

over the historical ($1979\text{--}2022$) and projection ($2023\text{--}2100$) eras.

### 1.2 Strict Governance Boundaries (Phase 5.2.2 Implementation Remains Locked)
In strict accordance with project governance:
1. **Phase 5.2.2 remains locked.**
2. **Zero solver code implementation, zero parameter calibration, zero machine learning training, zero hybrid coupling, and zero forward 2100 projections** are permitted in this phase.
3. **Pillar 1 Independence Protocol:** Pillar 1 must remain entirely independent of ISMIP6 model outputs. ISMIP6 serves strictly as an external comparison benchmark (Pillar 2).
4. **Final Determination:** This specification achieves **PASS — ready for a separate implementation authorization review**. Implementation requires separate explicit authorization after independent review.

---

## 2. Definition of the Physical Glaciological System

```mermaid
flowchart TD
    subgraph "Spatial Domain: 1D Curvilinear Flowline Coordinates"
        DIV["Inland Ice Divide (x = 0)<br>u = 0 (Dirichlet)<br>ds/dx = 0 (Neumann)"]
        INTERIOR["Grounded Ice Flowline (0 < x < x_GL)<br>SSA-with-Drag Momentum Balance<br>Width-Integrated Continuity"]
        GL["Moving Grounding Line (x = x_GL(t))<br>Flotation: H_flot = -(rho_w / rho_i) * z_b<br>Schoof Flux: q_GL = q_unbutt * [1 - omega_b * theta]^mu<br>Dirichlet Velocity: u_GL = q_GL / h_GL"]
        SHELF["Floating Ice Shelf / Embayment (x > x_GL)<br>Dynamic Buttressing theta_buttress(t)<br>Sub-shelf basal melt / Cavity warming"]
    end

    DIV -->|Membrane Stress Divergence| INTERIOR
    INTERIOR -->|Advective Solid Ice Flux Q| GL
    GL -->|Calving / Hydrofracture Loss| SHELF
    SHELF -.->|Buttressing Resistance| GL

    style DIV fill:#e6f2ff,stroke:#1f77b4,stroke-width:2px;
    style INTERIOR fill:#e6ffe6,stroke:#2ca02c,stroke-width:2px;
    style GL fill:#fff2e6,stroke:#ff7f0e,stroke-width:2px;
    style SHELF fill:#f9f9f9,stroke:#666666,stroke-width:2px;
```

---

## 3. Mathematical Governing Equations & Dimensional Closure

### 3.1 Flowline Continuity Equation & Rigorous SMB Conversion

#### Definition of Fluid and Solid Densities
1. **Solid Pure Ice Density:** $\rho_i = 917.0\text{ kg m}^{-3}$ (governs ice mass and solid ice thickness $H$).
2. **Fresh Water Standard Reference Density:** $\rho_{\text{water}} = 1000.0\text{ kg m}^{-3}$ (governs glaciological water-equivalent SMB).
3. **Polar Ambient Seawater Density:** $\rho_{\text{ocean}} = \rho_w = 1028.0\text{ kg m}^{-3}$ (governs Archimedean flotation).

#### Solid-Ice Accumulation Conversion
RACMO2.3p2 water-equivalent SMB ($\dot{a}_{\text{we}}$ in $\text{m w.e. yr}^{-1}$) is converted to solid-ice accumulation rate $\dot{a}_i$ via:
$$\mathbf{\dot{a}_i(x, t) = \left(\frac{\rho_{\text{water}}}{\rho_i}\right) \dot{a}_{\text{we}}(x, t) = \left(\frac{1000.0}{917.0}\right) \dot{a}_{\text{we}}(x, t) \approx 1.0905125 \times \dot{a}_{\text{we}}(x, t) \quad [\text{m ice-eq yr}^{-1}]}$$

#### Width-Integrated Flowline Continuity Equation
$$\mathbf{\frac{\partial}{\partial t}\Big(W(x) H(x, t)\Big) + \frac{\partial}{\partial x}\Big(W(x) H(x, t) \bar{u}(x, t)\Big) = W(x) \dot{a}_i(x, t) = W(x) \left(\frac{\rho_{\text{water}}}{\rho_i}\right) \dot{a}_{\text{we}}(x, t)}$$
All terms have exact SI units of $\mathbf{\text{m}^2 \text{s}^{-1}}$.

---

### 3.2 Moving-Grounding-Line Mass Budget & Double-Counting Prevention

#### Continuous Lagrangian Formulation (Reynolds Transport Theorem)
The total grounded ice mass within the moving domain $\Omega_g(t) = [0, x_{\text{GL}}(t)]$ is:
$$M_g(t) = \int_0^{x_{\text{GL}}(t)} \rho_i W(x) H(x, t) \, dx \quad [\text{kg}]$$
Differentiating with respect to time using the Leibniz integral rule:
$$\frac{d M_g}{dt} = \int_0^{x_{\text{GL}}(t)} \frac{\partial}{\partial t}\Big(\rho_i W(x) H(x, t)\Big) dx + \rho_i W(x_{\text{GL}}) H(x_{\text{GL}}, t) \frac{dx_{\text{GL}}}{dt}$$
Substituting the continuous local continuity equation $\frac{\partial (\rho_i W H)}{\partial t} = - \frac{\partial (\rho_i W H \bar{u})}{\partial x} + \rho_i W \dot{a}_i$:
$$\frac{d M_g}{dt} = \int_0^{x_{\text{GL}}(t)} \rho_i W \dot{a}_i \, dx - \Big[ \rho_i W(x) H(x, t) \bar{u}(x, t) \Big]_0^{x_{\text{GL}}(t)} + \rho_i W(x_{\text{GL}}) H(x_{\text{GL}}, t) \frac{dx_{\text{GL}}}{dt}$$
Applying the divide boundary condition $\bar{u}(0, t) = 0$:
$$\mathbf{\frac{d M_g}{dt} = \text{SMB}_g(t) - D_{\text{GL}}(t) - M_{\text{ungrounding}}(t)}$$
where:
1. **Integrated Grounded Surface Mass Balance:**
   $$\text{SMB}_g(t) = \int_0^{x_{\text{GL}}(t)} \rho_i W(x) \dot{a}_i(x, t) \, dx = \int_0^{x_{\text{GL}}(t)} \rho_{\text{water}} W(x) \dot{a}_{\text{we}}(x, t) \, dx \quad [\text{kg s}^{-1}]$$
2. **Advective Grounding-Line Discharge:**
   $$D_{\text{GL}}(t) = \rho_i W(x_{\text{GL}}) H(x_{\text{GL}}, t) \bar{u}(x_{\text{GL}}, t) = \rho_i W_{\text{GL}} q_{\text{GL}}(t) \quad [\text{kg s}^{-1}]$$
   This represents ice mass flux physically crossing the spatial boundary coordinate $x = x_{\text{GL}}(t)$.
3. **Boundary Migration Ungrounding Transfer:**
   $$M_{\text{ungrounding}}(t) = - \rho_i W(x_{\text{GL}}) H(x_{\text{GL}}, t) \frac{dx_{\text{GL}}}{dt} = - \rho_i W_{\text{GL}} h_{\text{GL}} v_{\text{GL}}(t) \quad [\text{kg s}^{-1}]$$
   where $v_{\text{GL}} = dx_{\text{GL}}/dt$ is the grounding-line migration velocity.
   - When the grounding line retreats inland ($v_{\text{GL}} < 0$), $M_{\text{ungrounding}} > 0$: previously grounded ice columns are ungrounded and transferred to the floating shelf category.
   - When the grounding line advances seaward ($v_{\text{GL}} > 0$), $M_{\text{ungrounding}} < 0$: shelf ice becomes grounded upon topographic shoals.

#### Mathematical Proof of Orthogonality (Zero Double-Counting)
$D_{\text{GL}}$ and $M_{\text{ungrounding}}$ are mathematically disjoint:
* $D_{\text{GL}}$ is the flux integral of velocity $\bar{u}$ across the instantaneous boundary position.
* $M_{\text{ungrounding}}$ is the kinematic domain velocity term resulting from the coordinate motion of $x_{\text{GL}}(t)$.
* Both terms must appear in the continuous mass budget of a moving domain.

#### Discrete Finite-Volume Formulation & Implementation Rule
In our numerical solver, the spatial domain is discretized into fixed Eulerian grid cells $x_i$ with static cell faces $x_{i+1/2}$:
1. **Fixed Eulerian Continuity Update:**
   Within all fully grounded interior cells ($i < k$), thickness evolves purely through discrete face flux divergence:
   $$H_i^{t+\Delta t} = H_i^t + \frac{\Delta t}{W_i \Delta x} \Big( Q_{i-1/2}^t - Q_{i+1/2}^t \Big) + \Delta t \dot{a}_{i}^t$$
2. **Terminal Grounding-Line Cell:**
   The terminal cell $k$ contains the moving boundary $x_{\text{GL}}(t) \in [x_{k-1/2}, x_{k+1/2}]$, with grounded fraction $\lambda_{\text{GL}}(t) = \frac{x_{\text{GL}}(t) - x_{k-1/2}}{\Delta x} \in [0, 1]$.
3. **Discrete Mass Accounting Rule:**
   Total grounded mass is calculated by integrating over the active grounded footprint:
   $$M_g(t) = \sum_{i=1}^{k-1} \rho_i W_i H_i(t) \Delta x + \lambda_{\text{GL}}(t) \rho_i W_k H_k(t) \Delta x$$
   **Implementation Rule:** The discrete solver computes grounded volume strictly via cell summation. The continuous identity $\frac{d M_g}{dt} = \text{SMB}_g - D_{\text{GL}} - M_{\text{ungrounding}}$ is monitored as an analytical diagnostic audit. Double-counting is precluded because $M_{\text{ungrounding}}$ is not subtracted a second time from the cell-integrated mass.

---

### 3.3 Boundary Conditions at Inland Divide ($x = 0$)
By physical reflection symmetry across the Peninsula ridge spine ($x \to -x$):
* **Horizontal Velocity:** Odd function $\implies \mathbf{\bar{u}(0, t) = 0}$ (**Homogeneous Dirichlet Boundary Condition**).
* **Surface Elevation and Thickness:** Even functions $\implies \mathbf{\frac{\partial s}{\partial x}\Big|_0 = 0}$, $\mathbf{\frac{\partial H}{\partial x}\Big|_0 = 0}$ (**Homogeneous Neumann Boundary Conditions**).
* **Force Equilibrium:** Driving stress $\rho_i g W H \frac{\partial s}{\partial x} = 0$, basal drag $\tau_b = 0$, lateral drag $\tau_{\text{wall}} = 0$. Longitudinal strain rate $\partial \bar{u}/\partial x$ is an even function (non-zero divide extension), while membrane divergence $\frac{\partial}{\partial x}(W H \bar{\nu} \frac{\partial \bar{u}}{\partial x})$ is an odd function that vanishes at $x=0$, satisfying exact equilibrium ($0 - 0 - 0 = 0$).

---

### 3.4 Schoof Grounding-Line Flux & Downstream Boundary Formulation

#### Asymptotic Unbuttressed Grounding-Line Flux
From Schoof (2007, Eq. 32):
$$q_{\text{unbuttressed}} = \left( \frac{\rho_i g (1 - \rho_i / \rho_{\text{ocean}})}{4^n A} \right)^{\frac{1}{m+1}} C_{\text{bed}}^{-\frac{1}{m+1}} h_{\text{GL}}^{\frac{m+n+3}{m+1}} \quad [\text{m}^2\text{ s}^{-1}]$$
where $h_{\text{GL}} = - (\rho_{\text{ocean}} / \rho_i) z_b(x_{\text{GL}})$ is the flotation thickness.

#### Authoritative Buttressed Grounding-Line Flux
$$\mathbf{q_{\text{GL}}(h_{\text{GL}}, \theta_{\text{buttress}}) = q_{\text{unbuttressed}}(h_{\text{GL}}) \cdot \Big[ 1 - \omega_b \cdot \theta_{\text{buttress}}(t) \Big]^\mu \quad [\text{m}^2\text{ s}^{-1}]}$$
where $\theta_{\text{buttress}} \in [0, 1]$, $\omega_b \in [0.40, 0.85]$, and $\mu \in [1.0, 3.0]$.

#### Consistency of the Dirichlet Velocity Boundary Condition
In our model, the grounding-line boundary condition for the SSA momentum solve is formulated as an essential **Dirichlet condition on velocity**:
$$\mathbf{u_{\text{GL}}(t) = \frac{q_{\text{GL}}(h_{\text{GL}}(t), \theta_{\text{buttress}}(t))}{h_{\text{GL}}(t)} \quad [\text{m s}^{-1}]}$$

**Physical & Mathematical Justification:**
1. **Mathematical Well-Posedness:** The 1D SSA is a second-order elliptic differential equation in velocity $\bar{u}(x)$. A well-posed boundary-value problem requires one boundary condition at each domain end:
   - Divide ($x = 0$): Dirichlet condition $u(0) = 0$.
   - Terminus ($x = x_{\text{GL}}$): Dirichlet condition $u(x_{\text{GL}}) = u_{\text{GL}}$.
   This uniquely determines the interior velocity field and ensures existence and uniqueness of the solution.
2. **Coarse-Grid Boundary Layer Matching:** In full Stokes or fine-grid SSA models ($\Delta x \le 50\text{ m}$), the downstream boundary condition is a **Neumann stress condition** balancing longitudinal ice tension against hydrostatic ocean backpressure:
   $$2 H \bar{\nu} \frac{\partial \bar{u}}{\partial x} = \frac{1}{2} \rho_i g \left( 1 - \frac{\rho_i}{\rho_{\text{ocean}}} \right) H^2 - \tau_{\text{backstress}}$$
   However, on coarse flowline grids ($\Delta x \ge 500\text{ m}$ to $1000\text{ m}$), solving the SSA with a pure stress boundary condition fails to resolve the narrow boundary layer ($\mathcal{O}(10\text{--}100\text{ m})$) where basal drag transitions to zero, resulting in catastrophic mesh-size dependence and unphysical grounding line pinning (Vieli & Payne 2005; Schoof 2007).
   The Schoof asymptotic matching theory was derived specifically to replace this under-resolved boundary layer with the analytical flux $q_{\text{GL}}$.
3. **Coupling to Mass Conservation:** Setting $u(x_{\text{GL}}) = q_{\text{GL}} / h_{\text{GL}}$ guarantees that the velocity entering the continuity equation at the grounding-line face produces the exact mass discharge $D_{\text{GL}} = \rho_i W_{\text{GL}} h_{\text{GL}} u_{\text{GL}} = \rho_i W_{\text{GL}} q_{\text{GL}}$ dictated by the asymptotic theory.

---

### 3.5 Formalization of Option A: 1D Shallow Shelf Equation with Drag
The 1D SSA-with-drag momentum equation is:
$$2 \frac{\partial}{\partial x} \left( W(x) H(x, t) \bar{\nu} \frac{\partial \bar{u}}{\partial x} \right) - W(x) \tau_{b, \text{reg}}(x) - 2 H(x, t) \tau_{\text{wall}, \text{reg}}(x) = \rho_i g W(x) H(x, t) \frac{\partial s}{\partial x}$$
Effective viscosity at cell centers:
$$\bar{\nu} = \frac{1}{2} A(T)^{-1/n} \left[ \left(\frac{\partial \bar{u}}{\partial x}\right)^2 + \dot{\varepsilon}_0^2 \right]^{\frac{1-n}{2n}} \quad [\text{Pa s}]$$
with strain rate regularizer $\dot{\varepsilon}_0 = 10^{-10}\text{ s}^{-1} \approx 3.15 \times 10^{-3}\text{ yr}^{-1}$.

---

### 3.6 Non-Linear Drag Regularization Near Zero Velocity

#### The Singularity in Unregularized Linearized Drag
In Picard iteration, non-linear drag is linearized as $\tau_b = \beta_b(u) \cdot u$ and $\tau_{\text{wall}} = \beta_{\text{wall}}(u) \cdot u$.
For Weertman sliding with $m = 1/3$ and lateral drag with Glen exponent $n = 3$:
$$\beta_b(u) = C_{\text{bed}} |u|^{-2/3} \xrightarrow{u \to 0} \infty, \qquad \beta_{\text{wall}}(u) \propto |u|^{-2/3} \xrightarrow{u \to 0} \infty$$
At the inland divide ($u = 0$) or stagnant flowline zones, unregularized evaluation results in division by zero (`inf`), crashing the matrix assembly.

#### Smooth Drag Regularization Formulation
To guarantee finite matrix coefficients while strictly preserving physical mechanics, the velocity regularization parameter $u_{\text{reg}}$ is introduced (Bueler & Brown 2009; Jouvet 2023):

1. **Regularized Basal Sliding Friction:**
   $$\mathbf{\beta_{b, \text{reg}}(u) = C_{\text{bed}} \left( u^2 + u_{\text{reg}}^2 \right)^{\frac{m-1}{2}} \quad [\text{Pa s m}^{-1} = \text{N s m}^{-3}]}$$
   $$\mathbf{\tau_{b, \text{reg}}(u) = \beta_{b, \text{reg}}(u) \cdot u = C_{\text{bed}} \left( u^2 + u_{\text{reg}}^2 \right)^{\frac{m-1}{2}} u \quad [\text{Pa}]}$$
2. **Regularized Lateral Sidewall Drag:**
   $$\mathbf{\beta_{\text{wall}, \text{reg}}(u) = \left( \frac{5}{A(T) W} \right)^{\frac{1}{n}} \left( u^2 + u_{\text{reg}}^2 \right)^{\frac{1-n}{2n}} \quad [\text{Pa s m}^{-1} = \text{N s m}^{-3}]}$$
   $$\mathbf{\tau_{\text{wall}, \text{reg}}(u) = \beta_{\text{wall}, \text{reg}}(u) \cdot u = \left( \frac{5}{A(T) W} \right)^{\frac{1}{n}} \left( u^2 + u_{\text{reg}}^2 \right)^{\frac{1-n}{2n}} u \quad [\text{Pa}]}$$

#### Rigorous SI Arithmetic Derivation for Zero Velocity
Let:
* $C_{\text{bed}} = 1.0 \times 10^7\text{ Pa (m s}^{-1})^{-1/3}$
* $u_{\text{reg}} = 1.0 \times 10^{-4}\text{ m yr}^{-1}$
* Standard conversion: $1\text{ yr} = 31,557,600\text{ s}$ ($365.25\text{ d}$)
* $u_{\text{reg}} = \frac{1.0 \times 10^{-4}\text{ m}}{3.15576 \times 10^7\text{ s}} \approx \mathbf{3.16881 \times 10^{-12}\text{ m s}^{-1}}$
* $m = 1/3 \implies m - 1 = -2/3$

Evaluating $u_{\text{reg}}^{m-1}$:
$$u_{\text{reg}}^{-2/3} = (3.16881 \times 10^{-12}\text{ m s}^{-1})^{-2/3} = (3.16881)^{-2/3} \times (10^{-12})^{-2/3} = 0.463521 \times 10^8 = \mathbf{4.63521 \times 10^7\text{ (m s}^{-1})^{-2/3}}$$

Evaluating $\beta_{b, \text{reg}}(0)$:
$$\mathbf{\beta_{b, \text{reg}}(0) = C_{\text{bed}} \cdot u_{\text{reg}}^{-2/3} = (1.0 \times 10^7) \times (4.63521 \times 10^7) = \mathbf{4.6352 \times 10^{14}\text{ Pa s m}^{-1} = 4.6352 \times 10^{14}\text{ N s m}^{-3}}}$$

* **Correction of Previous Value:** The earlier reported draft value of $4.64 \times 10^{10}\text{ Pa s m}^{-1}$ was an arithmetic error that mistakenly omitted a factor of $10^4$. The mathematically correct SI value is $\mathbf{4.64 \times 10^{14}\text{ Pa s m}^{-1}}$.
* **Evaluation of Lateral Drag at $u = 0$:**
  With $A = 10^{-24}\text{ Pa}^{-3}\text{ s}^{-1}$, $W = 10\text{ km} = 10^4\text{ m}$, and $n = 3$:
  $$\left( \frac{5}{A W} \right)^{1/3} = \left( \frac{5}{10^{-20}} \right)^{1/3} = (5 \times 10^{20})^{1/3} \approx 7.937 \times 10^6\text{ Pa (m s}^{-1})^{-1/3}$$
  $$\mathbf{\beta_{\text{wall}, \text{reg}}(0) = (7.937 \times 10^6) \times (4.6352 \times 10^7) = \mathbf{3.679 \times 10^{14}\text{ Pa s m}^{-1}}}$$

#### Conditioning and Convergence Assessment of the Large Divide Coefficient
1. **Physical Mechanics Near the Divide:**
   In Form 1 (integrated over control volume $\Delta x = 1\text{ km} = 10^3\text{ m}$ and width $W = 10\text{ km} = 10^4\text{ m}$):
   $$D_{b, 0} = W \beta_{b, \text{reg}}(0) \Delta x = 10^4 \times (4.6352 \times 10^{14}) \times 10^3 \approx \mathbf{4.64 \times 10^{21}\text{ N s m}^{-1}}$$
   Membrane stress conductance $A_{i+1/2} = \frac{2 W H \bar{\nu}}{\Delta x} \approx \frac{2 \times 10^4 \times 10^3 \times 10^{14}}{10^3} \approx \mathbf{2.0 \times 10^{18}\text{ N s m}^{-1}}$.
   The drag coefficient exceeds membrane conductance by:
   $$\frac{D_{b, 0}}{A_{i+1/2}} \approx \frac{4.64 \times 10^{21}}{2.0 \times 10^{18}} \approx \mathbf{2,320}$$
   This strong drag dominance physically pins near-divide velocity to near zero ($u \sim F/D \approx 10^{10} / 4.64 \times 10^{21} \approx 2 \times 10^{-12}\text{ m s}^{-1} \approx 6 \times 10^{-5}\text{ m yr}^{-1}$).
2. **Impact on the Linear Solve (Thomas Algorithm):**
   A large positive drag coefficient $D_i$ appears on the main diagonal $B_i = A_i + C_i + D_i$. This **enhances diagonal dominance**, ensuring that elimination pivots $d_i$ are large and positive. The linear solve is well-damped locally and does not suffer from floating-point overflow or loss of significance.
3. **Impact on Non-Linear Picard Iterations:**
   Downstream where $u \approx 100\text{ m yr}^{-1} \approx 3.17 \times 10^{-6}\text{ m s}^{-1}$, the drag coefficient is:
   $$\beta_b(100\text{ m yr}^{-1}) = 10^7 \times (3.17 \times 10^{-6})^{-2/3} \approx \mathbf{4.64 \times 10^{10}\text{ Pa s m}^{-1}}$$
   The spatial contrast between the divide and the fast stream is $\frac{4.64 \times 10^{14}}{4.64 \times 10^{10}} = \mathbf{10^4}$.
   Because $\beta_b(u)$ varies by four orders of magnitude, initializing Picard iterations from an arbitrary zero-velocity field ($u^0 = 0$) results in an overly sluggish first iterate, followed by large derivative swings.
   **Algorithmic Remedy:**
   - Under-relaxation with $\omega \le 0.50$ is mandatory during the initial iterations.
   - For forward transient runs, initializing $u^0$ from the previous timestep's converged velocity field provides an excellent initial estimate within the radius of convergence.
   - The sensitivity of Picard iteration count to $u_{\text{reg}} \in [10^{-5}, 10^{-2}]\text{ m yr}^{-1}$ will be formally audited in Test 15.

#### Proof of Required Regularization Properties
1. **Strictly Finite Coefficients:** $\beta_{b, \text{reg}}(0) = 4.64 \times 10^{14} < \infty$.
2. **Vanishing Force at Stagnation:** $\tau_{b, \text{reg}}(0) = \beta_b(0) \cdot 0 \equiv \mathbf{0.0\text{ Pa}}$.
3. **Sign Parity:** $\text{sgn}(\tau_{\text{reg}}(u)) = \text{sgn}(\beta_{\text{reg}}(u) \cdot u) \equiv \mathbf{\text{sgn}(u)}$.
4. **Negligible Perturbation:** For glaciological velocities $|u| \ge 1.0\text{ m yr}^{-1}$, relative error is bounded by $\frac{1}{3} (u_{\text{reg}} / u)^2 \le \mathbf{3.3 \times 10^{-9}}$ ($< 0.000001\%$).

---

### 3.7 Lateral Glen-Law Constitutive Derivation & Reduced-Order Qualification

#### Full Tensorial Framework
1. **Cauchy Stress & Deviatoric Stress Tensor:**
   $$\boldsymbol{\sigma} = - p \mathbf{I} + \boldsymbol{\tau}$$
   where $p = - \frac{1}{3} \text{tr}(\boldsymbol{\sigma})$ is the isotropic cryostatic pressure, and $\boldsymbol{\tau}$ is the symmetric, trace-free deviatoric stress tensor ($\text{tr}(\boldsymbol{\tau}) = 0$).
2. **Symmetric Strain Rate Tensor:**
   $$\dot{\boldsymbol{\varepsilon}} = \frac{1}{2} \Big( \nabla \mathbf{u} + (\nabla \mathbf{u})^T \Big) \implies \dot{\varepsilon}_{ij} = \frac{1}{2} \left( \frac{\partial u_i}{\partial x_j} + \frac{\partial u_j}{\partial x_i} \right)$$
3. **Second Invariant Conventions in Glaciology:**
   Following Cuffey & Paterson (2010, p. 58) and Greve & Blatter (2009, p. 77), the effective stress invariant $\tau_e$ and effective strain rate invariant $\dot{\varepsilon}_e$ are defined as:
   $$\tau_e \equiv \sqrt{\frac{1}{2} \tau_{ij} \tau_{ij}} = \sqrt{\frac{1}{2} \left( \tau_{xx}^2 + \tau_{yy}^2 + \tau_{zz}^2 + 2\tau_{xy}^2 + 2\tau_{xz}^2 + 2\tau_{yz}^2 \right)}$$
   $$\dot{\varepsilon}_e \equiv \sqrt{\frac{1}{2} \dot{\varepsilon}_{ij} \dot{\varepsilon}_{ij}} = \sqrt{\frac{1}{2} \left( \dot{\varepsilon}_{xx}^2 + \dot{\varepsilon}_{yy}^2 + \dot{\varepsilon}_{zz}^2 + 2\dot{\varepsilon}_{xy}^2 + 2\dot{\varepsilon}_{xz}^2 + 2\dot{\varepsilon}_{yz}^2 \right)}$$
4. **Glen's Tensorial Constitutive Law:**
   $$\dot{\boldsymbol{\varepsilon}} = A(T) \tau_e^{n-1} \boldsymbol{\tau} \iff \dot{\varepsilon}_{ij} = A(T) \tau_e^{n-1} \tau_{ij}$$
   Taking the inner product and using invariant definitions confirms $\dot{\varepsilon}_e = A(T) \tau_e^n \iff \tau_e = A(T)^{-1/n} \dot{\varepsilon}_e^{1/n}$.

#### Specialization to Pure Horizontal Lateral Shear
Consider an idealized rectilinear glacial channel bounded by vertical sidewalls at $y = \pm W/2$.
Assume pure horizontal shear flow parallel to the valley axis:
$$\mathbf{u} = \Big( u(y), 0, 0 \Big)$$
The only non-zero velocity gradient is $\frac{\partial u}{\partial y}$.

1. **Strain Rate Components:**
   $$\dot{\varepsilon}_{xy} = \dot{\varepsilon}_{yx} = \frac{1}{2} \frac{\partial u}{\partial y}, \qquad \dot{\varepsilon}_{xx} = \dot{\varepsilon}_{yy} = \dot{\varepsilon}_{zz} = \dot{\varepsilon}_{xz} = \dot{\varepsilon}_{yz} = 0$$
   The tensorial factor of $1/2$ originates strictly from the definition of the symmetric strain rate tensor.
2. **Effective Invariant Under Pure Shear:**
   $$\dot{\varepsilon}_e = \sqrt{\frac{1}{2} \left( 2 \dot{\varepsilon}_{xy}^2 \right)} = |\dot{\varepsilon}_{xy}| = \mathbf{\frac{1}{2} \left| \frac{\partial u}{\partial y} \right|}$$
3. **Deviatoric Stress Invariant:**
   By constitutive symmetry, $\tau_{xy}$ is the only non-zero shear stress component:
   $$\tau_e = \sqrt{\frac{1}{2} \left( 2 \tau_{xy}^2 \right)} = |\tau_{xy}|$$
4. **Equating Tensor Components via Glen's Law:**
   Evaluating the $xy$ tensor component of Glen's law:
   $$\dot{\varepsilon}_{xy} = A(T) \tau_e^{n-1} \tau_{xy} = A(T) |\tau_{xy}|^{n-1} \tau_{xy}$$
   Taking magnitudes:
   $$|\dot{\varepsilon}_{xy}| = A(T) |\tau_{xy}|^n$$
   Substituting $|\dot{\varepsilon}_{xy}| = \frac{1}{2} \left| \frac{\partial u}{\partial y} \right|$:
   $$\frac{1}{2} \left| \frac{\partial u}{\partial y} \right| = A(T) |\tau_{xy}|^n \implies \mathbf{|\tau_{xy}| = \left( \frac{1}{2 A(T)} \left| \frac{\partial u}{\partial y} \right| \right)^{\frac{1}{n}}}$$

#### Channel Sidewall Gradient & Exact Cancellation of the Factor of Two
Whillans & van der Veen (1997) and Pattyn (2006) prescribe a power-law velocity profile across the channel width $y \in [-W/2, W/2]$:
$$u(y) = u_c \left[ 1 - \left| \frac{2y}{W} \right|^{n+1} \right]$$
The width-averaged velocity $\bar{u}$ for Glen exponent $n = 3$ is:
$$\bar{u} = \frac{1}{W} \int_{-W/2}^{W/2} u_c \left[ 1 - \left(\frac{2y}{W}\right)^4 \right] dy = u_c \left(1 - \frac{1}{5}\right) = \frac{4}{5} u_c \implies u_c = \frac{5}{4} \bar{u}$$
Differentiating with respect to $y$ and evaluating at the channel rock wall ($y = W/2$):
$$\left| \frac{\partial u}{\partial y} \right|_{\text{wall}} = u_c \cdot (n+1) \cdot \left(\frac{2}{W}\right) = \left( \frac{5}{4} \bar{u} \right) \cdot 4 \cdot \left(\frac{2}{W}\right) = \mathbf{\frac{10 \bar{u}}{W}}$$
Substituting this wall gradient into the pure-shear stress expression:
$$\tau_{\text{wall}} = \left( \frac{1}{2 A(T)} \cdot \frac{10 \bar{u}}{W} \right)^{\frac{1}{n}} = \left( \frac{10 \bar{u}}{2 A(T) W} \right)^{\frac{1}{n}} = \mathbf{\left( \frac{5 \bar{u}}{A(T) W} \right)^{\frac{1}{n}}}$$

#### Explicit Qualification as a Reduced-Order Scalar Approximation
* **Coupling Limitation:** In a full 2D or 3D ice stream, longitudinal stretching $\frac{\partial u}{\partial x}$ and lateral shearing $\frac{\partial u}{\partial y}$ are coupled through the effective invariant $\dot{\varepsilon}_e = \sqrt{(\partial u/\partial x)^2 + (0.5 \partial u/\partial y)^2}$. Strong longitudinal stretching softens the ice rheology, decreasing effective viscosity and modulating lateral shear.
* **Classification:** The expression $\tau_{\text{wall}} = (5 \bar{u} / (AW))^{1/n}$ assumes **pure uncoupled transverse shear**. It is explicitly classified as a **reduced-order 1D boundary layer parameterization** appropriate for narrow, confined glacial troughs ($W/H \le 10$). Universal applicability across all geometry regimes is not claimed; sensitivity to cross-sectional trough geometry is evaluated in Test 14.

---

## 4. Finite-Volume Stencil & Matrix Coefficient Derivation

### 4.1 Control-Volume Integration of Momentum Balance
Integrating across cell face $x_{i+1/2}$ over the control volume $x \in [x_i, x_{i+1}]$ of length $\Delta x$:

$$\int_{x_i}^{x_{i+1}} 2 \frac{\partial}{\partial x} \left( W H \bar{\nu} \frac{\partial \bar{u}}{\partial x} \right) dx - \int_{x_i}^{x_{i+1}} \left[ W \tau_b + 2 H \tau_{\text{wall}} \right] dx = \int_{x_i}^{x_{i+1}} \rho_i g W H \frac{\partial s}{\partial x} dx$$

### 4.2 Control-Volume Integrated Stencil (Form 1: Primary Formulation in $[\text{N}]$)
$$\mathbf{- A_{i+1/2} u_{i-1/2}^{k+1} + B_{i+1/2} u_{i+1/2}^{k+1} - C_{i+1/2} u_{i+3/2}^{k+1} = F_{i+1/2}}$$
where:
* **Lower Conductance:** $A_{i+1/2} = \frac{2 (W H \bar{\nu})_i^k}{\Delta x} \quad [\text{N s m}^{-1} = \text{kg s}^{-1}]$
* **Upper Conductance:** $C_{i+1/2} = \frac{2 (W H \bar{\nu})_{i+1}^k}{\Delta x} \quad [\text{N s m}^{-1} = \text{kg s}^{-1}]$
* **Integrated Drag Dissipation:**
  $$D_{i+1/2}^k = \left( W_{i+1/2} \beta_{b, \text{reg}, i+1/2}^k + 2 H_{i+1/2} \beta_{\text{wall}, \text{reg}, i+1/2}^k \right) \Delta x \quad [\text{N s m}^{-1} = \text{kg s}^{-1}]$$
* **Main Diagonal Coefficient:**
  $$B_{i+1/2} = A_{i+1/2} + C_{i+1/2} + D_{i+1/2}^k \quad [\text{N s m}^{-1} = \text{kg s}^{-1}]$$
* **Driving Gravitational Force:**
  $$F_{i+1/2} = \rho_i g (W H)_{i+1/2} (s_i - s_{i+1}) \quad [\text{N}]$$

**Dimensional Verification:** $[A u] = [\text{N s m}^{-1}] [\text{m s}^{-1}] = \mathbf{\text{N}}$, matching $F \in \mathbf{\text{N}}$.

---

### 4.3 Boundary Stencils
1. **Divide Boundary ($i = 0$, Face $x_{1/2} = 0$):**
   Homogeneous Dirichlet: $u_{1/2}^{k+1} = 0.0\text{ m s}^{-1}$.
   Row 1: $A_{1/2} = 0, B_{1/2} = 1.0, C_{1/2} = 0, F_{1/2} = 0.0$.
2. **Grounding-Line Boundary (Face $x_{N+1/2} = x_{\text{GL}}$):**
   Dirichlet velocity condition: $u_{N+1/2}^{k+1} = u_{\text{GL}}^t = \frac{q_{\text{GL}}(h_{\text{GL}}^t, \theta_{\text{buttress}}^t)}{h_{\text{GL}}^t}$.
   Row $N+1$: $A_{N+1/2} = 0, B_{N+1/2} = 1.0, C_{N+1/2} = 0, F_{N+1/2} = u_{\text{GL}}^t$.

---

### 4.4 Rigorous Delineation of Linear-Solver Stability, Conditioning, and Convergence

To replace imprecise assertions of "unconditional stability", the mathematical properties are rigorously categorized:

#### 1. Diagonal Dominance Definitions
Let $M$ be the $N \times N$ tridiagonal matrix.
* **Strict Diagonal Dominance:** $|M_{ii}| > \sum_{j \ne i} |M_{ij}|$ for all rows $i$.
  In interior rows where drag is active ($D_i > 0$), $|B_i| - (|A_i| + |C_i|) = D_i > 0$. If $D_i > 0$ for all $i$, the matrix is strictly diagonally dominant.
* **Weak Diagonal Dominance:** $|M_{ii}| \ge \sum_{j \ne i} |M_{ij}|$ for all rows $i$.
  If drag vanishes in an ungrounded or frictionless zone ($D_i = 0$), $|B_i| = |A_i| + |C_i|$.
* **Irreducible Diagonal Dominance:**
  A matrix is irreducibly diagonally dominant if:
  1. It is irreducible (for a tridiagonal matrix, $A_i \ne 0$ and $C_i \ne 0$, guaranteed since $W, H, \bar{\nu} > 0$).
  2. It is weakly diagonally dominant across all rows.
  3. At least one row is strictly diagonally dominant.
  In our discrete system, both boundary rows ($u_{1/2} = 0$ and $u_{N+1/2} = u_{\text{GL}}$) have $B = 1.0 > 0 = |A| + |C|$, providing strict diagonal dominance.
  **Theorem (Taussky 1949):** Every irreducibly diagonally dominant matrix is **nonsingular**.

#### 2. Positive Definiteness Clarification
* Irreducible diagonal dominance alone does **NOT** imply symmetric positive definiteness (SPD).
* If boundary Dirichlet values are eliminated by partitioning them directly into the right-hand side, the interior $(N-1) \times (N-1)$ tridiagonal operator $\tilde{M}$ satisfies:
  $$\tilde{M}_{i, i-1} = - A_{i+1/2} = - \frac{2 (W H \bar{\nu})_i}{\Delta x}, \qquad \tilde{M}_{i-1, i} = - C_{i-1/2} = - \frac{2 (W H \bar{\nu})_i}{\Delta x}$$
  Because $\tilde{M}_{i, i-1} \equiv \tilde{M}_{i-1, i}$, the interior reduced operator is **strictly symmetric** ($\tilde{M} = \tilde{M}^T$).
* By the Gershgorin Circle Theorem and Taussky's theorem, all real eigenvalues of $\tilde{M}$ are strictly positive ($\lambda_i > 0$). Therefore, the reduced interior operator is **Symmetric Positive Definite (SPD)**.

#### 3. Thomas Algorithm Pivot Safety & Numerical Backward Stability
* **Zero Pivot Impossibility:** During forward Gaussian elimination on an irreducibly diagonally dominant tridiagonal matrix with $B_i > 0$ and $A_i, C_i > 0$, the elimination pivots $d_i$ satisfy:
  $$d_1 = B_1 > 0, \qquad d_i = B_i - \frac{A_i C_{i-1}}{d_{i-1}} > C_i > 0 \quad \forall i = 2, \dots, N$$
  Therefore, **zero pivots can never occur in exact arithmetic**, and pivoting is unnecessary.
* **Backward Stability (Higham 2002):** Gaussian elimination without pivoting on a diagonally dominant tridiagonal matrix is **backward stable**: the computed solution $\hat{u}$ satisfies $(M + \delta M) \hat{u} = F$ with:
  $$\|\delta M\|_\infty \le 3 \epsilon_{\text{mach}} \|M\|_\infty$$
  where $\epsilon_{\text{mach}} \approx 1.11 \times 10^{-16}$ in IEEE 754 double precision.

#### 4. Matrix Conditioning & Forward Error Amplification
* Backward stability guarantees that the algorithm introduces no spurious instability. However, the forward error satisfies:
  $$\frac{\|\hat{u} - u\|}{\|u\|} \le \kappa(M) \frac{\|\delta M\|}{\|M\|}$$
  where $\kappa(M) = \|M\| \|M^{-1}\|$ is the matrix condition number.
* **Condition Number Scaling:**
  For the SSA operator with variable drag, the condition number scales as:
  $$\kappa(M) \approx \mathcal{O}\left( N^2 \cdot \frac{\max_i B_i}{\min_i B_i} \right)$$
  For $N = 100$ and coefficient contrast $\frac{\max B}{\min B} \approx 10^4$ (from divide to fast stream), $\kappa(M) \approx 10^4 \times 10^4 \approx \mathbf{10^8}$.
* **Precision Impact:** In double-precision arithmetic, a condition number of $10^8$ causes a loss of $\approx 8$ decimal digits, leaving $\approx 8$ reliable digits (relative error $\approx 10^{-8}$). While completely sufficient for geophysical applications, this demonstrates that **algebraic solvability does NOT imply $\mathcal{O}(1)$ conditioning**.

#### 5. Qualification of Picard Non-Linear Iteration & Operational Defaults
* Non-singularity of the linear matrix at each step **does NOT guarantee convergence of the non-linear Picard loop**.
* Picard iteration for power-law fluids ($n=3$) has **no universal analytical convergence proof** for arbitrary initial guesses or severe geometric perturbations.
* **Operational Defaults:**
  - `max_iter = 25`: This is an **operational ceiling**, NOT a mathematical guarantee.
  - $\omega_{\text{relax}} = 0.60$: This is an **empirically chosen operational default** (Pattyn 2003; Bueler & Brown 2009), not a universal constant. The operational tuning interval is $\omega \in [0.4, 0.7]$.
* **Emergency Adaptive Step Halving:** If Picard iterations fail to converge ($\epsilon_{\text{Picard}} < 10^{-5}$) within 25 iterations, the solver halves the time step ($\Delta t \leftarrow \Delta t / 2$). Step halving reduces the non-linear deformation increment per step, restoring Picard convergence.

#### 6. Coupled Time-Dependent Model Stability
* The coupled physical ice sheet model is **conditionally stable**, governed by advective CFL bounds:
  $$\Delta t \le C_{\text{CFL}} \frac{\Delta x}{u_{\text{max}}}, \qquad C_{\text{CFL}} = 0.50$$
* All prior claims of "unconditional stability" for the coupled model are formally revoked.

---

## 5. Audited Physical Parameter Registry with 5-Tier Provenance

The 22 parameters in [`reports/tables/physical_parameter_registry.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/physical_parameter_registry.csv) are classified into five formal tiers:
* **Category A:** Published physical constants or consensus values.
* **Category B:** Values directly derived from project observed spatial datasets.
* **Category C:** Literature-supported theoretical ranges & numerical regularizers.
* **Category D:** Analyst-selected scenario / sensitivity exploration intervals.
* **Category E:** Formal calibration targets for Stage 1 (Observational Calibration).

### Master Summary of Physical Parameters

| No. | Parameter Name | Symbol | SI Units | Baseline / Published Range | Category & Literature Citation |
| :---: | :--- | :---: | :---: | :---: | :--- |
| 1 | Solid Ice Density | $\rho_i$ | $\text{kg m}^{-3}$ | 917.0 | Category A: Cuffey & Paterson (2010) |
| 2 | Ambient Ocean Seawater Density | $\rho_{\text{ocean}} / \rho_w$ | $\text{kg m}^{-3}$ | 1028.0 | Category A: Jenkins (1991); Jourdain et al. (2020) |
| 3 | Gravitational Acceleration | $g$ | $\text{m s}^{-2}$ | 9.81 | Category A: Standard Physical Constant |
| 4 | Glen Flow Law Exponent | $n$ | dimensionless | 3.0 (2.5 to 3.5) | Category A: Glen (1955); Cuffey & Paterson (2010) |
| 5 | Ice Softness Factor | $A(T)$ | $\text{Pa}^{-3}\text{ s}^{-1}$ | $1.0\times 10^{-25}$ to $3.5\times 10^{-24}$ | Category C/E: Cuffey & Paterson (2010) Table 3.4 |
| 6 | Basal Sliding Exponent | $m$ | dimensionless | 0.333 (0.333 to 1.0) | Category C: Weertman (1957); Schoof (2005) |
| 7 | Schoof Flux Exponent | $\gamma$ | dimensionless | 4.75 (3.50 to 4.75) | Category C: Derived analytic property $\gamma = \frac{m+n+3}{m+1}$ |
| 8 | Basal Friction Coefficient | $C_{\text{bed}}$ | $\text{Pa (m s}^{-1})^{-m}$ | $1.0\times 10^7$ to $5.0\times 10^{10}$ | Category C/E: Morlighem et al. (2020) |
| 9 | Reference Grounding Thickness | $h_{\text{GL}, 0}$ | $\text{m}$ | 250.0 to 1250.0 | Category B: BedMachine Antarctica V4.1 |
| 10 | Reference Baseline Discharge | $D_0$ | $\text{kg s}^{-1}$ | Basin-specific historical mean | Category B/E: Phase 3.2 Reconstruction |
| 11 | Grounding Bedrock Elevation | $z_{b, \text{GL}}$ | $\text{m}$ | -1200.0 to -150.0 | Category B: BedMachine Antarctica V4.1 |
| 12 | Retrograde Bed Slope | $\alpha_{\text{bed}}$ | dimensionless | -0.02 to +0.02 | Category B: BedMachine Antarctica V4.1 |
| 13 | Buttressing State Factor | $\theta_{\text{buttress}}$ | dimensionless | 0.0 to 1.0 | Category C: Gudmundsson (2013); Fürst et al. (2016) |
| 14 | Max Embayment Buttressing | $\omega_b$ | dimensionless | 0.40 to 0.85 | Category D/E: Fürst et al. (2016); Reese et al. (2018) |
| 15 | Buttressing Non-Linear Exponent | $\mu$ | dimensionless | 1.0 to 3.0 | Category D/E: Gudmundsson (2013); Pegler (2018) |
| 16 | Ocean Thermal Forcing | $\Delta T_{\text{ocean}}$ | $\text{K}$ | -1.0 to +4.0 | Category B/D: Schmidtko et al. (2014) |
| 17 | Sub-Shelf Thermal Transfer | $\gamma_0$ | $\text{m s}^{-1}$ | $1.45\times 10^{-4}$ | Category C: Jourdain et al. (2020) ISMIP6 |
| 18 | Seawater Specific Heat | $c_{pw}$ | $\text{J kg}^{-1}\text{ K}^{-1}$ | 3974.0 | Category A: TEOS-10 Standard |
| 19 | Latent Heat of Fusion | $L_f$ | $\text{J kg}^{-1}$ | $3.34\times 10^5$ | Category A: Cuffey & Paterson (2010) |
| 20 | Surface Mass Balance Rate | $\dot{a}_{\text{we}} \to \dot{a}_i$ | $\text{m w.e. yr}^{-1} \to \text{m ice yr}^{-1}$ | -0.5 to +3.5 | Category B: RACMO2.3p2 ($\dot{a}_i = 1.09051 \dot{a}_{\text{we}}$) |
| 21 | Firn Air Content | $\text{FAC}$ | $\text{m}$ | 0.0 to 18.0 | Category B: Ligtenberg et al. (2011) |
| 22 | Velocity Drag Regularizer | $u_{\text{reg}}$ | $\text{m s}^{-1}$ ($\text{m yr}^{-1}$) | $10^{-4}\text{ m yr}^{-1} \approx 3.17\times 10^{-12}\text{ m s}^{-1}$ | Category C: Bueler & Brown (2009); Jouvet (2023) |

---

## 6. Numerical Timestep Specifications & Sub-Grid Protocol

### 6.1 Timestep Hierarchy
* **Operational Adaptive Window:** $\Delta t_{\text{oper}} \in [0.01, 0.10]\text{ yr}$ (production simulations).
* **Reference Benchmark Step:** $\Delta t_{\text{ref}} = 0.005\text{ yr}$ (strictly used in Test 12).
* **Minimum Permitted Floor:** $\Delta t_{\text{min}} = 0.001\text{ yr} \approx 8.76\text{ h}$ (lower limit of adaptive step halving).
* **Maximum Permitted Ceiling:** $\Delta t_{\text{max}} = 0.25\text{ yr}$ (bounded by Courant $C_{\text{CFL}} \le 0.50$).
* **Emergency Divergence Protocol:** If Picard iteration fails to converge within 25 iterations after halving to $\Delta t < \Delta t_{\text{min}}$, solver halts execution, raises `NonlinearConvergenceError`, and dumps diagnostic state.

### 6.2 Sub-Grid Grounding Line Migration Protocol
* Continuous flotation root: $x_{\text{GL}} = x_k + \Delta x \left( \frac{\Delta z_{\text{flot}}(x_k)}{\Delta z_{\text{flot}}(x_k) - \Delta z_{\text{flot}}(x_{k+1})} \right)$.
* Friction smoothing: $\tau_{b, \text{cell } k} = \lambda_{\text{GL}} \cdot \beta_{b, \text{reg}}(u_k) u_k$, where $\lambda_{\text{GL}} = (x_{\text{GL}} - x_k)/\Delta x \in [0, 1]$.
* Formulated as a **computational hypothesis** to mitigate cell-pinning shocks, to be empirically audited in Test 13.

---

## 7. Reconciled Verification Suite Protocol

### 7.1 Analytically Demonstrated Properties (Phase 5.2.1)
* **Property A (Dimensional Consistency):** All 11 governing equations proven dimensionally consistent in SI units.
* **Property B (Telescoping Conservation):** Discrete finite-volume divergence operator cancels interior fluxes identically.
* **Property C (Schoof Exponent Emergence):** Asymptotic matching proves $\gamma = \frac{m+n+3}{m+1}$ analytically.
* **Property D (Irreducible Diagonal Dominance & Pivot Safety):** Proven algebraically that the SSA tridiagonal matrix is irreducibly diagonally dominant, strictly non-singular, and has non-zero Thomas pivots.
* **Property E (Linear Regional Additivity):** $\Delta V_{\text{Domain A}} \equiv \sum \Delta V_{\text{basins}}$ holds by construction.

### 7.2 Planned Numerical Verification Tests (Phase 5.2.2 Execution)
* **Tests 1--10:** Idealized canonical benchmarks (equilibrium, accumulation, discharge, steady-state, relaxation, sinusoidal climate, MISI retreat, prograde advance, 100-year mass conservation, non-negativity barrier). Includes explicit zero-velocity divide test.
* **Test 11:** Spatial Grid Convergence ($\Delta x \in \{2.0, 1.0, 0.5, 0.25\}\text{ km}$; tolerance $< 2\%$).
* **Test 12:** Temporal Timestep Convergence ($\Delta t \in [0.005, 0.10]\text{ yr}$; tolerance $< 0.5\%$).
* **Test 13:** Sub-Grid Grounding-Line Transition Smoothness Suite (retreat, advance, cyclic crossing, reference comparison, flux jump metric $\le 1.0\%$).
* **Test 14:** Lateral Drag Geometry Sensitivity Suite (aspect ratio $W/H \in [1, 50]$, trough shape factor, velocity exponent $p \in [2, 6]$, wide-embayment vanishing).
* **Test 15:** Drag Regularization Convergence Suite ($u_{\text{reg}} \in \{10^{-6}, 10^{-5}, 10^{-4}, 10^{-3}, 10^{-2}\}\text{ m yr}^{-1}$), verifying finite coefficients ($\beta_b(0) = 4.64 \times 10^{14}\text{ Pa s m}^{-1}$), zero division errors, and asymptotic independence.

---

## 8. Explicit Section on Remaining Unresolved Issues

In accordance with scientific integrity guidelines, the following open technical considerations are explicitly documented for Phase 5.2.2 implementation:

1. **Optimal Choice of Regularization Threshold $u_{\text{reg}}$:**
   The exact value $u_{\text{reg}} = 10^{-4}\text{ m yr}^{-1}$ yields $\beta_{b, \text{reg}}(0) \approx 4.64 \times 10^{14}\text{ Pa s m}^{-1}$, creating a $10^4$ contrast relative to downstream fast flow. While the linear solve is stable, this large contrast may require tight Picard under-relaxation ($\omega \le 0.50$) during initial steps. Test 15 will evaluate whether a slightly higher threshold ($u_{\text{reg}} = 10^{-3}\text{ m yr}^{-1}$ yielding $\beta_b(0) \approx 10^{14}\text{ Pa s m}^{-1}$) provides faster Picard convergence without degrading forward trajectory accuracy.
2. **Coupling of Lateral Shear with Longitudinal Stretching in Non-Rectangular Troughs:**
   The adopted lateral drag formula $\tau_{\text{wall}} = (5 \bar{u}/(AW))^{1/n}$ assumes pure uncoupled horizontal shear in a rectangular trough. Real alpine valleys in Graham Land have parabolic or trapezoidal cross-sections where lateral shear couples with vertical shear and longitudinal stretching. Test 14 is specifically designed to quantify the sensitivity of grounding-line retreat to this 1D geometric approximation.
3. **Picard Convergence Robustness Under Catastrophic Buttressing Loss:**
   When an ice shelf experiences instantaneous collapse ($\theta_{\text{buttress}} \to 0$), the grounding-line velocity jumps by a factor of $R_{\text{surge}} \in [2.5\times, 6.0\times]$. In fixed-point Picard iteration, large sudden boundary velocity shocks can cause iterative oscillations. The emergency adaptive step-halving protocol is designed to mitigate this, but if convergence remains slow under extreme forcing, an operational switch to a damped Newton-Raphson or continuation method will be evaluated during Phase 5.2.2 implementation.

---

## 9. Final Scientific Review & Gate Determination

```
========================================================================================================
FINAL FORMAL DETERMINATION: PASS — READY FOR IMPLEMENTATION AUTHORIZATION REVIEW
========================================================================================================
1. Basal Drag Arithmetic:        CORRECTED: beta_b_reg(0) = 4.6352e14 Pa s m^-1 in SI units;
                                 Previous 4.64e10 slip resolved. Conditioning and Picard impact documented.
2. Linear Stability Terms:       REFINED: Irreducible diagonal dominance proves non-singularity (Taussky).
                                 Symmetry and SPD hold upon Dirichlet partitioning. Thomas pivots strictly positive.
                                 Conditioning kappa ~ O(N^2 * contrast) ~ 10^8. Blanket stability claims revoked.
3. Lateral Glen Law:             DERIVED: Full tensor invariants specialized to pure horizontal shear.
                                 Tensorial 1/2 cancels 10/W to yield (5 u / (A W))^(1/n). Qualified as reduced-order.
4. Grounding-Line Boundary:      COUPLED: Dirichlet velocity u_GL = q_GL / h_GL justified for coarse-grid SSA.
                                 Moving-boundary mass budget (Reynolds) vs Eulerian cell updates prevents double-counting.
5. Conditioning & Defaults:      QUALIFIED: Condition number scaling derived; 25 iterations and omega=0.60
                                 explicitly classified as operational defaults/heuristics triggering step halving.
6. Parameter & Test Suite:       22 parameters audited; 15 verification tests specified in test plan.
7. Phase 5.2.2 Status:           PHASE 5.2.2 IMPLEMENTATION REMAINS STRICTLY LOCKED.
                                 Separate explicit approval required after independent review.
========================================================================================================
```
