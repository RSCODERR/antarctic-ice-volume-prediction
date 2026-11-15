from pypdf import PdfReader
import re

pdf_path = "antarctic-ice-volume-prediction/data/raw/nsidc-0756-v004-userguide.pdf"
reader = PdfReader(pdf_path)

print(f"Total pages: {len(reader.pages)}")
full_text = ""
for idx, page in enumerate(reader.pages):
    text = page.extract_text() or ""
    full_text += f"\n--- PAGE {idx+1} ---\n" + text

with open("antarctic-ice-volume-prediction/data/raw/userguide_text.txt", "w", encoding="utf-8") as f:
    f.write(full_text)

print("Saved extracted text to data/raw/userguide_text.txt")

# Search for variables table
lines = full_text.splitlines()
in_table = False
table_lines = []
for line in lines:
    if any(k in line.lower() for k in ["variable", "thickness", "errbed", "geoid", "source", "rgi", "firn"]):
        table_lines.append(line)

print("\nSample lines referencing variables:")
for l in table_lines[:30]:
    print(" ", l)

