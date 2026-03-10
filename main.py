from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import os

import loader
import compute

app = FastAPI(title="Market Event Analysis API")

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/assets")
def get_assets():
    return loader.DEFAULT_ASSETS

@app.get("/events")
def get_events():
    return loader.load_events()

class AnalyzeRequest(BaseModel):
    ticker: str
    event_type_id: str
    phase: str = "start"
    pre_days: int = 20
    post_days: int = 60

@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    events_data = loader.load_events()
    
    # Find the event type
    event_type = next((et for et in events_data["event_types"] if et["id"] == req.event_type_id), None)
    if not event_type:
        raise HTTPException(status_code=404, detail="Event type not found")
        
    events = event_type["events"]
    if not events:
        raise HTTPException(status_code=400, detail="No events found for this type")
        
    # Resolve dates
    resolved_events = []
    for ev in events:
        date_str = compute.resolve_event_date(ev, req.phase)
        if date_str:
            enriched = compute.enrich_event(ev)
            enriched["_resolved_date"] = date_str
            resolved_events.append(enriched)
            
    if not resolved_events:
        raise HTTPException(status_code=400, detail="No valid dates resolved for events")
        
    # Build date range
    start_date, end_date = compute.build_date_range(resolved_events, req.pre_days, req.post_days)
    
    # Fetch price series
    try:
        price_series = compute.fetch_price_series(req.ticker, start_date, end_date)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    # Compute windows
    event_results = []
    valid_events = []
    for ev in resolved_events:
        res = compute.compute_event_window(
            price_series, 
            ev["_resolved_date"], 
            req.pre_days, 
            req.post_days
        )
        if res:
            ev_result = {**ev, "results": res}
            valid_events.append(ev_result)
            event_results.append(res)
        else:
            event_results.append(None)
            
    if not any(event_results):
        raise HTTPException(status_code=400, detail="Could not compute windows for any events")
        
    # Compute aggregate stats
    agg_stats = compute.compute_aggregate_stats(event_results, req.pre_days, req.post_days)
    
    return {
        "ticker": req.ticker,
        "event_type_id": req.event_type_id,
        "phase": req.phase,
        "aggregate_stats": agg_stats,
        "events": valid_events
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
