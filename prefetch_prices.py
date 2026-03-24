"""
prefetch_prices.py

Run this LOCALLY whenever you want to update price data.
Reads tickers from loader.DEFAULT_ASSETS — no duplication needed.
To add or remove assets, edit DEFAULT_ASSETS in loader.py only.

Usage:
    pip install yfinance pandas pyarrow
    python prefetch_prices.py

Then commit the price_cache/ directory and push to Railway.
"""

import yfinance as yf
import pandas as pd
from pathlib import Path
import time

from loader import DEFAULT_ASSETS

CACHE_DIR = Path("price_cache")
CACHE_DIR.mkdir(exist_ok=True)

TICKERS = [asset["ticker"] for asset in DEFAULT_ASSETS]
FETCH_START = "1930-01-01"

print(f"Fetching {len(TICKERS)} tickers from loader.DEFAULT_ASSETS...\n")

ok, failed = [], []

for ticker in TICKERS:
    safe_name = ticker.replace("/", "_").replace("^", "_").replace("=", "_")
    path = CACHE_DIR / f"{safe_name}.parquet"
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
        time.sleep(0.5)
    except Exception as e:
        print(f"ERROR: {e}")
        failed.append(ticker)
        time.sleep(1)

print(f"\n✓ {len(ok)} succeeded, ✗ {len(failed)} failed")
if failed:
    print(f"Failed: {failed}")
print(f"\nCommit the price_cache/ directory to your repo.")