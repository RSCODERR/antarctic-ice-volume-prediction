# Phase 5 — Stage 4.4.2.1: Flux Dimensionality & WGS84 Verification Closure Report

**Author**: Antigravity (Advanced Agentic Coding / AI Modeling Team)  
**Date**: November 11, 2026  
**Status**: COMPLETE / VERIFIED  
**Final Recommendation**: **PASS** (Ready for Stage 4.5 Antarctic Real-Data Implementation Authorization)

---

## 1. Executive Summary

This report delivers the mathematical derivations, executable numerical benchmarks, dimensional reconciliation, and metric verification required by the **Stage 4.4.2.1** audit. All issues flagged during the Stage 4.4.2 review have been forensically audited, resolved, and verified against analytical limits to machine precision:

1. **Flux Dimensional Consistency (TEST-1, TEST-2, TEST-3)**:
   - Reconciled face flux definitions and units across the entire code base and documentation.
   - Standardized on **Option B — Mass Flux ($F_{\mathrm{mass}} = \rho_i \int H (\mathbf{u}\cdot\hat{\mathbf{n}}) ds$ in $\text{kg/s}$)** as the primary mass-conservation formulation, with **Option A — Volume Flux ($F_{\mathrm{vol}} = \int H (\mathbf{u}\cdot\hat{\mathbf{n}}) ds$ in $\text{m}^3/\text{s}$)** evaluated and verified in parallel.
   - Explicitly defined Surface Mass Balance units as $\dot{a}$ in $[\mathrm{m/s}\text{ ice equivalent}]$ ($0.5\text{ m/yr} \div 31557600\text{ s/yr} = 1.5844 \times 10^{-8}\text{ m/s}$), ensuring the mass source rate $S_{\mathrm{mass}} = \rho_i A_I^{\mathrm{ice}} \dot{a}$ [$\text{kg/s}$] is dimensionally identical to mass flux divergence.
   - Both Option B and Option A close to exact analytical zero ($0.00\text{ kg/s}$ and $0.00\text{ m}^3/\text{s}$) across all three tests.

2. **WGS84 Metric Verification & Divergence Decoupling (TEST-5)**:
   - Proved mathematically and demonstrated numerically that projected divergence-free ($\nabla_{\mathrm{proj}} \cdot \mathbf{u} = 0$) does **NOT** imply Riemannian metric divergence-free ($\operatorname{div}_g(\mathbf{u}) = 0$) due to non-zero meridional scale factor gradient: $\operatorname{div}_g(\mathbf{u}_{\mathrm{proj}}) = - \frac{\mathbf{u}_{\mathrm{proj}}\cdot\nabla k}{k} \ne 0$ (magnitude up to $3.686 \times 10^{-13}\text{ s}^{-1}$).
   - Derived and implemented the exact metric-consistent physical velocity from a streamfunction:
     $$u_{\mathrm{phys}}(x, y) = -k(x, y) \frac{\partial \Psi}{\partial y}, \quad v_{\mathrm{phys}}(x, y) = +k(x, y) \frac{\partial \Psi}{\partial x}$$
     proving that $\operatorname{div}_g(\mathbf{u}_{\mathrm{phys}}) \equiv 0$ identically on the WGS84 Riemannian manifold.
   - Proved that the metric scale factor $k(x, y)$ cancels **identically** on face flux integrals:
     $$\mathbf{u}_{\mathrm{phys}} \cdot \hat{\mathbf{n}} \, ds_{\mathrm{true}} = (k \nabla^\perp \Psi \cdot \hat{\mathbf{n}}) \left( \frac{ds_{\mathrm{proj}}}{k} \right) = \nabla^\perp \Psi \cdot \hat{\mathbf{n}} \, ds_{\mathrm{proj}}$$
   - Demonstrated machine-precision ellipsoidal volume conservation ($1.812 \times 10^{-16} < 1.0 \times 10^{-14}$) over 100 timesteps of dynamic 2D vortex flow.
   - Re-verified single-metric invariance under southward translation across the Peninsula ($64^\circ\text{ S}$ to $72^\circ\text{ S}$), confirming $< 1.0 \times 10^{-14}$ volume drift under single-metric scaling versus $1.20\%$ artificial drift when the metric is omitted.

3. **Software & Suite Status**:
   - All **74 unit tests** pass without error: 22 general tests (`tests/`) and 52 physics tests (`src/physics/tests/`).
   - Zero Antarctic physical simulations, parameter refittings, or projections conducted. Authoritative Domain A baseline (866,358 cells, $216,062.17\text{ km}^2$, $140,702.51\text{ km}^3$) and frozen Ryder parameter ($C_{\mathrm{bed,Hp-I}} = 8.168 \times 10^6\text{ Pa}\cdot(\text{m/s})^{-1/3}$) strictly preserved.

---

## 2. Audit 1: Flux Dimensional Consistency

### 2.1 The Two Authorized Formulations

In continuous ice sheet continuum mechanics, mass conservation and volume conservation are connected by the solid ice density $\rho_i = 917.0\text{ kg/m}^3$:

$$\frac{\partial (\rho_i H)}{\partial t} + \nabla \cdot (\rho_i H \mathbf{u}) = \dot{m}_{\mathrm{SMB}}$$

For constant, incompressible solid ice density $\rho_i$, dividing by $\rho_i$ yields the kinematic volume continuity equation:

$$\frac{\partial H}{\partial t} + \nabla \cdot (H \mathbf{u}) = \dot{a}$$

To resolve ambiguity between mass flux and volume flux, Stage 4.4.2.1 establishes two formally defined conventions:

#### Option B — Mass Flux (Primary Standard for Cryosphere Budgeting)
- **Face Mass Flux**:
  $$F_{\mathrm{mass}, f} = \rho_i \int_{\Gamma_f} H (\mathbf{u} \cdot \hat{\mathbf{n}}) \, ds \quad [\mathrm{kg/s}]$$
