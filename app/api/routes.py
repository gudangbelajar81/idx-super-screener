from app.core.database import get_db_connection
import pymysql
from fastapi import APIRouter, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import concurrent.futures
import os
from urllib.parse import urlparse
from dbutils.pooled_db import PooledDB
from cachetools import cached, TTLCache

from app.core.config import MIN_DAILY_VOLUME
from app.services.engines.data_engine import download_daily_data, download_intraday_data, download_global_data
from app.services.engines.technical_engine import analyze_swing_fortress, analyze_ninja_scalper, analyze_cavalry_fast_swing
from app.services.engines.news_engine import get_news_sentiment, get_ipo_news
from app.services.engines.macro_engine import get_macro_data
from app.services.engines.notif_engine import notify_signal, notify_macro_warning
from app.services.engines.universe_engine import build_universe, get_universe_by_category
from app.services.engines.sensus_engine import run_sensus_pilihan, run_sensus_ninja, run_sensus_kavaleri
from apscheduler.schedulers.background import BackgroundScheduler
from app.services.engines.notif_engine import send_telegram_message
from app.services.engines.paper_engine import record_paper_trade, get_paper_portfolio, evaluate_open_trades
from app.services.engines.whale_engine import scan_whale_accumulation
from app.services.engines.astro_engine import get_astro_cycles, get_current_astro_forecast
from fastapi import Security, Depends
from fastapi.security.api_key import APIKeyHeader
from app.core.config import API_SECRET_KEY

router = APIRouter()

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_SECRET_KEY:
        raise HTTPException(status_code=403, detail="Akses Ditolak: Kunci API Salah atau Tidak Ada")
    return api_key


class WatchlistItem(BaseModel):
    ticker: str
    mode: str

@router.get("/api/watchlist")
def get_watchlist():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, ticker, mode FROM watchlists ORDER BY id DESC LIMIT 500")
            return {"data": cursor.fetchall()}
    finally:
        conn.close()

@router.post("/api/watchlist")
def add_watchlist(item: WatchlistItem, api_key: str = Depends(verify_api_key)):
    # Ensure ticker ends with .JK for Yahoo Finance
    ticker = item.ticker.upper()
    if not ticker.endswith(".JK"):
        ticker += ".JK"
        
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Check if exists
            cursor.execute("SELECT id FROM watchlists WHERE ticker=%s", (ticker,))
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail="Ticker already exists")
                
            cursor.execute("INSERT INTO watchlists (ticker, mode) VALUES (%s, %s)", (ticker, item.mode))
            conn.commit()
            return {"message": "Success", "ticker": ticker}
    finally:
        conn.close()

@router.delete("/api/watchlist/{id}")
def delete_watchlist(id: int, api_key: str = Depends(verify_api_key)):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM watchlists WHERE id=%s", (id,))
            conn.commit()
            return {"message": "Deleted"}
    finally:
        conn.close()

@router.post("/api/sensus")
def trigger_sensus(api_key: str = Depends(verify_api_key)):
    """
    Menjalankan proses Sensus Emiten Pilihan.
    Menghapus watchlist lama, dan memasukkan saham-saham pilihan yang lolos sensor ketat.
    """
    # 1. Jalankan algoritma Sensus (mengunduh data ratusan saham & filter)
    curated_tickers = run_sensus_pilihan()
    
    if not curated_tickers:
        return {"message": "Tidak ada saham yang memenuhi kriteria ketat hari ini.", "count": 0}
        
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 2. Hapus watchlist lama (Khusus Mode Swing agar bisa diganti hasil sensus)
            cursor.execute("DELETE FROM watchlists WHERE mode='swing'")
            
            # 3. Masukkan kandidat baru
            for ticker in curated_tickers:
                # Pastikan format .JK
                ticker_jk = ticker if ticker.endswith(".JK") else f"{ticker}.JK"
                cursor.execute("INSERT INTO watchlists (ticker, mode) VALUES (%s, %s)", (ticker_jk, 'swing'))
            
            conn.commit()
            
        return {"message": f"Sensus Selesai! {len(curated_tickers)} saham super dimasukkan ke Screener.", "count": len(curated_tickers)}
    finally:
        conn.close()

