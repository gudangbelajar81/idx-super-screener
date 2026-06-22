import pandas as pd
import ta
import numpy as np

# ===========================================================================
#  HELPER: ZLSMA (Zero Lag SMA)
# ===========================================================================
def calc_zlsma(series: pd.Series, length: int = 32) -> pd.Series:
    """Menghitung Zero Lag SMA (ZLSMA) sesuai algoritma SUPREME TREND."""
    ema1 = ta.trend.ema_indicator(series, window=length)
    ema2 = ta.trend.ema_indicator(ema1, window=length)
    diff = ema1 - ema2
    zlsma = ema1 + diff
    return zlsma


# ===========================================================================
#  HELPER: PIVOT POINTS (Dasar dari Pine Script S&R Zones [FEELS])
# ===========================================================================
def find_pivot_highs(series: pd.Series, left: int = 5, right: int = 5) -> pd.Series:
    """
    Mencari Pivot High: Titik dimana harga lebih tinggi dari N candle kiri dan kanan.
    Inilah terjemahan dari fungsi ta.pivothigh() di Pine Script.
    """
    pivots = pd.Series(np.nan, index=series.index)
    n = len(series)
    for i in range(left, n - right):
        window = series.iloc[i - left: i + right + 1]
        if series.iloc[i] == window.max():
            pivots.iloc[i] = series.iloc[i]
    return pivots


def find_pivot_lows(series: pd.Series, left: int = 5, right: int = 5) -> pd.Series:
    """
    Mencari Pivot Low: Titik dimana harga lebih rendah dari N candle kiri dan kanan.
    Inilah terjemahan dari fungsi ta.pivotlow() di Pine Script.
    """
    pivots = pd.Series(np.nan, index=series.index)
    n = len(series)
    for i in range(left, n - right):
        window = series.iloc[i - left: i + right + 1]
        if series.iloc[i] == window.min():
            pivots.iloc[i] = series.iloc[i]
    return pivots


# ===========================================================================
#  HELPER: S&R ZONE CALCULATOR (Inti dari Pine Script S&R Zones [FEELS])
# ===========================================================================
def calculate_sr_zones(df: pd.DataFrame, left: int = 5, right: int = 5, zone_pct: float = 0.01) -> dict:
    """
    Menghitung Zona Support dan Resistance dari Pivot Points.
    
    Analogi: Bayangkan sebuah lantai dan langit-langit di dalam rumah.
    - Zona Support = Lantai (harga susah turun menembus ini)
    - Zona Resistance = Langit-langit (harga susah naik menembus ini)
    
    zone_pct: Toleransi lebar zona dalam persen (default 1%)
    """
    pivot_highs = find_pivot_highs(df['High'], left, right)
    pivot_lows = find_pivot_lows(df['Low'], left, right)
    
    # Ambil pivot yang valid (tidak NaN)
    valid_highs = pivot_highs.dropna().values
    valid_lows = pivot_lows.dropna().values
    
    last_close = df['Close'].iloc[-1]
    
    # Kelompokkan Zona Resistance: Pivot High yang di ATAS harga saat ini
    resistance_zones = []
    for ph in valid_highs:
        if ph > last_close:
            zone = {"center": ph, "low": ph * (1 - zone_pct), "high": ph * (1 + zone_pct)}
            resistance_zones.append(zone)
    
    # Kelompokkan Zona Support: Pivot Low yang di BAWAH harga saat ini
    support_zones = []
    for pl in valid_lows:
        if pl < last_close:
            zone = {"center": pl, "low": pl * (1 - zone_pct), "high": pl * (1 + zone_pct)}
            support_zones.append(zone)
    
    # Urutkan: Resistance terdekat (paling bawah), Support terdekat (paling atas)
    resistance_zones.sort(key=lambda x: x['center'])
    support_zones.sort(key=lambda x: x['center'], reverse=True)
    
    return {
        "nearest_resistance": resistance_zones[0] if resistance_zones else None,
        "nearest_support": support_zones[0] if support_zones else None,
        "all_resistance": resistance_zones[:5],  # 5 zona terdekat
        "all_support": support_zones[:5]
    }