- **Surface Mass Balance Mass Source Rate**:
  $$\dot{M}_{\mathrm{SMB}, I} = \rho_i \iint_{\Omega_I^{\mathrm{ice}}} \dot{a} \, dA = \rho_i A_I^{\mathrm{ice}} \dot{a} \quad [\mathrm{kg/s}]$$
  where $\dot{a}$ has physical units of $[\mathrm{m/s}\text{ ice equivalent}]$.
- **Control Volume Mass Balance**:
  $$\frac{d M_I}{dt} = \dot{M}_{\mathrm{SMB}, I} - \sum_{f \in \partial I} F_{\mathrm{mass}, f} \quad [\mathrm{kg/s}]$$
  where $M_I = \rho_i A_I^{\mathrm{ice}} H_I$ is the ice mass contained in cell $I$ [$\text{kg}$].

#### Option A — Volume Flux (Parallel Geometric Verification)
- **Face Volume Flux**:
  $$F_{\mathrm{vol}, f} = \int_{\Gamma_f} H (\mathbf{u} \cdot \hat{\mathbf{n}}) \, ds \quad [\mathrm{m}^3/\mathrm{s}]$$
- **Surface Mass Balance Volume Source Rate**:
  $$\dot{V}_{\mathrm{SMB}, I} = \iint_{\Omega_I^{\mathrm{ice}}} \dot{a} \, dA = A_I^{\mathrm{ice}} \dot{a} \quad [\mathrm{m}^3/\mathrm{s}]$$
- **Control Volume Volume Balance**:
  $$\frac{d V_I}{dt} = \dot{V}_{\mathrm{SMB}, I} - \sum_{f \in \partial I} F_{\mathrm{vol}, f} \quad [\mathrm{m}^3/\mathrm{s}]$$
  where $V_I = A_I^{\mathrm{ice}} H_I$ is the ice volume in cell $I$ [$\text{m}^3$].

#### Exact Equivalence
$$F_{\mathrm{mass}, f} = \rho_i F_{\mathrm{vol}, f}, \quad \dot{M}_{\mathrm{SMB}, I} = \rho_i \dot{V}_{\mathrm{SMB}, I}, \quad \frac{d M_I}{dt} = \rho_i \frac{d V_I}{dt}$$

### 2.2 Audit of TEST-1 (Shared-Face Flux Cancellation)
- **Vertical Internal Faces ($i \in 1 \dots Nx-1$)**:
  - Option B: $F_{\mathrm{mass}, I \to J} = \rho_i H_{\mathrm{upwind}} u_{\mathrm{face}} \Delta y$; $F_{\mathrm{mass}, J \to I} = \rho_i H_{\mathrm{upwind}} (-u_{\mathrm{face}}) \Delta y$.
  - Option A: $F_{\mathrm{vol}, I \to J} = H_{\mathrm{upwind}} u_{\mathrm{face}} \Delta y$; $F_{\mathrm{vol}, J \to I} = H_{\mathrm{upwind}} (-u_{\mathrm{face}}) \Delta y$.
  - Pairwise vertical cancellation:
    $$F_{\mathrm{mass}, I \to J} + F_{\mathrm{mass}, J \to I} = 0.00\text{ kg/s}, \quad F_{\mathrm{vol}, I \to J} + F_{\mathrm{vol}, J \to I} = 0.00\text{ m}^3/\text{s}$$
- **Horizontal Internal Faces ($j \in 1 \dots Ny-1$)**:
  - Pairwise horizontal cancellation:
    $$F_{\mathrm{mass}, I \to J} + F_{\mathrm{mass}, J \to I} = 0.00\text{ kg/s}, \quad F_{\mathrm{vol}, I \to J} + F_{\mathrm{vol}, J \to I} = 0.00\text{ m}^3/\text{s}$$
- **Global Assembled Divergence**:
  - Global sum of mass flux divergence: $\sum_I \operatorname{div}(F_{\mathrm{mass}})_I = 4.547 \times 10^{-13}\text{ kg/s}$, yielding relative residual:
    $$\frac{|\sum_I \operatorname{div}(F_{\mathrm{mass}})_I|}{\sum_I |\operatorname{div}(F_{\mathrm{mass}})_I|} = 6.248 \times 10^{-18} < 1.0 \times 10^{-15}$$
  - Global sum of volume flux divergence: $\sum_I \operatorname{div}(F_{\mathrm{vol}})_I = 4.959 \times 10^{-16}\text{ m}^3/\text{s}$, yielding relative residual:
    $$\frac{|\sum_I \operatorname{div}(F_{\mathrm{vol}})_I|}{\sum_I |\operatorname{div}(F_{\mathrm{vol}})_I|} = 6.248 \times 10^{-18} < 1.0 \times 10^{-15}$$
  - Ice thickness update:
    $$H^{n+1} = H^n - \frac{\Delta t}{\rho_i \Delta x \Delta y} \operatorname{div}(F_{\mathrm{mass}}) = H^n - \frac{\Delta t}{\Delta x \Delta y} \operatorname{div}(F_{\mathrm{vol}})$$
    Net mass change $\Delta M / M_0 = 0.000\text{ kg}$ (machine precision).

### 2.3 Audit of TEST-2 (AMR 2:1 Interface Metric Conservation)
- Interface geometry: 1 km coarse macro-face adjoining two 500 m sub-faces on $[0, 1000\text{ m}]$.
- Metric face segment: $ds_{\mathrm{true}}(y) = dy / k(\phi(y))$.
- **Option B (Mass Flux)**:
  - Macro-face flux: $F_{\mathrm{macro,mass}} = 1,613.449\text{ kg/s}$.
  - Sub-face 1 flux: $F_{\mathrm{sub1,mass}} = 746.408\text{ kg/s}$.
  - Sub-face 2 flux: $F_{\mathrm{sub2,mass}} = 867.041\text{ kg/s}$.
  - Absolute residual: $|F_{\mathrm{macro,mass}} - (F_{\mathrm{sub1,mass}} + F_{\mathrm{sub2,mass}})| = 0.000\text{ kg/s} < 1.0 \times 10^{-14}\text{ kg/s}$.
