import yfinance as yf
import pandas as pd
from typing import Dict
import requests
import json

GOAPI_KEY = "9801bcc5-9a0e-5762-08b8-178ad122"
GOAPI_HEADERS = {"X-API-KEY": GOAPI_KEY, "Accept": "application/json"}

def download_daily_data(tickers: list, period: str = "1y") -> Dict[str, pd.DataFrame]:
    """
    Mengunduh data harian (End of Day) menggunakan VIP GoAPI untuk saham Lokal.
    """
    print(f"[Data Engine - VIP GoAPI] Mengunduh data Harian untuk {len(tickers)} saham...")
    data_dict = {}
    for ticker in tickers:
        clean_ticker = ticker.replace(".JK", "") # GoAPI tidak pakai .JK
        try:
            url = f"https://api.goapi.io/stock/idx/{clean_ticker}/historical"
            res = requests.get(url, headers=GOAPI_HEADERS, timeout=10)
            if res.status_code == 200:
                data = res.json()
                if "data" in data and "results" in data["data"]:
                    df = pd.DataFrame(data["data"]["results"])
                    if not df.empty:
                        df['date'] = pd.to_datetime(df['date'])
                        df.set_index('date', inplace=True)
                        df.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'}, inplace=True)
                        df = df.sort_index()
                        data_dict[ticker] = df
            else:
                print(f"GoAPI Error {clean_ticker}: {res.status_code}")
        except Exception as e:
            print(f"Gagal mengunduh {ticker}: {e}")
    return data_dict

def download_intraday_data(tickers: list, interval: str = "5m", period: str = "5d") -> Dict[str, pd.DataFrame]:
    """
    Mengkombinasikan histori 5m dari Yahoo Finance dengan Real-Time Price dari GoAPI.
    """
    print(f"[Data Engine - Hybrid] Mengunduh data Intraday {interval} untuk {len(tickers)} saham...")
    data_dict = {}
    for ticker in tickers:
        try:
            # 1. Ambil history base dari Yahoo
            df = yf.download(ticker, period=period, interval=interval, progress=False)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                
                # 2. Ambil harga absolut detik ini dari GoAPI
                clean_ticker = ticker.replace(".JK", "")
                url = f"https://api.goapi.io/stock/idx/prices?symbols={clean_ticker}"
                res = requests.get(url, headers=GOAPI_HEADERS, timeout=5)
                if res.status_code == 200:
                    realtime_data = res.json()
                    if "data" in realtime_data and "results" in realtime_data["data"]:
                        rt = realtime_data["data"]["results"][0]
                        # Update candle terakhir dengan harga real-time
                        df.iloc[-1, df.columns.get_loc('Close')] = float(rt.get('close', df.iloc[-1]['Close']))
                        df.iloc[-1, df.columns.get_loc('Volume')] = float(rt.get('volume', df.iloc[-1]['Volume']))
                
                data_dict[ticker] = df
        except Exception as e:
            print(f"Gagal mengunduh Intraday {ticker}: {e}")
    return data_dict

def download_global_data(tickers: list, period: str = "1y") -> Dict[str, pd.DataFrame]:
    """
    Mengunduh data Market Global (Gold, Forex). Tetap menggunakan Yahoo Finance.
    """
    print(f"[Data Engine - Yahoo] Mengunduh data Global untuk {len(tickers)} instrumen...")
    data_dict = {}
    for ticker in tickers:
        try:
            df = yf.download(ticker, period=period, progress=False)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                data_dict[ticker] = df
        except Exception as e:
            print(f"Gagal mengunduh Global {ticker}: {e}")
    return data_dict