@router.post("/api/sensus/ninja")
def trigger_sensus_ninja(api_key: str = Depends(verify_api_key)):
    """
    Menjalankan proses Sensus khusus Saham Gorengan (Ninja).
    Menghapus watchlist ninja lama, dan memasukkan saham-saham liar yang sedang meledak volumenya.
    """
    curated_tickers = run_sensus_ninja()
    
    if not curated_tickers:
        return {"message": "Tidak ada saham gorengan yang sedang meledak hari ini.", "count": 0}
        
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Hapus watchlist lama (Khusus Mode Ninja)
            cursor.execute("DELETE FROM watchlists WHERE mode='scalp'")
            
            # Masukkan kandidat baru
            for ticker in curated_tickers:
                ticker_jk = ticker if ticker.endswith(".JK") else f"{ticker}.JK"
                cursor.execute("INSERT INTO watchlists (ticker, mode) VALUES (%s, %s)", (ticker_jk, 'scalp'))
            
            conn.commit()
            
        return {"message": f"Sensus Ninja Selesai! {len(curated_tickers)} saham gorengan liar masuk radar.", "count": len(curated_tickers)}
    finally:
        conn.close()

@router.post("/api/sensus/kavaleri")
def trigger_sensus_kavaleri(api_key: str = Depends(verify_api_key)):
    """Menjalankan kurasi khusus untuk Mode Kavaleri (Fast Swing)"""
    curated_tickers = run_sensus_kavaleri()
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Hapus watchlist lama mode kavaleri
            cursor.execute("DELETE FROM watchlists WHERE mode='kavaleri'")
            
            # Masukkan kandidat baru
            for ticker in curated_tickers:
                ticker_jk = ticker if ticker.endswith(".JK") else f"{ticker}.JK"
                cursor.execute("INSERT INTO watchlists (ticker, mode) VALUES (%s, %s)", (ticker_jk, "kavaleri"))
            conn.commit()
            
        return {"message": f"Sensus Kavaleri Selesai! {len(curated_tickers)} saham likuid siap dipantau.", "count": len(curated_tickers)}
    finally:
        conn.close()

@router.get("/api/news/ipo")
def get_ipo_radar():
    """
    Mengambil headline berita IPO terbaru.
    """
    ipo_news = get_ipo_news()
    return {"data": ipo_news}

@router.get("/api/candidates/{mode}")
def get_candidates(mode: str):
    category_map = {"swing": "SWING", "kavaleri": "KAVALERI", "ninja": "NINJA"}
    category = category_map.get(mode.lower(), "SWING")
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            order_by = "avg_value DESC" if category != "NINJA" else "volatility DESC"
            cursor.execute(f"SELECT ticker, avg_value FROM idx_universe WHERE category=%s ORDER BY {order_by} LIMIT 50", (category,))
            rows = cursor.fetchall()
            
            results = []
            for row in rows:
                results.append({
                    "ticker": row['ticker'].replace('.JK', ''),
                    "price": 0,
                    "liquidity": float(row['avg_value']),
                    "signal": False,
                    "status": "KANDIDAT MENTAH",
                    "reason": "Menunggu Pemindaian VIP"
                })
            return {"data": results}
    finally:
        conn.close()

