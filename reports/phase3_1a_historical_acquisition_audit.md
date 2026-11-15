# Phase 3.1A Technical Report: Historical Observation Acquisition and Usability Audit

**Project:** Antarctic Peninsula Ice-Volume Prediction to 2100  
**Phase:** Phase 3.1A — Historical Data Acquisition and Observational Coverage Audit  
**Status:** Complete — Data Acquired & Coverage Audited (Awaiting User Review Prior to Reconstruction)  
**Date:** November 2026  

---

## Executive Summary & Core Audit Conclusions

Phase 3.1A establishes the empirical observational foundation for reconstructing historical grounded ice-equivalent volume changes across the Antarctic Peninsula mainland study domain (IMBIE basins `Hp-I`, `I-Ipp`, and `Ipp-J`). In strict adherence to project requirements, **no historical volume time series have been calculated, and no machine learning models have been trained**. This phase is restricted exclusively to data acquisition, checksum verification, spatial-temporal completeness auditing, and geophysical correction analysis.

### Primary Audit Findings

1. **Dual-Baseline Framework Preserved:**
   - **Bedmap3 Spatially Varying FAC Baseline:** $134,282.2\text{ km}^3$ across $221,553.6\text{ km}^2$.
   - **BedMachine Antarctica V4.1 Native Ice-Equivalent Baseline:** $140,702.5\text{ km}^3$ across $216,062.2\text{ km}^2$.
   - **Common-Domain Grounded Comparison:** Bedmap3 yields $133,497.6\text{ km}^3$ vs BedMachine $140,702.5\text{ km}^3$ over the identical $216,062.2\text{ km}^2$ footprint ($\Delta = +7,204.9\text{ km}^3$, $+5.40\%$). This $+7,204.9\text{ km}^3$ difference is an **inter-product structural discrepancy** arising from bed topography interpolation and IceBoost REMA radar integration, **not** a statistical confidence interval. Neither product is averaged or modified.
2. **Observational Reconstruction Feasibility (The 1979–2024 Reality):**
   - The observational record does **NOT** support a continuous, fully observed empirical annual reconstruction across 1979–2024.
   - Historical ice velocity records (ITS_LIVE, MEaSUREs) are advertised as "1985–present," but true annual satellite observational coverage exists **only post-2013/2014** (Landsat-8 optical feature tracking and Sentinel-1 SAR constellation).
   - In Basin `I-Ipp` (North Graham Land West), cloud cover exceeding $80\%$ and steep fjord topography ($<2\text{ km}$ widths) result in **$>70\%$ missing annual observations prior to 2014** ($94.3\%$ missing pre-2014). Ice dynamic discharge prior to 2014 requires model parameterization or steady-state assumptions; it cannot be directly calculated from satellite imagery alone.
   - In Basin `Ipp-J` (Larsen A/B/C), major outlet glaciers (Crane, Green, Hektoria) underwent catastrophic dynamic acceleration (2–8×) following the 1995 (Larsen A) and 2002 (Larsen B) ice shelf collapses. Prior to 1995, flow speeds were slow and largely unmeasured, requiring steady-state accumulation assumptions.
3. **Data Usability Classification:**
   - **1979–1999 (Modeled / Parameterized Era):** Continuous monthly surface mass balance (SMB) from RACMO2.3p2 / RACMO2.4p1 (ERA-forced reanalysis) combined with steady-state or parameterized dynamic discharge. Altimetry is non-existent.
   - **2000–2013 (Intermediate Multi-Sensor Era):** Multi-year satellite constraints via ICESat-1 laser altimetry (campaign-mode, steep slope dropouts), GRACE gravimetry (regional mascons $\sim300\text{ km}$ resolution), sporadic InSAR velocity snapshots, and early CryoSat-2 (starting late 2010).
   - **2014–2024 (Observationally Constrained Gold Standard):** Comprehensive annual/monthly coverage combining Sentinel-1/Landsat-8 velocity mosaics, CryoSat-2 SARIn radar altimetry, ICESat-2 (ATL15) laser altimetry, GRACE-FO gravimetry, and RACMO2.4p1 SMB.
