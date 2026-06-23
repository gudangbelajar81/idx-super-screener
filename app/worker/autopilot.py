import time
from app.core.database import get_db_connection
from app.services.engines.sensus_engine import run_sensus_pilihan, run_sensus_kavaleri
from app.services.engines.technical_engine import analyze_swing_fortress, analyze_cavalry_fast_swing
from app.services.engines.notif_engine import send_telegram_message

def run_eod_autopilot():
    print("🚀 [AUTOPILOT] Memulai Proses End of Day (EOD) Autopilot...")
    
    # 1. Jalankan Sensus Master (Filter Saham Pilihan)
    print("   [1/4] Menjalankan Sensus Position (Benteng)...")
    position_tickers = run_sensus_pilihan()
    
    print("   [2/4] Menjalankan Sensus Swing (Kavaleri)...")
    swing_tickers = run_sensus_kavaleri()
    
    # 2. Analisa Teknikal (VIP Scan)
    print("   [3/4] Melakukan Analisis VIP untuk Position...")
    # Mode Position menggunakan logika Swing Fortress yang ketat
    position_results = analyze_swing_fortress(position_tickers, limit=len(position_tickers))
    
    print("   [4/4] Melakukan Analisis VIP untuk Swing...")
    swing_results = analyze_cavalry_fast_swing(swing_tickers, limit=len(swing_tickers))
    
    # 3. Simpan ke Database (Tabel idx_signals)
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Hapus data lama agar Command Center selalu fresh
            cursor.execute("DELETE FROM idx_signals WHERE mode IN ('position', 'swing')")
            
            # Insert Position Signals
            pos_count = 0
            for res in position_results:
                if res.get('signal'):
                    cursor.execute("""
                        INSERT INTO idx_signals (ticker, mode, price, volatility, signal_text, status, reason, tp, sl)
                        VALUES (%s, 'position', %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        res['ticker'], res['price'], res.get('volatility', 0), res['signal'],
                        res['status'], res['reason'], res.get('tp'), res.get('sl')
                    ))
                    pos_count += 1
            
            # Insert Swing Signals
            swing_count = 0
            for res in swing_results:
                if res.get('signal'):
                    cursor.execute("""
                        INSERT INTO idx_signals (ticker, mode, price, volatility, signal_text, status, reason, tp, sl)
                        VALUES (%s, 'swing', %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        res['ticker'], res['price'], res.get('volatility', 0), res['signal'],
                        res['status'], res['reason'], res.get('tp'), res.get('sl')
                    ))
                    swing_count += 1
            
            conn.commit()
            print(f"✅ [AUTOPILOT] Berhasil menyimpan {pos_count} Sinyal Position dan {swing_count} Sinyal Swing ke Database!")
            
            # 4. Kirim Telegram
            msg = f"📊 *Laporan EOD Autopilot Selesai*\n\n"
            msg += f"🛡️ *Sinyal Position (Invest)*: {pos_count} Saham\n"
            msg += f"📈 *Sinyal Swing (Trend)*: {swing_count} Saham\n\n"
            msg += f"Silakan buka Command Center untuk melihat hasilnya. 🚀"
            send_telegram_message(msg)
            
    except Exception as e:
        print(f"❌ [AUTOPILOT] Gagal menyimpan ke DB: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    run_eod_autopilot()
