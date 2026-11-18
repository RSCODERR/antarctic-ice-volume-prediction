# CryoPredict: Technical Methodology & Scientific Formulation Reference

**Platform:** CryoPredict — Antarctic Peninsula Ice-Volume Research & Inference Platform  
**Document Identifier:** `CRYO-REF-2026-METHOD`  
**Purpose:** Comprehensive Technical, Mathematical, and Operational Reference Manual  
**Date:** November 2026  
**Status:** Frozen Academic Reference (Stage 8.2 Release)  

---

## 1. Governing Physical and Mathematical Equations

### 1.1 Two-Dimensional Shallow Shelf Approximation (SSA)
The Shallow Shelf Approximation models horizontal plane-stress flow in ice shelves and fast-flowing outlet streams where vertical shear is neglected:

$$\begin{aligned}
\frac{\partial}{\partial x} \left[ 2 \mu H \left( 2 \frac{\partial u}{\partial x} + \frac{\partial v}{\partial y} \right) \right] + \frac{\partial}{\partial y} \left[ \mu H \left( \frac{\partial u}{\partial y} + \frac{\partial v}{\partial x} \right) \right] - \tau_{b,x} &= \rho_i g H \frac{\partial s}{\partial x} \\
\frac{\partial}{\partial y} \left[ 2 \mu H \left( 2 \frac{\partial v}{\partial y} + \frac{\partial u}{\partial x} \right) \right] + \frac{\partial}{\partial x} \left[ \mu H \left( \frac{\partial u}{\partial y} + \frac{\partial v}{\partial x} \right) \right] - \tau_{b,y} &= \rho_i g H \frac{\partial s}{\partial y}
\end{aligned}$$

### 1.2 Glen's Flow Law & Effective Viscosity
Vertically integrated effective viscosity $\mu$ is derived from Glen's non-linear constitutive relationship ($n=3$):

$$\mu = \frac{1}{2} A(T)^{-1/n} \dot{\varepsilon}_e^{(1-n)/n}$$

where effective strain rate $\dot{\varepsilon}_e$ is regularized by $\dot{\varepsilon}_0 = 10^{-5}\text{ yr}^{-1}$:

$$\dot{\varepsilon}_e^2 = \dot{\varepsilon}_{xx}^2 + \dot{\varepsilon}_{yy}^2 + \dot{\varepsilon}_{xx}\dot{\varepsilon}_{yy} + \dot{\varepsilon}_{xy}^2 + \dot{\varepsilon}_0^2$$

$$\dot{\varepsilon}_{xx} = \frac{\partial u}{\partial x}, \quad \dot{\varepsilon}_{yy} = \frac{\partial v}{\partial y}, \quad \dot{\varepsilon}_{xy} = \frac{1}{2} \left( \frac{\partial u}{\partial y} + \frac{\partial v}{\partial x} \right)$$

### 1.3 Basal Sliding Law
Non-linear Weertman-style power friction parameterized on grounded bedrock:

$$\boldsymbol{\tau}_b = -C(x, y) |\mathbf{u}|^{m-1} \mathbf{u}$$

- Grounded ice: $C(x, y) > 0$, $m = 1/3$ (or linear $m=1$ for diagnostic inversions).
- Floating ice shelf: $C_{\text{ocean}} = 0 \implies \boldsymbol{\tau}_b = \mathbf{0}$.

### 1.4 Hydrostatic Flotation & Moving Grounding Line
Flotation thickness $H_{\text{flot}}$ and height above flotation $h_f$:

$$H_{\text{flot}}(x, y) = \max\left( 0,\ -b(x, y) \frac{\rho_w}{\rho_i} \right) \quad (\text{for bedrock elevation } b(x,y) < 0)$$

$$h_f(x, y, t) = H(x, y, t) - H_{\text{flot}}(x, y)$$

- **Grounded state:** $h_f > 0 \implies s(x, y) = b(x, y) + H(x, y)$
- **Floating shelf state:** $h_f \le 0 \implies s(x, y) = \left(1 - \frac{\rho_i}{\rho_w}\right) H(x, y)$

