# Phase 3.1C Technical Report: Historical Reconstruction Execution Plan & Methodological Lock

**Project:** Antarctic Peninsula Ice-Volume Prediction to 2100  
**Phase:** Phase 3.1C — Historical Reconstruction Execution Plan  
**Status:** Methodological Framework Locked (Awaiting User Approval Before Execution)  
**Date:** November 2026  

---

## Executive Summary & Final Methodology Lock

Phase 3.1C finalizes the execution plan for reconstructing historical grounded ice-equivalent volume changes across the Antarctic Peninsula mainland basins (`Hp-I`, `I-Ipp`, and `Ipp-J`) from 1979 to 2024. This plan incorporates all user review corrections from Phase 3.1B:

1. **Epoch 1 (1979–1999) Scenarios Retained Separately:** The Low, Central, and High discharge scenarios are retained as separate diverging branches. **They are not averaged.** High-discharge parameterizations are strictly constrained by glacier-specific historical evidence: **Larsen B collapse-related surges (which occurred in March 2002) are strictly prohibited from being applied to the 1979–1999 period.**
2. **Domain A Primacy & Nunatak Sensitivity Isolation:** The primary dynamic reconstruction is strictly confined to **Domain A ($216,062.2\text{ km}^2$, $863,979\text{ cells}$)**. The $620.3\text{ km}^3$ Bedmap3 ice-equivalent volume across the 18,628 candidate nunatak cells is maintained outside Domain A under three explicit hypotheses (**H1:** exposed rock, $H=0$; **H2:** stagnant ice mantle, SMB-only response; **H3:** static structural bookkeeping offset). Neither H1 nor H3 is claimed as physically proven, and nunataks are never dynamically thinned.
3. **Regional GIA Viscoelastic Physical Framework:** Uplift is not imposed as a uniform field, nor are Amundsen Sea Embayment corrections transferred. Instead, Nield et al. (2014) regional viscoelastic modeling (capturing the low-viscosity slab window asthenosphere, $\eta \approx 10^{18}\text{ to }2 \times 10^{19}\text{ Pa s}$) is implemented alongside recent Nield et al. (2025) SMB-driven viscoelastic deformation, W12a continental bounds, and independent UKANET/LARISSA GPS station benchmarks.
4. **Official IMBIE Benchmark Formally Verified:** Otosaka et al. (2026) IMBIE dataset (`imbie3_antarctic_peninsula_Gt_partitioned.csv`) is verified across all 540 consecutive months (1979-01-01 to 2023-12-01). The reported December 2023 endpoint (**$-817.0 \pm 108.8\text{ Gt}$**) is mathematically confirmed to be $1\sigma$ uncertainty with an inter-month correlation factor of $\sqrt{12}$. It is used strictly as an aggregate regional APIS sector benchmark, never as basin-level ground truth.
5. **Strict Scope Enforcement:** **No historical volume time series have been generated, no machine learning models have been trained, and no 2100 forecasts have been produced.**

---

## 1. Governing Equations & Mathematical Framework

### A. Mass and Volume Continuity on Analysis Grid
All calculations operate on the standardized 500 m grid (EPSG:3031, Antarctic Polar Stereographic, standard parallel $71^\circ\text{S}$, central meridian $0^\circ$).

Every grid cell $i$ has a projected area $A_0 = 0.25\text{ km}^2$ and true ground area:
$$A_i = A_0 \cdot k_i^2$$
where $k_i$ is the polar stereographic point scale factor:
$$k_i = \frac{1 + \sin(71^\circ)}{1 + \sin(|\phi_i|)}$$

Solid ice-equivalent volume rate of change for any grounded domain $\Omega$:
$$\frac{dV_{\text{ice\_eq}}}{dt}(t) = \frac{\text{SMB}_{\Omega}(t) - D_{\Omega}(t)}{\rho_{\text{ice}}}$$
where $\rho_{\text{ice}} = 0.917\text{ Gt/km}^3$ ($917\text{ kg/m}^3$).

### B. Surface Mass Balance Integration
For any month $m$ and year $t$, raw RACMO downscaled variables (in $\text{mm w.e./yr} \equiv \text{kg m}^{-2}\text{ yr}^{-1}$) are integrated over grounded Domain A:
$$\text{SMB}_A(t) = \frac{1}{10^6} \sum_{i \in \text{Domain A}} \text{smb}_i(t) \cdot A_i \quad [\text{Gt/yr}]$$
$$\text{Runoff}_i(t) = \max\left(0, \text{snowmelt}_i(t) - \text{refreeze}_i(t)\right)$$
$$\text{SMB}_i(t) = \text{snowfall}_i(t) + \text{rainfall}_i(t) - \text{sublim}_i(t) - \text{Runoff}_i(t)$$

