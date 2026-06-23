import os

new_routes = """
@router.get("/api/master/intraday")
def get_master_intraday():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM idx_master WHERE intraday_score > 0 ORDER BY intraday_score DESC, composite_score DESC")
            rows = cursor.fetchall()
            return {"data": rows, "message": "Berhasil mengambil data Intraday Momentum"}
    except Exception as e:
        return {"data": [], "message": str(e)}
    finally:
        conn.close()

@router.get("/api/master/swing")
def get_master_swing():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM idx_master WHERE swing_score > 0 ORDER BY swing_score DESC, composite_score DESC")
            rows = cursor.fetchall()
            return {"data": rows, "message": "Berhasil mengambil data Swing Trading"}
    except Exception as e:
        return {"data": [], "message": str(e)}
    finally:
        conn.close()
"""

with open('app/api/routes.py', 'a', encoding='utf-8') as f:
    f.write(new_routes)

print("Routes updated successfully.")
