import requests
import zipfile
import io

url = "https://imbie.org/wp-content/uploads/2026/10/IMBIE_AIS_Regional_Delineations.zip"
print("Fetching headers from:", url)
r = requests.get(url, timeout=15)
print("Status:", r.status_code, "Size:", len(r.content), "bytes")

if r.status_code == 200:
    zf = zipfile.ZipFile(io.BytesIO(r.content))
    print("Files inside zip:")
    for name in zf.namelist():
        print(" ", name)

