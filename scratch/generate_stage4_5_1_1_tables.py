"""
Script: generate_stage4_5_1_1_tables.py
Purpose: Generate Stage 4.5.1.1 Corrected Product Registry and Download Protocol Audit CSV tables.
"""

import os
import csv
import shutil

PROJECT_TABLES_DIR = os.path.join("reports", "tables")
BRAIN_TABLES_DIR = r"C:\Users\akash\.gemini\antigravity\brain\52ad6ae8-887d-48db-85e7-7d53f431979f\tables"

os.makedirs(PROJECT_TABLES_DIR, exist_ok=True)
os.makedirs(BRAIN_TABLES_DIR, exist_ok=True)

# 1. stage4_5_1_1_corrected_product_registry.csv
registry_headers = [
    "Product_ID",
    "Product_Name",
    "Provider_Organization",
    "Version",
    "Native_Resolution",
    "Grid_CRS",
    "Temporal_Window",
    "Primary_Variables",
    "Official_DOI",
    "Repository_Landing_URL",
    "Verified_Provider_Facts",
    "Unresolved_Download_Assumptions_or_Risks"
]

registry_rows = [
    [
        "DATA-01-BM4",
        "MEaSUREs BedMachine Antarctica",
        "NASA NSIDC DAAC / UC Irvine",
        "v4.1",
        "500 m",
        "EPSG:3031",
        "1970-01-01 to 2019-10-01",
        "thickness (ice-equivalent [m]), bed, surface, mask, firn (FAC [m])",
        "10.5067/POJQI54A45HX",
        "https://nsidc.org/data/nsidc-0756/versions/4",
        "Verified file on local disk (1.20 GB, SHA-256: 6bd08dbbe1...). Authoritative Domain A baseline: 866,358 cells, 216,062.17 km2, 140,702.51 km3 solid ice equivalent.",
        "None (Existing & Verified). Firn air content must NEVER be subtracted from BedMachine solid ice thickness."
    ],
    [
        "DATA-02-BM3",
        "Bedmap3 Antarctic Topography",
        "BAS / SCAR",
        "v1.0 (2023/2025)",
        "500 m",
        "EPSG:3031",
        "1958 to 2022 multi-decadal radar",
        "bm3_thickness (geometric [m]), bm3_bed, bm3_surface, bm3_masks, bm3_thickness_uncertainty",
        "10.5285/2d0e4791-8e20-46a3-80e4-f5f6716025d2",
        "https://data.bas.ac.uk/items/2d0e4791-8e20-46a3-80e4-f5f6716025d2/",
        "Verified 5 GeoTIFF rasters on local disk (1.81 GB total). Represents physical geometric column thickness (ice + aerated firn column).",
        "None (Existing & Verified). Must NEVER be mixed with BedMachine solid ice volume integration."
    ],
    [
        "DATA-03-IMBIE-BOUNDS",
        "IMBIE AIS Regional Delineations",
        "IMBIE Consortium / CPOM / NASA",
        "Rignot 2011 / RGI 7.0 update",
        "Vector shapefile + 1km/5km/10km rasters",
        "EPSG:3031",
        "2011 (Rignot) / 2023 update",
        "Basin polygons: Basin 24 (Palmer Land W / Hp-I), Basin 25 (Graham Land W / I-Ipp), Basin 26 (Graham Land E / Ipp-J)",
        "10.5285/128c5e33-5224-4197-82f0-19dcc95b80a0",
        "http://imbie.org/",
        "Verified vector shapefile and gridded NetCDF files on local disk (168.8 MB). Authoritative boundary definition for Domain A.",
        "None (Existing & Verified). Peripheral islands (Alexander, Adelaide, etc.) must remain masked out from Domain A."
    ],
    [
        "DATA-04-IMBIE-TS",
        "IMBIE3 Historical Mass Balance Timeseries",
        "IMBIE Consortium / Otosaka et al. (2023)",
        "IMBIE 2023 Release",
        "Sector-integrated monthly scalar",
        "Antarctic Peninsula sector",
        "1979-01-01 to 2023-12-01",
        "mass_change (Gt), dM_dt (Gt/yr), partitioned altimetry, gravimetry, input-output method",
        "10.5285/128c5e33-5224-4197-82f0-19dcc95b80a0",
        "http://imbie.org/data-downloads/",
        "Verified monthly and annual CSV tables on local disk (97.2 KB). Benchmark for regional dynamic mass loss trajectories.",
        "None (Existing & Verified)."
    ],
    [
        "DATA-05A-RACMO-ANT055",
        "RACMO2.3p2 Native Regional AP SMB",
        "IMAU (Utrecht University) / KNMI",
        "RACMO2.3p2 (XPEN055 domain)",
        "5.5 km (40 vertical levels)",
        "Rotated Polar Coordinate Grid",
        "1979-01 to 2019-08 (ERA-Int), 2019-08 to 2022-12 (ERA5)",
        "smb (Surface Mass Balance [mm w.e./month]), precip, snowmelt, sublim, runoff",
        "10.5281/zenodo.7961733",
        "https://zenodo.org/records/7961733",
        "Verified authoritative regional model output for Antarctic Peninsula (van Wessem et al.). Captures extreme orographic precipitation gradient.",
        "Native resolution is 5.5 km on rotated polar grid. Requires rotation to EPSG:3031 and elevation-dependent downscaling to 1 km in Stage 4.5.2."
    ],
    [
        "DATA-05B-RACMO-DOWNSCALED",
        "RACMO2.3p2 Statistically Downscaled Antarctic SMB",
        "IMAU (Utrecht University) / Univ Liege",
        "Downscaled 2 km ERA5 (Noël et al., 2023)",
        "2 km (2000 m)",
        "EPSG:3031",
        "1979-01 to 2021-12",
        "smb_yearly (Annual SMB [mm w.e./yr]), sector annual totals (Gt/yr)",
        "10.5281/zenodo.10007855",
        "https://zenodo.org/records/10007855",
        "Published in Nature Communications (Noël et al., 2023). Highest resolution open-access Antarctic RACMO product archived on Zenodo.",
        "Spatial resolution is 2 km, NOT 1 km. 1 km downscaling was developed for Greenland. Substituting 27 km ANT27 is strictly prohibited."
    ],
    [
        "DATA-06-ITSLIVE-2015",
        "ITS_LIVE Annual Surface Ice Velocity Mosaic 2015",
        "NASA JPL / MEaSUREs",
        "v02 (Gardner et al., 2018/2021)",
        "120 m (ANT_G0120) and 240 m (ANT_G0240)",
        "EPSG:3031",
        "2015-01-01 to 2015-12-31",
        "v (speed magnitude [m/yr]), vx, vy (Cartesian components [m/yr]), v_error (uncertainty [m/yr])",
        "10.5067/URXET9MR7NNK",
        "https://registry.opendata.aws/its-live/",
        "Publicly hosted on AWS S3 bucket s3://its-live-data/ in us-west-2. Anonymous public read access enabled.",
        "Unauthenticated HTTP requests can return XML error pages (<Error><Code>AccessDenied</Code>) or HTML 404 pages. Download pipeline must verify NetCDF magic header."
    ],
    [
        "DATA-07A-MEASURES-ANNUAL-1KM",
        "MEaSUREs Annual Antarctic Ice Velocity Maps",
        "NASA NSIDC DAAC / UC Irvine",
        "v01 / v02 (NSIDC-0720)",
        "1 km (1000 m)",
        "EPSG:3031",
        "Annual July 1 to June 30 epochs (2000-2001, 2005-2025; target: 2014-2015)",
        "VX, VY (Cartesian velocity [m/yr]), ERRX, ERRY (uncertainty [m/yr])",
        "10.5067/MEASURES/CRYOSPHERE/nsidc-0720.001",
        "https://nsidc.org/data/nsidc-0720/versions/1",
        "True native resolution is 1 km (1000 m), perfectly matching the macro-mesh scale. Cadence is annual July-June. NOT a 450 m product.",
        "Requires NASA Earthdata URS authentication. Granule name: antarctica_ice_velocity_2014_2015_1km_v01.nc."
    ],
    [
        "DATA-07B-MEASURES-REF-450M",
        "MEaSUREs Multi-year Reference Velocity Maps of AIS",
        "NASA NSIDC DAAC / UC Irvine",
        "v01 (NSIDC-0761)",
        "450 m",
        "EPSG:3031",
        "Multi-year epochs: 1995-2001, 2007-2009, 2014-2017, 2020-2022",
        "VX, VY (Cartesian velocity [m/yr]), STDX, STDY, observation counts, date stamps",
        "10.5067/MEASURES/CRYOSPHERE/nsidc-0761.001",
        "https://nsidc.org/data/nsidc-0761/versions/1",
        "High-resolution 450 m grid matching BedMachine 500 m bedrock geometry. Optimal for spatial basal friction inversion (C_bed).",
        "Multi-year epoch (2014-2017) composite; does not isolate single-year transient spikes. Requires NASA Earthdata URS authentication."
    ],
    [
        "DATA-08-MEASURES-GL-V21",
        "MEaSUREs Antarctic Grounding Line from DInSAR",
        "NASA NSIDC DAAC / UC Irvine",
        "v2.1 (NSIDC-0498, active release)",
        "DInSAR vector line features",
        "EPSG:3031",
        "1992-02-07 to 2025-11-26 (multi-epoch: 1996, 2000, 2008, 2015, 2020-2025)",
        "Grounding line polylines with attributes: Year, Satellite, Sensor, Source",
        "10.5067/MEASURES/CRYOSPHERE/nsidc-0498.002",
        "https://nsidc.org/data/nsidc-0498/versions/2.1",
        "Active release is Version 2.1 (minor update expanding coverage to late 2025, adding PAZ/ICEYE, and GeoPackage format). Historical lines identical to v2.0 in Domain A.",
        "Requires NASA Earthdata URS authentication. Distributed as zip archive containing Shapefile and GeoPackage formats."
    ]
]

