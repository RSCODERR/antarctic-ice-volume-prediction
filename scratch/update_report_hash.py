import os
import hashlib
import csv
import shutil

report_path = os.path.abspath("antarctic-ice-volume-prediction/reports/phase5_stage4_2_minimal_ssa_solver_report.md")
with open(report_path, "rb") as f:
    h = hashlib.sha256(f.read()).hexdigest()
size = os.path.getsize(report_path)

csv_path = os.path.abspath("antarctic-ice-volume-prediction/reports/tables/phase5_stage4_2_file_hashes.csv")
brain_csv_path = os.path.abspath("C:/Users/akash/.gemini/antigravity/brain/52ad6ae8-887d-48db-85e7-7d53f431979f/tables/phase5_stage4_2_file_hashes.csv")

row = ["reports/phase5_stage4_2_minimal_ssa_solver_report.md", size, h, "Markdown Report", "Stage 4.2 Comprehensive Synthesis Report"]

with open(csv_path, "a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(row)

shutil.copy2(csv_path, brain_csv_path)
print(f"Appended report hash {h[:12]}... to {csv_path} and mirrored to brain.")

