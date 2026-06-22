from app.services.engines.data_engine import download_daily_data, download_intraday_data
from app.services.engines.technical_engine import analyze_swing_fortress, analyze_ninja_scalper
from app.services.engines.news_engine import get_news_sentiment
from app.services.engines.macro_engine import get_macro_data
from app.services.engines.goapi_engine import get_goapi_price, get_broker_summary

def generate_mentor_advice(ticker, daily_res, intraday_res, news_res, macro_res, broker_res):
    """
    Menghasilkan kesimpulan bergaya mentor formal berdasarkan kompilasi data.
    """
    ticker_clean = ticker.replace(".JK", "")
    advice = []
    
    # 1. Analisis Tren Harian (Swing)
    if daily_res.get("signal"):
        advice.append(f"Secara fundamental teknikal harian, {ticker_clean} berada dalam fase Uptrend yang solid, didukung oleh akumulasi institusional (ZLSMA) dengan Arus Uang (CMF) positif sebesar {daily_res.get('cmf', 0)}.")
    else:
        advice.append(f"Berdasarkan kerangka waktu harian, {ticker_clean} belum menunjukkan sinyal Uptrend yang valid atau masih berada di bawah tekanan distribusi.")

    # 2. Analisis Intraday (Ninja/Scalping)
    if intraday_res.get("signal"):
        advice.append(f"Pada kerangka waktu jangka pendek (5-menit), terdapat anomali lonjakan volume yang mengindikasikan adanya akumulasi agresif (Smart Money).")
    elif intraday_res.get("volume_spike"):
        advice.append(f"Secara jangka pendek, terlihat ada volume transaksi besar namun harga cenderung tertahan (distribusi tersembunyi).")
    else:
        advice.append(f"Secara jangka pendek, volume perdagangan relatif sepi tanpa adanya partisipasi pelaku pasar dominan.")

    # 3. Sentimen Berita
    sentiment = news_res.get("sentiment", "NETRAL")
    if "POSITIF" in sentiment:
        advice.append(f"Sentimen pemberitaan saat ini sangat mendukung pergerakan harga ke atas.")
    elif "NEGATIF" in sentiment:
        advice.append(f"Terdapat sentimen negatif pada pemberitaan yang berpotensi menjadi katalis penurunan.")

    # 4. Makro Ekonomi
    coal_stocks = ["ADRO", "PTBA", "ITMG", "BUMI", "HRUM", "INDY", "DOID", "BSSR"]
    gold_stocks = ["MDKA", "PSAB", "BRMS", "AMMN", "ARCI", "SQMI"]
    
    macro_note = ""
    coal_trend = macro_res.get("coal", {}).get("trend", "STABIL")
    gold_trend = macro_res.get("gold", {}).get("trend", "STABIL")
    
    if ticker_clean in coal_stocks and coal_trend == "TURUN":
        macro_note = "Peringatan Makro: Harga acuan batu bara global sedang dalam fase penurunan. Risiko sistemik cukup tinggi."
    elif ticker_clean in gold_stocks and gold_trend == "NAIK":
        macro_note = "Katalis Makro: Kenaikan harga emas global memberikan dorongan positif yang sangat kuat bagi emiten ini."

    if macro_note:
        advice.append(macro_note)

    # 5. Kesimpulan Bandarmologi & Rekomendasi
    advice.append("\n**Kesimpulan & Rekomendasi:**")
    
    broker_info = f"Terdeteksi Bandar menggunakan broker {broker_res['top_buyer']} sedang melakukan {broker_res['status']} melawan ritel {broker_res['top_seller']}. "
    
    if broker_res.get('jejak_kaki') and broker_res['jejak_kaki']['is_golden']:
        advice.append(f"**GOLDEN ENTRY:** Harga saat ini lebih rendah/sama dengan harga modal bandar! Ini adalah kesempatan emas untuk masuk dengan risiko minim.")
    elif broker_res.get('jejak_kaki') and broker_res['jejak_kaki']['is_danger']:
        advice.append(f"**RAWAN GUYURAN:** Harga sudah naik terlalu tinggi dari modal bandar dan bandar sedang distribusi. Sangat berisiko!")

    if daily_res.get("signal") and intraday_res.get("signal") and broker_res['status'] == "AKUMULASI":
        advice.append(broker_info + "Sangat Direkomendasikan. Emiten ini layak untuk eksekusi beli (Buy) dengan strategi Swing maupun Scalping, mengingat konfirmasi positif di berbagai kerangka waktu dan didukung bandar.")
    elif broker_res['status'] == "AKUMULASI":
        advice.append(broker_info + "Layak Dipertimbangkan. Meski teknikal belum sempurna, dukungan akumulasi bandar (Big Money) menjadi katalis yang kuat.")
    elif daily_res.get("signal"):
        advice.append("Layak Dipertimbangkan untuk Swing Trading, namun berhati-hati karena Bandar belum sepenuhnya akumulasi.")
    elif intraday_res.get("signal"):
        if daily_res.get("last_close", 0) < daily_res.get("ema50", 0):
             advice.append("Spekulatif Tinggi. Terdapat perlawanan jangka pendek, namun tren utama masih turun (Downtrend). Eksekusi hanya disarankan bagi Scalper berpengalaman dengan Stop Loss sangat ketat (Hit and Run).")
        else:
             advice.append("Peluang Scalping. Sangat cocok untuk *day-trading* memanfaatkan momentum volume saat ini.")
    else:
        advice.append(f"Tidak Direkomendasikan (Wait and See). {broker_res['top_seller']} sedang membuang barang. Sebaiknya Anda menghindari emiten ini hingga struktur harganya membaik.")

    return " ".join(advice)

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

    return {
        "ticker": ticker_clean,
        "price": float(last_price),
        "daily": daily_res,
        "intraday": intraday_res,
        "news": news_res,
        "broker": broker_res,
        "mentor_advice": mentor_text
    }
