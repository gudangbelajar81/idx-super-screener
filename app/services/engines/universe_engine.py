import yfinance as yf
import pandas as pd
import pymysql
import numpy as np
import os
import requests

from app.core.config import MIN_DAILY_VOLUME
from app.core.idx_tickers import get_all_idx_tickers

# Nilai batas volatilitas (misal rata-rata pergerakan harian > 2.5% = Gorengan)
VOLATILITY_THRESHOLD = 0.025

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

def build_universe(goapi_key: str = None):
    from app.core.key_router import APIKeyRouter
    import os
    raw_keys = os.getenv("GOAPI_KEYS", os.getenv("GOAPI_KEY", goapi_key or ""))
    goapi_router = APIKeyRouter(raw_keys)
    """
    Menjalankan sensus saham secara Background Task:
    - Menggunakan GoAPI jika goapi_key disediakan (Bypass blokir Yahoo)
    - Fallback ke Yahoo Finance jika gagal
    """
    tickers = get_all_idx_tickers()
    total_tickers = len(tickers)
    print(f"[Universe Builder] Memulai sensus untuk {total_tickers} saham (GoAPI Key terdeteksi: {bool(goapi_key)})...")
    
    set_status("running", 0, f"Memulai sensus {total_tickers} saham...")
    
    results = []
    chunk_size = 50
    
    for i in range(0, total_tickers, chunk_size):
        chunk = tickers[i:i + chunk_size]
        batch_num = (i // chunk_size) + 1
        total_batches = (total_tickers // chunk_size) + 1
        
        set_status("running", int((i / total_tickers) * 100), f"Memproses batch {batch_num}/{total_batches} ({len(chunk)} saham)")
        print(f"[Universe Builder] Mendownload batch {batch_num}/{total_batches}...")
        
        goapi_success = False
        if goapi_key:
            try:
                symbols = ",".join([t.replace(".JK", "") for t in chunk])
                url = f"https://api.goapi.io/stock/idx/prices?symbols={symbols}"
                headers = {"X-API-KEY": goapi_key, "Accept": "application/json"}
                res = requests.get(url, headers=headers, timeout=15)
                if res.status_code == 200:
                    data = res.json().get("data", {}).get("results", [])
                    if data:
                        goapi_success = True
                        for rt in data:
                            ticker = rt.get("symbol") + ".JK"
                            close_price = float(rt.get("close", 0))
                            volume = float(rt.get("volume", 0))
                            change_percent = float(rt.get("percent", 0))
                            
                            avg_value = close_price * volume
                            avg_volatility = abs(change_percent) / 100.0  # Konversi percent ke desimal
                            
                            if avg_value < MIN_DAILY_VOLUME or close_price == 0:
                                category = "SAMPAH"
                            else:
                                if avg_volatility > VOLATILITY_THRESHOLD:
                                    category = "NINJA"
                                elif avg_value >= 15_000_000_000:
                                    category = "KAVALERI"
                                else:
                                    category = "SWING"
                                    
                            results.append((ticker, category, avg_value, avg_volatility))
            except Exception as e:
                print(f"[Universe Builder] GoAPI Error: {e}")

        # Fallback ke Yahoo Finance jika GoAPI gagal atau tidak ada key
        if not goapi_success:
            print(f"[Universe Builder] Fallback ke Yahoo Finance untuk batch {batch_num}...")
            try:
                session = requests.Session()
                session.headers.update({
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5'
                })
                data = yf.download(chunk, period="1mo", threads=True, progress=False, session=session)
                
                for ticker in chunk:
                    try:
                        if len(chunk) == 1:
                            df = data.ffill().fillna(0)
                            df = df[df['Close'] > 0]
                        else:
                            if isinstance(data.columns, pd.MultiIndex):
                                df = pd.DataFrame({
                                    'Close': data['Close'][ticker],
                                    'Volume': data['Volume'][ticker],
                                    'High': data['High'][ticker],
                                    'Low': data['Low'][ticker]
                                }).ffill().fillna(0)
                                df = df[df['Close'] > 0]
                            else:
                                df = pd.DataFrame()
                        
                        if df.empty or len(df) < 10:
                            results.append((ticker, "SAMPAH", 0, 0))
                            continue
                            
                        df['Value'] = df['Close'] * df['Volume']
                        avg_value = df['Value'].tail(20).mean()
                        
                        df['Range'] = np.where(df['Low'] > 0, (df['High'] - df['Low']) / df['Low'], 0)
                        avg_volatility = df['Range'].tail(20).mean()
                        
                        avg_value = float(avg_value) if np.isfinite(avg_value) else 0.0
                        avg_volatility = float(avg_volatility) if np.isfinite(avg_volatility) else 0.0
                        
                        if avg_value < MIN_DAILY_VOLUME:
                            category = "SAMPAH"
                        else:
                            if avg_volatility > VOLATILITY_THRESHOLD:
                                category = "NINJA"
                            elif avg_value >= 15_000_000_000:
                                category = "KAVALERI"
                            else:
                                category = "SWING"
                                
                        results.append((ticker, category, avg_value, avg_volatility))
                    except Exception as e:
                        print(f"Error proses {ticker}: {e}")
                        results.append((ticker, "SAMPAH", 0.0, 0.0))
            except Exception as e:
                print(f"[Universe Builder] Batch {batch_num} gagal didownload: {e}")
                for ticker in chunk:
                    results.append((ticker, "SAMPAH", 0.0, 0.0))

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
        set_status("running", 50, "Sensus selesai, memuat Mesin VIP...")
        
        # Trigger Autopilot untuk memindai hasil sensus
        try:
            from app.worker.autopilot import run_eod_autopilot
            run_eod_autopilot()
        except Exception as e:
            print(f"[Universe Builder] Gagal menjalankan Autopilot: {e}")
            set_status("error", 50, f"Autopilot gagal: {e}")
            
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
