import os

path = 'app/services/engines/data_engine.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Import APIKeyRouter
if 'from app.core.key_router import APIKeyRouter' not in content:
    content = content.replace('import pandas as pd', 'import pandas as pd\nfrom app.core.key_router import APIKeyRouter')

# 2. Update _apply_goapi_bulk_prices
old_func = '''def _apply_goapi_bulk_prices(data_dict, goapi_key):
    tickers = list(data_dict.keys())
    chunk_size = 50
    print(f"[Bulk API] Menarik harga Real-Time untuk {len(tickers)} saham dari GoAPI...")
    
    for i in range(0, len(tickers), chunk_size):
        chunk = tickers[i:i + chunk_size]
        symbols = ",".join([t.replace(".JK", "") for t in chunk])
        url = f"https://api.goapi.io/stock/idx/prices?symbols={symbols}"
        headers = {"X-API-KEY": goapi_key, "Accept": "application/json"} if goapi_key else {"Accept": "application/json"}'''

new_func = '''def _apply_goapi_bulk_prices(data_dict, goapi_key):
    tickers = list(data_dict.keys())
    chunk_size = 50
    print(f"[Bulk API] Menarik harga Real-Time untuk {len(tickers)} saham dari GoAPI...")
    
    router = APIKeyRouter("GoAPI")
    db_key, _ = router.get_key()
    final_key = goapi_key or db_key
    
    if not final_key:
        print("[Bulk API] Peringatan: Tidak ada GoAPI Key ditemukan di Database. Sensus hanya menggunakan data Yahoo Finance (Delay).")
    
    for i in range(0, len(tickers), chunk_size):
        chunk = tickers[i:i + chunk_size]
        symbols = ",".join([t.replace(".JK", "") for t in chunk])
        url = f"https://api.goapi.io/stock/idx/prices?symbols={symbols}"
        headers = {"X-API-KEY": final_key, "Accept": "application/json"} if final_key else {"Accept": "application/json"}'''

content = content.replace(old_func, new_func)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("data_engine.py patched with APIKeyRouter for Bulk API.")
