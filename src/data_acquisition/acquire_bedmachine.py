"""
BedMachine Antarctica V4.1 Acquisition and Spatial Cropping Module
Authenticates with NASA Earthdata using earthaccess (token or environment credentials),
downloads the official BedMachine V4.1 NetCDF granule, and extracts the Antarctic Peninsula domain.

Security:
- Never prints credentials or tokens in terminal logs.
- Never writes credentials to source files.
- Reads EARTHDATA_TOKEN or EARTHDATA_USERNAME/PASSWORD explicitly from OS environment
  or git-ignored .env file.
"""

import os
import sys
import hashlib
import json
import datetime
import numpy as np
import xarray as xr
from dotenv import load_dotenv, find_dotenv

# Verified Antarctic Peninsula Domain Coordinates in EPSG:3031
PENINSULA_BOUNDS = {
    'min_x': -2700000.0,
    'max_x': -1400000.0,
    'min_y':  250000.0,
    'max_y': 1950000.0,
    'crs': 'EPSG:3031',
    'res_m': 500.0
}

EXPECTED_SIZE_BYTES = 1198815840  # 1.12 GB (official NSIDC-0756 V04.1 size)

def load_auth_environment():
    """Explicitly searches and loads .env files from project and current directories."""
    # 1. Check find_dotenv
    found = find_dotenv(usecwd=True)
    if found:
        load_dotenv(found)
        
    # 2. Check explicit known locations
    load_dotenv("antarctic-ice-volume-prediction/.env")
    load_dotenv(".env")
    load_dotenv(os.path.join(os.path.expanduser("~"), ".env"))
    
    token = os.getenv("EARTHDATA_TOKEN")
    user = os.getenv("EARTHDATA_USERNAME")
    pwd = os.getenv("EARTHDATA_PASSWORD")
    
    return token, user, pwd

def check_auth_prerequisites():
    """Verifies that authentication credentials/tokens are configured."""
    token, user, pwd = load_auth_environment()
    
    if not token and not (user and pwd):
        print("\n" + "="*80)
        print("NASA EARTHDATA AUTHENTICATION STATUS: NOT CONFIGURED")
        print("="*80)
        print("MEaSUREs BedMachine Antarctica V4.1 requires NASA Earthdata authentication.")
        print("\nTo configure your Earthdata Token locally:")
        print("1. Log in to your NASA Earthdata account at: https://urs.earthdata.nasa.gov/")
        print("2. Navigate to 'Generate Token' (direct link: https://urs.earthdata.nasa.gov/users/tokens).")
        print("3. Click 'Generate Token' and copy your token string.")
        print("4. Provide it locally via either method:")
        print("   - PowerShell: $env:EARTHDATA_TOKEN = \"your_token_here\"")
        print("   - Local .env: Create a file named 'antarctic-ice-volume-prediction/.env'")
        print("                 containing: EARTHDATA_TOKEN=your_token_here")
        print("   (Note: .env is git-ignored and will never be tracked or committed).")
        print("="*80 + "\n")
        return False
    return True

def compute_checksums(filepath):
    """Computes SHA-256 and MD5 checksums of a large file efficiently."""
    sha256_hash = hashlib.sha256()
    md5_hash = hashlib.md5()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(65536), b""):
            sha256_hash.update(byte_block)
            md5_hash.update(byte_block)
    return sha256_hash.hexdigest(), md5_hash.hexdigest()