@router.get("/api/scan/swing")
def scan_swing(premium: bool = True, x_goapi_key: str = Header(None)):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT ticker FROM idx_universe WHERE category='SWING' ORDER BY avg_value DESC LIMIT 50")
            swing_universe = [row['ticker'] for row in cursor.fetchall()]
    finally:
        conn.close()
        
    if not swing_universe:
        return {"data": []}

    daily_data = download_daily_data(swing_universe, period="1y", use_premium=premium, goapi_key=x_goapi_key)
    results = []
    
    for ticker, df in daily_data.items():
        if df.empty:
            continue
            
        avg_volume = df['Volume'].tail(20).mean()
        last_close = df['Close'].iloc[-1]
        avg_value = avg_volume * last_close
        
        item = {
            "ticker": ticker.replace(".JK", ""),
            "price": float(last_close),
            "liquidity": float(avg_value),
            "signal": False,
            "status": "Aman",
            "reason": ""
        }
        
        if avg_value < MIN_DAILY_VOLUME:
            item["status"] = "Ditolak"
            item["reason"] = f"Likuiditas Rendah"
            results.append(item)
            continue
            
        analysis = analyze_swing_fortress(df)
        item["signal"] = analysis.get("signal", False)
        item["cmf"] = analysis.get("cmf", 0)
        item["tp"] = analysis.get("tp")
        item["sl"] = analysis.get("sl")
        item["rr"] = analysis.get("rr")
        
        if item["signal"]:
            item["status"] = "KANDIDAT"
            rr_text = f" | R:R {item['rr']}x" if item['rr'] else ""
            item["reason"] = f"Uptrend + ZLSMA + CMF:{item['cmf']}{rr_text}"
            
            # Ambil sentimen berita untuk kandidat saja (hemat waktu)
            news = get_news_sentiment(ticker)
            item["sentiment"] = news.get("sentiment", "NETRAL")
            item["news_count"] = news.get("news_count", 0)
            
            # Jika sentimen sangat negatif, ubah status jadi HATI-HATI
            if "NEGATIF" in item["sentiment"]:
                item["status"] = "HATI-HATI"
            
            # Kirim notifikasi Telegram
            notify_signal(item, mode="swing")
            
            # Auto beli di Portofolio Robot
            if item.get("tp") and item.get("sl"):
                record_paper_trade(item["ticker"], item["price"], item["tp"], item["sl"])
        else:
            item["reason"] = "Belum memenuhi semua syarat masuk"
            item["sentiment"] = "NETRAL"
            
        results.append(item)
        
    return {"data": results}

