import os

path = 'app/services/engines/universe_engine.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

new_content = content.replace(
    'def build_universe(goapi_key: str = None):',
    'def build_universe(goapi_key: str = None):\n    from app.core.key_router import APIKeyRouter\n    import os\n    raw_keys = os.getenv("GOAPI_KEYS", os.getenv("GOAPI_KEY", goapi_key or ""))\n    goapi_router = APIKeyRouter(raw_keys)'
)

# Ganti blok eksekusi API GoAPI
old_api_block = '''        if goapi_key:
            try:
                symbols = ",".join([t.replace(".JK", "") for t in chunk])
                url = f"https://api.goapi.io/stock/idx/prices?symbols={symbols}"
                headers = {"X-API-KEY": goapi_key, "Accept": "application/json"}
                res = requests.get(url, headers=headers, timeout=15)
                if res.status_code == 200:
                    data = res.json().get("data", {}).get("results", [])
                    if data:
                        goapi_success = True
                        for rt in data:
                            ticker = rt.get("symbol") + ".JK"
                            close_price = float(rt.get("close", 0))
                            volume = float(rt.get("volume", 0))
                            change_percent = float(rt.get("percent", 0))

                            avg_value = close_price * volume
                            
                            # Filter Liquidity: Volume > 1M, Transaksi > 500 Juta, Harga > 50
                            if volume >= 1000000 and avg_value >= 500000000 and close_price >= 50:
                                valid_data.append(ticker)
                                
            except Exception as e:
                print(f"[Universe Builder] GoAPI Error: {e}")'''

new_api_block = '''        if goapi_router.has_active_keys():
            symbols = ",".join([t.replace(".JK", "") for t in chunk])
            url = f"https://api.goapi.io/stock/idx/prices?symbols={symbols}"
            
            while goapi_router.has_active_keys():
                current_key = goapi_router.get_key()
                try:
                    headers = {"X-API-KEY": current_key, "Accept": "application/json"}
                    res = requests.get(url, headers=headers, timeout=15)
                    
                    if res.status_code == 429:
                        print(f"[Universe Builder] GoAPI Limit Tercapai (429). Rotasi kunci...")
                        goapi_router.mark_dead(current_key)
                        continue
                        
                    if res.status_code == 200:
                        data = res.json().get("data", {}).get("results", [])
                        if data:
                            goapi_success = True
                            for rt in data:
                                ticker = rt.get("symbol") + ".JK"
                                close_price = float(rt.get("close", 0))
                                volume = float(rt.get("volume", 0))
                                change_percent = float(rt.get("percent", 0))

                                avg_value = close_price * volume
                                
                                # Filter Liquidity: Volume > 1M, Transaksi > 500 Juta, Harga > 50
                                if volume >= 1000000 and avg_value >= 500000000 and close_price >= 50:
                                    valid_data.append(ticker)
                        break # Success, exit retry loop
                    else:
                        break # Other HTTP error
                except Exception as e:
                    print(f"[Universe Builder] GoAPI Error: {e}")
                    break # Exception, break retry loop'''

if 'goapi_router.has_active_keys()' not in new_content:
    new_content = new_content.replace(old_api_block, new_api_block)

with open(path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print('universe_engine.py patched with API Key Rotator')
