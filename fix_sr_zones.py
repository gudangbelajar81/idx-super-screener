with open(r'app\services\engines\technical_engine.py', 'r', encoding='utf-8') as f:
    c = f.read()

# We look for the start of calculate_sr_zones
start_idx = c.find('def calculate_sr_zones')
if start_idx != -1:
    # Find where the advanced block starts inside it
    adv_start = c.find('    # --- Bandarmology Engine & Probability (Advanced) ---', start_idx)
    if adv_start != -1:
        # Find the end of the corrupted return block
        end_idx = c.find('    }\n', adv_start) + 6
        
        orig_return = '''    return {
        "nearest_resistance": resistance_zones[0] if resistance_zones else None,
        "nearest_support": support_zones[0] if support_zones else None,
        "all_resistance": resistance_zones[:5],  # 5 zona terdekat
        "all_support": support_zones[:5]
    }\n'''
        c = c[:adv_start] + orig_return + c[end_idx:]

with open(r'app\services\engines\technical_engine.py', 'w', encoding='utf-8') as f:
    f.write(c)
print('Fixed calculate_sr_zones')
