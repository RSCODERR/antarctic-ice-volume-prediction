import os
import requests
import time

raw_dir = "antarctic-ice-volume-prediction/data/raw/bedmap3"
os.makedirs(raw_dir, exist_ok=True)
dest = os.path.join(raw_dir, "bm3_thickness.tif.part")

url = "https://ramadda.data.bas.ac.uk/repository/entry/get/bm3_thickness.tif?entryid=synth:2d0e4791-8e20-46a3-80e4-f5f6716025d2:L2JtM190aGlja25lc3MudGlm"
print("Testing download speed to disk...")
t0 = time.time()
downloaded = 0

with requests.get(url, stream=True, timeout=30) as r:
    with open(dest, "wb") as f:
        for chunk in r.iter_content(chunk_size=1024*1024):
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)
                # Test for 15 seconds
                if time.time() - t0 > 15:
                    break

dt = time.time() - t0
print(f"Downloaded {downloaded / 1e6:.2f} MB in {dt:.2f} seconds ({downloaded / 1e6 / dt:.2f} MB/s)")
if os.path.exists(dest):
    os.remove(dest)

