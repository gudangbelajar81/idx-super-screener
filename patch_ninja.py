import re

with open('app/api/routes.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: get_candidates
# We need to change how it fetches candidates. For Swing/Kavaleri it's no longer used, but for Ninja it is!
old_get_candidates = r'''@router\.get\(\"/api/candidates/\{mode\}\"\)
def get_candidates\(mode: str\):.*?finally:\n        conn\.close\(\)'''

new_get_candidates = '''@router.get("/api/candidates/{mode}")
def get_candidates(mode: str):
    category_map = {"swing": "SWING", "kavaleri": "KAVALERI", "ninja": "NINJA"}
    category = category_map.get(mode.lower(), "SWING")
    
    FALLBACK = {
        "NINJA": ["BUMI.JK","BRMS.JK","BBYB.JK","ARTO.JK","GOTO.JK","BUKA.JK","VKTR.JK","WIRG.JK","WIFI.JK","DOID.JK","HRUM.JK","ESSA.JK","PSAB.JK","NCKL.JK","PGEO.JK","MBMA.JK","STRK.JK","CUAN.JK","PANI.JK","PTMP.JK"]
    }
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            if category == 'NINJA':
                cursor.execute("SELECT ticker FROM watchlists WHERE mode='scalp'")
                rows = cursor.fetchall()
                if not rows:
                    tickers = FALLBACK['NINJA']
                else:
                    tickers = [r['ticker'] for r in rows]
                
                results = []
                for t in tickers:
                    results.append({
                        "ticker": t.replace('.JK', ''),
                        "price": 0,
                        "liquidity": 0,
                        "signal": False,
                        "status": "KANDIDAT MENTAH",
                        "reason": "Menunggu Pemindaian VIP..." if rows else "Data default — Jalankan Sensus Master"
                    })
                return {"data": results, "message": "Candidates loaded"}
            else:
                return {"data": [], "message": "Not used for Swing/Position"}
    except Exception as e:
        print(f"DB Error get_candidates: {e}")
        return {"data": [], "message": "Failed"}
    finally:
        conn.close()'''

content = re.sub(old_get_candidates, new_get_candidates, content, flags=re.DOTALL)

# Fix 2: scan_ninja
old_scan_ninja = r'''@router\.get\(\"/api/scan/ninja\"\)\ndef scan_ninja\(.*?conn\.close\(\)'''

new_scan_ninja = '''@router.get("/api/scan/ninja")
def scan_ninja(premium: bool = True, x_goapi_key: str = Header(None)):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT ticker FROM watchlists WHERE mode='scalp'")
            scalp_universe = [row['ticker'] for row in cursor.fetchall()]
    finally:
        conn.close()'''

content = re.sub(old_scan_ninja, new_scan_ninja, content, flags=re.DOTALL)

with open('app/api/routes.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Patched routes.py for Ninja DB connection.')
