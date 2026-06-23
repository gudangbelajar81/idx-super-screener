import os
import json

path = 'app/services/engines/master_engine.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Tambahkan import json dan os di bagian atas
if 'import json' not in content:
    content = content.replace('import pandas as pd', 'import pandas as pd\nimport json\nimport os')

# Tambahkan fungsi load_edge_db sebelum calculate_master_score
EDGE_DB_LOAD = '''
EDGE_DB_CACHE = None

def get_edge_db():
    global EDGE_DB_CACHE
    if EDGE_DB_CACHE is None:
        try:
            db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'historical_edge_db.json')
            with open(db_path, 'r') as f:
                EDGE_DB_CACHE = json.load(f)
        except:
            EDGE_DB_CACHE = {"base_win_rates": {}, "astro_modifiers": {}}
    return EDGE_DB_CACHE
'''
if 'def get_edge_db' not in content:
    content = content.replace('def calculate_master_score', EDGE_DB_LOAD + '\ndef calculate_master_score')

# Tambahkan hitungan ATR dan logika is_swing_eligible
ATR_LOGIC = '''
    # Volatilitas (ATR%)
    df['ATR'] = ta.volatility.average_true_range(df['High'], df['Low'], df['Close'], window=14)
    atr_val = df['ATR'].iloc[-1]
    atr_pct = (atr_val / last_close) * 100 if last_close > 0 else 0
'''
if "df['ATR'] =" not in content:
    content = content.replace('cmf_20 = calc_chaikin_money_flow(df, period=20)', 'cmf_20 = calc_chaikin_money_flow(df, period=20)\n' + ATR_LOGIC)

content = content.replace("not pd.isna(curr['EMA200']) and", "not pd.isna(curr['EMA200']) and\n        atr_pct >= 3.0 and # FILTER SAHAM KEONG")

# Injeksi edge_data di return dict
EDGE_INJECT = '''
    # Inject Historical Edge Data
    edge_db = get_edge_db()
    # Untuk simulasi, kita anggap astro hari ini Normal, tapi jika ada boost, kita kirim.
    # Secara default kita kirim base win rates
    edge_data = edge_db.get("base_win_rates", {})
    # Bisa tambahkan logika Astro disini jika perlu
'''

if 'edge_db = get_edge_db()' not in content:
    content = content.replace('# Projections', EDGE_INJECT + '\n    # Projections')

if '"edge_data": edge_data' not in content:
    content = content.replace('"risk_reward_ratio": rr', '"risk_reward_ratio": rr,\n        "edge_data": json.dumps(edge_data)')

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print('master_engine.py updated')
