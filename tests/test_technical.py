"""Tests for technical analysis: SMA, ATR, regime."""
from stock_research.analysis.technical import (
    compute_sma, compute_atr, regime_score, range_position_pct,
)


def make_candle(o, h, l, c, v=1000):
    return {"open": o, "high": h, "low": l, "close": c, "volume": v}


def test_compute_sma():
    closes = [10, 11, 12, 13, 14]
    assert compute_sma(closes, 3) == 13.0  # (12+13+14)/3
    assert compute_sma(closes, 5) == 12.0
    assert compute_sma(closes, 10) is None  # not enough data


def test_compute_sma_empty():
    assert compute_sma([], 3) is None


def test_compute_atr_simple():
    # constant $1 range candles → ATR = 1.0
    candles = [make_candle(10, 11, 10, 10) for _ in range(16)]
    atr = compute_atr(candles, n=14)
    assert atr is not None
    assert abs(atr - 1.0) < 0.001


def test_compute_atr_not_enough_data():
    candles = [make_candle(10, 11, 10, 10) for _ in range(5)]
    assert compute_atr(candles, n=14) is None


def test_compute_atr_with_gaps():
    # candle with gap: TR should reflect high-low plus gap from prev close
    candles = [
        make_candle(10, 11, 10, 10),
        make_candle(15, 16, 14, 15),  # gap up, TR = max(16-14, |16-10|, |14-10|) = 6
    ]
    # n=1 means just the last candle's TR
    atr = compute_atr(candles, n=1)
    assert atr == 6.0


def test_regime_bullish_sequence():
    """A clean uptrend should score positively."""
    candles = []
    for i in range(60):
        c = make_candle(o=100 + i, h=102 + i, l=99 + i, c=101 + i)
        candles.append(c)
    score, label = regime_score(candles)
    assert score > 20
    assert label in ("bullish", "neutral-bullish")


def test_regime_bearish_sequence():
    """A clean downtrend should score negatively."""
    candles = []
    for i in range(60):
        c = make_candle(o=200 - i, h=201 - i, l=198 - i, c=199 - i)
        candles.append(c)
    score, label = regime_score(candles)
    assert score < 0


def test_regime_short_history():
    candles = [make_candle(10, 11, 10, 10) for _ in range(3)]
    score, label = regime_score(candles)
    assert score == 0
    assert label == "neutral"


def test_range_position_at_high():
    candles = [make_candle(10, 110, 90, 110) for _ in range(20)]
    pos = range_position_pct(candles, n=20)
    assert pos == 100.0


def test_range_position_at_low():
    candles = [make_candle(10, 110, 90, 90) for _ in range(20)]
    pos = range_position_pct(candles, n=20)
    assert pos == 0.0


def test_range_position_mid():
    # range 90-110, close 100 → 50%
    candles = [make_candle(95, 110, 90, 100) for _ in range(20)]
    pos = range_position_pct(candles, n=20)
    assert abs(pos - 50.0) < 0.1
