"""Quote + fundamentals fetcher."""
from __future__ import annotations
from datetime import date
from stock_research.models import Quote, Fundamentals


def parse_quote(raw: dict) -> tuple[Quote, Fundamentals | None]:
    """Parse the Schwab /quotes response for one symbol.

    `raw` is the inner dict under data["{SYMBOL}"].
    """
    q = raw.get("quote", {})
    f = raw.get("fundamental", {})
    ref = raw.get("reference", {})

    last = q.get("lastPrice") or q.get("mark") or q.get("closePrice", 0.0)
    close_prior = q.get("closePrice", last)
    change_pct = q.get("markPercentChange", q.get("netPercentChange", 0.0))

    quote = Quote(
        symbol=raw.get("symbol", ""),
        last=float(last),
        bid=float(q.get("bidPrice", 0.0) or 0.0),
        ask=float(q.get("askPrice", 0.0) or 0.0),
        open=float(q.get("openPrice", 0.0) or 0.0),
        high=float(q.get("highPrice", 0.0) or 0.0),
        low=float(q.get("lowPrice", 0.0) or 0.0),
        close_prior=float(close_prior),
        change_pct=float(change_pct),
        volume=int(q.get("totalVolume", 0) or 0),
        high_52wk=float(q.get("52WeekHigh", 0.0) or 0.0),
        low_52wk=float(q.get("52WeekLow", 0.0) or 0.0),
        description=ref.get("description", ""),
    )

    fundamentals = None
    if f:
        def _date(s: str | None) -> date | None:
            if not s:
                return None
            try:
                return date.fromisoformat(s[:10])
            except Exception:
                return None

        fundamentals = Fundamentals(
            pe_ratio=_f(f.get("peRatio")),
            eps=_f(f.get("eps")),
            div_yield=_f(f.get("divYield")),
            div_amount=_f(f.get("divAmount")),
            div_ex_date=_date(f.get("divExDate")),
            shares_out=int(f.get("sharesOutstanding") or 0) or None,
            avg_volume_10d=_f(f.get("avg10DaysVolume")),
            last_earnings=_date(f.get("lastEarningsDate")),
        )

    return quote, fundamentals


def _f(v) -> float | None:
    if v is None or v == 0:
        return None
    try:
        return float(v)
    except Exception:
        return None


def fetch_quote(client, symbol: str) -> tuple[Quote, Fundamentals | None]:
    """Live fetch via schwab-py client."""
    resp = client.get_quote(symbol)
    data = resp.json()
    raw = data.get(symbol, data)
    return parse_quote(raw)