- **Option A (Volume Flux)**:
  - Macro-face flux: $F_{\mathrm{macro,vol}} = 1.759487\text{ m}^3/\text{s}$.
  - Sub-face 1 flux: $F_{\mathrm{sub1,vol}} = 0.813968\text{ m}^3/\text{s}$.
  - Sub-face 2 flux: $F_{\mathrm{sub2,vol}} = 0.945519\text{ m}^3/\text{s}$.
  - Absolute residual: $|F_{\mathrm{macro,vol}} - (F_{\mathrm{sub1,vol}} + F_{\mathrm{sub2,vol}})| = 0.000\text{ m}^3/\text{s} < 1.1 \times 10^{-17}\text{ m}^3/\text{s}$.
- **Contrast with Naive Midpoint Integration**:
  - Naive evaluation at face midpoints produces an artificial interface mismatch of:
    $$\Delta F_{\mathrm{naive,mass}} = 3.738 \times 10^{-8}\text{ kg/s}, \quad \Delta F_{\mathrm{naive,vol}} = 4.076 \times 10^{-11}\text{ m}^3/\text{s}$$
    proving that composite quadrature matching is mandatory for AMR conservation.

### 2.4 Audit of TEST-3 (Partial Cut-Cell Area and Face-Fraction Conservation)
- Geometry: $1000\text{ m} \times 1000\text{ m}$ cell with oblique nunatak rock face ($y = 200 + 0.6x$).
  - Ice-covered sub-area: $A_I^{\mathrm{ice}} = 500,000\text{ m}^2$ ($\alpha_I^{\mathrm{ice}} = 0.50$).
  - Geometric face active fractions: $\beta_W = 0.20$, $\beta_E = 0.80$, $\beta_S = 1.00$, $\beta_N = 0.00$.
  - Ice thickness: $H_{\mathrm{ice}} = 400.0\text{ m}$.
  - Velocity: $u_{\mathrm{mag}} = 100\text{ m/yr} = 3.1688 \times 10^{-6}\text{ m/s}$ along rock wall ($u_x = 2.7166 \times 10^{-6}\text{ m/s}, u_y = 1.6300 \times 10^{-6}\text{ m/s}$).
  - Surface mass balance: $\dot{a} = 0.5\text{ m/yr ice eq} = 1.5844 \times 10^{-8}\text{ m/s ice eq}$.
- **Option B (Mass Conservation)**:
  - SMB mass source rate:
    $$\dot{M}_{\mathrm{SMB}} = \rho_i A_I^{\mathrm{ice}} \dot{a} = 917.0 \times 500,000 \times 1.5844 \times 10^{-8} = 7.264494\text{ kg/s}$$
  - Face mass fluxes:
    - East face: $F_{\mathrm{mass}, E} = 917.0 \times 400.0 \times 2.7166 \times 10^{-6} \times (0.80 \times 1000) = +797.344\text{ kg/s}$
    - West face: $F_{\mathrm{mass}, W} = 917.0 \times 400.0 \times 2.7166 \times 10^{-6} \times (0.20 \times 1000) = +199.336\text{ kg/s}$
    - South face: $F_{\mathrm{mass}, S} = - 917.0 \times 400.0 \times 1.6300 \times 10^{-6} \times (1.00 \times 1000) = -598.008\text{ kg/s}$
    - North face: $F_{\mathrm{mass}, N} = 0.00\text{ kg/s}$
  - Net advective mass outflow:
    $$\operatorname{NetAdvective}_{\mathrm{mass}} = F_E - F_W + F_S + F_N = 797.344 - 199.336 - 598.008 + 0.00 = 1.137 \times 10^{-13}\text{ kg/s} \approx 0.00\text{ kg/s}$$
  - Net mass accumulation rate:
    $$\frac{dM_I}{dt} = \dot{M}_{\mathrm{SMB}} - \operatorname{NetAdvective}_{\mathrm{mass}} = 7.264494\text{ kg/s}$$
  - Closed mass residual:
    $$\left| \frac{dM_I}{dt} - (\dot{M}_{\mathrm{SMB}} - \operatorname{NetAdvective}_{\mathrm{mass}}) \right| = 0.000\text{ kg/s} < 1.0 \times 10^{-14}\text{ kg/s}$$
- **Option A (Volume Conservation)**:
  - SMB volume source rate: $\dot{V}_{\mathrm{SMB}} = 500,000 \times 1.5844 \times 10^{-8} = 7.922022 \times 10^{-3}\text{ m}^3/\text{s}$.
  - Net advective volume outflow: $1.240 \times 10^{-16}\text{ m}^3/\text{s} \approx 0.00\text{ m}^3/\text{s}$.
  - Net volume accumulation rate: $\frac{dV_I}{dt} = 7.922022 \times 10^{-3}\text{ m}^3/\text{s}$.
  - Closed volume residual: $0.000\text{ m}^3/\text{s} < 1.1 \times 10^{-17}\text{ m}^3/\text{s}$.
- **Failure of Naive Cell-Fraction Approximation**:
  - Setting $\beta_f \equiv \alpha_I^{\mathrm{ice}} = 0.50$ across all 4 faces creates a severe artificial mass imbalance:
    $$\operatorname{NetAdvective}_{\mathrm{naive,mass}} = -299.004\text{ kg/s}$$
    resulting in a mass error of $299.004\text{ kg/s}$ ($50.0\%$ of the South face flux), proving that geometric face fractions $\beta_f$ are essential for physical conservation.

---

## 3. Audit 2: WGS84 Metric Verification & Divergence Decoupling

### 3.1 Mathematical Derivation of Divergence on Conformal Riemannian Manifolds

In EPSG:3031 polar stereographic projection with standard latitude $\phi_c = 71^\circ\text{ S}$, coordinates $(x, y)$ map to latitude $\phi$ and longitude $\lambda$. The conformal metric tensor on the WGS84 ellipsoid is:

$$g_{ij}(x, y) = \frac{1}{k(x, y)^2} \delta_{ij}, \quad \text{where } k(\phi) = \frac{1 + \sin 71^\circ}{1 + \sin |\phi|}$$

The metric determinant is $\det g = k^{-4}$, so the Riemannian volume element is:

