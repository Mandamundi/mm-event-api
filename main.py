from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from pathlib import Path
import uvicorn
import os
import io
import pandas as pd
import loader
import compute

app = FastAPI(title="Event Study API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store for uploaded CSV price series
# Keys are the custom ticker strings the frontend assigns (e.g. "custom_1234567890")
custom_price_cache: dict[str, pd.Series] = {}


@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/api/events")
def get_events():
    return loader.load_events()

@app.get("/api/assets")
def get_assets():
    grouped = {}
    for asset in loader.DEFAULT_ASSETS:
        grouped.setdefault(asset["category"], []).append(asset)
    return {"assets": loader.DEFAULT_ASSETS, "grouped": grouped}

CACHE_DIR = Path(__file__).parent / "price_cache"

@app.get("/api/prices/{ticker}")
def get_prices(ticker: str, start: Optional[str] = None, end: Optional[str] = None):
    safe_name = ticker.replace("/", "_").replace("^", "_").replace("=", "_")
    path = CACHE_DIR / f"{safe_name}.parquet"
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"No cached data for {ticker}")
    df = pd.read_parquet(path)
    if start:
        df = df[df.index >= pd.to_datetime(start)]
    if end:
        df = df[df.index <= pd.to_datetime(end)]
    df.index = df.index.strftime("%Y-%m-%d")
    return {"ticker": ticker, "prices": df["Close"].to_dict()}


class AnalysisRequest(BaseModel):
    event_ids: list[str]
    ticker: str
    phase: str = "start"
    pre_days: int = 30
    post_days: int = 60
    benchmark_ticker: Optional[str] = None
    second_ticker: Optional[str] = None


@app.post("/api/analysis")
def run_analysis(req: AnalysisRequest):
    if not req.event_ids:
        raise HTTPException(status_code=400, detail="No event IDs provided")
    if req.phase not in ("start", "end"):
        raise HTTPException(status_code=400, detail="phase must be 'start' or 'end'")
    if req.pre_days < 1 or req.post_days < 1:
        raise HTTPException(status_code=400, detail="pre_days and post_days must be >= 1")
    if req.pre_days > 252 or req.post_days > 504:
        raise HTTPException(status_code=400, detail="Window too large")

    events = []
    skipped = []
    for eid in req.event_ids:
        ev = loader.get_event_by_id(eid)
        if ev is None:
            raise HTTPException(status_code=404, detail=f"Event ID not found: {eid}")
        resolved_date = compute.resolve_event_date(ev, req.phase)
        if resolved_date is None:
            skipped.append({"event_id": eid, "reason": "end_date not available"})
            continue
        enriched = compute.enrich_event(ev)
        enriched["_resolved_date"] = resolved_date
        events.append(enriched)

    if not events:
        raise HTTPException(status_code=400, detail="No valid events after phase resolution")

    start_date, end_date = compute.build_date_range(events, req.pre_days, req.post_days)

    tickers_needed = {req.ticker}
    if req.benchmark_ticker:
        tickers_needed.add(req.benchmark_ticker)
    if req.second_ticker:
        tickers_needed.add(req.second_ticker)

    price_data = {}
    for ticker in tickers_needed:
        # Check in-memory custom cache first before hitting yfinance
        if ticker in custom_price_cache:
            price_data[ticker] = custom_price_cache[ticker]
        else:
            try:
                price_data[ticker] = compute.fetch_price_series(ticker, start_date, end_date)
            except Exception as e:
                raise HTTPException(status_code=502, detail=f"Failed to fetch data for {ticker}: {str(e)}")

    def compute_series_for_ticker(ticker: str, use_excess: bool = False) -> dict:
        series = price_data[ticker]
        if use_excess and req.benchmark_ticker and req.benchmark_ticker != ticker:
            bm_series = price_data[req.benchmark_ticker]
            common_idx = series.index.intersection(bm_series.index)
            series    = series.loc[common_idx]
            bm_series = bm_series.loc[common_idx]
            ticker_ret = series / series.iloc[0]
            bm_ret     = bm_series / bm_series.iloc[0]
            series     = ticker_ret / bm_ret * series.iloc[0]

        event_results = []
        for ev in events:
            result = compute.compute_event_window(
                series, ev["_resolved_date"], req.pre_days, req.post_days
            )
            event_results.append({
                "event_id":    ev["id"],
                "event_label": ev["label"],
                "event_date":  ev["_resolved_date"],
                "phase":       req.phase,
                "event_meta":  {k: v for k, v in ev.items()
                                if k not in ("id", "label", "start_date", "end_date", "_resolved_date")},
                "window_data": result,
            })

        valid_results = [e["window_data"] for e in event_results if e["window_data"] is not None]
        aggregate = compute.compute_aggregate_stats(valid_results, req.pre_days, req.post_days)

        return {
            "ticker": ticker,
            "excess_return_mode": use_excess,
            "benchmark_ticker": req.benchmark_ticker if use_excess else None,
            "events": event_results,
            "aggregate": aggregate,
            "meta": {
                "pre_days":  req.pre_days,
                "post_days": req.post_days,
                "n_events":  len(events),
                "n_valid":   len(valid_results),
                "day_type":  "trading_days",
            },
        }

    response = {
        "phase": req.phase,
        "skipped_events": skipped,
        "primary": compute_series_for_ticker(req.ticker, use_excess=False),
    }
    if req.benchmark_ticker:
        response["primary_excess"] = compute_series_for_ticker(req.ticker, use_excess=True)
    if req.second_ticker:
        response["secondary"] = compute_series_for_ticker(req.second_ticker, use_excess=False)
        if req.benchmark_ticker:
            response["secondary_excess"] = compute_series_for_ticker(req.second_ticker, use_excess=True)

    return response


