import requests
import re

url = "https://ramadda.data.bas.ac.uk/repository/entry/show?entryid=2d0e4791-8e20-46a3-80e4-f5f6716025d2"
r = requests.get(url, timeout=10)
print("Title:", re.findall(r'<title>(.*?)</title>', r.text, re.IGNORECASE))
all_hrefs = re.findall(r'href=[\'"]([^\'"]+)[\'"]', r.text)
print(f"Total hrefs: {len(all_hrefs)}")
for h in all_hrefs:
    if "entry" in h or "download" in h or "get" in h or "repository" in h:
        print(" ", h)