### 1.5 Transient Ice Thickness Conservation
Two-dimensional depth-integrated continuity equation:

$$\frac{\partial H}{\partial t} = -\nabla \cdot (H \mathbf{u}) + \dot{a}(x, y, t) - \dot{m}_b(x, y, t)$$

In discrete finite-volume form with Snyder metric scale factor $k_{\text{scale}}$:

$$H_{i,j}^{n+1} = H_{i,j}^n + \Delta t \left[ \dot{a}_{i,j}^n - \frac{1}{A_{i,j}} \sum_{k \in \text{faces}} H_k^* (\mathbf{u}_k^n \cdot \mathbf{n}_k) ds_k \right]$$

### 1.6 Sea-Level Equivalent (SLE) Conversion
Conversion of drift-corrected Volume Above Flotation change ($\Delta\text{VAF}_{\text{clim}}$) into global mean sea-level contribution:

$$\text{SLE}_{\text{clim}}(t) = -\frac{\Delta\text{VAF}_{\text{clim}}(t) \times \rho_i}{A_{\text{ocean}} \times \rho_{\text{fw}}} = -\frac{\Delta\text{VAF}_{\text{clim}}(t) \times 0.917\text{ Gt/km}^3}{361.8\text{ Gt/mm}}$$

### 1.7 Asymmetric Pinball Loss (Quantile Regression)
Loss function for estimating the $\tau$-th quantile ($\tau \in (0, 1)$):

$$\mathcal{L}_\tau(y, \hat{y}) = \begin{cases} \tau (y - \hat{y}), & \text{if } y \ge \hat{y} \\ (1 - \tau) (\hat{y} - y), & \text{if } y < \hat{y} \end{cases} = \max\left( \tau(y - \hat{y}),\ (1 - \tau)(\hat{y} - y) \right)$$

### 1.8 Monotone Quantile Rearrangement Operator
The Chernozhukov, Fernández-Val, and Galichon (2010) non-crossing rearrangement:

$$q^*(u) = \text{sort}\left( \{ \hat{q}(\tau_k) \}_{k=1}^K \right)$$

Guarantees:
$$q_{10}^* \le q_{16}^* \le q_{50}^* \le q_{84}^* \le q_{90}^*$$

---

## 2. Fundamental Model Parameters & Physical Constants

| Constant / Parameter | Symbol | Value | Units | Provenance / Definition |
| :--- | :---: | :---: | :---: | :--- |
| **Solid Ice Density** | $\rho_i$ | $917.0$ | $\text{kg/m}^3$ | Standard glaciological convention |
| **Ocean Water Density** | $\rho_w$ | $1,028.0$ | $\text{kg/m}^3$ | Sub-polar Antarctic seawater density |
| **Freshwater Density** | $\rho_{\text{fw}}$ | $1,000.0$ | $\text{kg/m}^3$ | Global hydrological standard |
| **Gravitational Acceleration** | $g$ | $9.81$ | $\text{m/s}^2$ | Standard surface gravity |
| **Global Ocean Surface Area** | $A_{\text{ocean}}$ | $3.618 \times 10^{14}$ | $\text{m}^2$ | Standard ISMIP6 / CMIP6 ocean area |
| **Mass-to-SLE Constant** | $\mathcal{C}_{\text{sle}}$ | $361.8$ | $\text{Gt/mm}$ | $A_{\text{ocean}} \times \rho_{\text{fw}} / 10^{12}$ |
| **Glen's Exponent** | $n$ | $3.0$ | dimensionless | Ice deformation power law |
| **Glen's Flow Rate Factor** | $A(T)$ | $3.5 \times 10^{-25}$ | $\text{Pa}^{-3}\text{ s}^{-1}$ | Ice rate factor at approx. $-10^\circ\text{C}$ |
| **Regularization Strain Rate** | $\dot{\varepsilon}_0$ | $1.0 \times 10^{-5}$ | $\text{yr}^{-1}$ | Prevents singularity in stagnancy |
| **Weertman Friction Exponent** | $m$ | $1/3$ or $1.0$ | dimensionless | Non-linear / linear basal sliding |
| **Grid Cell Dimensions** | $\Delta x, \Delta y$ | $500.0$ | meters | EPSG:3031 Polar Stereographic grid |
| **Grid Cell Area** | $A_{\text{cell}}$ | $0.25$ | $\text{km}^2$ | Standard 500 m pixel footprint |
| **Analysis Bounding Box** | $X_{\text{span}}, Y_{\text{span}}$ | $1300 \times 1700$ | km | Processing envelope ($2600 \times 3400$ px) |

