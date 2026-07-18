"""Report builder: assemble Report model from all data modules."""
from __future__ import annotations
from stock_research.config import Config
from stock_research.data.schwab_client import get_client
from stock_research.data.fundamentals import fetch_quote
from stock_research.data.price_history import fetch_daily_candles
from stock_research.data.options_snapshot import fetch_options_snapshot
from stock_research.data.news_rss import fetch_news
from stock_research.analysis.technical import (
    compute_sma,
    compute_atr,
    regime_score,
    range_position_pct,
)
from stock_research.analysis.levels import pivot_points, cluster_levels
from stock_research.models import Report, Technical, Level


def build_report(
    symbol: str,
    config: Config | None = None,
    include_options: bool = True,
    include_news: bool = True,
    client=None,
) -> Report:
    """Assemble a full Report from Schwab + news data.

    Pass `client=` to reuse an authenticated schwab-py client across calls.
    """
    cfg = config or Config.from_env()
    if client is None:
        client = get_client(cfg)

    symbol = symbol.upper()

    # Quote + fundamentals
    quote, fundamentals = fetch_quote(client, symbol)

    # Price history → candles + technicals
    candles = fetch_daily_candles(client, symbol, period_months=6)
    closes = [c["close"] for c in candles]
    score, label = regime_score(candles) if len(candles) >= 5 else (0, "neutral")

    sma_8_v = compute_sma(closes, 8)
    sma_20_v = compute_sma(closes, 20)
    sma_50_v = compute_sma(closes, 50)
    technical = Technical(
        sma_8=sma_8_v,
        sma_20=sma_20_v,
        sma_50=sma_50_v,
        sma_200=compute_sma(closes, 200),
        above_20=bool(sma_20_v and quote.last > sma_20_v),
        above_50=bool(sma_50_v and quote.last > sma_50_v),
        regime_score=score,
        regime_label=label,
        atr_14=compute_atr(candles, 14),
        range_position_pct=range_position_pct(candles, 20),
    )

    # S/R levels
    pivots = pivot_points(candles, window=3)
    clustered = cluster_levels(pivots, tolerance=0.02, last_price=quote.last)
    levels = [Level(price=l["price"], kind=l["kind"], strength=l["strength"]) for l in clustered]

    # Options
    options = None
    if include_options:
        try:
            options = fetch_options_snapshot(client, symbol)
        except Exception as e:
            options = None
            import sys
            print(f"[warn] options snapshot failed: {type(e).__name__}: {e}", file=sys.stderr)

    # News
    news = []
    if include_news:
        # Use company description or symbol for query
        q = fundamentals and quote.description or symbol
        try:
            news = fetch_news(symbol, query=f'"{q}" OR {symbol}', limit=12)
        except Exception:
            news = []

    return Report(
        symbol=symbol,
        quote=quote,
        fundamentals=fundamentals,
        technical=technical,
        levels=levels,
        options=options,
        news=news,
    )
