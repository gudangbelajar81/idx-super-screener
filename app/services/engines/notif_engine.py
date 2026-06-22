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
    [TITAN VISUAL v3] Memformat dan mengirim notifikasi sinyal saham ke Telegram.
    Format: Premium Institutional Grade (Standar J.P. Morgan / Goldman Sachs)
    Ditambah fitur AstroCycle: Win Probability & Smart Money Score.
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
    above_vwap = stock.get("above_vwap", None)
    stoch_k = stock.get("stoch_rsi_k", None)
    
    # Field Baru Fase 1 & 2 (AstroCycle)
    smart_money_score = stock.get("smart_money_score", 0)
    bandar_verdict = stock.get("bandar_verdict", "netral")
    win_probability = stock.get("win_probability", 50.0)
    
    ai_prediction = stock.get("ai_prediction", "")
    ai_confidence = stock.get("ai_confidence", 0)
    
    # === HEADER BERDASARKAN MODE ===
    if mode == "ninja":
        mode_icon = "🥷"
        mode_label = "S C A L P I N G   A L E R T"
        accent = "⚡"
        urgency = "⏱ <b>EKSEKUSI SEGERA</b> | Time-sensitive!"
    elif mode == "kavaleri":
        mode_icon = "⚡"
        mode_label = "K A V A L E R I   A L E R T"
        accent = "🎯"
        urgency = "⚡ <b>SESI AKTIF</b> | Fast Swing Entry!"
    else:
        mode_icon = "🏰"
        mode_label = "S W I N G   S I G N A L"
        accent = "📊"
        urgency = "📅 <b>SWING TRADE</b> | Hold 3–10 Hari"
    
    # === KALKULASI PERSENTASE ===
    tp_pct = f"+{((tp - price) / price * 100):.1f}%" if tp and price else "—"
    sl_pct = f"{((sl - price) / price * 100):.1f}%" if sl and price else "—"
    rr_text = f"{rr}x" if rr else "—"
    
    # === SENTIMENT BADGE ===
    if "POSITIF" in sentiment:
        sent_badge = "🟢 BULLISH"
    elif "NEGATIF" in sentiment:
        sent_badge = "🔴 BEARISH"
    else:
        sent_badge = "⚪ NETRAL"
    
    # === CMF STRENGTH ===
    if cmf > 0.15:
        cmf_badge = "💪 Sangat Kuat"
    elif cmf > 0.05:
        cmf_badge = "✅ Kuat"
    elif cmf > 0:
        cmf_badge = "➕ Positif"
    else:
        cmf_badge = "⚠️ Lemah"
        
    # === BANDARMOLOGY (SMART MONEY) ===
    if bandar_verdict == "akumulasi":
        bandar_badge = f"🟢 Akumulasi ({smart_money_score:.2f})"
    elif bandar_verdict == "distribusi":
        bandar_badge = f"🔴 Distribusi ({smart_money_score:.2f})"
    else:
        bandar_badge = f"⚪ Netral ({smart_money_score:.2f})"
        
    # === WIN PROBABILITY ===
    prob_badge = f"🌟 {win_probability:.1f}% (Tinggi)" if win_probability >= 65 else f"⭐ {win_probability:.1f}% (Moderat)"
    
    # === AI PREDICTION ===
    ai_line = ""
    if ai_prediction:
        ai_line = f"  🤖 Prediksi 5-Hari    : <b>{ai_prediction}</b> (Akurasi: {ai_confidence}%)\n"
    
    # === VWAP STATUS ===
    vwap_line = ""
    if above_vwap is not None:
        vwap_status = "✅ Di Atas VWAP" if above_vwap else "⚠️ Di Bawah VWAP"
        vwap_line = f"  📍 VWAP         : {vwap_status}\n"
    
    # === STOCHASTIC RSI ===
    stoch_line = ""
    if stoch_k is not None:
        stoch_pct = stoch_k * 100
        if stoch_pct < 50:
            stoch_status = f"🔵 {stoch_pct:.0f}% (Ruang Naik Lebar)"
        elif stoch_pct < 80:
            stoch_status = f"🟡 {stoch_pct:.0f}% (Momentum Aktif)"
        else:
            stoch_status = f"🔶 {stoch_pct:.0f}% (Mendekati Puncak)"
        stoch_line = f"  📈 Stoch RSI    : {stoch_status}\n"
    
    # === BADAN PESAN UTAMA ===
    message = (
        f"{mode_icon} <b>{mode_label}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"  🎯 <b>{ticker}</b>  ·  Rp {price:,.0f}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"\n"
        f"{accent} <b>RENCANA TRADING</b>\n"
        f"  🟢 Target Profit : <b>Rp {tp:,.0f}</b>  ({tp_pct})\n"
        f"  🔴 Stop Loss     : <b>Rp {sl:,.0f}</b>  ({sl_pct})\n"
        f"  ⚖️  Risk / Reward : <b>{rr_text}</b>\n"
        f"\n"
        f"📡 <b>ANALISIS MESIN (ASTROCYCLE)</b>\n"
        f"  💎 Probabilitas Menang: <b>{prob_badge}</b>\n"
        f"  🐋 Aksi Bandar        : <b>{bandar_badge}</b>\n"
        f"  💰 Tekanan CMF        : {cmf_badge} ({cmf})\n"
        f"  📰 Sentimen Berita    : {sent_badge}\n"
        f"{ai_line}"
        f"{vwap_line}"
        f"{stoch_line}"
        f"\n"
        f"┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄\n"
        f"{urgency}\n"
        f"┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄\n"
        f"<i>⚠️ Bukan rekomendasi investasi. Keputusan adalah tanggung jawab pribadi.</i>\n"
        f"<i>🤖 IDX Super Screener · Titan Engine v3</i>"
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
