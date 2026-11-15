"""
Inspection script to query official NASA CMR and BAS RAMADDA APIs
for dataset metadata, exact file names, sizes, and endpoints.
"""
import requests
import json
import sys

def inspect_nsidc_collection(short_name, version=None):
    print(f"\n=======================================================")
    print(f"Querying NASA CMR for collection: {short_name} (Version: {version})")
    print(f"=======================================================")
    url = f"https://cmr.earthdata.nasa.gov/search/granules.json?short_name={short_name}"
    if version:
        url += f"&version={version}"
    
    try:
        resp = requests.get(url, timeout=15)
        if resp.status_code != 200:
            print(f"Error {resp.status_code}: {resp.text[:200]}")
            return
        
        data = resp.json()
        entries = data.get("feed", {}).get("entry", [])
        print(f"Found {len(entries)} granules:")
        for idx, entry in enumerate(entries[:10]):
            title = entry.get("title")
            size_mb = entry.get("granule_size")
            links = entry.get("links", [])
            download_urls = [l.get("href") for l in links if l.get("rel") == "http://esipfed.org/ns/fed/user/1.0#inherited#content#"]
            opendap_urls = [l.get("href") for l in links if "opendap" in l.get("href", "").lower()]
            print(f"\n--- Granule {idx+1}: {title} ---")
            print(f"  Size: {size_mb} MB")
            print(f"  Download URLs: {download_urls[:2]}")
            if opendap_urls:
                print(f"  OPeNDAP URLs: {opendap_urls[:2]}")
    except Exception as e:
        print(f"Exception querying CMR: {e}")

def inspect_bedmap3():
    print(f"\n=======================================================")
    print(f"Querying BAS RAMADDA for Bedmap3 (2d0e4791-8e20-46a3-80e4-f5f6716025d2)")
    print(f"=======================================================")
    url = "https://ramadda.data.bas.ac.uk/repository/entry/show?entryid=2d0e4791-8e20-46a3-80e4-f5f6716025d2&output=json"
    try:
        resp = requests.get(url, timeout=15)
        if resp.status_code == 200:
            items = resp.json()
            print(f"RAMADDA returned {len(items)} items:")
            for item in items[:15]:
                name = item.get("name")
                id_ = item.get("id")
                size = item.get("size")
                print(f"  Name: {name} (ID: {id_}, Size: {size})")
        else:
            print(f"Status: {resp.status_code}, trying HTML parsing...")
    except Exception as e:
        print(f"Exception querying RAMADDA: {e}")

if __name__ == "__main__":
    inspect_nsidc_collection("NSIDC-0709")
    inspect_nsidc_collection("NSIDC-0756")
    inspect_bedmap3()

