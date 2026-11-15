import requests
import json

url = "https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-public/MEASURES/NSIDC-0756/4/1970/01/01/NSIDC-0756_BedMachineAntarctica_19700101-20191001_V04.1.nc.json"
print("Fetching public metadata JSON for BedMachine V4.1...")
r = requests.get(url, timeout=10)
print("Status:", r.status_code)
if r.status_code == 200:
    data = r.json()
    print("Top-level keys:", list(data.keys()))
    # Pretty-print first 1000 chars
    print(json.dumps(data, indent=2)[:2000])

