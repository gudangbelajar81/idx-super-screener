content = """
# ===========================================================================
#  ANALISA UTAMA: MODE NINJA (SCALPER/GORENGAN) - Versi Alpha Engine
# ===========================================================================
def analyze_ninja_scalper(df):
    import numpy as np
    import ta
    from app.services.engines.technical_engine import calc_chaikin_money_flow, calc_obv, calc_vwap, calculate_sr_zones
    from app.services.advanced.bandarmology_engine import build_bandarmology
    from app.services.advanced.utils import _round_price, calibrated_probability_from_score
    
    if len(df) < 50:
        return {"signal": False, "reason": "Data kurang dari 50 candle"}
        
    df = df.copy()
    
    # Volume SMA
    df['Vol_SMA20'] = df['Volume'].rolling(window=20).mean()
    
    # Spread analysis
    df['Spread'] = abs(df['Close'] - df['Open'])
    df['Spread_Pct'] = (df['Spread'] / df['Open'].replace(0, np.nan)) * 100
    
    # CMF Intraday
    cmf = calc_chaikin_money_flow(df, period=14)
    
    # OBV Analysis
    df['OBV'] = calc_obv(df)
    df['OBV_SMA5'] = df['OBV'].rolling(window=5).mean()
    df['OBV_SMA10'] = df['OBV'].rolling(window=10).mean()
    
    # VWAP
    df['VWAP'] = calc_vwap(df)
    
    # StochRSI
    try:
        stoch_rsi = ta.momentum.StochRSIIndicator(close=df['Close'], window=14, smooth1=3, smooth2=3)
        df['StochRSI_K'] = stoch_rsi.stochrsi_k()
        df['StochRSI_D'] = stoch_rsi.stochrsi_d()
    except Exception:
        df['StochRSI_K'] = 0.5
        df['StochRSI_D'] = 0.5
        
    sr_zones = calculate_sr_zones(df, left=3, right=3, zone_pct=0.005)
    
    last_idx = df.index[-1]
    curr = df.loc[last_idx]
    last_close = float(curr['Close'])
    
    vol_spike_4x = curr['Volume'] > (curr['Vol_SMA20'] * 4)
    body = abs(curr['Close'] - curr['Open'])
    upper_wick = curr['High'] - max(curr['Close'], curr['Open'])
    no_trap = body > upper_wick
    
    price_up_2pct = curr['Spread_Pct'] > 2.0 and curr['Close'] > curr['Open']
    highest_1h = df['High'].tail(12).max()
    is_breakout = curr['Close'] >= highest_1h
    
    strong_money_flow = cmf > 0.05
    obv_up = curr['OBV_SMA5'] > curr['OBV_SMA10']
    
    above_vwap = last_close > float(curr['VWAP']) if not np.isnan(curr['VWAP']) else True
    stoch_k = float(curr['StochRSI_K']) if not np.isnan(curr['StochRSI_K']) else 0.5
    not_overbought = stoch_k < 0.85
    
    raw_signal = bool(vol_spike_4x and no_trap and price_up_2pct and is_breakout and strong_money_flow and obv_up and above_vwap and not_overbought)
    
    tp_price = None
    sl_price = None
    risk_reward = None
    signal = False
    
    if raw_signal:
        if sr_zones['nearest_resistance']:
            tp_price = round(sr_zones['nearest_resistance']['center'], 0)
        else:
            tp_price = round(last_close * 1.02, 0)
            
        if sr_zones['nearest_support']:
            sl_price = round(sr_zones['nearest_support']['center'], 0)
        else:
            sl_price = round(last_close * 0.99, 0)
        
        if tp_price and sl_price and last_close > sl_price:
            risk = last_close - sl_price
            reward = tp_price - last_close
            if risk > 0:
                risk_reward = round(reward / risk, 2)
                signal = risk_reward >= 1.5
            else:
                signal = False
        else:
            signal = False

    # --- Bandarmology Engine & Probability (Advanced) ---
    df_bandar = df.copy()
    df_bandar.columns = [str(col).lower() for col in df_bandar.columns]
    if "date" not in df_bandar.columns:
        df_bandar["date"] = df_bandar.index

    bandar_data = {}
    try:
        bandar_data = build_bandarmology(df_bandar, ticker="")
    except Exception:
        pass
        
    smart_money_score = bandar_data.get("smart_money_score", 0)
    verdict_bandar = bandar_data.get("verdict", "netral")
    
    base_score = 65 if signal else 40
    if signal and smart_money_score > 0.2:
        base_score += 10
    if signal and vol_spike_4x:
        base_score += 10
    win_probability = calibrated_probability_from_score(base_score)

    if tp_price: tp_price = _round_price(tp_price)
    if sl_price: sl_price = _round_price(sl_price)

    return {
        "signal": signal,
        "volume_spike": bool(vol_spike_4x),
        "spread_pct": float(curr['Spread_Pct']),
        "cmf": round(cmf, 3),
        "above_vwap": bool(above_vwap),
        "stoch_rsi_k": round(stoch_k, 3),
        "rr": risk_reward,
        "close": last_close,
        "tp": tp_price,
        "sl": sl_price,
        "smart_money_score": round(smart_money_score, 3),
        "bandar_verdict": verdict_bandar,
        "win_probability": round(win_probability, 1)
    }
"""

with open(r'app\services\engines\technical_engine.py', 'a', encoding='utf-8') as f:
    f.write('\n' + content + '\n')
print('Restored analyze_ninja_scalper')
