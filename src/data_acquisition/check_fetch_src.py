import requests

url = "https://raw.githubusercontent.com/mdtanker/polartoolkit/main/src/polartoolkit/fetch.py"
r = requests.get(url, timeout=10)
print("Status:", r.status_code)
if r.status_code == 200:
    for line in r.text.splitlines():
        if "bedmachine" in line.lower() or "nsidc" in line.lower() or "zenodo" in line.lower() or "ftp" in line.lower() or "url" in line.lower():
            if "http" in line or "def " in line or "url" in line:
                print(line)

