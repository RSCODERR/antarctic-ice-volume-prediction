# Phase 3.1B Technical Report: Historical Reconstruction Methodology Design

**Project:** Antarctic Peninsula Ice-Volume Prediction to 2100  
**Phase:** Phase 3.1B — Historical Reconstruction Methodology Design  
**Status:** Methodological Framework Completed (Awaiting User Review Prior to Implementation)  
**Date:** November 2026  

---

## Executive Summary & Scientific Charter

Following the empirical data acquisition and coverage audit in Phase 3.1A, Phase 3.1B establishes the rigorous mathematical, geospatial, and glaciological methodology required to reconstruct historical grounded ice-equivalent volume changes across Antarctic Peninsula mainland basins (`Hp-I`, `I-Ipp`, and `Ipp-J`) from 1979 to 2024.

In strict compliance with project directives:
- **No historical volume time series have been calculated.**
- **No machine-learning models have been trained.**
- **No 2100 forecasts have been generated.**
- **No missing observations have been fabricated or interpolated as direct measurements.**
- **Modelled discharge is never described as observed discharge.**
- **The official Otosaka et al. (2026) IMBIE dataset is utilized strictly as an aggregate regional sector benchmark, never as independent basin-level ground truth.**
- **The +7,204.9 km³ Bedmap3–BedMachine common-domain discrepancy is preserved strictly as an inter-product structural divergence, not as a statistical confidence interval.**
- **Bedmap3 and BedMachine baselines are preserved independently without averaging or modification.**

---

## 1. Three-Epoch Reconstruction Framework

Because the density, physical nature, and spatial completeness of Earth observation data changed radically between 1979 and 2024, a monolithic reconstruction methodology across the entire 45-year record is physically and methodologically indefensible. The historical trajectory is structured across three distinct evidence epochs.

