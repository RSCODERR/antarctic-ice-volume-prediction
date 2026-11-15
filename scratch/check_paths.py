import os
import re

pattern = re.compile(r'[a-zA-Z]:\\[^"\n\r\t]+|/home/[^"\n\r\t]+|/Users/[^"\n\r\t]+')
matches = []

for root, dirs, files in os.walk('src'):
    for f in files:
        if f.endswith('.py'):
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8', errors='ignore') as fp:
                for lno, line in enumerate(fp, 1):
                    # Ignore comments that are just examples or docs
                    if line.strip().startswith('#'):
                        continue
                    m = pattern.search(line)
                    if m:
                        matches.append((path, lno, m.group(0)))

print(f"Hardcoded paths in src/ ({len(matches)}):")
for p, l, val in matches:
    print(f"  {p}:{l} -> {val}")
