"""
Stream download NSIDC-0761 with retry and logging.
"""
import os
import sys
import earthaccess
from dotenv import load_dotenv

load_dotenv()
auth = earthaccess.login(strategy="environment")
session = earthaccess.get_requests_https_session()

url = "https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/MEASURES/NSIDC-0761/1/2014/07/01/antarctica_ice_velocity_2014-2017_450m_v01.1.nc"
dest = "data/raw/measures/antarctica_ice_velocity_2014-2017_450m_v01.1.nc"
dest_part = dest + ".part"

print(f"Connecting to {url}...")
try:
    resp = session.get(url, stream=True, timeout=30)
    print("Status:", resp.status_code, "Headers:", resp.headers.get('content-type'), "Length:", resp.headers.get('content-length'))
    resp.raise_for_status()
    total = int(resp.headers.get('content-length', 0))
    downloaded = 0
    with open(dest_part, "wb") as f:
        for chunk in resp.iter_content(chunk_size=1048576): # 1 MB chunks
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)
                if downloaded % (50 * 1048576) == 0 or downloaded == total:
                    print(f"  Downloaded {downloaded / (1024*1024):.1f} / {total / (1024*1024):.1f} MB ({(downloaded/total)*100:.1f}%)")
                    sys.stdout.flush()
    os.rename(dest_part, dest)
    print("Finished download successfully!")
except Exception as e:
    print(f"Download failed: {e}")

