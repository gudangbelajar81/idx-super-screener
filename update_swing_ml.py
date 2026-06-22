import re

with open(r'app\services\engines\technical_engine.py', 'r', encoding='utf-8') as f:
    c = f.read()

# Add import at the top
if 'from app.services.advanced.ml_proxy import get_ml_prediction' not in c:
    import_idx = c.find('import numpy as np\n')
    if import_idx != -1:
        c = c[:import_idx+19] + 'from app.services.advanced.ml_proxy import get_ml_prediction\n' + c[import_idx+19:]

# Insert ML prediction into analyze_swing_fortress
swing_idx = c.find('def analyze_swing_fortress')
if swing_idx != -1:
    return_idx = c.find('    return {', swing_idx + 100)
    
    ml_code = '''
    # --- AI Prediction (AstroCycle Machine Learning Proxy) ---
    ai_data = get_ml_prediction(df)
    ai_text = ai_data.get("prediction_text", "Tidak ada data")
    ai_confidence = ai_data.get("ai_confidence", 0)
    
'''
    if return_idx != -1 and 'ai_data =' not in c[swing_idx:return_idx]:
        c = c[:return_idx] + ml_code + c[return_idx:]
        
    # Update the return block to include ml fields
    end_idx = c.find('    }\n', return_idx)
    if end_idx != -1 and '"ai_prediction"' not in c[return_idx:end_idx]:
        c = c[:end_idx] + '        "ai_prediction": ai_text,\n        "ai_confidence": ai_confidence\n' + c[end_idx:]

with open(r'app\services\engines\technical_engine.py', 'w', encoding='utf-8') as f:
    f.write(c)
    
print("Integrated ML Prediction into Swing Fortress")
