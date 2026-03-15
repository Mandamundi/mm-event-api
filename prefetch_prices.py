"""
prefetch_prices.py

Run this LOCALLY (not on Railway) whenever you want to update price data.
It downloads all tickers via yfinance and saves them as parquet files
in a price_cache/ directory that gets committed to your git repo.

Usage:
    pip install yfinance pandas pyarrow
    python prefetch_prices.py

Then commit the price_cache/ directory and push to Railway.
Railway never calls Yahoo Finance — it only reads these local files.
"""

import yfinance as yf
import pandas as pd
from pathlib import Path
import time

CACHE_DIR = Path("price_cache")
CACHE_DIR.mkdir(exist_ok=True)

# All tickers your app uses — use standard yfinance symbols
TICKERS = [
    # Equity indices
    "^GSPC",   # S&P 500
    "^NDX",    # Nasdaq 100
    "^DJI",    # Dow Jones
    "^RUT",    # Russell 2000
    "^N225",   # Nikkei 225
    "^FTSE",   # FTSE 100
    "^VIX",    # VIX
    # Sector ETFs
    "XLE", "XLF", "XLK", "XLV", "XLU", "XLI",
    # Fixed income ETFs
    "TLT", "IEF", "HYG", "LQD",
    # Commodities (futures)
    "GC=F",    # Gold
    "CL=F",    # WTI Crude
    "SI=F",    # Silver
    "HG=F",    # Copper
    # FX
    "EURUSD=X",
    "GBPUSD=X",
    "JPY=X",
    "DX-Y.NYB",  # DXY
    # Stocks
    "AAPL", "MSFT", "NVDA", "GOOG", "TSLA", "META", "TSM", "PLTR",
    # Crypto
    "BTC-USD",
    "ETH-USD",
]

FETCH_START = "1930-01-01"

print(f"Fetching {len(TICKERS)} tickers from Yahoo Finance...\n")

ok, failed = [], []

for ticker in TICKERS:
    path = CACHE_DIR / f"{ticker.replace('/', '_').replace('^', '_').replace('=', '_')}.parquet"
    print(f"  {ticker:<15} ", end="", flush=True)
    try:
        df = yf.download(ticker, start=FETCH_START, auto_adjust=True, progress=False)
        if df.empty:
            print("EMPTY")
            failed.append(ticker)
            continue
        series = df["Close"]
        if isinstance(series, pd.DataFrame):
            series = series.squeeze()
        series.index = pd.to_datetime(series.index).normalize()
        series = series.dropna()
        series.to_frame("Close").to_parquet(path)
        print(f"OK  ({len(series)} days, {series.index[0].date()} → {series.index[-1].date()})")
        ok.append(ticker)
        time.sleep(0.5)  # gentle rate limiting
    except Exception as e:
        print(f"ERROR: {e}")
        failed.append(ticker)
        time.sleep(1)

print(f"\n✓ {len(ok)} succeeded, ✗ {len(failed)} failed")
if failed:
    print(f"Failed: {failed}")
print(f"\nCommit the price_cache/ directory to your repo.")