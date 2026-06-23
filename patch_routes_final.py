import re

with open('app/api/routes.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add clear_watchlist route at the very end
clear_route = """
@router.delete("/watchlist/all")
def clear_all_watchlist():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE idx_watchlist")
            cursor.execute("TRUNCATE TABLE idx_universe")
        conn.commit()
        return {"message": "Daftar Pantau berhasil dibersihkan!"}
    finally:
        conn.close()
"""
content = content + clear_route

with open('app/api/routes.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Patch applied to routes.py')
