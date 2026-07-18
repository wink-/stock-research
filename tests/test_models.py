"""Tests for data models."""
from datetime import datetime
from stock_research.models import Quote, Fundamentals, Technical, Report, Level


def test_quote_instantiation():
    q = Quote(
        symbol="KMI", last=32.56, bid=32.5, ask=32.6, open=32.9,
        high=32.97, low=32.46, close_prior=32.54, change_pct=0.06,
        volume=2_400_000, high_52wk=34.81, low_52wk=25.60,
    )
    assert q.symbol == "KMI"
    assert q.high_52wk == 34.81


def test_report_minimal():
    q = Quote(
        symbol="KMI", last=32.56, bid=32.5, ask=32.6, open=32.9,
        high=32.97, low=32.46, close_prior=32.54, change_pct=0.06,
        volume=2_400_000, high_52wk=34.81, low_52wk=25.60,
    )
    t = Technical(sma_20=32.26, sma_50=32.23, above_20=True, above_50=True)
    r = Report(symbol="KMI", quote=q, technical=t)
    assert r.symbol == "KMI"
    assert r.technical.above_20 is True
    assert r.fundamentals is None
    assert r.levels == []


def test_report_serialization():
    q = Quote(
        symbol="TEST", last=100.0, bid=99.9, ask=100.1, open=99.5,
        high=100.5, low=99.0, close_prior=99.5, change_pct=0.5,
        volume=1000, high_52wk=110.0, low_52wk=90.0,
    )
    t = Technical(regime_score=30, regime_label="neutral-bullish")
    r = Report(symbol="TEST", quote=q, technical=t)
    js = r.model_dump_json()
    assert '"symbol":"TEST"' in js
    # Round trip
    from stock_research.models import Report as R2
    r2 = R2.model_validate_json(js)
    assert r2.quote.last == 100.0


def test_level_defaults():
    l = Level(price=100.0, kind="support")
    assert l.strength == 1
