# Phase 2.2 Technical Report: BedMachine Acquisition Architecture, Thickness Harmonisation & Independent Geodesic Validation

**Project:** Antarctic Ice-Volume Prediction Using Machine Learning (Peninsula Focus to 2100)  
**Document:** Phase 2.2 Baseline Comparison & Scientific Validation Report  
**Date:** November 2026  
**Status:** Complete (Awaiting User Token Configuration / Approval for Phase 3)  
**Author:** Geospatial Data Engineering & Machine Learning Research Team  

---

## Executive Summary

Phase 2.2 establishes the definitive mathematical, glaciological, and security foundations required to execute a scientifically consistent comparison between the two preeminent digital elevation baselines of the Antarctic continent: the British Antarctic Survey / SCAR **Bedmap3** compilation and the NASA / UC Irvine **MEaSUREs BedMachine Antarctica Version 4.1**.

### Core Achievements & Scientific Deliverables:
1. **Thickness Convention Investigation:** Resolved the fundamental physical discrepancy between Bedmap3 and BedMachine. Bedmap3 reports **physical geometric column thickness** ($H_{\text{geom}} = \text{surface} - \text{bed}$), which includes the porous firn air column. BedMachine V4.1 reports **ice-equivalent thickness** ($H_{\text{ice-eq}}$) with firn air removed. Direct raw differencing is **not a like-for-like comparison** and systematically biases Bedmap3 upwards by $10\text{--}30\text{ m}$ of firn air. We formulated the exact harmonisation equation using the co-registered BedMachine `firn` parameter:
   $$H_{\text{geom}} = H_{\text{ice-eq}} + \text{firn}, \quad H_{\text{ice-eq}} = H_{\text{geom}} - \text{firn}$$
2. **Independent Geodesic Validation:** Evaluated the vectorized EPSG:3031 projection-scale-factor area correction against an independent geodesic polygon calculation on the WGS 84 ellipsoid across 125 representative grid cells spanning latitudes $-63^\circ\text{S}$ to $-75^\circ\text{S}$ and longitudes $-75^\circ\text{W}$ to $-55^\circ\text{W}$. The two independent mathematical formulations agree to within **$0.000018\text{ m}^2$ per $250,000\text{ m}^2$ cell** ($0.00000001\%$, or $0.0001\text{ ppm}$), establishing absolute precision.
3. **Rigorous Statistical Disaggregation:** Disentangled spatial variability ($\sigma_{\text{spatial}}$, standard deviation of terrain thickness) from observational measurement uncertainty ($\bar{\sigma}_{\text{meas}}$, airborne radar error). Computed corrected area-weighted mean thicknesses:
   $$\bar{H}_{\text{ground}} = \frac{\sum H_i \cdot A_{\text{ground}, i}}{\sum A_{\text{ground}, i}}$$
   Confirming that true ground-weighted continental ice thickness across the Peninsula is **$626.3\text{ m}$** (compared to unweighted projected $621.6\text{ m}$).
4. **Secure Earthdata Acquisition Pipeline:** Engineered a token-compatible acquisition script ([`src/data_acquisition/acquire_bedmachine.py`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/src/data_acquisition/acquire_bedmachine.py)) that enforces zero-compromise credential security (no source code storage, no terminal printing, strict `.gitignore` exclusion). Ready to download and crop BedMachine V4.1 the moment the user configures their local browser token via `$env:EARTHDATA_TOKEN` or a local `.env` file.
5. **Structural Uncertainty Framework:** Established that differences between Bedmap3 and BedMachine reflect structural modeling differences (ordinary kriging vs. IceBoost machine learning) and observational sparsity, rather than historical glacier retreat.

---

## 1. Task 1: Earthdata Authentication Architecture & Acquisition Pipeline

