"""
Inspect files inside GB-NERC-BAS-PDC-01477 and GB-NERC-BAS-PDC-02074.
"""
import requests
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

headers = {'User-Agent': 'Mozilla/5.0'}

for slug in ["/repository/a/GB-NERC-BAS-PDC-01477", "/repository/a/GB-NERC-BAS-PDC-02074"]:
    url = f"https://ramadda.data.bas.ac.uk{slug}"
    print(f"\nChecking {url}...")
    try:
        r = requests.get(url, headers=headers, timeout=15)
        p = LinkParser()
        p.feed(r.text)
        print(f"  Total links: {len(p.links)}")
        for h, t in p.links:
            if any(ext in h.lower() for ext in ['.csv', '.zip', '.nc', 'get', 'download']) or any(ext in t.lower() for ext in ['.csv', '.zip', '.nc', 'download', 'antarctica', 'apis']):
                print(f"    File: {t} -> {h}")
    except Exception as e:
        print(f"  Failed: {e}")

