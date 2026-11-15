import os, hashlib, shutil, csv

if not os.path.exists('reports') and os.path.exists('antarctic-ice-volume-prediction'):
    os.chdir('antarctic-ice-volume-prediction')

brain_dir = 'C:/Users/akash/.gemini/antigravity/brain/52ad6ae8-887d-48db-85e7-7d53f431979f'
repo_report = os.path.join('reports', 'phase5_stage4_0_2_mathematical_closure_report.md')
brain_report = os.path.join(brain_dir, 'phase5_stage4_0_2_mathematical_closure_report.md')

template_path = os.path.join('scratch', 'stage4_0_2_report_template.md')
with open(template_path, 'r', encoding='utf-8') as f:
    content = f.read()

with open(repo_report, 'w', encoding='utf-8') as f:
    f.write(content)

shutil.copyfile(repo_report, brain_report)
print("Copied report to workspace and brain mirror.")

# List of all files to hash
table_files = [
    'phase5_stage4_0_2_calving_and_grounding_equations.csv',
    'phase5_stage4_0_2_hybrid_flux_evaluation.csv',
    'phase5_stage4_0_2_domain_decomposition_spec.csv',
    'phase5_stage4_0_2_computational_domain_definition.csv',
    'phase5_stage4_0_2_conservation_tolerances.csv',
    'phase5_stage4_0_2_convergence_criteria.csv',
    'phase5_stage4_0_2_computational_feasibility.csv',
    'phase5_stage4_0_2_risk_register.csv',
    'phase5_stage4_0_2_implementation_prerequisites.csv'
]

def get_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

manifest_rows = []

# First hash the report
rep_sha = get_sha256(repo_report)
brain_rep_sha = get_sha256(brain_report)
rep_size = os.path.getsize(repo_report)
manifest_rows.append([
    'phase5_stage4_0_2_mathematical_closure_report.md',
    rep_sha,
    rep_size,
    rep_sha == brain_rep_sha,
    os.path.abspath(repo_report).replace('\\', '/'),
    brain_report.replace('\\', '/')
])

for tf in table_files:
    repo_tf = os.path.join('reports', 'tables', tf)
    brain_tf = os.path.join(brain_dir, 'tables', tf)
    sha = get_sha256(repo_tf)
    b_sha = get_sha256(brain_tf)
    sz = os.path.getsize(repo_tf)
    manifest_rows.append([
        tf,
        sha,
        sz,
        sha == b_sha,
        os.path.abspath(repo_tf).replace('\\', '/'),
        brain_tf.replace('\\', '/')
    ])

manifest_repo = os.path.join('reports', 'tables', 'phase5_stage4_0_2_file_hashes.csv')
manifest_brain = os.path.join(brain_dir, 'tables', 'phase5_stage4_0_2_file_hashes.csv')

with open(manifest_repo, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['File_Name', 'SHA256_Hash', 'Byte_Size', 'Brain_Mirror_Matches', 'Workspace_Path', 'Brain_Path'])
    writer.writerows(manifest_rows)

shutil.copyfile(manifest_repo, manifest_brain)
print("File hashes manifest written and mirrored.")

for row in manifest_rows:
    print(f"{row[0]}: {row[1]} (Size: {row[2]} bytes, Match: {row[3]})")