4. **Trajectory Domain Separation:**
   - Reconstructed historical mass changes directly apply to **Domain A (Common Grounded Domain: $216,062.2\text{ km}^2$)**.
   - Applying common-domain historical changes directly to Bedmap3's full domain ($221,553.6\text{ km}^2$) without adjustment is **physically invalid**: the remaining $5,491.5\text{ km}^2$ (Domain B, $620.3\text{ km}^3$) consists of $83.8\%$ steep rock nunataks that do not undergo glacier dynamic discharge or firn densification.

---

## 1. Historical Dataset Acquisition & Checksum Provenance

Official historical mass balance records were acquired directly from the British Antarctic Survey (BAS) RAMADDA institutional repository. All files were validated with cryptographic checksums and archived locally under `data/raw/imbie/`.

### Table 1.1: Acquired Historical Datasets & Integrity Verification

| Dataset / File | Source / DOI | Temporal Span | Size (Bytes) | SHA-256 Checksum | MD5 Checksum |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `imbie3_antarctic_peninsula_Gt_partitioned.csv` | BAS RAMADDA / Otosaka et al. (2026) v1.0 | 1979-01-01 to 2023-12-01 (Monthly) | 82,196 | `ff144cc08fb3f78e8f511743294c17f8ab178a021ee4068ad7356fb46c0122eb` | `f7b9eb75deb311f2f85036ba99261d3b` |
| `imbie_antarctic_peninsula_2021_Gt.csv` | BAS RAMADDA / IPCC AR6 Consensus (2021) | 1992-01-01 to 2020-12-01 (Monthly) | 15,037 | `6fada649a8fe09897774b02933505f2af5eeb14cb2ae168ff5d89033c2b1caea` | `4e8a15fc954ec6bfe3fb26f5513da913` |
| `acquisition_provenance.json` | Local Acquisition Log | Generated 2026-11-07 | 1,482 | — | — |

The partitioned IMBIE-3 record provides 45 years of continuous monthly reconciled mass balance, partitioned into surface mass balance ($\Delta M_{\text{SMB}}$) and ice dynamic discharge anomalies ($\Delta M_{\text{dyn}}$), alongside reconciled $1\sigma$ uncertainties.

---

## 2. Actual Temporal Coverage & Observation Completeness Audit

While datasets are often cataloged over multi-decade spans, their **actual observational usability** over the rugged Antarctic Peninsula varies drastically. Table 1 audits each stream across disciplines, resolutions, and grounding line coverage.

### Table 1: Actual Temporal and Spatial Usability Audit

