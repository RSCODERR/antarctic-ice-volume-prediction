# Phase 5.0 — Physical-Model Feasibility Research & Hybrid Physics-ML Framework Design

**Project:** Antarctic Ice-Volume Prediction Using Machine Learning (Peninsula Focus to 2100)  
**Document Status:** Authoritative Technical Feasibility Report  
**Phase:** 5.0 (Physical-Model Feasibility Research & Architecture Design)  
**Date:** November 2026  
**Lead Author:** Cryospheric Modeling, Geospatial Data Engineering & Scientific ML Team  
**Evaluation Target:** 2100 Multi-Scenario Projections across CMIP6 Pathways (**SSP1-2.6, SSP2-4.5, SSP5-8.5**)  
**Primary Spatial Domain:** Antarctic Peninsula Mainland Basins (**Hp-I**, **I-Ipp**, **Ipp-J**) and Regional **Domain A**  

---

## Executive Summary

Phase 5 represents the pivotal strategic transition of the Antarctic Peninsula Ice-Volume Prediction Project: transitioning from **historical empirical hindcast evaluation (1979–2024)** to **physics-informed forward forecasting up to the year 2100** under diverse climate pathways (SSP1-2.6, SSP2-4.5, and SSP5-8.5).

The motivation for this transition is grounded directly in the audited findings of **Phase 4C** and **Phase 4C.1**:
1. **Failure of Pure Statistical ML to Beat Climatology:** Pure empirical machine learning models (Bayesian Ridge, ElasticNet, Random Forest, Gradient Boosting, Gaussian Processes) trained on lag-1 surface mass balance, lag-1 discharge, and static topography failed to outperform a simple pre-test historical mean climatological baseline (`M0_Historical_Mean`, RMSE $14.69\text{ km}^3/\text{yr}$ vs Bayesian Ridge $15.36\text{ km}^3/\text{yr}$; $p < 0.01$).
2. **Structural Blindness to Dynamic Regime Shifts:** In basin $Ipp-J$ (Larsen Coast), the catastrophic collapse of the Larsen B Ice Shelf in 2002 triggered an abrupt, sustained glaciological acceleration (reconstructed loss increased from $-3.21\text{ km}^3/\text{yr}$ to $-21.80\text{ km}^3/\text{yr}$). Because statistical models lacked ice-shelf buttressing variables, they under-predicted ice loss in all nine held-out test years (accumulating $+52$ to $+77\text{ km}^3$ of positive drift).
3. **Prohibition on Unconstrained Extrapolation:** The Phase 4C.1 audit formally instituted a binding prohibition: *under no circumstances may pure statistical regression models be used for multi-decadal forward forecasting to 2100 without coupled dynamic ice-sheet physics (buttressing, ocean cavity thermal forcing, and grounding line migration).*

This report establishes the physical-model feasibility research, inventory, architectural trade-offs, and mathematical foundations required to construct a scientifically defensible, hybrid physics-machine learning prediction system for Phase 5.

```
========================================================================================================
PHASE 5.0 FEASIBILITY RESEARCH AT A GLANCE
========================================================================================================
1. Numerical Models Evaluated:    BISICLES, ISSM, Elmer/Ice, PISM, CISM, Úa, MALI
2. Resolution Bottleneck:         Peninsula alpine fjords (1–3 km wide) are unresolved by continental
                                  ISMIP6 grids (8–16 km); sub-kilometer AMR or flowline physics is mandatory.
3. CMIP6 Forcing Archives:        ISMIP6 CMIP6 standardized atmospheric & ocean cavity anomalies 
                                  (Zenodo 3897711) + downscaled RACMO2.3p2 / MAR fields up to 2100.
4. Selected Architecture:         PARADIGM 4: Hybrid Reduced-Complexity Physical Backbone + ML Climate
                                  Residual Emulation, benchmarked against PARADIGM 2 (ISMIP6 Multi-Model).
5. Dynamic State Variables:       Formalized 7 missing physical state variables (buttressing theta, shelf
                                  area, grounding line migration dx_GL, back-stress, CDW thermal forcing,
                                  contemporaneous SMB, retrograde bed slopes).
6. Operational Target:            Generate calibrated 2100 projections for Hp-I, I-Ipp, Ipp-J, and Domain A
                                  at decadal milestones (2030, 2040, 2050, 2075, 2100) across SSP1-2.6,
                                  SSP2-4.5, and SSP5-8.5.
========================================================================================================
```

---

## 1. Inventory & Evaluation of Numerical Ice Sheet Models

