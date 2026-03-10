import json
from pathlib import Path
from typing import Optional

EVENTS_PATH = Path(__file__).parent / "events.json"

DEFAULT_ASSETS = [
    {"ticker": "^GSPC",  "label": "S&P 500",           "category": "Equity Index"},
    {"ticker": "^NDX",   "label": "Nasdaq 100",         "category": "Equity Index"},
    {"ticker": "^DJI",   "label": "Dow Jones",          "category": "Equity Index"},
    {"ticker": "^RUT",   "label": "Russell 2000",       "category": "Equity Index"},
    {"ticker": "^FTSE",  "label": "FTSE 100",           "category": "Equity Index"},
    {"ticker": "^N225",  "label": "Nikkei 225",         "category": "Equity Index"},
    {"ticker": "XLE",    "label": "Energy (XLE)",       "category": "Sector ETF"},
    {"ticker": "XLF",    "label": "Financials (XLF)",   "category": "Sector ETF"},
    {"ticker": "XLK",    "label": "Technology (XLK)",   "category": "Sector ETF"},
    {"ticker": "XLV",    "label": "Healthcare (XLV)",   "category": "Sector ETF"},
    {"ticker": "XLU",    "label": "Utilities (XLU)",    "category": "Sector ETF"},
    {"ticker": "XLI",    "label": "Industrials (XLI)",  "category": "Sector ETF"},
    {"ticker": "TLT",    "label": "20Y Treasury (TLT)", "category": "Fixed Income"},
    {"ticker": "IEF",    "label": "7-10Y Treasury (IEF)","category": "Fixed Income"},
    {"ticker": "HYG",    "label": "High Yield Corp (HYG)","category": "Fixed Income"},
    {"ticker": "GC=F",   "label": "Gold",               "category": "Commodity"},
    {"ticker": "CL=F",   "label": "Crude Oil (WTI)",    "category": "Commodity"},
    {"ticker": "SI=F",   "label": "Silver",             "category": "Commodity"},
    {"ticker": "DX-Y.NYB","label": "US Dollar Index",  "category": "FX"},
    {"ticker": "EURUSD=X","label": "EUR/USD",           "category": "FX"},
    {"ticker": "JPY=X",  "label": "USD/JPY",            "category": "FX"},
    {"ticker": "AAPL",   "label": "Apple",              "category": "Stock"},
    {"ticker": "MSFT",   "label": "Microsoft",          "category": "Stock"},
    {"ticker": "NVDA",   "label": "Nvidia",             "category": "Stock"},
    {"ticker": "XOM",    "label": "ExxonMobil",         "category": "Stock"},
    {"ticker": "JPM",    "label": "JPMorgan Chase",     "category": "Stock"},
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