@router.get("/api/scan/kavaleri")
def scan_kavaleri(premium: bool = True, x_goapi_key: str = Header(None)):
    """Memindai saham mode Kavaleri (Fast Swing 1-7 Hari) dengan TTM Squeeze & SMC"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT ticker FROM idx_universe WHERE category='KAVALERI' ORDER BY avg_value DESC LIMIT 50")
            tickers = [row["ticker"] for row in cursor.fetchall()]
    finally:
        conn.close()
    
    if not tickers:
        return {"data": [], "message": "Jalankan Sensus Kavaleri terlebih dahulu!"}
        
    yfinance_tickers = [t if t.endswith(".JK") else f"{t}.JK" for t in tickers]
    data_dict = download_daily_data(yfinance_tickers, period="6mo", use_premium=premium, goapi_key=x_goapi_key)
    
    results = []
    for t_raw, df in data_dict.items():
        if df.empty: continue
        t_clean = t_raw.replace(".JK", "")
        
        analysis = analyze_kavaleri_special(df)
        # Jika sinyal menyala, kirim notifikasi
        item = {
            "ticker": t_clean,
            "price": analysis.get("close", 0),
            "signal": analysis.get("signal", False),
            "status": "Aman",
            "reason": "",
            "tp": analysis.get("tp"),
            "sl": analysis.get("sl"),
            "rr": analysis.get("rr"),
            "squeeze_fired": analysis.get("squeeze_fired", False),
            "smc_trap": analysis.get("smc_trap", False)
        }
        
        if item["signal"]:
            item["status"] = "KANDIDAT KAVALERI"
            reasons = []
            if item["squeeze_fired"]: reasons.append("SQUEEZE FIRED")
            if item["smc_trap"]: reasons.append("SMC TRAP")
            item["reason"] = " + ".join(reasons) if reasons else "Momentum + Bandar Masuk"
            
            pesan = f"🐎 KAVALERI TRIGGER: {t_clean}\\nHarga: {item['price']}\\n"
            if item['squeeze_fired']:
                pesan += "💥 TTM SQUEEZE FIRED! (Energi Meledak)\\n"
            if item['smc_trap']:
                pesan += "🏦 SMC LIQUIDITY TRAP! (Bandar Makan Ritel)\\n"
            pesan += f"TP: {item['tp']} | SL: {item['sl']}"
            notify_signal(item, mode="kavaleri") # mock item to pass dict
            
            # Auto beli di Portofolio Robot
            if item.get("tp") and item.get("sl"):
                record_paper_trade(item["ticker"], item["price"], item["tp"], item["sl"])
        else:
            item["reason"] = "Menunggu Squeeze / Trap"
            item["status"] = "Pantau"
            
        results.append(item)
        
    return {"data": results}

@router.get("/api/scan/ninja")
def scan_ninja(premium: bool = True, x_goapi_key: str = Header(None)):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT ticker FROM idx_universe WHERE category='NINJA' ORDER BY volatility DESC LIMIT 50")
            scalp_universe = [row['ticker'] for row in cursor.fetchall()]
    finally:
        conn.close()
        
    if not scalp_universe:
        return {"data": []}

    intraday_data = download_intraday_data(scalp_universe, interval="5m", period="5d", use_premium=premium, goapi_key=x_goapi_key)
    results = []
    
    for ticker, df in intraday_data.items():
        if df.empty:
            continue
            
        last_close = df['Close'].iloc[-1]
        
        item = {
            "ticker": ticker.replace(".JK", ""),
            "price": float(last_close),
            "signal": False,
            "status": "Sepi",
            "reason": ""
        }
        
        analysis = analyze_ninja_scalper(df)
        item["signal"] = analysis.get("signal", False)
        item["tp"] = analysis.get("tp")
        item["sl"] = analysis.get("sl")
        
        if item["signal"]:
            item["status"] = "HAKA"
            item["reason"] = f"Vol Spikes! Naik {analysis.get('spread_pct', 0):.2f}% | CMF:{analysis.get('cmf', 0)}"
            notify_signal(item, mode="ninja")
            
            # Auto beli di Portofolio Robot
            if item.get("tp") and item.get("sl"):
                record_paper_trade(item["ticker"], item["price"], item["tp"], item["sl"])
        elif analysis.get("volume_spike"):
            item["status"] = "Waspada"
            item["reason"] = "Volume besar tapi harga stagnan"
        else:
            item["reason"] = "Tidak ada lonjakan volume"
            
        results.append(item)
        
    return {"data": results}

@router.get("/api/scan/whale")
def scan_whale():
    """Memindai akumulasi Paus (Foreign Broker / Massive Net Buy) pada Watchlist."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Ambil semua ticker dari watchlists (swing & kavaleri)
            cursor.execute("SELECT DISTINCT ticker FROM watchlists WHERE mode IN ('swing', 'kavaleri')")
            tickers = [row['ticker'].replace(".JK", "") for row in cursor.fetchall()]
    finally:
        conn.close()
        
    if not tickers:
        return {"data": [], "message": "Jalankan Sensus terlebih dahulu!"}
        
    # Batasi sementara maks 50 saham agar API tidak kena limit
    tickers = tickers[:50]
    results = scan_whale_accumulation(tickers)
    
    # Notifikasi
    for item in results:
        if item.get("signal"):
            pesan = f"🐋 PAUS TERDETEKSI: {item['ticker']}\\nHarga: Rp {item['price']}\\nTop Buyer: {item['top_buyer']}\\nNet Vol: {item['net_volume']} Lot\\nAvg Bandar: Rp {item['avg_price']}"
            if item.get("is_golden"):
                pesan += "\\n🌟 GOLDEN ENTRY (Harga < Modal Bandar)"
            elif item.get("is_danger"):
                pesan += "\\n🚨 RAWAN GUYUR (Sudah Naik Tinggi)"
            # Send specific telegram message
            send_telegram_message(pesan)
            
    return {"data": results}

