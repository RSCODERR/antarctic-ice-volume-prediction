import requests
import re

url = "https://ramadda.data.bas.ac.uk/repository/entry/show?entryid=128c5e33-5224-4197-82f0-19dcc95b80a0"
r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
print(f"Status: {r.status_code}")
# Find all text and links
matches = re.findall(r'<a\s+[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', r.text, re.IGNORECASE | re.DOTALL)
print(f"Total a tags: {len(matches)}")
for href, text in matches:
    clean_text = re.sub(r'<[^>]+>', '', text).strip()
    if clean_text or any(x in href for x in ['get', 'show', 'entryid', 'download', 'file']):
        print(f"  {clean_text[:40]} -> {href}")

