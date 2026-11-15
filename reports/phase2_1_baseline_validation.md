# Phase 2.1 Technical Report: Baseline Data Validation, Area Distortion Audit & BedMachine V4.1 Acquisition

**Project:** Antarctic Ice-Volume Prediction Using Machine Learning (Peninsula Focus to 2100)  
**Document:** Phase 2.1 Baseline Validation and Acquisition Report  
**Date:** November 2026  
**Status:** Complete (Awaiting User Review before Phase 3)  
**Author:** Geospatial Data Engineering & Machine Learning Team  

---

## Executive Summary

Phase 2.1 executes a rigorous glaciological and mathematical validation of the Phase 2 baseline datasets, corrects the mask taxonomy for the British Antarctic Survey (BAS) / SCAR Bedmap3 gridded product, audits cell-level projection distortion across the Antarctic Peninsula, and establishes the secure acquisition and comparative pipeline for NASA MEaSUREs BedMachine Antarctica V4.1.

### Key Scientific & Technical Findings:
1. **Bedmap3 Mask Correction:** Mask class 2 was officially verified as **Transiently Grounded Ice Shelf** (pinning points / grounding zones in floating shelves), *not* subglacial lake features. Across the continental ice sheet boundary, class 2 occupies exactly $1.75\text{ km}^2$ ($0.537\text{ km}^3$); across the broader domain, it occupies $16.0\text{ km}^2$ ($8.810\text{ km}^3$). Class 1 is retained as permanently grounded continental ice, while class 2 is explicitly partitioned and monitored.
2. **Mathematical Volume Calculation Audit:** Verified that the reported $138,079.9\text{ km}^3$ baseline estimate used the correct permanently grounded mask (`m == 1`), valid positive thickness values in meters, excluded all NoData (`-9999`) cells, and produced **zero overlapping boundary pixels** across all three drainage basins (`Hp-I`, `I-Ipp`, `Ipp-J`). Sum of individual basins reconciles with the unified regional polygon to within $0.0\text{ km}^2$ and $0.0\text{ km}^3$.
3. **EPSG:3031 Projection Distortion Audit:** The Antarctic Polar Stereographic projection (standard parallel $\phi_c = 71^\circ\text{S}$) exhibits non-negligible scale distortion across the Antarctic Peninsula:
   - In **Graham Land (`I-Ipp`)** ($63^\circ\text{S}\text{ to }68^\circ\text{S}$), projected cells are stretched ($k > 1$), causing the standard $0.25\text{ km}^2$ cell assumption to **overestimate** true ground area by $+3.15\%$ and volume by $+2.96\%$ ($+369.5\text{ km}^3$).
   - In **Palmer Land (`Hp-I` and `Ipp-J`)** ($71^\circ\text{S}\text{ to }75^\circ\text{S}$), projected cells are compressed relative to the sphere ($k < 1$), meaning true ground area is slightly larger than $0.25\text{ km}^2$, **underestimating** volume by $-0.94\%$ and $-0.43\%$.
   - **Corrected Continental Grounded Volume:** Adjusting for cell-specific scale factors yields **$138,769.0\text{ km}^3$** (a net regional correction of $+689.1\text{ km}^3$, $+0.50\%$). Both projected and true ellipsoidal estimates are preserved for scientific transparency.
4. **BedMachine Antarctica V4.1 Acquisition & Security:** Formulated a zero-compromise authentication pipeline using NASA `earthaccess`. Credentials are never embedded in code, logs, or Git commits. The automated pipeline is wired to process browser-generated NASA Earthdata tokens (`EARTHDATA_TOKEN`) or `.env` configurations.
5. **Comparative Methodology:** Formulated an automated alignment and spatial differencing module ([`src/geospatial/compare_baselines.py`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/src/geospatial/compare_baselines.py)) to map thickness and mask discrepancies between Bedmap3 (kriging) and BedMachine V4.1 (IceBoost ML integration) without treating either dataset as infallible ground truth.

---

## 1. Task 1: Bedmap3 Mask Classification Correction

