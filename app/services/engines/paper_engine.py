import pymysql
import os
import yfinance as yf

def get_db_connection():
    return pymysql.connect(
        host=os.environ.get("MYSQLHOST", "localhost"),
        user=os.environ.get("MYSQLUSER", "root"),
        password=os.environ.get("MYSQLPASSWORD", ""),
        database=os.environ.get("MYSQLDATABASE", "idx_screener"),
        port=int(os.environ.get("MYSQLPORT", 3306)),
        cursorclass=pymysql.cursors.DictCursor
    )

def record_paper_trade(ticker: str, buy_price: float, tp_price: float, sl_price: float):
    """Mencatat pembelian virtual baru saat sinyal muncul."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Cek apakah sudah ada open posisi untuk saham ini
            cursor.execute("SELECT id FROM idx_paper_trades WHERE ticker = %s AND status = 'OPEN'", (ticker,))
            if cursor.fetchone():
                return False # Jangan beli lagi jika masih ada posisi open
                
            sql = "INSERT INTO idx_paper_trades (ticker, buy_price, tp_price, sl_price) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (ticker, buy_price, tp_price, sl_price))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error recording paper trade: {e}")
        return False
    finally:
        conn.close()

def get_paper_portfolio():
    """Mengambil riwayat paper trading."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM idx_paper_trades ORDER BY id DESC LIMIT 50")
            rows = cursor.fetchall()
            return rows
    finally:
        conn.close()

def evaluate_open_trades():
    """
    Tugas background: Cek harga terakhir untuk posisi OPEN.
    Jika kena TP -> WIN, jika kena SL -> LOSS.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM idx_paper_trades WHERE status = 'OPEN'")
            open_trades = cursor.fetchall()
            
            if not open_trades:
                return
                
            tickers = [f"{t['ticker']}.JK" for t in open_trades]
            data = yf.download(tickers, period="1d", progress=False)
            
            for trade in open_trades:
                ticker_jk = f"{trade['ticker']}.JK"
                try:
                    # Ambil harga terakhir
                    if len(tickers) == 1:
                        last_price = float(data['Close'].iloc[-1])
                        high = float(data['High'].iloc[-1])
                        low = float(data['Low'].iloc[-1])
                    else:
                        last_price = float(data['Close'][ticker_jk].iloc[-1])
                        high = float(data['High'][ticker_jk].iloc[-1])
                        low = float(data['Low'][ticker_jk].iloc[-1])
                        
                    status = 'OPEN'
                    sell_price = None
                    
                    if high >= trade['tp_price']:
                        status = 'WIN'
                        sell_price = trade['tp_price']
                    elif low <= trade['sl_price']:
                        status = 'LOSS'
                        sell_price = trade['sl_price']
                        
                    if status != 'OPEN':
                        pnl_pct = ((sell_price - trade['buy_price']) / trade['buy_price']) * 100
                        cursor.execute(
                            "UPDATE idx_paper_trades SET status=%s, sell_price=%s, pnl_pct=%s WHERE id=%s",
                            (status, sell_price, pnl_pct, trade['id'])
                        )
                except Exception as e:
                    print(f"Error evaluating {trade['ticker']}: {e}")
                    
        conn.commit()
    except Exception as e:
        print(f"Error evaluating open trades: {e}")
    finally:
        conn.close()
