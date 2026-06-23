import pymysql

try:
    conn = pymysql.connect(
        host='roundhouse.proxy.rlwy.net',
        user='root',
        password='KunciRahasiaBos88',
        database='railway',
        port=53077
    )
    with conn.cursor() as cur:
        # Drop old tables
        cur.execute("DROP TABLE IF EXISTS idx_signals")
        cur.execute("DROP TABLE IF EXISTS idx_universe")
        cur.execute("DROP TABLE IF EXISTS watchlists") # Just in case

        # Create Master Table
        cur.execute("""
            CREATE TABLE idx_master (
                ticker VARCHAR(10) PRIMARY KEY,
                sector VARCHAR(50),
                
                # Raw Data
                close_price FLOAT,
                avg_value FLOAT,
                avg_volatility FLOAT,
                
                # Component Scores (0-100)
                relative_strength_score INT,
                smart_money_score INT,
                institutional_score INT,
                catalyst_score INT,
                
                # Final Scores (0-100)
                composite_score INT,
                intraday_score INT,
                swing_score INT,
                
                # Status & Attributes
                smart_money_status VARCHAR(50),
                institutional_status VARCHAR(50),
                catalyst_status VARCHAR(50),
                trend_status VARCHAR(50),
                setup_type VARCHAR(50),
                
                # Recommendations
                recommendation VARCHAR(20), # Strong Buy, Buy, Watchlist, Avoid
                intraday_recommendation VARCHAR(20),
                swing_recommendation VARCHAR(20),
                
                # Projections
                expected_return FLOAT,
                target_profit FLOAT,
                stop_loss FLOAT,
                risk_reward_ratio FLOAT,
                
                # Metadata
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        print("Database schema successfully rebuilt to idx_master!")
    conn.commit()
except Exception as e:
    print('DB Error:', e)