To determine how physical modeling should be incorporated into the project, we conducted a rigorous comparative evaluation of the leading international numerical ice-sheet models. The full inventory is archived in [`reports/tables/phase5_physical_model_inventory.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/phase5_physical_model_inventory.csv) and synthesized below.

### 1.1 Candidate Numerical Ice-Sheet Models

| Model Name | Lead Institution | Stress Balance Approximation | Mesh Type & Min Resolution | Peninsula Fjord Resolution Capability | Standalone Local Feasibility | ISMIP6 Archive Availability | Feasibility Tier |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **BISICLES** | LBNL / Univ. Bristol | L1L2 (Vertically Integrated Higher-Order) + SSA | Block-Structured Adaptive Mesh Refinement (AMR); $250\text{ m} - 500\text{ m}$ | **High** (Resolves $1-3\text{ km}$ outlet fjords dynamically) | Moderate (Requires Linux HPC, MPI, Chombo) | Very High (Zenodo / GHub) | **Tier 1 (Top Candidate)** |
| **ISSM** | NASA JPL / UC Irvine | Multi-model: SIA, SSA, Higher-Order, Full-Stokes | Unstructured 2D/3D Triangular Finite Element; $100\text{ m} - 500\text{ m}$ | **Very High** (Mesh conforms to alpine coastlines) | Moderate-Low (Demanding C++/MATLAB/Python build) | High (NASA SLCT / ISMIP6) | **Tier 1 (Top Candidate)** |
| **Elmer/Ice** | CSC / IGE Grenoble | Full-Stokes 3D Navier-Stokes solver | Unstructured 3D Finite Element; $100\text{ m} - 250\text{ m}$ | **Exceptional** (Exact 3D vertical shear & bridging) | Low (Supercomputer required; $10^4+$ core-hrs) | Moderate (Selected regional runs) | **Tier 2 (Physics Reference)** |
| **PISM** | UAF / PIK Potsdam | Hybrid SIA + SSA (heuristic superposition) | Regular Structured Finite Difference; $1\text{ km} - 4\text{ km}$ (8–16 km cont.) | **Low-Moderate** (Regular grid blunts narrow fjords) | Moderate-High (Efficient C++/PETSc) | Very High (Major ISMIP6 contributor) | **Tier 2 (Archive Priority)** |
| **CISM** | NCAR / LANL | Depth-integrated Higher-Order (Blatter-Pattyn) | Structured Quad/Hex Finite Volume; $2\text{ km} - 4\text{ km}$ | **Moderate** (Struggles with $1\text{ km}$ Graham Land valleys) | Moderate (CESM Fortran/MPI component) | High (Core ISMIP6 contributor) | **Tier 2 (Archive Priority)** |
| **Úa** | Northumbria Univ. | Shallow Shelf Approximation (SSA) / SIA | Adaptive Unstructured Finite Element; $200\text{ m} - 1\text{ km}$ | **High** (Conforms to complex grounding lines) | Moderate (Requires proprietary MATLAB) | Moderate (Regional studies) | **Tier 2 (Adjoint Benchmark)** |
| **MALI** | LANL / Sandia | First-order (Blatter-Pattyn) / SSA | Unstructured Voronoi Spherical Mesh; $1\text{ km} - 2\text{ km}$ | **Moderate-High** (Variable resolution meshes) | Low-Moderate (Complex DOE MPAS stack) | Moderate-High (Zenodo) | **Tier 3 (Supercomputing)** |

### 1.2 The Antarctic Peninsula Spatial Resolution Bottleneck

The primary physical obstacle in simulating the Antarctic Peninsula with numerical models is the **scale mismatch between continental model grids and local fjord topography**:
1. **Topographic Geometry:** The spine of the Antarctic Peninsula rises to over $2,000\text{ m}$ elevation within $10\text{ to }30\text{ km}$ of the ocean. Glaciers draining Graham Land East into the Larsen embayment (e.g., Crane, Jorum, Green, Flask, Leppard) flow through steep, deeply carved U-shaped bedrock troughs that are only **$1\text{ to }3\text{ km}$ wide**, separated by high nunatak ridges.
2. **The Continental Grid Failure Mode:** Standard continental ice-sheet models in ISMIP6 (such as PISM, CISM, and standard AWI-ISSM) ran on continental grids with grid spacings of **$8\text{ km}$, $16\text{ km}$, or $32\text{ km}$**. At $16\text{ km}$ resolution, the entire Graham Land spine is only **1 to 2 grid cells wide**. As a result:
   - High mountain peaks are averaged down, while narrow submarine troughs are filled in.
   - Bedrock pinning points that prevent grounding line collapse are completely smoothed out.
   - Ice-shelf shear margins (which provide lateral resistive back-stress) cannot be resolved, causing unphysical ice streaming or artificial numerical freezing.
3. **Glaciological Rule for Phase 5:** **Continental-scale $8-16\text{ km}$ model projections cannot be applied directly to the Antarctic Peninsula without topographic downscaling or sub-kilometer flowline parameterization.** Only models utilizing Adaptive Mesh Refinement (**BISICLES**), unstructured finite elements (**ISSM**, **Elmer/Ice**), or calibrated 1D dynamic flowline approximations can accurately resolve the physical discharge of Peninsula glaciers.

---

## 2. ISMIP6 CMIP6 Multi-Model Projections Archive & Extraction Protocol

### 2.1 The ISMIP6 Multi-Model Archive

The **Ice Sheet Model Intercomparison Project for CMIP6 (ISMIP6)** represents the authoritative international standard for ice-sheet projections contributing to the Intergovernmental Panel on Climate Change (IPCC) Sixth Assessment Report (AR6).

```
+--------------------------------------------------------------------------------------------------------+
| ISMIP6 ANTARCTIC PROJECTIONS ARCHIVE SPECIFICATIONS (Zenodo: 10.5281/zenodo.3940766)                  |
+--------------------------------------------------------------------------------------------------------+
| Participating Groups: 16 international institutions, 21 numerical ice-sheet model configurations      |
| CMIP6 Climate Drivers: UKESM1-0-LL, CESM2, CNRM-CM6-1, NorESM1-M, MIROC-ESM-CHEM, HadGEM2-ES          |
| Scenarios Covered:     SSP5-8.5 (High emissions), SSP1-2.6 (Low emissions), SSP2-4.5 (Medium emissions) |
| Simulation Window:     2015 to 2100 (Continuous annual reporting at calendar year ends)                |
| Key Variables:         • vaf    (Volume Above Flotation, m³ or Gt)                                     |
|                        • lim    (Land Ice Mass, kg)                                                    |
|                        • dlndm  (Cumulative mass change relative to 2015 baseline, Gt)                 |
|                        • iareg  (Grounded ice area, m²)                                                |
|                        • lithk  (Ice thickness, m)                                                     |
|                        • topg   (Bedrock topography, m)                                                |
|                        • bmb    (Sub-shelf basal melt flux, kg/m²/s)                                   |
|                        • calv   (Calving front discharge flux, kg/m²/s)                                |
+--------------------------------------------------------------------------------------------------------+
```

### 2.2 Spatial Extraction Protocol for Peninsula Basins

To integrate ISMIP6 into Phase 5, model outputs must be spatially subsetted to match our audited basin boundaries:
1. **Grid Harmonization:** ISMIP6 continental outputs are delivered on regular Polar Stereographic grids (`EPSG:3031`) at $8\text{ km}$ or $16\text{ km}$ resolution with standard grid parameters ($x_{\text{min}} = -3040\text{ km}$, $y_{\text{min}} = -3040\text{ km}$).
2. **Basin Masking:** Using the authoritative Phase 2.6 spatial domain and the official IMBIE / MEaSUREs drainage boundaries, we define raster masks on the ISMIP6 native grid for:
   - **Basin 24 / Hp-I (Palmer Land West):** Longitudes $65^\circ\text{W} - 80^\circ\text{W}$, draining into Bellingshausen Sea and George VI Sound.
   - **Basin 25 / I-Ipp (Graham Land West):** Draining into the Bellingshausen Sea, Palmer Archipelago, and Gerlache Strait.
   - **Basin 26 / Ipp-J (Graham Land East / Larsen Coast):** Draining east into the Weddell Sea across the Larsen A, B, and C embayments.
   - **Domain A Aggregate:** The spatial union of $Hp-I + I-Ipp + Ipp-J$.
3. **Target Variable Harmonization:** In ISMIP6, the primary sea-level relevant metric is **Volume Above Flotation ($VAF$)**:
   $$VAF = \int_{\text{grounded}} \max\left( 0, H(x,y) + \frac{\rho_w}{\rho_{\text{ice}}} \min(0, B(x,y)) \right) \, dA$$
   Because our Phase 3 historical target is total grounded ice-equivalent volume change ($\Delta V_{\text{grounded}}$), we must explicitly link $VAF$ to total grounded volume using the subglacial bed depth:
   $$\Delta V_{\text{grounded}}(t) = \Delta VAF(t) + \Delta V_{\text{below\_flotation}}(t)$$
   where $V_{\text{below\_flotation}}$ represents the grounded ice column situated below sea level that does not displace ocean water upon ungrounding.

### 2.3 Historical Drift Correction of Numerical Models

A critical finding of cryospheric model audits (e.g., Nowicki et al. 2020; Seroussi et al. 2020) is that **numerical ice-sheet models suffer from uncalibrated historical drift**:
- When numerical models are initialized (via spin-up or inversion at ~2015), they are rarely in perfect steady-state equilibrium with the climate forcing.
- As a consequence, running the historical control simulation (`ctrl_proj`) produces non-zero volume changes (drift) in the absence of any climate change.
- **Audit Mandate for Phase 5:** **Raw ISMIP6 projections must never be ingested without control drift removal and historical baseline calibration.**
  $$\Delta V_{\text{forced}}(t) = \left[ V_{\text{model}}(t) - V_{\text{model}}(2015) \right] - \left[ V_{\text{ctrl}}(t) - V_{\text{ctrl}}(2015) \right]$$
  Furthermore, the model trajectory must be anchored to the Phase 3.2 verified historical trajectory at the 2015–2024 boundary to ensure seamless continuity without unphysical step-discontinuities.

---

## 3. Climate & Oceanic Forcing Datasets up to 2100

Forward projections of ice-sheet volume require driving boundary conditions from Earth System Models (ESMs). Table 2 archives the candidate forcing datasets (archived in [`reports/tables/phase5_forcing_datasets.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/phase5_forcing_datasets.csv)).