### 1.1 Credential Security Constraints
Per project directives, strict security controls govern the acquisition of protected NASA Earthdata assets:
* **No Plaintext Source Embedding:** Credentials, usernames, passwords, and tokens are never written into Python scripts.
* **No Terminal Leaks:** Standard out and standard error logs never echo credentials.
* **Git Hygiene:** [`.gitignore`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/.gitignore) strictly ignores `.env`, `.env.*`, `.netrc`, `_netrc`, `*.key`, and `*.token`.
* **Explicit Environment Loading:** Rather than assuming third-party libraries auto-discover configuration, our pipeline uses `python-dotenv` with explicit multi-path search order:
  1. `find_dotenv(usecwd=True)` (hierarchical parent-directory traversal).
  2. `antarctic-ice-volume-prediction/.env` (project root).
  3. `~/.env` (user profile).
  4. System environment variable: `EARTHDATA_TOKEN`.

### 1.2 Acquisition Workflow Implementation
The acquisition pipeline is codified in [`src/data_acquisition/acquire_bedmachine.py`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/src/data_acquisition/acquire_bedmachine.py):

```python
# Execution Workflow in acquire_bedmachine.py:
1. Load environment variables via python-dotenv.
2. Check presence of EARTHDATA_TOKEN (or EARTHDATA_USERNAME + EARTHDATA_PASSWORD).
3. If absent: Halt gracefully and display official browser token generation steps.
4. If present: Authenticate non-interactively via earthaccess.login(strategy="environment").
5. Search CMR: short_name="NSIDC-0756", version="4".
6. Download granule: NSIDC-0756_BedMachineAntarctica_19700101-20191001_V04.1.nc (1.12 GB).
7. Validate integrity: File size exactly 1,198,815,840 bytes.
8. Crop spatial domain: X in [-2700000, -1400000] m, Y in [250000, 1950000] m (EPSG:3031).
9. Save processed NetCDF: data/processed/bedmachine_v4.1_peninsula_500m.nc.
```

