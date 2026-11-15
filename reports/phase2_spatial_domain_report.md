# Phase 2 Technical Report: Antarctic Peninsula Spatial Domain Definition and Baseline Geospatial Data Acquisition

**Project:** Antarctic Ice-Volume Prediction Using Machine Learning (Peninsula Focus to 2100)  
**Document:** Phase 2 Spatial Domain & Baseline Data Acquisition Report  
**Date:** November 2026  
**Status:** Complete (Awaiting User Review for Phase 3)  
**Author:** Geospatial Data Engineering & Machine Learning Team  

---

## Executive Summary

Phase 2 establishes the scientifically rigorous spatial domain and baseline geospatial data foundations for the Antarctic Peninsula ice-volume prediction framework. In accordance with Phase 2 project directives, we have:

1. **Defined the Spatial Boundary:** Formally adopted the official **IMBIE / MEaSUREs Antarctic Drainage Basin Delineations** (Rignot et al., 2011; RGI 7.0 Consortium, 2023), identifying the exact boundaries and identifiers for the Antarctic Peninsula: **Basin `Hp-I`** (Palmer Land West & Alexander Island), **Basin `I-Ipp`** (Graham Land & Larsen Shelves), and **Basin `Ipp-J`** (Eastern Palmer Land & Weddell margin).
2. **Standardized Coordinate Reference System:** Locked the analysis grid to **EPSG:3031** (*WGS 84 / Antarctic Polar Stereographic*, standard parallel $71^\circ\text{S}$, central meridian $0^\circ\text{E}$).
3. **Acquired Baseline Gridded Products:** Successfully downloaded and verified the official **Bedmap3** 500 m grids from the British Antarctic Survey / SCAR RAMADDA repository (`bm3_thickness.tif`, `bm3_masks.tif`, and `bm3_thickness_uncertainty.tif`).
4. **Inspected BedMachine Antarctica V4.1 Metadata:** Acquired official NASA NSIDC DAAC User Guides and public NASA Common Metadata Repository (CMR) UMM-G metadata for **MEaSUREs BedMachine Antarctica V4.1** (`NSIDC-0756.004`), verifying its parameters, dimensions, and IceBoost integration.
5. **Standardized Spatial Preprocessing:** Engineered zero-distortion, sub-pixel-aligned cropping pipelines that subset the continent-wide grids ($13,334 \times 13,334$ pixels) to an exact Antarctic Peninsula processing envelope ($3,400 \times 2,600$ pixels at native 500 m resolution), reducing file sizes from 1.1 GB to under 4 MB without resampling or interpolation.
6. **Produced Publication-Quality Cartographic Maps:** Generated 5 comprehensive visual maps (300 DPI) depicting basin boundaries, ice thickness, discrete surface classifications, thickness uncertainties, and basin hypsometric profiles.
7. **Documented Data Accessibility:** Documented the authentication gate for the BedMachine V4.1 NetCDF raster (requiring NASA Earthdata OAuth credentials), providing a clear mechanism for user authentication.

---

## 1. Study Region Spatial Domain Definition

### 1.1 Official Boundary Source and Basin Identifiers
Rather than using arbitrary rectangular bounding boxes that encompass open ocean or exclude critical mountain ridges, we base our spatial domain on the official **IMBIE (Ice Sheet Mass Balance Inter-comparison Exercise)** regional delineations, published jointly with NASA MEaSUREs (Rignot et al., 2011; Mouginot et al., 2017) and updated with the Randolph Glacier Inventory (RGI 7.0 Consortium, 2023).

* **Repository:** IMBIE Data Portal / NSIDC-0709
* **Shapefile:** `IMBIE_AIS_Regional_Delineations.shp`
* **NetCDF Grids:** `IMBIE_AIS_Regional_Delineations_1km.nc`, `5km.nc`, `10km.nc`
* **Coordinate System:** EPSG:3031

In this scientific standard, the Antarctic continent is divided into 18 major ice-drainage systems. The **Antarctic Peninsula** (`Region == 'Peninsula'`) comprises exactly three contiguous drainage basins:

