# Stage 5.0 — Transient Historical Simulation Architecture Document

## 1. Architectural Overview & Design Philosophy

The Stage 5.0 Transient Historical Simulation Framework provides the computational, physical, and mathematical infrastructure required to evolve the Antarctic Peninsula ice sheet through time. Building directly upon the frozen Stage 4.8 regionally calibrated 2D Shallow Shelf Approximation (SSA) model, this architecture transitions the solver from a diagnostic snapshot tool into an explicit, finite-volume time-stepping simulation system.

### Core Governance Principles:
1. **Conservation Invariance:** Discrete mass conservation is preserved unconditionally. Internal transfers between grounded ice and floating ice shelves cancel to machine precision ($< 10^{{-12}}\ \\mathrm{{Gt}}$).
2. **Moving Boundary Continuity:** Grounding-line migration is governed by the physical flotation criterion. Transitions between grounded and floating states are tracked cell-by-cell with exact ledger balance.
3. **Strict Physical Realism:** Zero artificial forcing is applied. The simulation initializes from the authentic non-equilibrium state of the modern Antarctic Peninsula, preserving observed dynamic mass deficits without manufacturing a steady state.
4. **Historical Provenance:** Time-dependent atmospheric forcing is sourced directly from unadulterated RACMO2.3p2 annual fields; model trajectories are evaluated against independent satellite reconcilement data (IMBIE-3) without tuning.

---

## 2. Governing Equations & Numerical Formulations

### 2.1 The Two-Dimensional Ice Thickness Continuity Equation
The evolution of solid ice-equivalent thickness $H(x, y, t)$ across the model domain $\\Omega$ is governed by the two-dimensional mass continuity equation:

$$\\frac{{\\partial H}}{{\\partial t}} = -\\nabla \\cdot (H \\mathbf{{u}}) + \\dot{{a}}(x, y, t) - \\dot{{m}}_b(x, y, t)$$

where:
- $\\mathbf{{u}}(x, y, t) = (u, v)$ is the depth-averaged horizontal velocity vector ($\mathrm{{m/yr}}$).
- $\\dot{{a}}(x, y, t)$ is the surface mass balance expressed in solid ice-equivalent volume rate ($\\dot{{a}} = \\mathrm{{SMB}} / \\rho_i$, $\\mathrm{{m/yr}}$).
- $\\dot{{m}}_b(x, y, t)$ is the basal melt rate (declared unmodeled in static input package; set to zero on grounded bed).

### 2.2 Discrete Finite-Volume Formulation on WGS84 Curvilinear Grid
Integrating the continuity equation over a discrete grid cell $(i, j)$ with WGS84 ellipsoidal area $A_{{i,j}}$:

$$\\int_{{A_{{i,j}}}} \\frac{{\\partial H}}{{\\partial t}}\\, dA = -\\oint_{{\\partial A_{{i,j}}}} H (\\mathbf{{u}} \\cdot \\mathbf{{n}})\\, ds + \\int_{{A_{{i,j}}}} \\dot{{a}}\\, dA$$

In discrete algebraic form for time step $\\Delta t$:

$$H_{{i,j}}^{{n+1}} = H_{{i,j}}^n + \\Delta t \\left[ \\dot{{a}}_{{i,j}}^n - \\frac{{1}}{{A_{{i,j}}}} \\sum_{{k \\in \\mathrm{{faces}}}} F_k^n \\right]$$

where face flux $F_k^n$ across cell interface $k$ is evaluated using first-order upwind thickness:

$$F_k^n = H_k^* (\\mathbf{{u}}_k^n \\cdot \\mathbf{{n}}_k) ds_k$$

with Snyder metric scale factor:

$$ds_x = \\frac{{\\Delta y}}{{k_{{\\mathrm{{scale}}}}}}, \\quad ds_y = \\frac{{\\Delta x}}{{k_{{\\mathrm{{scale}}}}}}, \\quad k_{{\\mathrm{{scale}}}} = \\sqrt{{\\frac{{\\Delta x \\Delta y}}{{A_{{\\mathrm{{WGS84}}}}}}}}$$