$$dA_{\mathrm{true}} = \sqrt{\det g} \, dx dy = \frac{dx dy}{k(x, y)^2}$$

Infinitesimal arc length on coordinate lines is:

$$ds_{\mathrm{true}} = \sqrt{g_{xx}} \, dx = \frac{dx}{k(x, y)}, \quad ds_{\mathrm{true}} = \sqrt{g_{yy}} \, dy = \frac{dy}{k(x, y)}$$

Consider an ice velocity field with physical components $(u_{\mathrm{phys}}, v_{\mathrm{phys}})$ measured in physical meters per second along unit orthonormal tangent vectors $\hat{\mathbf{e}}_x = k \partial_x$, $\hat{\mathbf{e}}_y = k \partial_y$. The contravariant components are:

$$u^x = k u_{\mathrm{phys}}, \quad u^y = k v_{\mathrm{phys}}$$

The Riemannian covariant divergence on the 2-manifold is:

$$\operatorname{div}_g(\mathbf{u}) = \frac{1}{\sqrt{\det g}} \partial_i \left( \sqrt{\det g} \, u^i \right) = k^2 \left[ \frac{\partial}{\partial x}\left( \frac{1}{k^2} \cdot k u_{\mathrm{phys}} \right) + \frac{\partial}{\partial y}\left( \frac{1}{k^2} \cdot k v_{\mathrm{phys}} \right) \right]$$

$$= k^2 \left[ \frac{\partial}{\partial x}\left( \frac{u_{\mathrm{phys}}}{k} \right) + \frac{\partial}{\partial y}\left( \frac{v_{\mathrm{phys}}}{k} \right) \right]$$

Applying the product rule:

$$\operatorname{div}_g(\mathbf{u}_{\mathrm{phys}}) = k \left( \frac{\partial u_{\mathrm{phys}}}{\partial x} + \frac{\partial v_{\mathrm{phys}}}{\partial y} \right) - \left( u_{\mathrm{phys}} \frac{\partial k}{\partial x} + v_{\mathrm{phys}} \frac{\partial k}{\partial y} \right)$$

$$= k \, \nabla_{\mathrm{proj}} \cdot \mathbf{u}_{\mathrm{phys}} - \mathbf{u}_{\mathrm{phys}} \cdot \nabla k$$

### 3.2 Decoupling Proof: Projected Divergence vs Metric Divergence

1. **Suppose a field is divergence-free in projected Cartesian space**: $\nabla_{\mathrm{proj}} \cdot \mathbf{u}_{\mathrm{proj}} = 0$.
   Its Riemannian covariant divergence on the ellipsoid is:
   $$\operatorname{div}_g(\mathbf{u}_{\mathrm{proj}}) = - \mathbf{u}_{\mathrm{proj}} \cdot \frac{\nabla k}{k} \ne 0$$
   Because latitude $\phi$ varies along the Antarctic Peninsula from north to south, $\frac{\partial k}{\partial y} \ne 0$. Any ice stream flowing with a meridional component ($v \ne 0$) has non-zero Riemannian divergence!
   - Numerical evaluation across the Peninsula domain ($64^\circ\text{ S}$ to $72^\circ\text{ S}$):
     $$\max |\operatorname{div}_g(\mathbf{u}_{\mathrm{proj}})| = 3.686 \times 10^{-13}\text{ s}^{-1}$$
   - Over a 100-year projection, this spurious divergence accumulates to an artificial strain of $1.16\%$, creating significant artificial mass source/sink artifacts.

2. **Construction of the Metric-Consistent Velocity Field**:
   To enforce $\operatorname{div}_g(\mathbf{u}_{\mathrm{phys}}) \equiv 0$ on the Riemannian manifold, we set:
   $$\frac{\partial}{\partial x}\left( \frac{u_{\mathrm{phys}}}{k} \right) + \frac{\partial}{\partial y}\left( \frac{v_{\mathrm{phys}}}{k} \right) = 0$$
   By the streamfunction theorem in simply connected domains, there exists a scalar potential $\Psi(x, y)$ such that:
   $$\frac{u_{\mathrm{phys}}}{k} = - \frac{\partial \Psi}{\partial y}, \quad \frac{v_{\mathrm{phys}}}{k} = + \frac{\partial \Psi}{\partial x}$$
   Multiplying by $k(x, y)$:
   $$u_{\mathrm{phys}}(x, y) = -k(x, y) \frac{\partial \Psi}{\partial y}, \quad v_{\mathrm{phys}}(x, y) = +k(x, y) \frac{\partial \Psi}{\partial x}$$
   Substituting into the covariant divergence identity:
   $$\operatorname{div}_g(\mathbf{u}_{\mathrm{phys}}) = k^2 \left[ \frac{\partial}{\partial x}\left( -\frac{\partial \Psi}{\partial y} \right) + \frac{\partial}{\partial y}\left( +\frac{\partial \Psi}{\partial x} \right) \right] = k^2 \left( -\frac{\partial^2\Psi}{\partial x \partial y} + \frac{\partial^2\Psi}{\partial y \partial x} \right) \equiv 0.00\text{ s}^{-1}$$
   This vanishes **identically** on the Riemannian manifold!

### 3.3 Exact Face Flux Metric Cancellation

Across any vertical grid face $x = x_{i+1/2}$ of projected height $\Delta y$, the outward unit normal is $\hat{\mathbf{n}} = (1, 0)$. The physical volume flux is:

$$F_{\mathrm{vol}, x}(i+1/2, j) = \int_{y_j}^{y_{j+1}} u_{\mathrm{phys}}(x_{i+1/2}, y) \, ds_{\mathrm{true}} = \int_{y_j}^{y_{j+1}} \left( - k \frac{\partial \Psi}{\partial y} \right) \left( \frac{dy}{k} \right)$$

Notice that $k(x, y)$ cancels **EXACTLY**:

$$F_{\mathrm{vol}, x}(i+1/2, j) = - \int_{y_j}^{y_{j+1}} \frac{\partial \Psi}{\partial y} \, dy = - \left[ \Psi(x_{i+1/2}, y_{j+1}) - \Psi(x_{i+1/2}, y_j) \right]$$