@router.get("/api/macro")
def get_macro():
    """Endpoint untuk mengambil data Makro Ekonomi real-time."""
    data = get_macro_data()
    # Kirim peringatan Telegram jika kondisi buruk
    notify_macro_warning(data)
    return data

@router.get("/api/astro/forecast")
def get_astro_forecast():
    """Mengambil ramalan bintang (Astro Forecast) hari ini."""
    try:
        data = get_current_astro_forecast()
        return {"data": data}
    except Exception as e:
        return {"data": [], "error": str(e)}

@router.get("/api/composite")
def get_composite_signals(premium: bool = True):
    """Mengumpulkan semua sinyal aktif dari seluruh mode secara paralel."""
    results = []
    
    def fetch_swing():
        res = scan_all_swing(premium=premium)
        return [dict(item, source="Benteng") for item in res["data"] if item.get("signal")]
        
    def fetch_kavaleri():
        res = scan_kavaleri(premium=premium)
        return [dict(item, source="Kavaleri") for item in res["data"] if item.get("signal")]
        
    def fetch_ninja():
        res = scan_all_ninja(premium=premium)
        return [dict(item, source="Ninja") for item in res["data"] if item.get("signal")]
        
    def fetch_global():
        res = scan_global()
        return [dict(item, source="Global Astro") for item in res["data"] if item.get("signal")]
        
    def fetch_whale():
        res = scan_whale()
        return [dict(item, source="Paus") for item in res["data"] if item.get("signal")]

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_mode = {
            executor.submit(fetch_swing): "swing",
            executor.submit(fetch_kavaleri): "kavaleri",
            executor.submit(fetch_ninja): "ninja",
            executor.submit(fetch_global): "global",
            executor.submit(fetch_whale): "whale"
        }
        for future in concurrent.futures.as_completed(future_to_mode):
            try:
                data = future.result()
                results.extend(data)
            except Exception as e:
                print(f"Error fetching composite data: {e}")
                
    return {"data": results}

@router.get("/api/scan/global")
def scan_global():
    """Memindai aset Global (Gold & Forex Utama) menggunakan Astro Engine & Teknikal."""
    # Daftar aset global utama: Emas, EURUSD, GBPUSD, JPYUSD, Index S&P500
    global_tickers = ["GC=F", "EURUSD=X", "GBPUSD=X", "JPY=X", "^GSPC"]
    data_dict = download_global_data(global_tickers, period="3mo")
    
    results = []
    for ticker, df in data_dict.items():
        if df.empty: continue
        
        last_close = df['Close'].iloc[-1]
        analysis = analyze_swing_fortress(df) # Gunakan swing analysis untuk melihat trend besar
        
        item = {
            "ticker": ticker,
            "price": float(last_close),
            "signal": analysis.get("signal", False),
            "status": "Astro Mode",
            "tp": analysis.get("tp"),
            "sl": analysis.get("sl"),
            "sentiment": "GLOBAL"
        }
        
        # Sederhanakan nama untuk UI
        name_map = {
            "GC=F": "GOLD (Emas)",
            "EURUSD=X": "EUR/USD",
            "GBPUSD=X": "GBP/USD",
            "JPY=X": "USD/JPY",
            "^GSPC": "S&P 500"
        }
        item["name"] = name_map.get(ticker, ticker)
        results.append(item)
        
    return {"data": results}

@router.get("/api/chart/{ticker}")
def get_chart_data(ticker: str, is_global: bool = False):
    """Mengambil data OHLC historis untuk TradingView Chart dan Astro Markers"""
    # Menggunakan daily data selama 6 bulan
    try:
        if is_global:
            query_ticker = ticker
            df_dict = download_global_data([query_ticker], period="6mo")
            df_ticker = df_dict.get(query_ticker)
        else:
            query_ticker = f"{ticker}.JK"
            df_dict = download_daily_data([query_ticker], period="6mo")
            df_ticker = df_dict.get(query_ticker)
            
        if df_ticker is None or df_ticker.empty:
            return {"data": [], "markers": []}
            
        chart_data = []
        for index, row in df_ticker.iterrows():
            date_str = index.strftime("%Y-%m-%d")
            chart_data.append({
                "time": date_str,
                "open": float(row["Open"]),
                "high": float(row["High"]),
                "low": float(row["Low"]),
                "close": float(row["Close"]),
                "value": float(row["Volume"]) if "Volume" in row else 0
            })
            
        # Astro Engine Markers
        start_date = chart_data[0]["time"]
        end_date = chart_data[-1]["time"]
        markers = get_astro_cycles(start_date, end_date)
            
        return {"data": chart_data, "markers": markers}
    except Exception as e:
        return {"data": [], "markers": [], "error": str(e)}