The first-order upwind thickness $H_k^*$ selects the upstream donor cell:

$$H_k^* = \\begin{{cases}} H_{{\\mathrm{{upstream}}}}, & \\text{{if }} \\mathbf{{u}}_k \\cdot \\mathbf{{n}}_k > 0 \\\\ H_{{\\mathrm{{downstream}}}}, & \\text{{if }} \\mathbf{{u}}_k \\cdot \\mathbf{{n}}_k \\le 0 \\end{{cases}}$$

This scheme is unconditionally monotone, prevents spurious numerical oscillations, and guarantees positive thickness preservation.

---

## 3. Moving Grounding Line & Flotation Mechanism

### 3.1 Flotation Condition & Height Above Flotation
For bedrock elevation $b(x, y)$ and seawater density $\\rho_w = 1028\\ \\mathrm{{kg/m}}^3$, the flotation thickness $H_{{\\mathrm{{flot}}}}$ represents the ice thickness required for hydrostatic flotation:

$$H_{{\\mathrm{{flot}}}}(x, y) = \\begin{{cases}} -b(x, y) \\frac{{\\rho_w}}{{\\rho_i}}, & \\text{{if }} b < 0 \\\\ 0, & \\text{{if }} b \\ge 0 \\end{{cases}}$$

The height above flotation $h_f(x, y, t)$ is defined as:

$$h_f(x, y, t) = H(x, y, t) - H_{{\\mathrm{{flot}}}}(x, y)$$

### 3.2 Cell State Classification & Migration Tracking
At each time step $n+1$:
1. **Grounded Cell:** A cell is grounded if $h_f^{{n+1}} > 0$ and $H^{{n+1}} > 10\\ \\mathrm{{m}}$.
   - $\\alpha_g = 1, \\alpha_f = 0$
   - Basal sliding active: $\\boldsymbol{{\\tau}}_b = -C_{{\\mathrm{{bed}}}} |\\mathbf{{u}}|^{{m-1}} \\mathbf{{u}}$
   - Surface elevation: $s = b + H$
2. **Floating Shelf Cell:** A cell floats in hydrostatic equilibrium if $h_f^{{n+1}} \\le 0$, $b < 0$, and $H^{{n+1}} > 10\\ \\mathrm{{m}}$.
   - $\\alpha_g = 0, \\alpha_f = 1$
   - Basal drag vanishes: $\\boldsymbol{{\\tau}}_b = \\mathbf{{0}}$ ($C_{{\\mathrm{{ocean}}}} = 0$)
   - Surface elevation: $s = (1 - \\rho_i / \\rho_w) H$

### 3.3 Dynamic Migration & Mass Ledger Neutrality
- **Ungrounding Transition (Retreat):** When a grounded cell thins such that $h_f$ transitions from positive to non-positive, the cell un-grounds. Its solid ice mass $M_{{\\mathrm{{cell}}}} = \\rho_i H_{{i,j}}^{{n+1}} A_{{i,j}}$ is transferred from the grounded mass ledger to the floating shelf ledger:
  $$M_g \\leftarrow M_g - M_{{\\mathrm{{cell}}}}, \\quad M_f \\leftarrow M_f + M_{{\\mathrm{{cell}}}}$$
- **Regrounding Transition (Advance):** When a floating shelf cell thickens such that $h_f > 0$, the cell touches the sea floor and grounds. Its mass is transferred from floating shelf to grounded ledger:
  $$M_g \\leftarrow M_g + M_{{\\mathrm{{cell}}}}, \\quad M_f \\leftarrow M_f - M_{{\\mathrm{{cell}}}}$$

In both cases:
$$\\Delta M_{{\\mathrm{{migration}}}} = -M_{{\\mathrm{{cell}}}} + M_{{\\mathrm{{cell}}}} \\equiv 0.00000000\\ \\mathrm{{Gt}}$$
Mass is conserved identically without numerical creation or destruction.