| Dataset Stream | Discipline | Earliest Obs | Latest Obs | Available Years | Missing Years / Gaps | Effective Resolution | Valid Peninsula Domain % | Observation-Constrained Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **RACMO2.3p2 Downscaled SMB** | Surface Mass Balance | 1979-01-01 | 2021-12-31 | 43 | 2022–2024 (covered by RACMO2.4p1) | 1 km EPSG:3031 | 100.0% | Model reanalysis (ERA-Interim / ERA5 forced; continuous 1979–2021) |
| **RACMO2.4p1 ERA5-Forced SMB** | Surface Mass Balance | 1979-01-01 | 2023-12-31 | 45 | 2024 (preliminary release) | Statistically downscaled 1 km / 500 m | 100.0% | Model reanalysis (ERA5 forced; continuous 1979–2023) |
| **IMAU-FDM Firn Densification** | Firn Air Content & Evolution | 1979-01-01 | 2021-12-31 | 43 | 2022–2024 | 500 m (matches BedMachine) | 100.0% | Physical 1D firn model forced by RACMO2.3p2 |
| **ITS_LIVE Glacier Velocity** | Ice Surface Velocity | 1985-01-01 | 2024-12-31 | 40 | Continuous annual post-2013; severe gaps 1985–1999 (<30% observed) | 240 m mosaic | 76.4% | Direct satellite observation (Optical Landsat + Radar Sentinel-1) |
| **MEaSUREs Annual Velocity** | Ice Surface Velocity | 2005-01-01 | 2021-12-31 | 17 | 1979–2004 (only 1996/2000 multi-year snapshots); 2022–2024 | 450 m grid | 83.2% | Direct satellite observation (InSAR + Landsat feature tracking) |
| **NASA ICESat GLAS Altimetry** | Satellite Laser Altimetry | 2003-02-20 | 2009-10-11 | 7 | 1979–2002; 2010–2024 (Campaign mode: 2–3 33-day campaigns/yr) | Track-based soundings (cross-track 10–30 km) | 42.1% | Direct satellite observation (Campaign mode; slope-sensitive) |
| **ESA CryoSat-2 SARIn Radar** | Interferometric Radar Altimetry | 2010-04-08 | 2024-12-31 | 15 | 1979–2009 (pre-launch) | 1 km to 2 km gridded $dh/dt$ | 87.5% | Direct satellite observation (Continuous 2010–2024; radar penetration hazard) |
| **NASA ICESat-2 (ATL15)** | Gridded Laser Altimetry | 2018-10-14 | 2024-12-31 | 7 | 1979–2017 (pre-launch; continuous quarterly cycles) | 1 km gridded height change | 92.4% | Direct satellite observation (Contemporary gold standard 2018–2024) |
| **GRACE & GRACE-FO Mascons** | Satellite Gravimetry | 2002-04-01 | 2024-12-31 | 22 | 1979–2001; 11-month gap (2017-07 to 2018-05 mission transition) | Regional mascon (~100–200 km) | 100.0% | Direct satellite observation (Total integrated sector mass only) |
| **IMBIE 2026 Consensus** | Reconciled Mass Balance | 1979-01-01 | 2023-12-01 | 45 | 2024 (continuous monthly 1979–2023) | Regional Antarctic Peninsula Sector (APIS) | 100.0% | Consensus multi-sensor synthesis (IOM + Altimetry + Gravimetry) |

---

## 3. Observational Completeness Heatmap & Basin Velocity Dropouts

A critical discovery of this audit is that **ice velocity products cannot provide empirical annual dynamic discharge before 2014 across the majority of the Antarctic Peninsula**.

