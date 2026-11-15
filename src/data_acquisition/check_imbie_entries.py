"""
Check exact BAS entry IDs for IMBIE 2023 and IMBIE 1992-2020.
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

for entry_id in ["77b64c55-7166-4a06-9def-2e400398e452", "128c5e33-5224-4197-82f0-19dcc95b80a0"]:
    url = f"https://ramadda.data.bas.ac.uk/repository/entry/show?entryid={entry_id}"
    print(f"\nChecking {url}...")
    try:
        r = requests.get(url, headers=headers, timeout=10)
        p = LinkParser()
        p.feed(r.text)
        print(f"  Title / Links ({len(p.links)} found):")
        for h, t in p.links:
            if any(ext in h.lower() for ext in ['.csv', '.zip', '.nc', 'get', 'download']) or any(ext in t.lower() for ext in ['.csv', '.zip', '.nc', 'download', 'mass', 'imbie']):
                print(f"    Match: {t} -> {h}")
    except Exception as e:
        print(f"  Failed: {e}")

