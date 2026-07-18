"""Price history fetcher + candle normalization."""
from __future__ import annotations


def fetch_daily_candles(client, symbol: str, period_months: int = 6) -> list[dict]:
    """Fetch daily candles for the last N months.

    Returns list of {datetime, open, high, low, close, volume}.
    """
    resp = client.get_price_history_everywhere(
        symbol,
        period_type="MONTH",
        period=f"{period_months}_MONTHS" if period_months != 6 else "SIX_MONTHS",
        frequency_type="DAILY",
        frequency=1,
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
    client, symbol: str, days: int = 1, freq_min: int = 5
) -> list[dict]:
    """Intraday candles (for auction analysis, GEX intraday, etc.)."""
    period_map = {1: "ONE_DAY", 2: "TWO_DAYS", 5: "FIVE_DAYS"}
    freq_map = {1: "EVERY_MINUTE", 5: "EVERY_FIVE_MINUTES"}
    resp = client.get_price_history_everywhere(
        symbol,
        period_type="DAY",
        period=period_map.get(days, "FIVE_DAYS"),
        frequency_type="MINUTE",
        frequency=freq_map.get(freq_min, "EVERY_FIVE_MINUTES"),
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