---

## 3. Dataset Registry & Provenance Specifications

```
+-----------------------------------------------------------------------------------------------+
| DATASET IDENTIFIER | SOURCE INSTITUTION   | ACCESS PROTOCOL | VARIABLES USED                  |
+--------------------+----------------------+-----------------+---------------------------------+
| Bedmap3            | British Ant. Survey  | Open CC-BY-4.0  | thickness, masks, err_thickness |
| BedMachine v4.1    | NASA NSIDC DAAC      | Earthdata OAuth | bed, surface, mask, errbed, firn|
| REMA v1.1          | PGC / Byrd Polar     | Open GeoTIFF    | 8m/100m/500m Surface DEM        |
| RACMO2.3p2         | Utrecht Univ. (IMAU) | NetCDF-4        | SMB, precip, sublimation, melt  |
| Satellite InSAR D  | MEaSUREs (UCI/JPL)   | Tabular CSV     | Flux gate solid-ice discharge   |
| IMBIE Reconcilement| IMBIE Consortium     | Tabular CSV     | Independent annual mass balance |
| ISMIP6 Multi-Model | CMIP6 / NASA GSFC    | NetCDF / Tabular| ivaf, ivol, model control runs  |
+-----------------------------------------------------------------------------------------------+
```

1. **Bedmap3 (BAS / SCAR, 2025):**
   - *DOI:* `10.5285/2d0e4791-8e20-46a3-80e4-f5f6716025d2`
   - *Grid Specs:* $13,334 \times 13,334$ continent grid at 500 m. Subsampled without interpolation to $3,400 \times 2,600$ Peninsula window.
   - *Masks:* 1=permanently grounded, 2=transiently grounded, 3=floating shelf, 4=ice-free rock.
2. **BedMachine Antarctica v4.1 (NASA NSIDC, 2026):**
   - *DOI:* `10.5067/POJQI54A45HX`
   - *Specific Feature:* Incorporates IceBoost machine-learning ice thickness (`source == 8`) across the complex topography of the Antarctic Peninsula.
3. **RACMO2.3p2 (IMAU, 2018):**
   - *Resolution:* 5.5 km non-hydrostatic regional atmospheric model driven by ERA-Interim and ERA5 boundary conditions.
4. **ISMIP6 Multi-Model Archive (Seroussi et al., 2020):**
   - *DOI:* `10.5194/tc-14-3033-2020`
   - *Included Model Families:* `AISMPALEO`, `CISM`, `ElmerIce`, `GRISLI`, `IMAUICE`, `ISSM`, `MALI`, `PISM`, `SICOPOLIS`, `fETISh`.

---

## 4. Feature Schemas

### 4.1 Stage 6.0 Historical Feature Schema (14 Features)
Strictly enforces temporal antecedence to prevent lookahead data leakage:

