from app.services.engines.data_engine import download_daily_data, download_intraday_data
from app.services.engines.technical_engine import analyze_swing_fortress, analyze_ninja_scalper
from app.services.engines.news_engine import get_news_sentiment
from app.services.engines.macro_engine import get_macro_data
from app.services.engines.goapi_engine import get_goapi_price, get_broker_summary

def generate_mentor_advice(ticker, daily_res, intraday_res, news_res, macro_res, broker_res):
    """
    Menghasilkan kesimpulan bergaya mentor formal berdasarkan kompilasi data.
    """
    from app.services.engines.llm_engine import generate_xray_analysis
    
    # Bungkus semua data ke dalam dictionary untuk dikirim ke LLM
    stock_data = {
        "ticker": ticker,
        "price": daily_res.get("last_close", intraday_res.get("last_close", 0)),
        "daily": daily_res,
        "intraday": intraday_res,
        "news": news_res,
        "macro": macro_res,
        "broker": broker_res
    }
    
    # Panggil Omni-API Gateway untuk meminta AI merangkai kata-kata
    return generate_xray_analysis(stock_data)

def run_xray_scan(ticker: str):
    """
    Melakukan Deep Scan pada satu saham secara spesifik.
    """
    ticker_clean = ticker.upper().replace(".JK", "")
    ticker_jk = f"{ticker_clean}.JK"
    
    # 1. Ambil Makro
    macro_res = get_macro_data()
    
    # 2. Ambil Berita
    news_res = get_news_sentiment(ticker_clean)
    
    # 3. Analisis Daily
    daily_data = download_daily_data([ticker_jk], period="1y")
    daily_res = {"signal": False, "cmf": 0, "tp": None, "sl": None}
    df_d = daily_data.get(ticker_jk)
    
    if df_d is not None and not df_d.empty:
        daily_res = analyze_swing_fortress(df_d)
        import ta
        daily_res["last_close"] = df_d['Close'].iloc[-1]
        daily_res["ema50"] = ta.trend.ema_indicator(df_d['Close'], window=50).iloc[-1]

    # 4. Analisis Intraday
    intraday_data = download_intraday_data([ticker_jk], period="5d", interval="5m")
    intraday_res = {"signal": False, "volume_spike": False, "tp": None, "sl": None}
    df_i = intraday_data.get(ticker_jk)
    
    if df_i is not None and not df_i.empty:
        intraday_res = analyze_ninja_scalper(df_i)

    # 5. Ambil Harga & Broker Summary dari GoAPI
    goapi_data = get_goapi_price(ticker_clean)
    broker_res = get_broker_summary(ticker_clean)

    # Gunakan harga GoAPI jika ada, kalau tidak fallback ke yfinance
    last_price = goapi_data["price"] if goapi_data else daily_res.get("last_close", df_i['Close'].iloc[-1] if df_i is not None and not df_i.empty else 0)

    # 6. Kalkulasi Jejak Kaki Bandar (Ide 3)
    if broker_res.get("avg_price", 0) > 0:
        broker_res["jejak_kaki"] = {
            "is_golden": last_price <= broker_res["avg_price"] and broker_res["status"] == "AKUMULASI",
            "is_danger": last_price > broker_res["avg_price"] * 1.05 and broker_res["status"] == "DISTRIBUSI",
            "diff_pct": round(((last_price - broker_res["avg_price"]) / broker_res["avg_price"]) * 100, 2)
        }
    else:
        broker_res["jejak_kaki"] = None

    # 7. Buat Laporan Mentor
    mentor_text = generate_mentor_advice(ticker_clean, daily_res, intraday_res, news_res, macro_res, broker_res)

    from app.services.advanced.utils import sanitize_for_json
    
    return sanitize_for_json({
        "ticker": ticker_clean,
        "price": float(last_price),
        "daily": daily_res,
        "intraday": intraday_res,
        "news": news_res,
        "broker": broker_res,
        "mentor_advice": mentor_text
    })
