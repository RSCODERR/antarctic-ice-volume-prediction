# Antarctic Ice-Volume Prediction Using Machine Learning

A research-oriented machine learning project designed to estimate historical ice volume and predict future ice-volume changes across the **Antarctic Peninsula up to the year 2100** under diverse climate pathways (SSP1-2.6, SSP2-4.5, SSP5-8.5).

---

## 1. Project Overview & Motivation

The Antarctic Peninsula (AP) is one of the most rapidly warming regions on Earth, characterized by rugged alpine topography, narrow outlet glaciers, and sensitive ice shelves (e.g., Larsen A, B, and C). Accurately estimating current ice volume and forecasting future retreat requires bridging observational satellite data with climate forcings and physical principles.

This project implements an incremental, scientifically rigorous workflow to:
1. Establish a verified baseline of ice thickness, bed topography, and ice volume.
2. Track historical mass and volume changes from satellite altimetry, gravimetry, and velocity fields.
3. Train and validate machine learning architectures to predict ice-volume evolution at key milestones (**2030, 2040, 2050, 2075, and 2100**).
4. Quantify uncertainties across observational measurements and future climate scenarios.

---

## 2. Core Scientific Principles & Rules

Cryospheric data science requires strict adherence to physical definitions:
* **Grounded Ice vs. Floating Ice Shelves:**
  * Grounded ice rests directly on the subglacial bedrock. Loss of grounded ice directly raises global mean sea level (GMSL).
  * Floating ice shelves displace seawater according to Archimedes' principle; their melting does not directly raise sea level, but their buttressing protects upstream grounded ice.
  * *Implementation Rule:* Grounded ice and floating ice shelves must be partitioned using categorical mask variables (e.g., `mask == 2` for grounded vs. `mask == 3` for floating shelves in BedMachine Antarctica).
* **Ice Volume vs. Ice Mass:**
  * Ice volume ($V$, measured in $\text{km}^3$ or $\text{m}^3$) is geometric.
  * Ice mass ($M$, measured in Gigatons, $\text{Gt}$, where $1\text{ Gt} = 10^9\text{ tonnes} = 10^{12}\text{ kg}$) depends on density.
  * Pure glacier ice has a standard density $\rho_{\text{ice}} \approx 917\text{ kg/m}^3$ (or $0.917\text{ Gt/km}^3$).
  * Near-surface firn contains air pores with variable density ($\sim 300\text{--}800\text{ kg/m}^3$). Firn air content (FAC) must be accounted for when converting volume to mass or interpreting surface-elevation changes.
* **Coordinate Reference System (CRS):**
  * All geospatial calculations, area summations, and volume integrations are computed in **Antarctic Polar Stereographic** (`EPSG:3031`, standard parallel $71^\circ\text{S}$, WGS 84 ellipsoid), never in unprojected geographic degrees (`EPSG:4326`).
* **Elevation Change Interpretation:**
  * Surface-height changes ($\Delta h / \Delta t$, e.g., from ICESat-2) reflect a combination of ice-dynamical thinning, snow accumulation fluctuations, and firn compaction. They are not assumed to equal direct ice volume loss without calibration against surface mass balance (SMB) and firn models.
