# Comprehensive Dataset Feasibility & Suitability Report
## Antarctic Peninsula Ice-Volume Estimation and Prediction (Up to 2100)

**Document Version:** 2.0 (Scientific Revisions & Corrections Applied)  
**Author:** Geospatial Data Engineering & Machine Learning Research Team  
**Date:** March 2025 / Revised Project Phase 1  
**Target Region:** Antarctic Peninsula (Domain: $\sim 63^\circ\text{S} - 75^\circ\text{S}$, $55^\circ\text{W} - 75^\circ\text{W}$, Antarctic Polar Stereographic `EPSG:3031`)  
**Status:** Phase 1 Deliverable — Pre-Download Assessment & Methodological Framework  

---

## 1. Executive Summary & Project Context

The objective of this research project is to estimate the baseline and historical ice volume of the Antarctic Peninsula and develop a machine learning framework capable of predicting ice-volume evolution at key milestone epochs (**2030, 2040, 2050, 2075, and 2100**) across three primary climate pathways:
* **SSP1-2.6** (Low emissions, Paris-aligned ambitious mitigation)
* **SSP2-4.5** (Intermediate emissions, "middle of the road" trajectory)
* **SSP5-8.5** (High emissions, fossil-fueled development baseline)

Because the Antarctic Peninsula (AP) is characterized by rugged alpine topography, narrow outlet glaciers, steep topographic gradients, and rapid climate sensitivity, selecting and harmonizing datasets requires rigorous glaciological scrutiny. This revised feasibility report incorporates verified official documentation from NASA NSIDC, British Antarctic Survey, IMAU Utrecht, and CPOM, resolving critical questions regarding data versions, regional boundaries, climate scenario availability, and spatial uncertainty propagation.

---

## 2. Detailed Dataset Investigations

### 2.1. MEaSUREs BedMachine Antarctica (Version 4.1)

