import requests
import re

url = "https://data.bas.ac.uk/metadata.php?id=GB/NERC/BAS/PDC/01477"
r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
print(f"Status: {r.status_code}")
links = re.findall(r'href=[\'"]?([^\'" >]+)', r.text)
for l in links:
    if any(ext in l.lower() for ext in ['.csv', '.zip', '.nc', 'download', 'ramadda']):
        print(f"  {l}")

