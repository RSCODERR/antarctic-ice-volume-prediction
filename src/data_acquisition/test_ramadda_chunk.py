import requests
import time

url = "https://ramadda.data.bas.ac.uk/repository/entry/get/bm3_thickness.tif?entryid=synth:2d0e4791-8e20-46a3-80e4-f5f6716025d2:L2JtM190aGlja25lc3MudGlm"
print("Connecting to RAMADDA stream...")
t0 = time.time()
try:
    with requests.get(url, stream=True, timeout=30) as r:
        print("Connected! Status code:", r.status_code)
        chunk = r.raw.read(1024 * 1024)
        print(f"Read {len(chunk)} bytes in {time.time() - t0:.2f} seconds!")
except Exception as e:
    print("Error:", e)