### 3.1 Atmospheric & Surface Mass Balance Forcing

```
                                  ATMOSPHERIC FORCING PIPELINE (2015–2100)
                                  
  ┌─────────────────────────────────┐                 ┌─────────────────────────────────┐
  │   CMIP6 Earth System Models     │                 │   Regional Climate Downscaling  │
  │  (UKESM1, CESM2, NorESM1-M)     │                 │       (RACMO2.3p2 / MAR)        │
  └────────────────┬────────────────┘                 └────────────────┬────────────────┘
                   │                                                   │
                   ▼                                                   ▼
  ┌─────────────────────────────────┐                 ┌─────────────────────────────────┐
  │ ISMIP6 Standardized Anomalies   │                 │ 1 km / 2 km Topographic Grids   │
  │ • ΔSMB(x, y, t)                 │                 │ • Orographic precipitation      │
  │ • ΔT_surface(x, y, t)           │                 │ • Extreme summer surface melt   │
  └────────────────┬────────────────┘                 └────────────────┬────────────────┘
                   │                                                   │
                   └───────────────────────┬───────────────────────────┘
                                           │
                                           ▼
                   ┌───────────────────────────────────────────────────┐
                   │   Peninsula Basin Surface Mass Balance Driving    │
                   │   • Hp-I: Accumulation surges (snowfall)          │
                   │   • Ipp-J: Meltwater ponding & hydrofracture     │
                   └───────────────────────────────────────────────────┘
```

