import pymysql

try:
    conn = pymysql.connect(
        host='roundhouse.proxy.rlwy.net',
        user='root',
        password='KunciRahasiaBos88',
        database='railway',
        port=53077
    )
    with conn.cursor(pymysql.cursors.DictCursor) as cur:
        cur.execute("SELECT category, COUNT(ticker) as cnt FROM idx_universe GROUP BY category")
        rows = cur.fetchall()
        print('Universe Counts:', rows)
except Exception as e:
    print('DB Error:', e)
