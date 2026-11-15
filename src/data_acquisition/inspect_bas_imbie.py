"""
Inspect BAS RAMADDA entry for IMBIE and download the IMBIE Antarctic Peninsula time series.
"""
import requests
import json
import os
import re
from html.parser import HTMLParser

class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.current_href = None
        self.current_text = ""

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for k, v in attrs:
                if k.lower() == 'href':
                    self.current_href = v
                    self.current_text = ""

    def handle_data(self, data):
        if self.current_href:
            self.current_text += data

    def handle_endtag(self, tag):
        if tag == 'a' and self.current_href:
            self.links.append((self.current_href, self.current_text.strip()))
            self.current_href = None
            self.current_text = ""

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW_IMBIE_DIR = os.path.join(BASE_DIR, "data", "raw", "imbie")
os.makedirs(RAW_IMBIE_DIR, exist_ok=True)

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

url = "https://ramadda.data.bas.ac.uk/repository/entry/show?entryid=cb159b6c-a4b3-4245-80fd-4b4e8122a858"
print(f"Fetching BAS RAMADDA IMBIE entry: {url}...")
r = requests.get(url, headers=headers, timeout=15)
parser = LinkParser()
parser.feed(r.text)

print(f"Total links found: {len(parser.links)}")
data_links = []
for href, text in parser.links:
    if any(ext in href.lower() for ext in ['.csv', '.zip', '.nc', 'get', 'download']) or any(ext in text.lower() for ext in ['.csv', '.zip', '.nc', 'download', 'peninsula', 'apis']):
        print(f"  Candidate: {text} -> {href}")
        data_links.append((href, text))

# If there's an entryid or child entry, let's explore children
for h, t in parser.links:
    if 'entryid=' in h and h != url:
        print(f"  Child entry: {t} -> {h}")

