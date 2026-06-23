import re

with open('app/worker/autopilot.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('from app.services.engines.notif_engine import send_telegram_message', 'from app.services.engines.notif_engine import send_telegram_message, notify_signal')

new_db_loop = '''            pos_count = 0
            for res in position_results:
                if res.get('signal'):
                    cursor.execute("""
                        INSERT INTO idx_signals (ticker, mode, price, volatility, signal_text, status, reason, tp, sl)
                        VALUES (%s, 'position', %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        res['ticker'], res['price'], res['volatility'], res['signal'],
                        res['status'], res['reason'], res['tp'], res['sl']
                    ))
                    pos_count += 1
                    try:
                        notify_signal(res, mode='position')
                    except Exception as e:
                        print(f"Gagal kirim notif telegram (Position): {e}")
            
            swing_count = 0
            for res in swing_results:
                if res.get('signal'):
                    cursor.execute("""
                        INSERT INTO idx_signals (ticker, mode, price, volatility, signal_text, status, reason, tp, sl)
                        VALUES (%s, 'swing', %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        res['ticker'], res['price'], res['volatility'], res['signal'],
                        res['status'], res['reason'], res['tp'], res['sl']
                    ))
                    swing_count += 1
                    try:
                        notify_signal(res, mode='swing')
                    except Exception as e:
                        print(f"Gagal kirim notif telegram (Swing): {e}")'''

pattern = re.compile(r'            pos_count = 0.*?swing_count \+= 1', re.DOTALL)
content = pattern.sub(new_db_loop.strip(), content)

with open('app/worker/autopilot.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Patched autopilot.py to include notify_signal.')