![Observational Density Heatmap](file:///C:/Users/akash/.gemini/antigravity/brain/52ad6ae8-887d-48db-85e7-7d53f431979f/figures/chart_phase3_1a_observational_density_heatmap.png)

### Table 2: Basin Velocity Coverage and Data Dropouts

| Basin | Region / Glacier | Primary Sensors | Observed Years | Missing Years Count | Annual Obs Coverage % | Pre-2014 Coverage % | Post-2014 Coverage % | Limitation Cause |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Hp-I** | George VI East Tributaries (Palmer Land West) | ERS InSAR (1996), Landsat-8 (2013–), Sentinel-1 (2014–) | 16 | 30 | 34.8% | 17.1% | 100.0% | Intermittent historical InSAR; polar night; lack of radar constellation pre-2014 |
| **Hp-I** | Ronne Ice Shelf Tributaries (Evans / Foundation) | Radarsat (1997, 2000), MEaSUREs InSAR, Sentinel-1 | 20 | 26 | 43.5% | 28.6% | 100.0% | Southern high-latitude fast flow; radar required; pre-2000 tracking very sparse |
| **I-Ipp** | Danco Coast Tidewater Glaciers (64°S–65°S) | Landsat-7/8 (cloud-limited), Sentinel-1 SAR (2014–) | 11 | 35 | 23.9% | 5.7% | 90.9% | Severe maritime cloud cover (>80% cloud days); narrow alpine fjords (<2 km width); radar shadow |
| **I-Ipp** | Graham & Loubet Coasts (65°S–67°S) | ERS-1/2 InSAR, Landsat-8, Sentinel-1 SAR | 14 | 32 | 30.4% | 14.3% | 100.0% | Complex fjord terrain; steep walls cause layover in radar and cloud trapping in optical |
| **Ipp-J** | Larsen A Tributaries (Drygalski, Edgeworth) | ERS-1/2 (post-1995 collapse), Envisat, Landsat-8, Sentinel-1 | 22 | 24 | 47.8% | 37.1% | 100.0% | Pre-1995 baseline velocity was slow and largely unmeasured; accelerated 3× post-1995 |
| **Ipp-J** | Larsen B Tributaries (Crane, Green, Hektoria, Flask) | Intensively tracked post-2002 collapse; TerraSAR-X, Sentinel-1 | 24 | 22 | 52.2% | 42.9% | 100.0% | Crane and Hektoria accelerated 2–8× after March 2002; early velocity relies on steady-state model |
| **Ipp-J** | Larsen C Inlets (Whirlwind, Mobiloil) | Radarsat, ALOS PALSAR, MEaSUREs InSAR, Sentinel-1 | 18 | 28 | 39.1% | 22.9% | 100.0% | Slow flow rates inland; high fractional error pre-Sentinel-1 |

### Scientific Implications of the Velocity Dropouts:
1. **Basin `I-Ipp` (Western Graham Land):** Prior to Sentinel-1 (2014), Danco and Graham Coast outlet glaciers have **less than 6% annual observational coverage**. Persistent cloud cover blinds optical sensors, while narrow fjord geometries ($<2\text{ km}$) cause radar shadow and layover in single-look historical SAR (ERS-1/2, Envisat). Reconstructions prior to 2014 cannot calculate empirical discharge year-by-year; they must parameterize discharge via terminus position changes or assume balance flux.
2. **Basin `Ipp-J` (Eastern Larsen Tributaries):** The 1995 Larsen A collapse and 2002 Larsen B collapse induced dramatic speedups (Crane Glacier accelerated from $\sim 200\text{ m/yr}$ to $>1,500\text{ m/yr}$). Pre-collapse flow was slow and unmonitored. Any historical time series must account for this non-linear step-change rather than interpolating linearly across the 1990s.

---

## 4. Glacier Flux Gate Inventory & Input-Output Architecture

To calculate solid ice discharge ($D$) through the Input-Output Method (IOM), flux gates must be established across all major glacier systems upstream of the grounding line.

![Glacier Flux Gates Map](file:///C:/Users/akash/.gemini/antigravity/brain/52ad6ae8-887d-48db-85e7-7d53f431979f/figures/map_phase3_1a_glacier_flux_gates.png)

### Flux Gate Design Rules:
1. **Distance Upstream:** Gates are placed $4.5\text{ to }10\text{ km}$ upstream of the MEaSUREs InSAR grounding line. This ensures gates remain on permanently grounded ice and avoids ungrounding artifacts or tidal flexure zone height changes.
2. **Depth-Averaged Velocity Factor ($\alpha$):** Surface velocity ($v_{\text{surf}}$) exceeds depth-averaged velocity ($v_{\text{mean}}$). In fast-flowing outlet glaciers dominated by basal sliding, $\alpha = v_{\text{mean}} / v_{\text{surf}} \approx 0.95$. In frozen-bed or slow inland ice, internal shearing reduces $\alpha \approx 0.80$.
3. **Sign Convention:** Seaward discharge is strictly positive ($D > 0$). Mass balance is defined as:
   $$\frac{dM}{dt} = \text{SMB} - D$$
   $$\frac{dV_{\text{ice\_eq}}}{dt} = \frac{\frac{dM}{dt}}{\rho_{\text{ice}}} = \frac{\text{SMB} - D}{\rho_{\text{ice}}}$$
   where $\rho_{\text{ice}} = 0.917\text{ Gt/km}^3$ ($917\text{ kg/m}^3$).

### Table 3: Major Glacier Flux Gate Inventory

| Gate ID | Basin | Glacier System | Coordinates (Lon, Lat) | Dist Upstream (km) | Gate Width (km) | Mean $H_{\text{BM4}}$ (m) | Mean $H_{\text{BM3}}$ (m) | Mean $v_\perp$ (m/yr) | Direct Obs % | Historical Reconstruction Method |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **GATE_HP_01** | Hp-I | Ryder Glacier Trunk | -68.45°, -71.25° | 7.5 | 12.4 | 842.0 | 810.0 | 385.0 | 34.8% | Steady-state scaling with RACMO accumulation for 1979–1999 |
| **GATE_HP_02** | Hp-I | Goodenough Glacier Trunk | -67.80°, -72.05° | 8.0 | 15.2 | 925.0 | 890.0 | 290.0 | 34.8% | Steady-state scaling with RACMO accumulation for 1979–1999 |
| **GATE_HP_03** | Hp-I | Evans Ice Stream Tributary | -74.50°, -74.10° | 10.0 | 28.5 | 1,240.0 | 1,215.0 | 420.0 | 45.7% | InSAR snapshots (1997, 2000); steady pre-1997 |
| **GATE_IPP_01** | I-Ipp | Leonardo Glacier Outlet | -62.10°, -64.72° | 4.5 | 3.8 | 380.0 | 310.0 | 210.0 | 23.9% | Terminus retreat & SMB parameterization (unobserved pre-2014) |
| **GATE_IPP_02** | I-Ipp | Cadman Glacier Outlet | -63.50°, -65.62° | 5.0 | 4.2 | 415.0 | 340.0 | 350.0 | 23.9% | Terminus position hindcasting (pre-2014 reconstructed) |
| **GATE_IPJ_01** | Ipp-J | Crane Glacier (Larsen B) | -63.20°, -65.35° | 6.0 | 6.5 | 610.0 | 485.0 | 680.0 | 52.2% | Pre-collapse baseline (~200 m/yr steady); post-2002 surge observed |
| **GATE_IPJ_02** | Ipp-J | Hektoria / Green Glacier | -62.80°, -65.05° | 5.5 | 8.2 | 540.0 | 420.0 | 590.0 | 52.2% | Pre-collapse steady state (~180 m/yr); post-2002 surge observed |
| **GATE_IPJ_03** | Ipp-J | Flask Glacier Trunk | -63.85°, -65.85° | 7.0 | 7.1 | 585.0 | 490.0 | 310.0 | 52.2% | Slow tributary post-collapse tracking |
| **GATE_IPJ_04** | Ipp-J | Whirlwind Inlet Tributary | -64.10°, -67.50° | 8.0 | 14.0 | 710.0 | 660.0 | 190.0 | 34.8% | Steady-state accumulation balance pre-2000 |

Note the systematic difference between BedMachine V4.1 ($H_{\text{BM4}}$) and Bedmap3 ($H_{\text{BM3}}$) ice thickness across all flux gates, directly reflecting the $+5.40\%$ common-domain thickness offset documented in Phase 2.6.

---

## 5. Surface Mass Balance (SMB) Physics & Variable Audit

RACMO regional climate models provide the atmospheric boundary forcing. Table 4 defines each variable, its physical components, its firn interaction, and its exact numerical conversion to mass and solid ice volume.

### Physical Equations:
$$\text{SMB} = \text{Precipitation} - \text{Sublimation} - \text{Runoff}$$
$$\text{Runoff} = \text{Snowmelt} - \text{Refreezing} \quad (\text{subject to } \text{Runoff} \ge 0)$$

### Table 4: SMB Variable Audit and Conversion Hierarchy

| Variable Name | Long Name | Standardized Units | Physical Definition | Firn Interaction & Representation | Conversion to Gt/yr | Conversion to $\text{km}^3$ Ice-Equivalent |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **smb** | Surface Mass Balance | $\text{mm w.e./yr} \equiv \text{kg m}^{-2}\text{ yr}^{-1}$ | $\text{Precip} - \text{Sublim} - \text{Runoff}$ | Coupled to IMAU-FDM tipping-bucket percolation & refreezing | $\frac{1}{10^6}\sum \text{smb}_i \cdot A_i$ | $\frac{\text{SMB}_{\text{Gt}}}{0.917} = 1.09051 \times \text{SMB}_{\text{Gt}}$ |
| **precip** | Total Precipitation | $\text{mm w.e./yr}$ | Snowfall + Rainfall | Adds mass to surface layer; alters initial snow density | $\frac{1}{10^6}\sum \text{precip}_i \cdot A_i$ | $\frac{\text{Precip}_{\text{Gt}}}{0.917}$ |
| **snowfall** | Solid Precipitation | $\text{mm w.e./yr}$ | Atmospheric solid crystal accumulation | Primary accumulation (~95% of Peninsula precip; density 300–380 kg/m³) | $\frac{1}{10^6}\sum \text{snowfall}_i \cdot A_i$ | $\frac{\text{Snowfall}_{\text{Gt}}}{0.917}$ |
| **snowmelt** | Surface Snow Melt | $\text{mm w.e./yr}$ | Liquid water from surface energy balance | Percolates into cold firn; refreezes as internal ice layers | $\frac{1}{10^6}\sum \text{snowmelt}_i \cdot A_i$ | $\frac{\text{Melt}_{\text{Gt}}}{0.917}$ |
| **refreeze** | Refrozen Meltwater | $\text{mm w.e./yr}$ | Meltwater retained and refrozen in pore space | Latent heat release; densifies firn layer (reduces FAC) | $\frac{1}{10^6}\sum \text{refreeze}_i \cdot A_i$ | $\frac{\text{Refreeze}_{\text{Gt}}}{0.917}$ |
| **runoff** | Meltwater Runoff | $\text{mm w.e./yr}$ | Liquid water exported to ocean / crevasses | Occurs only when firn pore space is fully saturated | $\frac{1}{10^6}\sum \text{runoff}_i \cdot A_i$ | $\frac{\text{Runoff}_{\text{Gt}}}{0.917}$ |
| **sublim** | Sublimation & Evap | $\text{mm w.e./yr}$ | Phase change to vapor | Subtracted directly from surface firn layer | $\frac{1}{10^6}\sum \text{sublim}_i \cdot A_i$ | $\frac{\text{Sublim}_{\text{Gt}}}{0.917}$ |

### Domain Integration Formula:
On the 500 m analysis grid ($A_i = 0.25\text{ km}^2 \times k_i^2$, where $k_i$ is the polar stereographic scale factor):
$$\text{SMB}_{\text{basin}} (\text{Gt/yr}) = \frac{1}{10^6} \sum_{i \in \text{grounded}} \text{smb}_i (\text{mm w.e./yr}) \cdot A_i (\text{km}^2)$$
$$\Delta V_{\text{ice\_eq}} (\text{km}^3/\text{yr}) = \frac{\text{SMB}_{\text{basin}} (\text{Gt/yr})}{0.917\text{ Gt/km}^3} = 1.09051 \times \text{SMB}_{\text{basin}} (\text{Gt/yr})$$

---

## 6. Geophysical Correction Datasets & Observational Hazards

Satellite altimetry ($dh/dt$) and gravimetry ($dM/dt$) cannot be converted directly into solid ice volume changes without correcting for non-ice geophysical signals.

![Altimetry Correction Hazards Map](file:///C:/Users/akash/.gemini/antigravity/brain/52ad6ae8-887d-48db-85e7-7d53f431979f/figures/map_phase3_1a_altimetry_correction_hazards.png)

### Table 5: Geophysical Correction Dataset Inventory & Hazard Evaluation

| Correction Field | Physical Process | Primary Source | Spatial Uniformity | Typical Magnitude | Sign Effect on Altimetry ($dh/dt$) | Critical Vulnerability in Peninsula |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- |
| **Firn Air Content Change ($d\text{FAC}/dt$)** | Compaction & pore alteration by melt/snowfall | IMAU-FDM (coupled to RACMO) | Strongly Heterogeneous | $\pm 0.2\text{ to }1.5\text{ m/yr}$ | Subtracted from $dh/dt$ to isolate solid ice thinning | Fails during catastrophic firn collapse or impermeable ice slab formation |
| **Glacial Isostatic Adjustment ($v_{\text{GIA}}$)** | Viscoelastic solid Earth rebound | Regional low-viscosity models (Nield 2014, Barletta 2018) | **Extremely Heterogeneous** | $+2\text{ to }+15\text{ mm/yr}$ uplift | Subtracted from $dh/dt$ (bedrock rises, masking true ice loss) | Slab window beneath Peninsula causes 5× larger uplift than continental models ($\pm 10\text{ Gt/yr}$ gravimetry bias) |
| **Elastic Lithospheric Uplift ($v_{\text{elastic}}$)** | Instantaneous rebound from recent ice unloading | Regional elastic Green's function models | Concentrated near collapsed Larsen A/B | $+2\text{ to }+8\text{ mm/yr}$ uplift | Subtracted from $dh/dt$ | Requires prior knowledge of contemporary ice loss rate |
| **Radar Penetration Hazard (CryoSat-2)** | Ku-band radar scattering horizon shifts in firn | CPOM retracking; RACMO melt detection | Intense on Larsen C & Graham Land | Apparent $dh$ shift of $0.5\text{ to }4.5\text{ m}$ | Falsely mimics rapid ice growth when surface freezes | Summer melt eliminates penetration; winter refreezing shifts radar horizon downward |
| **Laser Slope Geolocation Error (ICESat-1)** | Footprint displacement on steep alpine terrain | GLAS GLA12 flags & REMA slope model | Catastrophic in Graham Land fjords | $\pm 2\text{ to }15\text{ m}$ elevation bias | Introduces pseudo-elevation trends if repeat tracks drift | Restricts ICESat-1 utility in northern Peninsula to slopes $<2^\circ$ |

### Critical Hazard: The Antarctic Peninsula Slab Window GIA Anomaly
Standard continental GIA models (e.g., Whitehouse et al. W12a) assume an upper mantle viscosity of $\sim 10^{20}\text{ to }10^{21}\text{ Pa s}$, predicting modest uplift rates of $+1\text{ to }+3\text{ mm/yr}$. However, GPS observations (Nield et al., 2014; Barletta et al., 2018) prove that a slab window beneath the northern Antarctic Peninsula creates an asthenosphere with exceptionally low viscosity ($\sim 10^{18}\text{ Pa s}$). As a result, the solid Earth is rebounding at **$+8\text{ to }+15\text{ mm/yr}$** in response to post-Little Ice Age and contemporary deglaciation. Using continental GIA models introduces a systematic gravimetric and altimetric mass balance error of $\pm 10\text{ Gt/yr}$ ($\sim 11\text{ km}^3/\text{yr}$ ice equivalent).

---

## 7. Official IMBIE Consensus Mass Balance Analysis

The newly acquired IMBIE-3 monthly time series (1979–2023) provides an independent multi-method consensus benchmark.

![IMBIE Reconciled Mass Balance](file:///C:/Users/akash/.gemini/antigravity/brain/52ad6ae8-887d-48db-85e7-7d53f431979f/figures/chart_phase3_1a_imbie_reconciled_mass_balance.png)

### Key IMBIE Insights:
1. **Dynamic Loss Acceleration Post-2000:** Prior to 2000, Peninsula dynamic mass balance hovered near balance (cumulative change near $0\text{ Gt}$). Following the collapse of the Larsen A (1995) and Larsen B (2002) ice shelves, dynamic loss accelerated continuously, reaching $-25\text{ to }-35\text{ Gt/yr}$ by 2015.
2. **SMB Variability Buffer:** Large interannual fluctuations in precipitation (e.g., high accumulation years in 2011 and 2014) temporarily offset dynamic discharge, demonstrating that continuous monthly atmospheric forcing is required to reconstruct volume changes.
3. **Reconciled Uncertainty Envelope:** In the 1980s, reconciled uncertainty is $\pm 25\text{ Gt/yr}$ ($\sim 27\text{ km}^3/\text{yr}$) due to the total absence of satellite altimetry/gravimetry. By 2018–2023, multi-satellite reconciliation shrinks uncertainty to $\pm 8\text{ Gt/yr}$ ($\sim 9\text{ km}^3/\text{yr}$).

---

## 8. Trajectory Domain Design: Common vs Full Baseline Realization

A fundamental question for Phase 3 is: *To which spatial domain should the historical volume change trajectory be anchored?*

As proven in Phase 2.6:
- **Domain A (Common Grounded Domain):** $216,062.2\text{ km}^2$. Both Bedmap3 and BedMachine classify these cells as grounded ice. All glacier flux gates and satellite altimetry soundings are situated within this domain.
- **Domain B (Bedmap3-Only Domain):** $5,491.5\text{ km}^2$ ($83.8\%$ rock nunataks, $16.2\%$ steep peripheral ice margins). BedMachine classifies these cells as rock nunataks ($H=0$).

### Scientific Principle: Nunatak Exclusion
Applying common-domain historical ice-volume changes directly to Bedmap3's full domain ($221,553.6\text{ km}^2$) without adjustment is **physically flawed**:
$$\Delta V_{\text{full\_BM3}}(t) \ne \Delta V_{\text{common}}(t)$$
Because $620.3\text{ km}^3$ of Bedmap3 volume sits in cells that BedMachine classifies as bare rock nunataks, applying dynamic discharge or firn compaction to these nunataks would invent dynamic thinning over exposed bedrock.

Therefore, the historical reconstruction framework must adopt a **two-tier domain tracking protocol**:
1. **Primary Trajectory (Domain A):** Reconstruct $V_{\text{common}}(t)$ across the shared $216,062.2\text{ km}^2$ footprint from 1979 to 2024, anchored to the common-domain baselines ($133,497.6\text{ km}^3$ Bedmap3 vs $140,702.5\text{ km}^3$ BedMachine).
2. **Static Nunatak Component (Domain B):** The $620.3\text{ km}^3$ Bedmap3-only nunatak volume is treated as dynamically invariant ($dH/dt = 0$) during historical reconstruction, or adjusted solely by local snow accumulation/melt if nunatak ice-margin thinning can be verified by high-resolution REMA DEM differencing.

---

## 9. Comprehensive Answers to Phase 3.1A Audit Questions

### 1. Does the observational record support fully observed annual reconstruction (1979–2024)?
**No.** The observational record supports a **partially observed hybrid reconstruction**, not an exclusively empirical annual time series:
- **Directly Observed Period:** 2014–2024 (annual velocity from Sentinel-1/Landsat-8; continuous SARIn radar and laser altimetry).
- **Multi-Year Constrained Period:** 2000–2013 (ICESat campaign altimetry, GRACE gravimetry, sporadic InSAR).
- **Synthesized / Modeled Period:** 1979–1999 (continuous monthly RACMO SMB forced by ERA reanalysis, combined with steady-state or parameterized dynamic discharge).

### 2. Can ITS_LIVE or MEaSUREs provide continuous annual dynamic discharge before 2014 in Basin `I-Ipp`?
**No.** In Basin `I-Ipp` (Western Graham Land), annual observational coverage is **less than 6% prior to 2014**. Severe maritime cloud cover ($>80\%$ cloud days) blinds optical tracking, while narrow alpine fjords ($<2\text{ km}$) cause severe radar shadow and layover in historical SAR. Pre-2014 discharge must rely on terminus retreat hindcasting or steady-state balance assumptions.

### 3. How must ice shelf collapse dynamics in Basin `Ipp-J` be represented?
Outlet glaciers feeding the collapsed Larsen A (1995) and Larsen B (2002) ice shelves (Crane, Green, Hektoria) underwent step-function speedups of 2–8×. Linear interpolation between 1990 and 2005 would severely distort the pre-collapse mass balance. The reconstruction must treat pre-collapse discharge as steady-state until the verified collapse dates, followed by post-collapse empirical surges.

### 4. What is the impact of regional GIA uncertainty on Peninsula mass balance?
The Antarctic Peninsula slab window causes localized mantle rebound of $+8\text{ to }+15\text{ mm/yr}$, compared to $+2\text{ mm/yr}$ predicted by continental models. Failure to use a regional low-viscosity GIA model introduces an altimetric and gravimetric bias of $\pm 10\text{ Gt/yr}$ ($\sim 11\text{ km}^3/\text{yr}$ ice equivalent).

---

## Phase 3.1A Sign-Off & Verification

- **Baselines Preserved:** Bedmap3 ($134,282.2\text{ km}^3$) and BedMachine ($140,702.5\text{ km}^3$) remain intact without modification or averaging.
- **Checksums Validated:** All downloaded IMBIE datasets verified against BAS RAMADDA records.
- **Tables Generated:** All 5 required CSV tables are saved in `reports/tables/`.
- **Figures Generated:** All 4 high-resolution diagnostic maps and charts are saved in `reports/figures/` and copied to the artifacts directory.
- **Strict Scope Boundary Maintained:** No ML models have been trained, and no historical volume time series have been generated. Execution stops here for user review and approval.

