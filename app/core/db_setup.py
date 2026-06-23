from app.core.database import get_db_connection

def setup_database():
    print("Memeriksa struktur Database...")
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # 1. Tabel Watchlists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS watchlists (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    ticker VARCHAR(20) NOT NULL UNIQUE,
                    mode VARCHAR(20) NOT NULL
                )
            """)
            
            # 2. Tabel IDX Universe
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS idx_universe (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    ticker VARCHAR(20) NOT NULL UNIQUE,
                    category VARCHAR(50) NOT NULL,
                    avg_value BIGINT NOT NULL,
                    volatility FLOAT NOT NULL
                )
            """)
            
            # 3. Tabel Paper Trades
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS idx_paper_trades (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    ticker VARCHAR(20) NOT NULL,
                    buy_price FLOAT NOT NULL,
                    tp_price FLOAT NOT NULL,
                    sl_price FLOAT NOT NULL,
                    status VARCHAR(20) DEFAULT 'OPEN',
                    sell_price FLOAT DEFAULT NULL,
                    pnl_pct FLOAT DEFAULT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """)

            # 4. Tabel Signals (Untuk Autopilot Swing & Position)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS idx_signals (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    ticker VARCHAR(20) NOT NULL,
                    mode VARCHAR(20) NOT NULL,
                    price FLOAT NOT NULL,
                    volatility FLOAT,
                    signal_text VARCHAR(50) NOT NULL,
                    status VARCHAR(50),
                    reason TEXT,
                    tp FLOAT,
                    sl FLOAT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE KEY unique_ticker_mode (ticker, mode)
                )
            """)

            # 5. Seeding Data Awal (Hanya jika kosong/baru)
            initial_data = [
                ("BBCA.JK", "swing"), ("BBRI.JK", "swing"), ("BMRI.JK", "swing"), ("BBNI.JK", "swing"),
                ("TLKM.JK", "swing"), ("ASII.JK", "swing"), ("UNVR.JK", "swing"), ("ICBP.JK", "swing"),
                ("AMMN.JK", "swing"), ("BREN.JK", "swing"), ("PGEO.JK", "swing"), ("BRPT.JK", "swing"),
                ("CUAN.JK", "scalp"), ("PANI.JK", "scalp"), ("STRK.JK", "scalp"), 
                ("GOTO.JK", "scalp"), ("BRMS.JK", "scalp"), ("BUMI.JK", "scalp"), ("DOID.JK", "scalp")
            ]
            sql = "INSERT IGNORE INTO watchlists (ticker, mode) VALUES (%s, %s)"
            cursor.executemany(sql, initial_data)
        
        conn.commit()
        print("✅ Database siap untuk digunakan!")
    except Exception as e:
        print(f"❌ Terjadi kesalahan setup DB: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    setup_database()
