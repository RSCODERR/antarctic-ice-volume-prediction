import os

for root, dirs, files in os.walk('.'):
    if any(x in root for x in ['.venv', '.git', '__pycache__', 'archive']):
        continue
    for f in files:
        if f.endswith(('.py', '.csv', '.md', '.json', '.yaml', '.yml')):
            p = os.path.join(root, f)
            try:
                with open(p, 'r', encoding='utf-8', errors='ignore') as fl:
                    cnt = fl.read()
                    matches = []
                    for term in ['FL_HPI_02', 'Millett', 'Flask', 'Drygalski', 'FL_IPPJ_01', 'FL_IPPJ_03']:
                        if term in cnt:
                            matches.append(term)
                    if matches:
                        print(f"{p}: {matches}")
            except Exception as e:
                pass

