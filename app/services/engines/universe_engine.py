import yfinance as yf
import pandas as pd
import pymysql
import numpy as np
import os

from app.core.config import MIN_DAILY_VOLUME
from app.core.idx_tickers import get_all_idx_tickers

# Nilai batas volatilitas (misal rata-rata pergerakan harian > 4% = Gorengan)
VOLATILITY_THRESHOLD = 0.04

from urllib.parse import urlparse
import json
import time

STATUS_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "sensus_status.json")

def set_status(status, progress, message, total_scanned=0, total_found=0):
    try:
        with open(STATUS_FILE, "w") as f:
            json.dump({
                "status": status,
                "progress": progress,
                "message": message,
                "total_scanned": total_scanned,
                "total_found": total_found
            }, f)
    except Exception as e:
        print(f"Gagal menulis status: {e}")

def get_db_connection():
    db_url = os.environ.get("MYSQL_URL")
    if db_url:
        parsed = urlparse(db_url)
        return pymysql.connect(
            host=parsed.hostname,
            user=parsed.username,
            password=parsed.password,
            database=parsed.path[1:],
            port=parsed.port or 3306,
            cursorclass=pymysql.cursors.DictCursor
        )
    else:
        return pymysql.connect(
            host=os.environ.get("MYSQLHOST", "localhost"),
            user=os.environ.get("MYSQLUSER", "root"),
            password=os.environ.get("MYSQLPASSWORD") or os.environ.get("MYSQL_PASSWORD", ""),
            database=os.environ.get("MYSQLDATABASE", "idx_screener"),
            port=int(os.environ.get("MYSQLPORT", 3306)),
            cursorclass=pymysql.cursors.DictCursor
        )

def build_universe():
    """
    Menjalankan sensus saham secara Background Task:
    - Batching per 50 saham.
    - Menyimpan status ke sensus_status.json.
    """
    tickers = get_all_idx_tickers()
    total_tickers = len(tickers)
    print(f"[Universe Builder] Memulai sensus untuk {total_tickers} saham...")
    
    set_status("running", 0, f"Memulai sensus {total_tickers} saham...")
    
    results = []
    chunk_size = 50
    
    for i in range(0, total_tickers, chunk_size):
        chunk = tickers[i:i + chunk_size]
        batch_num = (i // chunk_size) + 1
        total_batches = (total_tickers // chunk_size) + 1
        
        set_status("running", int((i / total_tickers) * 100), f"Memproses batch {batch_num}/{total_batches} ({len(chunk)} saham)")
        print(f"[Universe Builder] Mendownload batch {batch_num}/{total_batches}...")
        
        try:
            data = yf.download(chunk, period="1mo", threads=True, progress=False)
            time.sleep(1) # Jeda menghindari rate limit
            
            for ticker in chunk:
                try:
                    if len(chunk) == 1:
                        df = data.dropna()
                    else:
                        df = pd.DataFrame({
                            'Close': data['Close'][ticker],
                            'Volume': data['Volume'][ticker],
                            'High': data['High'][ticker],
                            'Low': data['Low'][ticker]
                        }).dropna()
                    
                    if df.empty or len(df) < 10:
                        results.append((ticker, "SAMPAH", 0, 0))
                        continue
                        
                    df['Value'] = df['Close'] * df['Volume']
                    avg_value = df['Value'].tail(20).mean()
                    
                    df['Range'] = (df['High'] - df['Low']) / df['Low']
                    avg_volatility = df['Range'].tail(20).mean()
                    
                    if avg_value < MIN_DAILY_VOLUME:
                        category = "SAMPAH"
                    else:
                        if avg_volatility > VOLATILITY_THRESHOLD:
                            category = "NINJA"
                        elif avg_value >= 15_000_000_000:
                            category = "KAVALERI"
                        else:
                            category = "SWING"
                            
                    results.append((ticker, category, float(avg_value), float(avg_volatility)))
                except Exception:
                    results.append((ticker, "SAMPAH", 0, 0))
        except Exception as e:
            print(f"[Universe Builder] Batch {batch_num} gagal didownload: {e}")
            for ticker in chunk:
                results.append((ticker, "SAMPAH", 0, 0))

    # Simpan ke Database
    set_status("running", 95, "Menyimpan hasil ke database...")
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Bersihkan tabel lama
            cursor.execute("TRUNCATE TABLE idx_universe")
            
            # Masukkan data baru
            sql = "INSERT INTO idx_universe (ticker, category, avg_value, volatility) VALUES (%s, %s, %s, %s)"
            cursor.executemany(sql, results)
        conn.commit()
        print(f"[Universe Builder] Sensus Selesai! {len(results)} saham diklasifikasikan.")
        set_status("done", 100, "Sensus selesai!", total_tickers, len([r for r in results if r[1] != 'SAMPAH']))
    except Exception as e:
        print(f"[Universe Builder] Database Error: {e}")
        set_status("error", 0, f"Error Database: {e}")
    finally:
        conn.close()
        
    return {"status": "success", "total": len(results)}

def get_universe_by_category(category: str):
    """
    Mengambil daftar saham berdasarkan kategori.
    category: 'SWING' atau 'NINJA'
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT ticker FROM idx_universe WHERE category = %s", (category,))
            rows = cursor.fetchall()
            return [r['ticker'] for r in rows]
    finally:
        conn.close()

if __name__ == "__main__":
    build_universe()
