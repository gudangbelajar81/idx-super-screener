import yfinance as yf
import pandas as pd
from typing import Dict
import requests
import json
from tenacity import retry, stop_after_attempt, wait_exponential

import os

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def reliable_get(url, headers, timeout):
    res = requests.get(url, headers=headers, timeout=timeout)
    res.raise_for_status()
    return res

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def reliable_yf_download(ticker, period, interval="1d", threads=False):
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5'
    })
    df = yf.download(ticker, period=period, interval=interval, threads=threads, session=session, progress=False)
    if df is None or df.empty:
        raise ValueError(f"Empty data from Yahoo Finance for {ticker}")
    return df

from cachetools import TTLCache, cached

# Cache untuk menyimpan hasil history Yahoo Finance selama 15 menit
yf_history_cache = TTLCache(maxsize=20, ttl=900)

@cached(cache=yf_history_cache)
def _get_bulk_yf_history(tickers_tuple, period, interval):
    tickers = list(tickers_tuple)
    print(f"[Bulk Fetch] Mendownload history {len(tickers)} saham (period={period}, interval={interval}) via Yahoo...")
    try:
        data = yf.download(tickers, period=period, interval=interval, threads=True, progress=False)
    except Exception as e:
        print(f"Gagal bulk download YF: {e}")
        return {}
        
    data_dict = {}
    for ticker in tickers:
        try:
            if len(tickers) == 1:
                df = data.dropna()
            else:
                df = pd.DataFrame({
                    'Open': data['Open'][ticker],
                    'High': data['High'][ticker],
                    'Low': data['Low'][ticker],
                    'Close': data['Close'][ticker],
                    'Volume': data['Volume'][ticker]
                }).dropna()
            if not df.empty:
                data_dict[ticker] = df
        except Exception:
            pass
    return data_dict

def _apply_goapi_bulk_prices(data_dict, goapi_key):
    tickers = list(data_dict.keys())
    chunk_size = 50
    print(f"[Bulk API] Menarik harga Real-Time untuk {len(tickers)} saham dari GoAPI...")
    
    for i in range(0, len(tickers), chunk_size):
        chunk = tickers[i:i + chunk_size]
        symbols = ",".join([t.replace(".JK", "") for t in chunk])
        url = f"https://api.goapi.io/stock/idx/prices?symbols={symbols}"
        headers = {"X-API-KEY": goapi_key, "Accept": "application/json"} if goapi_key else {"Accept": "application/json"}
        
        try:
            res = reliable_get(url, headers=headers, timeout=10)
            if res.status_code == 200:
                results = res.json().get("data", {}).get("results", [])
                for rt in results:
                    clean_ticker = rt.get("symbol")
                    ticker = clean_ticker + ".JK"
                    if ticker in data_dict:
                        df = data_dict[ticker]
                        df.iloc[-1, df.columns.get_loc('Close')] = float(rt.get('close', df.iloc[-1]['Close']))
                        df.iloc[-1, df.columns.get_loc('Volume')] = float(rt.get('volume', df.iloc[-1]['Volume']))
        except Exception as e:
            print(f"GoAPI Bulk Error chunk {i}: {e}")
    return data_dict

# ===========================================================================
#  FREE MODE: Yahoo Finance (Gratis, delay ~15 menit)
# ===========================================================================
def _download_daily_free(tickers: list, period: str = "1y") -> Dict[str, pd.DataFrame]:
    return _get_bulk_yf_history(tuple(sorted(tickers)), period, "1d")

def _download_intraday_free(tickers: list, interval: str = "5m", period: str = "5d") -> Dict[str, pd.DataFrame]:
    return _get_bulk_yf_history(tuple(sorted(tickers)), period, interval)

# ===========================================================================
#  PREMIUM MODE: Bulk Hybrid (YF History + GoAPI Realtime Bulk)
# ===========================================================================
def _download_daily_premium(tickers: list, period: str = "1y", goapi_key: str = None) -> Dict[str, pd.DataFrame]:
    data_dict = _get_bulk_yf_history(tuple(sorted(tickers)), period, "1d")
    return _apply_goapi_bulk_prices(data_dict.copy(), goapi_key)

def _download_intraday_premium(tickers: list, interval: str = "5m", period: str = "5d", goapi_key: str = None) -> Dict[str, pd.DataFrame]:
    data_dict = _get_bulk_yf_history(tuple(sorted(tickers)), period, interval)
    return _apply_goapi_bulk_prices(data_dict.copy(), goapi_key)

# ===========================================================================
#  GATEWAY UTAMA: Fungsi Publik dengan Saklar use_premium
# ===========================================================================
def download_daily_data(tickers: list, period: str = "1y", use_premium: bool = True, goapi_key: str = None) -> Dict[str, pd.DataFrame]:
    """
    Gateway utama untuk data harian.
    - use_premium=True  -> GoAPI VIP (potong token, data akurat)
    - use_premium=False -> Yahoo Finance (gratis, delay ~15 menit)
    """
    if use_premium:
        return _download_daily_premium(tickers, period, goapi_key)
    else:
        return _download_daily_free(tickers, period)

def download_intraday_data(tickers: list, interval: str = "5m", period: str = "5d", use_premium: bool = True, goapi_key: str = None) -> Dict[str, pd.DataFrame]:
    """
    Gateway utama untuk data intraday.
    - use_premium=True  -> Hybrid (Yahoo history + GoAPI realtime, potong token)
    - use_premium=False -> Yahoo Finance saja (gratis)
    """
    if use_premium:
        return _download_intraday_premium(tickers, interval, period, goapi_key)
    else:
        return _download_intraday_free(tickers, interval, period)

def download_global_data(tickers: list, period: str = "1y") -> Dict[str, pd.DataFrame]:
    """
    Mengunduh data Market Global (Gold, Forex). Selalu menggunakan Yahoo Finance (Gratis).
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