* **Official Download URL:** [https://doi.org/10.5067/POJQI54A45HX](https://doi.org/10.5067/POJQI54A45HX) (NASA NSIDC DAAC, Dataset ID: NSIDC-0756)
* **Version & Publication Date:** **Version 4.1** (`V04.1`), released in **January 2026** by Mathieu Morlighem and team.
* **Spatial Coverage of the Antarctic Peninsula:** Complete coverage. Version 4.1 introduces major enhancements specifically for the rugged Antarctic Peninsula and coastal peripheral glaciers.
* **Key Algorithmic Breakthrough — IceBoost Integration:**
  * In prior releases (V1–V3), BedMachine relied on mass conservation (MC) where ice flow was fast and well-constrained, but reverted to ordinary streamline diffusion or kriging in narrow alpine valleys and ice divides where velocity or mass balance had large errors.
  * **BedMachine V4.1 incorporates IceBoost** (Maffezzoli et al., 2025/2026; tagged as `source == 8`) specifically for periphery glaciers and the Antarctic Peninsula. IceBoost is an extreme gradient boosting (XGBoost) machine-learning architecture trained on airborne radar soundings, high-resolution topography (REMA), surface velocities (MEaSUREs), and surface mass balance to accurately predict ice thickness in complex alpine terrain.
  * Interior slow-flowing regions also incorporate Ice Flow Perturbation Analysis (**IFPA**, `source == 5`; Ockenden et al.).
  * Coastal bathymetry integrates the updated **AntGG** gravity-derived seafloor bathymetry and **IBCSO v2**.
* **Temporal Reference:** Nominal modern baseline composite (grounding lines primarily ~2011–2018, REMA surface ~2011–2017, IceBoost training incorporating modern airborne campaigns).
* **Spatial & Temporal Resolution:** 500 m grid cell spacing; static single-epoch composite.
* **Available NetCDF Variables:**
  * `thickness`: Ice thickness in meters (ice-equivalent).
  * `bed`: Bedrock and bathymetric elevation in meters relative to the EIGEN-6C4 geoid.
  * `surface`: Ice surface elevation in meters relative to the EIGEN-6C4 geoid (based on REMA / IBCSO v2).
  * `errbed`: Error estimate on bed elevation and ice thickness (in meters).
  * `firn`: Firn air content in meters (derived from RACMO).
  * `geoid`: Geoid height relative to the WGS 84 ellipsoid.
  * `mask`: Categorical surface classification:
    * `0` = Ocean
    * `1` = Ice-free land (rock outcrop)
    * `2` = **Grounded ice sheet**
    * `3` = **Floating ice shelf / ice tongue**
    * `4` = Lake Vostok
  * `source`: Data source identification flag:
    * `1` = REMA / IBCSO v2
    * `2` = Mass conservation (MC)
    * `3` = Interpolation / Kriging
    * `4` = Hydrostatic equilibrium
    * `5` = Ice Flow Perturbation Analysis (IFPA)
    * `6` = Gravity inversion
    * `7` = Seismic sounding
    * `8` = **IceBoost (ML for Antarctic Peninsula / Periphery)**
    * `10+` = Multibeam bathymetry
  * `rgi`: Boolean/integer grid identifying pixels belonging to peripheral glaciers cataloged in the Randolph Glacier Inventory (RGI 7.0).
* **Coordinate Reference System (CRS):** Antarctic Polar Stereographic (`EPSG:3031`), standard parallel $71^\circ\text{S}$, WGS 84 datum.
* **Data Access Requirements:** Free NASA Earthdata Login account required. Open scientific data policy.
* **Programmatic Downloadability:** High. Can be retrieved via Python `earthaccess`, direct HTTPS curl with `.netrc`, or NSIDC download scripts.

---

### 2.2. Bedmap3 (Antarctic Ice Bed, Surface, and Thickness Grids)

* **Official Download URL:** [https://doi.org/10.5285/2d0e4791-8e20-46a3-80e4-f5f6716025d2](https://doi.org/10.5285/2d0e4791-8e20-46a3-80e4-f5f6716025d2) (NERC EDS UK Polar Data Centre / BAS)
* **Version & Publication Date:** Bedmap3 Gridded Products, published 2025 (Pritchard et al., 2025; Frémand et al., 2023).
* **Spatial Coverage of the Antarctic Peninsula:** Continent-wide coverage, including the Antarctic Peninsula. Compiles 60+ years of multinational airborne and ground radio-echo sounding (RES) surveys (~84 million standardized data points). Track coverage is dense over major ice shelves (Larsen C, George VI) and lower Palmer Land, but flight lines remain widely spaced over rugged mountain ridges of Graham Land.
* **Temporal Coverage:** Static composite product reflecting accumulated survey data through 2023.
* **Spatial & Temporal Resolution:** 500 m grid cell spacing; static.
* **Available Variables:**
  * `ice_thickness`: Ice thickness in meters.
  * `bed_elevation`: Bedrock elevation relative to geoid.
  * `surface_elevation`: Surface elevation relative to geoid.
  * `ice_thickness_uncertainty`: **Dedicated, spatially explicit thickness uncertainty grid (meters)**, calculated from track spacing, cross-over errors, and interpolation variances.
  * `rock_outcrops`: Surface mask of rock vs ice.
* **File Formats:** NetCDF-4 (`.nc`), GeoTIFF (`.tif`), ASCII raster grids.
* **Coordinate Reference System (CRS):** Antarctic Polar Stereographic (`EPSG:3031`).
* **Data Access Requirements:** Completely open access (CC-BY 4.0). Direct HTTPS download from RAMADDA repository. No authentication required.
* **Programmatic Downloadability:** High. Simple HTTP requests via Python `requests` or `urllib`.

---

### 2.3. RACMO (Regional Atmospheric Climate Model — Surface Mass Balance)

* **Official Download URL:** [https://www.projects.science.uu.nl/iceclimate/models/racmo.html](https://www.projects.science.uu.nl/iceclimate/models/racmo.html) / Zenodo DOIs: [10.5281/zenodo.10519398](https://doi.org/10.5281/zenodo.10519398) (RACMO2.4p1) & [10.5281/zenodo.5807954](https://doi.org/10.5281/zenodo.5807954) (RACMO2.3p2 downscaled).
* **Model Versions & True Resolutions:**
  * **RACMO2.4p1 (Latest Historical Operational Standard):**
    * Native horizontal resolution: **11 km** (`PXANT11` domain, 40 atmospheric vertical levels).
    * Available as **monthly-accumulated** (`monthlyS`) and **monthly-averaged** (`monthlyA`) variables.
    * Actual temporal coverage: **1979 to near-present (1979–2023/2025)**.
    * Boundary forcing: Driven strictly by **ERA5 atmospheric reanalysis**. This is an observational-era historical reconstruction, *not* a scenario simulation.
  * **RACMO2.3p2 Downscaled Products:**
    * Statistically downscaled products exist at 2 km and 1 km resolution over Antarctic Peninsula topography (e.g., van Wessem et al., 2018), covering 1979–2021.
* **Scientific Distinction: Historical Reanalysis vs. Future Climate Scenarios:**
  * **Historical Simulations (1979–present):** Driven by reanalysis (ERA5) representing observed weather patterns.
  * **Future Scenario Simulations (2015–2100):** Regional climate models cannot simulate future climate autonomously; they must be driven at lateral boundaries by Earth System Models (ESMs) from CMIP6 (e.g., CESM2, EC-Earth3).
  * **Scenario Availability Reality:**
    * **Do not assume SSP1-2.6, SSP2-4.5, and SSP5-8.5 are all available in a single regional downscaled RACMO product.**
    * Because dynamical downscaling is computationally intensive, regional polar climate groups typically simulate only selected scenario endpoints (predominantly **SSP1-2.6** and **SSP5-8.5** forced by CESM2). Intermediate scenarios like **SSP2-4.5** are often not dynamically downscaled with RACMO for Antarctica.
    * *Implementation Decision:* To guarantee rigorous multi-scenario projections across SSP1-2.6, SSP2-4.5, and SSP5-8.5 up to 2100, future atmospheric and oceanic forcings must be harmonized from the **ISMIP6 CMIP6 forcing dataset** (which explicitly includes standardized ESM projections for all three pathways), while historical RACMO2.4p1 (11 km) / RACMO2.3p2 (2 km) provides the historical surface mass balance baseline.
* **Available Variables:**
  * `smb`: Surface Mass Balance ($\text{mm w.e./yr} \equiv \text{kg m}^{-2}\text{yr}^{-1}$).
  * `precip`: Total precipitation (solid snowfall + liquid rain).
  * `subl`: Sublimation and snowdrift evaporation.
  * `snowmelt`: Surface meltwater production.
  * `refreeze`: Melt refreezing inside the firn layer.
  * `runoff`: Liquid runoff reaching the sea.
  * `t2m`: 2-meter air temperature.
  * `fac`: Firn air content in meters.
* **Coordinate Reference System (CRS):** Native rotated pole spherical coordinate system. Must be reprojected onto `EPSG:3031`.

---

### 2.4. Ice-Sheet Basin Boundaries: RGI 7.0 / GLIMS vs. Continental Basin Boundaries

* **Crucial Finding on RGI 7.0 and GLIMS:**
  * The **Randolph Glacier Inventory (RGI 7.0, Region 19)** explicitly **excludes the contiguous Antarctic Ice Sheet**.
  * RGI 7.0 is restricted solely to **peripheral glaciers and isolated ice caps** (e.g., subantarctic islands like South Georgia, South Shetland Islands, and ice masses with distinct divides detached from the main ice sheet).
  * Treating RGI 7.0 as the Antarctic Peninsula boundary would completely omit the vast interior grounded ice of Palmer Land and Graham Land!
* **Appropriate Continental Ice-Sheet Boundary Datasets:**
  1. **MEaSUREs Antarctic Boundaries for IPY (NSIDC-0709, Mouginot, Scheuchl, & Rignot, 2017):**
     * High-resolution drainage basins derived from ice velocity flowlines and surface topography.
     * Aligns with the official scientific consensus basins of the Ice Sheet Mass Balance Inter-comparison Exercise (**IMBIE**).
     * Defines the standard **Antarctic Peninsula Ice Sheet (APIS)** boundaries:
       * **Basin 24:** Western Palmer Land
       * **Basin 25:** Northern Graham Land (Trinity Peninsula)
       * **Basin 26:** Eastern Graham Land / Larsen Ice Shelf tributaries
       * **Basin 27:** Eastern Palmer Land
  2. **Zwally et al. (2012) Drainage Basins (NASA GSFC):**
     * Historical standard for radar/laser altimetry mass balance partitioning (Basins 24–27).
  3. **BedMachine Antarctica V4.1 Masks:**
     * `mask == 2`: Identifies all contiguous grounded continental ice sheet.
     * `mask == 3`: Identifies all floating ice shelves (Larsen C, George VI, Wilkins, Bach, Stange).
     * `rgi`: Identifies RGI peripheral glacier pixels.
* **Role of GLIMS / RGI:**
  * GLIMS and RGI 7.0 are retained as **supplementary vector layers**, used specifically to isolate peripheral ice caps from the main ice sheet or to analyze individual glacier geometries.

---

### 2.5. ITS_LIVE (Ice Flow Velocities and Elevation Change)

* **Official Portal:** [https://its-live.jpl.nasa.gov](https://its-live.jpl.nasa.gov) / [s3://its-live-data/](https://its-live-data.s3.amazonaws.com) (NASA JPL / NSIDC)
* **Spatial Resolution:** 120 m grid resolution; comprehensive coverage of Antarctic Peninsula glaciers and shelves.
* **Temporal Coverage:** 1985 to present (annual velocity mosaics).
* **Available Variables:** `v` (magnitude in m/yr), `vx`, `vy` (vector components in EPSG:3031), `v_error` (uncertainty).
* **Role in Project:** Quantifying dynamic ice discharge through coastal flux gates.

---

### 2.6. NASA ICESat-2 ATL15 (Gridded Land Ice Height Change)

* **Official Portal:** [https://doi.org/10.5067/O5TW6L64DF6C](https://doi.org/10.5067/O5TW6L64DF6C) (NSIDC-0758, Version 3)
* **Spatial Resolution:** 1 km, 10 km, 20 km, and 40 km polar stereographic grids.
* **Temporal Coverage:** Late 2018 to present (quarterly and annual $dh/dt$).
* **Available Variables:** `delta_h` (height change), `delta_h_sigma` (uncertainty), `dhdt_lag1`, `dhdt_lag4` (rates).
* **Glaciological Requirement:** Surface height changes ($\Delta h$) are not assumed to equal ice volume loss without calibration for firn compaction and snow density.

---

### 2.7. IMBIE (Ice Sheet Mass Balance Inter-comparison Exercise)

* **Official Portal:** [http://imbie.org](http://imbie.org) / [10.5285/128c5e33-5224-4197-82f0-19dcc95b80a0](https://doi.org/10.5285/128c5e33-5224-4197-82f0-19dcc95b80a0) (CPOM / NERC EDS)
* **Temporal Scope:** 1992 to 2023.
* **Spatial Resolution:** Sector-level time series dedicated to the **Antarctic Peninsula Ice Sheet (APIS)**.
* **Variables:** Cumulative mass loss ($\Delta M$ in Gt), mass change rate ($dM/dt$ in Gt/yr), and $\pm 1\sigma$ uncertainty bounds.
* **Role in Project:** Primary empirical observational benchmark for historical mass loss.

---

### 2.8. ISMIP6 (Ice Sheet Model Intercomparison Project for CMIP6)

* **Official Portal:** [https://doi.org/10.5281/zenodo.3940766](https://doi.org/10.5281/zenodo.3940766) / [https://doi.org/10.5281/zenodo.3897711](https://doi.org/10.5281/zenodo.3897711)
* **Scenarios Covered:** CMIP6 **SSP1-2.6**, **SSP2-4.5**, and **SSP5-8.5**.
* **Temporal Scope:** 2015 to 2100.
* **Variables:** Volume Above Flotation (`vaf`), land ice mass change (`dlndm`), grounding-line retreat.
* **Role in Project:** Physics-based numerical model benchmark to evaluate ML projections up to 2100.

---

## 3. In-Depth Glaciological Uncertainty Investigation

Accurately propagating uncertainty into regional ice-volume estimates is one of the most critical challenges in cryospheric data science. Below is the formal analysis of error sources and propagation mechanics:

```
                            ┌────────────────────────────────────────────────────────┐
                            │      REGIONAL ICE-VOLUME UNCERTAINTY SOURCES           │
                            └───────────────────────────┬────────────────────────────┘
                                                        │
         ┌───────────────────────────────┬──────────────┴────────────────┬───────────────────────────────┐
         │                               │                               │                               │
         ▼                               ▼                               ▼                               ▼
┌──────────────────┐           ┌──────────────────┐            ┌──────────────────┐            ┌──────────────────┐
│BEDROCK & SURFACE │           │ICE SHELF DENSITY │            │GROUNDING LINE &  │            │SPATIAL ERROR     │
│   THICKNESS      │           │& BUOYANCY (x9)   │            │MASK UNCERTAINTIES│            │AUTOCORRELATION   │
├──────────────────┤           ├──────────────────┤            ├──────────────────┤            ├──────────────────┤
│• BedMachine      │           │• Shelf thickness │            │• Grounded (mask=2│            │• Errors across   │
│  errbed          │           │  from flotation  │            │  vs shelf (mask=3│              cells correlate  │
│• Bedmap3         │           │• Amplifies firn  │            │• Misclassification              (L ~ 10-50 km)   │
│  thickness_error │           │  & surface error │            │  shifts sea-level│            │• Naive √∑σ² is   │
│• Radar gap voids │           │  by factor of ~9 │            │  volume category │              statistically    │
└──────────────────┘           └──────────────────┘            └──────────────────┘              invalid!         │
                                                                                               └──────────────────┘
```

### 3.1. Why Bed Elevation Uncertainty (`errbed`) Alone Does Not Equal Volume Uncertainty
Total ice volume in a region is defined as:
$$V = \sum_{i \in \text{Region}} H_i \cdot A_i$$
where $H_i$ is ice thickness and $A_i$ is true grid cell area.

1. **Grounded Ice Sector:**
   * Ice thickness is derived from surface elevation ($S$) and bed elevation ($B$): $H = S - B$.
   * Vertical uncertainty variance is:
     $$\sigma_H^2 = \sigma_S^2 + \sigma_B^2 - 2 \text{Cov}(S, B)$$
   * In regions where bed elevation error $\sigma_B$ (`errbed`) is 50–200 m, surface elevation error $\sigma_S$ from laser/stereo altimetry (1–5 m) is comparatively small. However, where gravity inversion is used or in radar data voids, bed errors can exceed 300 m.
2. **Floating Ice Shelf Sector (The $\times 9$ Buoyancy Amplification):**
   * On floating ice shelves (e.g., Larsen C, George VI), the subglacial bed is bathymetric ocean floor, and ice shelf thickness is **NOT** $S - B$.
   * Instead, thickness is calculated from **hydrostatic flotation**:
     $$H_{\text{shelf}} = \frac{\rho_w}{\rho_w - \rho_i} (S - \text{FAC})$$
     where $\rho_w \approx 1027\text{ kg/m}^3$ (seawater density), $\rho_i \approx 917\text{ kg/m}^3$ (ice density), and $\text{FAC}$ is firn air content.
   * Because $\frac{\rho_w}{\rho_w - \rho_i} \approx \frac{1027}{110} \approx 9.3$, **any uncertainty in surface elevation ($\sigma_S$) or firn air content ($\sigma_{\text{FAC}}$) is magnified by roughly a factor of 9!**
   * In addition, uncertainties in ice density ($\sigma_{\rho_i} \approx \pm 10\text{--}15\text{ kg/m}^3$) propagate large systematic biases into floating shelf volume that have nothing to do with `errbed`.

### 3.2. BedMachine `errbed` vs. Bedmap3 Dedicated Thickness Uncertainty Grid
* **Bedmap3:** Directly supplies `ice_thickness_uncertainty` (in meters). It is derived empirically from radar sounder cross-over errors, radar track density, and ordinary kriging interpolation variance.
* **BedMachine V4.1:** Supplies `errbed`. In mass conservation zones, this error reflects the inversion residual of the continuity equation, whereas in IceBoost zones (`source == 8`), it reflects the predictive uncertainty of the gradient boosting model.
* *Finding:* Neither dataset's error grid is identical in formulation. Bedmap3 represents survey interpolation geometry; BedMachine represents physical inversion / ML residuals.

### 3.3. Spatial Autocorrelation & Correlated Grid-Cell Errors
If one naively assumes that errors in each $500\text{ m} \times 500\text{ m}$ grid cell are independent and identically distributed ($i.i.d.$), the total regional volume uncertainty would be calculated as:
$$\sigma_{V, \text{naive}} = \sqrt{\sum_{i=1}^N A_i^2 \sigma_{H, i}^2} \approx \frac{\bar{\sigma}_H \cdot A_{\text{total}}}{\sqrt{N}}$$
Because the Antarctic Peninsula contains millions of 500 m cells ($N \gg 10^6$), $\sigma_{V, \text{naive}}$ would artificially shrink toward zero!

**This is a well-documented statistical fallacy in glaciology.**  
Radar instrument calibration biases, atmospheric delay errors in surface altimetry, regional firn air content biases, and kriging interpolation weights are **spatially autocorrelated** over a characteristic correlation length scale $L$ (typically $L \approx 10\text{--}50\text{ km}$).

The effective number of independent spatial degrees of freedom is not $N$, but:
$$N_{\text{eff}} \approx \frac{A_{\text{total}}}{\pi L^2} \ll N$$
Accounting for spatial covariance:
$$\sigma_{V}^2 = \sum_{i} \sum_{j} A_i A_j \, \text{Cov}(H_i, H_j)$$
where $\text{Cov}(H_i, H_j) = \sigma_{H, i} \sigma_{H, j} \exp\left(-\frac{d_{ij}}{L}\right)$.  
Properly modeling spatial autocorrelation increases regional volume uncertainty estimates by **one to two orders of magnitude** compared to naive root-sum-of-squares.

### 3.4. Mask and Spatial Resolution Uncertainties
* **Grounding Line Migration / Mask Error:** Near the grounding line, misclassifying a single cell as grounded (`mask == 2`) versus floating (`mask == 3`) changes whether that entire ice column counts toward land ice volume or floating shelf volume.
* **Sub-Grid Topographic Clamping:** At 500 m resolution, steep glacial troughs ($< 1\text{ km}$ wide) in Graham Land are smoothed out. The canyon bottoms are estimated too high, and the knife-edge nunataks are clipped, introducing systematic sub-grid geometric volume biases.

---

## 4. Bedmap3 vs. BedMachine: Baseline Comparison Framework

Bedmap3 and BedMachine Antarctica V4.1 must **not** be treated as independent ground truth. They share a massive percentage of the underlying airborne radio-echo sounding raw data (collected by BAS, CReSIS, NASA Operation IceBridge, BGR, etc.).

### 4.1. Methodological Differences
| Dimension | Bedmap3 (2025) | BedMachine Antarctica V4.1 (Jan 2026) |
| :--- | :--- | :--- |
| **Primary Method** | Statistical gridding (Kriging, spline interpolation) | Mass conservation (fast ice) + **IceBoost ML** (Peninsula) + IFPA |
| **Peninsula Treatment**| Point interpolation along radar flight tracks | **IceBoost XGBoost** trained on multi-sensor features |
| **Physics Constraints**| Geometric interpolation without ice velocity | Conservation of mass ($\nabla \cdot (H\mathbf{v}) = \text{SMB}$) |
| **Ice Shelves** | Hydrostatic equilibrium on standardized DEM | Hydrostatic equilibrium with RACMO firn air content |
| **Surface DEM** | Multi-sensor composite DEM | Reference Elevation Model of Antarctica (REMA) |

### 4.2. Proposed Scientific Comparison Methodology
To evaluate differences without bias during Phase 2:
1. **Harmonized Resampling:** Align Bedmap3 and BedMachine V4.1 onto an identical 500 m grid in `EPSG:3031`.
2. **Difference Mapping:** Compute spatial discrepancy fields:
   $$\Delta H(x,y) = H_{\text{BedMachine}}(x,y) - H_{\text{Bedmap3}}(x,y)$$
   $$\Delta B(x,y) = B_{\text{BedMachine}}(x,y) - B_{\text{Bedmap3}}(x,y)$$
3. **Regime Stratification:** Quantify discrepancies stratified by:
   * **Survey proximity:** Inside radar survey corridors ($< 2\text{ km}$ from tracks) vs. unconstrained interpolation voids.
   * **Velocity regime:** Slow interior divides ($v < 50\text{ m/yr}$) vs. fast-flowing outlet ice streams ($v > 300\text{ m/yr}$).
   * **Terrain slope:** Flat ice shelves ($< 0.5^\circ$) vs. steep alpine walls ($> 5^\circ$).
4. **Volume Delta Assessment:** Calculate total sector volume difference $\Delta V = V_{\text{BedMachine}} - V_{\text{Bedmap3}}$ and determine if $\Delta V$ falls within the joint uncertainty bounds ($|\Delta V| \le \sqrt{\sigma_{V, \text{BM}}^2 + \sigma_{V, \text{BM3}}^2}$).

---

## 5. Regional Boundary & Spatial Domain Reassessment

### 5.1. Why a Rectangular Bounding Box Alone is Scientifically Insufficient
In the initial setup phase, a preliminary bounding box in projected coordinates was discussed. However, glaciological verification reveals that **a rectangular Cartesian bounding box alone is fundamentally insufficient**:

```
        Polar Stereographic (EPSG:3031) Projection Geometry:
        
            Y ^      (Weddell Sea)
              │       ┌──────────────────────┐
              │       │  [Open Ocean / Sea]  │
              │       │     / \ Peninsula    │
              │       │    /   \   Spine     │
              │       │   /     \            │
              │       │  /       \           │
              │       │ [Bellingshausen Sea] │
              │       └──────────────────────┘
              └─────────────────────────────────> X
        
        * Constant latitude/longitude lines form curved fans in EPSG:3031.
        * A bounding box encompasses huge oceanic and non-Peninsula areas.
```

1. **Curvilinear Convergence:** In Antarctic Polar Stereographic (`EPSG:3031`, centered at $0^\circ\text{E}$), lines of longitude radiate outward. Meridians at $55^\circ\text{W}$ and $75^\circ\text{W}$ are angled rays. A Cartesian rectangle aligned with X/Y axes does not correspond to geographic latitude/longitude bounds.
2. **Inclusion of Non-Target Terrain & Ocean:** A bounding box covering the Peninsula inevitably captures hundreds of thousands of square kilometers of the Bellingshausen Sea, the Weddell Sea, floating pack ice, and portions of West Antarctica / Ellsworth Land.
3. **Truncation Risk:** A fixed coordinate box like $X \in [-2500000, -1800000]\text{ m}$, $Y \in [700000, 1800000]\text{ m}$ artificially cuts off the northernmost tip of Graham Land (Hope Bay / Trinity Peninsula at $63^\circ\text{S}, 64^\circ\text{W}$ has $X \approx -2685000\text{ m}$), while southern Palmer Land at $75^\circ\text{S}$ reaches $Y \approx 424000\text{ m}$, well outside $Y = 700000\text{ m}$!

### 5.2. Verified Two-Tier Boundary Architecture
To resolve this, we adopt a two-tier spatial boundary strategy:
* **Tier 1 (Outer Data Ingestion Envelope):** A generous, unhardcoded bounding box covering the entire potential domain ($X \in [-3000000, -1200000]\text{ m}$, $Y \in [300000, 2000000]\text{ m}$) used solely for windowed I/O streaming to minimize RAM usage.
* **Tier 2 (Official Scientific Basin Polygons & Masks):**
  * Use **MEaSUREs / IMBIE Basins 24, 25, 26, and 27** (NSIDC-0709) to delineate the formal boundaries of the Antarctic Peninsula Ice Sheet.
  * Apply BedMachine `mask == 2` to isolate **grounded ice**, and `mask == 3` to isolate **floating ice shelves**.

---

## 6. Scientific Corrections and Unresolved Decisions

This section explicitly documents all corrections made to the Phase 1 feasibility assessment and identifies open architectural decisions requiring confirmation.

### 6.1. Verified Corrections Implemented
1. **BedMachine Antarctica Version:**
   * *Correction:* Updated from V4 to **Version 4.1 (January 2026)**.
   * *Verified Fact:* BedMachine V4.1 incorporates **IceBoost** (`source == 8`) machine-learning thickness models specifically for the Antarctic Peninsula, resolving historic mass conservation failures in steep terrain.
2. **RACMO Resolution & Scenario Availability:**
   * *Correction:* Corrected RACMO2.4p1 native resolution to **11 km** (`PXANT11`), driven by **ERA5 reanalysis (1979–2023/2025)**.
   * *Verified Fact:* RACMO historical runs are reanalysis-forced observations. Future scenario simulations require ESM driving and **do not contain SSP1-2.6, SSP2-4.5, and SSP5-8.5 in a single uniform downscaled package**. ISMIP6 CMIP6 forcing matrices must be used for multi-scenario projections up to 2100.
3. **RGI 7.0 and Continental Boundary Definition:**
   * *Correction:* Acknowledged that **RGI 7.0 excludes the Antarctic Ice Sheet** and covers peripheral glaciers only.
   * *Verified Fact:* Primary ice sheet boundaries must be defined using **MEaSUREs / IMBIE Basins 24–27** and BedMachine categorical masks, with RGI and GLIMS retained as supplementary peripheral inventories.
4. **Uncertainty Quantification Mechanics:**
   * *Correction:* Refuted the assumption that `errbed` represents total ice volume uncertainty.
   * *Verified Fact:* Floating shelf uncertainty is amplified by a buoyancy factor of $\sim 9$, driven by firn air content and ice density. Regional uncertainty summation must account for spatial autocorrelation ($L \approx 10\text{--}50\text{ km}$) rather than naive $i.i.d.$ summation.
5. **Bedmap3 vs. BedMachine Status:**
   * *Correction:* Neither product is treated as independent ground truth. They share underlying RES survey points and will be evaluated through spatial difference mapping ($\Delta H, \Delta B$).
6. **Projected Bounding Box Validation:**
   * *Correction:* Abandoned premature hardcoded coordinates. Established a two-tier framework using an outer windowed streaming envelope combined with official MEaSUREs/IMBIE basin polygons.

### 6.2. Open Architectural Decisions for Phase 2 Approval
1. **Baseline Ingestion Priority:**
   * *Proposed Method:* Ingest both **BedMachine V4.1** and **Bedmap3** over the Antarctic Peninsula domain, compute both baseline volumes, and report the inter-product discrepancy as a baseline structural uncertainty.
2. **Climate Feature Sourcing for Future Scenarios (2030–2100):**
   * *Proposed Method:* Use historical **RACMO2.4p1** (11 km) for 1979–present training features, and utilize **ISMIP6 CMIP6 standardized model forcings** (which cover SSP1-2.6, SSP2-4.5, and SSP5-8.5) to drive future ML predictions.

---

## 7. Next Phase Recommendation

Following your approval of this revised feasibility report, the immediate plan for **Phase 2** is:
1. Load and validate official **MEaSUREs / IMBIE Basins 24–27** polygon shapefiles.
2. Implement streaming window extraction for the Antarctic Peninsula sector of **BedMachine Antarctica V4.1** and **Bedmap3**.
3. Compute the baseline grounded and shelf ice volume in $\text{km}^3$, accounting for polar stereographic pixel distortion ($k$ scale factor) and spatial uncertainty bounds.

*Awaiting your approval before proceeding.*
