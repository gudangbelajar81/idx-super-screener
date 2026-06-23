import os

path = 'app/api/routes.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

api_keys_routes = '''
from pydantic import BaseModel
from app.core.database import get_db_connection

class APIKeyItem(BaseModel):
    provider: str
    name: str
    api_key: str
    base_url: str = ""

@router.get("/api/keys")
def get_api_keys():
    """Mengambil semua API Keys dari database"""
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database Error")
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, provider, name, api_key, base_url, status, used_count FROM api_keys_manager ORDER BY id DESC")
            results = cursor.fetchall()
            keys = []
            for r in results:
                # Sembunyikan sebagian key untuk keamanan UI
                masked_key = r[3][:6] + "..." + r[3][-4:] if len(r[3]) > 10 else "***"
                keys.append({
                    "id": r[0],
                    "provider": r[1],
                    "name": r[2],
                    "api_key_masked": masked_key,
                    "base_url": r[4],
                    "status": r[5],
                    "used_count": r[6]
                })
            return {"status": "success", "data": keys}
    finally:
        conn.close()

@router.post("/api/keys")
def add_api_key(item: APIKeyItem):
    """Menambahkan API Key baru"""
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database Error")
    try:
        with conn.cursor() as cursor:
            sql = "INSERT INTO api_keys_manager (provider, name, api_key, base_url) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (item.provider, item.name, item.api_key, item.base_url))
            conn.commit()
            return {"status": "success", "message": "API Key berhasil ditambahkan"}
    except Exception as e:
        if 'Duplicate' in str(e):
            raise HTTPException(status_code=400, detail="API Key sudah terdaftar")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@router.delete("/api/keys/{key_id}")
def delete_api_key(key_id: int):
    """Menghapus API Key"""
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database Error")
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM api_keys_manager WHERE id = %s", (key_id,))
            conn.commit()
            return {"status": "success", "message": "API Key dihapus"}
    finally:
        conn.close()

@router.put("/api/keys/{key_id}/reset")
def reset_api_key_status(key_id: int):
    """Mereset status API Key menjadi Alive"""
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database Error")
    try:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE api_keys_manager SET status = 'Alive' WHERE id = %s", (key_id,))
            conn.commit()
            return {"status": "success"}
    finally:
        conn.close()
'''

if '@router.get("/api/keys")' not in content:
    content = content + '\n' + api_keys_routes
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("routes.py patched with API Keys CRUD endpoints.")
else:
    print("routes.py already has API Keys CRUD endpoints.")
