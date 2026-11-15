import requests
import json

entry_id = "synth:2d0e4791-8e20-46a3-80e4-f5f6716025d2:L2JtM190aGlja25lc3MudGlm"
url = f"https://ramadda.data.bas.ac.uk/repository/entry/show?entryid={entry_id}&output=json"
r = requests.get(url, timeout=10)
data = r.json()
print(json.dumps(data, indent=2))
