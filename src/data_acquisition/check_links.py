import requests

def show_links(short_name):
    url = f"https://cmr.earthdata.nasa.gov/search/granules.json?short_name={short_name}"
    resp = requests.get(url, timeout=15).json()
    entries = resp.get("feed", {}).get("entry", [])
    for entry in entries:
        title = entry.get("title")
        print(f"\nGranule: {title}")
        for link in entry.get("links", []):
            print(f"  rel: {link.get('rel')} -> href: {link.get('href')}")

if __name__ == "__main__":
    show_links("NSIDC-0709")
    show_links("NSIDC-0756")

