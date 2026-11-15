"""
List all files in Zenodo record 7961733.
"""
import requests

resp = requests.get("https://zenodo.org/api/records/7961733", timeout=15)
if resp.status_code == 200:
    data = resp.json()
    files = data.get('files', [])
    print(f"Total files in Zenodo 7961733: {len(files)}")
    for f in files:
        fn = f.get('key')
        sz = f.get('size', 0) / (1024*1024)
        if 'smb' in fn.lower() or 'precip' in fn.lower() or 'snow' in fn.lower() or 'runoff' in fn.lower():
            print(f"  SMB/Melt file: {fn} ({sz:.2f} MB)")

