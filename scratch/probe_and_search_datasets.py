"""
Script: probe_and_search_datasets.py
Purpose: Search and inspect external datasets using earthaccess, requests, and urllib.
"""

import os
import json
import requests
import earthaccess
from dotenv import load_dotenv

load_dotenv()
auth = earthaccess.login(strategy="environment")
print(f"earthaccess authenticated: {auth.authenticated}")

results = {}

# 1. Search NSIDC-0720 (Annual 1 km Velocity)
print("\n--- Searching NSIDC-0720 ---")
try:
    granules_0720 = earthaccess.search_data(
        short_name="NSIDC-0720",
        temporal=("2014-07-01", "2015-06-30")
    )
    print(f"Found {len(granules_0720)} granules for NSIDC-0720")
    results['NSIDC-0720'] = []
    for g in granules_0720[:5]:
        meta = {
            'title': g['meta'].get('native-id'),
            'size_MB': g['data_granule'].get('archive_files', [{}])[0].get('size_in_bytes', 0) / (1024*1024) if 'data_granule' in g else 0,
            'urls': [link['href'] for link in g['umm']['related_urls'] if link.get('type') == 'GET DATA'][:2]
        }
        print(f"Granule: {meta['title']}, Size: {meta['size_MB']:.2f} MB, URLs: {meta['urls']}")
        results['NSIDC-0720'].append(meta)
except Exception as e:
    print(f"Error searching NSIDC-0720: {e}")
    results['NSIDC-0720_error'] = str(e)

# 2. Search NSIDC-0761 (450 m Reference Velocity)
print("\n--- Searching NSIDC-0761 ---")
try:
    granules_0761 = earthaccess.search_data(
        short_name="NSIDC-0761"
    )
    print(f"Found {len(granules_0761)} granules for NSIDC-0761")
    results['NSIDC-0761'] = []
    for g in granules_0761[:5]:
        meta = {
            'title': g['meta'].get('native-id'),
            'urls': [link['href'] for link in g['umm']['related_urls'] if link.get('type') == 'GET DATA'][:2]
        }
        print(f"Granule: {meta['title']}, URLs: {meta['urls']}")
        results['NSIDC-0761'].append(meta)
except Exception as e:
    print(f"Error searching NSIDC-0761: {e}")
    results['NSIDC-0761_error'] = str(e)

# 3. Search NSIDC-0498 (Grounding lines)
print("\n--- Searching NSIDC-0498 ---")
try:
    granules_0498 = earthaccess.search_data(
        short_name="NSIDC-0498"
    )
    print(f"Found {len(granules_0498)} granules for NSIDC-0498")
    results['NSIDC-0498'] = []
    for g in granules_0498[:5]:
        meta = {
            'title': g['meta'].get('native-id'),
            'urls': [link['href'] for link in g['umm']['related_urls'] if link.get('type') == 'GET DATA'][:2]
        }
        print(f"Granule: {meta['title']}, URLs: {meta['urls']}")
        results['NSIDC-0498'].append(meta)
except Exception as e:
    print(f"Error searching NSIDC-0498: {e}")
    results['NSIDC-0498_error'] = str(e)

# 4. Probe Zenodo RACMO records
print("\n--- Probing Zenodo RACMO Records ---")
for record_id in ["7961733", "10007855"]:
    url = f"https://zenodo.org/api/records/{record_id}"
    try:
        resp = requests.get(url, timeout=15)
        print(f"Zenodo {record_id} status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            title = data.get('metadata', {}).get('title')
            files = [{'key': f.get('key'), 'size_MB': f.get('size', 0)/(1024*1024), 'link': f.get('links', {}).get('self')} for f in data.get('files', [])[:5]]
            print(f"Title: {title}")
            for f in files:
                print(f"  File: {f['key']}, Size: {f['size_MB']:.2f} MB")
            results[f'zenodo_{record_id}'] = {'title': title, 'files': files}
    except Exception as e:
        print(f"Error querying Zenodo {record_id}: {e}")

# 5. Probe ITS_LIVE on AWS S3
print("\n--- Probing ITS_LIVE on AWS S3 ---")
for fn in ["ANT_G0240_2015.nc", "ANT_G0120_2015.nc"]:
    url = f"https://its-live-data.s3.amazonaws.com/velocity_mosaic/v2/annual/{fn}"
    try:
        resp = requests.head(url, timeout=15)
        print(f"ITS_LIVE {fn} status: {resp.status_code}, headers: content-type={resp.headers.get('Content-Type')}, content-length={int(resp.headers.get('Content-Length', 0))/(1024*1024):.2f} MB")
        results[f'its_live_{fn}'] = {'status': resp.status_code, 'size_MB': int(resp.headers.get('Content-Length', 0))/(1024*1024)}
    except Exception as e:
        print(f"Error querying ITS_LIVE {fn}: {e}")

with open("scratch/probe_results.json", "w") as f:
    json.dump(results, f, indent=2)
print("\nWrote probe results to scratch/probe_results.json")