# ===========================================================================
#  HELPER: ACCUMULATION / DISTRIBUTION & CMF (Detektor Jejak Bandar)
# ===========================================================================
def calc_chaikin_money_flow(df: pd.DataFrame, period: int = 20) -> float:
    """
    Menghitung Chaikin Money Flow (CMF) untuk mendeteksi akumulasi/distribusi.
    
    Analogi: Ini adalah 'Detektor Logam' yang mendeteksi apakah 'uang besar'
    sedang masuk ke saham (Akumulasi) atau keluar dari saham (Distribusi).
    
    Hasil: 
    - CMF > 0.1 = Akumulasi (Beli disokong bandar, AMAN)
    - CMF < -0.1 = Distribusi (Bandar sedang jual, BERBAHAYA!)
    """
    high = df['High']
    low = df['Low']
    close = df['Close']
    volume = df['Volume']
    
    # Money Flow Multiplier
    mfm = ((close - low) - (high - close)) / (high - low + 1e-9)
    
    # Money Flow Volume
    mfv = mfm * volume
    
    # CMF = Sum(MFV, N) / Sum(Volume, N)
    cmf = mfv.rolling(window=period).sum() / volume.rolling(window=period).sum()
    
    return float(cmf.iloc[-1])


# ===========================================================================
#  HELPER: FAIR VALUE GAP (FVG)
# ===========================================================================
def detect_fvg(df: pd.DataFrame) -> pd.Series:
    """Mendeteksi Bullish Fair Value Gap (FVG)."""
    fvg = pd.Series(False, index=df.index)
    if len(df) >= 3:
        high_prev2 = df['High'].shift(2)
        close_prev1 = df['Close'].shift(1)
        is_bull_fvg = (df['Low'] > high_prev2) & (close_prev1 > high_prev2)
        fvg = is_bull_fvg
    return fvg


# ===========================================================================
#  HELPER: ON-BALANCE VOLUME (OBV)
# ===========================================================================
def calc_obv(df: pd.DataFrame) -> pd.Series:
    """
    Menghitung On-Balance Volume (OBV).
    Jika harga ditutup naik, volume ditambah. Jika turun, volume dikurangi.
    Mendeteksi akumulasi diam-diam.
    """
    obv = ta.volume.OnBalanceVolumeIndicator(close=df['Close'], volume=df['Volume'])
    return obv.on_balance_volume()


# ===========================================================================
#  HELPER: VWAP (Volume Weighted Average Price)
# ===========================================================================
def calc_vwap(df: pd.DataFrame) -> pd.Series:
    """
    Menghitung VWAP (Volume Weighted Average Price).
    
    Analogi: VWAP adalah 'Harga Adil' yang disepakati oleh semua pelaku pasar
    (termasuk institusi besar) pada hari itu. 
    - Harga di ATAS VWAP = Pasar bullish, institusi sudah masuk.
    - Harga di BAWAH VWAP = Harga masih murah, tapi belum ada konfirmasi.
    
    Filter VWAP sangat ampuh memotong sinyal palsu (false breakout).
    """
    typical_price = (df['High'] + df['Low'] + df['Close']) / 3
    cumulative_tp_vol = (typical_price * df['Volume']).cumsum()
    cumulative_vol = df['Volume'].cumsum()
    vwap = cumulative_tp_vol / cumulative_vol
    return vwap