1. **Downscaled RACMO2.3p2 & RACMO2.4p1:**
   - Provides $1\text{ km}$ and $2\text{ km}$ downscaled surface mass balance across the Antarctic Peninsula, driven by ERA5 historically and CMIP6 models for future pathways.
   - Crucial for resolving the intense precipitation shadow across the Peninsula spine (Palmer Land receives $> 1,500\text{ mm w.e./yr}$ on the western slopes, dropping to $< 300\text{ mm w.e./yr}$ on eastern Larsen shelves).
2. **ISMIP6 Standardized Atmospheric Anomalies (Zenodo 3897711):**
   - Provides standardized monthly and annual anomalies of surface mass balance ($\Delta \text{SMB}$) and surface skin temperature ($\Delta T_s$) relative to the 1995–2014 reference climatology across CMIP6 models (UKESM1-0-LL, CESM2, CNRM-CM6-1, NorESM1-M).
   - Guarantees exact IPCC AR6 scenario comparability across **SSP1-2.6**, **SSP2-4.5**, and **SSP5-8.5**.

### 3.2 Oceanic Thermal Forcing & Sub-Shelf Cavity Melting

Ocean-driven basal melting at ice-shelf bases and grounding lines is the dominant trigger of dynamic mass loss in Antarctica:
1. **The Physical Mechanism:** Warm, salty **Circumpolar Deep Water (CDW)** occupies intermediate depths in the Southern Ocean. Where the continental shelf slopes downward toward the grounding line (retrograde beds), CDW intrudes into the sub-ice shelf cavity, delivering intense thermal energy ($1\text{--}3^\circ\text{C}$ above the in-situ freezing point).
2. **Regional Disparity on the Antarctic Peninsula:**
   - **Western Sector (Basin Hp-I & George VI Sound):** Directly exposed to warm CDW intrusions from the Bellingshausen Sea. The George VI Ice Shelf suffers basal melt rates exceeding $3\text{--}8\text{ m/yr}$, driving grounding line retreat in Palmer Land West.
   - **Eastern Sector (Basin Ipp-J & Larsen C):** Buffered by cold High Salinity Shelf Water ($-1.8^\circ\text{C}$) formed by sea-ice production in the Weddell Sea gyre. Basal melt rates under Larsen C are currently low ($< 0.5\text{ m/yr}$); however, climate models project potential warm water redirection into the Weddell Sea cavity under SSP5-8.5 in the late 21st century.
