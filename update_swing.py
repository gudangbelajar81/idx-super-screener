import re
with open(r'app\services\engines\technical_engine.py', 'r', encoding='utf-8') as f:
    c = f.read()

swing_idx = c.find('def analyze_swing_fortress')
return_idx = c.find('    return {', swing_idx + 100)
end_idx = c.find('    }\n', return_idx) + 6

enhancement_swing = '''
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
'''
if return_idx != -1 and end_idx != -1:
    c = c[:return_idx] + enhancement_swing + c[end_idx:]

with open(r'app\services\engines\technical_engine.py', 'w', encoding='utf-8') as f:
    f.write(c)
print('Fixed swing fortress end return')
