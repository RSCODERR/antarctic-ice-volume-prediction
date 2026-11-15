import requests
import re

url = "https://nsidc.org/sites/default/files/documents/user-guide/nsidc-0756-v004-userguide.pdf"
save_path = "antarctic-ice-volume-prediction/data/raw/nsidc-0756-v004-userguide.pdf"

print("Downloading NSIDC-0756 V4 User Guide...")
r = requests.get(url, timeout=20)
with open(save_path, "wb") as f:
    f.write(r.content)
print(f"Saved {len(r.content)} bytes to {save_path}")

# Quick text inspection by finding text objects in PDF streams or keywords
with open(save_path, "rb") as f:
    content = f.read().decode("latin1", errors="ignore")

# Look for variable tables
keywords = ["thickness", "bed", "surface", "mask", "errbed", "source", "firn", "geoid", "rgi", "missing_value", "_FillValue"]
for kw in keywords:
    matches = [m.start() for m in re.finditer(kw, content, re.IGNORECASE)]
    print(f"Keyword '{kw}' found {len(matches)} times in user guide.")

