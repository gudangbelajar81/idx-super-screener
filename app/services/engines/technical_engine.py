import pandas as pd
import ta
import numpy as np
from app.services.advanced.ml_proxy import get_ml_prediction

from app.services.advanced.bandarmology_engine import build_bandarmology
from app.services.advanced.utils import _round_price, calibrated_probability_from_score
from app.services.advanced.technical.setup_detector import detect_setup

# ===========================================================================
#  HELPER: ZLSMA (Zero Lag SMA)
# ===========================================================================
def calc_zlsma(series: pd.Series, length: int = 32) -> pd.Series:
    ema1 = ta.trend.ema_indicator(series, window=length)
    ema2 = ta.trend.ema_indicator(ema1, window=length)
    diff = ema1 - ema2
    zlsma = ema1 + diff
    return zlsma

def find_pivot_highs(series: pd.Series, left: int = 5, right: int = 5) -> pd.Series:
    pivots = pd.Series(np.nan, index=series.index)
    n = len(series)
    for i in range(left, n - right):
        window = series.iloc[i - left: i + right + 1]
        if series.iloc[i] == window.max():
            pivots.iloc[i] = series.iloc[i]
    return pivots

def find_pivot_lows(series: pd.Series, left: int = 5, right: int = 5) -> pd.Series:
    pivots = pd.Series(np.nan, index=series.index)
    n = len(series)
    for i in range(left, n - right):
        window = series.iloc[i - left: i + right + 1]
        if series.iloc[i] == window.min():
            pivots.iloc[i] = series.iloc[i]
    return pivots

def calculate_sr_zones(df: pd.DataFrame, left: int = 5, right: int = 5, zone_pct: float = 0.02) -> dict:
    pivot_highs = find_pivot_highs(df['High'], left, right)
    pivot_lows = find_pivot_lows(df['Low'], left, right)
    valid_highs = pivot_highs.dropna().values
    valid_lows = pivot_lows.dropna().values
    last_close = df['Close'].iloc[-1]
    
    def cluster_pivots(pivots, threshold=0.03):
        clusters = []
        for p in pivots:
            found = False
            for cluster in clusters:
                if abs(p - cluster['center']) / cluster['center'] <= threshold:
                    cluster['points'].append(p)
                    cluster['center'] = sum(cluster['points']) / len(cluster['points'])
                    cluster['count'] += 1
                    found = True
                    break
            if not found:
                clusters.append({'center': p, 'points': [p], 'count': 1})
        return clusters

    res_clusters = cluster_pivots(valid_highs, zone_pct)
    sup_clusters = cluster_pivots(valid_lows, zone_pct)
    
    resistance_zones = [c for c in res_clusters if c['center'] > last_close]
    support_zones = [c for c in sup_clusters if c['center'] < last_close]
    
    # Sort resistance by closest to current price (ascending)
    resistance_zones.sort(key=lambda x: x['center'])
    # Sort support by closest to current price (descending)
    support_zones.sort(key=lambda x: x['center'], reverse=True)
    
    # Find strongest support (highest count)
    strongest_support = sorted(support_zones, key=lambda x: x['count'], reverse=True)[0] if support_zones else None
    
    return {
        "nearest_resistance": resistance_zones[0] if resistance_zones else None,
        "nearest_support": support_zones[0] if support_zones else None,
        "strongest_support": strongest_support,
        "all_resistance": resistance_zones[:5],
        "all_support": support_zones[:5]
    }

def calc_chaikin_money_flow(df: pd.DataFrame, period: int = 20) -> float:
    high = df['High']
    low = df['Low']
    close = df['Close']
    volume = df['Volume']
    mfm = ((close - low) - (high - close)) / (high - low + 1e-9)
    mfv = mfm * volume
    cmf = mfv.rolling(window=period).sum() / volume.rolling(window=period).sum()
    return float(cmf.iloc[-1])

def detect_fvg(df: pd.DataFrame) -> pd.Series:
    fvg = pd.Series(False, index=df.index)
    if len(df) >= 3:
        high_prev2 = df['High'].shift(2)
        close_prev1 = df['Close'].shift(1)
        is_bull_fvg = (df['Low'] > high_prev2) & (close_prev1 > high_prev2)
        fvg = is_bull_fvg
    return fvg

def calc_obv(df: pd.DataFrame) -> pd.Series:
    obv = ta.volume.OnBalanceVolumeIndicator(close=df['Close'], volume=df['Volume'])
    return obv.on_balance_volume()

