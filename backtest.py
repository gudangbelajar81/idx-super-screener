import pandas as pd
import yfinance as yf
from app.services.engines.technical_engine import analyze_swing_fortress
import warnings
warnings.filterwarnings('ignore')

def run_historical_backtest(ticker: str, start_date: str = "2023-01-01", initial_capital: float = 10000000.0):
    print(f"\n[MARKET HISTORIAN] Memulai Ekspedisi Waktu: {ticker}")
    print(f"Modal Awal: Rp {initial_capital:,.0f} | Periode: {start_date} - Sekarang\n")
    
    # Download data
    df = yf.download(ticker, start=start_date, progress=False)
    if isinstance(df.columns, tuple) or hasattr(df.columns, 'levels'):
        df.columns = df.columns.get_level_values(0)
    df = df.rename(columns={"Open": "Open", "High": "High", "Low": "Low", "Close": "Close", "Volume": "Volume"})
    
    if len(df) < 250:
        print(f"Data {ticker} terlalu sedikit untuk sejarah jangka panjang.")
        return
        
    capital = initial_capital
    position = 0
    entry_price = 0
    tp_price = 0
    sl_price = 0
    
    win_count = 0
    loss_count = 0
    trade_log = []
    
    # Kita mulai iterasi setelah hari ke-200 (karena butuh EMA200)
    for i in range(200, len(df)):
        current_date = df.index[i]
        window_df = df.iloc[:i+1].copy()
        current_close = float(window_df['Close'].iloc[-1])
        
        # 1. Cek Posisi Berjalan
        if position > 0:
            high = float(window_df['High'].iloc[-1])
            low = float(window_df['Low'].iloc[-1])
            
            # --- Trailing Stop Logic ---
            # Jika harga naik menyentuh/melewati TP awal, jangan jual dulu, tapi naikkan SL ke Entry Price (Break Even)
            # Dan terus trailing SL setiap kali harga membuat rekor baru (selisih 3% dari puncak)
            current_peak = float(window_df['High'].iloc[window_df.index > pd.to_datetime(current_date) - pd.Timedelta(days=30)].max())
            if current_close > entry_price * 1.05:
                # Harga sudah naik 5%, kita trailing SL sejauh 3% dari pucuk
                new_sl = current_peak * 0.97
                if new_sl > sl_price:
                    sl_price = new_sl
            
            if low <= sl_price:
                # Stop Loss / Trailing Stop Tersentuh
                loss = (entry_price - sl_price) * position
                capital += (entry_price * position) - loss
                position = 0
                
                if sl_price > entry_price:
                    win_count += 1
                    trade_log.append(f"[{current_date.strftime('%Y-%m-%d')}] TRAILING STOP HIT @ {sl_price:,.0f} | Cuan: +Rp {-loss:,.0f} | Modal: Rp {capital:,.0f}")
                else:
                    loss_count += 1
                    trade_log.append(f"[{current_date.strftime('%Y-%m-%d')}] STOP LOSS @ {sl_price:,.0f} | Rugi: -Rp {loss:,.0f} | Modal: Rp {capital:,.0f}")
                continue
                
        # 2. Cari Peluang Entry (Hanya jika sedang kosong)
        if position == 0:
            result = analyze_swing_fortress(window_df)
            if result.get("signal"):
                entry_price = current_close
                tp_price = result.get("tp")
                sl_price = result.get("sl")
                
                if tp_price and sl_price and tp_price > entry_price and sl_price < entry_price:
                    # Beli dengan maksimal 20% modal
                    invest_amount = capital * 0.20
                    position = int(invest_amount / entry_price)
                    capital -= (position * entry_price)
                    trade_log.append(f"[{current_date.strftime('%Y-%m-%d')}] BUY SIGNAL @ {entry_price:,.0f} | Target: {tp_price:,.0f} | SL: {sl_price:,.0f}")

    # Rekapitulasi
    if position > 0:
        # Likuidasi posisi terakhir di harga saat ini
        final_close = float(df['Close'].iloc[-1])
        capital += position * final_close
        trade_log.append(f"[SEKARANG] LIKUIDASI SISA POSISI @ {final_close:,.0f}")
        
    total_trades = win_count + loss_count
    win_rate = (win_count / total_trades * 100) if total_trades > 0 else 0
    profit_pct = ((capital - initial_capital) / initial_capital) * 100
    
    print("\n" + "="*50)
    print("[REPORT] REKAPITULASI SEJARAH (BACKTEST RESULT)")
    print("="*50)
    for log in trade_log[-10:]: # Tampilkan 10 trade terakhir
        print(log)
    if len(trade_log) > 10:
        print(f"... dan {len(trade_log) - 10} transaksi lainnya.")
        
    print("\n" + "-"*50)
    print(f"Total Trading : {total_trades} kali")
    print(f"Win Rate      : {win_rate:.1f}%")
    print(f"Total Menang  : {win_count}")
    print(f"Total Kalah   : {loss_count}")
    print(f"Modal Akhir   : Rp {capital:,.0f} (Growth: {profit_pct:+.1f}%)")
    print("-"*50 + "\n")

if __name__ == "__main__":
    run_historical_backtest("BBCA.JK", "2023-01-01")
    run_historical_backtest("BMRI.JK", "2023-01-01")
