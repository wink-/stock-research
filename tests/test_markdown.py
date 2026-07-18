"""Tests for markdown rendering."""
from datetime import datetime, date
from stock_research.models import (
    Quote, Fundamentals, Technical, Level, OptionsSnapshot, NewsItem, Report,
)
from stock_research.report.markdown import render_markdown


def make_report():
    q = Quote(
        symbol="KMI", last=32.56, bid=32.5, ask=32.6, open=32.9,
        high=32.97, low=32.46, close_prior=32.54, change_pct=0.06,
        volume=2_400_000, high_52wk=34.81, low_52wk=25.60,
        description="KINDER MORGAN INC DE",
    )
    f = Fundamentals(pe_ratio=21.9, eps=1.37, div_yield=3.66, div_amount=1.19,
                     shares_out=2_224_825_757)
    t = Technical(sma_8=32.4, sma_20=32.26, sma_50=32.23,
                  above_20=True, above_50=True,
                  regime_score=55, regime_label="neutral-bullish",
                  atr_14=0.67, range_position_pct=64.0)
    levels = [
        Level(price=31.65, kind="support", strength=2),
        Level(price=34.81, kind="resistance", strength=1),
    ]
    options = OptionsSnapshot(
        expiry=date(2027, 1, 15), dte=182, atm_iv=22.0,
        implied_move=5.06, put_wall=30.0, call_wall=35.0,
    )
    news = [NewsItem(title="KMI data center win", published=datetime(2026, 7, 8))]
    return Report(
        symbol="KMI", quote=q, fundamentals=f, technical=t,
        levels=levels, options=options, news=news,
    )


def test_render_markdown_basic():
    r = make_report()
    md = render_markdown(r)
    assert "KMI" in md
    assert "$32.56" in md
    assert "neutral-bullish" in md.lower() or "Neutral-Bullish" in md
    assert "$31.65" in md  # support level
    assert "22.0%" in md or "22.0" in md  # IV


def test_render_markdown_missing_sections():
    """Report with no fundamentals/options/news should still render."""
    q = Quote(
        symbol="X", last=10, bid=9.9, ask=10.1, open=9.8,
        high=10.2, low=9.7, close_prior=9.8, change_pct=2.0,
        volume=1000, high_52wk=12, low_52wk=8,
    )
    t = Technical(regime_score=0, regime_label="neutral")
    r = Report(symbol="X", quote=q, technical=t)
    md = render_markdown(r)
    assert "X" in md
    assert "n/a" in md or "No fundamental" in md


def test_render_markdown_options_iv_zero():
    """IV None should render as n/a without crashing."""
    r = make_report()
    r.options.atm_iv = None
    md = render_markdown(r)
    assert "n/a" in md