@app.post("/api/validate-csv")
async def validate_csv(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not parse CSV: {str(e)}")

    # Drop fully empty columns (common in FRED/Yahoo exports with trailing commas)
    df = df.dropna(axis=1, how="all")
    df.columns = df.columns.str.strip()
    cols_lower = [c.lower() for c in df.columns]

    # Auto-detect date column
    date_col = None
    if "date" in cols_lower:
        date_col = df.columns[cols_lower.index("date")]
    else:
        for col in df.columns:
            try:
                parsed = pd.to_datetime(df[col].dropna().head(5), infer_datetime_format=True)
                if len(parsed) >= 3:
                    date_col = col
                    break
            except Exception:
                continue

    if date_col is None:
        raise HTTPException(
            status_code=400,
            detail=f"Could not find a date column. Columns found: {list(df.columns)}"
        )

    # Auto-detect price column: named aliases first, then first remaining numeric
    price_col = None
    price_aliases = {"close", "price", "value", "adj close", "adj_close", "adjusted_close"}
    for col in df.columns:
        if col.lower() in price_aliases and col != date_col:
            price_col = col
            break
    if price_col is None:
        for col in df.columns:
            if col == date_col:
                continue
            try:
                pd.to_numeric(df[col].dropna().head(5))
                price_col = col
                break
            except Exception:
                continue

    if price_col is None:
        raise HTTPException(
            status_code=400,
            detail=f"Could not find a price/value column. Columns found: {list(df.columns)}"
        )

    # Build clean dataframe
    df = df[[date_col, price_col]].copy()
    df.columns = ["date", "close"]
    df["date"]  = pd.to_datetime(df["date"], infer_datetime_format=True, errors="coerce")
    df["close"] = pd.to_numeric(df["close"], errors="coerce")
    df = df.dropna().sort_values("date").reset_index(drop=True)

    if len(df) < 10:
        raise HTTPException(
            status_code=400,
            detail=f"Not enough valid rows after parsing (got {len(df)}, need at least 10)"
        )

    # Store as a pd.Series indexed by date in the custom cache.
    # The frontend passes a ticker like "custom_1234567890" — it must also send
    # that same string in the request so we know what key to store it under.
    # We use the original filename (sanitised) as the key and return it to the frontend.
    safe_name = "custom_" + "".join(c for c in (file.filename or "upload") if c.isalnum() or c in "_-")
    series = pd.Series(df["close"].values, index=pd.to_datetime(df["date"]))
    custom_price_cache[safe_name] = series

    return {
        "valid": True,
        "ticker": safe_name,       # frontend must use this exact string as the asset ticker
        "rows": len(df),
        "date_col_found": date_col,
        "price_col_found": price_col,
        "date_range": {
            "start": str(df["date"].min().date()),
            "end":   str(df["date"].max().date()),
        },
        "preview": df.head(5).assign(
            date=df["date"].dt.strftime("%Y-%m-%d")
        ).to_dict(orient="records"),
    }


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)