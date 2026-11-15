import os, hashlib, csv, shutil

if not os.path.exists('reports') and os.path.exists('antarctic-ice-volume-prediction'):
    os.chdir('antarctic-ice-volume-prediction')

repo_root = os.path.abspath('.')
brain_dir = 'C:/Users/akash/.gemini/antigravity/brain/52ad6ae8-887d-48db-85e7-7d53f431979f'

def get_hash(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

# 1. First hash the 4 CSV tables
tables = {
    'per_glacier': os.path.join(repo_root, 'reports', 'tables', 'phase5_stage3C_per_glacier_comparison.csv'),
    'velocity_profiles': os.path.join(repo_root, 'reports', 'tables', 'phase5_stage3C_velocity_profiles.csv'),
    'convergence_mass': os.path.join(repo_root, 'reports', 'tables', 'phase5_stage3C_convergence_mass_audit.csv'),
    'risk_register': os.path.join(repo_root, 'reports', 'tables', 'phase5_stage3C_risk_register.csv'),
}

hashes = {k: get_hash(p) for k, p in tables.items()}

# 2. Update Section 5 of phase5_stage3C_independent_validation_report.md
rep_path = os.path.join(repo_root, 'reports', 'phase5_stage3C_independent_validation_report.md')
with open(rep_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the Section 5 table with one that includes hashes
old_table = """| Deliverable Description | Format | Workspace Path | Brain Mirror Path |
| :--- | :---: | :--- | :--- |
| **Per-Glacier Comparison Table** | CSV | [`reports/tables/...`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/phase5_stage3C_per_glacier_comparison.csv) | [`brain/tables/...`](file:///C:/Users/akash/.gemini/antigravity/brain/52ad6ae8-887d-48db-85e7-7d53f431979f/tables/phase5_stage3C_per_glacier_comparison.csv) |
| **Velocity Profiles Table** | CSV | [`reports/tables/...`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/phase5_stage3C_velocity_profiles.csv) | [`brain/tables/...`](file:///C:/Users/akash/.gemini/antigravity/brain/52ad6ae8-887d-48db-85e7-7d53f431979f/tables/phase5_stage3C_velocity_profiles.csv) |
| **Convergence & Mass Audit Table** | CSV | [`reports/tables/...`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/phase5_stage3C_convergence_mass_audit.csv) | [`brain/tables/...`](file:///C:/Users/akash/.gemini/antigravity/brain/52ad6ae8-887d-48db-85e7-7d53f431979f/tables/phase5_stage3C_convergence_mass_audit.csv) |
| **Validation Risk Register Table** | CSV | [`reports/tables/...`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/phase5_stage3C_risk_register.csv) | [`brain/tables/...`](file:///C:/Users/akash/.gemini/antigravity/brain/52ad6ae8-887d-48db-85e7-7d53f431979f/tables/phase5_stage3C_risk_register.csv) |
| **Independent Validation Report** | MD | [`reports/...`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/phase5_stage3C_independent_validation_report.md) | [`brain/...`](file:///C:/Users/akash/.gemini/antigravity/brain/52ad6ae8-887d-48db-85e7-7d53f431979f/phase5_stage3C_independent_validation_report.md) |
| **File Checksums Manifest** | CSV | [`reports/tables/...`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/phase5_stage3C_file_hashes.csv) | [`brain/tables/...`](file:///C:/Users/akash/.gemini/antigravity/brain/52ad6ae8-887d-48db-85e7-7d53f431979f/tables/phase5_stage3C_file_hashes.csv) |"""

new_table = f"""| Deliverable Description | Format | Workspace Path | Brain Mirror Path | SHA256 Checksum |
| :--- | :---: | :--- | :--- | :--- |
| **Per-Glacier Comparison Table** | CSV | [`reports/tables/...`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/phase5_stage3C_per_glacier_comparison.csv) | [`brain/tables/...`](file:///C:/Users/akash/.gemini/antigravity/brain/52ad6ae8-887d-48db-85e7-7d53f431979f/tables/phase5_stage3C_per_glacier_comparison.csv) | `{hashes['per_glacier']}` |
| **Velocity Profiles Table** | CSV | [`reports/tables/...`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/phase5_stage3C_velocity_profiles.csv) | [`brain/tables/...`](file:///C:/Users/akash/.gemini/antigravity/brain/52ad6ae8-887d-48db-85e7-7d53f431979f/tables/phase5_stage3C_velocity_profiles.csv) | `{hashes['velocity_profiles']}` |
| **Convergence & Mass Audit Table** | CSV | [`reports/tables/...`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/phase5_stage3C_convergence_mass_audit.csv) | [`brain/tables/...`](file:///C:/Users/akash/.gemini/antigravity/brain/52ad6ae8-887d-48db-85e7-7d53f431979f/tables/phase5_stage3C_convergence_mass_audit.csv) | `{hashes['convergence_mass']}` |
| **Validation Risk Register Table** | CSV | [`reports/tables/...`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/phase5_stage3C_risk_register.csv) | [`brain/tables/...`](file:///C:/Users/akash/.gemini/antigravity/brain/52ad6ae8-887d-48db-85e7-7d53f431979f/tables/phase5_stage3C_risk_register.csv) | `{hashes['risk_register']}` |
| **Independent Validation Report** | MD | [`reports/...`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/phase5_stage3C_independent_validation_report.md) | [`brain/...`](file:///C:/Users/akash/.gemini/antigravity/brain/52ad6ae8-887d-48db-85e7-7d53f431979f/phase5_stage3C_independent_validation_report.md) | *(See File Checksums Manifest)* |
| **File Checksums Manifest** | CSV | [`reports/tables/...`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/phase5_stage3C_file_hashes.csv) | [`brain/tables/...`](file:///C:/Users/akash/.gemini/antigravity/brain/52ad6ae8-887d-48db-85e7-7d53f431979f/tables/phase5_stage3C_file_hashes.csv) | *(Self-manifest verification)* |"""

assert old_table in content, "old_table string not found in report"
content = content.replace(old_table, new_table)

with open(rep_path, 'w', encoding='utf-8') as f:
    f.write(content)

# Mirror report to brain
brain_rep_path = os.path.join(brain_dir, 'phase5_stage3C_independent_validation_report.md')
shutil.copy2(rep_path, brain_rep_path)

# 3. Mirror all tables to brain
os.makedirs(os.path.join(brain_dir, 'tables'), exist_ok=True)
for k, p in tables.items():
    dst = os.path.join(brain_dir, 'tables', os.path.basename(p))
    shutil.copy2(p, dst)

# 4. Generate manifest with all 5 core files
rep_hash = get_hash(rep_path)
files_to_manifest = [
    ('phase5_stage3C_independent_validation_report.md', rep_path, brain_rep_path),
    ('phase5_stage3C_per_glacier_comparison.csv', tables['per_glacier'], os.path.join(brain_dir, 'tables', 'phase5_stage3C_per_glacier_comparison.csv')),
    ('phase5_stage3C_velocity_profiles.csv', tables['velocity_profiles'], os.path.join(brain_dir, 'tables', 'phase5_stage3C_velocity_profiles.csv')),
    ('phase5_stage3C_convergence_mass_audit.csv', tables['convergence_mass'], os.path.join(brain_dir, 'tables', 'phase5_stage3C_convergence_mass_audit.csv')),
    ('phase5_stage3C_risk_register.csv', tables['risk_register'], os.path.join(brain_dir, 'tables', 'phase5_stage3C_risk_register.csv'))
]

rows = []
for fname, p_repo, p_brain in files_to_manifest:
    h_repo = get_hash(p_repo)
    h_brain = get_hash(p_brain)
    assert h_repo == h_brain, f"Hash mismatch for {fname}"
    sz = os.path.getsize(p_repo)
    rows.append([fname, h_repo, sz, True, p_repo.replace('\\', '/'), p_brain.replace('\\', '/')])

manifest_hdr = ['File_Name', 'SHA256_Hash', 'Byte_Size', 'Brain_Mirror_Matches', 'Workspace_Path', 'Brain_Path']
manifest_repo = os.path.join(repo_root, 'reports', 'tables', 'phase5_stage3C_file_hashes.csv')
manifest_brain = os.path.join(brain_dir, 'tables', 'phase5_stage3C_file_hashes.csv')

with open(manifest_repo, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(manifest_hdr)
    for r in rows:
        w.writerow(r)

shutil.copy2(manifest_repo, manifest_brain)

# Final verification
print("Final verification of deliverables:")
for fname, p_repo, p_brain in files_to_manifest:
    h1 = get_hash(p_repo)
    h2 = get_hash(p_brain)
    print(f"  {fname:48s} | Match: {h1 == h2} | Size: {os.path.getsize(p_repo):6d} B | SHA256: {h1}")

hm1 = get_hash(manifest_repo)
hm2 = get_hash(manifest_brain)
print(f"  {'phase5_stage3C_file_hashes.csv':48s} | Match: {hm1 == hm2} | Size: {os.path.getsize(manifest_repo):6d} B | SHA256: {hm1}")
print("SUCCESS: All deliverables synchronized and verified.")

