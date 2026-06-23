import os
import google.generativeai as genai
from dotenv import load_dotenv
from app.core.key_router import APIKeyRouter

load_dotenv()

# Inisialisasi Key Router (Baca dari GEMINI_API_KEYS yang dipisah koma)
# Jika GEMINI_API_KEYS tidak ada, coba baca GEMINI_API_KEY (backward compatibility)
# Inisialisasi Key Router menggunakan Database
gemini_router = APIKeyRouter('Gemini')
openai_router = APIKeyRouter('OpenAI')
custom_router = APIKeyRouter('Custom')

def generate_xray_analysis(stock_data: dict) -> str:
    """
    Menghasilkan narasi analisis mendalam (X-Ray) menggunakan Google Gemini.
    Otomatis merotasi API Key jika terjadi limit/error.
    """
    if not gemini_router.has_active_keys():
        return "⚠️ **API Key Gemini belum dikonfigurasi atau semua limit habis!**\n\nSilakan tambahkan `GEMINI_API_KEYS` (bisa lebih dari satu, pisah koma) di pengaturan server (Railway/Vercel) atau file `.env` lokal Bos."

    # Ekstrak data mentah
    ticker = stock_data.get('ticker', 'UNKNOWN')
    close_price = stock_data.get('price', 0)
    
    daily = stock_data.get('daily', {})
    broker = stock_data.get('broker', {})
    news = stock_data.get('news', {})
    
    tp = daily.get('tp', 'N/A')
    sl1 = daily.get('sl', 'N/A')
    sl2 = daily.get('sl2', 'N/A')
    sl2_uji = daily.get('sl2_uji', 0)
    cmf = daily.get('cmf', 0)
    
    broker_status = broker.get('status', 'NETRAL')
    top_buyer = broker.get('top_buyer', 'N/A')
    
    news_sentiment = news.get('sentiment', 'NETRAL')
    
    # Prompt Engineering (Rahasia Dapur)
    prompt = f"""
    Anda adalah "Jenderal Kuantitatif & Ahli Bandarmologi Senior" yang sedang melapor ke Bos Besar.
    Gunakan bahasa Indonesia yang lugas, profesional, sedikit gaul (gunakan sebutan "Bos"), tanpa basa-basi.
    
    Tugas: Berikan Laporan Intelijen Trading (Trading Thesis) untuk saham {ticker}.
    
    [DATA INTELIJEN SAHAM]
    - Ticker: {ticker}
    - Harga Terakhir: Rp {close_price}
    - Arus Uang (CMF): {cmf}
    - Status Bandar: {broker_status} (Akumulator: {top_buyer})
    - Sentimen Berita: {news_sentiment}
    - Target Profit (TP): Rp {tp}
    - Stop Loss 1 (Terdekat): Rp {sl1}
    - Stop Loss 2 (Major Support): Rp {sl2} (Area ini telah diuji {sl2_uji}x)
    
    [FORMAT LAPORAN YANG DIMINTA]
    1. 🕵️ **Kesimpulan Intelijen**: 1-2 kalimat tajam tentang prospek saham ini (Apakah bagus untuk dibeli?). Kaitkan dengan sentimen berita atau akumulasi bandar.
    2. 🐋 **Jejak Bandarmologi**: Analisa logis kenapa bandar mengakumulasi/distribusi di harga ini.
    3. 🛡️ **Analisis Risiko (Risk Management)**: 
       - Jelaskan kenapa SL1 dipasang di {sl1} (sebagai batas toleransi swing trader normal).
       - Jelaskan kekuatan SL2 di {sl2}. Banggakan fakta bahwa level {sl2} sudah diuji sebanyak {sl2_uji}x sehingga ini adalah benteng pertahanan terakhir yang sangat kokoh.
    4. 🎯 **Strategi Eksekusi**: Jelaskan di harga berapa sebaiknya *entry*, di mana TP-nya, dan pastikan Bos tahu kapan harus memotong kerugian tanpa ragu.
    
    Ingat: Jangan berikan disclaimer basi seperti "ini bukan saran keuangan". Bos sudah tahu risikonya. Langsung ke intinya saja! Gunakan format Markdown (bold, bullet) agar elegan.
    """

    # Looping Rotasi API Key (Gemini)
    while gemini_router.has_active_keys():
        current_key, base_url = gemini_router.get_key()
        if not current_key:
            break
            
        try:
            genai.configure(api_key=current_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            error_msg = str(e).lower()
            if 'quota' in error_msg or '429' in error_msg or 'exhausted' in error_msg:
                print(f"[LLM Engine] Key limit tercapai. Mencoba kunci lain...")
                gemini_router.mark_dead(current_key)
            else:
                return f"❌ **Gagal menghubungi Otak AI (Gemini):** {str(e)}\n\nMungkin ada gangguan koneksi server."

    # Todo: Jika Bos memilih Provider selain Gemini, bisa diimplementasikan menggunakan openai_router
    return "❌ **Semua API Key Gemini telah mencapai limit atau belum disetel di Pusat API Key.**"
