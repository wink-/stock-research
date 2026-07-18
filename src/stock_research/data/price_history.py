"""Price history fetcher + candle normalization."""
from __future__ import annotations
from datetime import datetime, timedelta, timezone


def fetch_daily_candles(
    client, symbol: str, period_months: int = 6, end: datetime | None = None
) -> list[dict]:
    """Fetch daily candles for the last N months ending at `end` (default now).

    Returns list of {datetime, open, high, low, close, volume}.
    """
    end = end or datetime.now(timezone.utc)
    start = end - timedelta(days=period_months * 30 + 5)
    resp = client.get_price_history_every_day(
        symbol,
        start_datetime=start,
        end_datetime=end,
        need_extended_hours_data=False,
    )
    data = resp.json()
    candles_raw = data.get("candles", [])
    out: list[dict] = []
    for c in candles_raw:
        out.append({
            "datetime": c.get("datetime"),
            "open": float(c["open"]),
            "high": float(c["high"]),
            "low": float(c["low"]),
            "close": float(c["close"]),
            "volume": int(c.get("volume", 0) or 0),
        })
    return out


def fetch_intraday_candles(
    client, symbol: str, days: int = 1, freq_min: int = 5, end: datetime | None = None
) -> list[dict]:
    """Intraday candles (for auction analysis, GEX intraday, etc.).

    days: lookback days. freq_min: bar size (1/5/10/15/30).
    """
    end = end or datetime.now(timezone.utc)
    start = end - timedelta(days=days)
    fn_map = {
        1: client.get_price_history_every_minute,
        5: client.get_price_history_every_five_minutes,
        10: client.get_price_history_every_ten_minutes,
        15: client.get_price_history_every_fifteen_minutes,
        30: client.get_price_history_every_thirty_minutes,
    }
    fn = fn_map.get(freq_min, client.get_price_history_every_five_minutes)
    resp = fn(
        symbol,
        start_datetime=start,
        end_datetime=end,
        need_extended_hours_data=False,
    )
    data = resp.json()
    out: list[dict] = []
    for c in data.get("candles", []):
        out.append({
            "datetime": c.get("datetime"),
            "open": float(c["open"]),
            "high": float(c["high"]),
            "low": float(c["low"]),
            "close": float(c["close"]),
            "volume": int(c.get("volume", 0) or 0),
        })
    return out
