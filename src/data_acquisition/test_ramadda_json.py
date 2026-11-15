import requests
import json

url = "https://ramadda.data.bas.ac.uk/repository/entry/show?entryid=77b64c55-7166-4a06-9def-2e400398e452&output=json"
r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
print(f"Status: {r.status_code}")
try:
    data = r.json()
    print("RAMADDA JSON received:")
    for entry in data:
        print(f"  ID: {entry.get('id')} | Name: {entry.get('name')} | Type: {entry.get('type')}")
        if 'filename' in entry:
            print(f"    File: {entry.get('filename')}")
except Exception as e:
    print(f"Error: {e}")
    print(r.text[:500])