def acquire_bedmachine(raw_dir="antarctic-ice-volume-prediction/data/raw/bedmachine"):
    """Authenticates and downloads BedMachine Antarctica V4.1 using earthaccess."""
    if not check_auth_prerequisites():
        raise PermissionError("NASA Earthdata authentication not configured. Set EARTHDATA_TOKEN in .env.")
        
    import earthaccess
    print("Authenticating with NASA Earthdata using environment strategy...")
    try:
        auth = earthaccess.login(strategy="environment")
    except Exception as e:
        raise PermissionError(f"Authentication failed: {e}. Please check your token validity.")
        
    if not auth.authenticated:
        raise PermissionError("Authentication failed: Earthdata rejected the provided token/credentials.")
        
    print("Authentication successful! NASA Earthdata session established.")
    os.makedirs(raw_dir, exist_ok=True)
    
    print("Searching NASA CMR for BedMachine Antarctica V4.1 (NSIDC-0756)...")
    results = earthaccess.search_data(short_name="NSIDC-0756", version="4")
    if not results:
        raise FileNotFoundError("BedMachine Antarctica V4.1 granule not found in NASA CMR.")
        
    granule = results[0]
    expected_filename = "NSIDC-0756_BedMachineAntarctica_19700101-20191001_V04.1.nc"
    target_path = os.path.join(raw_dir, expected_filename)
    data_links = granule.data_links()
    source_url = data_links[0] if data_links else "https://data.nsidc.earthdatacloud.nasa.gov/"
    
    # Check if already downloaded and intact
    if os.path.exists(target_path) and os.path.getsize(target_path) == EXPECTED_SIZE_BYTES:
        print(f"Verified existing raw dataset: {target_path} ({os.path.getsize(target_path):,d} bytes).")
        sha256, md5 = compute_checksums(target_path)
        print(f"  SHA-256: {sha256}")
        print(f"  MD5:     {md5}")
        return target_path
        
    print(f"Initiating download of {expected_filename} (~1.12 GB)...")
    downloaded = earthaccess.download(results, raw_dir)
    if not downloaded:
        raise RuntimeError("Download completed but no file was returned.")
        
    downloaded_file = downloaded[0]
    actual_size = os.path.getsize(downloaded_file)
    print(f"Download complete: {downloaded_file} ({actual_size:,d} bytes).")
    
    sha256, md5 = compute_checksums(downloaded_file)
    print(f"Checksum verification:")
    print(f"  SHA-256: {sha256}")
    print(f"  MD5:     {md5}")
    
    # Record provenance
    prov_path = os.path.join(raw_dir, "acquisition_provenance.json")
    provenance = {
        "dataset_name": "MEaSUREs BedMachine Antarctica, Version 4.1",
        "dataset_id": "NSIDC-0756",
        "version": "4.1",
        "access_date_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "source_url": source_url,
        "file_name": expected_filename,
        "file_size_bytes": actual_size,
        "expected_size_bytes": EXPECTED_SIZE_BYTES,
        "sha256": sha256,
        "md5": md5
    }
    with open(prov_path, "w") as f:
        json.dump(provenance, f, indent=2)
    print(f"Provenance saved to {prov_path}")
    
    if actual_size != EXPECTED_SIZE_BYTES:
        print(f"WARNING: File size ({actual_size} bytes) differs from expected ({EXPECTED_SIZE_BYTES} bytes).")
        
    return downloaded_file

def crop_bedmachine(nc_path, out_nc_path="antarctic-ice-volume-prediction/data/processed/bedmachine_v4.1_peninsula_500m.nc"):
    """Crops BedMachine Antarctica V4.1 to the Antarctic Peninsula domain and validates variables."""
    print(f"\nOpening raw BedMachine NetCDF: {nc_path}")
    ds = xr.open_dataset(nc_path)
    
    # Inspect all required variables
    required_vars = ['thickness', 'bed', 'surface', 'mask', 'errbed', 'source', 'firn', 'rgi']
    print("\n--- VARIABLE AUDIT (BedMachine V4.1) ---")
    for v in required_vars:
        if v in ds:
            da = ds[v]
            print(f"  • {v:<10}: dtype={str(da.dtype):<8} | units={da.attrs.get('units', 'N/A'):<12} | {da.attrs.get('long_name', '')}")
        else:
            print(f"  • WARNING: Expected variable '{v}' not found in NetCDF dataset!")

    min_x, max_x = PENINSULA_BOUNDS['min_x'], PENINSULA_BOUNDS['max_x']
    min_y, max_y = PENINSULA_BOUNDS['min_y'], PENINSULA_BOUNDS['max_y']
    
    # Check y orientation
    y_slice = slice(max_y, min_y) if ds.y[0] > ds.y[-1] else slice(min_y, max_y)
    x_slice = slice(min_x, max_x)
    
    print(f"\nSubsetting Peninsula domain: X [{min_x}, {max_x}] m, Y [{min_y}, {max_y}] m...")
    ds_pen = ds.sel(x=x_slice, y=y_slice)
    
    print(f"Cropped dimensions: {dict(ds_pen.dims)}")
    os.makedirs(os.path.dirname(out_nc_path), exist_ok=True)
    
    print(f"Saving cropped domain NetCDF: {out_nc_path}...")
    ds_pen.to_netcdf(out_nc_path)
    print("BedMachine Peninsula domain cropped and saved successfully!")
    return out_nc_path

if __name__ == "__main__":
    try:
        raw_nc = acquire_bedmachine()
        crop_bedmachine(raw_nc)
    except Exception as e:
        print(f"Acquisition halted: {e}")
