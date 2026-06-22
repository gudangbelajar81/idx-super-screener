import re
import os

filepath = r"D:\PROJEK APLIKASI\IDX_SuperScreener\app\services\engines\technical_engine.py"

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add imports at the top
if "from app.services.advanced.bandarmology_engine" not in content:
    import_str = """
from app.services.advanced.bandarmology_engine import build_bandarmology
from app.services.advanced.utils import _round_price, calibrated_probability_from_score
from app.services.advanced.technical.setup_detector import detect_setup
"""
    content = content.replace("import numpy as np", "import numpy as np\n" + import_str)

# 2. Modify analyze_swing_fortress
# Replace the end of analyze_swing_fortress starting from "return {"
swing_return_pattern = re.compile(r"    return \{(.*?)\}", re.DOTALL)
swing_match = swing_return_pattern.search(content)

if swing_match and "smart_money_score" not in swing_match.group(0):
    enhancement = """
    # --- Bandarmology Engine & Probability (Advanced) ---
    df_bandar = df.copy()
    df_bandar.columns = [str(c).lower() for c in df_bandar.columns]
    if 'date' not in df_bandar.columns:
        df_bandar['date'] = df_bandar.index

    bandar_data = {}
    try:
        bandar_data = build_bandarmology(df_bandar, ticker="")
    except Exception as e:
        pass
        
    smart_money_score = bandar_data.get("smart_money_score", 0)
    verdict_bandar = bandar_data.get("verdict", "netral")
    
    # Calculate Probability
    base_score = 65 if signal else 40
    if signal and smart_money_score > 0.35:
        base_score += 15
    if signal and is_uptrend:
        base_score += 10
    win_probability = calibrated_probability_from_score(base_score)

    if tp_price: tp_price = _round_price(tp_price)
    if sl_price: sl_price = _round_price(sl_price)

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
        "rr": risk_reward
    }
"""
    content = content[:swing_match.start()] + enhancement + content[swing_match.end():]


# 3. Modify analyze_ninja_scalper
ninja_return_pattern = re.compile(r"(    return \{[^\}]+\})", re.DOTALL)
# The first match is swing, so we need to find the one after "def analyze_ninja_scalper"
ninja_idx = content.find("def analyze_ninja_scalper")
if ninja_idx != -1:
    ninja_match = ninja_return_pattern.search(content, ninja_idx)
    if ninja_match and "smart_money_score" not in ninja_match.group(0):
        enhancement_ninja = """
    # --- Bandarmology Engine & Probability (Advanced) ---
    df_bandar = df.copy()
    df_bandar.columns = [str(c).lower() for c in df_bandar.columns]
    if 'date' not in df_bandar.columns:
        df_bandar['date'] = df_bandar.index

    bandar_data = {}
    try:
        bandar_data = build_bandarmology(df_bandar, ticker="")
    except Exception:
        pass
        
    smart_money_score = bandar_data.get("smart_money_score", 0)
    verdict_bandar = bandar_data.get("verdict", "netral")
    
    base_score = 65 if final_signal else 40
    if final_signal and smart_money_score > 0.2:
        base_score += 10
    if final_signal and volume_spike_ok:
        base_score += 10
    win_probability = calibrated_probability_from_score(base_score)

    if tp_price: tp_price = _round_price(tp_price)
    if sl_price: sl_price = _round_price(sl_price)

    return {
        "signal": bool(final_signal),
        "vol_spike": round(float(vol_ratio), 1),
        "fvg_detected": bool(fvg_ok),
        "zlsma_up": bool(zlsma_up),
        "stoch_rsi": round(float(k), 1),
        "vwap_prox": round(float(vwap_prox), 3),
        "smart_money_score": round(smart_money_score, 3),
        "bandar_verdict": verdict_bandar,
        "win_probability": round(win_probability, 1),
        "tp": tp_price,
        "sl": sl_price,
        "rr": round(float(risk_reward), 2) if risk_reward else 0
    }
"""
        content = content[:ninja_match.start()] + enhancement_ninja + content[ninja_match.end():]


with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

print("Integration Phase 1 injected into technical_engine.py successfully.")
