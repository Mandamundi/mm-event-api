import math
from datetime import timedelta
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

CACHE_DIR = Path(__file__).parent / "price_cache"


def resolve_event_date(ev: dict, phase: str) -> Optional[str]:
    if phase == "end" and ev.get("end_date"):
        return ev["end_date"]
    return ev.get("start_date")


def enrich_event(ev: dict) -> dict:
    enriched = dict(ev)
    if ev.get("start_date") and ev.get("end_date"):
        start = pd.Timestamp(ev["start_date"])
        end   = pd.Timestamp(ev["end_date"])
        enriched["duration_days"] = (end - start).days
    else:
        enriched["duration_days"] = None
    return enriched


def _cache_path(ticker: str) -> Path:
    safe = ticker.replace("/", "_").replace("^", "_").replace("=", "_")
    return CACHE_DIR / f"{safe}.parquet"


def fetch_price_series(ticker: str, start: str, end: str) -> pd.Series:
    path = _cache_path(ticker)

    if not path.exists():
        raise ValueError(
            f"No cached data found for {ticker}. "
            f"Run prefetch_prices.py locally and commit the price_cache/ directory."
        )

    try:
        series = pd.read_parquet(path).squeeze()
    except Exception as e:
        raise ValueError(f"Could not read cache for {ticker}: {e}")

    series.index = pd.to_datetime(series.index).normalize()
    series = series.dropna()

    if series.empty:
        raise ValueError(f"Cache file for {ticker} is empty.")

    start_dt = pd.Timestamp(start)
    end_dt   = pd.Timestamp(end)
    result   = series.loc[start_dt:end_dt]

    if result.empty:
        raise ValueError(
            f"No data for {ticker} between {start} and {end}. "
            f"Cache covers {series.index[0].date()} to {series.index[-1].date()}."
        )

    return result


def compute_event_window(
    price_series: pd.Series,
    event_date_str: str,
    pre_days: int,
    post_days: int,
) -> Optional[dict]:
    event_date   = pd.Timestamp(event_date_str)
    trading_days = price_series.index

    future_mask = trading_days >= event_date
    if not future_mask.any():
        return None

    t0_idx    = trading_days[future_mask][0]
    pos       = trading_days.get_loc(t0_idx)
    start_pos = max(pos - pre_days, 0)          # clamp to series start
    end_pos   = min(pos + post_days, len(trading_days) - 1)  # clamp to series end

    # Require at least the anchor point itself
    if start_pos > pos:
        return None

    window       = price_series.iloc[start_pos : end_pos + 1]
    anchor_price = price_series.iloc[pos]

    if anchor_price == 0 or pd.isna(anchor_price):
        return None

    # t offset is relative to the actual start_pos, not always -pre_days
    actual_pre = pos - start_pos   # may be < pre_days if event is near series start

    returns = []
    for i, (dt, price) in enumerate(window.items()):
        t   = i - actual_pre
        pct = (price / anchor_price - 1) * 100
        returns.append({"t": t, "pct_return": round(pct, 4), "date": str(dt.date())})

    post_window = window.iloc[actual_pre:]

    def horizon_return(n_days: int) -> Optional[float]:
        if n_days >= len(post_window):
            return None
        return round((post_window.iloc[n_days] / anchor_price - 1) * 100, 4)

    peak   = anchor_price
    max_dd = 0.0
    for price in post_window:
        if price > peak:
            peak = price
        dd = (price - peak) / peak * 100
        if dd < max_dd:
            max_dd = dd

    stats = {
        "return_1w":              horizon_return(5),
        "return_1m":              horizon_return(21),
        "return_3m":              horizon_return(63),
        "return_6m":              horizon_return(126),
        "return_12m":             horizon_return(252),
        "max_drawdown_in_window": round(max_dd, 4),
    }

    return {"returns": returns, "stats": stats}


def compute_aggregate_stats(event_results: list, pre_days: int, post_days: int) -> dict:
    total_days = pre_days + post_days + 1
    matrix     = np.full((len(event_results), total_days), np.nan)

    for i, ev in enumerate(event_results):
        if ev is None:
            continue
        for point in ev["returns"]:
            col = point["t"] + pre_days
            if 0 <= col < total_days:
                matrix[i, col] = point["pct_return"]

    t_axis      = list(range(-pre_days, post_days + 1))
    median_line = np.nanmedian(matrix, axis=0).tolist()
    mean_line   = np.nanmean(matrix, axis=0).tolist()
    p25_line    = np.nanpercentile(matrix, 25, axis=0).tolist()
    p75_line    = np.nanpercentile(matrix, 75, axis=0).tolist()

    def win_rate(n_days: int):
        col = pre_days + n_days
        if col >= total_days:
            return None
        vals  = matrix[:, col]
        valid = vals[~np.isnan(vals)]
        if len(valid) == 0:
            return None
        positive = int(np.sum(valid > 0))
        return {
            "n":        int(len(valid)),
            "positive": positive,
            "rate":     round(positive / len(valid) * 100, 1),
        }

    def clean(v):
        return round(v, 4) if not math.isnan(v) else None

    return {
        "t_axis":    t_axis,
        "median":    [clean(v) for v in median_line],
        "mean":      [clean(v) for v in mean_line],
        "p25":       [clean(v) for v in p25_line],
        "p75":       [clean(v) for v in p75_line],
        "win_rates": {
            "1w":  win_rate(5),
            "1m":  win_rate(21),
            "3m":  win_rate(63),
            "6m":  win_rate(126),
            "12m": win_rate(252),
        },
    }


def build_date_range(events: list, pre_days: int, post_days: int) -> tuple:
    cal_pre  = int(pre_days  * 1.5) + 10
    cal_post = int(post_days * 1.5) + 10

    dates = []
    for ev in events:
        if isinstance(ev, dict):
            dates.append(pd.Timestamp(ev["_resolved_date"]))
        else:
            dates.append(pd.Timestamp(ev.date))

    earliest = min(dates) - timedelta(days=cal_pre)
    latest   = max(dates) + timedelta(days=cal_post)
    return str(earliest.date()), str(latest.date())