---

## 4. Discrete Mass Conservation Ledger & Internal Cancellation

The discrete finite volume scheme satisfies exact discrete Gauss divergence on the mutually exclusive grounded and floating subdomains:

$$\\sum_{{i,j \\in \\mathcal{{G}}}} \\operatorname{{div}}(F)_{{i,j}} = F_{{\\mathrm{{gl}}}} + F_{{\\mathrm{{calv,g}}}}$$

$$\\sum_{{i,j \\in \\mathcal{{F}}}} \\operatorname{{div}}(F)_{{i,j}} = F_{{\\mathrm{{calv,f}}}} - F_{{\\mathrm{{gl}}}}$$

Adding the two equations:

$$\\sum_{{i,j \\in \\mathcal{{G}} \\cup \\mathcal{{F}}}} \\operatorname{{div}}(F)_{{i,j}} = (F_{{\\mathrm{{gl}}}} + F_{{\\mathrm{{calv,g}}}}) + (F_{{\\mathrm{{calv,f}}}} - F_{{\\mathrm{{gl}}}}) \\equiv F_{{\\mathrm{{calv,g}}}} + F_{{\\mathrm{{calv,f}}}} \\equiv F_{{\\mathrm{{calv,total}}}}$$

The internal grounding-line flux $F_{{\\mathrm{{gl}}}}$ cancels with zero error:
$$+F_{{\\mathrm{{gl}}}} - F_{{\\mathrm{{gl}}}} \\equiv 0.00000000\\ \\mathrm{{Gt}}$$

The total system mass balance equation at every time step is:
$$\\Delta M_{{\\mathrm{{total}}}} = \\Delta M_g + \\Delta M_f = \\left[ \\mathrm{{SMB}}_{{\\mathrm{{total}}}} - F_{{\\mathrm{{calv,total}}}} - \\dot{{M}}_{{\\mathrm{{melt}}}} \\right] \\Delta t$$

The numerical residual $\\epsilon_{{\\mathrm{{mass}}}}$ is bounded strictly by machine floating-point precision:
$$\\epsilon_{{\\mathrm{{mass}}}} = |\\Delta M_{{\\mathrm{{total}}}} - \\Delta M_{{\\mathrm{{pred}}}}| < 10^{{-11}}\\ \\mathrm{{Gt}}$$

---

## 5. Numerical Stability & Courant-Friedrichs-Lewy (CFL) Analysis

The explicit time step $\\Delta t$ for ice thickness advection is restricted by the multi-dimensional Courant-Friedrichs-Lewy (CFL) condition:

$$\\mathrm{{CFL}} = \\Delta t \\left( \\frac{{|u|}}{{\\Delta x}} + \\frac{{|v|}}{{\\Delta y}} \\right) \\le 1.0$$

On a $1,000\\ \\mathrm{{m}}$ grid:
- In fast glacial outlet streams ($|\\mathbf{{u}}| \\approx 500\\ \\mathrm{{m/yr}}$), the physical CFL limit is $\\Delta t_{{\\mathrm{{cfl}}}} = 1000 / 500 = 2.0\\ \\mathrm{{years}}$.
- On steep alpine nunatak cliffs (the 340 gated cliff headwalls), un-damped 2D SSA velocities can reach several thousand meters per year. Per the mitigation established in FAIL-01, local cliff velocities are capped at $u_{{\\mathrm{{max}}}} = 5,000\\ \\mathrm{{m/yr}}$ during time-stepping.
- For operational time step $\\Delta t = 0.10\\ \\mathrm{{year}}$ (36.5 days):
  $$\\mathrm{{CFL}}_{{\\mathrm{{max}}}} = \\frac{{5,000 \\times 0.10}}{{1,000}} = 0.50 < 1.0$$
The time-stepping scheme is unconditionally stable, monotone, and prevents negative physical thickness.
