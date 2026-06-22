import os
from apscheduler.schedulers.background import BackgroundScheduler
from app.services.engines.universe_engine import build_universe
from app.services.engines.notif_engine import send_telegram_message
from app.services.engines.paper_engine import evaluate_open_trades
from app.services.engines.data_engine import download_intraday_data
from app.services.engines.technical_engine import analyze_ninja_scalper
from app.core.database import get_db_connection

scheduler = BackgroundScheduler()

def scheduled_universe_build():
    print("[Scheduler] Memulai Sensus Saham Otomatis...")
    try:
        res = build_universe()
        send_telegram_message(f"🤖 <b>SENSUS OTOMATIS SELESAI</b>\n━━━━━━━━━━━━━━━━━━━━\nSistem telah berhasil memperbarui dan mengklasifikasikan <b>{res.get('total', 0)} saham</b> untuk minggu ini.\n\nMesin siap digunakan untuk *trading* besok pagi! 🚀")
    except Exception as e:
        print(f"[Scheduler] Error: {e}")

def scheduled_swing_daily():
    print("[Cronjob] Memulai Radar Benteng (Harian)...")
    try:
        from app.api.routes import scan_all_swing
        res = scan_all_swing()
        signals = [s for s in res.get("data", []) if s.get("signal")]
        if signals:
            msg = "🏰 <b>REKAP BENTENG (SWING) HARI INI</b>\n━━━━━━━━━━━━━━━━━━━━\n"
            for s in signals:
                msg += f"• <b>{s['ticker']}</b> | Rp {s['price']}\n  TP: {s['tp']} | SL: {s['sl']}\n"
            send_telegram_message(msg)
    except Exception as e:
        print(f"Cronjob Swing Error: {e}")

def scheduled_kavaleri_session():
    print("[Cronjob] Memulai Radar Kavaleri (Sesi)...")
    try:
        from app.api.routes import scan_kavaleri
        res = scan_kavaleri()
        signals = [s for s in res.get("data", []) if s.get("signal")]
        if signals:
            msg = "⚡ <b>REKAP KAVALERI (SESI)</b>\n━━━━━━━━━━━━━━━━━━━━\n"
            for s in signals:
                msg += f"• <b>{s['ticker']}</b> | Rp {s['price']}\n  Fast TP: {s['tp']} | SL: {s['sl']}\n"
            send_telegram_message(msg)
    except Exception as e:
        print(f"Cronjob Kavaleri Error: {e}")

def scheduled_ninja_realtime():
    print("[Cronjob] Memulai Radar Ninja (Real-time)...")
    try:
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT ticker FROM watchlists WHERE mode='ninja' LIMIT 35")
                ninja_tickers = [row['ticker'] for row in cursor.fetchall()]
        finally:
            conn.close()
            
        if not ninja_tickers:
            return
            
        intraday_data = download_intraday_data(ninja_tickers, interval="5m", period="5d")
        for ticker, df in intraday_data.items():
            if df.empty: continue
            analysis = analyze_ninja_scalper(df)
            if analysis.get("signal"):
                last_close = df['Close'].iloc[-1]
                msg = f"🥷 <b>NINJA ALERT: {ticker.replace('.JK', '')}</b>\nVolume Spike Terdeteksi!\nHarga: Rp {last_close}\nTP: {analysis.get('tp')} | SL: {analysis.get('sl')}"
                send_telegram_message(msg)
    except Exception as e:
        print(f"Cronjob Ninja Error: {e}")

def scheduled_paper_evaluate():
    print("[Scheduler] Evaluasi Paper Trading...")
    evaluate_open_trades()

def start_scheduler():
    scheduler.add_job(scheduled_universe_build, 'cron', day_of_week='sun', hour=23, minute=0)
    scheduler.add_job(scheduled_paper_evaluate, 'cron', day_of_week='mon-fri', hour='9-16', minute=0)
    scheduler.add_job(scheduled_swing_daily, 'cron', day_of_week='mon-fri', hour=16, minute=15)
    scheduler.add_job(scheduled_kavaleri_session, 'cron', day_of_week='mon-fri', hour=11, minute=30)
    scheduler.add_job(scheduled_kavaleri_session, 'cron', day_of_week='mon-fri', hour=15, minute=30)
    scheduler.add_job(scheduled_ninja_realtime, 'cron', day_of_week='mon-fri', hour='9-15', minute='*/15')
    scheduler.start()
    print("[Scheduler] APScheduler aktif.")

def stop_scheduler():
    scheduler.shutdown()
