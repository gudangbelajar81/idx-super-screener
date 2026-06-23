import os

path = 'app/services/engines/llm_engine.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

old_block = '''raw_keys = os.getenv("GEMINI_API_KEYS", os.getenv("GEMINI_API_KEY", ""))
gemini_router = APIKeyRouter(raw_keys)'''
new_block = '''# Inisialisasi Key Router menggunakan Database
gemini_router = APIKeyRouter('Gemini')
openai_router = APIKeyRouter('OpenAI')
custom_router = APIKeyRouter('Custom')'''

content = content.replace(old_block, new_block)

old_loop = '''    # Looping Rotasi API Key
    while gemini_router.has_active_keys():
        current_key = gemini_router.get_key()
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
                return f"❌ **Gagal menghubungi Otak AI (Gemini):** {str(e)}\\n\\nMungkin ada gangguan koneksi server."

    return "❌ **Semua API Key Gemini telah mencapai limit (Habis Kuota).** Silakan tambahkan kunci baru di konfigurasi server."'''

new_loop = '''    # Looping Rotasi API Key (Gemini)
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
                return f"❌ **Gagal menghubungi Otak AI (Gemini):** {str(e)}\\n\\nMungkin ada gangguan koneksi server."

    # Todo: Jika Bos memilih Provider selain Gemini, bisa diimplementasikan menggunakan openai_router
    return "❌ **Semua API Key Gemini telah mencapai limit atau belum disetel di Pusat API Key.**"'''

content = content.replace(old_loop, new_loop)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("llm_engine.py patched with new DB Router")
