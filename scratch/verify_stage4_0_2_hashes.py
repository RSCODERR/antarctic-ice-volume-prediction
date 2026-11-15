import csv, hashlib, os

if not os.path.exists('reports') and os.path.exists('antarctic-ice-volume-prediction'):
    os.chdir('antarctic-ice-volume-prediction')

manifest = 'reports/tables/phase5_stage4_0_2_file_hashes.csv'
with open(manifest, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        w_sha = hashlib.sha256(open(row['Workspace_Path'], 'rb').read()).hexdigest()
        b_sha = hashlib.sha256(open(row['Brain_Path'], 'rb').read()).hexdigest()
        name = row['File_Name']
        assert w_sha == row['SHA256_Hash'], f"Workspace hash mismatch in {name}"
        assert b_sha == row['SHA256_Hash'], f"Brain mirror hash mismatch in {name}"
        print(f"Verified {name}: OK ({w_sha[:10]}...)")

print("\nALL 10 DELIVERABLES 100% BYTE-FOR-BYTE VERIFIED AND SYNCHRONIZED!")

