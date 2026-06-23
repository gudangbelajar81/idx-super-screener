import os

path = 'app/worker/autopilot.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

old_block = """            cursor.execute('''
                DROP TABLE IF EXISTS idx_master;
                CREATE TABLE IF NOT EXISTS idx_master (
                    ticker VARCHAR(10) PRIMARY KEY, sector VARCHAR(50), close_price FLOAT, avg_value FLOAT, avg_volatility FLOAT,
                    relative_strength_score INT, smart_money_score INT, institutional_score INT, catalyst_score INT,
                    composite_score INT, intraday_score INT, swing_score INT,
                    smart_money_status VARCHAR(50), institutional_status VARCHAR(50), catalyst_status VARCHAR(50), trend_status VARCHAR(50), setup_type VARCHAR(50),
                    recommendation VARCHAR(20), intraday_recommendation VARCHAR(20), swing_recommendation VARCHAR(20),
                    expected_return FLOAT, target_profit FLOAT, stop_loss FLOAT, risk_reward_ratio FLOAT, edge_data TEXT,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            ''')"""

new_block = """            # Pisahkan eksekusi karena pymysql tidak support multiple statements secara default
            cursor.execute('DROP TABLE IF EXISTS idx_master')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS idx_master (
                    ticker VARCHAR(10) PRIMARY KEY, sector VARCHAR(50), close_price FLOAT, avg_value FLOAT, avg_volatility FLOAT,
                    relative_strength_score INT, smart_money_score INT, institutional_score INT, catalyst_score INT,
                    composite_score INT, intraday_score INT, swing_score INT,
                    smart_money_status VARCHAR(50), institutional_status VARCHAR(50), catalyst_status VARCHAR(50), trend_status VARCHAR(50), setup_type VARCHAR(50),
                    recommendation VARCHAR(20), intraday_recommendation VARCHAR(20), swing_recommendation VARCHAR(20),
                    expected_return FLOAT, target_profit FLOAT, stop_loss FLOAT, risk_reward_ratio FLOAT, edge_data TEXT,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            ''')"""

if "DROP TABLE IF EXISTS idx_master;" in content:
    content = content.replace(old_block, new_block)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("autopilot.py patched successfully to split SQL executions.")
else:
    print("Could not find the target block in autopilot.py")

