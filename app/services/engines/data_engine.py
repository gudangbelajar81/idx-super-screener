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

# ===========================================================================
#  FREE MODE: Yahoo Finance (Gratis, delay ~15 menit - untuk Testing)
# ===========================================================================
def _download_daily_free(tickers: list, period: str = "1y") -> Dict[str, pd.DataFrame]:
    """
    Mode Gratis: Mengunduh data harian via Yahoo Finance.
    Tidak memotong token API GoAPI. Cocok untuk testing & pengembangan.
    """
    print(f"[Data Engine - FREE/Yahoo] Mengunduh data Harian untuk {len(tickers)} saham...")
    data_dict = {}
    for ticker in tickers:
        try:
            df = reliable_yf_download(ticker, period=period, interval="1d")
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                data_dict[ticker] = df
        except Exception as e:
            print(f"[FREE] Gagal mengunduh {ticker}: {e}")
    return data_dict

def _download_intraday_free(tickers: list, interval: str = "5m", period: str = "5d") -> Dict[str, pd.DataFrame]:
    """
    Mode Gratis: Data intraday via Yahoo Finance saja. Tanpa harga real-time GoAPI.
    """
    print(f"[Data Engine - FREE/Yahoo] Mengunduh data Intraday {interval} untuk {len(tickers)} saham...")
    data_dict = {}
    for ticker in tickers:
        try:
            df = reliable_yf_download(ticker, period=period, interval=interval)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                data_dict[ticker] = df
        except Exception as e:
            print(f"[FREE] Gagal mengunduh Intraday {ticker}: {e}")
    return data_dict

# ===========================================================================
#  PREMIUM MODE: GoAPI VIP (Berbayar, data terkini - untuk Live Trading)
# ===========================================================================
def _download_daily_premium(tickers: list, period: str = "1y", goapi_key: str = None) -> Dict[str, pd.DataFrame]:
    """
    Mode Premium (VIP GoAPI): Mengunduh data harian terkini untuk saham IDX.
    MEMOTONG TOKEN API. Gunakan saat siap Live Trading.
    """
    print(f"[Data Engine - PREMIUM/GoAPI] Mengunduh data Harian untuk {len(tickers)} saham...")
    data_dict = {}
    for ticker in tickers:
        clean_ticker = ticker.replace(".JK", "") # GoAPI tidak pakai .JK
        try:
            url = f"https://api.goapi.io/stock/idx/{clean_ticker}/historical"
            headers = {"X-API-KEY": goapi_key, "Accept": "application/json"} if goapi_key else {"Accept": "application/json"}
            res = reliable_get(url, headers=headers, timeout=10)
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
            print(f"[PREMIUM] Gagal mengunduh {ticker}: {e}")
    return data_dict

def _download_intraday_premium(tickers: list, interval: str = "5m", period: str = "5d", goapi_key: str = None) -> Dict[str, pd.DataFrame]:
    """
    Mode Premium: Yahoo Finance history + Real-Time price dari GoAPI.
    MEMOTONG TOKEN API.
    """
    print(f"[Data Engine - PREMIUM/Hybrid] Mengunduh data Intraday {interval} untuk {len(tickers)} saham...")
    data_dict = {}
    for ticker in tickers:
        try:
            # 1. Ambil history base dari Yahoo
            try:
                df = reliable_yf_download(ticker, period=period, interval=interval)
            except Exception:
                df = pd.DataFrame()
                
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                
                # 2. Ambil harga absolut detik ini dari GoAPI (ini yang potong token)
                clean_ticker = ticker.replace(".JK", "")
                url = f"https://api.goapi.io/stock/idx/prices?symbols={clean_ticker}"
                headers = {"X-API-KEY": goapi_key, "Accept": "application/json"} if goapi_key else {"Accept": "application/json"}
                try:
                    res = reliable_get(url, headers=headers, timeout=5)
                except Exception:
                    res = None
                    
                if res and res.status_code == 200:
                    realtime_data = res.json()
                    if "data" in realtime_data and "results" in realtime_data["data"]:
                        rt = realtime_data["data"]["results"][0]
                        # Update candle terakhir dengan harga real-time
                        df.iloc[-1, df.columns.get_loc('Close')] = float(rt.get('close', df.iloc[-1]['Close']))
                        df.iloc[-1, df.columns.get_loc('Volume')] = float(rt.get('volume', df.iloc[-1]['Volume']))
                
                data_dict[ticker] = df
        except Exception as e:
            print(f"[PREMIUM] Gagal mengunduh Intraday {ticker}: {e}")
    return data_dict

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