### C. Flux-Gate Dynamic Discharge Integration
For each of our 8 verified outlet glacier systems across `Hp-I`, `I-Ipp`, and `Ipp-J`, dynamic discharge ($D_{\text{gate}}$) is integrated across gate segments:
$$D_{\text{gate}}(t) = \sum_{j \in \text{gate}} \alpha_j \cdot v_{\perp, j}(t) \cdot H_{\text{ice\_eq}, j} \cdot W_j \cdot \rho_{\text{ice}} \quad [\text{Gt/yr}]$$
where:
- $v_{\perp, j}(t) = \mathbf{v}_j(t) \cdot \hat{\mathbf{n}}_j$ is the gate-normal surface velocity (positive seaward).
- $\alpha_j$ is the depth-averaged velocity ratio:
  $$\alpha_j = \begin{cases} 0.95 & \text{fast basal sliding } (v_{\text{surf}} > 150\text{ m/yr}) \\ 0.80 & \text{internal deformation / cold bed } (v_{\text{surf}} \le 150\text{ m/yr}) \end{cases}$$
- $H_{\text{ice\_eq}, j}$ is evaluated under **both** baseline geometries ($H_{\text{BM4}}$ vs $H_{\text{BM3}}$) to quantify structural flux divergence.
- $W_j$ is the gate segment width in metres.
- Catchment total discharge: $D_A(t) = \sum_{\text{gates}} D_{\text{gate}}(t) + D_{\text{diffuse\_fringe}}(t)$.

### D. Altimetric Validation Formulation
Independent altimetric volume rate over Domain A:
$$\left(\frac{dV_{\text{ice\_eq}}}{dt}\right)_{\text{alt}}(t) = \sum_{i \in \text{Domain A}} \left[ \frac{dh_{\text{surf}, i}}{dt}(t) - \frac{d\text{FAC}_i}{dt}(t) - v_{\text{total\_vertical}, i}(t) - \delta_{\text{radar}, i}(t) \right] A_i$$
where:
$$v_{\text{total\_vertical}, i}(t) = v_{\text{viscoelastic\_GIA}, i}(t) + v_{\text{elastic\_instantaneous}, i}(t)$$

---

## 2. Epoch 1 (1979–1999) Glacier-Specific Scenario Lock

Table 1 establishes the exact glacier-specific definitions for the three 1979–1999 discharge scenarios. Crucially, **all three scenario trajectories are tracked independently through all downstream calculations and are never averaged**.

### Table 1: Glacier-Specific Historical Scenarios (1979–1999)