@router.get("/api/xray/{ticker}")
def xray_ticker(ticker: str):
    """Melakukan deep scan pada satu saham"""
    from xray_engine import run_xray_scan
    try:
        res = run_xray_scan(ticker)
        return {"data": res}
    except Exception as e:
        return {"error": str(e)}

@router.get("/api/portfolio")
def get_portfolio():
    """Mengambil riwayat Paper Trading"""
    data = get_paper_portfolio()
    return {"data": data}

@router.post("/api/universe/build")
def build_idx_universe():
    """Endpoint untuk menjalankan sensus seluruh saham IDX"""
    result = build_universe()
    return result

swing_cache = TTLCache(maxsize=100, ttl=60)

@router.get("/api/scan/all-swing")
def scan_all_swing(premium: bool = True):
    """Scan menggunakan kategori SWING dari Universe"""
    swing_universe = get_universe_by_category("SWING")
    if not swing_universe:
        return {"data": [], "message": "Universe kosong. Jalankan Sensus Saham dulu."}
    
    swing_universe = swing_universe[:100] 
    
    macro_data = get_macro_data()
    coal_trend = macro_data.get("coal", {}).get("trend", "STABIL")
    gold_trend = macro_data.get("gold", {}).get("trend", "STABIL")
    
    COAL_STOCKS = ["ADRO", "PTBA", "ITMG", "BUMI", "HRUM", "INDY", "DOID", "BSSR"]
    GOLD_STOCKS = ["MDKA", "PSAB", "BRMS", "AMMN", "ARCI", "SQMI"]
    
    daily_data = download_daily_data(swing_universe, period="1y", use_premium=premium)
    results = []
    
    for ticker, df in daily_data.items():
        if df.empty: continue
            
        ticker_clean = ticker.replace(".JK", "")
            
        avg_volume = df['Volume'].tail(20).mean()
        last_close = df['Close'].iloc[-1]
        avg_value = avg_volume * last_close
        
        item = {
            "ticker": ticker.replace(".JK", ""),
            "price": float(last_close),
            "liquidity": float(avg_value),
            "signal": False,
            "status": "Aman",
            "reason": ""
        }
        
        analysis = analyze_swing_fortress(df)
        item["signal"] = analysis.get("signal", False)
        item["cmf"] = analysis.get("cmf", 0)
        item["tp"] = analysis.get("tp")
        item["sl"] = analysis.get("sl")
        item["rr"] = analysis.get("rr")
        
        if item["signal"]:
            # Intermarket Analysis (Sector Rotation)
            if ticker_clean in COAL_STOCKS and coal_trend == "TURUN":
                item["signal"] = False
                item["status"] = "DIBATALKAN MAKRO"
                item["reason"] = "Sektor Batu Bara sedang Downtrend Global"
            elif ticker_clean in GOLD_STOCKS and gold_trend == "NAIK":
                item["status"] = "HAKA SUPER"
                rr_text = f" | R:R {item['rr']}x" if item['rr'] else ""
                item["reason"] = f"Gold Uptrend Global! + ZLSMA + CMF:{item['cmf']}{rr_text}"
            else:
                item["status"] = "KANDIDAT"
                rr_text = f" | R:R {item['rr']}x" if item['rr'] else ""
                item["reason"] = f"Uptrend + ZLSMA + CMF:{item['cmf']}{rr_text}"
            
            if item["signal"]: # Jika tidak dibatalkan makro
                news = get_news_sentiment(ticker)
                item["sentiment"] = news.get("sentiment", "NETRAL")
                item["news_count"] = news.get("news_count", 0)
                if "NEGATIF" in item["sentiment"]:
                    item["status"] = "HATI-HATI"
                    
                notify_signal(item, mode="swing")
                
                # Record Paper Trade
                if item["tp"] and item["sl"]:
                    record_paper_trade(ticker_clean, item["price"], item["tp"], item["sl"])
        else:
            item["reason"] = "Belum memenuhi semua syarat masuk"
            item["sentiment"] = "NETRAL"
            
        results.append(item)
        
    return {"data": results}