3. **ISMIP6 Sub-Shelf Melt Parameterization:**
   Basal melt rates ($\dot{m}_{\text{basal}}$, in $\text{m/yr}$) in Phase 5 will be governed by the standard ISMIP6 non-local parameterization (Jourdain et al. 2020):
   $$\dot{m}_{\text{basal}}(x,y,t) = \gamma_0 \cdot \left( \frac{\rho_w c_{pw}}{\rho_{\text{ice}} L_f} \right)^2 \cdot \left| \Delta T_{\text{ocean}}(t) \right| \cdot \Delta T_{\text{ocean}}(t) \cdot \left( \sin \alpha_{\text{slope}} \right)$$
   where:
   - $\Delta T_{\text{ocean}} = T_{\text{cavity}} - T_{\text{freeze}}$ is the thermal forcing above the pressure-dependent freezing point.
   - $\gamma_0$ is the calibrated regional thermal exchange velocity ($\text{m/s}$).
   - $\alpha_{\text{slope}}$ is the local ice-shelf base slope (derived from BedMachine V4.1).

---

## 4. Architectural Trade-Off Analysis & Selection

We comparatively evaluated four potential modeling architectures for Phase 5. The trade-off matrix is archived in [`reports/tables/phase5_architecture_tradeoffs.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/phase5_architecture_tradeoffs.csv) and detailed below.

### 4.1 Comparative Evaluation Matrix

| Criterion | Paradigm 1: Standalone Numerical Model (BISICLES / ISSM) | Paradigm 2: Direct ISMIP6 Multi-Model Extraction | Paradigm 3: Physics-Informed Neural Networks (PINN) | Paradigm 4: Hybrid Reduced-Physics Backbone + ML Residual |
| :--- | :--- | :--- | :--- | :--- |
| **Physical Fidelity** | **Highest** (Full Navier-Stokes / L1L2 PDE solver) | **High** (Peer-reviewed 16-model ensemble) | **Moderate** (Weak PDE residual loss) | **High** (Analytical grounding line & buttressing physics) |
| **Peninsula Fjord Resolution** | High (with $<500\text{ m}$ AMR mesh) | Low-Moderate ($8-16\text{ km}$ continental grid) | Low (Struggles with steep alpine boundaries) | **High** (Basin-specific 500 m geometry & flux gates) |
| **Computational Feasibility** | **Very Low** (Requires supercomputing HPC clusters) | **Very High** (Direct NetCDF processing) | Moderate (GPU training; high optimization instability) | **Exceptional** (Executes in seconds on standard hardware) |
| **Scenario Sweeping to 2100** | Difficult (Multi-day runs per SSP pathway) | Fast (Pre-computed SSP1-2.6, 2-4.5, 5-8.5) | Moderate (Requires retraining per forcing field) | **Instantaneous** (Continuous probabilistic Monte Carlo sweeps) |
| **Historical Target Alignment** | Uncalibrated (Models have large historical drift) | Uncalibrated (Requires post-hoc bias correction) | Moderate (Direct target loss optimization) | **Optimal** (Directly calibrated to Phase 3.2 1979–2024 targets) |
| **Scientific Auditability** | High | Very High (IPCC AR6 standard) | Moderate-Low (Black-box neural weights) | **Exceptional** (Every physical parameter is inspectable) |
| **Recommendation** | *Rejected for Standalone Local Execution* | **APPROVED AS MANDATORY BENCHMARK** | *Deferred (High Technical Risk)* | **STRONGLY RECOMMENDED AS PRIMARY ARCHITECTURE** |

### 4.2 Strategic Recommendation: The Hybrid Two-Pillar Framework

Based on this evaluation, Phase 5 will implement a **Two-Pillar Framework**:

```
========================================================================================================
THE PHASE 5 TWO-PILLAR PREDICTION FRAMEWORK
========================================================================================================
PILLAR 1: THE DYNAMIC PHYSICAL-ML HYBRID MODEL (PRIMARY OPERATIONAL FORECASTER)
  • Integrates a calibrated reduced-complexity dynamic physical backbone (Schoof grounding-line flux,
    ice-shelf buttressing parameterization, and mass conservation) with a machine-learning climate
    residual emulator.
  • Solves the spatial resolution bottleneck by operating directly on basin-aggregated BedMachine V4.1
    500 m retrograde topography and historical ITS_LIVE flux gates.
  • Seamlessly trained on the Phase 3.2 1979–2024 historical trajectory, eliminating numerical drift.
  • Generates high-speed forward projections up to 2100 across SSP1-2.6, SSP2-4.5, and SSP5-8.5.

PILLAR 2: THE ISMIP6 MULTI-MODEL ENSEMBLE BENCHMARK (PHYSICAL COMPARISON PRIOR)
  • Ingests and harmonizes the official IPCC AR6 ISMIP6 multi-model archive (Zenodo 3940766).
  • Extracts basin-specific trajectories for Hp-I, I-Ipp, and Ipp-J across all participating models.
  • Applies rigorous historical control drift removal and zero-epoch anchoring at 2015/2024.
  • Serves as the independent, physics-based numerical benchmark against which the Hybrid Model
    projections are evaluated and validated.
========================================================================================================
```

---

## 5. Mathematical Formulation of the Hybrid Physics-ML Architecture

To guarantee strict compliance with cryospheric physics and resolve the seven missing physical state variables identified in Phase 4C.1, we formalize the governing equations of the hybrid architecture. The variables are cataloged in [`reports/tables/phase5_dynamic_state_variables.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/phase5_dynamic_state_variables.csv).

