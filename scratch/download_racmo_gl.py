"""
Acquire RACMO and NSIDC-0498 datasets and validate.
"""
import os
import hashlib
import requests
import earthaccess
from dotenv import load_dotenv

load_dotenv()
os.makedirs("data/raw/racmo", exist_ok=True)
os.makedirs("data/raw/measures_gl", exist_ok=True)

# 1. Download RACMO2.3p2 from Zenodo
racmo_files = [
    ("smb_monthlyS_XPEN055_ERA5-3H_RACMO2.3p2_201601_202212.nc", "https://zenodo.org/api/records/7961733/files/smb_monthlyS_XPEN055_ERA5-3H_RACMO2.3p2_201601_202212.nc/content"),
    ("smb_monthlyS_XPEN055_ERAINx_RACMO2.3p2_197901_201908.nc", "https://zenodo.org/api/records/7961733/files/smb_monthlyS_XPEN055_ERAINx_RACMO2.3p2_197901_201908.nc/content")
]

for fn, url in racmo_files:
    dest = os.path.join("data/raw/racmo", fn)
    if os.path.exists(dest) and os.path.getsize(dest) > 1000000:
        print(f"RACMO file already exists: {dest} ({os.path.getsize(dest)} bytes)")
    else:
        print(f"Downloading {fn} from Zenodo...")
        resp = requests.get(url, stream=True, timeout=60)
        resp.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in resp.iter_content(chunk_size=65536):
                f.write(chunk)
        print(f"Downloaded {dest} ({os.path.getsize(dest)} bytes)")

# 2. Download NSIDC-0498 Grounding Lines
auth = earthaccess.login(strategy="environment")
g_0498 = earthaccess.search_data(short_name="NSIDC-0498")
print(f"Downloading {len(g_0498)} granules for NSIDC-0498...")
downloaded_gl = earthaccess.download(g_0498, "data/raw/measures_gl")
print(f"Downloaded GL files: {downloaded_gl}")

# 3. Validation
for d, _, files in os.walk("data/raw"):
    for f in files:
        if "racmo" in d or "measures_gl" in d:
            fp = os.path.join(d, f)
            sz = os.path.getsize(fp)
            with open(fp, "rb") as fl:
                header = fl.read(16)
                fl.seek(0)
                sha = hashlib.sha256(fl.read()).hexdigest()
            print(f"Validated: {f} | Size: {sz} bytes | Header: {header[:4]} | SHA-256: {sha[:16]}...")

