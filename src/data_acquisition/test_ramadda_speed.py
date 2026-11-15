import requests
import time

url = "https://ramadda.data.bas.ac.uk/repository/entry/get/bm3_thickness.tif?entryid=synth:2d0e4791-8e20-46a3-80e4-f5f6716025d2:L2JtM190aGlja25lc3MudGlm"

# Test range request
headers = {"Range": "bytes=0-1024"}
r = requests.get(url, headers=headers, timeout=10)
print("Range request status:", r.status_code)
print("Accept-Ranges:", r.headers.get("Accept-Ranges"))
print("Content-Range:", r.headers.get("Content-Range"))
print("Bytes received:", len(r.content))

# Test streaming download speed for 5 MB
t0 = time.time()
with requests.get(url, stream=True, timeout=10) as r_stream:
    downloaded = 0
    for chunk in r_stream.iter_content(chunk_size=1024*1024):
        downloaded += len(chunk)
        if downloaded >= 10 * 1024 * 1024:
            break
dt = time.time() - t0
print(f"Downloaded {downloaded / 1e6:.1f} MB in {dt:.2f} seconds ({downloaded / 1e6 / dt:.2f} MB/s)")

