import requests
import re

url = "https://ramadda.data.bas.ac.uk/repository/entry/show?entryid=2d0e4791-8e20-46a3-80e4-f5f6716025d2"
r = requests.get(url, timeout=10)
print("Status:", r.status_code)
links = re.findall(r'href=[\'"]([^\'"]+bm3[^\'"]*)[\'"]', r.text)
print("Found bm3 links:")
for l in links[:10]:
    print(" ", l)

# Look for 'entry/get' links
get_links = re.findall(r'href=[\'"]([^\'"]*entry/get[^\'"]*)[\'"]', r.text)
print("Found get links:")
for l in get_links[:10]:
    print(" ", l)

