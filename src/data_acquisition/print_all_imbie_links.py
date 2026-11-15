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

url = "https://ramadda.data.bas.ac.uk/repository/a/GB-NERC-BAS-PDC-01477"
r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
p = LinkParser()
p.feed(r.text)
for h, t in p.links:
    print(f"  {t} -> {h}")

