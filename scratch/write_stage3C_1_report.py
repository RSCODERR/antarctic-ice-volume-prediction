import os, sys, hashlib, csv, shutil

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

tables = {
    'geom_obs': os.path.join(repo_root, 'reports', 'tables', 'phase5_stage3C_1_geometry_observation_audit.csv'),
    'num_conv': os.path.join(repo_root, 'reports', 'tables', 'phase5_stage3C_1_numerical_convergence_audit.csv'),
    'reg_mass': os.path.join(repo_root, 'reports', 'tables', 'phase5_stage3C_1_regional_mass_reconciliation.csv'),
    'risk_reg': os.path.join(repo_root, 'reports', 'tables', 'phase5_stage3C_1_risk_register.csv')
}

table_hashes = {k: get_hash(p) for k, p in tables.items()}

# We use standard string replacement to avoid any f-string LaTeX brace escaping pitfalls
with open('scratch/report_template.md', 'r', encoding='utf-8') as f:
    template = f.read()

for k, h in table_hashes.items():
    template = template.replace(f"{{HASH_{k.upper()}}}", h)

rep_path = os.path.join(repo_root, 'reports', 'phase5_stage3C_1_discrepancy_audit_report.md')
with open(rep_path, 'w', encoding='utf-8') as f:
    f.write(template)

brain_rep_path = os.path.join(brain_dir, 'phase5_stage3C_1_discrepancy_audit_report.md')
shutil.copy2(rep_path, brain_rep_path)

files_to_manifest = [
    ('phase5_stage3C_1_discrepancy_audit_report.md', rep_path, brain_rep_path),
    ('phase5_stage3C_1_geometry_observation_audit.csv', tables['geom_obs'], os.path.join(brain_dir, 'tables', 'phase5_stage3C_1_geometry_observation_audit.csv')),
    ('phase5_stage3C_1_numerical_convergence_audit.csv', tables['num_conv'], os.path.join(brain_dir, 'tables', 'phase5_stage3C_1_numerical_convergence_audit.csv')),
    ('phase5_stage3C_1_regional_mass_reconciliation.csv', tables['reg_mass'], os.path.join(brain_dir, 'tables', 'phase5_stage3C_1_regional_mass_reconciliation.csv')),
    ('phase5_stage3C_1_risk_register.csv', tables['risk_reg'], os.path.join(brain_dir, 'tables', 'phase5_stage3C_1_risk_register.csv'))
]

rows = []
for fname, p_repo, p_brain in files_to_manifest:
    h_repo = get_hash(p_repo)
    h_brain = get_hash(p_brain)
    assert h_repo == h_brain, f"Hash mismatch for {fname}"
    sz = os.path.getsize(p_repo)
    rows.append([fname, h_repo, sz, True, p_repo.replace('\\', '/'), p_brain.replace('\\', '/')])

manifest_hdr = ['File_Name', 'SHA256_Hash', 'Byte_Size', 'Brain_Mirror_Matches', 'Workspace_Path', 'Brain_Path']
manifest_repo = os.path.join(repo_root, 'reports', 'tables', 'phase5_stage3C_1_file_hashes.csv')
manifest_brain = os.path.join(brain_dir, 'tables', 'phase5_stage3C_1_file_hashes.csv')

with open(manifest_repo, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(manifest_hdr)
    for r in rows:
        w.writerow(r)

shutil.copy2(manifest_repo, manifest_brain)

print("Deliverables Hash Manifest:")
for fname, p_repo, p_brain in files_to_manifest:
    h1 = get_hash(p_repo)
    h2 = get_hash(p_brain)
    print(f"  {fname:50s} | Match: {h1 == h2} | Size: {os.path.getsize(p_repo):6d} B | SHA256: {h1}")

hm1 = get_hash(manifest_repo)
hm2 = get_hash(manifest_brain)
print(f"  {'phase5_stage3C_1_file_hashes.csv':50s} | Match: {hm1 == hm2} | Size: {os.path.getsize(manifest_repo):6d} B | SHA256: {hm1}")
print("SUCCESS: Stage 3C.1 report and manifest generated and synchronized.")
