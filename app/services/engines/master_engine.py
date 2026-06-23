import pandas as pd
import json
import os
import ta
import numpy as np
import random
from .technical_engine import calculate_sr_zones

def calc_vwap(df: pd.DataFrame) -> pd.Series:
    typical_price = (df['High'] + df['Low'] + df['Close']) / 3
    cumulative_tp_vol = (typical_price * df['Volume']).cumsum()
    cumulative_vol = df['Volume'].cumsum()
    return cumulative_tp_vol / cumulative_vol

def calc_chaikin_money_flow(df: pd.DataFrame, period: int = 20) -> float:
    high = df['High']
    low = df['Low']
    close = df['Close']
    volume = df['Volume']
    mfm = ((close - low) - (high - close)) / (high - low + 1e-9)
    mfv = mfm * volume
    cmf = mfv.rolling(window=period).sum() / volume.rolling(window=period).sum()
    return float(cmf.iloc[-1]) if not pd.isna(cmf.iloc[-1]) else 0.0


EDGE_DB_CACHE = None

def get_edge_db():
    global EDGE_DB_CACHE
    if EDGE_DB_CACHE is None:
        try:
            db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'historical_edge_db.json')
            with open(db_path, 'r') as f:
                EDGE_DB_CACHE = json.load(f)
        except:
            EDGE_DB_CACHE = {"base_win_rates": {}, "astro_modifiers": {}}
    return EDGE_DB_CACHE

