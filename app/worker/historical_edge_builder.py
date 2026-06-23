import os
import sys
import json
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

# Pastikan path import benar
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from app.services.engines.astro_engine import get_astro_cycles

DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'historical_edge_db.json')

def build_astro_map(start_date, end_date):
    """Membangun lookup table untuk Astro Cycles."""
    print(f"[*] Menghitung Ephemeris Astro dari {start_date} hingga {end_date}...")
    markers = get_astro_cycles(start_date, end_date)
    astro_map = {}
    for m in markers:
        # Menyimpan fase astro untuk tanggal tertentu
        phase_name = m['text'].split(' ')[1] if ' ' in m['text'] else m['text']
        astro_map[m['time']] = phase_name
    return astro_map

def calculate_technical_setup(df):
    """Menghitung Setup (Volume Spike & Breakout)"""
    df['Vol_MA20'] = df['Volume'].rolling(window=20).mean()
    df['Vol_Spike'] = df['Volume'] > (df['Vol_MA20'] * 2.0)
    
    df['High_20'] = df['High'].rolling(window=20).max().shift(1)
    df['Breakout'] = df['Close'] > df['High_20']
    
    # Setup = Breakout + Volume Spike
    df['Setup_Valid'] = df['Vol_Spike'] & df['Breakout']
    return df

def simulate_forward_returns(df, entry_idx, lookforward=15):
    """Mensimulasikan apakah harga mengenai TP dalam 15 hari ke depan."""
    if entry_idx + 1 >= len(df):
        return False, False, False, False
        
    entry_price = df['Close'].iloc[entry_idx]
    
    # Ambil 15 hari ke depan
    end_idx = min(entry_idx + 1 + lookforward, len(df))
    future_data = df.iloc[entry_idx+1:end_idx]
    
    max_high = future_data['High'].max()
    max_gain_pct = ((max_high - entry_price) / entry_price) * 100
    
    hit_tp1 = max_gain_pct >= 5.0
    hit_tp2 = max_gain_pct >= 8.0
    hit_tp3 = max_gain_pct >= 12.0
    hit_tp4 = max_gain_pct >= 15.0
    
    return hit_tp1, hit_tp2, hit_tp3, hit_tp4

def build_historical_edge(tickers, start_date="2019-01-01"):
    print(f"[*] Memulai Historical Edge Engine (Backtester) untuk {len(tickers)} saham...")
    end_date = datetime.now().strftime("%Y-%m-%d")
    astro_map = build_astro_map(start_date, end_date)
    
    results = {
        "overall": {"total_setups": 0, "tp1_hits": 0, "tp2_hits": 0, "tp3_hits": 0, "tp4_hits": 0},
        "by_astro": {}
    }
    
    for ticker in tickers:
        print(f"  - Mengunduh & Simulasi: {ticker} ...")
        try:
            df = yf.download(ticker, start=start_date, end=end_date, progress=False)
            if df.empty:
                continue
                
            # Flatten multi-index columns if exist (yfinance newer versions)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
                
            df = calculate_technical_setup(df)
            
            # Cari hari di mana Setup_Valid == True
            setup_indices = df.index[df['Setup_Valid'] == True].tolist()
            
            for date_idx in setup_indices:
                idx_pos = df.index.get_loc(date_idx)
                date_str = date_idx.strftime("%Y-%m-%d")
                
                tp1, tp2, tp3, tp4 = simulate_forward_returns(df, idx_pos)
                
                # Update Overall
                results["overall"]["total_setups"] += 1
                if tp1: results["overall"]["tp1_hits"] += 1
                if tp2: results["overall"]["tp2_hits"] += 1
                if tp3: results["overall"]["tp3_hits"] += 1
                if tp4: results["overall"]["tp4_hits"] += 1
                
                # Cek Astro Confluence
                astro_phase = astro_map.get(date_str, "Normal")
                if astro_phase not in results["by_astro"]:
                    results["by_astro"][astro_phase] = {"total_setups": 0, "tp1_hits": 0, "tp2_hits": 0, "tp3_hits": 0, "tp4_hits": 0}
                
                results["by_astro"][astro_phase]["total_setups"] += 1
                if tp1: results["by_astro"][astro_phase]["tp1_hits"] += 1
                if tp2: results["by_astro"][astro_phase]["tp2_hits"] += 1
                if tp3: results["by_astro"][astro_phase]["tp3_hits"] += 1
                if tp4: results["by_astro"][astro_phase]["tp4_hits"] += 1
                
        except Exception as e:
            print(f"    [!] Error pada {ticker}: {str(e)}")
            continue

    # Konversi ke Persentase
    final_db = {
        "last_updated": end_date,
        "base_win_rates": {},
        "astro_modifiers": {}
    }
    
    # Calculate Base
    tot = results["overall"]["total_setups"]
    if tot > 0:
        final_db["base_win_rates"] = {
            "tp1_prob": round((results["overall"]["tp1_hits"] / tot) * 100, 1),
            "tp2_prob": round((results["overall"]["tp2_hits"] / tot) * 100, 1),
            "tp3_prob": round((results["overall"]["tp3_hits"] / tot) * 100, 1),
            "tp4_prob": round((results["overall"]["tp4_hits"] / tot) * 100, 1),
        }
    
    # Calculate Astro Modifiers
    for phase, stats in results["by_astro"].items():
        ptot = stats["total_setups"]
        if ptot >= 5: # Minimal sampel statistik
            p_tp1 = round((stats["tp1_hits"] / ptot) * 100, 1)
            p_tp3 = round((stats["tp3_hits"] / ptot) * 100, 1)
            
            # Cek seberapa kuat boost/penalty nya dibanding base
            boost_tp3 = round(p_tp3 - final_db.get("base_win_rates", {}).get("tp3_prob", 0), 1)
            
            final_db["astro_modifiers"][phase] = {
                "tp1_prob": p_tp1,
                "tp3_prob": p_tp3,
                "boost_tp3": boost_tp3,
                "sample_size": ptot
            }
            
    # Simpan ke file
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with open(DB_PATH, 'w') as f:
        json.dump(final_db, f, indent=4)
        
    print(f"[*] Selesai! Database tersimpan di {DB_PATH}")
    print(json.dumps(final_db, indent=4))

if __name__ == "__main__":
    # Untuk demonstrasi, kita jalankan pada Top 10 Saham Bluechip & Explosive IDX
    test_tickers = ["BBCA.JK", "BMRI.JK", "BBRI.JK", "BBNI.JK", "TLKM.JK", "AMMN.JK", "BREN.JK", "ASII.JK", "BRPT.JK", "CUAN.JK"]
    build_historical_edge(test_tickers)