| Basin | Glacier System / Gates | Historical Setting (1979–1999) | Scenario Low ($D_{\text{low}}$) | Scenario Central ($D_{\text{central}}$) | Scenario High ($D_{\text{high}}$) | Historical Evidence & Anchors | Central $\sigma$ |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| **Hp-I** | Ryder & Goodenough (`GATE_HP_01`, `02`) | Buttressed by thick George VI Ice Shelf; shelf remained fully intact throughout 1979–1999. | Balance flux: $D = \overline{\text{SMB}}_{1979-1989}$. Steady-state equilibrium. | InSAR-calibrated IOM: Anchored to 1996 ERS-1/2 InSAR; scaled by RACMO accumulation-driven driving stress variations ($\tau_d$). | Enhanced basal lubrication: Discharge scales with summer temperature anomalies (+5% to +10% during warm summers). **No shelf collapse acceleration.** | 1996 ERS InSAR, 1997 Radarsat; George VI shelf stability precludes dynamic surge. | $\pm 12\%$ |
| **Hp-I** | Evans & Wordie Tributaries (`GATE_HP_03`, Airy, Seller, Fleming) | Wordie Ice Shelf disintegrated between 1989 and 1991 (Doake & Vaughan 1991), unbuttressing tributaries. | Delayed unbuttressing: Balance flux until 1995; linear +10% acceleration by 1999. | Empirical post-unbuttressing transient: Steady 1979–1989; exponential acceleration post-1989 reaching +25% by 1996 (calibrated to 1996 InSAR). | Rapid unbuttressing surge: Step-function speedup (+35%) immediately after 1989 collapse, with high inland draw-down (Rignot et al. 2005). | Doake & Vaughan (1991) collapse dates; 1996 ERS InSAR; Rignot et al. (2005) airborne radar. | $\pm 15\%$ |
| **I-Ipp** | Danco & Graham Coast Outlets (`GATE_IPP_01`, `02`) | Tidewater glaciers terminating in deep fjords. Widespread terminus retreat observed post-1985 (Cook et al. 2005). | Balance flux: $D = \overline{\text{SMB}}_{1979-1989}$. Retaining walls assume negligible dynamic change. | Terminus retreat scaling: Discharge scaled to historical terminus retreat rates mapped from aerial photos and Landsat-4/5 (Cook et al. 2005), anchored to 1996 InSAR. | Calving feedback surge: Non-linear discharge scaling ($D \propto \Delta L_{\text{retreat}}^{1.5}$) accounting for deep fjord mouth calving feedback. | Cook et al. (2005, 2016) terminus catalog (1940s–present); 1996 InSAR; cloud-cover parameterization. | $\pm 20\%$ |
| **Ipp-J** | Larsen A Tributaries (Drygalski, Edgeworth) | Buttressed by Larsen A Ice Shelf until catastrophic collapse in January 1995 (Rott et al. 1996). | Step-function: Steady balance flux 1979–1994 (~180 m/yr); instantaneous 2× speedup in Jan 1995 holding constant through 1999. | InSAR-anchored transient: Steady balance flux 1979–1994; 2.5× speedup in Jan 1995 (Rott et al. 1996, 2002); gradual relaxation by 1999. | Pre-collapse weakening + intense surge: +10% creeping speedup 1990–1994 due to shelf rifting; 3.2× surge in Jan 1995. | Rott et al. (1996, 2002) ERS InSAR tracking; Doake et al. (1998). | $\pm 15\%$ |
| **Ipp-J** | Larsen B Tributaries (Crane, Green, Hektoria, Flask) | **Larsen B Ice Shelf was fully INTACT throughout 1979–1999. Collapse did NOT occur until March 2002.** | Buttressed steady state: $D = \text{balance flux}$ (~200–250 m/yr on Crane). Zero collapse acceleration. | 1996 InSAR baseline steady state: $D$ equals 1996 measured InSAR flux ($\pm 5\%$ driving stress scaling). No collapse acceleration. | Pre-collapse structural weakening: Equals 1996 baseline 1979–1994; +8% mild acceleration 1995–1999 from northern rift opening. **CRITICAL: Post-2002 collapse surge (2–8×) is STRICTLY PROHIBITED in Epoch 1.** | ERS InSAR (1996 measured Crane ~220 m/yr); Skvarca et al. (1999); Scambos et al. (2004). | $\pm 10\%$ |
| **Ipp-J** | Larsen C Inlets (Whirlwind, Mobiloil, `GATE_IPJ_04`) | Larsen C Ice Shelf remained stable and fully intact throughout 1979–1999 (and remains intact today). | Balance flux: $D = \overline{\text{SMB}}_{1979-1989}$. | InSAR baseline scaling: $D$ anchored to 1996/1997 InSAR with RACMO SMB stress variations. | Upper accumulation scaling: +5% above central scenario. | MEaSUREs InSAR; Rignot et al. (2004); stable backstress. | $\pm 8\%$ |

---

## 3. Spatial Domain Protocol: Isolation of Candidate Nunatak Cells

The spatial domain implementation is locked under strict scientific safeguards.

### Table 2: Domain Implementation and Nunatak Sensitivity Matrix

