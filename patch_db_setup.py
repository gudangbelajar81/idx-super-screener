import os
import re

path = 'app/core/db_setup.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

new_table_sql = '''            # 6. Tabel Pusat API Key
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
            
            # Seeding Data Awal'''

if 'api_keys_manager' not in content:
    content = content.replace('            # 5. Seeding Data Awal', new_table_sql)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("db_setup.py updated with api_keys_manager table.")
else:
    print("api_keys_manager already in db_setup.py")
