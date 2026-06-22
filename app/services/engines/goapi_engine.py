import requests
from datetime import datetime

API_KEY = "9801bcc5-9a0e-5762-08b8-178ad122"
BASE_URL = "https://api.goapi.io/stock/idx"
HEADERS = {
    "X-API-KEY": API_KEY,
    "Accept": "application/json"
}

def get_goapi_price(ticker):
    """Mengambil harga terbaru dari GoAPI"""
    try:
        url = f"{BASE_URL}/prices?symbols={ticker}"
        res = requests.get(url, headers=HEADERS, timeout=5)
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
    except Exception as e:
        print(f"GoAPI Price Error: {e}")
    return None

def get_broker_summary(ticker):
    """
    Mengambil data Broker Summary (Bandarmologi) Asli dari GoAPI.
    Menghitung Top Buyer, Top Seller, Net Volume, dan Status Akumulasi/Distribusi.
    """
    try:
        import datetime
        
        # Coba tarik data hari ini mundur maksimal 5 hari (melewati weekend/libur)
        for i in range(5):
            check_date = (datetime.datetime.now() - datetime.timedelta(days=i)).strftime('%Y-%m-%d')
            url = f"{BASE_URL}/{ticker}/broker_summary?date={check_date}"
            
            res = requests.get(url, headers=HEADERS, timeout=5)
            if res.status_code == 429:
                return {
                    "status": "LIMIT EXCEEDED",
                    "top_buyer": "-",
                    "top_seller": "-",
                    "net_volume": 0,
                    "avg_price": 0
                }
            if res.status_code == 200:
                data = res.json()
                if "data" in data and "results" in data["data"]:
                    results = data["data"]["results"]
                    
                    if len(results) > 0:
                        # Pisahkan berdasar 'side'
                        buy_data = [r for r in results if r.get("side") == "BUY"]
                        sell_data = [r for r in results if r.get("side") == "SELL"]
                        
                        # Urutkan berdasarkan lot terbesar (hanya berjaga-jaga jika API tidak mengurutkan)
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
    except Exception as e:
        print(f"GoAPI Broker Summary Error: {e}")
        
    return {
        "status": "TIDAK ADA DATA",
        "top_buyer": "-",
        "top_seller": "-",
        "net_volume": 0,
        "avg_price": 0
    }
