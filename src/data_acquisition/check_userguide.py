import requests

url = "https://nsidc.org/sites/default/files/documents/user-guide/nsidc-0756-v004-userguide.pdf"
r = requests.head(url, timeout=10)
print("PDF Status:", r.status_code, "Content-Length:", r.headers.get("Content-Length"))

