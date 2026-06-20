import time
from config import SWING_UNIVERSE, SCALP_UNIVERSE, MIN_DAILY_VOLUME
from data_engine import download_daily_data, download_intraday_data
from technical_engine import analyze_swing_fortress, analyze_ninja_scalper

def run_swing_fortress():
    print("\n" + "="*50)
    print("[ MODE BENTENG - SWING TRADING ]")
    print("="*50)
    
    daily_data = download_daily_data(SWING_UNIVERSE, period="1y")
    
    buy_candidates = []
    
    for ticker, df in daily_data.items():
        # Filter Likuiditas
        avg_volume = df['Volume'].tail(20).mean()
        last_close = df['Close'].iloc[-1]
        avg_value = avg_volume * last_close
        
        if avg_value < MIN_DAILY_VOLUME:
            print(f"[{ticker}] DITOLAK: Likuiditas terlalu kecil (Rp {avg_value:,.0f})")
            continue
            
        result = analyze_swing_fortress(df)
        
        if result['signal']:
            print(f"*** KANDIDAT SWING: {ticker} (Harga: {result['close']}) ***")
            print(f"   Alasan: Uptrend EMA200 & Momentum ZLSMA Naik & Terdapat Bullish FVG")
            buy_candidates.append(ticker)
        else:
            print(f"[{ticker}] Aman tapi belum ada sinyal beli.")
            
    print(f"\nTotal Kandidat Swing: {len(buy_candidates)}")


def run_ninja_scalper():
    print("\n" + "="*50)
    print("[ MODE NINJA - GORENGAN SCALPER ]")
    print("="*50)
    print("PERINGATAN: RISIKO SANGAT TINGGI. GUNAKAN MAKS 1% PORTOFOLIO.")
    
    # Download data 5 menit untuk 5 hari terakhir
    intraday_data = download_intraday_data(SCALP_UNIVERSE, interval="5m", period="5d")
    
    buy_candidates = []
    
    for ticker, df in intraday_data.items():
        result = analyze_ninja_scalper(df)
        
        if result['signal']:
            print(f"*** KANDIDAT SCALP: {ticker} (Harga: {result['close']}) ***")
            print(f"   Alasan: VOLUME MELEDAK! Lonjakan {result['spread_pct']:.2f}% dalam 5 menit terakhir.")
            buy_candidates.append(ticker)
        else:
            if result.get('volume_spike'):
                print(f"[{ticker}] Ada volume spike, tapi harga tidak naik tajam. Hati-hati Bandar Jualan.")
            else:
                print(f"[{ticker}] Sepi.")
                
    print(f"\nTotal Kandidat Scalping: {len(buy_candidates)}")

if __name__ == "__main__":
    print("Memulai Mesin Pengekstrak Kekayaan IDX...")
    time.sleep(1)
    
    run_swing_fortress()
    run_ninja_scalper()
    
    print("\nPemindaian Selesai.")
