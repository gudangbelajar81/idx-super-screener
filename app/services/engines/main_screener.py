import time
from app.core.config import SWING_UNIVERSE, SCALP_UNIVERSE, MIN_DAILY_VOLUME
from app.services.engines.data_engine import download_daily_data, download_intraday_data
from app.services.engines.technical_engine import analyze_swing_fortress, analyze_ninja_scalper
from app.services.engines.macro_engine import get_macro_data
from app.services.engines.sensus_engine import run_sensus_pilihan
from app.services.engines.notif_engine import notify_macro_warning, notify_signal

def run_swing_fortress(macro_condition: str, universe: list):
    print("\n" + "="*50)
    print(f"[ MODE BENTENG - SWING TRADING | Makro: {macro_condition} ]")
    print("="*50)
    
    if macro_condition == "BAHAYA":
        print("[WARNING] MAAF BOS, PASAR SEDANG BADAI (BAHAYA). MODE SWING DIBEKUKAN SEMENTARA.")
        return []
        
    daily_data = download_daily_data(universe, period="1y")
    
    buy_candidates = []
    
    for ticker, df in daily_data.items():
        if df.empty or len(df) < 200:
            continue
            
        avg_volume = df['Volume'].tail(20).mean()
        last_close = df['Close'].iloc[-1]
        avg_value = avg_volume * last_close
        
        if avg_value < MIN_DAILY_VOLUME:
            print(f"[{ticker}] DITOLAK: Likuiditas terlalu kecil (Rp {avg_value:,.0f})")
            continue
            
        result = analyze_swing_fortress(df)
        
        if result.get('signal'):
            print(f"*** KANDIDAT SWING: {ticker} (Harga: {result['close']}) ***")
            print(f"   Aksi Bandar: {result.get('bandar_verdict', 'netral')} | Win Prob: {result.get('win_probability', 0)}%")
            result['ticker'] = ticker
            result['price'] = result['close']
            buy_candidates.append(result)
            notify_signal(result, mode="swing")
        else:
            print(f"[{ticker}] Aman tapi belum ada sinyal beli.")
            
    print(f"\nTotal Kandidat Swing: {len(buy_candidates)}")
    return buy_candidates


def run_ninja_scalper(macro_condition: str, universe: list):
    print("\n" + "="*50)
    print(f"[ MODE NINJA - GORENGAN SCALPER | Makro: {macro_condition} ]")
    print("="*50)
    print("PERINGATAN: RISIKO SANGAT TINGGI. GUNAKAN MAKS 1% PORTOFOLIO.")
    
    # Kalau market BAHAYA, scalping justru kadang menguntungkan, tapi universe dikurangi.
    intraday_data = download_intraday_data(universe, interval="5m", period="5d")
    
    buy_candidates = []
    
    for ticker, df in intraday_data.items():
        if df.empty or len(df) < 50:
            continue
            
        result = analyze_ninja_scalper(df)
        
        if result.get('signal'):
            print(f"*** KANDIDAT SCALP: {ticker} (Harga: {result['close']}) ***")
            print(f"   Lonjakan {result['spread_pct']:.2f}% | Win Prob: {result.get('win_probability', 0)}%")
            result['ticker'] = ticker
            result['price'] = result['close']
            buy_candidates.append(result)
            notify_signal(result, mode="ninja")
        else:
            if result.get('volume_spike'):
                print(f"[{ticker}] Ada volume spike, tapi harga tidak naik tajam. Hati-hati Bandar Jualan.")
            else:
                print(f"[{ticker}] Sepi.")
                
    print(f"\nTotal Kandidat Scalping: {len(buy_candidates)}")
    return buy_candidates

if __name__ == "__main__":
    print("Memulai Mesin Pengekstrak Kekayaan IDX (Titan Engine v3)...")
    time.sleep(1)
    
    # 1. Pengecekan Makro Ekonomi (IHSG & USD)
    print("\n--- 1. ANALISIS MAKRO EKONOMI ---")
    macro_data = get_macro_data()
    macro_cond = macro_data.get("market_condition", "NETRAL")
    print(f"Kondisi Pasar: {macro_cond}")
    if macro_cond in ["WASPADA", "BAHAYA"]:
        notify_macro_warning(macro_data)
        
    # 2. Sensus Rotasi Sektor (Pemilihan Universe Dinamis)
    print("\n--- 2. SENSUS ROTASI SEKTOR ---")
    print("Mencari saham dengan uang institusi masuk (CMF Positif & Uptrend)...")
    sensus_winners = run_sensus_pilihan()
    
    if sensus_winners:
        active_swing_universe = sensus_winners
        print(f"Sensus Selesai! Menggunakan {len(active_swing_universe)} saham pilihan untuk Swing.")
    else:
        active_swing_universe = SWING_UNIVERSE
        print("Sensus gagal / tidak ada hasil. Menggunakan Universe Default.")
        
    # Untuk scalper kita biarkan default liar (karena gorengan tidak kenal makro)
    active_scalp_universe = SCALP_UNIVERSE
    
    # 3. Eksekusi Strategi Utama
    print("\n--- 3. PENYARINGAN UTAMA ---")
    run_swing_fortress(macro_cond, active_swing_universe)
    run_ninja_scalper(macro_cond, active_scalp_universe)
    
    print("\nPemindaian Selesai.")


