import time
import os
from app.core.database import get_db_connection
from app.services.engines.master_engine import calculate_master_score
from app.services.engines.data_engine import download_daily_data
from app.services.engines.notif_engine import send_telegram_message
from app.services.engines.universe_engine import set_status
from app.core.idx_tickers import get_all_idx_tickers

def run_eod_autopilot():
    print("🚀 [MASTER AI] Memulai Proses Pemindaian Total...")
    
    # Ambil 800+ saham IDX
    all_tickers = get_all_idx_tickers()
    total_tickers = len(all_tickers)
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Kita tidak menghapus tabel, tapi REPLACE INTO atau bersihkan data lama
            cursor.execute("TRUNCATE TABLE idx_master")
        conn.commit()
    except Exception as e:
        print(f"Error reset db: {e}")
    finally:
        conn.close()

    chunk_size = 30
    intraday_count = 0
    swing_count = 0
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            for i in range(0, total_tickers, chunk_size):
                chunk = all_tickers[i:i + chunk_size]
                
                progress = int((i / total_tickers) * 95)
                set_status("running", progress, f"Master AI Menganalisa Batch {i//chunk_size + 1}...")
                print(f"   [MASTER SCAN] Mendownload Data Batch {i//chunk_size + 1}...")
                
                # Download data untuk batch ini (1y karena butuh EMA200)
                batch_data = download_daily_data(chunk, period="1y", use_premium=True)
                
                results = []
                for ticker, df in batch_data.items():
                    if df is None or df.empty: continue
                    
                    # Panggil AI Ranking Engine
                    analysis = calculate_master_score(df)
                    if analysis.get("error"): continue
                    
                    # Cek rekomendasi
                    if analysis["intraday_recommendation"] in ["BUY", "STRONG BUY"]:
                        intraday_count += 1
                    if analysis["swing_recommendation"] in ["BUY", "STRONG BUY"]:
                        swing_count += 1
                        
                    results.append((
                        ticker.replace(".JK", ""), "Unknown", analysis["close_price"], analysis["avg_value"], analysis["avg_volatility"],
                        analysis["relative_strength_score"], analysis["smart_money_score"], analysis["institutional_score"], analysis["catalyst_score"],
                        analysis["composite_score"], analysis["intraday_score"], analysis["swing_score"],
                        analysis["smart_money_status"], analysis["institutional_status"], analysis["catalyst_status"], analysis["trend_status"], analysis["setup_type"],
                        analysis["recommendation"], analysis["intraday_recommendation"], analysis["swing_recommendation"],
                        analysis["expected_return"], analysis["target_profit"], analysis["stop_loss"], analysis["risk_reward_ratio"]
                    ))
                
                if results:
                    sql = """
                        INSERT INTO idx_master (
                            ticker, sector, close_price, avg_value, avg_volatility,
                            relative_strength_score, smart_money_score, institutional_score, catalyst_score,
                            composite_score, intraday_score, swing_score,
                            smart_money_status, institutional_status, catalyst_status, trend_status, setup_type,
                            recommendation, intraday_recommendation, swing_recommendation,
                            expected_return, target_profit, stop_loss, risk_reward_ratio
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.executemany(sql, results)
                    conn.commit()
                
                del batch_data
                
            set_status("done", 100, "Sensus Master AI Selesai!", total_tickers, intraday_count + swing_count)
            print(f"✅ [MASTER AI] Berhasil menganalisa {total_tickers} saham!")
            
            # Kirim Telegram Rangkuman
            msg = f"📊 *Laporan Master Trading AI Selesai*\n\n"
            msg += f"⚡ *Intraday Momentum (Scalping)*: {intraday_count} Kandidat\n"
            msg += f"📈 *Swing Trading*: {swing_count} Kandidat\n\n"
            msg += f"Buka Command Center untuk melihat Composite Score. 🚀"
            send_telegram_message(msg)
            
    except Exception as e:
        print(f"❌ [MASTER AI] Gagal menyimpan ke DB: {e}")
        set_status("error", 0, f"Gagal memindai: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    run_eod_autopilot()