1. `Target_Volume_Change_Lag1_km3_yr`: Measured volume change rate at $t-1$ ($\text{km}^3/\text{yr}$).
2. `Target_Volume_Change_Lag2_km3_yr`: Measured volume change rate at $t-2$ ($\text{km}^3/\text{yr}$).
3. `Net_MB_Lag1_Gt_yr`: Antecedent net mass budget ($SMB - D$) at $t-1$ ($\text{Gt/yr}$).
4. `SMB_Lag1_Gt_yr`: RACMO2.3p2 surface mass balance at $t-1$ ($\text{Gt/yr}$).
5. `Discharge_Lag1_Gt_yr`: Satellite grounding-line flux gate discharge at $t-1$ ($\text{Gt/yr}$).
6. `SMB_Rolling3yr_Gt_yr`: 3-year trailing rolling average of SMB over $[t-3, t-1]$ ($\text{Gt/yr}$).
7. `SMB_Anomaly_Lag1_Gt_yr`: Anomaly relative to 1979–2005 baseline mean ($\text{Gt/yr}$).
8. `Grounded_Area_km2`: Grounded basin area from BedMachine mask ($\text{km}^2$).
9. `Mean_Baseline_Ice_Thickness_m`: Basin mean ice column thickness ($\text{m}$).
10. `Bed_Elevation_at_Gates_m`: Mean bedrock elevation at marine grounding line flux gates ($\text{m}$).
11. `Driving_Stress_Index_kPa`: Gravitational shear driving stress proxy ($\rho_i g H \nabla s$) ($\text{kPa}$).
12. `is_Hp_I`: One-hot binary indicator for Palmer Land West {0.0, 1.0}.
13. `is_I_Ipp`: One-hot binary indicator for Graham Land {0.0, 1.0}.
14. `is_Ipp_J`: One-hot binary indicator for Palmer Land East {0.0, 1.0}.

### 4.2 Stage 7.1 Future Projection Feature Schema (17 Features)
Combines macro-climatic GCM forcing with regional topographic boundary conditions:

1. `Projection_Horizon_yr`: Elapsed lead time ($t - 2014$) (years).
2. `Scenario_Code`: Radiative forcing scenario {0=RCP2.6, 1=SSP2-4.5, 2=RCP8.5}.
3. `Global_Mean_Temp_Anomaly_degC`: GCM global surface warming anomaly ($^\circ\text{C}$).
4. `Radiative_Forcing_W_m2`: Top-of-atmosphere radiative forcing anomaly ($\text{W/m}^2$).
5. `Cumulative_Radiative_Forcing_W_m2_yr`: Time-integrated radiative forcing ($\text{W/m}^2\cdot\text{yr}$).
6. `GCM_ECS_degC`: Equilibrium Climate Sensitivity of parent GCM ($^\circ\text{C}$).
7. `GCM_TCR_degC`: Transient Climate Response of parent GCM ($^\circ\text{C}$).
8. `Ocean_Thermal_Regime_Code`: Sub-shelf thermal melt parameterization {0=Standard, 1=High, 2=PIGL}.
9. `Ocean_Sensitivity_Factor`: Thermal melt scalar $\gamma_T$ ($1.0$ to $3.5$).
10. `Grounded_Area_km2`: Grounded basin surface area ($\text{km}^2$).
11. `Mean_Ice_Thickness_m`: Hypsometric mean ice column thickness ($\text{m}$).
12. `Bed_Elevation_Gates_m`: Bedrock elevation at marine outlet gates ($\text{m a.s.l.}$).
13. `Driving_Stress_kPa`: Mean gravitational driving stress ($\text{kPa}$).
14. `is_Hp_I`: Spatial dummy indicator for Palmer Land West {0, 1}.
15. `is_I_Ipp`: Spatial dummy indicator for Graham Land {0, 1}.
16. `is_Ipp_J`: Spatial dummy indicator for Palmer Land East {0, 1}.
17. `is_Domain_A`: Spatial dummy indicator for aggregate Domain A {0, 1}.

---

## 5. Validation Protocols & Chronological Designs

### 5.1 Historical Chronological Split Design
- **Training Set (1979–2005, 27 years):** $27 \times 3 = 81$ rows (58.7%).
- **Embargo Period 1 (2006–2007, 2 years):** $2 \times 3 = 6$ rows (4.3%). Quarantines 2-year lagged autoregressive correlation.
- **Validation Set (2008–2014, 7 years):** $7 \times 3 = 21$ rows (15.2%). Used for hyperparameter tuning.
- **Embargo Period 2 (2015, 1 year):** $1 \times 3 = 3$ rows (2.2%). Quarantines 1-year lagged features.
- **Prospective Test Set (2016–2024, 9 years):** $9 \times 3 = 27$ rows (19.6%). Strict hold-out test set.