ninja_cache = TTLCache(maxsize=100, ttl=60)

@router.get("/api/scan/all-ninja")
def scan_all_ninja(premium: bool = True):
    """Scan menggunakan kategori NINJA dari Universe"""
    ninja_universe = get_universe_by_category("NINJA")
    if not ninja_universe:
        return {"data": [], "message": "Universe kosong. Jalankan Sensus Saham dulu."}
        
    ninja_universe = ninja_universe[:100]
    
    macro_data = get_macro_data()
    coal_trend = macro_data.get("coal", {}).get("trend", "STABIL")
    gold_trend = macro_data.get("gold", {}).get("trend", "STABIL")
    
    COAL_STOCKS = ["ADRO", "PTBA", "ITMG", "BUMI", "HRUM", "INDY", "DOID", "BSSR"]
    GOLD_STOCKS = ["MDKA", "PSAB", "BRMS", "AMMN", "ARCI", "SQMI"]
    
    intraday_data = download_intraday_data(ninja_universe, period="1mo", interval="5m", use_premium=premium)
    results = []
    
    for ticker, df in intraday_data.items():
        if df.empty: continue
            
        ticker_clean = ticker.replace(".JK", "")
            
        item = {
            "ticker": ticker.replace(".JK", ""),
            "price": float(df['Close'].iloc[-1]),
            "signal": False,
            "status": "Aman",
            "reason": ""
        }
        
        analysis = analyze_ninja_scalper(df)
        item["signal"] = analysis.get("signal", False)
        item["tp"] = analysis.get("tp")
        item["sl"] = analysis.get("sl")
        
        if item["signal"]:
            # MTC (Multi-Timeframe Confluence)
            daily_df = download_daily_data([ticker], period="3mo")
            if ticker in daily_df and not daily_df[ticker].empty:
                d_df = daily_df[ticker]
                last_d_close = d_df['Close'].iloc[-1]
                ema50 = ta.trend.ema_indicator(d_df['Close'], window=50).iloc[-1]
                
                if last_d_close < ema50:
                    item["signal"] = False
                    item["status"] = "DIBATALKAN MTC"
                    item["reason"] = "Tren Harian Hancur (Di bawah EMA50)"
            
            # Intermarket Analysis
            if item["signal"]:
                if ticker_clean in COAL_STOCKS and coal_trend == "TURUN":
                    item["signal"] = False
                    item["status"] = "DIBATALKAN MAKRO"
                    item["reason"] = "Sektor Batu Bara sedang Downtrend Global"
                elif ticker_clean in GOLD_STOCKS and gold_trend == "NAIK":
                    item["status"] = "HAKA SUPER"
                    item["reason"] = f"Gold Rally! Vol Spikes! Naik {analysis.get('spread_pct', 0):.2f}% | CMF:{analysis.get('cmf', 0)}"
                else:
                    item["status"] = "HAKA"
                    item["reason"] = f"Vol Spikes! Naik {analysis.get('spread_pct', 0):.2f}% | CMF:{analysis.get('cmf', 0)}"
            
            if item["signal"]:
                notify_signal(item, mode="ninja")
                
                # Record Paper Trade
                if item["tp"] and item["sl"]:
                    record_paper_trade(ticker_clean, item["price"], item["tp"], item["sl"])
        elif analysis.get("volume_spike"):
            item["status"] = "Waspada"
            item["reason"] = "Volume besar tapi harga stagnan"
        else:
            item["reason"] = "Tidak ada lonjakan volume"
            
        results.append(item)
        
    return {"data": results}