### 1.3 How the User Configures the Token
To initiate download without exposing passwords:
1. Log in to NASA Earthdata at **[https://urs.earthdata.nasa.gov](https://urs.earthdata.nasa.gov)**.
2. Navigate to **[Generate Token](https://urs.earthdata.nasa.gov/users/tokens)** under your profile.
3. Click "Generate Token" and copy the token string.
4. Set it in your local environment:
   ```powershell
   $env:EARTHDATA_TOKEN = "your_token_string"
   ```
   *(Or save it into a local `antarctic-ice-volume-prediction/.env` file as `EARTHDATA_TOKEN=your_token_string`).*
5. Run the acquisition script:
   ```powershell
   .\antarctic-ice-volume-prediction\.venv\Scripts\python.exe antarctic-ice-volume-prediction/src/data_acquisition/acquire_bedmachine.py
   ```

---

## 2. Task 2: Critical Investigation of Thickness Definitions

A fundamental pitfall in Antarctic glaciological data science is assuming that "thickness" in different compilations measures the identical physical quantity.

### 2.1 Bedmap3 Thickness Definition
* **Source:** Pritchard, Fretwell, et al. (2025), *Scientific Data*, 12, 414.
* **Physical Basis:** Bedmap3 integrates over six decades of radio-echo sounding (RES) data. Radar travel time is converted using electromagnetic wave velocity in glacier ice, calibrated with firn corrections so that the calculated depth reaches the true physical snow surface.
* **Mathematical Definition:** **Physical Geometric Column Thickness ($H_{\text{geom}}$)**:
  $$H_{\text{Bedmap3}} = H_{\text{geom}} = z_{\text{surface}} - z_{\text{bed}}$$
* **Implication:** Bedmap3 thickness represents the full geometric column from bedrock up to the ambient snow surface, including the low-density, air-filled pores of the upper firn layer ($\sim 10\text{--}30\text{ m}$).

### 2.2 MEaSUREs BedMachine Antarctica V4.1 Thickness Definition
* **Source:** Morlighem (2026), NSIDC-0756 V4.1 User Guide; Morlighem et al. (2020), *Nature Geoscience*, 13, 132–137.
* **Physical Basis:** BedMachine solves mass conservation ($\nabla \cdot (\bar{u} H) = \text{SMB} - \frac{\partial H}{\partial t}$) using regional atmospheric climate model inputs (RACMO2 SMB).
* **Mathematical Definition:** **Ice-Equivalent Thickness ($H_{\text{ice-eq}}$)**:
  $$H_{\text{BedMachine}} = H_{\text{ice-eq}} = \frac{1}{\rho_{\text{pure}}} \int_{z_{\text{bed}}}^{z_{\text{surface}}} \rho(z) \, dz$$
  where $\rho_{\text{pure}} = 917\text{ kg/m}^3$.
* **Implication:** BedMachine mathematically compresses all air pores in the firn layer to solid ice density. The height of the air column is extracted into a dedicated parameter:
  $$\text{FAC} = \text{firn} \quad (\text{Firn Air Content depth in meters})$$

### 2.3 Required Conversions for Like-for-Like Comparison
Because $H_{\text{Bedmap3}}$ includes firn air and $H_{\text{BedMachine}}$ excludes firn air:

$$\mathbf{H_{\text{Bedmap3}} > H_{\text{BedMachine}} \quad \text{by approximately } \mathbf{\text{FAC}} \sim 10\text{--}30\text{ m}}$$

#### Scientifically Consistent Harmonisation Framework:
1. **Raw Product Difference (NOT Like-for-Like):**
   $$\Delta H_{\text{raw}} = H_{\text{BedMachine}} - H_{\text{Bedmap3}}$$
   *Bias:* BedMachine will appear artificially thinner across the entire high plateau simply because firn air is missing from its thickness variable. This map is preserved strictly as a baseline audit, clearly labeled: `NOT A LIKE-FOR-LIKE COMPARISON`.
2. **Harmonised Geometric Comparison (True Physical Geometry):**
   $$H_{\text{BedMachine, geom}} = H_{\text{BedMachine}} + \text{firn}$$
   $$\Delta H_{\text{geom}} = (H_{\text{BedMachine}} + \text{firn}) - H_{\text{Bedmap3}}$$
   *Physical Meaning:* Compares the true physical column height from bed to snow surface for both products.
3. **Harmonised Ice-Equivalent Comparison (True Mass / Ice Equivalent):**
   $$H_{\text{Bedmap3, ice-eq}} = H_{\text{Bedmap3}} - \text{firn}$$
   $$\Delta H_{\text{ice-eq}} = H_{\text{BedMachine}} - (H_{\text{Bedmap3}} - \text{firn})$$
   *Physical Meaning:* Compares the pure solid ice mass column for both products.
   *(Note: Mathematically, $\Delta H_{\text{geom}} \equiv \Delta H_{\text{ice-eq}}$, ensuring consistency across both perspectives).*

---

## 3. Task 3: Comparison Framework & Structural Uncertainty

Our comparison module ([`src/geospatial/compare_baselines.py`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/src/geospatial/compare_baselines.py)) implements these principles:

### 3.1 Grid & Transform Audit
* **CRS:** Identical polar stereographic projection (`EPSG:3031`, standard parallel $-71^\circ\text{S}$).
* **Origin & Bounds:** Locked to $X \in [-2700000, -1400000]\text{ m}$, $Y \in [250000, 1950000]\text{ m}$.
* **Cell Alignment:** Native $500.0\text{ m} \times 500.0\text{ m}$ spacing with exact integer offsets.
* **Orientation:** Checks row coordinate monotonicity and aligns both rasters top-down ($Y_{\max}$ to $Y_{\min}$).

### 3.2 Methodological Divergence (Kriging vs. Machine Learning)
It is critical to document that **neither dataset represents infallible ground truth**:
* **Bedmap3 (Ordinary Kriging & Splines):** Direct interpolation between flight lines. Where flight tracks are dense (e.g., parts of Palmer Land), Bedmap3 captures radar reflections with high fidelity. However, in data-sparse alpine valleys (Graham Land), kriging smooths over deep glacial troughs, overestimating bed elevation and underestimating valley ice thickness.
* **BedMachine Antarctica V4.1 (IceBoost ML):** Integrates **IceBoost** (Maffezzoli et al., 2025; integrated as `source == 8`), an ensemble machine learning architecture trained on ice velocity, surface slopes, and mass conservation constraints specifically designed to resolve the narrow outlet troughs of the Antarctic Peninsula.
* **Temporal Vintage Limitation:** BedMachine uses the REMA surface DEM (nominal epoch 2015), whereas Bedmap3 is a multi-decadal data compilation (~1960–2022). Discrepancies between the two **must not be interpreted as historical glacier retreat**; they represent differences in subglacial interpolation methodology and observation density.

---

## 4. Task 4: Independent Geodesic Validation of Area Distortion

To validate the scale-factor area calculation in `src/geospatial/audit_distortion.py`, we executed an independent mathematical validation using Karney's geodesic polygon area algorithm on the WGS 84 ellipsoid (via `pyproj.Geod`).

### 4.1 Methodology
For representative grid cells across the Antarctic Peninsula:
1. Defined projected cell corner coordinates in EPSG:3031:
   $$(X \pm \Delta/2, \, Y \pm \Delta/2) \quad \text{where } \Delta = 500.0\text{ m}$$
2. Inversely projected each corner to geographic coordinates $(\lambda, \phi)$ on the WGS 84 ellipsoid.
3. Calculated true ellipsoidal polygon area $A_{\text{geodesic}}$ using Charles Karney's rigorous geodesic algorithm (`geod.polygon_area_perimeter`).
4. Computed point scale factor cell area:
   $$A_{\text{scale}} = \frac{(500\text{ m} \times 500\text{ m})}{[k(\phi_0)]^2} = \frac{0.25\text{ km}^2}{m_A(\phi_0)}$$
5. Compared $A_{\text{scale}}$ and $A_{\text{geodesic}}$.

### 4.2 Validation Results Across Study Domain
Sampled 125 representative grid cells across the entire longitudinal ($-75^\circ\text{W}$ to $-55^\circ\text{W}$) and latitudinal ($-63^\circ\text{S}$ to $-75^\circ\text{S}$) extent:

$$\begin{aligned}
\text{Sampled Cells} &= 125 \\
\text{Max Absolute Disagreement} &= \mathbf{0.000018\text{ m}^2} \quad \mathbf{(0.00000001\% \text{ of a } 250,000\text{ m}^2 \text{ cell})} \\
\text{Average Disagreement} &= \mathbf{0.000010\text{ m}^2} \quad \mathbf{(0.00000000\%)} \\
\text{RMS Disagreement} &= \mathbf{0.000010\text{ m}^2}
\end{aligned}$$

#### Latitude-by-Latitude Disagreement Table:
| Latitude | Representative Geographic Location | Geodesic Area ($A_{\text{geodesic}}$) | Scale Factor Area ($A_{\text{scale}}$) | Absolute Disagreement | Relative Disagreement |
| :---: | :--- | :---: | :---: | :---: | :---: |
| **$-63.0^\circ\text{S}$** | Trinity Peninsula (Hope Bay) | $236,200.7944\text{ m}^2$ | $236,200.7944\text{ m}^2$ | $+0.000007\text{ m}^2$ | $+0.00000000\%$ |
| **$-65.0^\circ\text{S}$** | Central Graham Land / Larsen B | $240,033.7321\text{ m}^2$ | $240,033.7321\text{ m}^2$ | $+0.000011\text{ m}^2$ | $+0.00000000\%$ |
| **$-67.0^\circ\text{S}$** | Marguerite Bay / Adelaide Island | $243,618.2748\text{ m}^2$ | $243,618.2749\text{ m}^2$ | $+0.000016\text{ m}^2$ | $+0.00000001\%$ |
| **$-69.0^\circ\text{S}$** | Northern Palmer Land / Wilkins | $246,943.6986\text{ m}^2$ | $246,943.6986\text{ m}^2$ | $+0.000010\text{ m}^2$ | $+0.00000000\%$ |
| **$-71.0^\circ\text{S}$** | **Standard Parallel (True Scale)** | **$250,000.0000\text{ m}^2$** | **$250,000.0000\text{ m}^2$** | **$+0.000013\text{ m}^2$** | **$+0.00000000\%$** |
| **$-73.0^\circ\text{S}$** | Central Palmer Land Plateau | $252,777.9394\text{ m}^2$ | $252,777.9394\text{ m}^2$ | $+0.000012\text{ m}^2$ | $+0.00000000\%$ |
| **$-75.0^\circ\text{S}$** | Southern Palmer Land / Ronne | $255,269.0810\text{ m}^2$ | $255,269.0810\text{ m}^2$ | $+0.000002\text{ m}^2$ | $+0.00000000\%$ |

**Mathematical Proof of Validity:**  
Because a 500 m grid cell is small relative to the Earth's radius of curvature ($R \approx 6,378\text{ km}$), the scale factor across a single cell is essentially constant. The maximum possible second-order Taylor expansion term is:
$$\Delta A \approx \frac{\Delta^4}{24 R^2} \sim 10^{-5}\text{ m}^2$$
The vectorized scale-factor method in [`src/geospatial/audit_distortion.py`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/src/geospatial/audit_distortion.py) is thus confirmed to be exact to eight decimal places.

---

## 5. Task 5: Clarified Descriptive Statistics & Rigorous Disaggregation

To eliminate ambiguity, all basin-level statistics are strictly disaggregated:
1. **$\sigma_{\text{spatial}}$ (Spatial Dispersion / Standard Deviation):** Measures natural geographic variation across the terrain (coastal margins to mountain divides). It is **not** an error or uncertainty metric.
2. **$\bar{\sigma}_{\text{meas}}$ (Observational Measurement Uncertainty):** Sourced from the Bedmap3 radar uncertainty grid (`bm3_thickness_uncertainty.tif`). Represents instrument and interpolation error.
3. **Area-Weighted Mean Thickness ($\bar{H}_{\text{ground}}$):**
   $$\bar{H}_{\text{ground}} = \frac{V_{\text{ground}}}{A_{\text{ground}}} = \frac{\sum H_i \cdot A_{\text{ground}, i}}{\sum A_{\text{ground}, i}}$$
   Computed using cell-specific geodesic scale factors rather than simple arithmetic unweighted averaging.

### 5.1 Definitive Basin-Level Baseline Inventory (Bedmap3 Grounded Ice)

| Drainage Basin | Metric | Projected (Uncorrected) | True Ground (Corrected) | Spatial Dispersion ($\sigma_{\text{spatial}}$) | Observational Uncertainty ($\bar{\sigma}_{\text{meas}}$) |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Basin `Hp-I`**<br>*(W. Palmer Land)* | **Area**<br>**Volume**<br>**Mean Thickness** | $109,105.5\text{ km}^2$<br>$102,102.3\text{ km}^3$<br>$935.8\text{ m}$ | **$109,958.0\text{ km}^2$**<br>**$103,060.5\text{ km}^3$**<br>**$937.3\text{ m}$** | —<br>—<br>$\pm 444.5\text{ m}$ | —<br>—<br>$\pm 99.9\text{ m}$ |
| **Basin `I-Ipp`**<br>*(Graham Land)* | **Area**<br>**Volume**<br>**Mean Thickness** | $53,821.0\text{ km}^2$<br>$12,472.2\text{ km}^3$<br>$231.7\text{ m}$ | **$52,125.7\text{ km}^2$**<br>**$12,102.7\text{ km}^3$**<br>**$232.2\text{ m}$** | —<br>—<br>$\pm 181.8\text{ m}$ | —<br>—<br>$\pm 105.3\text{ m}$ |
| **Basin `Ipp-J`**<br>*(E. Palmer Land)* | **Area**<br>**Volume**<br>**Mean Thickness** | $59,221.8\text{ km}^2$<br>$23,505.4\text{ km}^3$<br>$396.9\text{ m}$ | **$59,469.9\text{ km}^2$**<br>**$23,605.8\text{ km}^3$**<br>**$396.9\text{ m}$** | —<br>—<br>$\pm 309.6\text{ m}$ | —<br>—<br>$\pm 126.3\text{ m}$ |
| **Total Continental**<br>*(Antarctic Peninsula)* | **Area**<br>**Volume**<br>**Mean Thickness** | **$222,148.2\text{ km}^2$**<br>**$138,079.9\text{ km}^3$**<br>**$621.6\text{ m}$** | **$221,553.6\text{ km}^2$**<br>**$138,769.0\text{ km}^3$**<br>**$626.3\text{ m}$** | —<br>—<br>$\pm 478.9\text{ m}$ | —<br>—<br>$\pm 108.2\text{ m}$ |
| **Peripheral Islands**<br>*(Alexander, Adelaide, etc.)*| **Area**<br>**Volume**<br>**Mean Thickness** | $76,053.5\text{ km}^2$<br>$23,736.5\text{ km}^3$<br>$312.1\text{ m}$ | **$75,434.6\text{ km}^2$**<br>**$23,702.3\text{ km}^3$**<br>**$314.2\text{ m}$** | —<br>—<br>$\pm 298.4\text{ m}$ | —<br>—<br>$\pm 114.7\text{ m}$ |

---

## 6. Summary of Remaining Scientific Limitations

1. **Spatial Autocorrelation in Error Propagation:** The regional observational uncertainty ($\pm 108.2\text{ m}$) represents the average point-wise radar error. Because radar interpolation errors are strongly autocorrelated over flight-line spacing ($10\text{--}50\text{ km}$), regional volume uncertainty cannot be calculated by dividing by $\sqrt{N}$. Full spatial covariance modeling will be implemented in the uncertainty quantification phase.
2. **Ice Shelf Grounding Zone Ephemerality:** The $1.75\text{ km}^2$ of transiently grounded ice shelf (Class 2) detected in Graham Land indicates pinning point sensitivity to tidal deflection and ice shelf thinning.
3. **Temporal Asynchrony:** Bedmap3 represents a multi-decadal compilation centered on airborne surveys from the 1970s to 2020s, whereas BedMachine V4.1 references the 2015 REMA surface. Inter-product differences must be evaluated as structural methodology uncertainty, not historical thinning.

---

## 7. Deliverables & Next Step

- [x] Verified BedMachine V4.1 metadata and variables.
- [x] Documented and resolved the physical thickness definition mismatch (firn air correction).
- [x] Validated map distortion independently with Karney's WGS84 geodesic algorithm ($< 0.00000001\%$ error).
- [x] Disentangled spatial variability from measurement uncertainty in all basin tables.
- [x] Updated [`dataset_sources.md`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/dataset_sources.md) and [`reports/phase2_1_baseline_validation.md`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/phase2_1_baseline_validation.md).
- [x] Built the secure acquisition module ([`src/data_acquisition/acquire_bedmachine.py`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/src/data_acquisition/acquire_bedmachine.py)) and comparative audit pipeline ([`src/geospatial/compare_baselines.py`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/src/geospatial/compare_baselines.py)).
- [ ] **Awaiting User Token:** Once you set `$env:EARTHDATA_TOKEN = "your_token"` (or save it into `.env`), run `python src/data_acquisition/acquire_bedmachine.py` and `python src/geospatial/compare_baselines.py` to trigger the download and generate the dual difference maps.

