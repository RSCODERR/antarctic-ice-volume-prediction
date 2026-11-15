import zlib
import re

pdf_path = "antarctic-ice-volume-prediction/data/raw/nsidc-0756-v004-userguide.pdf"
with open(pdf_path, "rb") as f:
    pdf_bytes = f.read()

# Find stream objects
streams = re.findall(b'stream[\r\n]+(.*?)[\r\n]+endstream', pdf_bytes, re.DOTALL)
print(f"Found {len(streams)} streams in PDF.")

extracted_text = []
for s in streams:
    try:
        decompressed = zlib.decompress(s)
        # Find text inside BT ... ET or parenthesized strings
        text_matches = re.findall(rb'\((.*?)\)', decompressed)
        for tm in text_matches:
            extracted_text.append(tm.decode('latin1', errors='ignore'))
    except Exception:
        pass

full_text = " ".join(extracted_text)
print(f"Extracted {len(full_text)} characters of text.")

# Search for variables
for kw in ["thickness", "bed", "surface", "mask", "errbed", "source", "firn", "geoid", "rgi", "FillValue", "EPSG"]:
    found = [m.start() for m in re.finditer(kw, full_text, re.IGNORECASE)]
    print(f"Keyword '{kw}': {len(found)} occurrences")

# Find table of variables
var_pos = full_text.find("Variable Name")
if var_pos != -1:
    print("\n--- Variable Table Section ---")
    print(full_text[var_pos:var_pos+2000])
else:
    # Look for BedMachine variables in text
    pos = full_text.find("thickness")
    if pos != -1:
        print("\n--- Around 'thickness' ---")
        print(full_text[max(0, pos-200):pos+800])

