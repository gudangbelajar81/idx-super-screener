import yfinance as yf
import pandas as pd
import pymysql
import numpy as np
import os

from config import MIN_DAILY_VOLUME
from idx_tickers import get_all_idx_tickers

# Nilai batas volatilitas (misal rata-rata pergerakan harian > 4% = Gorengan)
VOLATILITY_THRESHOLD = 0.04

from urllib.parse import urlparse

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
    Menjalankan sensus saham:
    1. Mengunduh data 1 bulan terakhir untuk 400+ saham secara serentak (batch).
    2. Menghitung likuiditas (Average Daily Value).
    3. Menghitung volatilitas (Average Daily Range).
    4. Menyimpan kategorinya ke database.
    """
    tickers = get_all_idx_tickers()
    
    # Download batch (sangat cepat karena multi-threading)
    print(f"[Universe Builder] Memulai sensus untuk {len(tickers)} saham...")
    
    # Kita bagi jadi beberapa batch jika terlalu banyak (tapi yfinance biasanya handle 400 dgn baik)
    # yfinance.download otomatis mereturn DataFrame dengan multi-index columns jika banyak ticker
    data = yf.download(tickers, period="1mo", threads=True, progress=False)
    
    results = []
    
    for ticker in tickers:
        try:
            # Ambil data spesifik per ticker
            # yf.download dengan banyak ticker mengembalikan kolom multi-level: (PriceType, Ticker)
            df = pd.DataFrame({
                'Close': data['Close'][ticker],
                'Volume': data['Volume'][ticker],
                'High': data['High'][ticker],
                'Low': data['Low'][ticker]
            }).dropna()
            
            if df.empty or len(df) < 10:
                results.append((ticker, "SAMPAH", 0, 0))
                continue
                
            # Hitung Likuiditas (Avg Value 20 hari terakhir)
            df['Value'] = df['Close'] * df['Volume']
            avg_value = df['Value'].tail(20).mean()
            
            # Hitung Volatilitas (Rata-rata jarak High ke Low dalam %)
            df['Range'] = (df['High'] - df['Low']) / df['Low']
            avg_volatility = df['Range'].tail(20).mean()
            
            # Klasifikasi
            if avg_value < MIN_DAILY_VOLUME:
                category = "SAMPAH"
            else:
                if avg_volatility > VOLATILITY_THRESHOLD:
                    category = "NINJA"
                else:
                    category = "SWING"
                    
            results.append((ticker, category, float(avg_value), float(avg_volatility)))
            
        except Exception as e:
            # Jika error (saham baru IPO, disuspend lama, dsb)
            results.append((ticker, "SAMPAH", 0, 0))

    # Simpan ke Database
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
