import pymysql

def setup_database():
    print("Menghubungkan ke MySQL XAMPP...")
    # Hubungkan ke MySQL Server tanpa menetapkan database dulu
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="",
        port=3306
    )
    
    cursor = conn.cursor()
    
    # 1. Buat Database
    print("Membuat Database 'idx_screener' jika belum ada...")
    cursor.execute("CREATE DATABASE IF NOT EXISTS idx_screener")
    
    # 2. Gunakan Database tersebut
    cursor.execute("USE idx_screener")
    
    # 3. Buat Tabel Watchlist
    print("Membuat tabel 'watchlists'...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS watchlists (
            id INT AUTO_INCREMENT PRIMARY KEY,
            ticker VARCHAR(20) NOT NULL UNIQUE,
            mode VARCHAR(20) NOT NULL
        )
    """)
    
    # 4. Kosongkan tabel (untuk reset agar tidak double)
    cursor.execute("TRUNCATE TABLE watchlists")
    
    # 5. Seeding Data Awal (Sesuai dengan config.py sebelumnya)
    print("Memasukkan data awal saham...")
    initial_data = [
        # SWING UNIVERSE
        ("BBCA.JK", "swing"), ("BBRI.JK", "swing"), ("BMRI.JK", "swing"), ("BBNI.JK", "swing"),
        ("TLKM.JK", "swing"), ("ASII.JK", "swing"), ("UNVR.JK", "swing"), ("ICBP.JK", "swing"),
        ("AMMN.JK", "swing"), ("BREN.JK", "swing"), ("PGEO.JK", "swing"), ("BRPT.JK", "swing"),
        # SCALP UNIVERSE
        ("CUAN.JK", "scalp"), ("PANI.JK", "scalp"), ("STRK.JK", "scalp"), 
        ("GOTO.JK", "scalp"), ("BRMS.JK", "scalp"), ("BUMI.JK", "scalp"), ("DOID.JK", "scalp")
    ]
    
    sql = "INSERT IGNORE INTO watchlists (ticker, mode) VALUES (%s, %s)"
    cursor.executemany(sql, initial_data)
    
    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Database berhasil disiapkan dan diisi data awal!")

if __name__ == "__main__":
    try:
        setup_database()
    except Exception as e:
        print(f"❌ Terjadi kesalahan: {e}")
        print("Pastikan XAMPP MySQL sudah menyala (Run) di Control Panel.")
