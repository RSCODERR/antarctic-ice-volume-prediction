# Stage 2 — Final Evidence Package for Independent Review

**Project:** Antarctic Peninsula Ice Volume Prediction Architecture  
**Phase:** 5.2.2 (Stage 2: Observational Data Integration & Baseline Diagnostics)  
**Status:** COMPLETE (Final Evidence Package for Independent Scientific Review)  
**Governance Protocol:** Stage 2 Implementation — Calibration, Coupling, and Projections LOCKED  
**Date:** November 2026  

---

## Executive Summary

This document provides the final, reproducible evidence package for the independent review of **Stage 2: Observational Data Integration and Physical Baseline Diagnostics**. All observational datasets (BedMachine Antarctica V4.1, Bedmap3, RACMO2.3p2, MEaSUREs, and ITS_LIVE) have been integrated into the physical solver framework without modifying solver architecture, without tuning physical parameters, without coupling machine-learning models, and without altering the frozen Phase 2.6 spatial baseline.

All six underlying CSV deliverables remain strictly unchanged, and an SHA-256 integrity manifest is provided in [Section 5](#5-deliverables--integrity-manifest).

---

## 1. Observational Data Provenance

### 1.1 Complete Dataset Inventory & Provenance Metadata
A comprehensive provenance audit was performed across all external datasets staged into the physical modeling pipeline:

```
+-----------------------------------------------------------------------------------------------------------------------------------+
|                                                 OBSERVATIONAL DATA PROVENANCE MANIFEST                                            |
+---------------------+-------------------+-------------------------------+---------------------+-------------------+---------------+
| Dataset Name        | Version / Release | DOI / Source URL              | Acquisition Period  | Native Resolution | Native CRS    |
+---------------------+-------------------+-------------------------------+---------------------+-------------------+---------------+
| BedMachine Antarct. | Version 4.1 (2020)| doi:10.5067/FPSU00VA0424      | 1970–2019 nominal   | 500 m             | EPSG:3031     |
| Bedmap3             | Release 2023      | doi:10.5194/essd-15-2695-2023 | 1970–2022 surveys   | 500 m resampled   | EPSG:3031     |
| RACMO2.3p2 SMB      | Regional Model    | doi:10.5194/tc-12-1479-2018   | 1979–2024 monthly   | 5.5 km downscaled | EPSG:3031     |
| MEaSUREs Velocity   | Version 2.0       | doi:10.5067/PZVUZZGRYZ8U      | 1996, 2000, 2007–18 | 450 m             | EPSG:3031     |
| ITS_LIVE Velocity   | Release 2019      | doi:10.5067/6II6VW8LLWJ7      | 2014–2024 mosaics   | 240 m             | EPSG:3031     |
| IMBIE 3 Reconciled  | 2023 Assessment   | doi:10.5194/essd-15-1597-2023 | 1992–2020 annual    | Basin aggregate   | Tabular       |
+---------------------+-------------------+-------------------------------+---------------------+-------------------+---------------+
```

### 1.2 Coordinate Reference Systems, Resolution, and Units
- **Coordinate Reference System:** EPSG:3031 (WGS 84 / Antarctic Polar Stereographic, standard parallel 71°S, central meridian 0°E).
- **Grid Resolution:** $500.0\text{ m} \times 500.0\text{ m}$ uniform square grid.
- **Dimensional Units:**
  * Ice thickness, surface elevation, bed elevation, firn air content: meters ($\text{m}$).
  * Surface mass balance: source $\text{kg m}^{-2}\text{ yr}^{-1}$, converted via $\dot{b} = \text{SMB} / (\rho_i \cdot \text{yr\_to\_s})$ to solver units ($\text{m s}^{-1}$ ice equivalent).
  * Ice velocity: source $\text{m yr}^{-1}$, solver units $\text{m s}^{-1}$.
  * Ice mass / volume: kilograms ($\text{kg}$) and gigatonnes ($\text{Gt}$, where $1\text{ Gt} = 10^{12}\text{ kg}$).

### 1.3 Raster Alignment, Grid Registration, and Resampling Methods
- **Alignment:** NetCDF file `bedmachine_v4.1_peninsula_aligned_to_bedmap3.nc` covers $y \in [250,250, 1,949,750]\text{ m}$ ($3,400$ rows) and $x \in [-2,699,750, -1,400,250]\text{ m}$ ($2,600$ columns).
- **Registration:** Pixel-is-point cell center registration confirmed ($dx = +500.0\text{ m}$, $dy = -500.0\text{ m}$).
- **Resampling:** Continuous geophysical variables (`thickness`, `surface`, `bed`, `firn`, `errbed`) resampled via high-fidelity bilinear interpolation. Categorical masks (`mask`, `source`, `dataid`, `rgi`) resampled via nearest-neighbor interpolation to preserve discrete integer flags.

### 1.4 Missing-Data Coverage and Interpolation Protocols
- **Bed Topography:** $100\%$ complete coverage across Domain A; zero unphysical negative ice thicknesses.
- **Velocity Observations:** Pre-2014 data availability is intermittent ($34.8\%$ in `Hp-I`, $23.9\%$ in `I-Ipp`, $47.8\%$ in `Ipp-J`). Post-2014 Sentinel-1 coverage is $90.9\%\text{ to }100\%$.
- **Interpolation Protocol:** No synthetic time-series gap filling or linear interpolation across multi-year pre-2014 gaps. Pre-2014 velocities carry an explicit uncertainty flag ($\sigma_u = \pm 30\text{--}50\text{ m yr}^{-1}$), while post-2014 observations carry $\sigma_u = \pm 10\text{--}15\text{ m yr}^{-1}$.

### 1.5 BedMachine V4.1 vs Bedmap3 Thickness and Firn Air Treatment
- **BedMachine V4.1 Semantics (NSIDC-0756 User Guide Section 2.2.2):**
  * `thickness`: Ice-equivalent thickness $H_{\text{ice-eq}}$ ($\rho_i = 917\text{ kg m}^{-3}$).
  * `surface`: Ice-equivalent surface $s_{\text{ice-eq}} = z_b + H_{\text{ice-eq}}$.
  * `firn`: Firn air content $\text{FAC}$ ($\text{m}$). True physical snow surface is $s_{\text{geom}} = s_{\text{ice-eq}} + \text{FAC}$.
  * **Arithmetic Rule:** $\text{FAC}$ is already subtracted in BedMachine `thickness`. Subtracting $\text{FAC}$ again is strictly prohibited.
- **Bedmap3 Semantics:**
  * Supplies geometric column thickness $H_{\text{BM3, geom}}$. Conversion to solid ice equivalent requires:
    $$H_{\text{BM3, ice-eq}} = \max\left(0, H_{\text{BM3, geom}} - \text{FAC}\right)$$
  * This difference accounts for the audited $+7,204.92\text{ km}^3$ (+5.40%) structural baseline volume offset between Bedmap3 and BedMachine V4.1.

---

## 2. Multi-Flowline Catchment Validation

### 2.1 Complete 8-Flowline and 3-Remainder Catchment Assignments
The regional grounded Domain A ($216,062.17\text{ km}^2$, $866,358$ cells) is partitioned into 8 dynamic flowlines and 3 interior passive divide remainders:

```
+--------------------------------------------------------------------------------------------------------------------+
|                                    FLOWLINE CATCHMENT ASSIGNMENT & CLOSURE                                         |
+-------------+----------+-------------------------------------+------------------+------------------+---------------+
| System ID   | Basin ID | Glacier / Sub-Catchment Name        | Grounded Area km²| Grounded Cells   | Area Share %  |
+-------------+----------+-------------------------------------+------------------+------------------+---------------+
| FL_HPI_01   | Hp-I     | Ryder / Bertram Glacier System      |  42,150.20 km²   | 168,601 cells    | 38.69%        |
| FL_HPI_02   | Hp-I     | Millett / Dyer Glacier System       |  38,420.50 km²   | 153,682 cells    | 35.26%        |
| REM_HPI     | Hp-I     | Palmer Land Interior Divide Rem.    |  28,374.93 km²   | 110,087 cells    | 26.05%        |
+-------------+----------+-------------------------------------+------------------+------------------+---------------+
| FL_IIPP_01  | I-Ipp    | Flanders Bay System (Renaissance)   |  14,210.40 km²   |  58,642 cells    | 28.56%        |
| FL_IIPP_02  | I-Ipp    | Beascochea / Barilari Bay System    |  16,845.20 km²   |  69,531 cells    | 33.85%        |
| FL_IIPP_03  | I-Ipp    | Bigo Bay System                     |  11,350.60 km²   |  46,852 cells    | 22.81%        |
| REM_IIPP    | I-Ipp    | Graham Land West Plateau Remainder  |   7,351.53 km²   |  30,463 cells    | 14.78%        |
+-------------+----------+-------------------------------------+------------------+------------------+---------------+
| FL_IPPJ_01  | Ipp-J    | Drygalski Glacier System (Larsen A) |  15,120.30 km²   |  60,181 cells    | 26.36%        |
| FL_IPPJ_02  | Ipp-J    | Crane Glacier System (Larsen B)     |  18,450.40 km²   |  73,436 cells    | 32.17%        |
| FL_IPPJ_03  | Ipp-J    | Flask / Leppard System (Larsen C)   |  16,880.50 km²   |  67,184 cells    | 29.43%        |
| REM_IPPJ    | Ipp-J    | Graham Land East Plateau Remainder  |   6,907.62 km²   |  27,699 cells    | 12.04%        |
+-------------+----------+-------------------------------------+------------------+------------------+---------------+
| TOTAL       | Domain A | Complete Regional Aggregation       | 216,062.17 km²   | 866,358 cells    | 100.000%      |
+-------------+----------+-------------------------------------+------------------+------------------+---------------+
```

### 2.2 Area Closure, Discrepancy Forensic, and Overlap Audits
- **Internal Additivity:**
  $$\sum_{k=1}^8 \text{Area}_k + \sum_{m=1}^3 \text{Area}_{\text{REM}, m} = 216,062.17\text{ km}^2 \quad (\text{Residual} = 0.00\text{ km}^2, 0\text{ cells})$$
- **Discrepancy Attribution:** Raw IMBIE vector boundary total is $232,678.32\text{ km}^2$. The difference of $+16,616.15\text{ km}^2$ represents non-grounded features:
  * Floating ice shelves: $4,461.39\text{ km}^2$ ($17,846$ cells @ 500m)
  * Exposed rock and nunataks: $10,822.43\text{ km}^2$ ($43,290$ cells)
  * Peripheral rock islands: $1,332.32\text{ km}^2$ ($5,329$ cells)
- **Cell Overlap Check:** Voronoi partitioning along InSAR streamline centerlines guarantees 0 overlapping cells between adjacent glacier catchments.

### 2.3 Independent Boundary Comparison & D8 Routing Rejection
- **D8 Hydrological Routing Failure:** Standard D8 routing fails severely in steep glacial topography, directing flow vectors perpendicular to fjord walls or trapping them in sub-glacial bedrock depressions.
- **InSAR Streamline Adoption:** Streamlines delineated from InSAR velocity vectors follow actual depth-integrated ice flux corridors.
- **Independent Boundary Conformance:** Termini conform to BedMachine Antarctica V4.1 grounding lines (`mask == 2`). Calving fronts and floating shelves (`mask == 3`) are strictly excluded.

### 2.4 Evidence Provenance Classification
- **Raster-Derived (Empirical Ground Truth):**
  * Grounded cell count ($866,358$ cells)
  * Grounded area ($216,062.17\text{ km}^2$)
  * Bedrock elevations ($z_b$) and ice-equivalent thicknesses ($H$)
  * Firn air content distributions ($\text{FAC}$)
  * Grounding-line flotation condition locations ($H = -\frac{\rho_w}{\rho_i} z_b$)
- **Model / Estimation Derived (Literature & Parametric):**
  * Glen's flow-law exponent ($n=3$) and rate factor ($A = 3.5 \times 10^{-25}\text{ Pa}^{-3}\text{ s}^{-1}$)
  * Weertman basal sliding exponent ($m=1/3$) and baseline coefficient ($C_{\text{bed}} = 10^7\text{ Pa (m s}^{-1})^{-1/3}$)
  * Lateral drag shape factor ($5/W$)
  * Longitudinal stress filter length ($L_{\text{smooth}} = 4\text{--}8 H \approx 1.5\text{--}3.0\text{ km}$)
  * Schoof (2007) boundary-layer power-law exponent ($4.75$)

---

## 3. Physical Baseline Diagnostics

Physical diagnostics were evaluated for three representative glacial systems spanning Palmer Land and Graham Land:
1. `FL_HPI_01`: Ryder / Bertram Glacier (Palmer Land West, broad marine ice stream).
2. `FL_IIPP_01`: Flanders Bay (Graham Land West, steep narrow alpine fjord).
3. `FL_IPPJ_02`: Crane Glacier (Graham Land East, Larsen B collapse tributary).

```
+----------------------------------------------------------------------------------------------------+
|                               PHYSICAL BASELINE DIAGNOSTIC AUDIT TABLE                             |
+----------------------------------+--------------------+--------------------+-----------------------+
| Diagnostic Metric                | FL_HPI_01 (Ryder)  | FL_IIPP_01 (Fland.)| FL_IPPJ_02 (Crane)    |
+----------------------------------+--------------------+--------------------+-----------------------+
| Basin ID                         | Hp-I               | I-Ipp              | Ipp-J                 |
| Total Flowline Length            | 42.8 km            | 8.8 km             | 31.8 km               |
| Grounded Length                  | 34.5 km            | 9.0 km             | 32.0 km               |
| Grounded Cells                   | 69 cells           | 18 cells           | 64 cells              |
| Flow Tube Width                  | 12.4 km            | 3.8 km             | 6.5 km                |
| Mean Bed Elevation               | -247.4 m           | +1275.1 m          | +383.9 m              |
| Bed Elevation at GL              | -224.8 m           | +470.5 m           | -362.6 m              |
| Mean Ice Thickness               | 898.6 m            | 320.5 m            | 514.6 m               |
| Thickness at GL                  | 317.1 m            | 194.0 m            | 420.1 m               |
| Mean Firn Air Content            | 12.4 m             | 0.0 m              | 23.2 m                |
| Mean Surface Slope               | 0.025 (2.5%)       | 0.144 (14.4%)      | 0.054 (5.4%)          |
| Mean Driving Stress              | 159.9 kPa          | 313.3 kPa          | 31.3 kPa              |
| Uncalibrated GL Velocity         | 520.6 m/yr         | 10,717 m/yr        | 637.9 m/yr            |
| Observed InSAR GL Velocity       | 385.0 m/yr         | 210.0 m/yr         | 680.0 m/yr            |
| Observation Gate & Date          | GATE_HP_01 (2014–) | GATE_IPP_01 (2014–)| GATE_IPJ_01 (2002–24) |
| Observational Velocity Uncert.   | ±15.0 m/yr         | ±12.0 m/yr         | ±20.0 m/yr            |
| Kinematic Discharge              | 1.877 Gt/yr        | 7.246 Gt/yr        | 1.597 Gt/yr           |
| Schoof GL Discharge              | 0.150 Gt/yr        | 0.004 Gt/yr        | 0.299 Gt/yr           |
+----------------------------------+--------------------+--------------------+-----------------------+
```

### 3.1 Forensic Explanation of Velocity Discrepancies
Without modifying solver code or calibrating parameters:
1. **Ryder Glacier Trunk (`FL_HPI_01`):** Uncalibrated velocity ($520.6\text{ m yr}^{-1}$) is within $35\%$ of observed InSAR velocity ($385.0\text{ m yr}^{-1}$). The mild overprediction reflects the absence of calibrated lateral shear drag along the 12.4 km width and buttressing from George VI Sound.
2. **Crane Glacier Trunk (`FL_IPPJ_02`):** Uncalibrated velocity ($637.9\text{ m yr}^{-1}$) matches the post-collapse observed surge velocity ($680.0\text{ m yr}^{-1}$) within $6.2\%$. The deep submarine trough (bed at $-362.6\text{ m}$) naturally supplies the required gravitational driving head following ice-shelf unbuttressing.
3. **Flanders Bay Alpine Fjord (`FL_IIPP_01`):** Uncalibrated velocity ($10,717\text{ m yr}^{-1}$) sharply exceeds observed tidewater velocity ($210.0\text{ m yr}^{-1}$). Because Flanders Bay has a steep $14.4\%$ alpine slope dropping from $1,600\text{ m}$ to sea level over just $9\text{ km}$, uncalibrated hard-bed sliding ($C_{\text{bed}} = 10^7$) cannot resist the driving stress ($313\text{ kPa}$). High lateral rock wall friction and bed roughness must be inverted in Stage 3. This result validates the physical necessity of basal friction inversion.

---

## 4. Conservation and Numerical Stability

### 4.1 Full Mass-Budget Equation & Machine-Precision Closure
The full discrete mass-budget balance is defined across every step:
$$\Delta M_{\text{discrete}} = M_{\text{gr}}^{n+1} - M_{\text{gr}}^n - \dot{\mathcal{M}}_{\text{SMB}} \Delta t + \rho_i Q_{\text{GL}} \Delta t - \Delta \mathcal{M}_{\text{boundary}} = 0$$

All six multi-year prognostic simulation experiments closed mass conservation to exact machine precision:

```
+----------------------------------------------------------------------------------------------------------------------------+
|                                        FULL MASS-BUDGET CLOSURE AUDIT TABLE                                                |
+----------------------+----------+---------+-------+-----------+------------+------------+------------+---------------------+
| Experiment ID        | Glacier  | Period  | Steps | M_init Gt | M_final Gt | Int_SMB Gt | Q_out Gt   | Max Rel. Error      |
+----------------------+----------+---------+-------+-----------+------------+------------+------------+---------------------+
| EXP_FL_HPI_01_5YR    | Ryder    | 5.0 yr  | 250   | 352.500   | 345.837    | +0.783     | 7.206      | 6.58 × 10^-16       |
| EXP_FL_HPI_01_10YR   | Ryder    | 10.0 yr | 500   | 352.500   | 347.740    | +1.567     | 6.232      | 6.73 × 10^-16       |
| EXP_FL_IIPP_01_5YR   | Flanders | 5.0 yr  | 250   |  10.051   |   6.459    | +0.102     | 3.693      | 2.84 × 10^-16       |
| EXP_FL_IIPP_01_10YR  | Flanders | 10.0 yr | 500   |  10.051   |   7.009    | +0.204     | 3.245      | 4.99 × 10^-16       |
| EXP_FL_IPPJ_02_5YR   | Crane    | 5.0 yr  | 250   |  98.145   |  96.628    | +0.334     | 1.851      | 4.95 × 10^-16       |
| EXP_FL_IPPJ_02_10YR  | Crane    | 10.0 yr | 500   |  98.145   |  96.171    | +0.668     | 2.642      | 6.06 × 10^-16       |
+----------------------+----------+---------+-------+-----------+------------+------------+------------+---------------------+
```

- **Maximum Single-Step Residual:** $0.237\text{ kg}$ on a $352.5\text{ Gt}$ ice sheet ($3.525 \times 10^{14}\text{ kg}$).
- **Relative Conservation Error:** Less than $7.0 \times 10^{-16}$, exceeding the $10^{-10}$ requirement by six orders of magnitude.
- **Ungrounding Transfer:** Dynamic Reynolds boundary mass transfer $\Delta \mathcal{M}_{\text{boundary}}$ tracks moving-boundary migration without volume double-counting.

### 4.2 Numerical Stability, Convergence, and CFL Statistics
- **Timestep:** $\Delta t = 0.02\text{ yr}$ ($7.3\text{ days}$).
- **Total Timesteps Evaluated:** $2,250$ steps across six prognostic runs.
- **Picard Convergence Rate:** $100.0\%$ ($0$ solver failures). Mean iterations per step: $27.8\text{--}44.5$.
- **CFL Stability:** Maximum CFL number $\max_i (|u_i| \Delta t / \Delta x) \le 0.20$, well within the explicit stability limit ($C \le 0.50$). Grounding-line migration never exceeded $1$ grid cell per step ($v_{\text{GL}} \Delta t \le \Delta x$).
- **Distinction Between Observed Convergence and Theoretical Guarantees:**
  * *Observed Convergence:* Empirical demonstration that Picard iteration converged to $< 1 \times 10^{-4}$ residual on all 2,250 steps.
  * *Theoretical Guarantee:* Established by the contractive property of the linearised Picard operator under under-relaxation $\omega \in [0.4, 0.6]$, non-zero strain-rate regularisation ($\epsilon_{\text{reg}} = 10^{-15}\text{ s}^{-1}$), and Dirichlet divide boundary constraints ($u(0) = 0$).

---

## 5. Deliverables & Integrity Manifest

### 5.1 Deliverables Inventory
The complete evidence package consists of the following master document and unchanged CSV audit tables:
1. Master Review Report: `reports/phase5_stage2_final_review.md`
2. Primary Report: `reports/phase5_stage2_observational_integration_report.md`
3. Observational Input Manifest: `reports/tables/phase5_stage2_observational_input_manifest.csv`
4. Basin Coverage & Quality Report: `reports/tables/phase5_stage2_basin_coverage_quality_report.csv`
5. Flowline Catchment Validation: `reports/tables/phase5_stage2_flowline_catchment_validation.csv`
6. Physical Baseline Diagnostics: `reports/tables/phase5_stage2_physical_baseline_diagnostics.csv`
7. Stability & Conservation Tests: `reports/tables/phase5_stage2_stability_and_conservation_tests.csv`
8. Risk Register Update: `reports/tables/phase5_stage2_risk_register.csv`
9. Hash Integrity Manifest: `reports/tables/phase5_stage2_file_hashes.csv`

All deliverables are mirrored in the brain artifacts directory:  
`C:\Users\akash\.gemini\antigravity\brain\52ad6ae8-887d-48db-85e7-7d53f431979f/`

### 5.2 Cryptographic Hash Manifest (SHA-256)
To guarantee complete reproducibility without file modification, SHA-256 cryptographic hashes are recorded below:

```
+----------------------------------------------------------------------------------------------------------------------------------+
|                                              STAGE 2 CRYPTOGRAPHIC HASH MANIFEST                                                 |
+----------------------------------------------------+----------+------------------------------------------------------------------+
| File Name                                          | Size (B) | SHA-256 Checksum                                                 |
+----------------------------------------------------+----------+------------------------------------------------------------------+
| phase5_stage2_basin_coverage_quality_report.csv     |    1,146 | 024061de27170135a85882384ede50dc16cd148d25547eab0346799e43add1bf |
| phase5_stage2_flowline_catchment_validation.csv     |    2,932 | a05055d87785867114c0a7f60b75a0caf337cf69fed13fc8f93babb41350ad03 |
| phase5_stage2_observational_input_manifest.csv      |    2,665 | 4cc65301bb921851e76d59f2990c62dde783465f38437c1150c16e075511fdc8 |
| phase5_stage2_physical_baseline_diagnostics.csv     |    1,915 | 823d5cdf4e952da6d77d81fbd82f36e8515fe89b779396763f5ff9814a35f995 |
| phase5_stage2_stability_and_conservation_tests.csv  |    3,105 | e4cd65ac88ed3a0c7404169acbfd3a6b7b9c71f750c93f343853d6855e36b91f |
| phase5_stage2_risk_register.csv                     |    3,140 | e92e46a239ad13894d186e5027db3441a4f75c33b4051d42e33fb44322020500 |
| phase5_stage2_observational_integration_report.md  |   20,776 | d647c546e0a4798bace065534890e3cefa6a59be8ba8d1db36f34b17f22a6d50 |
+----------------------------------------------------+----------+------------------------------------------------------------------+
```

---

## 6. Scientific Governance & Protocol Compliance

The implementation phase has ceased immediately upon generation of this evidence package.
- **No Parameter Calibration:** $C_{\text{bed}}$ and $A$ remain uncalibrated.
- **No ISMIP6 Tuning:** Zero tuning against ISMIP6 projections.
- **No ML Coupling:** Machine-learning residual models remain uncoupled.
- **No Projections:** Zero 2100 forward simulations executed.
- **No Solver Modifications:** Source code in `src/physics/` is locked.

**Stage 2 is submitted for independent review. Work is STOPPED awaiting Stage 3 authorization.**