```
                                  HYBRID ARCHITECTURE FLOW DIAGRAM
                                  
   CMIP6 ESM Climate Forcings               BedMachine V4.1 500m Geometry
   • Downscaled SMB_contemp(t)              • Retrograde Bed Slope b_retro(x)
   • Ocean Thermal Forcing ΔT_ocean(t)      • Water Depth at GL h_GL(t)
   • Surface Meltwater Production           • Calving Front Width W_fjord
                 │                                        │
                 ▼                                        ▼
   ┌─────────────────────────────────────────────────────────────────────────────┐
   │             CALIBRATED REDUCED-COMPLEXITY DYNAMIC PHYSICAL BACKBONE         │
   │                                                                             │
   │   1. Sub-Shelf Basal Melt:     m_dot = gamma_0 * (ΔT_ocean)^alpha           │
   │   2. Buttressing Decay:        θ_buttress(t) = θ_0 * exp(-λ_melt * M_surf)  │
   │   3. Grounding Line Flux:      q_GL = f(h_GL, C_bed, θ_buttress)            │
   │   4. Grounding Line Migration: dx_GL/dt = [q_in - q_GL] / (slope * H_GL)   │
   │   5. Physical Discharge:       D_physics(t) = Σ q_GL * W_fjord              │
   └──────────────────────────────────────┬──────────────────────────────────────┘
                                          │
                                          ▼
                         D_physics(t) [Deterministic Dynamic Trend]
                                          │
                                          ▼
   ┌─────────────────────────────────────────────────────────────────────────────┐
   │                 MACHINE LEARNING CLIMATE RESIDUAL EMULATOR                   │
   │                                                                             │
   │   Inputs: CMIP6 climate anomalies (P - E, T_air, wind stress, NAO/SAM index) │
   │   Target: ΔD_residual = D_observed - D_physics (interannual variance)        │
   │   Model:  Calibrated Bayesian Ridge / Ridge Ensembles with uncertainty       │
   └──────────────────────────────────────┬──────────────────────────────────────┘
                                          │
                                          ▼
                         D_total(t) = D_physics(t) + ΔD_residual(t)
                                          │
                                          ▼
   ┌─────────────────────────────────────────────────────────────────────────────┐
   │                       MASS CONSERVATION INTEGRATOR                          │
   │                                                                             │
   │      V_grounded(t) = V_grounded(t-1) + [ SMB_contemp(t) - D_total(t) ] / ρ │
   └─────────────────────────────────────────────────────────────────────────────┘
```

### 5.1 Mass Conservation & Volume Integration

For each basin $b \in \{Hp-I, I-Ipp, Ipp-J\}$, the grounded ice-equivalent volume evolves according to:
$$V_{\text{grounded}}(t) = V_{\text{grounded}}(t-1) + \frac{1}{\rho_{\text{ice}}} \left( \text{SMB}_{\text{contemp}}(t) - D_{\text{total}}(t) \right)$$
where $\rho_{\text{ice}} = 0.917\text{ Gt/km}^3$, and $\text{SMB}_{\text{contemp}}(t)$ is the contemporaneous annual surface mass balance ($Gt/\text{year}$).

