import re

with open('app/api/routes.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Patch get_candidates
old_get_candidates = r'''@router\.get\(\"/api/candidates/\{mode\}\"\)
def get_candidates\(mode: str\):.*?finally:\n        conn\.close\(\)'''

new_get_candidates = '''@router.get("/api/candidates/{mode}")
def get_candidates(mode: str):
    category_map = {"swing": "SWING", "kavaleri": "KAVALERI", "ninja": "NINJA"}
    category = category_map.get(mode.lower(), "SWING")
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            if category == 'NINJA':
                cursor.execute("SELECT ticker FROM watchlists WHERE mode='scalp'")
                rows = cursor.fetchall()
                if not rows:
                    return {"data": [], "message": "Daftar Pantauan Kosong. Silakan klik 'Jalankan Sensus Master' terlebih dahulu."}
                
                tickers = [r['ticker'] for r in rows]
                results = []
                for t in tickers:
                    results.append({
                        "ticker": t.replace('.JK', ''),
                        "price": 0,
                        "liquidity": 0,
                        "signal": False,
                        "status": "KANDIDAT MENTAH",
                        "reason": "Menunggu Pemindaian VIP..."
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

# 2. Patch scan_ninja
old_scan_ninja = r'''@router\.get\(\"/api/scan/ninja\"\)
def scan_ninja\(premium: bool = True, x_goapi_key: str = Header\(None\)\):
    conn = get_db_connection\(\)
    try:
        with conn\.cursor\(\) as cursor:
            cursor\.execute\(\"SELECT ticker FROM watchlists WHERE mode='scalp'\"\)
            scalp_universe = \[row\['ticker'\] for row in cursor\.fetchall\(\)\]
    finally:
        conn\.close\(\)
    
    # Fallback jika idx_universe kosong
    if not scalp_universe:
        scalp_universe = \[
            \"BUMI\.JK\",\"BRMS\.JK\",\"BBYB\.JK\",\"ARTO\.JK\",\"GOTO\.JK\",\"BUKA\.JK\",\"VKTR\.JK\",
            \"WIRG\.JK\",\"WIFI\.JK\",\"DOID\.JK\",\"HRUM\.JK\",\"ESSA\.JK\",\"NCKL\.JK\",\"PGEO\.JK\",
            \"MBMA\.JK\",\"CUAN\.JK\",\"PANI\.JK\",\"PTMP\.JK\",\"BRPT\.JK\",\"MDKA\.JK\"
        \]'''

new_scan_ninja = '''@router.get("/api/scan/ninja")
def scan_ninja(premium: bool = True, x_goapi_key: str = Header(None)):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT ticker FROM watchlists WHERE mode='scalp'")
            scalp_universe = [row['ticker'] for row in cursor.fetchall()]
    finally:
        conn.close()
        
    if not scalp_universe:
        return {"data": [], "message": "Sensus belum dijalankan. Silakan Jalankan Sensus Master terlebih dahulu."}'''

content = re.sub(old_scan_ninja, new_scan_ninja, content)

with open('app/api/routes.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Routes patched to remove dummy data.')