# ===========================================================================
#  ANALISA UTAMA: MODE BENTENG (SWING/POSITIONAL)
# ===========================================================================
def analyze_swing_fortress(df: pd.DataFrame) -> dict:
    """
    [ALPHA ENGINE v2] Menganalisa saham untuk Mode Benteng.
    
    Lapis Penyaringan:
    1. EMA 200 (Tren Besar - Benteng Utama)
    2. ZLSMA 32 (Momentum - Gas Pedal)
    3. Bullish FVG (Katalis Entry)
    4. CMF (Detektor Jejak Bandar - Validasi Akumulasi)
    5. S&R Zones (Kalkulasi TP & SL Presisi)
    """
    if len(df) < 200:
        return {"signal": False, "reason": "Data kurang dari 200 hari"}
        
    df = df.copy()
    
    # --- Kalkulasi Indikator ---
    df['ZLSMA_32'] = calc_zlsma(df['Close'], 32)
    df['EMA_200'] = ta.trend.ema_indicator(df['Close'], window=200)
    df['RSI'] = ta.momentum.rsi(df['Close'], window=14)
    df['Bull_FVG'] = detect_fvg(df)
    
    # CMF untuk deteksi Bandar
    cmf = calc_chaikin_money_flow(df, period=20)
    
    # S&R Zones untuk TP & SL
    sr_zones = calculate_sr_zones(df, left=10, right=10)
    
    last_idx = df.index[-1]
    curr = df.loc[last_idx]
    prev = df.loc[df.index[-2]]
    
    last_close = float(curr['Close'])
    
    # --- Aturan Sinyal (Semua harus terpenuhi) ---
    is_uptrend = last_close > curr['EMA_200']           # Syarat 1: Di atas EMA200
    zlsma_up = curr['ZLSMA_32'] > prev['ZLSMA_32']     # Syarat 2: Momentum naik
    fvg_ok = bool(curr['Bull_FVG'])                     # Syarat 3: Ada FVG
    bandar_masuk = cmf > 0.0                            # Syarat 4: CMF positif (Bandar masuk)
    
    signal = is_uptrend and zlsma_up and (fvg_ok or bandar_masuk)
    
    # --- Kalkulasi TP & SL Presisi ---
    tp_price = None
    sl_price = None
    risk_reward = None
    
    if signal:
        # Target Profit = Zona Resistance Terdekat
        if sr_zones['nearest_resistance']:
            tp_price = round(sr_zones['nearest_resistance']['center'], 0)
        else:
            # Fallback: +5% dari harga saat ini
            tp_price = round(last_close * 1.05, 0)
        
        # Stop Loss = Zona Support Terdekat (atau -3% jika tidak ada)
        if sr_zones['nearest_support']:
            sl_price = round(sr_zones['nearest_support']['center'], 0)
        else:
            sl_price = round(last_close * 0.97, 0)
        
        # Risk/Reward Ratio
        if tp_price and sl_price and (last_close - sl_price) != 0:
            risk = last_close - sl_price
            reward = tp_price - last_close
            risk_reward = round(reward / risk, 2) if risk > 0 else 0

    return {
        "signal": bool(signal),
        "uptrend": bool(is_uptrend),
        "zlsma_val": float(curr['ZLSMA_32']),
        "fvg_detected": fvg_ok,
        "cmf": round(cmf, 3),
        "bandar_masuk": bandar_masuk,
        "close": last_close,
        "tp": tp_price,
        "sl": sl_price,
        "rr": risk_reward,
    }


