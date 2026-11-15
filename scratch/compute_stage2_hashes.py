import hashlib
import glob
import os
import pandas as pd

files = sorted(glob.glob('reports/tables/phase5_stage2_*.csv'))
report_file = 'reports/phase5_stage2_observational_integration_report.md'
if os.path.exists(report_file):
    files.append(report_file)

hash_records = []
for f in files:
    with open(f, 'rb') as fp:
        data = fp.read()
        sha256 = hashlib.sha256(data).hexdigest()
        size_bytes = len(data)
    hash_records.append({
        "File_Path": f.replace('\\', '/'),
        "File_Name": os.path.basename(f),
        "File_Size_Bytes": size_bytes,
        "SHA256_Hash": sha256
    })

df = pd.DataFrame(hash_records)
out_csv = 'reports/tables/phase5_stage2_file_hashes.csv'
df.to_csv(out_csv, index=False)
print(f"Generated hash manifest: {out_csv}")
for r in hash_records:
    print(f"  {r['File_Name']:55s} | {r['File_Size_Bytes']:6d} B | {r['SHA256_Hash']}")

