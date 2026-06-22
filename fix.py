import re

with open(r'app\services\engines\technical_engine.py', 'r', encoding='utf-8') as f:
    c = f.read()

idx = c.find('def analyze_ninja_scalper')
if idx != -1:
    idx2 = c.find('if len(df) < 50:\n', idx)
    if idx2 != -1:
        start_idx = idx2 + len('if len(df) < 50:\n')
        # Find the end of the wrongly inserted dictionary
        end_idx = c.find('    }\n', start_idx) + 6
        if end_idx > start_idx + 6:
            c = c[:start_idx] + '        return {"signal": False, "reason": "Data kurang dari 50 candle"}\n' + c[end_idx:]

with open(r'app\services\engines\technical_engine.py', 'w', encoding='utf-8') as f:
    f.write(c)
print('Fixed ninja scalper initial return')
