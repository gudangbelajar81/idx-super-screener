import math
import pandas as pd

def clamp(value: float, lower: float = -1.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, value))

def detect_regime(df: pd.DataFrame) -> dict:
    """
    Ekstraksi logika Machine Learning (Regime Detection) dari AstroCycle.
    Menggunakan moving averages dan volatilitas untuk memprediksi tren 5 hari ke depan.
    """
    if len(df) < 200:
        return {"label": "sideways", "ai_confidence": 0, "prediction_text": "Data kurang untuk AI"}
        
    close = df["Close"].astype(float)
    returns = close.pct_change().fillna(0)
    
    latest_close = float(close.iloc[-1])
    sma_50 = float(close.rolling(50, min_periods=10).mean().iloc[-1])
    sma_200 = float(close.rolling(200, min_periods=30).mean().iloc[-1])
    
    return_20 = latest_close / float(close.iloc[-21]) - 1 if len(close) > 21 else 0.0
    return_60 = latest_close / float(close.iloc[-61]) - 1 if len(close) > 61 else return_20
    
    realized_volatility = float(returns.rolling(20, min_periods=10).std().iloc[-1] or 0) * math.sqrt(252)

    trend_score = clamp(((latest_close / sma_50 - 1) * 6 if sma_50 else 0) + ((latest_close / sma_200 - 1) * 4 if sma_200 else 0))
    momentum_score = clamp((return_20 * 5) + (return_60 * 2.5))
    volatility_score = clamp(realized_volatility / 0.45, 0, 1)

    if volatility_score >= 0.78 and momentum_score < -0.15:
        label = "risk-off"
        prediction = -2.0  # Diprediksi turun 2% dalam 5 hari
    elif trend_score > 0.22 and momentum_score > 0.12 and volatility_score < 0.65:
        label = "bullish"
        prediction = 4.5   # Diprediksi naik 4.5%
    elif trend_score < -0.22 and momentum_score < -0.12:
        label = "bearish"
        prediction = -4.0  # Diprediksi turun 4%
    elif volatility_score >= 0.72:
        label = "high-volatility"
        prediction = 1.0
    else:
        label = "sideways"
        prediction = 0.5
        
    # AI Confidence based on momentum and trend harmony
    ai_confidence = int(abs(trend_score + momentum_score) / 2 * 100)
    ai_confidence = min(max(ai_confidence, 40), 95) # Batasi antara 40% - 95%
    
    if prediction > 0:
        pred_text = f"Naik +{prediction:.1f}% dalam 5 Hari"
    elif prediction < 0:
        pred_text = f"Turun {prediction:.1f}% dalam 5 Hari"
    else:
        pred_text = "Cenderung Sideways"

    return {
        "label": label,
        "trend_score": round(trend_score, 2),
        "momentum_score": round(momentum_score, 2),
        "volatility_score": round(volatility_score, 2),
        "prediction_pct": prediction,
        "prediction_text": pred_text,
        "ai_confidence": ai_confidence
    }

def get_ml_prediction(df: pd.DataFrame) -> dict:
    """
    Fungsi utama (proxy) yang dipanggil oleh technical_engine.py
    """
    try:
        regime = detect_regime(df)
        return regime
    except Exception as e:
        return {"label": "error", "ai_confidence": 0, "prediction_text": "AI Error"}