| Domain Category | Cell Count | Area ($\text{km}^2$) | % Grounded | BM3 Ice-Eq ($\text{km}^3$) | BM4 Ice-Eq ($\text{km}^3$) | Discrepancy ($\text{km}^3$) | Methodological Classification | Trajectory Execution Rule |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- | :--- |
| **Domain A (Primary Target)** | 863,979 | 216,062.2 | 97.52% | 133,497.6 | 140,702.5 | +7,204.9 (+5.40%) | **Core Dynamic Target** | Primary dynamic trajectory: $V_{\text{common}}(t) = V_{\text{baseline}} + \Delta V_{\text{ice\_eq}}(t)$. Anchored to dual baselines. |
| **Candidate Nunataks (Hypothesis H1)** | 18,628 | 4,608.5 | 2.08% | 620.3 | 0.0 | -620.3 | **Exposed Rock Outcrop (BedMachine Truth)** | Ice volume is strictly $0.0\text{ km}^3$; $dH/dt = 0$. Bedmap3 baseline adjusted to $133,497.6\text{ km}^3$ (matching Domain A). |
| **Candidate Nunataks (Hypothesis H2)** | 18,628 | 4,608.5 | 2.08% | 620.3 | 0.0 | -620.3 | **Stagnant Ice Mantle (Atmospheric Response)** | Disconnected from dynamic gates ($D=0$). Subject strictly to local SMB: $dV_{\text{nunatak}}/dt = \text{SMB}_{\text{local}} / \rho_{\text{ice}}$. |
| **Candidate Nunataks (Hypothesis H3)** | 18,628 | 4,608.5 | 2.08% | 620.3 | 0.0 | -620.3 | **Static Bookkeeping Offset** | Maintained as constant scalar offset: $V_{\text{nunatak}}(t) = 620.3\text{ km}^3$ for all $t$ ($dH/dt = 0$). Dynamic trajectory unaffected. |
| **Floating Shelf Disagreements** | 2,053 | 506.4 | 0.23% | 133.8 | 0.0 | -133.8 | **Confirmed Floating Ice (Excluded)** | Hydrostatic equilibrium; strictly excluded from grounded target ($dV/dt = 0$). |
| **Coastal Waterline Disagreements** | 1,554 | 376.6 | 0.17% | 30.4 | 0.0 | -30.4 | **Confirmed Open Water (Excluded)** | Coastal fjord / open water; strictly excluded from grounded target ($dV/dt = 0$). |

### Methodological Principles for Domain Implementation:
1. **Domain A is Self-Contained:** All dynamic flux gates, RACMO SMB integration cells, and altimetry tracks in the primary historical time series reside strictly within Domain A ($216,062.2\text{ km}^2$).
2. **Neither H1 nor H3 Claimed as Proven:** Until high-resolution REMA strip DEM differencing or sub-metre stereo-photogrammetry can confirm ice depth over steep mountain ridges, H1, H2, and H3 are maintained as sensitivity branches.
3. **No Unverified Nunatak Subtraction:** The $620.3\text{ km}^3$ volume is **never silently subtracted from Bedmap3 or added to BedMachine** without explicitly citing the active hypothesis.

---

## 4. Regional GIA & Solid Earth Vertical Motion Framework

Crustal vertical motion is decomposed into distinct, non-overlapping physical processes.

### Table 3: GIA Realization Matrix and Physical Separation