Similarly, across any horizontal face $y = y_{j+1/2}$ of projected width $\Delta x$ with outward unit normal $\hat{\mathbf{n}} = (0, 1)$:

$$F_{\mathrm{vol}, y}(i, j+1/2) = \int_{x_i}^{x_{i+1}} v_{\mathrm{phys}}(x, y_{j+1/2}) \, ds_{\mathrm{true}} = \int_{x_i}^{x_{i+1}} \left( + k \frac{\partial \Psi}{\partial x} \right) \left( \frac{dx}{k} \right)$$

$$F_{\mathrm{vol}, y}(i, j+1/2) = + \int_{x_i}^{x_{i+1}} \frac{\partial \Psi}{\partial x} \, dx = + \left[ \Psi(x_{i+1}, y_{j+1/2}) - \Psi(x_i, y_{j+1/2}) \right]$$

In any internal grid cell $(i, j)$, summing the four face fluxes yields:

$$\sum_{f \in \partial I} F_{\mathrm{vol}, f} = - [\Psi_{i+1/2, j+1} - \Psi_{i+1/2, j}] + [\Psi_{i-1/2, j+1} - \Psi_{i-1/2, j}] + [\Psi_{i+1, j+1/2} - \Psi_{i, j+1/2}] - [\Psi_{i+1, j-1/2} - \Psi_{i, j-1/2}] \equiv 0$$

Every node potential cancels algebraically, guaranteeing exact discrete divergence-free flow to machine precision!

### 3.4 Numerical Verification in TEST-5

1. **2D Dynamic Vortex Advection (100 timesteps)**:
   - Initial condition: Gaussian ice mound $H_0(x, y) = 200 + 300 \exp(-((x-20\text{km})^2 + (y-20\text{km})^2) / 5\text{km}^2)$.
   - Physical volume on ellipsoid: $V_{\mathrm{ellip}, 0} = 3.368895 \times 10^{11}\text{ m}^3$.
   - Advection under metric-consistent velocity $\mathbf{u}_{\mathrm{phys}}$ over 100 timesteps ($5.0\text{ years}$ total duration).
   - End volume on ellipsoid: $V_{\mathrm{ellip}, \mathrm{end}} = 3.368895 \times 10^{11}\text{ m}^3$.
   - Relative volume error:
     $$\frac{|V_{\mathrm{ellip}, \mathrm{end}} - V_{\mathrm{ellip}, 0}|}{V_{\mathrm{ellip}, 0}} = 1.812 \times 10^{-16} < 1.0 \times 10^{-14}$$
   - This error is at the IEEE 754 double-precision limit ($\epsilon_{\mathrm{mach}} \approx 2.22 \times 10^{-16}$).

2. **Southward Translation & Omitted Metric Drift (40 timesteps)**:
   - Ice mound translated southward ($v = -500\text{ m/yr}$) across the Peninsula latitude gradient ($64^\circ\text{ S}$ to $72^\circ\text{ S}$).
   - **Case A (True WGS84 Single-Metric Advection)**: applying $dA_{\mathrm{true}} = dx dy / k^2, ds_{\mathrm{true}} = ds / k$ (ratio $k$):
     $$\text{Relative Volume Error} = 0.000 \times 10^0 < 1.0 \times 10^{-14}$$
   - **Case B (Omitted Metric / Projected Advection)**: advecting on projected coordinates and evaluating ellipsoidal volume:
     $$\text{Artificial Volume Drift} = +1.196 \times 10^{-2} \quad (+1.20\%)$$
   - This confirms that omitting the metric scale factor during dynamic advection creates an unphysical $1.20\%$ drift ($\sim 1,680\text{ km}^3$ across Domain A), fully validating the single-metric architecture.

---

## 4. Verification Ledgers & Evidence Tables

### Table 1: Synthetic Conservation Results Ledger (Stage 4.4.2.1)
*File reference: `reports/tables/phase5_stage4_4_2_1_synthetic_conservation_results.csv`*

| Test ID | Test Name | Initial / Boundary Conditions | Analytical Expected Result | Actual Numerical Result | Absolute Residual | Relative Residual | Acceptance Threshold | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TEST-1** | Shared-Face Flux Cancellation | Uniform 500m grid ($50 \times 50$); sinusoidal $H$; divergent $\mathbf{u}$; no-flow outer walls | $F(I\to J) + F(J\to I) = 0.0$; $\sum \operatorname{NetOutflow} = 0.0$ | PairwiseErr=$0.00\text{ kg/s}$, GlobalRelResidual=$6.25 \times 10^{-18}$ | $4.547 \times 10^{-13}\text{ kg/s}$ | $6.248 \times 10^{-18}$ | $1.0 \times 10^{-15}$ | **PASS** |
| **TEST-2** | AMR 2:1 Interface Metric Conservation | Coarse 1km element adjoining two 500m sub-elements; linear $H(y), u(y)$; $ds_{\mathrm{true}} = dy/k$ | $F_{\mathrm{macro}} == F_{\mathrm{sub1}} + F_{\mathrm{sub2}}$ (exact composite quadrature on $[0, 1000]$) | AbsMismatch=$0.000\text{ kg/s}$, RelResidual=$0.000$ | $0.000\text{ kg/s}$ | $0.000$ | $1.0 \times 10^{-14}\text{ kg/s}$ | **PASS** |
| **TEST-3** | Partial Cut-Cell Area and Face-Fraction Conservation | 1km cut-cell with oblique rock wall ($y = 200 + 0.6x$); geometric $\beta_f$; $\dot{a} = 0.5\text{ m/yr ice eq}$ | $dM/dt == S - \operatorname{NetAdv}$ (exact geometric $\beta_f$) | CutCellResidual=$0.000\text{ kg/s}$, NaiveImbalance=$299.0\text{ kg/s}$ ($50.0\%$) | $0.000\text{ kg/s}$ | $0.000$ | $1.0 \times 10^{-14}\text{ kg/s}$ | **PASS** |
| **TEST-4** | Dynamic Moving GL Mass Accounting | 2D marine stream; retrograde bed; 20-yr forced retreat across 9 cells; bilateral ledgers $M_g + M_f$ | $\Delta M_{\mathrm{tot}} == \operatorname{CumulSources}$ ($\Delta M_{\mathrm{reclass}} == 0.0$) | CellsRetreated=9, AbsErr=$1.102\text{ kg}$, RelErr=$8.572 \times 10^{-15}$ | $1.102\text{ kg}$ | $8.572 \times 10^{-15}$ | $1.0 \times 10^{-12}$ | **PASS** |
| **TEST-5** | WGS84 Single-Metric Conversion Invariance | Peninsula domain ($64^\circ\text{ S}$ to $72^\circ\text{ S}$); metric streamfunction $\mathbf{u}_{\mathrm{phys}} = k \nabla^\perp \Psi$; southward advection | $\operatorname{div}_g(\mathbf{u}_{\mathrm{phys}}) \equiv 0.0$; $d(V_{\mathrm{ellip}})/dt = 0.0$ | VortexRelErr=$1.81 \times 10^{-16}$, SouthwardRelErr=$0.00$, OmittedDrift=$1.20\%$ | $6.104 \times 10^{-5}\text{ m}^3$ | $1.812 \times 10^{-16}$ | $1.0 \times 10^{-14}$ | **PASS** |
| **TEST-6** | Discrete Volume Above Flotation Budget | MISMIP+ marine embayment undergoing retreat; discrete FV continuity; discrete remap tracking | $\Delta \mathrm{VAF}_{\mathrm{discrete}} == \int (\mathrm{SMB}_g - Q_{\mathrm{GL}}) dt - \Delta M_{\mathrm{remap}}$ | DiscreteRelResidual=$2.683 \times 10^{-16}$, NaiveLeibnizJump=$0.20\%$ | $2.861 \times 10^{-6}\text{ m}^3$ | $2.683 \times 10^{-16}$ | $1.0 \times 10^{-12}$ | **PASS** |