# ===========================================================================
#  ANALISA UTAMA: MODE NINJA (SCALPER/GORENGAN) - Versi Alpha Engine
# ===========================================================================
def analyze_ninja_scalper(df: pd.DataFrame) -> dict:
    """
    [ALPHA ENGINE v3 - TITAN PRECISION] Menganalisa saham untuk Mode Ninja (Gorengan).
    
    Lapis Penyaringan (7 Filter):
    1. Volume Spike (Volume > 4x rata-rata 20 candle)
    2. Wick Trap Filter (Anti-jebakan guyuran bandar)
    3. Momentum Breakout (Tembus Harga Tertinggi 1 Jam)
    4. CMF Intraday (Deteksi Akumulasi Diam-diam Bandar)
    5. OBV Divergence (Konfirmasi Arah Volume)
    6. [NEW] VWAP Filter (Harga wajib > VWAP = Konfirmasi Institusi)
    7. [NEW] Stochastic RSI (Momentum tidak overbought = Anti-FOMO)
    8. [NEW] Minimum Risk/Reward 1:1.5 (Disiplin Manajemen Risiko)
    """
    if len(df) < 50:
        return {"signal": False, "reason": "Data intraday tidak cukup"}
        
    df = df.copy()
    
    # === KALKULASI INDIKATOR ===
    
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
    
    # [NEW] VWAP (Volume Weighted Average Price)
    df['VWAP'] = calc_vwap(df)
    
    # [NEW] Stochastic RSI untuk filter anti-FOMO
    try:
        stoch_rsi = ta.momentum.StochRSIIndicator(close=df['Close'], window=14, smooth1=3, smooth2=3)
        df['StochRSI_K'] = stoch_rsi.stochrsi_k()
        df['StochRSI_D'] = stoch_rsi.stochrsi_d()
        stoch_ok = True
    except Exception:
        df['StochRSI_K'] = 0.5
        df['StochRSI_D'] = 0.5
        stoch_ok = False
    
    # S&R untuk Scalping TP/SL (lebih ketat)
    sr_zones = calculate_sr_zones(df, left=3, right=3, zone_pct=0.005)
    
    last_idx = df.index[-1]
    curr = df.loc[last_idx]
    last_close = float(curr['Close'])
    
    # === FILTER 7 LAPIS: THE SNIPER ALGORITHM v3 ===
    
    # Filter 1: Volume Spike (4x dari Rata-rata)
    vol_spike_4x = curr['Volume'] > (curr['Vol_SMA20'] * 4)
    
    # Filter 2: Wick Trap Filter (Ekor atas tidak boleh mendominasi badan candle)
    body = abs(curr['Close'] - curr['Open'])
    upper_wick = curr['High'] - max(curr['Close'], curr['Open'])
    no_trap = body > upper_wick
    
    # Filter 3: Momentum Breakout (Naik > 2% dan Tembus Harga Tertinggi 1 Jam Terakhir)
    price_up_2pct = curr['Spread_Pct'] > 2.0 and curr['Close'] > curr['Open']
    highest_1h = df['High'].tail(12).max()
    is_breakout = curr['Close'] >= highest_1h
    
    # Filter 4: Validasi Bandar CMF (> 0.05 = Uang besar masuk)
    strong_money_flow = cmf > 0.05
    
    # Filter 5: OBV Divergence (Volume semakin kuat = Akumulasi nyata)
    obv_up = curr['OBV_SMA5'] > curr['OBV_SMA10']
    
    # Filter 6: [NEW] VWAP Filter - Harga harus berada di atas VWAP
    # Ini memastikan kita masuk saat institusi sudah dalam posisi PROFIT
    above_vwap = last_close > float(curr['VWAP']) if not np.isnan(curr['VWAP']) else True
    
    # Filter 7: [NEW] Stochastic RSI Anti-FOMO
    # Kita tidak mau beli di ujung momentum (overbought > 0.85)
    # Kita cari yang momentum baru MULAI naik (K masih di bawah 0.85)
    stoch_k = float(curr['StochRSI_K']) if not np.isnan(curr['StochRSI_K']) else 0.5
    not_overbought = stoch_k < 0.85
    
    # === KEPUTUSAN SINYAL AWAL ===
    raw_signal = bool(
        vol_spike_4x and
        no_trap and
        price_up_2pct and
        is_breakout and
        strong_money_flow and
        obv_up and
        above_vwap and
        not_overbought
    )
    
    # === TP & SL KALKULASI ===
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
        
        # Filter 8: [NEW] Minimum Risk/Reward 1:1.5 (Disiplin Wajib)
        # Hanya masuk jika potensi untung minimal 1.5x lipat dari potensi rugi
        if tp_price and sl_price and last_close > sl_price:
            risk = last_close - sl_price
            reward = tp_price - last_close
            if risk > 0:
                risk_reward = round(reward / risk, 2)
                signal = risk_reward >= 1.5  # Hanya sinyal jika RR >= 1.5x
            else:
                signal = False
        else:
            signal = False
    
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
    }

