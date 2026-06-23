import re

with open('app/worker/scheduler.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_scheduler = '''import os
from apscheduler.schedulers.background import BackgroundScheduler
from app.services.engines.universe_engine import build_universe
from app.services.engines.notif_engine import send_telegram_message
from app.services.engines.paper_engine import evaluate_open_trades
from app.worker.autopilot import run_eod_autopilot
from app.core.database import get_db_connection

scheduler = BackgroundScheduler()

def scheduled_universe_build():
    print("[Scheduler] Memulai Sensus Saham Otomatis...")
    try:
        res = build_universe()
        send_telegram_message(f"🤖 <b>SENSUS OTOMATIS SELESAI</b>\\n━━━━━━━━━━━━━━━━━━━━\\nSistem telah berhasil memperbarui dan mengklasifikasikan <b>{res.get('total', 0)} saham</b> untuk minggu ini.\\n\\nMesin siap digunakan untuk *trading* besok pagi! 🚀")
    except Exception as e:
        print(f"[Scheduler] Error: {e}")

def scheduled_paper_evaluate():
    print("[Scheduler] Evaluasi Paper Trading...")
    evaluate_open_trades()

def scheduled_eod_autopilot():
    print("[Scheduler] Memulai EOD Autopilot untuk Position & Swing...")
    run_eod_autopilot()

def start_scheduler():
    scheduler.add_job(scheduled_universe_build, 'cron', day_of_week='sun', hour=23, minute=0)
    scheduler.add_job(scheduled_paper_evaluate, 'cron', day_of_week='mon-fri', hour='9-16', minute=0)
    # Autopilot dijalankan setelah bursa tutup jam 16:15 WIB
    scheduler.add_job(scheduled_eod_autopilot, 'cron', day_of_week='mon-fri', hour=16, minute=15)
    scheduler.start()
    print("[Scheduler] APScheduler aktif.")

def stop_scheduler():
    scheduler.shutdown()
'''

with open('app/worker/scheduler.py', 'w', encoding='utf-8') as f:
    f.write(new_scheduler)
print('scheduler.py patched')