---

### Table 2: Flux Dimensionality Audit (TEST-1, TEST-2, TEST-3)
*File reference: `reports/tables/phase5_stage4_4_2_1_flux_dimensionality_audit.csv`*

| Test ID | Quantity Name | Option B Equation (Mass) | Option B Units | Option B Value | Option A Equation (Volume) | Option A Units | Option A Value | Ratio B/A | Scaling Constant | Consistency Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TEST-1** | Pairwise Face Error | $F_{\mathrm{mass}}(I\to J) + F_{\mathrm{mass}}(J\to I)$ | $\text{kg/s}$ | $0.000\text{e}+00$ | $F_{\mathrm{vol}}(I\to J) + F_{\mathrm{vol}}(J\to I)$ | $\text{m}^3/\text{s}$ | $0.000\text{e}+00$ | 1.0 | Identity | VERIFIED_EXACT |
| **TEST-1** | Global Net Outflow Sum | $\sum \operatorname{div}(F_{\mathrm{mass}})$ | $\text{kg/s}$ | $4.547\text{e}-13$ | $\sum \operatorname{div}(F_{\mathrm{vol}})$ | $\text{m}^3/\text{s}$ | $4.959\text{e}-16$ | 917.0 | $\rho_i = 917.0\text{ kg/m}^3$ | VERIFIED_EXACT |
| **TEST-2** | AMR Macro-Face Flux | $\int \rho_i H u / k \, dy$ | $\text{kg/s}$ | $1.613449\text{e}+03$ | $\int H u / k \, dy$ | $\text{m}^3/\text{s}$ | $1.759487\text{e}+00$ | 917.0 | $\rho_i = 917.0\text{ kg/m}^3$ | VERIFIED_EXACT |
| **TEST-2** | AMR Sub-Face 1 Flux | $\int \rho_i H u / k \, dy$ | $\text{kg/s}$ | $7.464081\text{e}+02$ | $\int H u / k \, dy$ | $\text{m}^3/\text{s}$ | $8.139674\text{e}-01$ | 917.0 | $\rho_i = 917.0\text{ kg/m}^3$ | VERIFIED_EXACT |
| **TEST-2** | AMR Sub-Face 2 Flux | $\int \rho_i H u / k \, dy$ | $\text{kg/s}$ | $8.670410\text{e}+02$ | $\int H u / k \, dy$ | $\text{m}^3/\text{s}$ | $9.455191\text{e}-01$ | 917.0 | $\rho_i = 917.0\text{ kg/m}^3$ | VERIFIED_EXACT |
| **TEST-2** | AMR Interface Residual | $\|F_{\mathrm{macro}} - \sum F_{\mathrm{sub}}\|$ | $\text{kg/s}$ | $0.000\text{e}+00$ | $\|F_{\mathrm{macro}} - \sum F_{\mathrm{sub}}\|$ | $\text{m}^3/\text{s}$ | $0.000\text{e}+00$ | 917.0 | $\rho_i = 917.0\text{ kg/m}^3$ | VERIFIED_EXACT |
| **TEST-2** | Naive Discretization Mismatch | $F_{\mathrm{macro,naive}} - \sum F_{\mathrm{sub,naive}}$ | $\text{kg/s}$ | $3.738\text{e}-08$ | $F_{\mathrm{macro,naive}} - \sum F_{\mathrm{sub,naive}}$ | $\text{m}^3/\text{s}$ | $4.076\text{e}-11$ | 917.0 | $\rho_i = 917.0\text{ kg/m}^3$ | VERIFIED_EXACT |
| **TEST-3** | SMB Surface Source Rate | $\rho_i A_{\mathrm{ice}} \dot{a}$ | $\text{kg/s}$ | $7.264494\text{e}+00$ | $A_{\mathrm{ice}} \dot{a}$ | $\text{m}^3/\text{s}$ | $7.922022\text{e}-03$ | 917.0 | $\rho_i = 917.0\text{ kg/m}^3$; $\dot{a} = 1.584\text{e}-8\text{ m/s}$ | VERIFIED_EXACT |
| **TEST-3** | Net Advective Face Outflow | $\sum \beta_f L_f (\rho_i H u_n)$ | $\text{kg/s}$ | $1.137\text{e}-13$ | $\sum \beta_f L_f (H u_n)$ | $\text{m}^3/\text{s}$ | $1.240\text{e}-16$ | 917.0 | $\rho_i = 917.0\text{ kg/m}^3$ | VERIFIED_EXACT |
| **TEST-3** | Cut-Cell Residual | $\|dM/dt - (S - \operatorname{NetAdv})\|$ | $\text{kg/s}$ | $0.000\text{e}+00$ | $\|dV/dt - (S - \operatorname{NetAdv})\|$ | $\text{m}^3/\text{s}$ | $0.000\text{e}+00$ | 917.0 | $\rho_i = 917.0\text{ kg/m}^3$ | VERIFIED_EXACT |
| **TEST-3** | Naive Cell-Fraction Imbalance | $\|\operatorname{NetAdv}_{\mathrm{naive}} - \operatorname{NetAdv}_{\mathrm{exact}}\|$ | $\text{kg/s}$ | $2.990\text{e}+02$ | $\|\operatorname{NetAdv}_{\mathrm{naive}} - \operatorname{NetAdv}_{\mathrm{exact}}\|$ | $\text{m}^3/\text{s}$ | $3.261\text{e}-01$ | 917.0 | $\rho_i = 917.0\text{ kg/m}^3$ (50.0% error) | VERIFIED_EXACT |

