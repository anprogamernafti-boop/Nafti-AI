import re

with open('server.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the /api/ai endpoint
match = re.search(r\"@app\.route\('/api/ai'.*?(?=@app\.route|\Z)\", content, re.DOTALL)
if match:
    endpoint = match.group()
    lines = endpoint.split('\n')[:60]  # First 60 lines
    for i, line in enumerate(lines, 1):
        print(f'{i}: {line}')
