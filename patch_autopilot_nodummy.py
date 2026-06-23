import re

with open('app/worker/autopilot.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the fallback for position_tickers
content = re.sub(
    r'position_tickers = run_sensus_pilihan\(\)\s*if not position_tickers:\s*position_tickers = \["BBCA\.JK", "BBRI\.JK", "BMRI\.JK"\] # fallback',
    r'''position_tickers = run_sensus_pilihan()
    if not position_tickers:
        print("   ❌ Sensus Position gagal atau tidak ada kandidat. Melewati proses Position.")
        position_tickers = []''',
    content
)

# Remove the fallback for swing_tickers
content = re.sub(
    r'swing_tickers = run_sensus_kavaleri\(\)\s*if not swing_tickers:\s*swing_tickers = \["BREN\.JK", "AMMN\.JK", "CUAN\.JK"\] # fallback',
    r'''swing_tickers = run_sensus_kavaleri()
    if not swing_tickers:
        print("   ❌ Sensus Swing gagal atau tidak ada kandidat. Melewati proses Swing.")
        swing_tickers = []''',
    content
)

with open('app/worker/autopilot.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Autopilot patched to remove dummy fallbacks.')
