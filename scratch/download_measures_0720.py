"""
Download NSIDC-0720 2014-2015 1 km annual velocity map.
"""
import os
import hashlib
import earthaccess
from dotenv import load_dotenv

load_dotenv()
os.makedirs("data/raw/measures", exist_ok=True)

auth = earthaccess.login(strategy="environment")
print(f"earthaccess authenticated: {auth.authenticated}")

g_0720 = earthaccess.search_data(
    short_name="NSIDC-0720",
    temporal=("2014-07-01", "2015-06-30")
)
print(f"Found {len(g_0720)} granules for NSIDC-0720. Downloading...")
files = earthaccess.download(g_0720, "data/raw/measures")
print(f"Downloaded files: {files}")

# Validate
for f in os.listdir("data/raw/measures"):
    fp = os.path.join("data/raw/measures", f)
    if os.path.isfile(fp):
        sz = os.path.getsize(fp)
        with open(fp, "rb") as fl:
            hdr = fl.read(16)
        print(f"Validated NSIDC-0720: {f} | Size: {sz} bytes ({sz/(1024*1024):.2f} MB) | Header: {hdr[:4]}")