# Write registry CSV
reg_project_path = os.path.join(PROJECT_TABLES_DIR, "stage4_5_1_1_corrected_product_registry.csv")
reg_brain_path = os.path.join(BRAIN_TABLES_DIR, "stage4_5_1_1_corrected_product_registry.csv")

with open(reg_project_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(registry_headers)
    writer.writerows(registry_rows)

shutil.copy2(reg_project_path, reg_brain_path)
print(f"Successfully generated {reg_project_path} and mirrored to {reg_brain_path}")


# 2. stage4_5_1_1_download_protocol_audit.csv
protocol_headers = [
    "Product_ID",
    "Product_Name",
    "Target_Local_Path",
    "Download_Protocol",
    "Endpoint_URL_or_S3_Key",
    "Auth_Mechanism",
    "File_Verification_Method",
    "Error_Response_Detection_Rule",
    "Actionable_Acquisition_Command"
]

protocol_rows = [
    [
        "DATA-01-BM4",
        "MEaSUREs BedMachine Antarctica v4.1",
        "data/raw/bedmachine/NSIDC-0756_BedMachineAntarctica_19700101-20191001_V04.1.nc",
        "Local Disk (Already Present)",
        "N/A (Local File)",
        "None (Local)",
        "SHA-256: 6bd08dbbe1a781834450cd25f7b5f438463a540a873d819bb781912e7ecb1538; Size: 1,198,815,840 bytes",
        "N/A (Local file verified)",
        "# File already present and verified. No acquisition command required."
    ],
    [
        "DATA-02-BM3",
        "Bedmap3 Antarctic Topography (5 GeoTIFFs)",
        "data/raw/bedmap3/bm3_*.tif",
        "Local Disk (Already Present)",
        "N/A (Local File)",
        "None (Local)",
        "SHA-256 verified for all 5 rasters (thickness, bed, surface, masks, thickness_uncertainty); Total: 1.81 GB",
        "N/A (Local files verified)",
        "# Files already present and verified. No acquisition command required."
    ],
    [
        "DATA-03-IMBIE-BOUNDS",
        "IMBIE AIS Regional Delineations",
        "data/raw/imbie_basins/IMBIE_AIS_Regional_Delineations/*",
        "Local Disk (Already Present)",
        "N/A (Local File)",
        "None (Local)",
        "SHA-256 verified for Shapefile package and NetCDF rasters (1km, 5km, 10km); Total: 168.8 MB",
        "N/A (Local files verified)",
        "# Files already present and verified. No acquisition command required."
    ],
    [
        "DATA-04-IMBIE-TS",
        "IMBIE3 Historical Mass Balance Timeseries",
        "data/raw/imbie/imbie3_antarctic_peninsula_Gt_partitioned.csv",
        "Local Disk (Already Present)",
        "N/A (Local File)",
        "None (Local)",
        "SHA-256 verified: ff144cc08fb3f78e8f511743294c17f8ab178a021ee4068ad7356fb46c0122eb; Size: 82,196 bytes",
        "N/A (Local file verified)",
        "# File already present and verified. No acquisition command required."
    ],
    [
        "DATA-05A-RACMO-ANT055",
        "RACMO2.3p2 Native Regional AP SMB (5.5 km)",
        "data/raw/racmo/RACMO2.3p2_XPEN055_monthly_smb.nc",
        "HTTPS REST API (Zenodo)",
        "https://zenodo.org/records/7961733/files/RACMO2.3p2_XPEN055_monthly_smb.nc",
        "Open Access (No credentials required)",
        "Zenodo MD5 checksum verification; NetCDF magic header \\x89HDF or CDF\\x01",
        "Reject if response code != 200 or payload begins with '<!DOCTYPE html' (Zenodo error landing page)",
        "curl -L -f -o data/raw/racmo/RACMO2.3p2_XPEN055_monthly_smb.nc \"https://zenodo.org/records/7961733/files/RACMO2.3p2_XPEN055_monthly_smb.nc?download=1\""
    ],
    [
        "DATA-05B-RACMO-DOWNSCALED",
        "RACMO2.3p2 Statistically Downscaled Antarctic SMB (2 km)",
        "data/raw/racmo/RACMO2.3p2_ANT_2km_yearly_smb_1979_2021.nc",
        "HTTPS REST API (Zenodo)",
        "https://zenodo.org/records/10007855/files/RACMO2.3p2_ANT_2km_yearly_smb_1979_2021.nc",
        "Open Access (No credentials required)",
        "Zenodo MD5 checksum verification; NetCDF magic header \\x89HDF or CDF\\x01",
        "Reject if response code != 200 or payload begins with '<!DOCTYPE html' (Zenodo error landing page)",
        "curl -L -f -o data/raw/racmo/RACMO2.3p2_ANT_2km_yearly_smb_1979_2021.nc \"https://zenodo.org/records/10007855/files/RACMO2.3p2_ANT_2km_yearly_smb_1979_2021.nc?download=1\""
    ],
    [
        "DATA-06-ITSLIVE-2015",
        "ITS_LIVE Annual Surface Ice Velocity Mosaic 2015 (120 m / 240 m)",
        "data/raw/its_live/ANT_G0120_2015.nc",
        "HTTPS Direct / AWS CLI (S3)",
        "https://its-live-data.s3.amazonaws.com/velocity_mosaic/v2/annual/ANT_G0120_2015.nc (s3://its-live-data/velocity_mosaic/v2/annual/ANT_G0120_2015.nc)",
        "Open Access (AWS Open Data, anonymous read enabled)",
        "HTTP Content-Type: application/x-netcdf; NetCDF magic header \\x89HDF (HDF5/NetCDF-4); Non-zero payload (>500 MB)",
        "Reject if payload begins with '<?xml' (<Error><Code>AccessDenied</Code>) or '<!DOCTYPE html' (403/404 HTML)",
        "curl -L -f -o data/raw/its_live/ANT_G0120_2015.nc \"https://its-live-data.s3.amazonaws.com/velocity_mosaic/v2/annual/ANT_G0120_2015.nc\" || aws s3 cp s3://its-live-data/velocity_mosaic/v2/annual/ANT_G0120_2015.nc data/raw/its_live/ --no-sign-request"
    ],
    [
        "DATA-07A-MEASURES-ANNUAL-1KM",
        "MEaSUREs Annual Antarctic Ice Velocity Maps (1 km)",
        "data/raw/measures/antarctica_ice_velocity_2014_2015_1km_v01.nc",
        "HTTPS Authenticated (NASA Earthdata Cloud)",
        "https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/MEASURES/NSIDC-0720/1/antarctica_ice_velocity_2014_2015_1km_v01.nc",
        "NASA Earthdata Login (URS) ~/.netrc credential auth with cookie jar (~/.urs_cookies)",
        "HTTP Content-Type: application/x-netcdf; NetCDF magic header \\x89HDF; Expected size ~420 MB",
        "Reject if payload begins with '<!DOCTYPE html' (URS login redirect / 401 unauthorized HTML)",
        "curl -b ~/.urs_cookies -c ~/.urs_cookies -L -n -f -o data/raw/measures/antarctica_ice_velocity_2014_2015_1km_v01.nc \"https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/MEASURES/NSIDC-0720/1/antarctica_ice_velocity_2014_2015_1km_v01.nc\""
    ],
    [
        "DATA-07B-MEASURES-REF-450M",
        "MEaSUREs Multi-year Reference Velocity Maps of AIS (450 m)",
        "data/raw/measures/antarctica_ice_velocity_450m_v02.nc",
        "HTTPS Authenticated (NASA Earthdata Cloud)",
        "https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/MEASURES/NSIDC-0761/1/antarctica_ice_velocity_450m_v02.nc",
        "NASA Earthdata Login (URS) ~/.netrc credential auth with cookie jar (~/.urs_cookies)",
        "HTTP Content-Type: application/x-netcdf; NetCDF magic header \\x89HDF; Expected size ~850 MB",
        "Reject if payload begins with '<!DOCTYPE html' (URS login redirect / 401 unauthorized HTML)",
        "curl -b ~/.urs_cookies -c ~/.urs_cookies -L -n -f -o data/raw/measures/antarctica_ice_velocity_450m_v02.nc \"https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/MEASURES/NSIDC-0761/1/antarctica_ice_velocity_450m_v02.nc\""
    ],
    [
        "DATA-08-MEASURES-GL-V21",
        "MEaSUREs Antarctic Grounding Line from DInSAR (v2.1)",
        "data/raw/measures_gl/MEaSUREs_Antarctic_Grounding_Line_v02.1.zip",
        "HTTPS Authenticated (NASA Earthdata Cloud)",
        "https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/MEASURES/NSIDC-0498/2.1/MEaSUREs_Antarctic_Grounding_Line_v02.1.zip",
        "NASA Earthdata Login (URS) ~/.netrc credential auth with cookie jar (~/.urs_cookies)",
        "ZIP archive magic header PK\\x03\\x04; Unzips cleanly to Shapefile (.shp, .shx, .dbf, .prj) and GeoPackage (.gpkg)",
        "Reject if payload begins with '<!DOCTYPE html' (URS login redirect / 401 unauthorized HTML)",
        "curl -b ~/.urs_cookies -c ~/.urs_cookies -L -n -f -o data/raw/measures_gl/MEaSUREs_Antarctic_Grounding_Line_v02.1.zip \"https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/MEASURES/NSIDC-0498/2.1/MEaSUREs_Antarctic_Grounding_Line_v02.1.zip\" && unzip -q data/raw/measures_gl/MEaSUREs_Antarctic_Grounding_Line_v02.1.zip -d data/raw/measures_gl/"
    ]
]

# Write protocol CSV
prot_project_path = os.path.join(PROJECT_TABLES_DIR, "stage4_5_1_1_download_protocol_audit.csv")
prot_brain_path = os.path.join(BRAIN_TABLES_DIR, "stage4_5_1_1_download_protocol_audit.csv")

with open(prot_project_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(protocol_headers)
    writer.writerows(protocol_rows)

shutil.copy2(prot_project_path, prot_brain_path)
print(f"Successfully generated {prot_project_path} and mirrored to {prot_brain_path}")

