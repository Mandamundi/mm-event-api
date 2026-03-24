import json
from pathlib import Path
from typing import Optional

EVENTS_PATH = Path(__file__).parent / "events.json"

DEFAULT_ASSETS = [
    # ── Equity Indices (22) ────────────────────────────────────────────────
    {"ticker": "^GSPC",      "label": "S&P 500",                      "category": "Equity Index"},
    {"ticker": "^VIX",       "label": "VIX Volatility Index",         "category": "Equity Index"},
    {"ticker": "^NDX",       "label": "Nasdaq 100",                   "category": "Equity Index"},
    {"ticker": "^DJI",       "label": "Dow Jones",                    "category": "Equity Index"},
    {"ticker": "^RUT",       "label": "Russell 2000",                 "category": "Equity Index"},
    {"ticker": "^MID",       "label": "S&P 400 MidCap",               "category": "Equity Index"},
    {"ticker": "^NYA",       "label": "NYSE Composite",               "category": "Equity Index"},
    {"ticker": "^FTSE",      "label": "FTSE 100",                     "category": "Equity Index"},
    {"ticker": "^GDAXI",     "label": "DAX",                          "category": "Equity Index"},
    {"ticker": "^FCHI",      "label": "CAC 40",                       "category": "Equity Index"},
    {"ticker": "^STOXX50E",  "label": "Euro Stoxx 50",                "category": "Equity Index"},
    {"ticker": "^GSPTSE",    "label": "S&P/TSX Composite",            "category": "Equity Index"},
    {"ticker": "^MXX",       "label": "IPC Mexico",                   "category": "Equity Index"},
    {"ticker": "^N225",      "label": "Nikkei 225",                   "category": "Equity Index"},
    {"ticker": "^HSI",       "label": "Hang Seng",                    "category": "Equity Index"},
    {"ticker": "000001.SS",  "label": "Shanghai Composite",           "category": "Equity Index"},
    {"ticker": "^TWII",      "label": "Taiwan Weighted Index",        "category": "Equity Index"},
    {"ticker": "^KS11",      "label": "KOSPI Composite",              "category": "Equity Index"},
    {"ticker": "^AXJO",      "label": "ASX 200",                      "category": "Equity Index"},
    {"ticker": "^NSEI",      "label": "Nifty 50",                     "category": "Equity Index"},
    {"ticker": "^BSESN",     "label": "S&P BSE SENSEX",               "category": "Equity Index"},
    {"ticker": "^BVSP",      "label": "Bovespa (Brazil)",             "category": "Equity Index"},

    # ── Sector ETFs (18) ───────────────────────────────────────────────────
    {"ticker": "XLE",        "label": "Energy",                       "category": "Sector ETF"},
    {"ticker": "XLF",        "label": "Financials",                   "category": "Sector ETF"},
    {"ticker": "XLK",        "label": "Technology",                   "category": "Sector ETF"},
    {"ticker": "XLV",        "label": "Healthcare",                   "category": "Sector ETF"},
    {"ticker": "XLU",        "label": "Utilities",                    "category": "Sector ETF"},
    {"ticker": "XLI",        "label": "Industrials",                  "category": "Sector ETF"},
    {"ticker": "XLB",        "label": "Materials",                    "category": "Sector ETF"},
    {"ticker": "XLC",        "label": "Communication Services",       "category": "Sector ETF"},
    {"ticker": "XLP",        "label": "Consumer Staples",             "category": "Sector ETF"},
    {"ticker": "XLY",        "label": "Consumer Discretionary",       "category": "Sector ETF"},
    {"ticker": "XLRE",       "label": "Real Estate",                  "category": "Sector ETF"},
    {"ticker": "SMH",        "label": "Semiconductors (SMH)",         "category": "Sector ETF"},
    {"ticker": "IBB",        "label": "Biotech (IBB)",                "category": "Sector ETF"},
    {"ticker": "KRE",        "label": "Regional Banks (KRE)",         "category": "Sector ETF"},
    {"ticker": "GDX",        "label": "Gold Miners (GDX)",            "category": "Sector ETF"},
    {"ticker": "ARKK",       "label": "ARK Innovation",               "category": "Sector ETF"},
    {"ticker": "ICLN",       "label": "Clean Energy (ICLN)",          "category": "Sector ETF"},
    {"ticker": "JETS",       "label": "Airlines (JETS)",              "category": "Sector ETF"},

    # ── Broad Market ETFs (14) ─────────────────────────────────────────────
    {"ticker": "SPY",        "label": "S&P 500 ETF (SPY)",            "category": "Broad ETF"},
    {"ticker": "QQQ",        "label": "Nasdaq 100 ETF (QQQ)",         "category": "Broad ETF"},
    {"ticker": "IWM",        "label": "Russell 2000 ETF (IWM)",       "category": "Broad ETF"},
    {"ticker": "DIA",        "label": "Dow Jones ETF (DIA)",          "category": "Broad ETF"},
    {"ticker": "VOO",        "label": "Vanguard S&P 500 (VOO)",       "category": "Broad ETF"},
    {"ticker": "VTI",        "label": "US Total Market (VTI)",        "category": "Broad ETF"},
    {"ticker": "EEM",        "label": "Emerging Markets (EEM)",       "category": "Broad ETF"},
    {"ticker": "EFA",        "label": "MSCI EAFE (EFA)",              "category": "Broad ETF"},
    {"ticker": "IEMG",       "label": "Core Emerging Markets (IEMG)", "category": "Broad ETF"},
    {"ticker": "KWEB",       "label": "China Internet (KWEB)",        "category": "Broad ETF"},
    {"ticker": "GLD",        "label": "Gold ETF (GLD)",               "category": "Broad ETF"},
    {"ticker": "SLV",        "label": "Silver ETF (SLV)",             "category": "Broad ETF"},
    {"ticker": "USO",        "label": "Oil ETF (USO)",                "category": "Broad ETF"},
    {"ticker": "IBIT",       "label": "Bitcoin ETF (IBIT)",           "category": "Broad ETF"},

    # ── Fixed Income (11) ──────────────────────────────────────────────────
    {"ticker": "TLT",        "label": "20Y Treasury (TLT)",           "category": "Fixed Income"},
    {"ticker": "IEF",        "label": "10Y Treasury (IEF)",           "category": "Fixed Income"},
    {"ticker": "IEI",        "label": "3-7Y Treasury (IEI)",          "category": "Fixed Income"},
    {"ticker": "SHY",        "label": "1-3Y Treasury (SHY)",          "category": "Fixed Income"},
    {"ticker": "TIP",        "label": "TIPS (TIP)",                   "category": "Fixed Income"},
    {"ticker": "AGG",        "label": "US Agg Bond (AGG)",            "category": "Fixed Income"},
    {"ticker": "BND",        "label": "Total Bond Market (BND)",      "category": "Fixed Income"},
    {"ticker": "HYG",        "label": "High Yield Corp (HYG)",        "category": "Fixed Income"},
    {"ticker": "LQD",        "label": "Corp Bonds (LQD)",             "category": "Fixed Income"},
    {"ticker": "EMB",        "label": "EM Bonds (EMB)",               "category": "Fixed Income"},
    {"ticker": "MUB",        "label": "Municipal Bonds (MUB)",        "category": "Fixed Income"},

    # ── Commodities (15) ───────────────────────────────────────────────────
    {"ticker": "GC=F",       "label": "Gold",                         "category": "Commodity"},
    {"ticker": "SI=F",       "label": "Silver",                       "category": "Commodity"},
    {"ticker": "PL=F",       "label": "Platinum",                     "category": "Commodity"},
    {"ticker": "PA=F",       "label": "Palladium",                    "category": "Commodity"},
    {"ticker": "HG=F",       "label": "Copper",                       "category": "Commodity"},
    {"ticker": "CL=F",       "label": "WTI Crude Oil",                "category": "Commodity"},
    {"ticker": "BZ=F",       "label": "Brent Crude Oil",              "category": "Commodity"},
    {"ticker": "NG=F",       "label": "Natural Gas",                  "category": "Commodity"},
    {"ticker": "ZC=F",       "label": "Corn",                         "category": "Commodity"},
    {"ticker": "ZW=F",       "label": "Wheat",                        "category": "Commodity"},
    {"ticker": "ZS=F",       "label": "Soybeans",                     "category": "Commodity"},
    {"ticker": "KC=F",       "label": "Coffee",                       "category": "Commodity"},
    {"ticker": "CT=F",       "label": "Cotton",                       "category": "Commodity"},
    {"ticker": "SB=F",       "label": "Sugar",                        "category": "Commodity"},
    {"ticker": "LBS=F",      "label": "Lumber",                       "category": "Commodity"},

    # ── FX (16) ────────────────────────────────────────────────────────────
    {"ticker": "DX-Y.NYB",   "label": "US Dollar Index",              "category": "FX"},
    {"ticker": "EURUSD=X",   "label": "EUR/USD",                      "category": "FX"},
    {"ticker": "GBPUSD=X",   "label": "GBP/USD",                      "category": "FX"},
    {"ticker": "JPY=X",      "label": "USD/JPY",                      "category": "FX"},
    {"ticker": "AUDUSD=X",   "label": "AUD/USD",                      "category": "FX"},
    {"ticker": "NZDUSD=X",   "label": "NZD/USD",                      "category": "FX"},
    {"ticker": "USDCAD=X",   "label": "USD/CAD",                      "category": "FX"},
    {"ticker": "USDCHF=X",   "label": "USD/CHF",                      "category": "FX"},
    {"ticker": "USDCNY=X",   "label": "USD/CNY",                      "category": "FX"},
    {"ticker": "USDINR=X",   "label": "USD/INR",                      "category": "FX"},
    {"ticker": "USDKRW=X",   "label": "USD/KRW",                      "category": "FX"},
    {"ticker": "USDSGD=X",   "label": "USD/SGD",                      "category": "FX"},
    {"ticker": "TWD=X",      "label": "USD/TWD",                      "category": "FX"},
    {"ticker": "USDBRL=X",   "label": "USD/BRL",                      "category": "FX"},
    {"ticker": "USDMXN=X",   "label": "USD/MXN",                      "category": "FX"},
    {"ticker": "USDZAR=X",   "label": "USD/ZAR",                      "category": "FX"},

    # ── Crypto (14) ────────────────────────────────────────────────────────
    {"ticker": "BTC-USD",    "label": "Bitcoin",                      "category": "Crypto"},
    {"ticker": "ETH-USD",    "label": "Ethereum",                     "category": "Crypto"},
    {"ticker": "BNB-USD",    "label": "Binance Coin",                 "category": "Crypto"},
    {"ticker": "SOL-USD",    "label": "Solana",                       "category": "Crypto"},
    {"ticker": "XRP-USD",    "label": "XRP",                          "category": "Crypto"},
    {"ticker": "ADA-USD",    "label": "Cardano",                      "category": "Crypto"},
    {"ticker": "AVAX-USD",   "label": "Avalanche",                    "category": "Crypto"},
    {"ticker": "DOGE-USD",   "label": "Dogecoin",                     "category": "Crypto"},
    {"ticker": "DOT-USD",    "label": "Polkadot",                     "category": "Crypto"},
    {"ticker": "LINK-USD",   "label": "Chainlink",                    "category": "Crypto"},
    {"ticker": "LTC-USD",    "label": "Litecoin",                     "category": "Crypto"},
    {"ticker": "MATIC-USD",  "label": "Polygon",                      "category": "Crypto"},
    {"ticker": "UNI-USD",    "label": "Uniswap",                      "category": "Crypto"},
    {"ticker": "ATOM-USD",   "label": "Cosmos",                       "category": "Crypto"},

    # ── Stocks: Mega-Cap Tech (17) ─────────────────────────────────────────
    {"ticker": "AAPL",       "label": "Apple",                        "category": "Stock"},
    {"ticker": "MSFT",       "label": "Microsoft",                    "category": "Stock"},
    {"ticker": "NVDA",       "label": "Nvidia",                       "category": "Stock"},
    {"ticker": "GOOG",       "label": "Alphabet",                     "category": "Stock"},
    {"ticker": "AMZN",       "label": "Amazon",                       "category": "Stock"},
    {"ticker": "META",       "label": "Meta",                         "category": "Stock"},
    {"ticker": "TSLA",       "label": "Tesla",                        "category": "Stock"},
    {"ticker": "AVGO",       "label": "Broadcom",                     "category": "Stock"},
    {"ticker": "ORCL",       "label": "Oracle",                       "category": "Stock"},
    {"ticker": "NFLX",       "label": "Netflix",                      "category": "Stock"},
    {"ticker": "AMD",        "label": "AMD",                          "category": "Stock"},
    {"ticker": "INTC",       "label": "Intel",                        "category": "Stock"},
    {"ticker": "QCOM",       "label": "Qualcomm",                     "category": "Stock"},
    {"ticker": "TXN",        "label": "Texas Instruments",            "category": "Stock"},
    {"ticker": "MU",         "label": "Micron Technology",            "category": "Stock"},
    {"ticker": "CRM",        "label": "Salesforce",                   "category": "Stock"},
    {"ticker": "ADBE",       "label": "Adobe",                        "category": "Stock"},

    # ── Stocks: Financials (11) ────────────────────────────────────────────
    {"ticker": "BRK-B",      "label": "Berkshire Hathaway B",         "category": "Stock"},
    {"ticker": "JPM",        "label": "JPMorgan Chase",               "category": "Stock"},
    {"ticker": "BAC",        "label": "Bank of America",              "category": "Stock"},
    {"ticker": "GS",         "label": "Goldman Sachs",                "category": "Stock"},
    {"ticker": "MS",         "label": "Morgan Stanley",               "category": "Stock"},
    {"ticker": "WFC",        "label": "Wells Fargo",                  "category": "Stock"},
    {"ticker": "C",          "label": "Citigroup",                    "category": "Stock"},
    {"ticker": "AXP",        "label": "American Express",             "category": "Stock"},
    {"ticker": "V",          "label": "Visa",                         "category": "Stock"},
    {"ticker": "MA",         "label": "Mastercard",                   "category": "Stock"},
    {"ticker": "BX",         "label": "Blackstone",                   "category": "Stock"},

    # ── Stocks: Fintech & Payments (4) ─────────────────────────────────────
    {"ticker": "PYPL",       "label": "PayPal",                       "category": "Stock"},
    {"ticker": "COIN",       "label": "Coinbase",                     "category": "Stock"},
    {"ticker": "SQ",         "label": "Block (Square)",               "category": "Stock"},
    {"ticker": "HOOD",       "label": "Robinhood",                    "category": "Stock"},

    # ── Stocks: Healthcare & Pharma (8) ───────────────────────────────────
    {"ticker": "UNH",        "label": "UnitedHealth Group",           "category": "Stock"},
    {"ticker": "LLY",        "label": "Eli Lilly",                    "category": "Stock"},
    {"ticker": "JNJ",        "label": "Johnson & Johnson",            "category": "Stock"},
    {"ticker": "ABBV",       "label": "AbbVie",                       "category": "Stock"},
    {"ticker": "MRK",        "label": "Merck",                        "category": "Stock"},
    {"ticker": "PFE",        "label": "Pfizer",                       "category": "Stock"},
    {"ticker": "AMGN",       "label": "Amgen",                        "category": "Stock"},
    {"ticker": "MRNA",       "label": "Moderna",                      "category": "Stock"},

    # ── Stocks: Energy (5) ────────────────────────────────────────────────
    {"ticker": "XOM",        "label": "ExxonMobil",                   "category": "Stock"},
    {"ticker": "CVX",        "label": "Chevron",                      "category": "Stock"},
    {"ticker": "COP",        "label": "ConocoPhillips",               "category": "Stock"},
    {"ticker": "SLB",        "label": "SLB (Schlumberger)",           "category": "Stock"},
    {"ticker": "OXY",        "label": "Occidental Petroleum",         "category": "Stock"},

    # ── Stocks: Consumer (10) ─────────────────────────────────────────────
    {"ticker": "WMT",        "label": "Walmart",                      "category": "Stock"},
    {"ticker": "COST",       "label": "Costco",                       "category": "Stock"},
    {"ticker": "AMZN",       "label": "Amazon",                       "category": "Stock"},  # also Broad Tech
    {"ticker": "HD",         "label": "Home Depot",                   "category": "Stock"},
    {"ticker": "MCD",        "label": "McDonald's",                   "category": "Stock"},
    {"ticker": "SBUX",       "label": "Starbucks",                    "category": "Stock"},
    {"ticker": "NKE",        "label": "Nike",                         "category": "Stock"},
    {"ticker": "KO",         "label": "Coca-Cola",                    "category": "Stock"},
    {"ticker": "PEP",        "label": "PepsiCo",                      "category": "Stock"},
    {"ticker": "PG",         "label": "Procter & Gamble",             "category": "Stock"},

    # ── Stocks: Industrials & Defense (7) ────────────────────────────────
    {"ticker": "BA",         "label": "Boeing",                       "category": "Stock"},
    {"ticker": "CAT",        "label": "Caterpillar",                  "category": "Stock"},
    {"ticker": "GE",         "label": "GE Aerospace",                 "category": "Stock"},
    {"ticker": "RTX",        "label": "RTX (Raytheon)",               "category": "Stock"},
    {"ticker": "LMT",        "label": "Lockheed Martin",              "category": "Stock"},
    {"ticker": "UPS",        "label": "UPS",                          "category": "Stock"},
    {"ticker": "DE",         "label": "John Deere",                   "category": "Stock"},

    # ── Stocks: Telecom & Media (5) ───────────────────────────────────────
    {"ticker": "T",          "label": "AT&T",                         "category": "Stock"},
    {"ticker": "VZ",         "label": "Verizon",                      "category": "Stock"},
    {"ticker": "DIS",        "label": "Disney",                       "category": "Stock"},
    {"ticker": "SPOT",       "label": "Spotify",                      "category": "Stock"},
    {"ticker": "UBER",       "label": "Uber",                         "category": "Stock"},

    # ── Stocks: Real Estate (3) ───────────────────────────────────────────
    {"ticker": "AMT",        "label": "American Tower REIT",          "category": "Stock"},
    {"ticker": "PLD",        "label": "Prologis REIT",                "category": "Stock"},
    {"ticker": "O",          "label": "Realty Income REIT",           "category": "Stock"},

    # ── Stocks: International (11) ────────────────────────────────────────
    {"ticker": "TSM",        "label": "TSMC",                         "category": "Stock"},
    {"ticker": "ASML",       "label": "ASML Holding",                 "category": "Stock"},
    {"ticker": "NVO",        "label": "Novo Nordisk",                 "category": "Stock"},
    {"ticker": "SAP",        "label": "SAP",                          "category": "Stock"},
    {"ticker": "TM",         "label": "Toyota",                       "category": "Stock"},
    {"ticker": "BABA",       "label": "Alibaba",                      "category": "Stock"},
    {"ticker": "BIDU",       "label": "Baidu",                        "category": "Stock"},
    {"ticker": "005930.KS",  "label": "Samsung Electronics",          "category": "Stock"},
    {"ticker": "9984.T",     "label": "SoftBank Group",               "category": "Stock"},
    {"ticker": "0700.HK",    "label": "Tencent Holdings",             "category": "Stock"},
    {"ticker": "SHOP",       "label": "Shopify",                      "category": "Stock"},

    # ── Stocks: Emerging Tech (5) ─────────────────────────────────────────
    {"ticker": "PLTR",       "label": "Palantir",                     "category": "Stock"},
    {"ticker": "ARM",        "label": "ARM Holdings",                 "category": "Stock"},
    {"ticker": "SNOW",       "label": "Snowflake",                    "category": "Stock"},
    {"ticker": "NET",        "label": "Cloudflare",                   "category": "Stock"},
    {"ticker": "DDOG",       "label": "Datadog",                      "category": "Stock"},
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