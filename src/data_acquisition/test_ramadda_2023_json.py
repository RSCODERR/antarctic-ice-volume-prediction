import requests
import json

url = "https://ramadda.data.bas.ac.uk/repository/entry/show?entryid=128c5e33-5224-4197-82f0-19dcc95b80a0&output=json"
r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
print(f"Status: {r.status_code}")
try:
    data = r.json()
    for entry in data:
        print(f"  ID: {entry.get('id')} | Name: {entry.get('name')}")
except Exception as e:
    print(f"Error: {e}")

