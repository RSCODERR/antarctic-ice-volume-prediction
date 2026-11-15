"""
Script to inspect earthaccess granules.
"""
import earthaccess
from dotenv import load_dotenv

load_dotenv()
auth = earthaccess.login(strategy="environment")

print("=== NSIDC-0720 Granules ===")
g_0720 = earthaccess.search_data(short_name="NSIDC-0720", temporal=("2014-07-01", "2015-06-30"))
for g in g_0720:
    print("ID:", g['meta']['native-id'])
    for u in g.data_links():
        print("  Data link:", u)

print("\n=== NSIDC-0761 Granules ===")
g_0761 = earthaccess.search_data(short_name="NSIDC-0761")
for g in g_0761:
    print("ID:", g['meta']['native-id'])
    for u in g.data_links():
        print("  Data link:", u)

print("\n=== NSIDC-0498 Granules ===")
g_0498 = earthaccess.search_data(short_name="NSIDC-0498")
for g in g_0498:
    print("ID:", g['meta']['native-id'])
    for u in g.data_links():
        print("  Data link:", u)