# ===========================================================================
#  ANALISA UTAMA: MODE KAVALERI (FAST SWING 1-7 HARI) - LEVEL DEWA
# ===========================================================================
def analyze_kavaleri_special(df: pd.DataFrame) -> dict:
    """
    [ALPHA ENGINE v3] Menganalisa saham untuk Mode Kavaleri (Fast Swing).
    Menggunakan algoritma Hedge Fund:
    1. TTM Squeeze (Bollinger Bands vs Keltner Channels)
    2. SMC Liquidity Trap (Deteksi manipulasi Support)
    3. CMF (Uang Bandar masuk)
    """
    if len(df) < 50:
        return {"signal": False, "reason": "Data kurang dari 50 hari"}
        
    df = df.copy()
    
    # 1. TTM SQUEEZE (Bollinger vs Keltner)
    # Bollinger Bands (20, 2)
    bb = ta.volatility.BollingerBands(df['Close'], window=20, window_dev=2)
    df['BB_High'] = bb.bollinger_hband()
    df['BB_Low'] = bb.bollinger_lband()
    
    # Keltner Channels (20, 1.5 ATR)
    kc = ta.volatility.KeltnerChannel(df['High'], df['Low'], df['Close'], window=20, window_atr=20, multiplier=1.5)
    df['KC_High'] = kc.keltner_channel_hband()
    df['KC_Low'] = kc.keltner_channel_lband()
    
    # Deteksi Squeeze: Bollinger Band sepenuhnya masuk ke dalam Keltner Channel
    df['Squeeze_On'] = (df['BB_Low'] > df['KC_Low']) & (df['BB_High'] < df['KC_High'])
    
    # 2. SMC LIQUIDITY TRAP (Wyckoff Spring)
    # Cari Pivot Low (Support) dari 10 hari terakhir
    pivots = find_pivot_lows(df['Low'], left=5, right=5)
    df['Support_Level'] = pivots.ffill()
    
    last_idx = df.index[-1]
    curr = df.loc[last_idx]
    
    # Cek apakah dalam 3 hari terakhir harga menembus Support ke bawah, tapi hari ini ditutup di atas Support (Trap)
    is_trap = False
    if not pd.isna(curr['Support_Level']):
        for i in range(1, 4):
            if df['Low'].iloc[-i] < curr['Support_Level'] and df['Close'].iloc[-1] > curr['Support_Level']:
                is_trap = True
                break
                
    # 3. Bandar Uang (CMF 10 hari, karena ini Fast Swing)
    cmf = calc_chaikin_money_flow(df, period=10)
    bandar_masuk = cmf > 0
    
    # 4. Momentum (ZLSMA 14)
    zlsma = calc_zlsma(df['Close'], 14)
    zlsma_up = zlsma.iloc[-1] > zlsma.iloc[-2]
    
    last_close = float(curr['Close'])
    
    # --- LOGIKA SINYAL (SANGAT KETAT) ---
    # Sinyal menyala jika: (Squeeze Fired ATAU Liquidity Trap terjadi) DAN Bandar Masuk DAN Momentum Naik
    # Squeeze Fired = Kemarin Squeeze On, Hari ini Squeeze Off (Energi dilepas)
    squeeze_fired = df['Squeeze_On'].iloc[-2] == True and df['Squeeze_On'].iloc[-1] == False
    
    is_squeeze = squeeze_fired or df['Squeeze_On'].iloc[-1]
    
    signal = (squeeze_fired or is_trap) and bandar_masuk and zlsma_up
    
    # TP & SL untuk Kavaleri (Ketat, max 1 minggu)
    sr_zones = calculate_sr_zones(df, left=5, right=5) # Lebih sensitif (5 candle)
    
    tp_price = round(sr_zones['nearest_resistance']['center'], 0) if sr_zones['nearest_resistance'] else round(last_close * 1.06, 0)
    sl_price = round(sr_zones['nearest_support']['center'], 0) if sr_zones['nearest_support'] else round(last_close * 0.95, 0)
    
    # Risk Reward
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
        "rr": risk_reward,
    }