* **Data Provenance & Integrity:**
  * Source datasets are kept immutable in `data/raw/`.
  * Observations, derived products, ML predictions, and numerical physical models (e.g., ISMIP6) are strictly distinguished.
  * **ISMIP6 Provenance Standard:** Official scalar projections originate strictly from Zenodo DOI [`10.5281/zenodo.3940766`](https://doi.org/10.5281/zenodo.3940766) (*Seroussi et al., 2020*). The invalid legacy identifier `Zenodo 3897711` is permanently purged. Control simulation dynamic drift must be subtracted prior to ML integration. Native ISMIP6 simulations do not exist for SSP2-4.5.

---

## 3. Directory Layout

```text
antarctic-ice-volume-prediction/
│
├── data/
│   ├── raw/                 # Immutable source datasets (never modified or committed)
│   ├── processed/           # Cropped, reprojected, harmonized Antarctic Peninsula grids
│   └── features/            # Extracted spatial & tabular ML feature matrices
│
├── notebooks/               # Step-by-step exploratory analysis and pedagogical notebooks
│
├── src/                     # Modular Python package
│   ├── data_acquisition/    # Download utilities, API clients, and integrity checks
│   ├── preprocessing/       # Masking, reprojection, and raster alignment
│   ├── geospatial/          # Coordinate transforms, glacier outline filtering, GIS ops
│   ├── volume_calculation/  # Ice thickness integration, area-weighted volume & uncertainty
│   ├── feature_engineering/ # Spatial lag features, climate anomalies, elevation statistics
│   ├── models/              # Model architectures, training pipelines, and baselines
│   └── evaluation/          # Cross-validation, spatial blocking, uncertainty metrics
│
├── reports/                 # Scientific feasibility reports, benchmark summaries, and charts
│   └── dataset_feasibility_report.md
│
├── models/                  # Serialized trained model weights, scalers, and hyperparameters
│
├── dataset_sources.md       # Citations, persistent DOIs, and access instructions
├── requirements.txt         # Minimal initial Python dependencies
├── README.md                # Project documentation and guide
└── .gitignore               # Comprehensive Git ignore rules for geospatial/cryo data
```

---

## 4. Initial Technology Stack

The project uses Python 3.12+ with modular scientific libraries selected specifically for geospatial and cryospheric data:

| Library | Purpose & Scientific Role |
| :--- | :--- |
| **NumPy** | High-performance N-dimensional array calculations for pixel grids, thickness arrays, and elevation math. |
| **Pandas** | Tabular timeseries manipulation, regional mass balance tables (IMBIE), and hypsometric statistics. |
| **SciPy** | Spatial interpolation, sparse matrices, and numerical integration over complex bedrock topography. |
| **Xarray** | Labeled multidimensional arrays; primary tool for NetCDF/HDF5 climate and ice-sheet datasets. |
| **netCDF4 / h5netcdf** | Low-level C/HDF5 backends enabling Xarray to open high-resolution satellite and model grids. |
| **Rasterio** | GDAL-backed geospatial raster reading, georeferencing, affine transformations, and windowed I/O. |
| **Rioxarray** | Geospatial extension for Xarray, facilitating projected CRS handling (`EPSG:3031`), clipping, and resampling. |
| **GeoPandas & Shapely** | Vector geometries for glacier basin outlines (GLIMS/RGI), grounding lines, and ice divide polygons. |
| **PyProj** | Cartographic transformations, geodesic area calculation, and ellipsoid parameter handling. |
| **Matplotlib** | Visualizing spatial maps, ice thickness profiles, and mass balance timeseries. |
| **Requests** | Programmatic verification and retrieval of open metadata records from scientific data archives. |

*Note: Machine learning frameworks (Scikit-Learn, XGBoost) and advanced APIs (Earthaccess) are scheduled for installation in subsequent phases when feature matrices are prepared.*

---

## 5. Getting Started & Environment Setup

### Prerequisites
* Python 3.12 installed on your system.
* Windows PowerShell, Linux bash, or macOS zsh terminal.

### Setup Instructions

1. **Activate the Virtual Environment:**
   * On Windows:
     ```powershell
     .\.venv\Scripts\Activate.ps1
     ```
   * On Linux/macOS:
     ```bash
     source .venv/bin/activate
     ```

2. **Verify Dependencies:**
   ```bash
   python -m pip install -r requirements.txt
   ```

3. **Check Environment Status:**
   ```bash
   python -c "import numpy, pandas, xarray, rasterio, geopandas; print('All core geospatial libraries imported successfully!')"
   ```

---

## 6. Project Roadmap & Execution History

* **Phase 1: Project Initialization & Feasibility Study (Completed)**
  * Repository initialization, dependency setup, and scientific evaluation of 8 candidate datasets.
* **Phase 2: Antarctic Peninsula Spatial Domain Definition & Baseline Volume (Completed)**
  * Spatial domain harmonization, BedMachine v4 integration, grounded vs shelf partitioning, and grid area distortion corrections.
* **Phase 3: Baseline Volume Uncertainty Propagation (Completed)**
  * Spatial uncertainty propagation and Bedmap3 cross-validation.
* **Phase 4: Historical Change Analysis & Chronological Machine Learning (Completed)**
  * Phase 4A/4A.1/4A.2: Methodological audits, leakage freeze, and sensor-era boundary accounting.
  * Phase 4B/4B.1/4B.2: Walk-forward expanding window cross-validation (1995–2014) and forensic spatial domain audit.
  * Phase 4C/4C.1: Held-out test evaluation (2016–2024) across 8 models and independent forensic audit.
* **Phase 5: Two-Pillar Hybrid Physical-ML 21st-Century Projections**
  * **Phase 5.0 / 5.0.1 (Completed):** Physical-model feasibility research, two-pillar architecture formulation, and mathematical audit.
  * **Phase 5.1 (Completed):** Authentic ISMIP6 21st-century projection data acquisition, provenance verification, spatial extraction, and control drift audit.
  * **Phase 5.2 (Upcoming):** Implementation of Pillar 1 parameterized physical emulator and Pillar 2 ML residual models.

---

## 7. ISMIP6 Projections Data Provenance & Spatial Extraction (Phase 5.1)

### 7.1 Authoritative Repository & Integrity
* **Zenodo Archive DOI:** [`10.5281/zenodo.3940766`](https://doi.org/10.5281/zenodo.3940766) (*Seroussi et al., 2020: ISMIP6 Antarctica 21st Century Computed Scalars*)
* **File Path:** `data/raw/ismip6/ComputedScalarsPaper.zip`
* **Size:** 32,578,545 bytes (~32.58 MB)
* **SHA256:** `f078b8546e05dc125cb15bf4c5fae87caea28f947b1d5ff59bc3c934e737cf96`
* **Purged Legacy Identifier:** `Zenodo 3897711` (erroneous T-Rex paleontology paper) has been completely removed.

### 7.2 Multi-Model Ensemble Overview
* **Model Configurations:** 16 models across 13 international institutions (AWI, DOE, ILTS_PIK, IMAU, JPL, LSCE, NCAR, PIK, UCIJPL, ULB, UTAS, VUB, VUW).
* **Ice-Flow Physics:** Encompasses SIA, SSA, hybrid SIA+SSA, first-order Blatter-Pattyn, and full Stokes approximations.
* **Temporal Coverage:** Annual projections from 2015 to 2100.
* **Scenarios Evaluated:** CMIP5 RCP8.5 (16 models) and CMIP5 RCP2.6 (13 models).
* **SSP2-4.5 Status:** Native ISMIP6 simulations do **not** exist for SSP2-4.5 / RCP4.5; intermediate pathways must be interpolated via physical scaling in Phase 5.2.

### 7.3 Spatial Basin Mapping
* **Sector 16** (Palmer Land West / Bellingshausen Sea) $\longleftrightarrow$ **`Hp-I`** ($63,153.4\text{ km}^2$)
* **Sector 17** (Graham Land West / Danco & Graham Coasts) $\longleftrightarrow$ **`I-Ipp`** ($47,716.5\text{ km}^2$)
* **Sector 18** (Graham Land East / Larsen Coast) $\longleftrightarrow$ **`Ipp-J`** ($157,311.2\text{ km}^2$)
* **Region 3** (Antarctic Peninsula Regional Aggregate) $\longleftrightarrow$ **`Domain A`** ($268,181.1\text{ km}^2$)
* *Additive Proof:* $\text{Sector 16} + \text{Sector 17} + \text{Sector 18} \equiv \text{Region 3 Area}$ ($268,181.1\text{ km}^2$).

### 7.4 Control Drift Correction
Unforced control simulations (`ctrl_proj_std`) exhibit uncalibrated initialization drift (e.g., $+9,940\text{ km}^3$ in UCIJPL ISSM; Signal-to-Drift Ratio = 0.20). Drift is subtracted synchronously at every annual timestep:
$$\Delta VAF(t) = VAF_{\text{experiment}}(t) - VAF_{\text{control}}(t)$$

### 7.5 Reproduction Instructions
To reproduce the extraction, metadata manifests, and multi-model ensemble statistics from the raw archive:
```bash
python scratch/run_phase5_1_pipeline.py
```
This produces the 8 authoritative CSV tables in `reports/tables/` and clean data in `data/processed/ismip6/`.

