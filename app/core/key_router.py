from app.core.database import get_db_connection
from fastapi import HTTPException

class APIKeyRouter:
    def __init__(self, provider: str):
        """
        Inisialisasi Key Router menggunakan Database.
        provider: 'GoAPI', 'Gemini', 'OpenAI', 'KieAI', dll.
        """
        self.provider = provider
        
    def get_key(self):
        """
        Mengambil satu kunci aktif (Alive) dari database.
        Mencoba merotasi berdasarkan urutan terlama dipakai (last_used).
        Mengembalikan tuple (api_key, base_url).
        Jika gagal mengembalikan (None, None).
        """
        conn = get_db_connection()
        if not conn:
            return None, None
            
        try:
            with conn.cursor() as cursor:
                # Ambil 1 kunci yang statusnya Alive, diurutkan dari yang paling lama gak dipakai
                sql = """
                    SELECT id, api_key, base_url 
                    FROM api_keys_manager 
                    WHERE provider = %s AND status = 'Alive' 
                    ORDER BY last_used ASC LIMIT 1
                """
                cursor.execute(sql, (self.provider,))
                result = cursor.fetchone()
                
                if result:
                    key_id, api_key, base_url = result
                    
                    # Update used_count dan last_used
                    update_sql = """
                        UPDATE api_keys_manager 
                        SET used_count = used_count + 1, last_used = CURRENT_TIMESTAMP 
                        WHERE id = %s
                    """
                    cursor.execute(update_sql, (key_id,))
                    conn.commit()
                    
                    return api_key, base_url
                else:
                    return None, None
        except Exception as e:
            print(f"[Key Router] DB Error: {e}")
            return None, None
        finally:
            conn.close()
            
    def mark_dead(self, api_key: str):
        """
        Menandai kunci mati (Limit/Dead) di Database akibat Error 429.
        """
        if not api_key:
            return
            
        conn = get_db_connection()
        if not conn:
            return
            
        try:
            with conn.cursor() as cursor:
                # Update status menjadi Limit
                sql = "UPDATE api_keys_manager SET status = 'Limit' WHERE api_key = %s"
                cursor.execute(sql, (api_key,))
                conn.commit()
                print(f"⚠️ [Key Router] Kunci ditandai Limit: ...{api_key[-4:] if api_key else ''}")
        except Exception as e:
            print(f"[Key Router] DB Error: {e}")
        finally:
            conn.close()
            
    def has_active_keys(self):
        """
        Mengecek apakah masih ada kunci Alive untuk provider ini.
        """
        conn = get_db_connection()
        if not conn:
            return False
            
        try:
            with conn.cursor() as cursor:
                sql = "SELECT COUNT(*) as count FROM api_keys_manager WHERE provider = %s AND status = 'Alive'"
                cursor.execute(sql, (self.provider,))
                result = cursor.fetchone()
                return result and result[0] > 0
        except:
            return False
        finally:
            conn.close()
