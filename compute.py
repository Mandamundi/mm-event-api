import math
from datetime import timedelta
from typing import Optional

import numpy as np
import pandas as pd


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


def fetch_price_series(ticker: str, start: str, end: str):
    import time
    import pandas as pd
    from pandas_datareader import data as pdr

    last_error = None
    for attempt in range(4):
        if attempt > 0:
            time.sleep(1.5 * attempt)
        try:
            df = pdr.DataReader(ticker, "stooq", start=start, end=end)

            if df is None or df.empty:
                last_error = ValueError(f"No data returned for {ticker}")
                continue   # Stooq sometimes returns empty on first hit, retry

            df = df.sort_index()
            series = df["Close"]
            series.index = pd.to_datetime(series.index).normalize()
            series = series.dropna()

            if series.empty:
                last_error = ValueError(f"Empty series for {ticker}")
                continue

            return series

        except Exception as e:
            last_error = e
            err_str = str(e).lower()
            if any(x in err_str for x in ["timeout", "connection", "remote", "read", "500", "503"]):
                continue
            raise ValueError(f"Could not fetch data for {ticker}: {e}")

    raise ValueError(f"Failed to fetch {ticker} after 4 attempts. Last error: {last_error}")


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
    start_pos = pos - pre_days
    end_pos   = pos + post_days

    if start_pos < 0 or end_pos >= len(trading_days):
        return None

    window       = price_series.iloc[start_pos : end_pos + 1]
    anchor_price = price_series.iloc[pos]

    if anchor_price == 0 or pd.isna(anchor_price):
        return None

    returns = []
    for i, (dt, price) in enumerate(window.items()):
        t   = i - pre_days
        pct = (price / anchor_price - 1) * 100
        returns.append({"t": t, "pct_return": round(pct, 4), "date": str(dt.date())})

    post_window = window.iloc[pre_days:]

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