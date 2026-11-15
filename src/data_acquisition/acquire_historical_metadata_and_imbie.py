"""
Acquire official IMBIE Antarctic Peninsula time series and query NASA CMR for historical datasets.
"""
import requests
import json
import os
import re
from html.parser import HTMLParser
import hashlib

class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.current_tag = None
        self.current_text = ""
        self.current_href = None

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for k, v in attrs:
                if k.lower() == 'href':
                    self.current_href = v
                    self.current_text = ""

    def handle_data(self, data):
        if self.current_href:
            self.current_text += data

    def handle_endtag(self, tag):
        if tag == 'a' and self.current_href:
            self.links.append((self.current_href, self.current_text.strip()))
            self.current_href = None
            self.current_text = ""

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
IMBIE_DIR = os.path.join(RAW_DIR, "imbie")
os.makedirs(IMBIE_DIR, exist_ok=True)

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'}

print("=" * 80)
print("1. Scraping IMBIE Data Download Links...")
print("=" * 80)
try:
    r = requests.get("http://imbie.org", headers=headers, timeout=15)
    parser = LinkParser()
    parser.feed(r.text)
    for href, text in parser.links:
        if any(ext in href.lower() for ext in ['.csv', '.zip', '.txt', 'data', 'download']):
            print(f"  Found link: {text} -> {href}")
            
    # Also check imbie.org/imbie-3 or imbie-2
    for slug in ["/imbie-3/", "/data-downloads/", "/imbie-2021/", "/imbie-2/", "/data/"]:
        r_slug = requests.get(f"http://imbie.org{slug}", headers=headers, timeout=10)
        if r_slug.status_code == 200:
            print(f"  Valid slug found: http://imbie.org{slug}")
            p_s = LinkParser()
            p_s.feed(r_slug.text)
            for h, t in p_s.links:
                if any(x in h.lower() for x in ['.csv', '.zip', '.txt', 'antarctica']):
                    print(f"    Data Link in {slug}: {t} -> {h}")
except Exception as e:
    print(f"IMBIE scraping error: {e}")

print("\n" + "=" * 80)
print("2. Checking BAS / NERC IMBIE Record...")
print("=" * 80)
try:
    bas_url = "https://data.bas.ac.uk/metadata.php?id=GB/NERC/BAS/PDC/01646"
    r = requests.get(bas_url, headers=headers, timeout=15)
    p_b = LinkParser()
    p_b.feed(r.text)
    for h, t in p_b.links:
        if any(ext in h.lower() for ext in ['.csv', '.zip', '.nc', 'download', 'ramadda']):
            print(f"  BAS data link: {t} -> {h}")
except Exception as e:
    print(f"BAS PDC error: {e}")

print("\n" + "=" * 80)
print("3. Querying NASA CMR for ICESat-2 ATL15 Granules...")
print("=" * 80)
try:
    cmr_atl15 = "https://cmr.earthdata.nasa.gov/search/granules.json?short_name=ATL15&version=003&page_size=5"
    r = requests.get(cmr_atl15, headers=headers, timeout=15)
    if r.status_code == 200:
        data = r.json()
        entries = data['feed']['entry']
        print(f"  ATL15 Total Granules Found: {len(entries)}")
        for e in entries:
            title = e['title']
            size = e.get('granule_size', 'N/A')
            links = [l['href'] for l in e.get('links', []) if 'data#' in l.get('rel', '') or l.get('href', '').endswith('.nc')]
            print(f"    Granule: {title} ({size} MB) | URL: {links[0] if links else 'N/A'}")
except Exception as e:
    print(f"CMR ATL15 query error: {e}")

print("\n" + "=" * 80)
print("4. Querying NASA CMR for MEaSUREs Annual Velocity (NSIDC-0754)...")
print("=" * 80)
try:
    cmr_vel = "https://cmr.earthdata.nasa.gov/search/granules.json?short_name=NSIDC-0754&version=1&page_size=3"
    r = requests.get(cmr_vel, headers=headers, timeout=15)
    if r.status_code == 200:
        data = r.json()
        entries = data['feed']['entry']
        print(f"  MEaSUREs Annual Velocity Granules Found: {len(entries)}")
        for e in entries:
            print(f"    Granule: {e['title']} ({e.get('granule_size', 'N/A')} MB)")
except Exception as e:
    print(f"CMR Velocity query error: {e}")

print("\n" + "=" * 80)
print("5. Querying NASA CMR for ICESat GLA12...")
print("=" * 80)
try:
    cmr_glas = "https://cmr.earthdata.nasa.gov/search/granules.json?short_name=GLA12&version=034&page_size=3"
    r = requests.get(cmr_glas, headers=headers, timeout=15)
    if r.status_code == 200:
        data = r.json()
        entries = data['feed']['entry']
        print(f"  ICESat GLA12 Granules Found: {len(entries)}")
        for e in entries:
            print(f"    Granule: {e['title']} ({e.get('granule_size', 'N/A')} MB)")
except Exception as e:
    print(f"CMR GLA12 query error: {e}")