| Basin Code | Historical ID | Glaciological Subregion | Continental Ice Sheet Area | Peripheral Islands Area | Total Subregion Area |
| :--- | :--- | :--- | :---: | :---: | :---: |
| **`Hp-I`** | Basin 24 / 25 | Western Palmer Land & Alexander Island Periphery | $110,265.5\text{ km}^2$ | $61,465.9\text{ km}^2$ | $171,731.4\text{ km}^2$ |
| **`I-Ipp`** | Basin 26 | Graham Land (Northern Peninsula & Larsen Margins) | $61,052.8\text{ km}^2$ | $18,731.8\text{ km}^2$ | $79,784.6\text{ km}^2$ |
| **`Ipp-J`** | Basin 27 | Eastern Palmer Land (Weddell Sea / Ronne Boundary) | $61,360.1\text{ km}^2$ | $2,037.3\text{ km}^2$ | $63,397.4\text{ km}^2$ |
| **Total** | **Basins 24–27** | **Antarctic Peninsula Domain** | **$232,678.4\text{ km}^2$** | **$83,235.0\text{ km}^2$** | **$315,913.4\text{ km}^2$** |

### 1.2 Reconciliation with Historical Basin Numbers (24–27)
In early satellite radar altimetry literature (Zwally et al., 2012; early MEaSUREs releases), Antarctic Peninsula basins were numbered 24, 25, 26, and 27:
- **Basin 24 & 25:** Palmer Land (Western and Bellingshausen Sea slopes), now standardized as **`Hp-I`**.
- **Basin 26:** Graham Land (northern spine up to Trinity Peninsula), now standardized as **`I-Ipp`**.
- **Basin 27:** Eastern Palmer Land (Weddell Sea drainage north of the Ronne Ice Shelf boundary), now standardized as **`Ipp-J`**.

### 1.3 Treatment of Islands and Peripheral Glaciers
A critical finding from our geospatial audit is that the IMBIE/MEaSUREs shapefile provides **explicit, separate polygon geometries** for:
1. `Type == 'Ice_sheet'`: Contiguous continental ice sheet and connected ice shelves ($232,678\text{ km}^2$).
2. `Type == 'Islands'`: Detached off-shore islands, ice caps, and archipelago glaciers ($83,235\text{ km}^2$).

Notable peripheral islands include:
- **Alexander Island** ($49,070\text{ km}^2$ in Basin `Hp-I`)
- **Adelaide Island** ($4,463\text{ km}^2$ in Basin `Hp-I`)
- **James Ross Island & Joinville Island group** ($2,598\text{ km}^2$ in Basin `I-Ipp`)
- **South Shetland Islands** ($3,687\text{ km}^2$ in Basin `I-Ipp`)

**Scientific Policy for This Project:**  
Our primary machine learning prediction target is the **grounded continental ice volume** (`Type == 'Ice_sheet'`). Peripheral islands are retained as a distinct, separable subset in our spatial database so that models can evaluate continental vs peripheral response modes independently without mixing dynamics.

### 1.4 Spatial Processing Envelope (Bounding Box)
Because Polar Stereographic coordinates are rotated relative to geographical meridians, rectangular bounding boxes in `EPSG:3031` encompass substantial ocean area. However, an I/O bounding box is required to crop large raster files efficiently.

Derived from the maximum polygon extents of Basins `Hp-I`, `I-Ipp`, and `Ipp-J`, plus a conservative **20 km buffer** (40 grid cells at 500 m) to ensure coastal and island margins are completely intact:

$$\begin{aligned}
X_{\min} &= -2,700,000.0\text{ m} \quad (-2,700\text{ km}) \\
X_{\max} &= -1,400,000.0\text{ m} \quad (-1,400\text{ km}) \quad (\Delta X = 1,300\text{ km}) \\
Y_{\min} &= 250,000.0\text{ m} \quad (250\text{ km}) \\
Y_{\max} &= 1,950,000.0\text{ m} \quad (1,950\text{ km}) \quad (\Delta Y = 1,700\text{ km})
\end{aligned}$$

---

