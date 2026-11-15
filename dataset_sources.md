# Official Dataset Sources, Citations & Access Directory

This document provides verified scientific citations, persistent Digital Object Identifiers (DOIs), official data portal URLs, and access mechanisms for all candidate datasets evaluated for the Antarctic Peninsula Ice-Volume Prediction Project.

---

## 1. MEaSUREs BedMachine Antarctica (Version 4.1)

* **Lead Organization:** NASA / UC Irvine / Dartmouth College / NSIDC DAAC
* **Official Data Repository:** NASA National Snow and Ice Data Center Distributed Active Archive Center (NSIDC DAAC)
* **Dataset Identifier:** NSIDC-0756
* **Dataset Version:** **Version 4.1** (`V04.1`), officially released in **January 2026**
* **Dataset DOI / Landing Page:** [10.5067/POJQI54A45HX](https://doi.org/10.5067/POJQI54A45HX)
* **Official User Guide:** [https://nsidc.org/sites/default/files/documents/user-guide/nsidc-0756-v004-userguide.pdf](https://nsidc.org/sites/default/files/documents/user-guide/nsidc-0756-v004-userguide.pdf)
* **Key Scientific Publications:**
  * Morlighem, M. (2026). *MEaSUREs BedMachine Antarctica, Version 4.1*. Boulder, Colorado USA: NASA NSIDC DAAC. DOI: [10.5067/POJQI54A45HX](https://doi.org/10.5067/POJQI54A45HX)
  * Maffezzoli, N., et al. (2025). *IceBoost: Machine-learning ice thickness estimates for the Antarctic Peninsula and peripheral glaciers*. (Integrated as `source == 8` in BedMachine V4.1).
  * Morlighem, M., et al. (2020). *Deep glacial troughs and stabilizing ridges unveiled beneath the margins of the Antarctic ice sheet*. Nature Geoscience, 13, 132–137. DOI: [10.1038/s41561-019-0510-8](https://doi.org/10.1038/s41561-019-0510-8)
* **Access Protocol & Requirements:** Free NASA Earthdata Login account required. Open scientific data policy. Can be downloaded programmatically via Python `earthaccess` using browser-generated EDL tokens (`EARTHDATA_TOKEN`) or `.env` credential files. No credentials should ever be hardcoded or logged.
* **Format:** Single NetCDF-4 file (`NSIDC-0756_BedMachineAntarctica_19700101-20191001_V04.1.nc`), 1,198,815,840 bytes (~1.12 GB).
* **Thickness Convention:** **Ice-equivalent thickness** (firn air removed). To convert to true physical geometric column thickness, the accompanying `firn` variable (firn air content depth in meters) must be added: $H_{\text{geom}} = H_{\text{ice-eq}} + \text{firn}$.

---

## 2. Bedmap3 (Antarctic Ice Bed, Surface, and Thickness Grids)

* **Lead Organization:** British Antarctic Survey (BAS) / SCAR (Scientific Committee on Antarctic Research)
* **Official Data Repository:** NERC EDS UK Polar Data Centre (RAMADDA)
* **Dataset DOI / Landing Page:**
  * Gridded Products: [10.5285/2d0e4791-8e20-46a3-80e4-f5f6716025d2](https://doi.org/10.5285/2d0e4791-8e20-46a3-80e4-f5f6716025d2)
  * Standardised Point Data: [10.5285/91523ff9-d621-46b3-87f7-ffb6efcd1847](https://doi.org/10.5285/91523ff9-d621-46b3-87f7-ffb6efcd1847)
  * Shapefiles and Geopackages: [10.5285/a72a50c6-a829-4e12-9f9a-5a683a1acc4a](https://doi.org/10.5285/a72a50c6-a829-4e12-9f9a-5a683a1acc4a)
* **Key Scientific Publications:**
  * Pritchard, H. D., Fretwell, P. T., Fremand, A. C., et al. (2025). *Bedmap3 updated ice bed, surface and thickness gridded datasets for Antarctica*. Scientific Data, 12, 414. DOI: [10.1038/s41597-025-04672-y](https://doi.org/10.1038/s41597-025-04672-y)
  * Frémand, A. C., et al. (2023). *Antarctic Bedmap data: Findable, Accessible, Interoperable, and Reusable (FAIR) sharing of 60 years of ice bed, surface, and thickness data*. Earth System Science Data, 15, 2695–2710. DOI: [10.5194/essd-15-2695-2023](https://doi.org/10.5194/essd-15-2695-2023)
* **Access Protocol & Requirements:** Open access under Creative Commons Attribution 4.0 International (CC-BY 4.0). Direct HTTPS download from RAMADDA repository. No authentication required.
* **Format:** NetCDF-4, GeoTIFF, and ASCII grids.
* **Thickness Convention:** **Physical geometric column thickness** ($H = \text{surface} - \text{bed}$), incorporating both ice and the overlying compacted firn air column. Verified with 100.0000% exact numerical agreement across all 1,650,227 grounded cells in the Antarctic Peninsula domain. To convert to ice-equivalent thickness, firn air content must be subtracted: $H_{\text{ice-eq}} = \max(H_{\text{geom}} - \text{FAC}, 0.0)$.
* **Mask Classification Scheme:** Class 1 = Permanently Grounded Ice Sheet; Class 2 = Transiently Grounded Ice Shelf (pinning points, offset: +2.0 m); Class 3 = Floating Ice Shelf (mean sub-ice ocean cavity depth: 202.86 m); Class 4 = Ice-free Rock Outcrops; -9999 / 0 = Ocean.

---

## 3. RACMO (Regional Atmospheric Climate Model — Surface Mass Balance)

* **Lead Organization:** Utrecht University (Institute for Marine and Atmospheric research Utrecht - IMAU) / KNMI
* **Official Data Repository:** Utrecht University Ice and Climate Portal & Zenodo / PANGAEA
* **Project Portal:** [https://www.projects.science.uu.nl/iceclimate/models/racmo.html](https://www.projects.science.uu.nl/iceclimate/models/racmo.html)
* **Repository DOIs:**
  * **RACMO2.4p1 Historical ERA5-Forced Data (11 km, 1979–2023/2025):** Zenodo IMAU Community ([10.5281/zenodo.10519398](https://doi.org/10.5281/zenodo.10519398))
  * **RACMO2.3p2 Statistically Downscaled SMB (2 km / 1 km, 1979–2021):** [10.5281/zenodo.5807954](https://doi.org/10.5281/zenodo.5807954)
* **Key Scientific Publications:**
  * van Wessem, J. M., et al. (2018). *Modelling the climate and surface mass balance of polar ice sheets using RACMO2: EVALUATION OF RACMO2.3p2*. The Cryosphere, 12, 1479–1498. DOI: [10.5194/tc-12-1479-2018](https://doi.org/10.5194/tc-12-1479-2018)
  * van Wessem, J. M., et al. (2016). *The modelled surface mass balance of the Antarctic Peninsula at 5.5 km resolution*. The Cryosphere, 10, 271–285. DOI: [10.5194/tc-10-271-2016](https://doi.org/10.5194/tc-10-271-2016)
* **Access Protocol & Requirements:** Open access under CC-BY. Direct download via Zenodo REST API and HTTPS.
* **Format:** NetCDF-4 (`.nc`), native rotated pole coordinates requiring reprojection to `EPSG:3031`.

---

## 4. Continental Ice-Sheet Drainage Basins: MEaSUREs & IMBIE

* **Lead Organization:** NASA JPL / UC Irvine / NSIDC DAAC
* **Official Data Repository:** NSIDC DAAC
* **Dataset Identifier:** NSIDC-0709 (*MEaSUREs Antarctic Boundaries for IPY 2007-2009 from Satellite Radar*)
* **Dataset DOI / Landing Page:** [10.5067/AXE412173225](https://doi.org/10.5067/AXE412173225)
* **Key Scientific Publications:**
  * Mouginot, J., Scheuchl, B., & Rignot, E. (2017). *Comprehensive Annual Ice Sheet Velocity Mapping of Antarctica from 1996 to 2017*. Geophysical Research Letters, 44(2), 911–918. DOI: [10.1002/2017GL072937](https://doi.org/10.1002/2017GL072937)
  * Zwally, H. J., et al. (2012). *Antarctic ice sheet mass balance: 2003 to 2008 from ICESat*. Journal of Glaciology, 58(210), 656–664.
* **Role in Project:** **Primary spatial boundary definition for the Antarctic Peninsula Ice Sheet (Basins 24, 25, 26, and 27)**.
* **Access Protocol & Requirements:** Free NASA Earthdata Login account required. Open access.
* **Format:** ESRI Shapefiles (`.shp`) and GeoPackage (`.gpkg`) in `EPSG:3031`.

---

## 5. GLIMS & Randolph Glacier Inventory (Supplementary Peripheral Glaciers)

* **Lead Organization:** Global Land Ice Measurements from Space (GLIMS) / NSIDC DAAC
* **Dataset Identifiers:**
  * Randolph Glacier Inventory (RGI 7.0, Region 19 Antarctic and Subantarctic): DOI: [10.5281/zenodo.10667086](https://doi.org/10.5281/zenodo.10667086) / NSIDC-0770
  * GLIMS Glacier Database: NSIDC-0272 (DOI: [10.7265/N5V98602](https://doi.org/10.7265/N5V98602))
* **Key Scientific Publications:**
  * Maussion, F., et al. (2023). *The Randolph Glacier Inventory version 7.0*. Zenodo. DOI: [10.5281/zenodo.10667086](https://doi.org/10.5281/zenodo.10667086)
  * Raup, B., et al. (2007). *The GLIMS Geospatial Glacier Database*. Global and Planetary Change, 56, 101–110.
* **Crucial Scope Note:** RGI 7.0 explicitly excludes the contiguous Antarctic Ice Sheet. It is retained strictly as a **supplementary source** for peripheral ice masses and subantarctic islands.
* **Format:** Shapefiles, GeoPackage, and GeoJSON.

---

## 6. ITS_LIVE (Inter-mission Time Series of Land Ice Velocity and Elevation)

* **Lead Organization:** NASA Jet Propulsion Laboratory (JPL) / MEaSUREs Program
* **Official Data Repository:** AWS Open Data Registry & NSIDC DAAC
* **Project Portal:** [https://its-live.jpl.nasa.gov](https://its-live.jpl.nasa.gov)
* **AWS S3 Open Data Bucket:** `s3://its-live-data/` (Public, unauthenticated access)
* **Key Scientific Publication:**
  * Gardner, A. S., et al. (2018). *Increased West Antarctic and Wilkes Land ice discharge balanced by short-term snow accumulation and East Antarctic thickening*. The Cryosphere, 12(2), 521–547. DOI: [10.5194/tc-12-521-2018](https://doi.org/10.5194/tc-12-521-2018)
* **Format:** NetCDF-4, Cloud-Optimized GeoTIFF (COG), Zarr data cubes.

---

## 7. NASA ICESat-2 ATL15 (Gridded Land Ice Height Change)

* **Lead Organization:** NASA Goddard Space Flight Center / NSIDC DAAC
* **Dataset Identifier:** NSIDC-0758 (ATL15, Version 3)
* **Dataset DOI / Landing Page:** [10.5067/O5TW6L64DF6C](https://doi.org/10.5067/O5TW6L64DF6C)
* **Key Scientific Publication:**
  * Smith, B., et al. (2023). *ATLAS/ICESat-2 L3B Annual and Quarterly Gridded Land Ice Height, Version 3*. Boulder, Colorado USA: NASA NSIDC DAAC.
* **Access Protocol & Requirements:** Free NASA Earthdata Login required.
* **Format:** NetCDF-4 files (`ATL15_AA_0314_01km_003_01.nc` etc.).

---

## 8. IMBIE (Ice Sheet Mass Balance Inter-comparison Exercise)

* **Lead Organization:** Centre for Polar Observation and Modelling (CPOM) / ESA / NASA
* **Official Project Portal:** [http://imbie.org](http://imbie.org)
* **Dataset DOIs:**
  * IMBIE 2023 Update (1972–2023): [10.5285/128c5e33-5224-4197-82f0-19dcc95b80a0](https://doi.org/10.5285/128c5e33-5224-4197-82f0-19dcc95b80a0)
  * IMBIE 1992–2020 Assessment: [10.5285/77b64c55-7166-4a06-9def-2e400398e452](https://doi.org/10.5285/77b64c55-7166-4a06-9def-2e400398e452)
* **Key Scientific Publication:**
  * Otosaka, I. N., et al. (2023). *Mass balance of the Greenland and Antarctic ice sheets from 1992 to 2020*. Earth System Science Data, 15, 1597–1616. DOI: [10.5194/essd-15-1597-2023](https://doi.org/10.5194/essd-15-1597-2023)
* **Format:** CSV tables and NetCDF timeseries, pre-partitioned into the Antarctic Peninsula (APIS) sector.

---

## 9. ISMIP6 (Ice Sheet Model Intercomparison Project for CMIP6)

* **Lead Organization:** NASA Goddard Space Flight Center / GHub / CMIP6
* **Official Data Repository:** Zenodo & The GHub (University at Buffalo)
* **Repository DOIs:**
  * ISMIP6 Antarctic Projections Archive: [10.5281/zenodo.3940766](https://doi.org/10.5281/zenodo.3940766)
  * ISMIP6 CMIP6 Climate Forcing Datasets (SSP1-2.6, SSP2-4.5, SSP5-8.5): [10.5281/zenodo.3897711](https://doi.org/10.5281/zenodo.3897711)
* **Key Scientific Publication:**
  * Seroussi, H., et al. (2020). *ISMIP6 Antarctica: a multi-model ensemble of the Antarctic ice sheet evolution over the 21st century*. The Cryosphere, 14, 3033–3070. DOI: [10.5194/tc-14-3033-2020](https://doi.org/10.5194/tc-14-3033-2020)
* **Format:** NetCDF-4 (`.nc`) on regular polar stereographic grids (4–32 km) and regional scalar tables.
