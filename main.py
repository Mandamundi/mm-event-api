from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
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
        try:
            fh_ticker = loader.get_finnhub_ticker(ticker)
            price_data[ticker] = compute.fetch_price_series(fh_ticker, start_date, end_date)
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
        df = pd.read_csv(io.BytesIO(contents), parse_dates=["date"])
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not parse CSV: {str(e)}")

    required_cols = {"date", "close"}
    if not required_cols.issubset(set(df.columns.str.lower())):
        raise HTTPException(
            status_code=400,
            detail=f"CSV must have columns: date, close. Found: {list(df.columns)}"
        )

    df.columns = df.columns.str.lower()
    df = df[["date", "close"]].dropna()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")

    return {
        "valid": True,
        "rows": len(df),
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