import concurrent.futures
from app.services.engines.goapi_engine import get_broker_summary, get_goapi_price

WHALE_BROKERS = ["AK", "BK", "ZP", "CS", "RX", "YU", "KZ", "CG", "YP", "CC", "NI"]

def process_single_ticker(ticker):
    """Memproses satu saham untuk mencari jejak akumulasi Paus."""
    try:
        broker_data = get_broker_summary(ticker)
        
        # MOCK DATA FALLBACK JIKA API LIMIT HABIS
        if broker_data.get("status") == "LIMIT EXCEEDED":
            import random
            if random.random() < 0.1: # 10% peluang jadi Paus bohongan untuk tes UI
                return {
                    "ticker": ticker,
                    "price": 1000 + random.randint(-50, 100),
                    "signal": True,
                    "status": "PAUS TERDETEKSI (MOCK)",
                    "reason": "Simulasi Limit API",
                    "top_buyer": random.choice(WHALE_BROKERS),
                    "net_volume": random.randint(15000, 50000),
                    "avg_price": 1000,
                    "is_golden": True,
                    "is_danger": False,
                    "diff_pct": -1.5
                }
            return None

        # Hanya filter yang sedang diakumulasi
        if broker_data.get("status") != "AKUMULASI":
            return None
            
        top_buyer = broker_data.get("top_buyer", "")
        net_volume = broker_data.get("net_volume", 0)
        avg_price = broker_data.get("avg_price", 0)
        
        # Syarat Paus: Broker masuk daftar WHALE atau Net Volume > 10.000 lot
        is_whale_broker = top_buyer in WHALE_BROKERS
        is_massive_volume = net_volume > 10000
        
        if not (is_whale_broker or is_massive_volume):
            return None
            
        # Ambil harga real-time untuk cek Golden Entry
        price_data = get_goapi_price(ticker)
        current_price = price_data["price"] if price_data else avg_price
        
        # Hitung Golden Entry
        is_golden = False
        is_danger = False
        diff_pct = 0.0
        
        if avg_price > 0 and current_price > 0:
            diff_pct = ((current_price - avg_price) / avg_price) * 100
            if current_price <= avg_price * 1.01: # Harga di bawah atau max 1% di atas rata-rata bandar
                is_golden = True
            elif current_price > avg_price * 1.05: # Sudah naik > 5% dari harga bandar
                is_danger = True
                
        return {
            "ticker": ticker,
            "price": current_price,
            "signal": True, # Untuk trigger UI/Notif
            "status": "PAUS TERDETEKSI",
            "reason": f"Akumulasi {net_volume} Lot",
            "top_buyer": top_buyer,
            "net_volume": net_volume,
            "avg_price": avg_price,
            "is_golden": is_golden,
            "is_danger": is_danger,
            "diff_pct": round(diff_pct, 2)
        }
    except Exception as e:
        print(f"Error processing {ticker} in Whale Engine: {e}")
        return None

def scan_whale_accumulation(tickers):
    """
    Memindai puluhan saham secara paralel untuk mencari jejak Paus.
    Menggunakan ThreadPoolExecutor untuk mempercepat proses ke GoAPI.
    """
    results = []
    
    # Batasi max_workers agar tidak kena rate limit API
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_ticker = {executor.submit(process_single_ticker, ticker): ticker for ticker in tickers}
        
        for future in concurrent.futures.as_completed(future_to_ticker):
            data = future.result()
            if data is not None:
                results.append(data)
                
    # Urutkan berdasarkan net_volume terbesar
    results = sorted(results, key=lambda x: x["net_volume"], reverse=True)
    return results
