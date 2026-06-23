import time
import json
import os
from app.core.database import get_db_connection
from app.services.engines.technical_engine import analyze_swing_fortress, analyze_cavalry_fast_swing
from app.services.engines.data_engine import download_daily_data
from app.services.engines.notif_engine import send_telegram_message, notify_signal
from app.services.engines.universe_engine import set_status, get_universe_by_category

def run_eod_autopilot():
    print("🚀 [AUTOPILOT] Memulai Proses End of Day (EOD) Autopilot...")
    
    # Ambil kandidat dari idx_universe
    position_tickers = get_universe_by_category('SWING')
    swing_tickers = get_universe_by_category('SWING')  # Kavaleri juga ambil dari universe SWING
    
    if not position_tickers:
        print("❌ Sensus Master belum dijalankan atau tidak ada data di idx_universe.")
        set_status("error", 0, "Gagal memindai: Sensus Master belum dijalankan.")
        return
        
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM idx_signals WHERE mode IN ('position', 'swing')")
        conn.commit()
    except Exception as e:
        print(f"Error reset db: {e}")
    finally:
        conn.close()

    total_tickers = len(position_tickers)
    chunk_size = 20
    pos_count = 0
    swing_count = 0
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Pindai secara berurutan dan batched (menghindari OOM Memory Crash)
            for i in range(0, total_tickers, chunk_size):
                chunk = position_tickers[i:i + chunk_size]
                
                progress = 50 + int((i / total_tickers) * 45) # 50% sampai 95%
                set_status("running", progress, f"Menganalisa VIP Batch {i//chunk_size + 1}...")
                print(f"   [VIP SCAN] Mendownload Data Batch {i//chunk_size + 1}...")
                
                # Download data untuk batch ini (1y untuk Position)
                pos_data = download_daily_data(chunk, period="1y", use_premium=True)
                
                for ticker, df in pos_data.items():
                    if df is None or df.empty or len(df) < 200: continue
                    
                    # 1. Analisa Position (Benteng)
                    analysis_pos = analyze_swing_fortress(df)
                    last_close = df['Close'].iloc[-1]
                    
                    if analysis_pos.get("signal"):
                        cursor.execute("""
                            INSERT INTO idx_signals (ticker, mode, price, volatility, signal_text, status, reason, tp, sl)
                            VALUES (%s, 'position', %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            ticker.replace(".JK", ""), last_close, 0, analysis_pos['signal'],
                            analysis_pos['status'], analysis_pos['reason'], analysis_pos['tp'], analysis_pos['sl']
                        ))
                        pos_count += 1
                        res_dict = {
                            "ticker": ticker.replace(".JK", ""), "price": last_close, "signal": True,
                            "status": analysis_pos['status'], "reason": analysis_pos['reason'],
                            "tp": analysis_pos['tp'], "sl": analysis_pos['sl']
                        }
                        try:
                            notify_signal(res_dict, mode='position')
                        except Exception as e:
                            pass

                    # 2. Analisa Swing (Kavaleri)
                    if len(df) >= 50:
                        analysis_swing = analyze_cavalry_fast_swing(df)
                        if analysis_swing.get("signal"):
                            cursor.execute("""
                                INSERT INTO idx_signals (ticker, mode, price, volatility, signal_text, status, reason, tp, sl)
                                VALUES (%s, 'swing', %s, %s, %s, %s, %s, %s, %s)
                            """, (
                                ticker.replace(".JK", ""), last_close, 0, analysis_swing['signal'],
                                analysis_swing['status'], analysis_swing['reason'], analysis_swing['tp'], analysis_swing['sl']
                            ))
                            swing_count += 1
                            res_dict = {
                                "ticker": ticker.replace(".JK", ""), "price": last_close, "signal": True,
                                "status": analysis_swing['status'], "reason": analysis_swing['reason'],
                                "tp": analysis_swing['tp'], "sl": analysis_swing['sl']
                            }
                            try:
                                notify_signal(res_dict, mode='swing')
                            except Exception as e:
                                pass
                
                conn.commit()
                # Bebaskan memory
                del pos_data
                
            set_status("done", 100, "Pemindaian VIP Selesai!", total_tickers, pos_count + swing_count)
            print(f"✅ [AUTOPILOT] Berhasil menyimpan {pos_count} Sinyal Position dan {swing_count} Sinyal Swing ke Database!")
            
            # Kirim Telegram Rangkuman
            msg = f"📊 *Laporan EOD Autopilot Selesai*\n\n"
            msg += f"🛡️ *Sinyal Position (Invest)*: {pos_count} Saham\n"
            msg += f"📈 *Sinyal Swing (Trend)*: {swing_count} Saham\n\n"
            msg += f"Silakan buka Command Center untuk melihat hasilnya. 🚀"
            send_telegram_message(msg)
            
    except Exception as e:
        print(f"❌ [AUTOPILOT] Gagal menyimpan ke DB: {e}")
        set_status("error", 0, f"Gagal memindai: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    run_eod_autopilot()
