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
    close_price = stock_data.get('close_price', 0)
    smart_money = stock_data.get('smart_money_status', 'Netral')
    setup = stock_data.get('setup_type', 'Tidak Jelas')
    score = stock_data.get('composite_score', 0)
    
    # Ekstrak Probabilitas Historis
    edge_raw = stock_data.get('edge_data', '{}')
    if isinstance(edge_raw, str):
        import json
        try:
            edge = json.loads(edge_raw)
        except:
            edge = {}
    else:
        edge = edge_raw
        
    tp1 = edge.get('tp1_prob', 'N/A')
    tp3 = edge.get('tp3_prob', 'N/A')
    
    # Ekstrak Rekomendasi
    rec = stock_data.get('recommendation', 'Netral')
    
    # Prompt Engineering (Rahasia Dapur)
    prompt = f"""
    Anda adalah "Jenderal Kuantitatif & Ahli Bandarmologi Senior" yang sedang melapor ke Bos Besar (seorang fund manager elit).
    Gunakan bahasa Indonesia yang lugas, profesional, sedikit gaul (gunakan sebutan "Bos"), tanpa basa-basi, seperti seorang consigliere mafia keuangan yang sangat cerdas.
    
    Tugas: Berikan analisis komprehensif (AI X-Ray) untuk saham ini.
    
    [DATA INTELIJEN SAHAM]
    - Ticker: {ticker}
    - Harga Terakhir: Rp {close_price}
    - Skor Komposit AI: {score}/100
    - Status Rekomendasi: {rec}
    - Pergerakan Bandar (Smart Money): {smart_money}
    - Setup Teknikal: {setup}
    - Probabilitas Historis Tembus TP1 (+5%): {tp1}%
    - Probabilitas Historis Tembus TP3 (+12%): {tp3}%
    
    [FORMAT LAPORAN YANG DIMINTA]
    1. 🕵️ **Kesimpulan Intelijen**: 1-2 kalimat tajam tentang status saham ini (Layak sikat atau tinggalkan?).
    2. 🐋 **Jejak Bandarmologi**: Analisa logis kenapa status Smart Money-nya seperti itu dan apa artinya bagi pergerakan harga.
    3. 📊 **Peluang Matematis (Historical Edge)**: Jelaskan angka probabilitas di atas. Jika probabilitas TP3 di bawah 40%, peringatkan Bos bahwa ini trading cepat saja.
    4. 🛡️ **Saran Eksekusi**: Area beli (entry) ideal, dan di mana harus pasang Trailing Stop ketat.
    
    Ingat: Jangan berikan disclaimer basi seperti "ini bukan saran keuangan". Bos sudah tahu risikonya. Langsung ke intinya saja! Gunakan format Markdown (bold, list) agar mudah dibaca.
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
