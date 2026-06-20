import requests

# ============================================================
#  KONFIGURASI TELEGRAM BOT
#  Isi variabel di bawah ini setelah membuat bot via @BotFather
# ============================================================
TELEGRAM_BOT_TOKEN = "8999801012:AAEvEmofo-cWWNWKEabTwA5cqENLz9jbaCU"
TELEGRAM_CHAT_ID   = "7668377537"


def send_telegram_message(text: str) -> bool:
    """
    Mengirim pesan teks ke Telegram.
    Return True jika berhasil, False jika gagal.
    """
    if TELEGRAM_BOT_TOKEN == "ISI_TOKEN_BOT_ANDA_DISINI":
        print("[Telegram] Bot belum dikonfigurasi. Lewati.")
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    
    try:
        resp = requests.post(url, json=payload, timeout=10)
        return resp.status_code == 200
    except Exception as e:
        print(f"[Telegram] Gagal kirim notifikasi: {e}")
        return False


def notify_signal(stock: dict, mode: str = "swing") -> bool:
    """
    Memformat dan mengirim notifikasi sinyal saham ke Telegram.
    
    stock: dict hasil dari api.py (berisi ticker, price, tp, sl, rr, sentiment)
    mode: 'swing' atau 'ninja'
    """
    if not stock.get("signal"):
        return False
    
    ticker = stock.get("ticker", "???")
    price  = stock.get("price", 0)
    tp     = stock.get("tp")
    sl     = stock.get("sl")
    rr     = stock.get("rr")
    sentiment = stock.get("sentiment", "NETRAL")
    cmf    = stock.get("cmf", 0)
    
    mode_icon = "🏰" if mode == "swing" else ("🐎" if mode == "kavaleri" else "🥷")
    mode_label = "SWING (Benteng)" if mode == "swing" else ("FAST SWING (Kavaleri)" if mode == "kavaleri" else "SCALP (Ninja)")
    
    sentiment_icon = "✅" if "POSITIF" in sentiment else ("⚠️" if "NEGATIF" in sentiment else "➖")
    
    tp_pct = f"+{((tp - price) / price * 100):.1f}%" if tp and price else "N/A"
    sl_pct = f"{((sl - price) / price * 100):.1f}%" if sl and price else "N/A"
    rr_text = f"{rr}x" if rr else "N/A"
    
    message = (
        f"{mode_icon} <b>SINYAL {mode_label.upper()} DITEMUKAN!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📌 Saham: <b>{ticker}</b>\n"
        f"💰 Harga: Rp {price:,.0f}\n"
        f"\n"
        f"🟢 Target Profit: Rp {tp:,.0f} ({tp_pct})\n" if tp else ""
        f"🔴 Stop Loss   : Rp {sl:,.0f} ({sl_pct})\n" if sl else ""
        f"⚖️  Risk/Reward : {rr_text}\n"
        f"\n"
        f"📰 Sentimen Berita: {sentiment_icon} {sentiment}\n"
        f"🏦 CMF (Bandar) : {cmf}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"<i>IDX Super Screener - Alpha Engine</i>"
    )
    
    return send_telegram_message(message)


def notify_macro_warning(macro_data: dict) -> bool:
    """
    Mengirim peringatan kondisi makro ke Telegram jika kondisi BAHAYA.
    """
    condition = macro_data.get("market_condition", "NETRAL")
    
    if condition not in ["BAHAYA", "WASPADA"]:
        return False
    
    score = macro_data.get("macro_score", 50)
    icon = "🚨" if condition == "BAHAYA" else "⚠️"
    
    ihsg = macro_data.get("ihsg", {})
    fx   = macro_data.get("usdidr", {})
    
    message = (
        f"{icon} <b>PERINGATAN MAKRO EKONOMI!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 Kondisi Pasar: <b>{condition}</b> (Skor: {score}/100)\n"
        f"\n"
        f"📈 IHSG: {ihsg.get('value', 'N/A')} — {ihsg.get('trend', 'N/A')}\n"
        f"💵 USD/IDR: {fx.get('value', 'N/A')} — {fx.get('trend', 'N/A')}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"<i>Harap lebih berhati-hati dalam mengambil posisi!</i>"
    )
    
    return send_telegram_message(message)
