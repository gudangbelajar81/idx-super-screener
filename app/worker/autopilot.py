import time
import concurrent.futures
from app.core.database import get_db_connection
from app.services.engines.sensus_engine import run_sensus_pilihan, run_sensus_kavaleri
from app.services.engines.technical_engine import analyze_swing_fortress, analyze_cavalry_fast_swing
from app.services.engines.data_engine import download_daily_data
from app.services.engines.notif_engine import send_telegram_message, notify_signal

def process_position(args):
    ticker, df = args
    if df is None or df.empty or len(df) < 200: return None
    analysis = analyze_swing_fortress(df)
    last_close = df['Close'].iloc[-1]
    return {
        "ticker": ticker.replace(".JK", ""),
        "price": last_close,
        "signal": analysis.get("signal", False),
        "status": analysis.get("status", "Sepi"),
        "reason": analysis.get("reason", ""),
        "tp": analysis.get("tp"),
        "sl": analysis.get("sl"),
        "volatility": 0
    }

def process_swing(args):
    ticker, df = args
    if df is None or df.empty or len(df) < 50: return None
    analysis = analyze_cavalry_fast_swing(df)
    last_close = df['Close'].iloc[-1]
    return {
        "ticker": ticker.replace(".JK", ""),
        "price": last_close,
        "signal": analysis.get("signal", False),
        "status": analysis.get("status", "Sepi"),
        "reason": analysis.get("reason", ""),
        "tp": analysis.get("tp"),
        "sl": analysis.get("sl"),
        "volatility": 0
    }

def run_eod_autopilot():
    print("🚀 [AUTOPILOT] Memulai Proses End of Day (EOD) Autopilot...")
    
    # 1. Jalankan Sensus Master
    print("   [1/4] Menjalankan Sensus Position (Benteng)...")
    position_tickers = run_sensus_pilihan()
    if not position_tickers:
        print("   ❌ Sensus Position gagal atau tidak ada kandidat. Melewati proses Position.")
        position_tickers = []
        
    print("   [2/4] Menjalankan Sensus Swing (Kavaleri)...")
    swing_tickers = run_sensus_kavaleri()
    if not swing_tickers:
        print("   ❌ Sensus Swing gagal atau tidak ada kandidat. Melewati proses Swing.")
        swing_tickers = []
    
    # 2. Download Data & Analisa
    print("   [3/4] Mendownload Data & Analisis VIP untuk Position...")
    pos_data = download_daily_data(position_tickers, period="1y", use_premium=True)
    position_results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        results = executor.map(process_position, pos_data.items())
        for res in results:
            if res: position_results.append(res)
            
    print("   [4/4] Mendownload Data & Analisis VIP untuk Swing...")
    swing_data = download_daily_data(swing_tickers, period="6mo", use_premium=True)
    swing_results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        results = executor.map(process_swing, swing_data.items())
        for res in results:
            if res: swing_results.append(res)
    
    # 3. Simpan ke Database
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM idx_signals WHERE mode IN ('position', 'swing')")
            
            pos_count = 0
            for res in position_results:
                if res.get('signal'):
                    cursor.execute("""
                        INSERT INTO idx_signals (ticker, mode, price, volatility, signal_text, status, reason, tp, sl)
                        VALUES (%s, 'position', %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        res['ticker'], res['price'], res['volatility'], res['signal'],
                        res['status'], res['reason'], res['tp'], res['sl']
                    ))
                    pos_count += 1
                    try:
                        notify_signal(res, mode='position')
                    except Exception as e:
                        print(f"Gagal kirim notif telegram (Position): {e}")
            
            swing_count = 0
            for res in swing_results:
                if res.get('signal'):
                    cursor.execute("""
                        INSERT INTO idx_signals (ticker, mode, price, volatility, signal_text, status, reason, tp, sl)
                        VALUES (%s, 'swing', %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        res['ticker'], res['price'], res['volatility'], res['signal'],
                        res['status'], res['reason'], res['tp'], res['sl']
                    ))
                    swing_count += 1
                    try:
                        notify_signal(res, mode='swing')
                    except Exception as e:
                        print(f"Gagal kirim notif telegram (Swing): {e}")
            
            conn.commit()
            print(f"✅ [AUTOPILOT] Berhasil menyimpan {pos_count} Sinyal Position dan {swing_count} Sinyal Swing ke Database!")
            
            # 4. Kirim Telegram
            msg = f"📊 *Laporan EOD Autopilot Selesai*\\n\\n"
            msg += f"🛡️ *Sinyal Position (Invest)*: {pos_count} Saham\\n"
            msg += f"📈 *Sinyal Swing (Trend)*: {swing_count} Saham\\n\\n"
            msg += f"Silakan buka Command Center untuk melihat hasilnya. 🚀"
            send_telegram_message(msg)
            
    except Exception as e:
        print(f"❌ [AUTOPILOT] Gagal menyimpan ke DB: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    run_eod_autopilot()
