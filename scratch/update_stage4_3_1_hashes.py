import hashlib
import os
import pandas as pd

rpt = "reports/phase5_stage4_3_1_spatial_accounting_correction_report.md"
h = hashlib.sha256(open(rpt, "rb").read()).hexdigest()
sz = os.path.getsize(rpt)

df = pd.read_csv("reports/tables/phase5_stage4_3_1_file_hashes.csv")
if rpt not in df["File_Path"].values:
    df = pd.concat([df, pd.DataFrame([{"File_Path": rpt, "Size_Bytes": sz, "SHA256_Checksum": h}])], ignore_index=True)
    df.to_csv("reports/tables/phase5_stage4_3_1_file_hashes.csv", index=False)
    df.to_csv("C:/Users/akash/.gemini/antigravity/brain/52ad6ae8-887d-48db-85e7-7d53f431979f/tables/phase5_stage4_3_1_file_hashes.csv", index=False)
print("Updated file hashes successfully.")