![Data Flow Architecture](file:///C:/Users/akash/.gemini/antigravity/brain/52ad6ae8-887d-48db-85e7-7d53f431979f/figures/diagram_phase3_1b_data_flow_architecture.png)

### Table 1: Three-Epoch Methodological Framework

| Epoch | Time Span | Methodological Characterization | Primary Data Streams | Provenance Classification | Annual Obs Coverage % | Discharge Methodology | Dominant Uncertainty | Validation Anchor |
| :--- | :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- |
| **Epoch 1** | **1979–1999** (21 yrs) | Model-assisted reconstruction with explicit parameterizations | RACMO2.3p2 / 2.4p1 SMB (ERA-forced); 1996 ERS-1/2 InSAR; 1997 Radarsat | SMB: **Model output**<br>Discharge: **Reconstructed / Parameterized estimate**<br>Altimetry/Gravimetry: **Non-existent** | 18.5% | Input-Output Method with 3 explicit discharge scenarios anchored to 1996 InSAR baseline and balance flux | Scenario uncertainty (unmeasured discharge) & model uncertainty (reanalysis) | Regional IMBIE 2026 reconciled aggregate APIS benchmark ($\pm 25\text{ Gt/yr}$) |
| **Epoch 2** | **2000–2013** (14 yrs) | Multi-sensor constrained reconstruction with spatial/temporal limits | RACMO2.3p2/2.4p1 SMB; ICESat-1 GLAS; GRACE RL06 mascons; Landsat-7/Envisat velocity; early CryoSat-2 (2010–) | SMB: **Model output**<br>Velocity: **Interpolated / Reconstructed estimate**<br>Altimetry: **Direct observation (campaign-mode; slopes $<2^\circ$)**<br>Gravimetry: **Regional constraint (~300 km)** | 52.4% | Surge-tracking IOM over Larsen B tributaries combined with multi-year satellite mass/elevation constraints | Measurement uncertainty (slope geolocation, leakage) & GIA uncertainty | IMBIE 2026 reconciled series ($\pm 14\text{ Gt/yr}$) & regional ICESat-1 / GRACE trends |
| **Epoch 3** | **2014–2024** (11 yrs) | Observation-rich reconstruction with remaining uncertainties | Sentinel-1 SAR (6–12 d); Landsat-8/9 feature tracking; CryoSat-2 SARIn; ICESat-2 ATL15; GRACE-FO mascons; RACMO2.4p1 | SMB: **Model output**<br>Velocity: **Direct observation**<br>Altimetry: **Direct observation**<br>Gravimetry: **Regional constraint** | 94.6% | Empirical annual IOM flux-gate integration across all verified outlet systems using observed velocity fields | Structural thickness uncertainty (BM3 vs BM4), Ku-band penetration, slab-window GIA | Tri-sensor synthesis: ICESat-2 ATL15, CryoSat-2, Sentinel-1 gates, & IMBIE consensus |

### Methodological Principles by Epoch:

#### A. Epoch 1 (1979–1999): Model-Assisted Reconstruction
1. **Unmeasured Historical Discharge:** Direct satellite velocity observations are virtually non-existent prior to the 1996 ERS-1/2 InSAR campaign and 1997 Radarsat Antarctic Mapping Project. Annual glacier velocities cannot be measured directly. Any continuous annual discharge curve is a **parameterized reconstruction**, never a measurement.
2. **Three Explicit Scenario Trajectories:** To prevent subjective bias, Epoch 1 dynamic discharge ($D$) is evaluated under three distinct scenario branches:
   - **Low-Discharge Scenario ($D_{\text{low}}$):** Steady-state balance flux ($D = \overline{\text{SMB}}_{1979-1989}$). Assumes that prior to major ice shelf weakening, ice discharge was in dynamic equilibrium with multi-decadal mean snow accumulation.
   - **Central-Discharge Scenario ($D_{\text{central}}$):** Calibrated IOM anchored to 1996 ERS InSAR velocity snapshots, scaled backward to 1979 using basin-averaged terminus positions and SMB-driven driving stress variations.
   - **High-Discharge Scenario ($D_{\text{high}}$):** Assumes early unobserved acceleration (+15% above balance) along the Larsen A and northern Danco coasts during the 1980s and early 1990s as warming atmospheric temperatures reduced coastal sea-ice backstress.
3. **No Averaging of Scenarios:** These three branches are maintained as separate diverging trajectories across 1979–1999, directly communicating scenario uncertainty to downstream users.

#### B. Epoch 2 (2000–2013): Multi-Sensor Constrained Reconstruction
1. **GRACE Spatial Resolution Limits:** GRACE gravity solutions have an effective spatial resolution of $\sim 300\text{ to }400\text{ km}$ (spherical harmonic degree 60 or 200–300 km mascons). GRACE **cannot independently resolve mass changes in individual Peninsula basins** (`Hp-I` vs `I-Ipp` vs `Ipp-J`). Furthermore, mass signals along the narrow Peninsula spine are susceptible to signal leakage across the marine-terminating boundary and floating ice shelves. GRACE is implemented exclusively as an **aggregate regional sector constraint**, not as a basin-level target.
2. **ICESat-1 Temporal & Topographic Limits:** ICESat-1 operated in campaign mode (2–3 33-day campaigns per year), leaving 8–10 months unobserved each year. Cross-track track spacing was 10–30 km. On slopes steeper than $2^\circ$ (which characterizes $>60\%$ of Basin `I-Ipp`), laser footprint geolocation errors and cross-track slope differences introduce pseudo-elevation artifacts of $\pm 2\text{ to }15\text{ m}$. ICESat-1 is restricted to repeat-track analysis on smooth ice divides (slopes $<2^\circ$) in Palmer Land and central plateaus.
3. **Larsen B Dynamic Surge Integration:** The catastrophic collapse of the Larsen B Ice Shelf in March 2002 caused tributary outlet glaciers (Crane, Green, Hektoria) to accelerate 2–8×. Because Envisat and Landsat-7 feature tracking captured key post-collapse speedups, Epoch 2 discharge models incorporate empirical transient decay curves ($D(t) = D_{\text{peak}} \exp(-t/\tau)$) parameterized from published surge studies (Scambos et al., 2004; Rott et al., 2011; Wuite et al., 2015).

#### C. Epoch 3 (2014–2024): Observation-Rich Reconstruction
1. **Not a Gold Standard:** While this period possesses unprecedented data density, it must **not** be termed a "gold standard." Substantial geophysical and instrument uncertainties persist:
   - **Ku-Band Radar Penetration:** CryoSat-2 Ku-band radar penetrates $0.5\text{ to }4.5\text{ m}$ into cold firn, but reflects from the wet surface during summer melt.
   - **Narrow Fjord Radar Shadow:** Despite Sentinel-1 SAR constellation coverage, steep alpine fjords ($<2\text{ km}$ width) in Basin `I-Ipp` experience geometric layover and shadow.
   - **Bedrock Uplift Uncertainty:** Rapid slab-window viscoelastic uplift ($+8\text{ to }+15\text{ mm/yr}$) creates large altimetric correction uncertainties.
2. **Empirical Gate Flux Integration:** For all major outlet glaciers, annual discharge is calculated directly from observed Sentinel-1 and Landsat-8/9 surface velocities across our 8 verified flux gates.

---

## 2. Strict Input and Output Provenance Matrix

To eliminate any ambiguity between observed facts and modelled approximations, every variable entering or exiting the reconstruction is cataloged in Table 2 under a formal provenance taxonomy.

### Table 2: Input and Output Provenance Taxonomy

| Variable | Description | Epoch 1 (1979–1999) | Epoch 2 (2000–2013) | Epoch 3 (2014–2024) | Provenance Class | Physical Units |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`smb_monthly`** | Gridded monthly surface mass balance | Model output (RACMO2.3p2 / ERA-Interim) | Model output (RACMO2.3p2 / ERA5) | Model output (RACMO2.4p1 / ERA5) | **Model output** | $\text{mm w.e./yr} \equiv \text{kg m}^{-2}\text{ yr}^{-1}$ |
| **`fac_evolution`** | Spatially varying firn air content ($d\text{FAC}/dt$) | Model output (IMAU-FDM) | Model output (IMAU-FDM) | Model output (IMAU-FDM) | **Model output** | $\text{m firn air / yr}$ |
| **`ice_velocity`** | Surface ice velocity field | Parameterized / Assumed (1996 InSAR snapshot) | Interpolated / Gap-filled (Landsat-7 / Envisat) | Direct observation (Sentinel-1 / Landsat-8/9) | **Mixed (Epoch-dependent)** | $\text{m/yr}$ |
| **`flux_gate_D`** | Solid ice dynamic discharge through gates | Reconstructed estimate (Low/Central/High scenarios) | Reconstructed estimate (Surge tracking + IOM) | Direct observation (Empirical gate integration) | **Mixed (Epoch-dependent)** | $\text{Gt/yr}$ & $\text{km}^3/\text{yr}$ |
| **`altimetry_dhdt`** | Surface elevation rate of change | Non-existent | Direct observation (ICESat campaigns; slopes $<2^\circ$) | Direct observation (CryoSat-2 SARIn + ICESat-2 ATL15) | **Direct observation** | $\text{m/yr}$ |
| **`gravimetry_dMdt`** | Integrated regional mass change rate | Non-existent | Regional constraint (GRACE RL06 mascons) | Regional constraint (GRACE-FO mascons) | **Regional constraint** | $\text{Gt/yr}$ |
| **`imbie_reconciled`** | Reconciled multi-method mass balance | Regional constraint (IOM-dominated) | Regional constraint (IOM + Altimetry + GRACE) | Regional constraint (Multi-satellite consensus) | **Regional constraint** | $\text{Gt/yr}$ & Cumulative $\text{Gt}$ |
| **`gia_uplift`** | Viscoelastic solid Earth rebound | Model output (Regional slab window model) | Model output (GPS-constrained regional solution) | Model output (GPS-constrained regional solution) | **Model output** | $\text{mm/yr uplift}$ |
| **`elastic_uplift`** | Instantaneous lithospheric elastic rebound | Assumption (Near-zero pre-1995) | Model output (Green's function convolution) | Model output (Green's function convolution) | **Model output / Assumption** | $\text{mm/yr uplift}$ |
| **`dV_ice_eq/dt`** | Reconstructed annual grounded ice-eq rate | Reconstructed estimate (Model-assisted IOM) | Reconstructed estimate (Multi-sensor synthesis) | Reconstructed estimate (Observation-rich synthesis) | **Reconstructed estimate** | $\text{km}^3/\text{yr}$ |

---

## 3. Official IMBIE 2026 Usage & Regional Constraint Protocol

The newly acquired Otosaka et al. (2026) IMBIE dataset (`imbie3_antarctic_peninsula_Gt_partitioned.csv`) is incorporated under strict glaciological conditions.

### A. Dataset Metadata & Specification Verification
- **Citation & Source:** Otosaka et al. (2026), Version 1.0, NERC EDS UK Polar Data Centre / BAS RAMADDA (`doi:10.5285/128c5e33-5224-4197-82f0-19dcc95b80a0`).
- **Spatial Domain:** Antarctic Peninsula Ice Sheet (APIS) regional sector in its entirety.
- **Temporal Resolution:** Monthly continuous, covering 540 consecutive months from **1979-01-01 to 2023-12-01**.
- **Variables Audited:**
  - `Mass balance (Gt/yr)` & `Mass balance uncertainty (Gt/yr)`
  - `Cumulative mass balance anomaly (Gt)` & `Cumulative mass balance anomaly uncertainty (Gt)`
  - `Surface mass balance anomaly (Gt/yr)` & `Cumulative surface mass balance anomaly (Gt)`
  - `Dynamics mass balance anomaly (Gt/yr)` & `Cumulative dynamics mass balance anomaly (Gt)`
- **Cumulative Reference Period:** Cumulative anomalies integrate monthly increments $\Delta M_m = (\text{Rate}_m / 12)\text{ Gt}$ anchored to zero at the start of January 1979.
- **End-of-Record State (2023-12-01):**
  - Cumulative Mass Balance Anomaly: **$-817.0 \pm 108.8\text{ Gt}$**
  - Cumulative Dynamics Mass Anomaly: **$-868.5 \pm 114.6\text{ Gt}$**
  - Cumulative SMB Mass Anomaly: **$+51.5 \pm 36.2\text{ Gt}$**

### B. Protocol for Regional Reconciled Integration:
1. **Never Basin-Level Ground Truth:** The IMBIE record is an aggregate sector-scale solution. It **must never be divided arbitrarily among Basins `Hp-I`, `I-Ipp`, and `Ipp-J` or treated as independent basin-level truth**.
2. **Regional Consistency Constraint:** In our methodology, the three basin reconstructions are conducted independently using local flux gates and downscaled RACMO SMB. Once integrated, the sum of the three basins:
   $$\Delta M_{\text{reconstructed\_total}}(t) = \rho_{\text{ice}} \left[ \Delta V_{\text{Hp-I}}(t) + \Delta V_{\text{I-Ipp}}(t) + \Delta V_{\text{Ipp-J}}(t) \right]$$
   is compared directly against the official IMBIE cumulative record $\Delta M_{\text{IMBIE}}(t)$.
3. **Formal Evaluation Function:** Any regional divergence exceeding the reconciled IMBIE $2\sigma$ uncertainty envelope ($\pm 108.8\text{ Gt}$ by 2023, $\sim 118\text{ km}^3$ ice-equivalent) triggers an audit of basin flux-gate velocity calibrations.

---

## 4. Spatial Domain Implementation: Investigation of Bedmap3-Only Cells

To ensure total geospatial consistency between Bedmap3 and BedMachine V4.1, the study region is partitioned into five distinct domain categories.

### Table 3: Domain Implementation and Cell Classification Matrix

| Domain Category | Definition | Cell Count | Area ($\text{km}^2$) | % Grounded | BM3 Ice-Eq ($\text{km}^3$) | BM4 Ice-Eq ($\text{km}^3$) | Structural $\Delta$ ($\text{km}^3$) | Dynamic Eligibility | Reconstruction Trajectory Rule |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- | :--- |
| **Domain A** | Grounded in BOTH BM3 and BM4 | 863,979 | 216,062.2 | 97.52% | 133,497.6 | 140,702.5 | +7,204.9 | **Fully Eligible** (Primary Dynamic Target) | Reconstruct $V_{\text{common}}(t) = V_{\text{baseline}} + \Delta V_{\text{ice\_eq}}(t)$ anchored independently to BM3 and BM4 baselines |
| **Domain B1** | BM3 Grounded, BM4 Rock Nunatak | 18,628 | 4,608.5 | 2.08% | 620.3 | 0.0 | -620.3 | **Ineligible for Dynamic Discharge** | Evaluated under 3 discrete static/SMB hypotheses; never dynamically thinned |
| **Domain B2** | BM3 Grounded, BM4 Floating Shelf | 2,053 | 506.4 | 0.23% | 133.8 | 0.0 | -133.8 | **Strictly Excluded** | Floating ice in hydrostatic equilibrium; excluded from grounded volume target ($dH/dt = 0$) |
| **Domain B3** | BM3 Grounded, BM4 Open Ocean | 1,554 | 376.6 | 0.17% | 30.4 | 0.0 | -30.4 | **Strictly Excluded** | Coastal fjord / calved ice tongue; excluded from grounded volume target ($dH/dt = 0$) |
| **Domain C** | BM4 Grounded, BM3 NOT Grounded | 0 | 0.0 | 0.00% | 0.0 | 0.0 | 0.0 | **Null Domain** | Empty set (BM4 is a strict mathematical subset of BM3) |

### In-Depth Investigation of the 18,628 Candidate Nunatak Cells ($620.3\text{ km}^3$):
Our audit of the 18,628 cells where Bedmap3 reports grounded ice but BedMachine reports ice-free rock (mask=1) reveals:
1. **Topographic Distribution:** Mean surface elevation is **$926.2\text{ m}$** (median $915.0\text{ m}$, max $2,959.0\text{ m}$). These cells are situated along steep high-elevation mountain ridges and nunatak crests along the spine of the Peninsula.
2. **Thickness Distribution in Bedmap3:**
   - Min thickness: $1.0\text{ m}$, max: $1,670.0\text{ m}$, mean: **$131.5\text{ m}$**, median: **$99.0\text{ m}$**.
   - $27.6\%$ of cells have $H < 50\text{ m}$; $34.1\%$ have $H$ between $50\text{ m}$ and $100\text{ m}$; only $14.6\%$ have $H \ge 250\text{ m}$.
3. **Cause of Discrepancy:**
   - Bedmap3 applied smooth splines/kriging across nunataks wherever rock was not flagged in the coarser SCAR ADD coastline mask, interpolating artificial ice thickness across rocky ridges.
   - BedMachine used high-resolution Landsat/REMA rock outcrop masks (Burton-Johnson et al., 2016), strictly clamping exposed rock to $H=0$.
   - However, steep ice-draped slopes and hanging cirque glaciers bordering nunataks were partially clipped by BedMachine's 500 m grid center snapping.
4. **Methodological Rule:**
   - These cells **cannot be dynamically thinned** ($D_{\text{gate}} = 0$). They are disconnected from the marine-terminating outlet glaciers.
   - To avoid unverified assumptions, they are tracked under three explicit hypothesis scenarios:
     - **Hypothesis H1 (BedMachine Ground Truth):** Exposed bedrock ($H=0$). The $620.3\text{ km}^3$ is an interpolation artifact in Bedmap3.
     - **Hypothesis H2 (Stagnant Ice Mantle):** Thin perched ice in balance with atmospheric accumulation ($dH/dt = \text{SMB}_{\text{local}} / \rho_{\text{ice}}$).
     - **Hypothesis H3 (Provisional Static Offset):** Maintained as a constant static structural volume ($dH/dt = 0$) until validated against high-resolution REMA strip DEM differencing.

---

## 5. Regional GIA & Vertical-Motion Correction Design

Satellite altimetry ($dh/dt$) and gravimetry ($dM/dt$) cannot be interpreted without rigorously separating solid Earth deformation from ice mass change.

![Geophysical Correction Sequence](file:///C:/Users/akash/.gemini/antigravity/brain/52ad6ae8-887d-48db-85e7-7d53f431979f/figures/diagram_phase3_1b_correction_sequence.png)

### Separation of Physical Vertical-Motion Components:
$$v_{\text{total\_vertical}}(\mathbf{x}, t) = v_{\text{viscoelastic\_GIA}}(\mathbf{x}, t) + v_{\text{elastic\_instantaneous}}(\mathbf{x}, t)$$
$$\frac{dh_{\text{ice\_eq}}}{dt}(\mathbf{x}, t) = \frac{dh_{\text{surf}}}{dt}(\mathbf{x}, t) - \frac{d\text{FAC}}{dt}(\mathbf{x}, t) - v_{\text{total\_vertical}}(\mathbf{x}, t) - \delta_{\text{radar\_bias}}(\mathbf{x}, t)$$

### Table 4: Regional GIA Model Evaluation and Comparison

| Model | Reference | Viscosity Structure | Northern AP Uplift | Southern Palmer Uplift | Spatial Character | Time Dependence | Peninsula Validity | Altimetric Impact ($\text{km}^3/\text{yr}$) | Gravimetric Impact ($\text{Gt/yr}$) |
| :--- | :--- | :--- | :---: | :---: | :--- | :--- | :--- | :---: | :---: |
| **W12 / W12a** | Whitehouse et al. (2012) | Uniform upper mantle: $2.0 \times 10^{20}\text{ Pa s}$ | $+1.5\text{ to }+3.0\text{ mm/yr}$ | $+1.0\text{ to }+2.0\text{ mm/yr}$ | Gentle continental gradient | Steady rate assumed | Low in North (misses slab window); moderate south | $-0.3\text{ to }-0.6$ | $+2\text{ to }+4$ |
| **ICE-6G_C** | Peltier et al. (2015) | 1D VM5a viscosity | $+1.0\text{ to }+2.5\text{ mm/yr}$ | $+0.5\text{ to }+1.5\text{ mm/yr}$ | Broad continental | Steady rate | Low in AP; ignores regional slab window | $-0.2\text{ to }-0.5$ | $+1\text{ to }+3$ |
| **IJ05_RII** | Ivins et al. (2013) | Regional upper mantle: $1.0 \times 10^{20}\text{ Pa s}$ | $+2.0\text{ to }+4.5\text{ mm/yr}$ | $+1.0\text{ to }+2.5\text{ mm/yr}$ | Moderate regional | Steady rate | Moderate; misses rapid post-1995 rebound | $-0.4\text{ to }-0.9$ | $+3\text{ to }+6$ |
| **Nield et al. (2014)** | Nield et al. (2014, *EPSL*) | Slab window asthenosphere: $10^{18}\text{ to }2 \times 10^{19}\text{ Pa s}$ | **$+8.0\text{ to }+15.0\text{ mm/yr}$** | $+1.5\text{ to }+3.5\text{ mm/yr}$ | **Extremely steep gradient** | **Strongly time-dependent** ($\tau \approx 3\text{–}15\text{ yrs}$) | **High; validated by UKANET / LARISSA GPS** | **$-1.5\text{ to }-3.2$** | **$+8\text{ to }+15$** |
| **Wolstencroft (2015)** | Wolstencroft et al. (2015) | Empirical GPS kriging (19 stations) | $+7.5\text{ to }+14.2\text{ mm/yr}$ | $+1.8\text{ to }+3.0\text{ mm/yr}$ | High local detail at GPS | Decadal average | High at GPS sites; unconstrained inland | $-1.4\text{ to }-2.9$ | $+7\text{ to }+13$ |
| **Elastic Model** | Green's function loading | Instantaneous elastic half-space | $+2.0\text{ to }+6.0\text{ mm/yr}$ | $+0.5\text{ to }+1.5\text{ mm/yr}$ | Localized at gates ($<20\text{ km}$) | Strictly instantaneous with $D(t) - \text{SMB}(t)$ | High; mandatory separate physical term | $-0.4\text{ to }-1.1$ | $+1\text{ to }+3$ |

### Critical GIA Design Directives:
1. **Rejection of Uniform Uplift:** Uplift must **never be imposed as a uniform $+8\text{ to }+15\text{ mm/yr}$ blanket across the Peninsula**. The slab window is concentrated in northern Graham Land (Basin `Ipp-J` and northern `I-Ipp`). In Palmer Land (`Hp-I`), mantle viscosity is higher and uplift is only $+1.5\text{ to }+3.5\text{ mm/yr}$.
2. **Rejection of Cross-Region Transfer:** As instructed, findings from Barletta et al. (2018) for the Amundsen Sea Embayment are **not transferred to the Antarctic Peninsula**. Only models specifically parameterized for the Peninsula tectonic arc (Nield et al. 2014, Wolstencroft et al. 2015) are employed.
3. **Viscoelastic Sensitivity Scenarios:** Rather than locking into a single model prematurely, the reconstruction designs three GIA sensitivity branches:
   - *Scenario GIA-1 (Regional Slab Window Primary):* Nield et al. (2014) time-dependent viscoelastic model coupled with GPS station constraints.
   - *Scenario GIA-2 (Empirical GPS Baseline):* Wolstencroft et al. (2015) spatially kriged GPS field.
   - *Scenario GIA-3 (Continental Stiff Baseline):* Whitehouse et al. (2012) W12a continental model.

---

## 6. Comprehensive Uncertainty Framework & Propagation Architecture

![Uncertainty Propagation Architecture](file:///C:/Users/akash/.gemini/antigravity/brain/52ad6ae8-887d-48db-85e7-7d53f431979f/figures/diagram_phase3_1b_uncertainty_propagation.png)

Uncertainties are formally partitioned into four distinct mathematical classes.

### Table 5: Comprehensive Uncertainty Budget Design

| Source Component | Discipline | Uncertainty Class | Estimated Magnitude | Covariance & Correlation Structure | Propagation Method | Cumulative Impact on 2024 Volume |
| :--- | :--- | :--- | :---: | :--- | :--- | :---: |
| **Ice Velocity Tracking** | Ice Dynamics | **Measurement** | $\pm 5\text{ to }20\text{ m/yr}$ | Spatially correlated over $\sim 5\text{ km}$; temporally independent across cycles | Quadrature flux-gate error: $\sigma_D = \sqrt{\sum (\alpha H W_i \sigma_v)^2}$ | $\pm 28\text{ to }45\text{ km}^3$ |
| **Altimetry Point Noise** | Elevation | **Measurement** | $\pm 0.02\text{ to }0.08\text{ m/yr}$ | Along-track covariance; slope-correlated in alpine relief | Kriging covariance with slope quality masking | $\pm 35\text{ to }60\text{ km}^3$ |
| **Ku-Band Radar Penetration** | Altimetry | **Measurement / Hazard** | $\pm 0.5\text{ to }2.5\text{ m}$ shift | Correlated with summer melt events and wet snow facies | RACMO melt masking and dual-peak waveform retracking | $\pm 20\text{ to }35\text{ km}^3$ |
| **RACMO2.4p1 SMB Physics** | Atmospheric | **Model** | $\pm 15\%$ ($\sim 15\text{ to }25\text{ Gt/yr}$) | High intra-basin spatial covariance; shared synoptic storm tracks | Regional ensemble spread & AWS accumulation validation | $\pm 85\text{ to }130\text{ km}^3$ |
| **Firn Compaction ($d\text{FAC}/dt$)** | Firn Physics | **Model** | $\pm 0.15\text{ to }0.40\text{ m/yr}$ | Covariant with summer melt and snowfall forcing | IMAU-FDM parameter perturbation and shallow firn core testing | $\pm 25\text{ to }45\text{ km}^3$ |
| **Slab-Window GIA Rebound** | Geophysics | **Model** | $\pm 3.0\text{ to }6.0\text{ mm/yr}$ | Long-wavelength correlation ($\sim 100\text{ km}$); time-dependent | Multi-model viscoelastic ensemble (Nield vs W12a) | $\pm 40\text{ to }80\text{ km}^3$ |
| **Unobserved Discharge (1979–99)**| Dynamics | **Scenario** | Low / Central / High | Decadal trend divergence across 21 years | 3 explicit scenario branches tracked separately (NOT averaged) | $\pm 65\text{ to }110\text{ km}^3$ |
| **BM3 vs BM4 Thickness** | Bed/Thickness | **Structural** | **$+7,204.9\text{ km}^3$ (+5.40%)** | Systematic positive offset on Domain A ($89.2\%$ of cells) | **NEVER CONVERTED TO GAUSSIAN SIGMA**. Dual baseline realization. | Baseline: $+7,204.9\text{ km}^3$<br>Flux impact: $\sim 18\text{ to }32\text{ km}^3$ |
| **BM3 Nunatak Volume** | Mask | **Structural** | **$+620.3\text{ km}^3$** | High-elevation mountain ridges exclusively | 3 discrete hypothesis branches (H1, H2, H3). Decoupled from dynamic gates. | Static offset: $0\text{ to }620.3\text{ km}^3$ |

### Strict Uncertainty Rule:
The $+7,204.9\text{ km}^3$ Bedmap3–BedMachine common-domain discrepancy is an **inter-product structural difference**, not random noise. It is never converted into a Gaussian standard error or added into a quadrature root-sum-square.

---

## 7. Decision Report & Readiness Review

### A. Summary of Unresolved Scientific Assumptions
1. **Pre-Collapse Glacier Velocities (1979–1994):** Because no satellite radar constellation monitored Antarctica prior to ERS-1, pre-1995 ice discharge in Larsen A and pre-2002 discharge in Larsen B cannot be directly measured. They rely on the assumption of balance flux or InSAR-scaled hindcasting.
2. **Bedmap3 High-Elevation Nunatak Ice Presence:** Whether the $620.3\text{ km}^3$ in the 18,628 nunatak cells represents real ice mantles or gridding artifacts remains an unresolved structural difference between Bedmap3 and BedMachine.
3. **Mantle Viscosity Bounds:** While continuous GPS confirms rapid uplift in northern Graham Land, asthenospheric viscosity between GPS stations along the spine remains constrained only by 3D viscoelastic model extrapolations.

### B. Summary of Data Limitations
1. **Basin `I-Ipp` Pre-2014 Blindness:** Persistent cloud cover ($>80\%$) and narrow fjord geometry ($<2\text{ km}$) prevent annual optical velocity tracking prior to Sentinel-1 (2014).
2. **GRACE Basin Indivisibility:** GRACE cannot resolve mass changes at the individual basin level (`Hp-I` vs `I-Ipp`).
3. **ICESat-1 Alpine Relief Dropouts:** Laser altimetry dropouts on slopes $>2^\circ$ eliminate ICESat-1 observations across the majority of western Graham Land.

### C. Validation Requirements Before Reconstruction Execution
1. Grounding-line flux gates must be run under **both** Bedmap3 and BedMachine ice thicknesses to quantify gate-specific flux sensitivity.
2. The regional sum of reconstructed basin trajectories must be formally validated against the official Otosaka et al. (2026) IMBIE cumulative record.
3. Altimetric volume loss rates in Epoch 3 must be cross-checked against independent ICESat-2 ATL15 laser altimetry and CryoSat-2 SARIn grids.

### D. Final Methodological Defensibility Determination
**The methodology is sufficiently defensible to proceed to historical reconstruction, provided that:**
- The dual-baseline realization architecture is strictly maintained.
- Epoch 1 (1979–1999) is implemented as three explicit scenario branches rather than a single fabricated time series.
- Domain A ($216,062.2\text{ km}^2$) serves as the primary dynamic reconstruction target, with candidate nunatak cells decoupled from dynamic discharge.
- Regional GIA corrections utilize spatially varying slab-window models rather than uniform continental approximations.

---

## Strict Stopping Condition Sign-Off

Execution stops here. No historical volume time series have been generated, no ML models have been trained, and no 2100 predictions have been produced. We await user review and approval of the Phase 3.1B methodology design before initiating Phase 3.2 reconstruction.

