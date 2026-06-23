import yfinance as yf
import pandas as pd
from app.services.engines.goapi_engine import get_broker_summary
from app.services.engines.llm_engine import generate_xray_analysis
from app.services.engines.data_engine import download_daily_data
from app.core.database import get_db_connection
import google.generativeai as genai
from app.core.key_router import APIKeyRouter
import time
import math

def calculate_growth_score(info: dict) -> dict:
    """
    Menghitung skor fundamental berbasis akselerasi (Growth).
    Jika data kosong dari yfinance, berikan skor 0 dan minta cek RTI/Stockbit.
    """
    if not info:
        return {"score": 0, "factors": "Cek data manual di aplikasi RTI Business (fokus pada EPS Growth, ROE, Net Profit)."}
        
    revenue_growth = info.get('revenueGrowth', 0)
    earnings_growth = info.get('earningsGrowth', 0)
    roe = info.get('returnOnEquity', 0)
    
    score = 0
    factors = []
    
    # 1. Earnings Growth
    if earnings_growth is not None:
        if earnings_growth > 0.3:
            score += 40
            factors.append(f"Laba Meroket (+{int(earnings_growth*100)}%)")
        elif earnings_growth > 0.1:
            score += 20
            factors.append(f"Laba Tumbuh (+{int(earnings_growth*100)}%)")
        elif earnings_growth < 0:
            score -= 10
            factors.append(f"Laba Turun ({int(earnings_growth*100)}%)")
            
    # 2. Revenue Growth
    if revenue_growth is not None:
        if revenue_growth > 0.2:
            score += 30
            factors.append(f"Sales Meroket (+{int(revenue_growth*100)}%)")
        elif revenue_growth > 0.05:
            score += 15
            factors.append(f"Sales Naik (+{int(revenue_growth*100)}%)")
            
    # 3. ROE
    if roe is not None:
        if roe > 0.15:
            score += 30
            factors.append(f"Efisiensi Tinggi (ROE {int(roe*100)}%)")
        elif roe > 0.08:
            score += 15
            factors.append(f"Efisiensi Cukup (ROE {int(roe*100)}%)")
            
    # Cap at 100, min 0
    score = max(0, min(100, score))
    
    if score == 0 and len(factors) == 0:
        return {"score": 0, "factors": "Data fundamental YF tidak tersedia. Cek aplikasi Stockbit (Foreign Flow) atau RTI Business secara manual."}
        
    return {"score": score, "factors": ", ".join(factors)}

def calculate_confirmation_score(ticker: str, close_price: float) -> dict:
    """
    Menghitung konfirmasi bandar (Technical + Volume Flow).
    """
    broker_data = get_broker_summary(ticker)
    
    score = 0
    reasons = []
    
    # Simple check on Broker Data
    if broker_data.get('status') == 'AKUMULASI':
        score += 50
        reasons.append(f"Diakumulasi masif oleh {broker_data.get('top_buyer')}")
    else:
        score += 10
        reasons.append(f"Sedang didistribusi oleh {broker_data.get('top_seller')}")
        
    # We ideally want technical breakout here too, but for speed, we give base points
    score += 20 # Base for surviving screener
    
    return {"score": max(0, min(100, score)), "factors": ", ".join(reasons)}

def generate_institutional_narrative(ticker: str, growth_data: dict, conf_data: dict) -> dict:
    """
    Menggunakan Gemini untuk mencari Narrative (Sebab-Akibat).
    """
    prompt = f"""
    Anda adalah Jenderal Analis Hedge Fund Senior.
    Tugas Anda: Buatlah narasi logis MENGAPA institusi besar membeli saham {ticker}.
    
    Data Pertumbuhan Fundamental: {growth_data['factors']}
    Data Konfirmasi Bandar: {conf_data['factors']}
    
    Jika data Fundamental mengatakan "Cek Stockbit / RTI", masukkan saran tersebut ke dalam Analisis.
    
    Tugas:
    1. Catalyst Score (0-100): Tebak skor katalis berdasarkan narasi yang mungkin (misal jika laba meroket, skor tinggi).
    2. Alasan Institusi Membeli: 2 kalimat tajam (Kaitkan dengan makro/ekspansi/sentimen komoditas jika logis).
    3. Risiko Utama: 1 kalimat.
    4. Expected Return 15 Hari: (contoh: +5% sd +10%)
    5. Expected Return 3 Bulan: (contoh: +15% sd +30%)
    6. Rekomendasi: (Strong Buy, Buy, Watchlist, Avoid)
    
    Balas HANYA dengan format JSON ketat (tanpa markdown), kunci:
    "catalyst_score" (int), "alasan_institusi" (str), "risiko_utama" (str), "expected_return_15d" (str), "expected_return_3m" (str), "rekomendasi" (str)
    """
    
    router = APIKeyRouter('Gemini')
    while router.has_active_keys():
        current_key, _ = router.get_key()
        if not current_key: break
        
        try:
            genai.configure(api_key=current_key)
            model = genai.GenerativeModel('gemini-1.5-flash', generation_config={"response_mime_type": "application/json"})
            response = model.generate_content(prompt)
            import json
            data = json.loads(response.text)
            return data
        except Exception as e:
            if 'quota' in str(e).lower() or '429' in str(e).lower():
                router.mark_dead(current_key)
            else:
                return {}
    return {}