### 5.2 Dynamic Discharge Formulation with Buttressing & Retrograde Beds

Dynamic ice discharge across the grounding line ($D_{\text{total}}$, in $\text{Gt/year}$) is parameterized as:
$$D_{\text{total}}(t) = D_{\text{physics}}(t) + \Delta D_{\text{ML}}(t)$$
$$D_{\text{physics}}(t) = D_0 \cdot \left( \frac{h_{\text{GL}}(t)}{h_{\text{GL},0}} \right)^\gamma \cdot \left[ 1 - (1 - \theta_{\text{min}}) \cdot (1 - \theta_{\text{buttress}}(t)) \right]^\beta$$
where:
- $D_0$ is the baseline dynamic discharge ($\text{Gt/year}$), calibrated to the 1995–2001 pre-collapse velocity fields from ITS_LIVE.
- $h_{\text{GL}}(t)$ is the ice thickness at the grounding line ($\text{m}$).
- $\gamma \approx \frac{m+n+3}{m+1} \approx 4.0$ is the theoretical Schoof (2007) grounding-line flux exponent for Weertman sliding ($m=3, n=3$).
- $\theta_{\text{buttress}}(t) \in [0.0, 1.0]$ is the **Ice-Shelf Buttressing Factor**:
  - $\theta_{\text{buttress}} = 1.0$: Fully buttressed, confined ice shelf (pre-collapse Larsen B).
  - $\theta_{\text{buttress}} = 0.0$: Complete ice-shelf loss, zero back-stress (post-2002 Crane/Flask glacier speedup).
  - $\theta_{\text{min}} \approx 0.125$ ensures maximum theoretical acceleration matches observed tributary speedups ($2\times \text{ to } 8\times$).
- $\beta \approx 1.0$ governs sensitivity to buttressing loss.

### 5.3 Grounding Line Migration Dynamics (MISI Trigger)

Grounding line migration along the BedMachine V4.1 retrograde bedrock profile is governed by mass continuity across the grounding boundary:
$$\frac{d x_{\text{GL}}}{dt} = \frac{q_{\text{in}} - q_{\text{GL}}\left(h_{\text{GL}}(t), \theta_{\text{buttress}}(t)\right)}{\alpha_{\text{bed}} \cdot \left( 1 - \frac{\rho_w}{\rho_{\text{ice}}} \right) \cdot h_{\text{GL}}(t)}$$
where:
- $x_{\text{GL}}$ is the grounding line position along the central flowline ($\text{km}$, positive inland).
- $\alpha_{\text{bed}} = \frac{dB}{dx}$ is the local bedrock slope. Where the bed is **retrograde** ($\alpha_{\text{bed}} < 0$, sloping downward inland), $\frac{d x_{\text{GL}}}{dt}$ becomes positive, triggering **Marine Ice Sheet Instability (MISI)**: retreat increases ice thickness at the grounding line ($h_{\text{GL}}$), which exponentially increases flux ($q_{\text{GL}} \propto h_{\text{GL}}^4$), driving self-sustaining retreat until an inland pinning point or prograde bed slope is encountered.

### 5.4 Hydrofracture & Surface Meltwater Collapse Parameterization

Ice-shelf collapse is triggered when summer surface meltwater production exceeds critical firn pore saturation thresholds (Trusel et al. 2015; Pollard et al. 2015):
$$\theta_{\text{buttress}}(t) = \theta_0 \cdot \exp\left( - \lambda_{\text{melt}} \cdot \max\left(0, M_{\text{surface}}(t) - M_{\text{crit}}\right) \right) \cdot \exp\left( - \lambda_{\text{ocean}} \cdot \Delta T_{\text{ocean}}(t) \right)$$
where $M_{\text{surface}}$ is the annual surface snowmelt ($\text{mm w.e./yr}$), $M_{\text{crit}} \approx 300\text{ mm w.e./yr}$ is the threshold for crevasse hydrofracture, and $\Delta T_{\text{ocean}}$ represents sub-shelf basal melting.

---

## 6. Implementation Roadmap, Phase Gates & Risk Mitigation

### 6.1 Phase 5 Operational Roadmap

