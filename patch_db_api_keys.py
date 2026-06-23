import os
from app.core.database import get_db_connection

def create_api_keys_table():
    print("Mengecek dan membuat tabel api_keys_manager...")
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS api_keys_manager (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    provider VARCHAR(50) NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    api_key VARCHAR(255) NOT NULL UNIQUE,
                    base_url VARCHAR(255) DEFAULT '',
                    status VARCHAR(20) DEFAULT 'Alive',
                    used_count INT DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_used TIMESTAMP NULL
                )
            """)
        conn.commit()
        print("Tabel api_keys_manager berhasil dibuat/diperbarui.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    create_api_keys_table()
