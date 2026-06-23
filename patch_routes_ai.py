import os

path = 'app/api/routes.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add import for llm_engine
if 'from app.services.engines.llm_engine import generate_xray_analysis' not in content:
    content = content.replace('from app.services.engines.notif_engine import send_telegram_message', 'from app.services.engines.notif_engine import send_telegram_message\nfrom app.services.engines.llm_engine import generate_xray_analysis')

ENDPOINT = '''
@router.get("/ai/xray/{ticker}")
def get_ai_xray(ticker: str):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM idx_master WHERE ticker = %s", (ticker,))
            stock = cursor.fetchone()
            if not stock:
                return {"data": "Data saham tidak ditemukan di database Master.", "message": "Error"}
            
            # Generate AI
            xray_text = generate_xray_analysis(stock)
            return {"data": xray_text, "message": "Berhasil"}
    except Exception as e:
        return {"data": str(e), "message": "Error"}
    finally:
        conn.close()
'''

if '@router.get("/ai/xray/{ticker}")' not in content:
    content = content + '\n' + ENDPOINT

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print('routes.py updated with AI endpoint')
