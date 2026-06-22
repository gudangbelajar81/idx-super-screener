import yfinance as yf
import pandas as pd
import ta

def get_macro_data() -> dict:
    """
    Mengambil dan menganalisis data Makro Ekonomi secara real-time.
    
    Analogi: Ini adalah "Laporan Cuaca" sebelum kita memutuskan pergi ke pasar.
    Jika cuaca badai (IHSG turun, Rupiah melemah), kita perlu lebih hati-hati.
    
    Return: dict berisi status setiap indikator makro dan skor keseluruhan.
    """
    result = {
        "ihsg": {"value": None, "trend": "TIDAK DIKETAHUI", "status": "netral"},
        "usdidr": {"value": None, "trend": "TIDAK DIKETAHUI", "status": "netral"},
        "coal": {"value": None, "trend": "TIDAK DIKETAHUI", "status": "netral"},
        "gold": {"value": None, "trend": "TIDAK DIKETAHUI", "status": "netral"},
        "macro_score": 50,  # Default netral
        "market_condition": "NETRAL",
        "warning": ""
    }
    
    try:
        # ===== 1. IHSG (Indeks Harga Saham Gabungan) =====
        ihsg_df = yf.download("^JKSE", period="3mo", interval="1d", progress=False)
        if not ihsg_df.empty:
            close = ihsg_df['Close'].squeeze()
            ema20 = ta.trend.ema_indicator(close, window=20)
            ema50 = ta.trend.ema_indicator(close, window=50)
            
            last_close = float(close.iloc[-1])
            last_ema20 = float(ema20.iloc[-1])
            last_ema50 = float(ema50.iloc[-1])
            
            if last_close > last_ema20 > last_ema50:
                ihsg_trend = "UPTREND"
                ihsg_status = "positif"
            elif last_close < last_ema50:
                ihsg_trend = "DOWNTREND"
                ihsg_status = "negatif"
            else:
                ihsg_trend = "SIDEWAYS"
                ihsg_status = "netral"
            
            result["ihsg"] = {
                "value": round(last_close, 0),
                "trend": ihsg_trend,
                "status": ihsg_status,
                "ema20": round(last_ema20, 0),
                "ema50": round(last_ema50, 0)
            }
    except Exception as e:
        result["warning"] += f"IHSG error: {str(e)[:50]}. "
    
    try:
        # ===== 2. USD/IDR (Kekuatan Rupiah) =====
        fx_df = yf.download("USDIDR=X", period="1mo", interval="1d", progress=False)
        if not fx_df.empty:
            fx_close = fx_df['Close'].squeeze()
            last_fx = float(fx_close.iloc[-1])
            prev_fx = float(fx_close.iloc[-5])  # 5 hari lalu
            
            pct_change = ((last_fx - prev_fx) / prev_fx) * 100
            
            if pct_change > 1.0:
                fx_trend = "RUPIAH MELEMAH"
                fx_status = "negatif"
            elif pct_change < -1.0:
                fx_trend = "RUPIAH MENGUAT"
                fx_status = "positif"
            else:
                fx_trend = "STABIL"
                fx_status = "netral"
            
            result["usdidr"] = {
                "value": round(last_fx, 0),
                "trend": fx_trend,
                "status": fx_status,
                "change_pct": round(pct_change, 2)
            }
    except Exception as e:
        result["warning"] += f"USD/IDR error: {str(e)[:50]}. "
    
    try:
        # ===== 3. Batu Bara (Penting untuk saham energi IDX) =====
        coal_df = yf.download("MTF=F", period="1mo", interval="1d", progress=False)
        if not coal_df.empty and len(coal_df) > 5:
            coal_close = coal_df['Close'].squeeze()
            last_coal = float(coal_close.iloc[-1])
            prev_coal = float(coal_close.iloc[-5])
            pct = ((last_coal - prev_coal) / prev_coal) * 100
            
            result["coal"] = {
                "value": round(last_coal, 2),
                "trend": "NAIK" if pct > 2 else ("TURUN" if pct < -2 else "STABIL"),
                "status": "positif" if pct > 2 else ("negatif" if pct < -2 else "netral"),
                "change_pct": round(pct, 2)
            }
    except Exception:
        pass
    
    try:
        # ===== 4. Emas (Safe Haven indicator) =====
        gold_df = yf.download("GC=F", period="1mo", interval="1d", progress=False)
        if not gold_df.empty and len(gold_df) > 5:
            gold_close = gold_df['Close'].squeeze()
            last_gold = float(gold_close.iloc[-1])
            prev_gold = float(gold_close.iloc[-5])
            pct = ((last_gold - prev_gold) / prev_gold) * 100
            
            result["gold"] = {
                "value": round(last_gold, 2),
                "trend": "NAIK" if pct > 1 else ("TURUN" if pct < -1 else "STABIL"),
                # Emas naik bisa jadi orang lari dari saham (negatif untuk pasar)
                "status": "negatif" if pct > 2 else ("positif" if pct < -1 else "netral"),
                "change_pct": round(pct, 2)
            }
    except Exception:
        pass
    
    # ===== Hitung Skor Makro Final =====
    score = 50  # Mulai dari netral
    
    ihsg_s = result["ihsg"].get("status", "netral")
    fx_s = result["usdidr"].get("status", "netral")
    coal_s = result["coal"].get("status", "netral")
    
    if ihsg_s == "positif": score += 25
    elif ihsg_s == "negatif": score -= 30
    
    if fx_s == "positif": score += 15
    elif fx_s == "negatif": score -= 15
    
    if coal_s == "positif": score += 10
    elif coal_s == "negatif": score -= 10
    
    score = max(0, min(100, score))
    
    if score >= 70:
        condition = "KONDUSIF"
    elif score >= 40:
        condition = "WASPADA"
    else:
        condition = "BAHAYA"
    
    result["macro_score"] = score
    result["market_condition"] = condition
    
    return result


if __name__ == "__main__":
    import json
    print("Mengambil data makro...")
    data = get_macro_data()
    print(json.dumps(data, indent=2))