import json
import os

STATUS_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "institutional_status.json")

def set_institutional_status(status, progress, message):
    try:
        with open(STATUS_FILE, "w") as f:
            json.dump({
                "status": status,
                "progress": progress,
                "message": message
            }, f)
    except Exception as e:
        print("Failed to write institutional status:", e)

def run_institutional_scan():
    """
    Fungsi Utama. Memindai daftar saham unggulan, lalu menyimpan hasilnya ke database.
    """
    print("Mulai Pemindaian Institutional Narrative Engine...")
    set_institutional_status("starting", 0, "Mempersiapkan Radar Institusi...")
    
    # Ambil 10 saham kapitalisasi besar sebagai proxy (agar tidak hit limit API)
    # Di masa depan, ini bisa disambung ke hasil Sensus Master
    target_tickers = ["BBCA", "BMRI", "BBNI", "BBRI", "TLKM", "ASII", "AMMN", "BRPT", "GOTO", "BREN"]
    
    results = []
    total = len(target_tickers)
    
    for i, ticker in enumerate(target_tickers):
        progress = int((i / total) * 100)
        set_institutional_status("running", progress, f"Menganalisis Fundamental & Narasi: {ticker}...")
        print(f"Menganalisis {ticker}...")
        try:
            ticker_jk = f"{ticker}.JK"
            yf_ticker = yf.Ticker(ticker_jk)
            info = yf_ticker.info
            
            # 1. Growth Score
            growth = calculate_growth_score(info)
            
            # 2. Confirmation Score
            conf = calculate_confirmation_score(ticker, info.get("currentPrice", 0))
            
            # 3. LLM Narrative Score
            narrative = generate_institutional_narrative(ticker, growth, conf)
            
            if not narrative:
                # Fallback if LLM fails
                narrative = {
                    "catalyst_score": 50,
                    "alasan_institusi": "Data sentimen tidak tersedia. Silakan cek berita terkini di aplikasi pihak ketiga.",
                    "risiko_utama": "Volatilitas pasar reguler.",
                    "expected_return_15d": "N/A",
                    "expected_return_3m": "N/A",
                    "rekomendasi": "Watchlist"
                }
                
            cat_score = narrative.get("catalyst_score", 50)
            grw_score = growth["score"]
            cnf_score = conf["score"]
            
            # Composite (40% Cat, 30% Growth, 30% Conf)
            comp_score = int(0.4 * cat_score + 0.3 * grw_score + 0.3 * cnf_score)
            
            results.append({
                "ticker": ticker,
                "catalyst_score": cat_score,
                "growth_score": grw_score,
                "confirmation_score": cnf_score,
                "composite_score": comp_score,
                "alasan_institusi": narrative.get("alasan_institusi", "-"),
                "faktor_pertumbuhan": growth["factors"],
                "risiko_utama": narrative.get("risiko_utama", "-"),
                "expected_return_15d": narrative.get("expected_return_15d", "-"),
                "expected_return_3m": narrative.get("expected_return_3m", "-"),
                "confidence_score": min(100, int(comp_score * 1.1)),  # Bonus confidence
                "rekomendasi": narrative.get("rekomendasi", "Watchlist")
            })
            
            # Anti-rate-limit sleep
            time.sleep(2)
            
        except Exception as e:
            print(f"Gagal memproses {ticker}: {e}")
            continue
            
    # Save to Database
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Hapus data lama
            cursor.execute("TRUNCATE TABLE institutional_candidates")
            
            sql = """INSERT INTO institutional_candidates 
                     (ticker, catalyst_score, growth_score, confirmation_score, composite_score, 
                      alasan_institusi, faktor_pertumbuhan, risiko_utama, expected_return_15d, 
                      expected_return_3m, confidence_score, rekomendasi)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                     
            for r in results:
                cursor.execute(sql, (
                    r["ticker"], r["catalyst_score"], r["growth_score"], r["confirmation_score"], 
                    r["composite_score"], r["alasan_institusi"], r["faktor_pertumbuhan"], 
                    r["risiko_utama"], r["expected_return_15d"], r["expected_return_3m"], 
                    r["confidence_score"], r["rekomendasi"]
                ))
            conn.commit()
            print("Penyimpanan selesai!")
            set_institutional_status("done", 100, f"Selesai! {len(results)} kandidat masuk radar.")
    except Exception as e:
        print("Database error saat menyimpan kandidat:", e)
        set_institutional_status("error", 0, f"Gagal menyimpan data: {e}")
    finally:
        conn.close()