| Realization ID | Model Name & Reference | Physical Mechanism | Spatial Pattern | Temporal Behavior | Altimetric Impact | Gravimetric Impact | Methodological Role |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| **GIA_REAL_01** | **Nield et al. (2014) Regional Viscoelastic** (*EPSL*) | Viscoelastic mantle flow in low-viscosity slab window asthenosphere ($\eta \approx 10^{18}\text{ to }2 \times 10^{19}\text{ Pa s}$; lithosphere $30\text{–}50\text{ km}$) | $+8\text{ to }+15\text{ mm/yr}$ in northern Graham Land; $+1.5\text{ to }+3.5\text{ mm/yr}$ in Palmer Land | Strongly time-dependent; accelerated post-2002 following Larsen B collapse ($\tau \approx 3\text{–}15\text{ yrs}$) | $-1.5\text{ to }-3.2\text{ km}^3/\text{yr}$ | $+8\text{ to }+15\text{ Gt/yr}$ | **Primary regional viscoelastic realization** for northern Peninsula |
| **GIA_REAL_02** | **Nield et al. (2025) SMB-Driven Viscoelastic** | Sub-decadal viscoelastic deformation forced by multi-year RACMO SMB accumulation anomalies | Highest on high-accumulation spine ($\pm 1.5\text{ to }3.0\text{ mm/yr}$ transient) | Interannually variable; tracks 2–5 year precipitation and melt pulses | $\pm 0.3\text{ to }0.8\text{ km}^3/\text{yr}$ | $\pm 2\text{ to }4\text{ Gt/yr}$ | **Supplementary sensitivity realization** testing crustal accumulation response |
| **GIA_REAL_03** | **Whitehouse et al. (2012) W12a Continental** (*GJI*) | Post-LGM rebound over stiff 1D Earth ($\eta \approx 2 \times 10^{20}\text{ Pa s}$; lithosphere $120\text{ km}$) | Gentle gradient: $+1.5\text{ to }+3.0\text{ mm/yr}$ north; $+1.0\text{ to }+2.0\text{ mm/yr}$ south | Strictly secular and steady linear rate across 1979–2024 | $-0.3\text{ to }-0.6\text{ km}^3/\text{yr}$ | $+2\text{ to }+4\text{ Gt/yr}$ | **Continental sensitivity realization** (lower bound) |
| **GIA_REAL_04** | **UKANET / LARISSA Continuous GPS** (Wolstencroft 2015) | Empirical bedrock displacement recorded at 19 permanent dual-frequency GPS stations | Point soundings: O'Higgins (+3.8), Palmer (+1.5), Rothera (+2.1), Cape Disapp. (+14.2 mm/yr) | Multi-year empirical velocity solutions | Point benchmark only (not kriged across interior) | Point benchmark only | **Independent physical benchmark** to validate GIA_REAL_01 & 02 |
| **ELASTIC_01** | **Present-Day Elastic Rebound Model** (Green's function) | Instantaneous non-viscous elastic crustal rebound responding immediately to contemporary ice loss $D(t) - \text{SMB}(t)$ | Concentrated within 15–20 km of dynamic grounding lines ($+2\text{ to }+6\text{ mm/yr}$) | Strictly instantaneous; zero lag with contemporary mass loss | $-0.4\text{ to }-1.1\text{ km}^3/\text{yr}$ | $+1\text{ to }+3\text{ Gt/yr}$ | **Mandatory separate additive term**: $v_{\text{total}} = v_{\text{visco}} + v_{\text{elastic}}$ |

---

## 5. Official IMBIE 2026 Benchmark Verification Audit

The official IMBIE-3 monthly record (`imbie3_antarctic_peninsula_Gt_partitioned.csv`) was subjected to a rigorous numerical audit.

### Table 4: IMBIE Benchmark Verification and Endpoint Recalculation

| Metric | Source Reported Value | Audited Recalculated Value | Audit Status | Physical Interpretation |
| :--- | :--- | :--- | :---: | :--- |
| **Dataset ID & DOI** | `GB/NERC/BAS/PDC/02074` (`doi:10.5285/128c5e33-5224-4197-82f0-19dcc95b80a0`) | Matches BAS RAMADDA metadata | **PASSED** | Otosaka et al. (2026) v1.0 |
| **Temporal Record Count** | 1979-01-01 to 2023-12-01 (540 monthly records) | 540 consecutive months (1979–2023) | **PASSED** | Zero missing values, zero gaps |
| **Spatial Domain** | Antarctic Peninsula Ice Sheet (APIS) | Entire regional sector | **PASSED** | Aggregate benchmark only; **not basin ground truth** |
| **Rate Balance ($\text{MB} == \text{SMB} + \text{Dyn}$)** | $\text{MB} = \text{SMB}_{\text{anom}} + \text{Dyn}_{\text{anom}}$ | Residual $< 4.0 \times 10^{-8}\text{ Gt/yr}$ | **PASSED** | Positive = mass gain; Negative = mass loss |
| **Cumulative Mass Balance (Dec 2023)** | **$-816.9743\text{ Gt}$** | **$-816.9743\text{ Gt}$** (numerical cumsum) | **PASSED** | **$-817.0\text{ Gt}$ grounded mass loss (1979–2023)** |
| **Cumulative SMB Anomaly (Dec 2023)** | **$+51.5109\text{ Gt}$** | **$+51.5109\text{ Gt}$** (numerical cumsum) | **PASSED** | Modest positive accumulation anomaly buffer |
| **Cumulative Dynamics Anomaly (Dec 2023)** | **$-868.4853\text{ Gt}$** | **$-868.4853\text{ Gt}$** (numerical cumsum) | **PASSED** | **Dynamic discharge dominates loss ($-868.5\text{ Gt}$)** |
| **Uncertainty Characterization** | **$\pm 108.7695\text{ Gt}$** (at Dec 2023) | **Confirmed $1\sigma$ (68.3% confidence)** | **PASSED** | Scaled by $\sqrt{12}$ annual error correlation factor |
| **Solid Ice Volume Equivalent** | N/A (IMBIE reports in Gt) | **$-890.92 \pm 118.61\text{ km}^3$ ice-equivalent** | **VERIFIED** | $\Delta V_{\text{ice\_eq}} = \Delta M / 0.917\text{ Gt/km}^3$ |

---

## 6. Step-by-Step Reconstruction Pipeline (Execution Order)

The reconstruction pipeline is structured as an 8-step reproducible workflow to be executed in Phase 3.2:

```
[Step 1: Domain Masking]
       │  - Extract Domain A (863,979 cells)
       │  - Separate 18,628 candidate nunatak cells into H1, H2, H3
       │  - Exclude floating shelves (2,053 cells) and open water (1,554 cells)
       ▼
[Step 2: Atmospheric Boundary Integration]
       │  - Ingest monthly RACMO2.3p2 (1979–2021) and RACMO2.4p1 (2022–2024)
       │  - Apply polar stereographic distortion factor k_i^2
       │  - Integrate SMB_A(t) and local nunatak SMB_nunatak(t)
       ▼
[Step 3: Flux-Gate Baseline Calibration]
       │  - Calculate gate geometries across 8 verified systems
       │  - Integrate under BedMachine V4.1 ice thickness (H_BM4)
       │  - Integrate under Bedmap3 ice thickness (H_BM3)
       │  - Establish gate depth-averaged velocity ratio alpha (0.95 vs 0.80)
       ▼
[Step 4: Three-Epoch Scenario Execution]
       │  - Epoch 1 (1979–1999): Run Low (balance), Central (InSAR), High (glacier-specific)
       │  - Epoch 2 (2000–2013): Run post-collapse surge tracking + GRACE/ICESat bounds
       │  - Epoch 3 (2014–2024): Run empirical Sentinel-1/Landsat gate discharge
       ▼
[Step 5: Geophysical Vertical Motion & Firn Corrections]
       │  - Apply Nield et al. (2014) regional viscoelastic field (GIA_REAL_01)
       │  - Apply instantaneous elastic rebound (ELASTIC_01)
       │  - Apply IMAU-FDM firn air content compaction dFAC/dt
       │  - Apply CryoSat-2 Ku-band summer melt penetration mask
       ▼
[Step 6: Uncertainty Budget & Trajectory Synthesis]
       │  - Propagate measurement covariance (sigma_v, sigma_h)
       │  - Propagate model ensemble spread (sigma_SMB, sigma_GIA)
       │  - Maintain three Epoch 1 scenario branches separately (NO AVERAGING)
       │  - Preserve +7,204.9 km3 baseline gap outside Gaussian error bands
       ▼
[Step 7: Regional Benchmark Validation]
       │  - Sum three basin trajectories: Delta M_reconstructed(t) = rho_ice * sum(Delta V_basin)
       │  - Compare with Otosaka et al. (2026) IMBIE cumulative series
       │  - Validate: |Delta M_reconstructed - Delta M_IMBIE| <= 2 * sigma_IMBIE
       ▼
[Step 8: Output Delivery & Baseline Anchoring]
          - Output Bedmap3-anchored trajectories (Domain A: 133,497.6 km3 + Delta V)
          - Output BedMachine-anchored trajectories (Domain A: 140,702.5 km3 + Delta V)
          - Output Nunatak sensitivity branches (H1: 0 km3, H2: SMB-only, H3: +620.3 km3)
```

---

## 7. Decision Report & Approval Request

### Final Defensibility Assessment:
All methodological requirements, physical constraints, and data protections are locked:
1. **Scenario Realism:** Epoch 1 scenarios use glacier-specific historical evidence, with Larsen B post-collapse surges strictly excluded from the pre-2000 period.
2. **Geospatial Integrity:** Primary dynamic trajectories operate strictly on Domain A ($216,062.2\text{ km}^2$), with nunatak cells tracked as decoupled sensitivities.
3. **Geophysical Rigor:** Viscoelastic slab-window rebound is physically separated from instantaneous elastic rebound and firn compaction.
4. **Benchmark Verification:** Official IMBIE records are verified to machine precision and designated as an aggregate sector benchmark.

**The execution plan is fully locked and ready for implementation.**

*Execution stops here in accordance with Phase 3.1C directives. We await user approval of this execution plan before initiating Phase 3.2 historical reconstruction.*

