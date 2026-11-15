"""
Check sizes of Earthdata files using earthaccess / requests head with auth.
"""
import earthaccess
from dotenv import load_dotenv

load_dotenv()
auth = earthaccess.login(strategy="environment")

# 1. NSIDC-0720
g_0720 = earthaccess.search_data(short_name="NSIDC-0720", temporal=("2014-07-01", "2015-06-30"))
print("NSIDC-0720 granule size:", g_0720[0].size, "MB")

# 2. NSIDC-0761 (2014-2017)
g_0761 = earthaccess.search_data(short_name="NSIDC-0761", temporal=("2014-07-01", "2017-06-30"))
print(f"NSIDC-0761 matching granules: {len(g_0761)}")
for g in g_0761:
    print(" ", g['meta']['native-id'], "Size:", g.size, "MB")

# 3. NSIDC-0498
g_0498 = earthaccess.search_data(short_name="NSIDC-0498")
print(f"NSIDC-0498 matching granules: {len(g_0498)}")
for g in g_0498:
    print(" ", g['meta']['native-id'], "Size:", g.size, "MB")