### 1.1 Glaciological Taxonomy Correction
In the Phase 2 preliminary inspection, Bedmap3 mask value `2` was incorrectly noted as subglacial lakes (by analogy with BedMachine's Lake Vostok classification). Following review of the primary Bedmap3 publication (Pritchard, Fretwell, et al., 2025, *Scientific Data*, 12, 414), the official classification scheme is established as:

| Bedmap3 Integer Value | Official Glaciological Classification | Cryospheric Description & Dynamics |
| :---: | :--- | :--- |
| **`-9999` / `0`** | **Open Ocean / Out-of-Domain** | Bathymetric ocean grid cells beyond ice boundaries |
| **`1`** | **Permanently Grounded Ice** | Continental ice resting on subglacial bedrock above hydrostatic buoyancy |
| **`2`** | **Transiently Grounded Ice Shelf** | Pinning points, grounding zone rumples, or ephemeral contacts with bathymetric highs |
| **`3`** | **Floating Ice Shelf** | Hydrostatically floating marine-terminating ice shelves (e.g., Larsen C, George VI) |
| **`4`** | **Ice-Free Rock Outcrops** | Exposed nunataks, cliff faces, and mountain ridge crests |

### 1.2 Quantitative Audit of Class 2 (Transiently Grounded Ice)
Across our high-resolution $3,400 \times 2,600$ Antarctic Peninsula processing envelope (native 500 m grid), Class 2 is extremely sparse but glaciologically diagnostic:
* **Total Domain Pixels:** Exactly $64\text{ pixels}$ ($16.0\text{ km}^2$).
* **Mean Ice Thickness:** $550.6\text{ m}$ (range: $300\text{--}938\text{ m}$).
* **Total Ice Volume in Class 2:** $8.810\text{ km}^3$.
* **Within Continental Ice Sheet Boundary (`I-Ipp`, Graham Land):** Exactly $7\text{ pixels}$ ($1.75\text{ km}^2$, mean thickness $307.1\text{ m}$, volume $0.537\text{ km}^3$).
* **Outside Continental Polygons:** 57 pixels lie seaward in the grounding zones of the Larsen C, Ronne, and George VI ice shelves, representing bathymetric shoal contacts.

### 1.3 Implementation Policy
* **Primary Target:** Class 1 is strictly retained as **permanently grounded continental ice**.
* **Accounting:** Class 2 is retained in our processed database as a distinct category and reported separately. It is not discarded, nor is it conflated with floating shelf ice (Class 3) or permanently grounded ice (Class 1).
* **Code & Visualization:** Code comments and visualization scripts ([`src/geospatial/generate_phase2_maps.py`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/src/geospatial/generate_phase2_maps.py)) have been updated to represent Class 2 as transiently grounded ice.

---

## 2. Task 2: Audit of Baseline Volume Calculation Implementation

We audited the core geospatial volume integration algorithm that produced the reported $138,079.9\text{ km}^3$ baseline estimate.

### 2.1 Audit Checklist & Verification Results
1. **Mask Verification:**  
   * The calculation evaluated `(mask == 1) & (thickness > 0)`.
   * Only permanently grounded ice cells were summed. Floating shelves (Class 3, $>40,000\text{ km}^3$) and rock outcrops (Class 4) were completely excluded.
2. **Vertical Units:**  
   * Bedmap3 `bm3_thickness.tif` stores thickness as integer meters (`int16`).
   * No unit conversion errors (e.g., feet, decimeters) were present.
3. **NoData Handling:**  
   * NoData cells are flagged with `-9999`. The condition `thickness > 0` strictly eliminated all NoData values.
4. **Boundary Integrity & Polygon Overlap:**  
   * We audited the rasterization of the IMBIE drainage basins (`Hp-I`, `I-Ipp`, `Ipp-J`).
   * Evaluated mutual overlap between each pair of basin masks:
     $$\text{Overlap}(\text{Hp-I}, \text{I-Ipp}) = \mathbf{0}\text{ pixels}, \quad \text{Overlap}(\text{Hp-I}, \text{Ipp-J}) = \mathbf{0}\text{ pixels}, \quad \text{Overlap}(\text{I-Ipp}, \text{Ipp-J}) = \mathbf{0}\text{ pixels}$$
5. **Reconciliation with Unified Region:**  
   * Summing individual basin masks gave $222,148.2\text{ km}^2$ area and $138,079.9\text{ km}^3$ volume.
   * Masking the unified regional polygon (`unary_union`) yielded identical numbers:
     $$\Delta\text{Area} = \mathbf{0.0}\text{ km}^2, \quad \Delta\text{Volume} = \mathbf{0.0}\text{ km}^3$$

The implementation is verified to be mathematically flawless for projected Cartesian space.

---

## 3. Task 3: Investigation of EPSG:3031 Projection Area Distortion

### 3.1 Mathematical Foundation of Map Distortion
The Antarctic Polar Stereographic projection (**EPSG:3031**) is conformal (preserves angles locally), defined on the WGS 84 ellipsoid ($a = 6,378,137.0\text{ m}$, $e \approx 0.08181919$). Its standard parallel of true scale is $\phi_c = 71^\circ\text{S}$.

For any latitude $\phi$, the linear scale factor $k(\phi)$ is given by Snyder (1987):
$$k(\phi) = \frac{m_c}{t_c} \cdot \frac{t(\phi)}{m(\phi)}$$
where:
$$m(\phi) = \frac{\cos\phi}{\sqrt{1 - e^2 \sin^2\phi}}, \quad t(\phi) = \frac{\tan(\pi/4 - \phi/2)}{\left[\frac{1 - e\sin\phi}{1 + e\sin\phi}\right]^{e/2}}$$
Because the projection is conformal, the **areal scale factor** $m_A(\phi)$ is exactly the square of the linear scale factor:
$$m_A(\phi) = [k(\phi)]^2$$

### 3.2 Projected Cell Area vs. True Ground Area
In a Cartesian raster grid with projected resolution $\Delta X = 500\text{ m}$ and $\Delta Y = 500\text{ m}$, the projected cell area is:
$$A_{\text{proj}} = \Delta X \cdot \Delta Y = 250,000\text{ m}^2 = 0.25\text{ km}^2$$
However, the true physical ground area $A_{\text{ground}}$ on the ellipsoidal Earth's surface represented by that grid cell is:
$$A_{\text{ground}}(\phi) = \frac{A_{\text{proj}}}{m_A(\phi)} = \frac{0.25\text{ km}^2}{[k(\phi)]^2}$$

#### Scale Factor Variation Across Study Latitudes:
| Latitude ($\phi$) | Representative Region | Linear Scale $k$ | Areal Scale $m_A = k^2$ | True Cell Ground Area | Projected Area Distortion |
| :---: | :--- | :---: | :---: | :---: | :---: |
| **$-63^\circ\text{S}$** | Trinity Peninsula (Hope Bay) | $1.028796$ | $1.058422$ | $0.236201\text{ km}^2$ | **$+5.84\%$ (Overestimation)** |
| **$-65^\circ\text{S}$** | Central Graham Land / Larsen B | $1.020549$ | $1.041520$ | $0.240034\text{ km}^2$ | **$+4.15\%$ (Overestimation)** |
| **$-68^\circ\text{S}$** | Southern Graham Land / Margins | $1.009506$ | $1.019102$ | $0.245314\text{ km}^2$ | **$+1.91\%$ (Overestimation)** |
| **$-71^\circ\text{S}$** | **Standard Parallel (True Scale)** | **$1.000000$** | **$1.000000$** | **$0.250000\text{ km}^2$** | **$0.00\%$ (Exact)** |
| **$-73^\circ\text{S}$** | Central Palmer Land | $0.994490$ | $0.989010$ | $0.252778\text{ km}^2$ | **$-1.10\%$ (Underestimation)** |
| **$-75^\circ\text{S}$** | Southern Palmer Land / Ronne | $0.989626$ | $0.979359$ | $0.255269\text{ km}^2$ | **$-2.06\%$ (Underestimation)** |

### 3.3 Quantitative Impact on Area and Volume
Using our script [`src/geospatial/audit_distortion.py`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/src/geospatial/audit_distortion.py), we computed the pixel-by-pixel scale correction across the entire Peninsula:

$$V_{\text{corrected}} = \sum_{i=1}^{N} \text{thickness}_i \times A_{\text{ground}}(\phi_i) = \sum_{i=1}^{N} \text{thickness}_i \times \frac{0.25\text{ km}^2}{[k(\phi_i)]^2}$$

#### Comparison Table: Projected vs. Corrected Baseline Estimates
| Drainage Basin | Subregion | Metric | Projected ($0.25\text{ km}^2$) | True Ground (Corrected) | Absolute Difference | Relative Difference |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| **`Hp-I`** | Western Palmer Land | **Area**<br>**Volume** | $109,105.5\text{ km}^2$<br>$102,102.3\text{ km}^3$ | $109,958.0\text{ km}^2$<br>$103,060.5\text{ km}^3$ | $+852.5\text{ km}^2$<br>$+958.2\text{ km}^3$ | $+0.78\%$<br>$\mathbf{+0.94\%}$ |
| **`I-Ipp`** | Graham Land | **Area**<br>**Volume** | $53,821.0\text{ km}^2$<br>$12,472.2\text{ km}^3$ | $52,125.7\text{ km}^2$<br>$12,102.7\text{ km}^3$ | $-1,695.3\text{ km}^2$<br>$-369.5\text{ km}^3$ | $-3.15\%$<br>$\mathbf{-2.96\%}$ |
| **`Ipp-J`** | Eastern Palmer Land | **Area**<br>**Volume** | $59,221.8\text{ km}^2$<br>$23,505.4\text{ km}^3$ | $59,469.9\text{ km}^2$<br>$23,605.8\text{ km}^3$ | $+248.1\text{ km}^2$<br>$+100.4\text{ km}^3$ | $+0.42\%$<br>$\mathbf{+0.43\%}$ |
| **Total Continental** | **Antarctic Peninsula** | **Area**<br>**Volume** | **$222,148.2\text{ km}^2$**<br>**$138,079.9\text{ km}^3$** | **$221,553.6\text{ km}^2$**<br>**$138,769.0\text{ km}^3$** | **$-594.6\text{ km}^2$**<br>**$+689.1\text{ km}^3$** | **$-0.27\%$**<br>$\mathbf{+0.50\%}$ |
| **Peripheral Islands** | Alexander, Adelaide, etc. | **Area**<br>**Volume** | $76,053.5\text{ km}^2$<br>$23,736.5\text{ km}^3$ | $75,434.6\text{ km}^2$<br>$23,702.3\text{ km}^3$ | $-618.9\text{ km}^2$<br>$-34.2\text{ km}^3$ | $-0.81\%$<br>$\mathbf{-0.14\%}$ |

### 3.4 Independent Geodesic Validation on WGS 84 Ellipsoid
To confirm that the vectorized scale-factor area calculation does not introduce numerical approximation artifacts, we independently computed true geodesic polygon areas across the WGS 84 ellipsoid using Karney's algorithm (via `pyproj.Geod`):
* **Sampled Domain:** 125 representative cells spanning $-63^\circ\text{S}\text{ to }-75^\circ\text{S}$ and $-75^\circ\text{W}\text{ to }-55^\circ\text{W}$.
* **Max Absolute Disagreement:** $0.000018\text{ m}^2$ per $250,000\text{ m}^2$ cell ($0.00000001\%$, or $0.0001\text{ ppm}$).
* **Average Disagreement:** $0.000010\text{ m}^2$ ($0.00000000\%$).
* **RMS Disagreement:** $0.000010\text{ m}^2$.
This confirms that the point scale factor method agrees with rigorous ellipsoidal geodesic integrals to eight decimal places.

---

## 4. Task 4: Acquisition and Security Architecture for BedMachine V4.1

### 4.1 NASA Earthdata Authentication Architecture
MEaSUREs BedMachine Antarctica Version 4.1 (`NSIDC-0756`, released January 2026) is hosted on the NASA Earthdata Cloud (`nsidc-cumulus-prod-protected`). Access requires NASA Earthdata OAuth 2.0 authentication.

To satisfy all strict security constraints:
1. **Source Code Hygiene:** No passwords, tokens, or usernames are written in any Python source file.
2. **Execution Log Hygiene:** Authentication tokens are stripped from all terminal logs and error traces.
3. **Version Control Protection:** [`.gitignore`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/.gitignore) explicitly excludes `.env`, `.env.*`, `.netrc`, `_netrc`, `*.key`, and `*.token`.
4. **Browser-Based Token Workflow:** Users can generate an EDL user token via the NASA web portal without exposing their primary password.

### 4.2 Automated Acquisition Script
We created [`src/data_acquisition/acquire_bedmachine.py`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/src/data_acquisition/acquire_bedmachine.py). It implements:
* Loading from `.env` via `python-dotenv` if present, or inspecting `os.environ`.
* Non-interactive authentication via `earthaccess.login(strategy="environment")`.
* Verification of the granule ID: `NSIDC-0756_BedMachineAntarctica_19700101-20191001_V04.1.nc`.
* Cropping across dimensions $X \in [-2700000, -1400000]$ and $Y \in [250000, 1950000]$ meters.
* Export of the processed NetCDF: `data/processed/bedmachine_v4.1_peninsula_500m.nc`.

#### Instructions for User Token Configuration:
To activate automated download:
1. Log in at **[https://urs.earthdata.nasa.gov](https://urs.earthdata.nasa.gov)** in your browser.
2. Under your profile, click **"Generate Token"** (direct link: `https://urs.earthdata.nasa.gov/users/tokens`).
3. Click "Generate Token" and copy the token string.
4. In your terminal session, set:
   ```powershell
   $env:EARTHDATA_TOKEN = "your_copied_token"
   ```
   *(Or save it into a local `antarctic-ice-volume-prediction/.env` file as `EARTHDATA_TOKEN=your_copied_token`).*
5. Running `python src/data_acquisition/acquire_bedmachine.py` will complete download and domain cropping automatically.

---

## 5. Task 5: Bedmap3 vs. BedMachine V4.1 Comparison Framework

We engineered the comparative audit pipeline in [`src/geospatial/compare_baselines.py`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/src/geospatial/compare_baselines.py).

### 5.1 Grid & Transform Alignment Principles
Before performing pixel-by-pixel spatial arithmetic, the script verifies:
1. **Coordinate Reference System:** EPSG:3031 in both products.
2. **Affine Transform Spacing:** Confirms cell sizes $\Delta X = 500.0\text{ m}$ and $\Delta Y = 500.0\text{ m}$.
3. **Axis Orientation:** Checks whether $Y$-coordinates are ordered descending (top-down, north-to-south) or ascending, applying vertical flips (`np.flipud`) if required so that matrix row 0 corresponds to $Y_{\max} = 1,950,000\text{ m}$.

### 5.2 Mask Cross-Walk
The comparison pipeline reconciles the disparate categorical schemes:

| Physical Feature | Bedmap3 Code | BedMachine V4.1 Code | Differencing Policy |
| :--- | :---: | :---: | :--- |
| **Permanently Grounded Ice** | `1` | `2` | **Included in mutual thickness comparison** |
| **Transiently Grounded Ice** | `2` | `2` or `3` | Audited separately |
| **Floating Ice Shelf** | `3` | `3` | Audited separately (hydrostatic equilibrium) |
| **Ice-Free Rock Outcrop** | `4` | `1` | Excluded from ice thickness difference |
| **Open Ocean** | `-9999` / `0` | `0` | Excluded |

### 5.3 Methodological Differences Between Datasets
Neither dataset is treated as "ground truth":
* **Bedmap3:** Uses direct radio-echo sounding (RES) survey points interpolated via ordinary kriging and splines. High fidelity along survey tracks, but smooths steep subglacial troughs in data-sparse alpine valleys.
* **BedMachine V4.1:** Incorporates **IceBoost** (Maffezzoli et al., 2025; integrated as `source == 8`), an ensemble machine-learning model trained on ice velocity, surface elevation, and mass conservation constraints specifically tailored to the complex relief of the Antarctic Peninsula. BedMachine reports ice-equivalent thickness, requiring firn air depth adjustments when comparing with Bedmap3 surface-derived geometry.

---

## 6. Summary of Updated Basin-Level Baseline Statistics

The complete updated inventory for the Antarctic Peninsula baseline (incorporating mask corrections, area distortion quantification, and explicit disaggregation of spatial dispersion from measurement error):

| Region / Basin | Surface Classification | Pixel Count | Projected Area | True Ground Area | Projected Volume | True Ground Volume | Mean Ground Thickness | Spatial Dispersion ($\sigma_{\text{spatial}}$) | Mean Meas. Error ($\bar{\sigma}_{\text{meas}}$) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Basin `Hp-I`** | Grounded Ice (Class 1) | $436,422$ | $109,105.5\text{ km}^2$ | **$109,958.0\text{ km}^2$** | $102,102.3\text{ km}^3$ | **$103,060.5\text{ km}^3$** | **$937.3\text{ m}$** | $\pm 444.5\text{ m}$ | $\pm 99.9\text{ m}$ |
| | Transiently Grounded (Class 2) | $0$ | $0.0\text{ km}^2$ | **$0.0\text{ km}^2$** | $0.0\text{ km}^3$ | **$0.0\text{ km}^3$** | N/A | N/A | N/A |
| **Basin `I-Ipp`** | Grounded Ice (Class 1) | $215,284$ | $53,821.0\text{ km}^2$ | **$52,125.7\text{ km}^2$** | $12,472.2\text{ km}^3$ | **$12,102.7\text{ km}^3$** | **$232.2\text{ m}$** | $\pm 181.8\text{ m}$ | $\pm 105.3\text{ m}$ |
| | Transiently Grounded (Class 2) | $7$ | $1.75\text{ km}^2$ | **$1.69\text{ km}^2$** | $0.537\text{ km}^3$ | **$0.520\text{ km}^3$** | **$307.1\text{ m}$** | $\pm 88.4\text{ m}$ | $\pm 88.4\text{ m}$ |
| **Basin `Ipp-J`** | Grounded Ice (Class 1) | $236,887$ | $59,221.8\text{ km}^2$ | **$59,469.9\text{ km}^2$** | $23,505.4\text{ km}^3$ | **$23,605.8\text{ km}^3$** | **$396.9\text{ m}$** | $\pm 309.6\text{ m}$ | $\pm 126.3\text{ m}$ |
| | Transiently Grounded (Class 2) | $0$ | $0.0\text{ km}^2$ | **$0.0\text{ km}^2$** | $0.0\text{ km}^3$ | **$0.0\text{ km}^3$** | N/A | N/A | N/A |
| **Continental Total** | **Class 1 (Perm. Grounded)** | **$888,593$** | **$222,148.2\text{ km}^2$** | **$221,553.6\text{ km}^2$** | **$138,079.9\text{ km}^3$** | **$138,769.0\text{ km}^3$** | **$626.3\text{ m}$** | $\pm 478.9\text{ m}$ | $\pm 108.2\text{ m}$ |
| | **Class 2 (Transiently Grounded)** | **$7$** | **$1.75\text{ km}^2$** | **$1.69\text{ km}^2$** | **$0.537\text{ km}^3$** | **$0.520\text{ km}^3$** | **$307.1\text{ m}$** | $\pm 88.4\text{ m}$ | $\pm 88.4\text{ m}$ |
| **Peripheral Islands**| Grounded Island Ice Caps | $304,214$ | $76,053.5\text{ km}^2$ | **$75,434.6\text{ km}^2$** | $23,736.5\text{ km}^3$ | **$23,702.3\text{ km}^3$** | **$314.2\text{ m}$** | $\pm 298.4\text{ m}$ | $\pm 114.7\text{ m}$ |

---

## 7. Unresolved Uncertainties for Subsequent Phases

1. **Firn Air Depth Calibration:** Bedmap3 surface elevation includes the firn air column ($\sim 10\text{--}30\text{ m}$ depth), whereas BedMachine expresses thickness in ice-equivalent meters. When comparing total ice volume or training mass balance models, firn compaction models (e.g., IMAU-FDM) must be applied.
2. **Correlated Spatial Errors in Radar Interpolation:** As shown in Map 4, interpolation uncertainty reaches $\pm 200\text{--}350\text{ m}$ in mountainous terrain. When integrating volume over millions of cells, assuming grid errors are uncorrelated leads to severe underestimation of regional volume uncertainty. Spatial autocorrelation lengths ($10\text{--}50\text{ km}$) will be modeled during the formal uncertainty phase.
3. **Transient Grounding Zone Migration:** The $1.75\text{ km}^2$ of transiently grounded ice shelf in Basin `I-Ipp` reflects dynamic grounding line migration under tidal cycles and recent ice shelf thinning.

---

## 8. Status & User Action Items

- [x] Corrected Bedmap3 mask taxonomy across all documentation and plotting code.
- [x] Audited volume integration algorithms and verified boundary reconciliation.
- [x] Quantified EPSG:3031 map scale distortion and tabulated projected vs. true ground area/volume.
- [x] Implemented secure, browser-token-compatible BedMachine V4.1 acquisition module.
- [x] Built grid alignment and spatial differencing framework.
- [ ] **Awaiting User Action:** Provide/set `EARTHDATA_TOKEN` to trigger automated BedMachine V4.1 download and run spatial differencing, OR proceed directly to Phase 3.

