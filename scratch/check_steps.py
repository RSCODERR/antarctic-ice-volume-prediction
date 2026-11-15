import json

with open(r"C:\Users\akash\.gemini\antigravity\brain\52ad6ae8-887d-48db-85e7-7d53f431979f\.system_generated\logs\transcript.jsonl", "r", encoding="utf-8") as f:
    lines = f.readlines()

for line in lines[-50:-35]:
    data = json.loads(line)
    idx = data.get("step_index")
    if idx in (8444, 8445, 8452, 8454):
        print(f"step {idx}: {data.get('tool_calls', [{}])[0].get('args', {}).get('CommandLine', '')}")