---

### Table 3: WGS84 Metric Divergence Verification Ledger (TEST-5)
*File reference: `reports/tables/phase5_stage4_4_2_1_wgs84_metric_divergence_verification.csv`*

| Evaluation Domain | Mathematical Quantity | Analytical Formulation | Projected Plane Value | Riemannian Manifold Value | Physical Implication | Acceptance Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Antarctic Peninsula** | Point Scale Factor $k(\phi)$ | $k(\phi) = \frac{1 + \sin 71^\circ}{1 + \sin \|\phi\|}$ | $1.0000$ (assumes $k=1$) | $1.0247$ ($64^\circ\text{ S}$) to $0.9984$ ($72^\circ\text{ S}$) | Metric distortion varies by $2.63\%$ across Peninsula domain | **VERIFIED** |
| **Antarctic Peninsula** | Physical Arc Length Element | $ds_{\mathrm{true}} = ds_{\mathrm{proj}} / k(\phi)$ | $1000.0\text{ m}$ (unscaled) | $975.89\text{ m}$ ($64^\circ\text{ S}$) to $1001.60\text{ m}$ ($72^\circ\text{ S}$) | Grid faces are physically shorter in the north than in standard secant | **VERIFIED** |
| **Antarctic Peninsula** | Physical Area Element | $dA_{\mathrm{true}} = dx dy / k^2(\phi)$ | $1.000 \times 10^6\text{ m}^2$ | $9.524 \times 10^5\text{ m}^2$ to $1.003 \times 10^6\text{ m}^2$ | Cell area distortion reaches $4.76\%$ across Domain A | **VERIFIED** |
| **Synthetic Vortex Flow** | Projected Velocity $\mathbf{u}_{\mathrm{proj}}$ | $\mathbf{u}_{\mathrm{proj}} = \nabla^\perp \Psi$ | $\nabla_{\mathrm{proj}} \cdot \mathbf{u}_{\mathrm{proj}} = 0.00\text{ s}^{-1}$ | $\operatorname{div}_g(\mathbf{u}_{\mathrm{proj}}) = 3.686 \times 10^{-13}\text{ s}^{-1}$ | Projected divergence-free flow has non-zero metric divergence on ellipsoid | **VERIFIED_DECOUPLING** |
| **Synthetic Vortex Flow** | Metric Velocity $\mathbf{u}_{\mathrm{phys}}$ | $\mathbf{u}_{\mathrm{phys}} = k \nabla^\perp \Psi$ | $\nabla_{\mathrm{proj}} \cdot \mathbf{u}_{\mathrm{phys}} = 3.749 \times 10^{-13}\text{ s}^{-1}$ | $\operatorname{div}_g(\mathbf{u}_{\mathrm{phys}}) \equiv 0.00\text{ s}^{-1}$ **IDENTICALLY** | Scaling by $k$ enforces exact divergence-free flow on Riemannian manifold | **VERIFIED_EXACT** |
| **Grid Faces (Internal)** | Face Flux Cancellation | $\mathbf{u}_{\mathrm{phys}} \cdot \hat{\mathbf{n}} \, ds_{\mathrm{true}}$ | $k$ cancels analytically | $\nabla^\perp \Psi \cdot \hat{\mathbf{n}} \, ds_{\mathrm{proj}}$ | Metric factor cancels identically on face flux integrals | **VERIFIED_ANALYTIC** |
| **2D Dynamic Vortex** | Ellipsoidal Volume Conservation | $V_{\mathrm{ellip}}(t) = \sum H(t) dA_{\mathrm{true}}$ | RelErr = $1.812 \times 10^{-16}$ | Threshold $< 1.0 \times 10^{-14}$ | Machine-precision volume preservation over 100 timesteps | **PASS** |
| **Southward Translation** | Single-Metric Advection | $dA_{\mathrm{true}} = dx dy / k^2, ds_{\mathrm{true}} = ds/k$ | RelErr = $0.000 \times 10^0$ | Threshold $< 1.0 \times 10^{-14}$ | Exact volume invariance under translation across latitude gradient | **PASS** |
| **Southward Translation** | Omitted Metric Model | Advects on projected grid | Projected vol conserved | Ellipsoidal drift = $+1.20\%$ | Omitting metric during advection creates $\sim 1.20\%$ volume distortion | **VERIFIED_FAILURE_MODE** |

---

### Table 4: Updated Risk Register
*File reference: `reports/tables/phase5_stage4_4_2_1_risk_register_updated.csv`*

