import zipfile
import hashlib
import time

zip_path = 'antarctic-ice-volume-prediction/data/raw/ismip6/ComputedScalarsPaper.zip'
t0 = time.time()
count = 0
with zipfile.ZipFile(zip_path, 'r') as z:
    for info in z.infolist()[:500]:
        if info.filename.endswith('.nc'):
            data = z.read(info.filename)
            h = hashlib.sha256(data).hexdigest()
            count += 1
t1 = time.time()
print(f"Hashed {count} files in {t1-t0:.2f} seconds.")

