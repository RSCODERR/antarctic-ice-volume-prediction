import requests

url = "https://ramadda.data.bas.ac.uk/repository/entry/get?entryid=128c5e33-5224-4197-82f0-19dcc95b80a0"
r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
print(f"Status: {r.status_code}, Length: {len(r.content)}")
print(f"Content-Type: {r.headers.get('Content-Type')}")
print(f"Content-Disposition: {r.headers.get('Content-Disposition')}")
if 'html' not in r.headers.get('Content-Type', ''):
    with open('antarctic-ice-volume-prediction/data/raw/imbie_data.zip', 'wb') as f:
        f.write(r.content)
    print("Downloaded imbie_data.zip!")
else:
    print("Returned HTML:")
    print(r.text[:500])

