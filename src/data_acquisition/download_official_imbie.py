"""
Download official IMBIE Antarctic Peninsula time series from BAS RAMADDA.
"""
import requests
import os
import hashlib
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
IMBIE_DIR = os.path.join(BASE_DIR, "data", "raw", "imbie")
os.makedirs(IMBIE_DIR, exist_ok=True)

headers = {'User-Agent': 'Mozilla/5.0'}

files_to_download = [
    {
        "name": "imbie3_antarctic_peninsula_Gt_partitioned.csv",
        "entryid": "synth:128c5e33-5224-4197-82f0-19dcc95b80a0:L2ltYmllM19hbnRhcmN0aWNfcGVuaW5zdWxhX0d0X3BhcnRpdGlvbmVkLmNzdg==",
        "doi": "10.5285/128c5e33-5224-4197-82f0-19dcc95b80a0",
        "description": "IMBIE 2023 Update (Otosaka et al., 2023, ESSD) - Antarctic Peninsula Mass Balance in Gt"
    },
    {
        "name": "imbie_antarctic_peninsula_2021_Gt.csv",
        "entryid": "synth:77b64c55-7166-4a06-9def-2e400398e452:L2ltYmllX2FudGFyY3RpY19wZW5pbnN1bGFfMjAyMV9HdC5jc3Y=",
        "doi": "10.5285/77b64c55-7166-4a06-9def-2e400398e452",
        "description": "IMBIE 2021 Assessment for IPCC AR6 - Antarctic Peninsula Mass Balance in Gt"
    }
]

provenance = {}

for item in files_to_download:
    fname = item["name"]
    fpath = os.path.join(IMBIE_DIR, fname)
    url = f"https://ramadda.data.bas.ac.uk/repository/entry/get?entryid={item['entryid']}"
    print(f"Downloading {fname} from {url}...")
    r = requests.get(url, headers=headers, timeout=20)
    if r.status_code == 200:
        with open(fpath, "wb") as f:
            f.write(r.content)
        size = len(r.content)
        sha256 = hashlib.sha256(r.content).hexdigest()
        md5 = hashlib.md5(r.content).hexdigest()
        print(f"  -> SUCCESS: {size} bytes")
        print(f"  SHA-256: {sha256}")
        print(f"  MD5:     {md5}")
        provenance[fname] = {
            "size_bytes": size,
            "sha256": sha256,
            "md5": md5,
            "doi": item["doi"],
            "url": url,
            "description": item["description"]
        }
    else:
        print(f"  -> FAILED: HTTP {r.status_code}")

prov_path = os.path.join(IMBIE_DIR, "acquisition_provenance.json")
with open(prov_path, "w") as f:
    json.dump(provenance, f, indent=2)
print(f"Provenance saved to {prov_path}")