@router.get("/api/init-db")
def init_db_endpoint():
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # Tabel idx_universe
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS idx_universe (
                    ticker VARCHAR(20) PRIMARY KEY,
                    category VARCHAR(20),
                    avg_value DOUBLE,
                    volatility DOUBLE,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """)
            
            # Tabel watchlists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS watchlists (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    ticker VARCHAR(20) NOT NULL UNIQUE,
                    mode VARCHAR(20) NOT NULL
                )
            """)
            
            # Tabel paper_trades
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS paper_trades (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    ticker VARCHAR(20),
                    mode VARCHAR(20),
                    entry_price DOUBLE,
                    tp DOUBLE,
                    sl DOUBLE,
                    status VARCHAR(20) DEFAULT 'OPEN',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    closed_at TIMESTAMP NULL,
                    pnl_pct DOUBLE NULL
                )
            """)
            
            # Seed awal watchlists jika kosong
            cursor.execute("SELECT COUNT(*) FROM watchlists")
            if cursor.fetchone()['COUNT(*)'] == 0:
                initial_data = [
                    ("BBCA.JK", "swing"), ("BBRI.JK", "swing"), ("BMRI.JK", "swing"), ("BBNI.JK", "swing"),
                    ("TLKM.JK", "swing"), ("ASII.JK", "swing"), ("UNVR.JK", "swing"), ("ICBP.JK", "swing"),
                    ("CUAN.JK", "ninja"), ("PANI.JK", "ninja"), ("BREN.JK", "ninja"), ("GOTO.JK", "ninja")
                ]
                cursor.executemany("INSERT INTO watchlists (ticker, mode) VALUES (%s, %s)", initial_data)
                
        conn.commit()
    except Exception as e:
        import traceback
        err_msg = traceback.format_exc()
        return {"status": "error", "message": str(e), "traceback": err_msg}
    finally:
        if conn:
            conn.close()
    
    return {"status": "success", "message": "Database tables created and seeded successfully!"}


@router.get("/api/debug-universe")
def debug_universe():
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as count FROM idx_universe")
            count = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM watchlists")
            wl_count = cursor.fetchone()['count']
            
            return {"universe_count": count, "watchlist_count": wl_count}
    except Exception as e:
        return {"error": str(e)}
    finally:
        if conn:
            conn.close()

@router.get("/api/emergency-seed")
def emergency_seed():
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # Masukkan 20 saham Ninja manual
            ninja_stocks = ["PANI.JK", "CUAN.JK", "BREN.JK", "GOTO.JK", "BRMS.JK", "BUMI.JK", "DOID.JK", "STRK.JK", "VKTR.JK", "WIFI.JK", "RAAM.JK", "CGAS.JK", "AMMN.JK", "PGEO.JK", "TPIA.JK", "KPIG.JK", "AWAN.JK", "DATA.JK"]
            
            # Masukkan 20 saham Swing manual
            swing_stocks = ["BBCA.JK", "BBRI.JK", "BMRI.JK", "BBNI.JK", "TLKM.JK", "ASII.JK", "UNVR.JK", "ICBP.JK", "BRPT.JK", "INDF.JK", "ADRO.JK", "ITMG.JK", "PTBA.JK", "UNTR.JK"]
            
            results = []
            for t in ninja_stocks:
                results.append((t, "NINJA", 5000000000.0, 0.05))
            for t in swing_stocks:
                results.append((t, "SWING", 50000000000.0, 0.02))
                
            cursor.execute("TRUNCATE TABLE idx_universe")
            sql = "INSERT INTO idx_universe (ticker, category, avg_value, volatility) VALUES (%s, %s, %s, %s)"
            cursor.executemany(sql, results)
        conn.commit()
        return {"status": "success", "message": f"{len(results)} saham disuntikkan secara manual."}
    except Exception as e:
        return {"error": str(e)}
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