def calc_vwap(df: pd.DataFrame) -> pd.Series:
    typical_price = (df['High'] + df['Low'] + df['Close']) / 3
    cumulative_tp_vol = (typical_price * df['Volume']).cumsum()
    cumulative_vol = df['Volume'].cumsum()
    vwap = cumulative_tp_vol / cumulative_vol
    return vwap

# ===========================================================================
#  ANALISA UTAMA: MODE BENTENG (SWING/POSITIONAL)
# ===========================================================================
def analyze_swing_fortress(df: pd.DataFrame) -> dict:
    if len(df) < 200:
        return {"signal": False, "reason": "Data kurang dari 200 hari"}
        
    df = df.copy()
    df['ZLSMA_32'] = calc_zlsma(df['Close'], 32)
    df['EMA_200'] = ta.trend.ema_indicator(df['Close'], window=200)
    df['RSI'] = ta.momentum.rsi(df['Close'], window=14)
    df['Bull_FVG'] = detect_fvg(df)
    
    cmf = calc_chaikin_money_flow(df, period=20)
    sr_zones = calculate_sr_zones(df, left=10, right=10)
    
    last_idx = df.index[-1]
    curr = df.loc[last_idx]
    prev = df.loc[df.index[-2]]
    last_close = float(curr['Close'])
    
    is_uptrend = last_close > curr['EMA_200']
    zlsma_up = curr['ZLSMA_32'] > prev['ZLSMA_32']
    fvg_ok = bool(curr['Bull_FVG'])
    bandar_masuk = cmf > 0.0
    
    signal = is_uptrend and zlsma_up and (fvg_ok or bandar_masuk)
    
    tp_price = None
    sl_price = None
    sl2_price = None
    sl2_uji = 0
    risk_reward = None
    
    if signal:
        if sr_zones['nearest_resistance']:
            tp_price = round(sr_zones['nearest_resistance']['center'], 0)
        else:
            tp_price = round(last_close * 1.05, 0)
            
        if sr_zones['nearest_support']:
            sl_price = round(sr_zones['nearest_support']['center'], 0)
        else:
            sl_price = round(last_close * 0.97, 0)
            
        # Tentukan SL 2 (SL Major)
        if sr_zones['strongest_support']:
            sl2_raw = round(sr_zones['strongest_support']['center'], 0)
            sl2_uji = sr_zones['strongest_support']['count']
        else:
            sl2_raw = round(last_close * 0.95, 0)
            sl2_uji = 1
            
        # Batasan maksimal SL 2 (Max Cap -8%)
        max_loss_price = round(last_close * 0.92, 0)
        if sl2_raw < max_loss_price:
            sl2_price = max_loss_price
        else:
            sl2_price = sl2_raw
            
        if tp_price and sl_price and (last_close - sl_price) > 0:
            risk = last_close - sl_price
            reward = tp_price - last_close
            risk_reward = round(reward / risk, 2)
            
            # [STRATEGY UPDATE] Filter Rasio Risk/Reward minimal 1.5
            if risk_reward < 1.5:
                signal = False  # Batal masuk jika tidak menguntungkan secara probabilitas

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
    if signal and smart_money_score > 0.35:
        base_score += 15
    if signal and is_uptrend:
        base_score += 10
    win_probability = calibrated_probability_from_score(base_score)

    if tp_price: tp_price = _round_price(tp_price)
    if sl_price: sl_price = _round_price(sl_price)
    if sl2_price: sl2_price = _round_price(sl2_price)


    # --- AI Prediction (AstroCycle Machine Learning Proxy) ---
    ai_data = get_ml_prediction(df)
    ai_text = ai_data.get("prediction_text", "Tidak ada data")
    ai_confidence = ai_data.get("ai_confidence", 0)
    
    return {
        "signal": bool(signal),
        "uptrend": bool(is_uptrend),
        "zlsma_val": float(curr['ZLSMA_32']),
        "fvg_detected": fvg_ok,
        "cmf": round(cmf, 3),
        "smart_money_score": round(smart_money_score, 3),
        "bandar_verdict": verdict_bandar,
        "win_probability": round(win_probability, 1),
        "tp": tp_price,
        "sl": sl_price,
        "sl2": sl2_price,
        "sl2_uji": sl2_uji,
        "rr": risk_reward,
        "ai_prediction": ai_text,
        "ai_confidence": ai_confidence
    }