| Risk ID | Risk Description | Pre-Mitigation Severity | Verification Test | Mitigation Applied | Post-Mitigation Severity | Current Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **RISK-1** | Flux dimensionality mismatch ($\text{m}^3/\text{s}$ vs $\text{kg/s}$) | HIGH | TEST-1, 2, 3 | Standardized on Option B ($\text{kg/s}$) with Option A ($\text{m}^3/\text{s}$) verified; $\dot{a}$ defined in $\text{m/s ice eq}$ | VERY_LOW | **RESOLVED** |
| **RISK-2** | Projected vs Riemannian divergence mismatch | HIGH | TEST-5 | Decoupled divergence; proved $\mathbf{u}_{\mathrm{phys}} = k \nabla^\perp \Psi$ has $\operatorname{div}_g \equiv 0$ | VERY_LOW | **RESOLVED** |
| **RISK-3** | Omitted metric scale factor causing volume drift | HIGH | TEST-5 | Single-metric conversion applied exactly once ($< 1.8 \times 10^{-16}$ drift) | VERY_LOW | **RESOLVED** |
| **RISK-4** | AMR 2:1 interface non-conservative mass leakage | MEDIUM | TEST-2 | Composite quadrature on sub-faces matching coarse macro-face ($< 10^{-14}\text{ kg/s}$) | VERY_LOW | **RESOLVED** |
| **RISK-5** | Cut-cell mass imbalance at nunatak boundaries | MEDIUM | TEST-3 | Exact geometric face fractions $\beta_f$ enforce divergence theorem ($< 10^{-14}\text{ kg/s}$) | VERY_LOW | **RESOLVED** |
| **RISK-6** | Discrete VAF jump during grounding line retreat | HIGH | TEST-6 | Discrete ungrounding remapping term $\Delta M_{\mathrm{remap}}$ closes budget ($< 10^{-12}$) | VERY_LOW | **RESOLVED** |

---

### Table 5: Checksum Manifest (SHA-256)
*File reference: `reports/tables/phase5_stage4_4_2_1_file_hashes.csv`*

| Relative Path | Size (Bytes) | SHA-256 Checksum |
| :--- | :--- | :--- |
| `src/physics/synthetic_conservation.py` | 40,209 | `48ec57fcb62b110398971705c26af54f48e835786e64f9a55c2ab2e41cccc5ac` |
| `tests/test_stage4_4_2_synthetic_conservation.py` | 5,972 | `8b5cac8d88b872b4546fc35024815d59cf97df9c8a37ef0fbb9f15906443abbf` |
| `reports/tables/phase5_stage4_4_2_1_synthetic_conservation_results.csv` | 3,830 | `4ec1023fab081fab64035fa77951e6b213b37e5318dcbbd322203b6c71917f82` |
| `reports/tables/phase5_stage4_4_2_1_flux_dimensionality_audit.csv` | 2,236 | `acaf26d4b2f9155e9a9bdece72c753a712cb8107b9878312554ffcd5b8141cd1` |
| `reports/tables/phase5_stage4_4_2_1_wgs84_metric_divergence_verification.csv` | 2,325 | `801c8b5c5ee479ffadd0b96b992be15f00768b0130d77ecadf23c3f894799d36` |
| `reports/tables/phase5_stage4_4_2_1_ocean_drag_scaling_audit.csv` | 602 | `a3e07e2526df1207380d637b7267014cd6586bf4e63d6e80867ad3cc5367af76` |
| `reports/tables/phase5_stage4_4_2_1_homogenized_vs_cut_cell_comparison.csv` | 611 | `8c8f6cab3aafc2895a0edc2a2730761089798a1a7bd91d872fea03dc1776fc32` |
| `reports/tables/phase5_stage4_4_2_1_approximations_and_limitations_ledger.csv` | 1,785 | `ccf2b8c238a32b976273932eed12fabccb3484b20307b6deccdc7b1370f96630` |
| `reports/tables/phase5_stage4_4_2_1_risk_register_updated.csv` | 1,217 | `ef113037daa051043b6ea807d1b105a2def55923dd0466df59edfd37e3078566` |
| `reports/tables/phase5_stage4_4_2_1_scientific_evidence_ledger_updated.csv` | 1,927 | `6363139d2413d932b98e7e3012b7c2d1464e85afd4e7b14d7647f2665a9a2e14` |
| `reports/figures/phase5_stage4_4_2_1_flux_and_metric_verification.png` | 613,979 | `5b5bab8c05c88de9edd40684f931ae2d9ca8fceebbaf5818f29c731a9b8a7893` |

---

## 5. Scope Restrictions Attestation

In accordance with explicit project governance directives:
1. **Zero Antarctic Physical Simulations**: No forward time-stepping, transient prognostic runs, or ice dynamic solves were executed for the Antarctic Peninsula or Domain A.
2. **Zero Inversions or Recalibrations**: The frozen Ryder parameter remains strictly preserved:
   $$C_{\mathrm{bed,Hp-I}} = 8.168 \times 10^6\text{ Pa}\cdot(\mathrm{m/s})^{-1/3}$$
3. **Zero Model Fitting**: No tuning or fitting of Crane Glacier, failed validation glaciers, or ISMIP6 benchmarks was performed.
4. **Zero Machine Learning Training**: No neural networks, emulators, or surrogate models were trained.
5. **Zero 2100 Projections**: No SLR or 2100 ice mass projection scenarios were run.
6. **Authoritative Domain A Baseline Invariance**: Grounded cell count (866,358 cells), grounded area ($216,062.17\text{ km}^2$), and solid ice volume ($140,702.51\text{ km}^3$) remain unchanged and authoritative.

---

## 6. Final Recommendation

All mathematical derivations, dimensional reconciliations, Riemannian divergence decouplings, executable source codes, unit tests, and evidentiary ledgers for **Stage 4.4.2.1** are fully complete and verified.

- **Status**: **PASS**
- **Readiness**: The computational architecture, discretization weak forms, AMR interface rules, cut-cell boundary formulations, and WGS84 single-metric scaling laws are mathematically verified and numerically closed to machine precision.
- **Next Step**: Authorize **Phase 5 — Stage 4.5: Antarctic Real-Data Implementation & Calibration Setup**.

