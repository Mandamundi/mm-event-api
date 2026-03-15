import json
from pathlib import Path
from typing import Optional

EVENTS_PATH = Path(__file__).parent / "events.json"

DEFAULT_ASSETS = [
    # Equity Indices
    {"ticker": "^GSPC",    "label": "S&P 500",                   "category": "Equity Index"},
    {"ticker": "^VIX",     "label": "VIX Volatility Index",      "category": "Equity Index"},
    {"ticker": "^NDX",     "label": "Nasdaq 100",                "category": "Equity Index"},  # was ^IXIC
    {"ticker": "^DJI",     "label": "Dow Jones",                 "category": "Equity Index"},
    {"ticker": "^RUT",     "label": "Russell 2000",              "category": "Equity Index"},
    {"ticker": "^N225",    "label": "Nikkei 225",                "category": "Equity Index"},
    # ^KS11 removed — not in cache
    # Sector ETFs
    {"ticker": "XLE",      "label": "Energy",                    "category": "Sector ETF"},
    {"ticker": "XLF",      "label": "Financials",                "category": "Sector ETF"},
    {"ticker": "XLK",      "label": "Technology",                "category": "Sector ETF"},
    {"ticker": "XLV",      "label": "Healthcare",                "category": "Sector ETF"},
    {"ticker": "XLU",      "label": "Utilities",                 "category": "Sector ETF"},
    {"ticker": "XLI",      "label": "Industrials",               "category": "Sector ETF"},
    # Fixed Income
    {"ticker": "TLT",      "label": "20Y Treasury (TLT)",        "category": "Fixed Income"},  # was ^TNX
    {"ticker": "IEF",      "label": "10Y Treasury (IEF)",        "category": "Fixed Income"},
    {"ticker": "HYG",      "label": "High Yield Corp (HYG)",     "category": "Fixed Income"},
    {"ticker": "LQD",      "label": "Corp Bonds (LQD)",          "category": "Fixed Income"},
    # Commodities
    {"ticker": "GC=F",     "label": "Gold",                      "category": "Commodity"},
    {"ticker": "CL=F",     "label": "WTI Crude Oil",             "category": "Commodity"},  # was MCL=F
    {"ticker": "SI=F",     "label": "Silver",                    "category": "Commodity"},
    {"ticker": "HG=F",     "label": "Copper",                    "category": "Commodity"},  # replaces BZ=F
    # FX
    {"ticker": "DX-Y.NYB", "label": "US Dollar Index",           "category": "FX"},
    {"ticker": "EURUSD=X", "label": "EUR/USD",                   "category": "FX"},
    {"ticker": "GBPUSD=X", "label": "GBP/USD",                   "category": "FX"},
    {"ticker": "JPY=X",    "label": "USD/JPY",                   "category": "FX"},
    # Stocks
    {"ticker": "AAPL",     "label": "Apple",                     "category": "Stock"},
    {"ticker": "MSFT",     "label": "Microsoft",                 "category": "Stock"},
    {"ticker": "NVDA",     "label": "Nvidia",                    "category": "Stock"},
    {"ticker": "GOOG",     "label": "Alphabet",                  "category": "Stock"},
    {"ticker": "TSLA",     "label": "Tesla",                     "category": "Stock"},
    {"ticker": "META",     "label": "Meta",                      "category": "Stock"},
    {"ticker": "TSM",      "label": "TSMC",                      "category": "Stock"},
    {"ticker": "PLTR",     "label": "Palantir",                  "category": "Stock"},
    # Crypto
    {"ticker": "BTC-USD",  "label": "Bitcoin",                   "category": "Crypto"},
    {"ticker": "ETH-USD",  "label": "Ethereum",                  "category": "Crypto"},
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