### 5.2 Leave-One-Model-Family-Out (LOMFO) Cross-Validation
Structure of the 10 cross-validation folds:

| Fold | Withheld Model Family | Constituent Models | Withheld Records |
| :---: | :--- | :--- | :---: |
| 1 | `AISMPALEO` | `VUB_AISMPALEO` | 3,400 |
| 2 | `CISM` | `NCAR_CISM` | 6,460 |
| 3 | `ElmerIce` | `UTAS_ElmerIce` | 1,020 |
| 4 | `GRISLI` | `LSCE_GRISLI` | 4,080 |
| 5 | `IMAUICE` | `IMAU_IMAUICE1`, `IMAU_IMAUICE2` | 6,800 |
| 6 | `ISSM` | `JPL1_ISSM`, `UCIJPL_ISSM` | 9,860 |
| 7 | `MALI` | `DOE_MALI` | 2,720 |
| 8 | `PISM` | `AWI_PISM1`, `PIK_PISM1`, `PIK_PISM2`, `VUW_PISM` | 11,220 |
| 9 | `SICOPOLIS` | `ILTS_PIK_SICOPOLIS` | 4,080 |
| 10 | `fETISh` | `ULB_fETISh_16km`, `ULB_fETISh_32km` | 14,280 |
| **Total** | **10 Families** | **16 Configurations** | **63,920** |

---

## 6. Scenario Provenance & Watermarks

1. **`RCP8.5` (High Emissions):**
   - *Provenance:* Native ISMIP6 Tier-1 numerical simulations.
   - *Forcing:* High fossil-fuel development; radiative forcing reaches $\sim 8.5\text{ W/m}^2$ by 2100.
2. **`RCP2.6` (Aggressive Mitigation):**
   - *Provenance:* Native ISMIP6 Tier-2 numerical simulations.
   - *Forcing:* Rapid decarbonization aiming for $< 2^\circ\text{C}$ warming; radiative forcing peaks and declines to $\sim 2.6\text{ W/m}^2$ by 2100.
3. **`SSP2-4.5` (Middle-of-the-Road Synthesis):**
   - *Provenance:* Pattern-scaled synthesis ($\alpha = 0.35$).
   - *Status:* Explicitly designated as `SCALED_EMULATOR_SYNTHESIS` across all system components.

---

## 7. Important Glaciological Terminology

- **Volume Above Flotation (VAF):** The column-integrated ice volume resting on bedrock above hydrostatic flotation. The sole glaciological metric directly determining global mean sea-level change.
- **Grounded Solid-Ice Volume ($V_g$):** The total geometric volume of solid ice situated on grounded bedrock. Does not equal VAF in marine basins where bedrock lies below sea level.
- **Geometric Ice Volume ($V_{\text{geom}}$):** Total ice volume including both grounded ice and floating ice shelves.
- **Sea-Level Equivalent (SLE):** The uniform global mean sea-level change resulting from melting a given ice mass, assuming an ocean surface area of $3.618 \times 10^{14}\text{ m}^2$ and ice density of $917\text{ kg/m}^3$.
- **Grounding Line:** The boundary dividing grounded ice resting on bedrock from ice shelves floating freely on seawater.
- **Pinball Loss (Tilted Absolute Loss):** Asymmetric piecewise-linear loss function used to estimate specific quantiles without parametric assumptions.
- **Leave-One-Model-Family-Out (LOMFO):** Cross-validation technique withholding all configurations of a numerical ice sheet model family to test out-of-distribution generalization.
- **Monotone Quantile Rearrangement:** Sorting estimated quantiles to strictly enforce monotonicity ($q_{10} \le \dots \le q_{90}$) without altering underlying empirical variance.