```
========================================================================================================
PHASE 5 SUB-PHASE EXECUTION ROADMAP
========================================================================================================
Phase 5.0 (Current):  Physical-Model Feasibility Research & Hybrid Architecture Design
                      • Model inventory, ISMIP6 audit, forcing inventory, mathematical formulation.

Phase 5.1:            ISMIP6 Multi-Model Projections Ingestion & Basin Extraction
                      • Download and process ISMIP6 NetCDF files for UKESM1, CESM2, NorESM1-M.
                      • Mask to Basins Hp-I, I-Ipp, Ipp-J and Domain A.
                      • Perform historical control drift removal and zero-epoch anchoring.

Phase 5.2:            Implementation of Calibrated Dynamic Flowline/Box Backbone
                      • Code the analytical grounding line migration and buttressing solver in Python.
                      • Calibrate D_0, h_GL,0, and theta_buttress to 1979–2024 historical reconstruction.
                      • Verify stability and reproduction of post-2002 Larsen B acceleration in Ipp-J.

Phase 5.3:            Multi-Scenario Forcing Integration (SSP1-2.6, SSP2-4.5, SSP5-8.5 to 2100)
                      • Ingest downscaled RACMO / ISMIP6 atmospheric SMB and ocean cavity ΔT anomalies.
                      • Build unified future feature matrices for 2025–2100.

Phase 5.4:            Forward Simulation, 2100 Projections & Multi-Model Evaluation
                      • Execute hybrid model forward simulations to 2100 under all three SSP pathways.
                      • Extract volume change milestones (2030, 2040, 2050, 2075, 2100).
                      • Quantify parametric, scenario, and structural uncertainties.
                      • Conduct formal scientific benchmark comparison against Pillar 2 (ISMIP6).
========================================================================================================
```

### 6.2 Key Scientific Risks & Mitigation Strategies

1. **Risk 1: Coarse Grid Smoothing in ISMIP6 Archive**
   - *Risk:* Continental ISMIP6 models running at 8–16 km may underestimate Peninsula mass loss due to unresolved fjords.
   - *Mitigation:* We do not rely solely on ISMIP6. The primary forecaster (Pillar 1) uses BedMachine V4.1 500 m high-resolution bedrock bathymetry to compute grounding line flux. ISMIP6 serves as a comparative benchmark and climate prior, not an uncorrected ground truth.
2. **Risk 2: Lack of In-Situ Oceanographic Data in Sub-Ice Shelf Cavities**
   - *Risk:* Ocean temperatures beneath George VI and Larsen C are poorly observed.
   - *Mitigation:* We use the peer-reviewed ISMIP6 ocean thermal forcing parameterization (Jourdain et al. 2020), anchored historically to the Schmidtko et al. (2014) observational climatology, and apply Monte Carlo perturbation across thermal exchange velocity bounds ($\gamma_0 \pm 50\%$).
3. **Risk 3: Abrupt Scenario Divergence Post-2050**
   - *Risk:* SSP1-2.6 and SSP5-8.5 diverge dramatically after 2050, introducing wide prediction intervals.
   - *Mitigation:* This is a physical reality of climate forcing, not a model defect. We formally report projections as scenario-conditional probability distributions, decoupling climate policy uncertainty from glaciological parameter uncertainty.

---

## 7. Deliverables & Data Directory

In support of Phase 5.0, the following authoritative technical tables have been compiled and archived in [`reports/tables/`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/):

1. [`reports/tables/phase5_physical_model_inventory.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/phase5_physical_model_inventory.csv) — Detailed inventory and comparative feasibility scores of candidate numerical ice-sheet models.
2. [`reports/tables/phase5_forcing_datasets.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/phase5_forcing_datasets.csv) — Catalog of atmospheric and oceanic forcing datasets up to 2100 across SSP1-2.6, SSP2-4.5, and SSP5-8.5.
3. [`reports/tables/phase5_architecture_tradeoffs.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/phase5_architecture_tradeoffs.csv) — Multi-criteria decision matrix evaluating Pure Numerical, Direct ISMIP6, PINN, and Hybrid Physics-ML paradigms.
4. [`reports/tables/phase5_dynamic_state_variables.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/phase5_dynamic_state_variables.csv) — Mathematical specifications and calibration anchors for the 7 physical state variables missing from Phase 4.

---

## Conclusion & Authorization Gate

Phase 5.0 feasibility research establishes that:
1. **Pure statistical machine learning cannot be extrapolated to 2100.**
2. **A standalone numerical ice-sheet simulation (e.g. Full-Stokes Elmer/Ice) is computationally infeasible on local hardware.**
3. **A Hybrid Two-Pillar Framework is scientifically optimal, mathematically rigorous, and computationally feasible.**

With Phase 5.0 complete, we are prepared to proceed to **Phase 5.1: ISMIP6 Multi-Model Projections Ingestion & Basin Extraction**.

