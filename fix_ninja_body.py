with open(r'app\services\engines\technical_engine.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = False
for i, line in enumerate(lines):
    if line.startswith('    if len(df) < 50:') and 'analyze_ninja_scalper' in ''.join(lines[max(0, i-20):i]):
        new_lines.append(line)
        new_lines.append('        return {"signal": False, "reason": "Data kurang dari 50 candle"}\n')
        skip = True
        continue
    
    if skip:
        if line.startswith('    df = df.copy()'):
            skip = False
            new_lines.append(line)
        continue
        
    new_lines.append(line)

with open(r'app\services\engines\technical_engine.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print('Fixed indentation and body')
