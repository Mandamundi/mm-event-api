import json
from pathlib import Path
from typing import Optional

EVENTS_PATH = Path(__file__).parent / "events.json"

DEFAULT_ASSETS = [
    # Equity Indices
    {"ticker": "^SPX",     "label": "S&P 500",              "category": "Equity Index"},
    {"ticker": "VI.F",     "label": "CBOE S&P 500 VIX",        "category": "Equity Index"},
    {"ticker": "^NDX",     "label": "Nasdaq 100",           "category": "Equity Index"},
    {"ticker": "^DJI",     "label": "Dow Jones",            "category": "Equity Index"},
    {"ticker": "QR.F",     "label": "Russell 2000",         "category": "Equity Index"},
    {"ticker": "^NKX",     "label": "Nikkei 225",           "category": "Equity Index"},
    {"ticker": "^KOSPI",     "label": "KOSPI Index",        "category": "Equity Index"},
    # Sector ETFs
    {"ticker": "XLE.US",      "label": "Energy",         "category": "Sector ETF"},
    {"ticker": "XLF.US",      "label": "Financials",     "category": "Sector ETF"},
    {"ticker": "XLK.US",      "label": "Technology",     "category": "Sector ETF"},
    {"ticker": "XLV.US",      "label": "Healthcare",     "category": "Sector ETF"},
    {"ticker": "XLU.US",      "label": "Utilities",      "category": "Sector ETF"},
    {"ticker": "XLI.US",      "label": "Industrials",    "category": "Sector ETF"},
    # Fixed Income
    {"ticker": "10YUSY.B",      "label": "10-Year Government Bond Yield",   "category": "Fixed Income"},
    {"ticker": "HYG.US",      "label": "High Yield Corp","category": "Fixed Income"},
    # Commodities
    {"ticker": "GC.F",     "label": "Gold",                 "category": "Commodity"},
    {"ticker": "CL.F",     "label": "WTI Crude Oil",      "category": "Commodity"},
    {"ticker": "SC.F",     "label": "Crude Oil Brent",      "category": "Commodity"},
    {"ticker": "SI.F",     "label": "Silver",               "category": "Commodity"},
    # FX
    {"ticker": "DX.F",  "label": "US Dollar Index",        "category": "FX"},
    {"ticker": "EURUSD",  "label": "EUR/USD",              "category": "FX"},
    {"ticker": "JPYUSD",  "label": "USD/JPY",              "category": "FX"},
    # Stocks
    {"ticker": "AAPL.US",  "label": "Apple",                "category": "Stock"},
    {"ticker": "MSFT.US",  "label": "Microsoft",            "category": "Stock"},
    {"ticker": "NVDA.US",  "label": "Nvidia",               "category": "Stock"},
    {"ticker": "GOOG.US",  "label": "Alphabet",             "category": "Stock"},
    {"ticker": "TSLA.US",  "label": "Tesla",                "category": "Stock"},
    {"ticker": "META.US",  "label": "Meta",                 "category": "Stock"},
    {"ticker": "TSM.US",   "label": "TSMC",                 "category": "Stock"},
    {"ticker": "PLTR.US",   "label": "Palantir",            "category": "Stock"},
    # Crypto
    {"ticker": "BTC.V", "label": "Bitcoin",  "category": "Crypto"},
    {"ticker": "ETH.V", "label": "Ethereum", "category": "Crypto"},
]

def load_events() -> dict:
    with open(EVENTS_PATH) as f:
        return json.load(f)

def get_event_by_id(event_id: str) -> Optional[dict]:
    data = load_events()
    for et in data["event_types"]:
        for ev in et["events"]:
            if ev["id"] == event_id:
                return ev
    return None