def calculate_master_score(df: pd.DataFrame) -> dict:
    if len(df) < 50:
        return {"error": "Data kurang dari 50 candle"}
        
    df = df.copy()
    last_close = float(df['Close'].iloc[-1])
    last_vol = float(df['Volume'].iloc[-1])
    
    # 1. Indikator Dasar
    df['EMA5'] = ta.trend.ema_indicator(df['Close'], window=5)
    df['EMA9'] = ta.trend.ema_indicator(df['Close'], window=9)
    df['EMA20'] = ta.trend.ema_indicator(df['Close'], window=20)
    df['EMA50'] = ta.trend.ema_indicator(df['Close'], window=50)
    df['EMA200'] = ta.trend.ema_indicator(df['Close'], window=200)
    df['VWAP'] = calc_vwap(df)
    
    vol_sma20 = df['Volume'].rolling(window=20).mean().iloc[-1]
    rvol = last_vol / vol_sma20 if vol_sma20 > 0 else 0
    vol_expansion_pct = (rvol - 1) * 100
    
    cmf_20 = calc_chaikin_money_flow(df, period=20)

    # Volatilitas (ATR%)
    df['ATR'] = ta.volatility.average_true_range(df['High'], df['Low'], df['Close'], window=14)
    atr_val = df['ATR'].iloc[-1]
    atr_pct = (atr_val / last_close) * 100 if last_close > 0 else 0

    
    highest_20 = df['High'].tail(20).max()
    lowest_20 = df['Low'].tail(20).min()
    
    curr = df.iloc[-1]
    
    # 2. Perhitungan Komponen Skor (0-100)
    
    # A. Relative Strength Score (20%)
    # Dihitung dari jarak harga terhadap EMA50 dan posisi di antara High-Low 20 hari
    rs_raw = (last_close - curr['EMA50']) / curr['EMA50'] * 100 if not pd.isna(curr['EMA50']) else 0
    rs_score = min(max(int((rs_raw + 10) * 5), 0), 100)
    
    # B. Smart Money & Institutional Score (20% + 10% = 30%)
    # Dihitung dari Chaikin Money Flow dan Volume Expansion
    sm_raw = cmf_20 * 100 # CMF range -1 to 1
    sm_score = min(max(int(sm_raw + 50), 0), 100)
    inst_score = min(max(int(rvol * 20), 0), 100)
    
    # C. Trend & Market Regime Score (15% + 15% = 30%)
    # Dihitung dari alignment EMA
    trend_score = 0
    if curr['EMA5'] > curr['EMA20']: trend_score += 30
    if curr['EMA20'] > curr['EMA50']: trend_score += 30
    if not pd.isna(curr['EMA200']) and curr['EMA50'] > curr['EMA200']: trend_score += 40
    
    # D. Catalyst Score (Proxy/Simulasi 10%)
    # Disimulasikan berdasarkan volatilitas dan spike (berita biasanya memicu spike)
    catalyst_score = min(max(int(vol_expansion_pct / 3), 0), 100)
    
    # E. Risk & Historical Edge (10%)
    # Jarak ke titik terendah 20 hari (makin dekat support makin kecil risiko)
    risk_dist = (last_close - lowest_20) / lowest_20 * 100 if lowest_20 > 0 else 100
    risk_score = 100 - min(max(int(risk_dist * 5), 0), 100)
    
    # 3. COMPOSITE SCORE (0-100)
    composite_score = int(
        (rs_score * 0.20) + 
        (sm_score * 0.20) + 
        (inst_score * 0.10) + 
        (trend_score * 0.30) + 
        (catalyst_score * 0.10) + 
        (risk_score * 0.10)
    )
    
    # 4. INTRADAY MOMENTUM LAYER (Filter Ketat)
    is_intraday_eligible = (
        rvol > 2.0 and 
        vol_expansion_pct > 200 and 
        last_close > curr['VWAP'] and 
        curr['EMA5'] > curr['EMA9'] and 
        curr['EMA9'] > curr['EMA20'] and 
        cmf_20 > 0
    )
    
    intraday_score = composite_score + 10 if is_intraday_eligible else 0
    intraday_score = min(intraday_score, 100)
    
    # 5. SWING TRADING LAYER (Filter Ketat)
    is_swing_eligible = (
        not pd.isna(curr['EMA200']) and
        atr_pct >= 3.0 and # FILTER SAHAM KEONG
        curr['EMA50'] > curr['EMA200'] and 
        cmf_20 > 0.05 and
        trend_score >= 60
    )
    
    swing_score = composite_score + 5 if is_swing_eligible else 0
    swing_score = min(swing_score, 100)
    
    # 6. Status & Attributes
    smart_money_status = "Akumulasi Masif" if sm_score > 70 else "Distribusi" if sm_score < 30 else "Netral"
    trend_status = "Strong Bullish" if trend_score == 100 else "Bullish" if trend_score >= 60 else "Sideways/Bearish"
    setup_type = "ORB Breakout" if is_intraday_eligible else "VCP/Pullback" if is_swing_eligible else "Tidak Ada"
    
    recommendation = "AVOID"
    if composite_score >= 80 and (is_intraday_eligible or is_swing_eligible):
        recommendation = "STRONG BUY"
    elif composite_score >= 65 and (is_intraday_eligible or is_swing_eligible):
        recommendation = "BUY"
    elif composite_score >= 50:
        recommendation = "WATCHLIST"
        
    intraday_rec = "BUY" if is_intraday_eligible else "AVOID"
    swing_rec = "BUY" if is_swing_eligible else "AVOID"
    if recommendation == "STRONG BUY" and is_intraday_eligible: intraday_rec = "STRONG BUY"
    if recommendation == "STRONG BUY" and is_swing_eligible: swing_rec = "STRONG BUY"
        
    
    # Inject Historical Edge Data & SL2
    edge_db = get_edge_db()
    edge_data = edge_db.get("base_win_rates", {})

    # Projections menggunakan Support/Resistance
    sr_zones = calculate_sr_zones(df, left=10, right=10, zone_pct=0.02)
    if sr_zones['nearest_resistance']:
        tp = round(sr_zones['nearest_resistance']['center'], 0)
    else:
        tp = round(highest_20 * 1.05, 0) if highest_20 > 0 else round(last_close * 1.05, 0)
        
    if sr_zones['nearest_support']:
        sl = round(sr_zones['nearest_support']['center'], 0)
    else:
        sl = round(lowest_20 * 0.98, 0) if lowest_20 > 0 else round(last_close * 0.95, 0)
        
    if sr_zones['strongest_support']:
        sl2_raw = round(sr_zones['strongest_support']['center'], 0)
        sl2_uji = sr_zones['strongest_support']['count']
    else:
        sl2_raw = round(last_close * 0.90, 0)
        sl2_uji = 1
        
    # Capping risiko (Anti-Kiamat)
    max_sl1_price = round(last_close * 0.94, 0) # Maksimal -6% untuk SL1
    max_sl2_price = round(last_close * 0.90, 0) # Maksimal -10% untuk SL2
    
    sl = max_sl1_price if sl < max_sl1_price else sl
    sl2_price = max_sl2_price if sl2_raw < max_sl2_price else sl2_raw
    
    # Pastikan SL2 tidak lebih tinggi dari SL1 (Logika terbalik yang bikin bingung)
    if sl2_price > sl:
        sl2_price = sl
        
    rr = round((tp - last_close) / (last_close - sl), 2) if last_close > sl else 0.0
    
    # Save SL2 in edge_data so it can be extracted later
    edge_data["sl2"] = sl2_price
    edge_data["sl2_uji"] = sl2_uji


    return {
        "error": None,
        "close_price": last_close,
        "avg_value": last_vol * last_close, # proxy
        "avg_volatility": (df['High'].iloc[-20:].mean() - df['Low'].iloc[-20:].mean()) / df['Low'].iloc[-20:].mean(),
        
        "relative_strength_score": rs_score,
        "smart_money_score": sm_score,
        "institutional_score": inst_score,
        "catalyst_score": catalyst_score,
        
        "composite_score": composite_score,
        "intraday_score": intraday_score,
        "swing_score": swing_score,
        
        "smart_money_status": smart_money_status,
        "institutional_status": "Foreign Inflow" if inst_score > 60 else "Netral",
        "catalyst_status": "Berita Positif" if catalyst_score > 60 else "Sepi",
        "trend_status": trend_status,
        "setup_type": setup_type,
        
        "recommendation": recommendation,
        "intraday_recommendation": intraday_rec,
        "swing_recommendation": swing_rec,
        
        "expected_return": round((tp - last_close) / last_close * 100, 2),
        "target_profit": tp,
        "stop_loss": sl,
        "risk_reward_ratio": rr,
        "edge_data": json.dumps(edge_data)
    }
