"""
Inspect exact endpoints for IMBIE, Zenodo, ITS_LIVE, and NASA CMR.
"""
import requests
import json

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'}

# 1. Test IMBIE
for url in ["http://imbie.org", "http://imbie.org/data/", "https://data.bas.ac.uk/metadata.php?id=GB/NERC/BAS/PDC/01646"]:
    try:
        r = requests.get(url, headers=headers, timeout=10)
        print(f"IMBIE ({url}): HTTP {r.status_code}")
    except Exception as e:
        print(f"IMBIE ({url}) failed: {e}")

# 2. Test Zenodo RACMO record
try:
    r = requests.get("https://zenodo.org/api/records/5807954", headers=headers, timeout=10)
    print(f"Zenodo 5807954: HTTP {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"Title: {data['metadata']['title']}")
        for f in data.get('files', []):
            print(f"  File: {f['key']} ({f['size']} bytes)")
except Exception as e:
    print(f"Zenodo failed: {e}")

# 3. Test NASA CMR query for ATL15
try:
    r = requests.get("https://cmr.earthdata.nasa.gov/search/granules.json?short_name=ATL15&version=003&page_size=3", headers=headers, timeout=10)
    print(f"NASA CMR ATL15: HTTP {r.status_code}")
    if r.status_code == 200:
        entries = r.json()['feed']['entry']
        print(f"  Total ATL15 granules found: {r.json()['feed']['hits']}")
        for entry in entries:
            print(f"  Granule: {entry['title']} ({entry.get('granule_size', 'N/A')} MB)")
except Exception as e:
    print(f"CMR failed: {e}")

# 4. Test ITS_LIVE S3
try:
    r = requests.get("https://its-live-data.s3.amazonaws.com/velocity_mosaic/landsat/v02/annual/index.html", headers=headers, timeout=10)
    print(f"ITS_LIVE Annual Index: HTTP {r.status_code}")
except Exception as e:
    print(f"ITS_LIVE failed: {e}")

