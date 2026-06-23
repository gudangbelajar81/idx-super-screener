import requests
import os
from datetime import datetime
from app.core.key_router import APIKeyRouter
from dotenv import load_dotenv

load_dotenv()

# Fallback ke hardcoded key jika di .env tidak ada
DEFAULT_GOAPI_KEY = "9801bcc5-9a0e-5762-08b8-178ad122"
BASE_URL = "https://api.goapi.io/stock/idx"

def get_goapi_router():
    return APIKeyRouter("GoAPI")

def get_headers(api_key):
    return {
        "X-API-KEY": api_key,
        "Accept": "application/json"
    }

def get_goapi_price(ticker):
    """Mengambil harga terbaru dari GoAPI"""
    router = get_goapi_router()
    
    while router.has_active_keys():
        current_key, _ = router.get_key()
        try:
            url = f"{BASE_URL}/prices?symbols={ticker}"
            res = requests.get(url, headers=get_headers(current_key), timeout=5)
            
            if res.status_code == 429:
                print(f"[GoAPI Engine] Rate limit 429 tercapai. Merotasi kunci...")
                router.mark_dead(current_key)
                continue
                
            if res.status_code == 200:
                data = res.json()
                if "data" in data and "results" in data["data"] and len(data["data"]["results"]) > 0:
                    result = data["data"]["results"][0]
                    return {
                        "price": float(result.get("close", 0)),
                        "open": float(result.get("open", 0)),
                        "high": float(result.get("high", 0)),
                        "low": float(result.get("low", 0)),
                        "volume": float(result.get("volume", 0)),
                        "change_pct": float(result.get("change_pct", 0))
                    }
                return None
        except Exception as e:
            print(f"GoAPI Price Error: {e}")
            break
            
    return None

def get_broker_summary(ticker):
    """
    Mengambil data Broker Summary (Bandarmologi) Asli dari GoAPI.
    Menghitung Top Buyer, Top Seller, Net Volume, dan Status Akumulasi/Distribusi.
    """
    router = get_goapi_router()
    import datetime
    
    while router.has_active_keys():
        current_key, _ = router.get_key()
        try:
            # Coba tarik data hari ini mundur maksimal 5 hari (melewati weekend/libur)
            success = False
            for i in range(5):
                check_date = (datetime.datetime.now() - datetime.timedelta(days=i)).strftime('%Y-%m-%d')
                url = f"{BASE_URL}/{ticker}/broker_summary?date={check_date}"
                
                res = requests.get(url, headers=get_headers(current_key), timeout=5)
                
                if res.status_code == 429:
                    print(f"[GoAPI Engine] Broker Summary Limit 429. Merotasi kunci...")
                    router.mark_dead(current_key)
                    success = False
                    break # Break inner loop, lanjut while loop untuk coba kunci baru
                    
                if res.status_code == 200:
                    success = True
                    data = res.json()
                    if "data" in data and "results" in data["data"]:
                        results = data["data"]["results"]
                        
                        if len(results) > 0:
                            # Pisahkan berdasar 'side'
                            buy_data = [r for r in results if r.get("side") == "BUY"]
                            sell_data = [r for r in results if r.get("side") == "SELL"]
                            
                            # Urutkan berdasarkan lot terbesar
                            buy_data = sorted(buy_data, key=lambda x: x.get("lot", 0), reverse=True)
                            sell_data = sorted(sell_data, key=lambda x: x.get("lot", 0), reverse=True)
                            
                            if buy_data and sell_data:
                                top_buyer = buy_data[0]
                                top_seller = sell_data[0]
                                
                                buy_lot = top_buyer.get("lot", 0)
                                sell_lot = top_seller.get("lot", 0)
                                
                                is_accumulation = buy_lot > sell_lot
                                
                                return {
                                    "status": "AKUMULASI" if is_accumulation else "DISTRIBUSI",
                                    "top_buyer": top_buyer.get("code", "N/A"),
                                    "top_seller": top_seller.get("code", "N/A"),
                                    "net_volume": abs(buy_lot - sell_lot),
                                    "avg_price": int(top_buyer.get("avg", 0) if is_accumulation else top_seller.get("avg", 0))
                                }
            
            # Jika lolos loop hari tapi tidak ada data
            if success:
                break 
                
        except Exception as e:
            print(f"GoAPI Broker Summary Error: {e}")
            break
            
    return {
        "status": "TIDAK ADA DATA",
        "top_buyer": "-",
        "top_seller": "-",
        "net_volume": 0,
        "avg_price": 0
    }
