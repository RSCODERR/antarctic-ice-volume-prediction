import requests
import re

def check_imbie_basins():
    url = "https://imbie.org/drainage-basins/"
    resp = requests.get(url, timeout=15)
    print("IMBIE status:", resp.status_code)
    if resp.status_code == 200:
        links = re.findall(r'href=[\'"]([^\'"]+)[\'"]', resp.text)
        for link in links:
            if any(ext in link.lower() for ext in ['.zip', '.shp', '.nc', '.tar', '.gz', 'basin']):
                print("Found basin link:", link)

if __name__ == "__main__":
    check_imbie_basins()
