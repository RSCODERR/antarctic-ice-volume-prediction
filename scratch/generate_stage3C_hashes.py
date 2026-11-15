import os, hashlib, csv

if not os.path.exists('reports') and os.path.exists('antarctic-ice-volume-prediction'):
    os.chdir('antarctic-ice-volume-prediction')

repo = '.'
brain = 'C:/Users/akash/.gemini/antigravity/brain/52ad6ae8-887d-48db-85e7-7d53f431979f'

files = [
    ('phase5_stage3C_independent_validation_report.md',
     os.path.join(repo, 'reports', 'phase5_stage3C_independent_validation_report.md'),
     os.path.join(brain, 'phase5_stage3C_independent_validation_report.md')),
    ('phase5_stage3C_per_glacier_comparison.csv',
     os.path.join(repo, 'reports', 'tables', 'phase5_stage3C_per_glacier_comparison.csv'),
     os.path.join(brain, 'tables', 'phase5_stage3C_per_glacier_comparison.csv')),
    ('phase5_stage3C_velocity_profiles.csv',
     os.path.join(repo, 'reports', 'tables', 'phase5_stage3C_velocity_profiles.csv'),
     os.path.join(brain, 'tables', 'phase5_stage3C_velocity_profiles.csv')),
    ('phase5_stage3C_convergence_mass_audit.csv',
     os.path.join(repo, 'reports', 'tables', 'phase5_stage3C_convergence_mass_audit.csv'),
     os.path.join(brain, 'tables', 'phase5_stage3C_convergence_mass_audit.csv')),
    ('phase5_stage3C_risk_register.csv',
     os.path.join(repo, 'reports', 'tables', 'phase5_stage3C_risk_register.csv'),
     os.path.join(brain, 'tables', 'phase5_stage3C_risk_register.csv'))
]

def get_hash(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

rows = []
for fname, p_repo, p_brain in files:
    h_repo = get_hash(p_repo)
    h_brain = get_hash(p_brain)
    match = (h_repo == h_brain)
    sz = os.path.getsize(p_repo)
    print(f'File: {fname:50s} | Match={match} | Size={sz:6d} B | SHA256={h_repo}')
    rows.append([fname, h_repo, sz, match, p_repo.replace('\\\\', '/'), p_brain.replace('\\\\', '/')])

hash_hdr = ['File_Name', 'SHA256_Hash', 'Byte_Size', 'Brain_Mirror_Matches', 'Workspace_Path', 'Brain_Path']
hash_repo = os.path.join(repo, 'reports', 'tables', 'phase5_stage3C_file_hashes.csv')
hash_brain = os.path.join(brain, 'tables', 'phase5_stage3C_file_hashes.csv')

for p in [hash_repo, hash_brain]:
    with open(p, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(hash_hdr)
        for r in rows:
            w.writerow(r)

h_r = get_hash(hash_repo)
h_b = get_hash(hash_brain)
print(f'File: phase5_stage3C_file_hashes.csv                                 | Match={h_r == h_b} | Size={os.path.getsize(hash_repo):6d} B | SHA256={h_r}')

