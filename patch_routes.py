import re
with open('app/api/routes.py', 'r', encoding='utf-8') as f:
    content = f.read()

# We need to replace scan_swing
swing_pattern = re.compile(r'@router\.get\(\"/api/scan/swing\"\).*?(?=@router\.get\(\"/api/scan/kavaleri\"\))', re.DOTALL)
new_swing = '''@router.get("/api/scan/swing")
def scan_swing(premium: bool = True, x_goapi_key: str = Header(None)):
    """Mode Position: Mengambil hasil EOD Autopilot dari database"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM idx_signals WHERE mode='position'")
            signals = cursor.fetchall()
            
            # Format to match frontend expectations
            results = []
            for s in signals:
                results.append({
                    'ticker': s['ticker'],
                    'price': s['price'],
                    'volatility': s['volatility'],
                    'signal': s['signal_text'],
                    'status': s['status'],
                    'reason': s['reason'],
                    'tp': s['tp'],
                    'sl': s['sl']
                })
            return {"data": results, "message": "Fetched from Autopilot Database"}
    except Exception as e:
        print(f"DB Fetch Error (Position): {e}")
        return {"data": [], "message": "Failed to fetch Autopilot data"}
    finally:
        conn.close()

'''

content = swing_pattern.sub(new_swing, content)

kavaleri_pattern = re.compile(r'@router\.get\(\"/api/scan/kavaleri\"\).*?(?=@router\.get\(\"/api/scan/ninja\"\))', re.DOTALL)
new_kavaleri = '''@router.get("/api/scan/kavaleri")
def scan_kavaleri(premium: bool = True, x_goapi_key: str = Header(None)):
    """Mode Swing: Mengambil hasil EOD Autopilot dari database"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM idx_signals WHERE mode='swing'")
            signals = cursor.fetchall()
            
            # Format to match frontend expectations
            results = []
            for s in signals:
                results.append({
                    'ticker': s['ticker'],
                    'price': s['price'],
                    'volatility': s['volatility'],
                    'signal': s['signal_text'],
                    'status': s['status'],
                    'reason': s['reason'],
                    'tp': s['tp'],
                    'sl': s['sl']
                })
            return {"data": results, "message": "Fetched from Autopilot Database"}
    except Exception as e:
        print(f"DB Fetch Error (Swing): {e}")
        return {"data": [], "message": "Failed to fetch Autopilot data"}
    finally:
        conn.close()

'''

content = kavaleri_pattern.sub(new_kavaleri, content)

with open('app/api/routes.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Routes patched successfully.')