# ===========================================================================
#  ANALISA UTAMA: MODE KAVALERI (FAST SWING)
# ===========================================================================
def analyze_cavalry_fast_swing(df: pd.DataFrame) -> dict:
    if len(df) < 50:
        return {"signal": False, "reason": "Data kurang dari 50 candle"}
    df = df.copy()
    
    bb = ta.volatility.BollingerBands(df['Close'], window=20, window_dev=2)
    df['BB_High'] = bb.bollinger_hband()
    df['BB_Low'] = bb.bollinger_lband()
    
    kc = ta.volatility.KeltnerChannel(df['High'], df['Low'], df['Close'], window=20, window_atr=20, multiplier=1.5)
    df['KC_High'] = kc.keltner_channel_hband()
    df['KC_Low'] = kc.keltner_channel_lband()
    
    df['Squeeze_On'] = (df['BB_Low'] > df['KC_Low']) & (df['BB_High'] < df['KC_High'])
    
    pivots = find_pivot_lows(df['Low'], left=5, right=5)
    df['Support_Level'] = pivots.ffill()
    
    last_idx = df.index[-1]
    curr = df.loc[last_idx]
    
    is_trap = False
    if not pd.isna(curr['Support_Level']):
        for i in range(1, 4):
            if df['Low'].iloc[-i] < curr['Support_Level'] and df['Close'].iloc[-1] > curr['Support_Level']:
                is_trap = True
                break
                
    cmf = calc_chaikin_money_flow(df, period=10)
    bandar_masuk = cmf > 0
    
    zlsma = calc_zlsma(df['Close'], 14)
    zlsma_up = zlsma.iloc[-1] > zlsma.iloc[-2]
    
    last_close = float(curr['Close'])
    
    squeeze_fired = df['Squeeze_On'].iloc[-2] == True and df['Squeeze_On'].iloc[-1] == False
    is_squeeze = squeeze_fired or df['Squeeze_On'].iloc[-1]
    
    signal = (squeeze_fired or is_trap) and bandar_masuk and zlsma_up
    
    sr_zones = calculate_sr_zones(df, left=5, right=5)
    
    tp_price = round(sr_zones['nearest_resistance']['center'], 0) if sr_zones['nearest_resistance'] else round(last_close * 1.06, 0)
    sl_price = round(sr_zones['nearest_support']['center'], 0) if sr_zones['nearest_support'] else round(last_close * 0.95, 0)
    
    if sr_zones['strongest_support']:
        sl2_raw = round(sr_zones['strongest_support']['center'], 0)
        sl2_uji = sr_zones['strongest_support']['count']
    else:
        sl2_raw = round(last_close * 0.93, 0)
        sl2_uji = 1
        
    max_loss_price = round(last_close * 0.94, 0)
    sl2_price = max_loss_price if sl2_raw < max_loss_price else sl2_raw
    
    risk_reward = 0
    if tp_price and sl_price and (last_close - sl_price) > 0:
        risk = last_close - sl_price
        reward = tp_price - last_close
        risk_reward = round(reward / risk, 2)
        
    return {
        "signal": bool(signal),
        "squeeze_fired": bool(squeeze_fired),
        "smc_trap": bool(is_trap),
        "cmf": round(cmf, 3),
        "bandar_masuk": bool(bandar_masuk),
        "close": last_close,
        "tp": tp_price,
        "sl": sl_price,
        "sl2": sl2_price,
        "sl2_uji": sl2_uji,
        "rr": risk_reward,
    }

# ===========================================================================
#  ANALISA UTAMA: MODE NINJA (SCALPER/GORENGAN)
# ===========================================================================
def analyze_ninja_scalper(df: pd.DataFrame) -> dict:
    if len(df) < 50:
        return {"signal": False, "reason": "Data kurang dari 50 candle"}
        
    df = df.copy()
    df['Vol_SMA20'] = df['Volume'].rolling(window=20).mean()
    df['Spread'] = abs(df['Close'] - df['Open'])
    df['Spread_Pct'] = (df['Spread'] / df['Open'].replace(0, np.nan)) * 100
    cmf = calc_chaikin_money_flow(df, period=14)
    df['OBV'] = calc_obv(df)
    df['OBV_SMA5'] = df['OBV'].rolling(window=5).mean()
    df['OBV_SMA10'] = df['OBV'].rolling(window=10).mean()
    df['VWAP'] = calc_vwap(df)
    
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
    
    # --- AI Prediction (AstroCycle Machine Learning Proxy) ---
    ai_data = get_ml_prediction(df)
    ai_text = ai_data.get("prediction_text", "Tidak ada data")
    ai_confidence = ai_data.get("ai_confidence", 0)

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
        "win_probability": round(win_probability, 1),
        "ai_prediction": ai_text,
        "ai_confidence": ai_confidence
    }
