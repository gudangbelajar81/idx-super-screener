import os

path = 'app/worker/autopilot.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

old_tickers = '''    # all_tickers = get_all_idx_tickers()
    all_tickers = ['BBCA.JK', 'BMRI.JK', 'BBRI.JK', 'BBNI.JK', 'TLKM.JK', 'AMMN.JK', 'BREN.JK', 'ASII.JK', 'BRPT.JK', 'CUAN.JK']'''

new_tickers = '''    all_tickers = get_all_idx_tickers()
    # all_tickers = ['BBCA.JK', 'BMRI.JK', 'BBRI.JK', 'BBNI.JK', 'TLKM.JK', 'AMMN.JK', 'BREN.JK', 'ASII.JK', 'BRPT.JK', 'CUAN.JK']'''

content = content.replace(old_tickers, new_tickers)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("autopilot.py patched to scan all tickers.")