## 2. Baseline Datasets & Detailed Variable Metadata

### 2.1 Bedmap3 Gridded Products (BAS / SCAR)
* **Lead Agency:** British Antarctic Survey (BAS) / SCAR
* **DOI:** [10.5285/2d0e4791-8e20-46a3-80e4-f5f6716025d2](https://doi.org/10.5285/2d0e4791-8e20-46a3-80e4-f5f6716025d2)
* **Citation:** Pritchard, H. D., Fretwell, P. T., et al. (2025). *Bedmap3 updated ice bed, surface and thickness gridded datasets for Antarctica*. Scientific Data, 12, 414.
* **Access Protocol:** Open Access (CC-BY-4.0), Direct HTTPS streaming via UK Polar Data Centre RAMADDA servlet.
* **Downloaded Files:**
  - `data/raw/bedmap3/bm3_thickness.tif` (344.7 MB)
  - `data/raw/bedmap3/bm3_masks.tif` (344.7 MB)
  - `data/raw/bedmap3/bm3_thickness_uncertainty.tif` (344.7 MB)
* **Native Grid Dimensions:** $13,334 \times 13,334$ pixels, 500 m resolution, origin at $[-3333500, 3333500]$ m.
* **NoData Value:** `-9999.0` (int16).
* **Mask Classification Scheme (Official Bedmap3 Publication, Pritchard et al., 2025):**
  - `-9999` / `0`: Open ocean / out-of-domain
  - `1`: Permanently grounded ice sheet
  - `2`: Transiently grounded ice shelf (grounding zone pinning points)
  - `3`: Floating ice shelf (e.g., Larsen C, George VI, Wilkins)
  - `4`: Ice-free exposed rock (nunataks and mountain ridges)

### 2.2 MEaSUREs BedMachine Antarctica Version 4.1 (NASA NSIDC DAAC)
* **Lead Agency:** NASA / UC Irvine / Dartmouth College / NSIDC DAAC
* **DOI:** [10.5067/POJQI54A45HX](https://doi.org/10.5067/POJQI54A45HX)
* **Dataset Identifier:** `NSIDC-0756` (Version 4.1, released January 2026)
* **Citation:** Morlighem, M. (2026). *MEaSUREs BedMachine Antarctica, Version 4.1*. NASA NSIDC DAAC.
* **Format:** Single NetCDF-4 file (`NSIDC-0756_BedMachineAntarctica_19700101-20191001_V04.1.nc`), 1,198,815,840 bytes (~1.12 GB).
* **Reference Elevation Epoch:** 2015 (REMA surface DEM).
* **Vertical Datum:** EIGEN-6C4 geoid (ice equivalent heights accounting for firn air depth).
* **Access Protocol:** NASA Earthdata Login required (OAuth 2.0 / Bearer token via `cumulus-prod-protected`).

#### Verified BedMachine Variable Specifications:
| NetCDF Variable | Data Type | Units | Description | Missing / Fill Value |
| :--- | :--- | :--- | :--- | :--- |
| `thickness` | float32 | meters | Ice thickness (ice-equivalent, firn-corrected) | `NaN` / `_FillValue` |
| `bed` | float32 | meters | Bed elevation relative to EIGEN-6C4 geoid | `NaN` / `_FillValue` |
| `surface` | float32 | meters | Surface elevation relative to EIGEN-6C4 geoid | `NaN` / `_FillValue` |
| `mask` | int8 | discrete | Ice/ocean mask: `0`=ocean, `1`=rock, `2`=grounded ice, `3`=floating shelf, `4`=Lake Vostok | None |
| `errbed` | float32 | meters | Bed elevation / ice thickness error | `NaN` / `_FillValue` |
| `firn` | float32 | meters | Firn air content depth | `NaN` / `_FillValue` |
| `geoid` | float32 | meters | Geoid undulation difference (EIGEN-6C4 minus WGS84) | `NaN` / `_FillValue` |
| `source` | int8 | discrete | Mapping method: `1`=REMA/IBCSO, `2`=Mass Conservation, `3`=Interpolation, `4`=Hydrostatic, `5`=IFPA, `6`=Gravity, `7`=Seismic, **`8`=IceBoost (Peninsula)**, `10`=Multibeam | None |
| `rgi` | int8 | discrete | Randolph Glacier Inventory v7.0 mask | `0` or `1` |

### 2.3 Side-by-Side Metadata Comparison

| Parameter / Feature | Bedmap3 (BAS / SCAR) | BedMachine Antarctica V4.1 (NASA NSIDC) | Reconciliation & Project Decision |
| :--- | :--- | :--- | :--- |
| **Coordinate System** | EPSG:3031 | EPSG:3031 | Identical native projection; no reprojection needed. |
| **Grid Cell Spacing** | 500 m | 500 m | Identical resolution; perfect integer alignment. |
| **Nominal Epoch** | Multi-decadal (~1960–2022) | 2015 (REMA surface) | Document as baseline snapshot; not time-series. |
| **Mask Encoding** | 1=Permanently Grounded, 2=Transiently Grounded, 3=Shelf, 4=Rock | 2=Grounded, 3=Shelf, 1=Rock, 4=Lake Vostok | Re-mapped to unified integer codes in preprocessing. |
| **Peninsula Method** | Kriging & spline interpolation | **IceBoost ML** (`source == 8`) | Key scientific comparison point for Phase 3. |
| **Uncertainty Grid** | Explicit thickness uncertainty grid | `errbed` (bed elevation error) | Both capture airborne radar line spacing. |
| **Firn Correction** | Integrated into surface | Separate `firn` variable | Explicit firn depth tracked in volume estimation. |

---

## 3. Spatial Preprocessing & Domain Standardization

### 3.1 Pixel Alignment Verification
A common error in geospatial workflows is using arbitrary bounding box crops that cause sub-pixel shifts or force bilinear resampling. We mathematically validated the raster bounds before cropping:

$$\begin{aligned}
\text{Origin } X_0 &= -3,333,500\text{ m}, \quad \text{Resolution } \Delta = 500.0\text{ m} \\
\text{Offset } \text{col}_{\text{start}} &= \frac{-2,700,000 - (-3,333,500)}{500} = \frac{633,500}{500} = \mathbf{1267.0} \quad (\text{Exact Integer}) \\
\text{Origin } Y_0 &= 3,333,500\text{ m} \\
\text{Offset } \text{row}_{\text{start}} &= \frac{3,333,500 - 1,950,000}{500} = \frac{1,383,500}{500} = \mathbf{2767.0} \quad (\text{Exact Integer}) \\
\text{Grid Width} &= \frac{1,300,000}{500} = \mathbf{2600} \text{ pixels} \\
\text{Grid Height} &= \frac{1,700,000}{500} = \mathbf{3400} \text{ pixels}
\end{aligned}$$

Because the pixel offsets and dimensions are exact integers, **every pixel extracted matches the raw source raster cell-for-cell without any interpolation, resampling, or shifting**.

### 3.2 Processed Datasets Generated
All processed files were exported to `data/processed/` using lossless DEFLATE compression:

1. `bedmap3_thickness_peninsula_500m.tif` ($3,400 \times 2,600$, 3.50 MB, raw size 344.7 MB $\rightarrow$ 99.0% reduction)
2. `bedmap3_masks_peninsula_500m.tif` ($3,400 \times 2,600$, 0.27 MB, raw size 344.7 MB $\rightarrow$ 99.9% reduction)
3. `bedmap3_uncertainty_peninsula_500m.tif` ($3,400 \times 2,600$, 1.27 MB, raw size 344.7 MB $\rightarrow$ 99.6% reduction)

---

## 4. Visual Inspection & Cartographic Products

All figures have been generated at 300 DPI, styled with standard polar glaciological color ramps, and saved in `reports/figures/`.

### Map 1: Antarctic Peninsula Study Domain & Drainage Basins
* **File:** [map1_peninsula_basins_domain.png](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/figures/map1_peninsula_basins_domain.png)  
* **Observations:** Demonstrates the spatial partition of the Antarctic Peninsula into Basin `Hp-I` (Palmer Land West, $110,266\text{ km}^2$), Basin `I-Ipp` (Graham Land, $61,053\text{ km}^2$), and Basin `Ipp-J` (Palmer Land East, $61,360\text{ km}^2$). Highlights peripheral islands (Alexander, Adelaide, James Ross) with distinct hatching.

### Map 2: Bedmap3 Baseline Ice Thickness
* **File:** [map2_bedmap3_thickness.png](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/figures/map2_bedmap3_thickness.png)  
* **Observations:** Shows the dramatic thickness gradient from the narrow, steep alpine glaciers of Graham Land (typically $100\text{--}400\text{ m}$) southward into the deep ice plateau of Palmer Land, where ice thickness frequently exceeds $1,800\text{--}2,500\text{ m}$.

### Map 3: Geospatial Ice Classification & Surface Masks
* **File:** [map3_bedmap3_classification_masks.png](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/figures/map3_bedmap3_classification_masks.png)  
* **Observations:** Delineates grounded ice sheet from the large floating ice shelves (Larsen C on the Weddell coast, George VI in the sound between Palmer Land and Alexander Island, Wilkins and Bach on the Bellingshausen margin). Nunataks and rock ridges (class 4) are prominently captured along the spine of the Antarctic Peninsula.

### Map 4: Bedmap3 Thickness Uncertainty Grid
* **File:** [map4_bedmap3_thickness_uncertainty.png](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/figures/map4_bedmap3_thickness_uncertainty.png)  
* **Observations:** Directly maps where airborne radar flight tracks were flown. Along surveyed flight lines, uncertainty drops to $\pm 30\text{--}50\text{ m}$. In data-sparse mountainous regions and inter-track gaps in Graham Land, uncertainty spikes to $\pm 150\text{--}350\text{ m}$.

### Map 5: Grounded Ice Thickness Frequency & Quantiles by Basin
* **File:** [map5_peninsula_thickness_distribution.png](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/figures/map5_peninsula_thickness_distribution.png)  
* **Observations:** Statistical distribution profiles highlight that Graham Land (`I-Ipp`) has a strongly right-skewed distribution centered at a median thickness of only $185\text{ m}$, whereas Western Palmer Land (`Hp-I`) exhibits a broad, high-volume distribution with a median of $920\text{ m}$.

---

## 5. Quantitative Baseline Ice Volume & Area Audit

Calculated strictly over grounded ice cells (`mask == 1` and `thickness > 0`) using the verified Bedmap3 baseline grids:

$$\text{Volume } (\text{km}^3) = \sum_{i=1}^{N} \text{thickness}_i \times \frac{(500\text{ m} \times 500\text{ m})}{10^9\text{ m}^3/\text{km}^3} = \sum_{i=1}^{N} \text{thickness}_i \times 0.00025$$

### 5.1 Continental Grounded Ice Sheet (Primary ML Prediction Target)
| Basin | Grounded Area ($\text{km}^2$) | Mean Thickness (m) | Median Thickness (m) | Max Thickness (m) | Grounded Ice Volume ($\text{km}^3$) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **`Hp-I` (W. Palmer Land)** | $109,105.5$ | $935.8 \pm 99.9$ | $920.0$ | $2,740.0$ | **$102,102.3$** |
| **`I-Ipp` (Graham Land)** | $53,821.0$ | $231.7 \pm 105.3$ | $185.0$ | $1,902.0$ | **$12,472.2$** |
| **`Ipp-J` (E. Palmer Land)** | $59,221.8$ | $396.9 \pm 126.3$ | $284.0$ | $2,460.0$ | **$23,505.4$** |
| **Continental Total** | **$222,148.2\text{ km}^2$** | **$621.6\text{ m}$** | **$540.0\text{ m}$** | **$2,740.0\text{ m}$** | **$138,079.9\text{ km}^3$** |

### 5.2 Peripheral Islands Grounded Ice (Separate Domain)
| Basin Islands | Grounded Area ($\text{km}^2$) | Mean Thickness (m) | Max Thickness (m) | Island Ice Volume ($\text{km}^3$) |
| :--- | :---: | :---: | :---: | :---: |
| **`Hp-I` Islands (Alexander, Adelaide)** | $58,519.5$ | $360.2 \pm 117.3$ | $2,250.0$ | **$21,078.4$** |
| **`I-Ipp` Islands (James Ross, Shetlands)** | $15,667.8$ | $137.3 \pm 105.6$ | $1,340.0$ | **$2,150.6$** |
| **`Ipp-J` Islands** | $1,866.2$ | $272.0 \pm 109.8$ | $980.0$ | **$507.6$** |
| **Islands Total** | **$76,053.5\text{ km}^2$** | **$312.1\text{ m}$** | **$2,250.0\text{ m}$** | **$23,736.5\text{ km}^3$** |

### 5.3 Glaciological Summary
1. **Palmer Land (`Hp-I`) contains 74.0%** of the Antarctic Peninsula continental grounded ice volume ($102,102.3\text{ km}^3$).
2. **Graham Land (`I-Ipp`) contains only 9.0%** of the continental ice volume ($12,472.2\text{ km}^3$), despite covering nearly 25% of the area, due to steep topography and thin alpine ice.
3. **Floating Ice Shelves:** Floating ice shelf volume across the Peninsula exceeds $40,000\text{ km}^3$ (predominantly the Larsen C and George VI shelves). In strict glaciological accounting, floating ice is in hydrostatic equilibrium with sea water; melting shelves do not directly raise sea level, but their loss removes buttressing on grounded outlet glaciers. Floating shelves must remain strictly excluded from the grounded ice volume target.

---

## 6. Data Quality, Missing Data & Access Status

### 6.1 MEaSUREs BedMachine Antarctica V4.1 Access Status
* **Endpoint:** `https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/MEASURES/NSIDC-0756/4/1970/01/01/NSIDC-0756_BedMachineAntarctica_19700101-20191001_V04.1.nc`
* **Access Barrier:** NASA Earthdata Cloud requires an active NASA Earthdata Login account (HTTP Basic Auth or OAuth token).
* **Investigation Result:** All public metadata, parameter tables, User Guides, and spatial extents have been acquired and verified. The Python environment has `earthaccess` installed and ready to authenticate.
* **Resolution Pathway:** Once the user provides or configures Earthdata credentials (via `EARTHDATA_USERNAME` and `EARTHDATA_PASSWORD` environment variables or `~/.netrc`), the automated pipeline will stream or download the BedMachine NetCDF file, apply the exact same cropping window, and generate the direct difference raster against Bedmap3.

### 6.2 Data Quality Considerations
1. **Radar Track Sparsity in Graham Land:** As revealed by Map 4, high relief along the Antarctic Peninsula spine makes airborne radar sounding hazardous. Interpolated values in high-elevation passes carry uncertainties of $\pm 100\text{--}300\text{ m}$.
2. **Firn Air Depth:** BedMachine reports ice-equivalent thickness, whereas Bedmap3 incorporates firn into total surface elevation. When comparing the two products, the firn depth layer ($10\text{--}30\text{ m}$) must be explicitly reconciled.

---

## 7. Deliverables Summary & Next Steps

### Completed Phase 2 Deliverables:
- [x] Defined and documented official spatial boundaries using MEaSUREs/IMBIE delineations.
- [x] Verified exact identifiers: Basins `Hp-I`, `I-Ipp`, `Ipp-J`, and isolated peripheral islands.
- [x] Downloaded, verified, and cropped Bedmap3 500 m thickness, mask, and uncertainty grids.
- [x] Inspected and documented BedMachine V4.1 parameters, dimensions, and metadata.
- [x] Generated 5 publication-quality cartographic figures in `reports/figures/`.
- [x] Quantified baseline grounded ice area and volume for all basins without inventing values.

### Next Phase Transition:
Per the project guidelines, no machine learning training, future projections, historical loss rates, or climate feature engineering have been performed. All baseline data pipelines are established. We now present this report for your review and approval before proceeding to the next phase.

