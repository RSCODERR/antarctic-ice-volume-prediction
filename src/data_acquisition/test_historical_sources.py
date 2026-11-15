"""
Test connectivity to historical data sources (IMBIE, Zenodo RACMO, AWS ITS_LIVE, Earthdata CMR).
"""
import urllib.request
import json
import os

def test_url(name, url):
    print(f"Testing {name}: {url}...")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            code = response.getcode()
            print(f"  -> SUCCESS: HTTP {code}")
            return True
    except Exception as e:
        print(f"  -> FAILED: {e}")
        return False

print("Probing public endpoints:")
test_url("IMBIE Website", "http://imbie.org/data-downloads/")
test_url("Zenodo RACMO2.3p2 Record", "https://zenodo.org/api/records/5807954")
test_url("NASA CMR API", "https://cmr.earthdata.nasa.gov/search/granules.json?short_name=ATL15&version=003&page_size=1")
test_url("AWS ITS_LIVE Catalog", "https://its-live-data.s3.amazonaws.com/index.html")

