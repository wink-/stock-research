"""Tests for the Schwab quote parser (no live API)."""
import json
from pathlib import Path
from stock_research.data.fundamentals import parse_quote

FIXTURE = Path(__file__).parent / "fixtures" / "sample_quote.json"


def test_parse_quote_kmi():
    raw = json.loads(FIXTURE.read_text())
    quote, fundamentals = parse_quote(raw["KMI"])
    assert quote.symbol == "KMI"
    assert abs(quote.last - 32.58) < 0.01
    assert quote.high_52wk == 34.805
    assert quote.low_52wk == 25.6
    assert quote.volume == 2421690
    assert "KINDER MORGAN" in quote.description


def test_parse_quote_fundamentals():
    raw = json.loads(FIXTURE.read_text())
    _, fundamentals = parse_quote(raw["KMI"])
    assert fundamentals is not None
    assert abs(fundamentals.pe_ratio - 21.94) < 0.1
    assert abs(fundamentals.eps - 1.37) < 0.01
    assert abs(fundamentals.div_yield - 3.66) < 0.1
    assert fundamentals.shares_out > 2_000_000_000


def test_parse_quote_missing_fields():
    """Minimal raw dict should not crash."""
    raw = {"symbol": "TEST", "quote": {"lastPrice": 50.0}}
    quote, fundamentals = parse_quote(raw)
    assert quote.symbol == "TEST"
    assert quote.last == 50.0
    assert fundamentals is None
