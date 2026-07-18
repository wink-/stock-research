"""Tests for support/resistance pivot detection."""
from stock_research.analysis.levels import pivot_points, cluster_levels


def make_candle(o, h, l, c, dt=None):
    d = {"open": o, "high": h, "low": l, "close": c}
    if dt is not None:
        d["datetime"] = dt
    return d


def test_pivot_high_detection():
    """A clear peak should be detected as a resistance pivot."""
    # prices around a peak at index 5
    candles = [
        make_candle(10, 11, 10, 10),   # 0
        make_candle(10, 12, 10, 11),   # 1
        make_candle(11, 13, 11, 12),   # 2
        make_candle(12, 14, 12, 13),   # 3
        make_candle(13, 15, 13, 14),   # 4
        make_candle(14, 20, 14, 15),   # 5 PEAK high=20
        make_candle(15, 15, 10, 11),   # 6
        make_candle(11, 12, 10, 10),   # 7
        make_candle(10, 11, 9, 10),    # 8
        make_candle(10, 11, 9, 10),    # 9
        make_candle(10, 11, 9, 10),    # 10
    ]
    pivots = pivot_points(candles, window=3)
    highs = [p for p in pivots if p["kind"] == "resistance"]
    assert any(abs(p["price"] - 20) < 0.001 for p in highs)


def test_pivot_low_detection():
    """A clear trough should be detected as a support pivot."""
    candles = [
        make_candle(20, 21, 20, 20),
        make_candle(20, 21, 20, 19),
        make_candle(19, 20, 18, 18),
        make_candle(18, 19, 17, 17),
        make_candle(17, 18, 16, 16),
        make_candle(16, 17, 10, 11),   # TROUGH low=10
        make_candle(11, 16, 11, 15),
        make_candle(15, 17, 15, 16),
        make_candle(16, 18, 16, 17),
        make_candle(17, 19, 17, 18),
        make_candle(18, 20, 18, 19),
    ]
    pivots = pivot_points(candles, window=3)
    lows = [p for p in pivots if p["kind"] == "support"]
    assert any(abs(p["price"] - 10) < 0.001 for p in lows)


def test_pivot_too_short():
    candles = [make_candle(10, 11, 10, 10) for _ in range(4)]
    assert pivot_points(candles, window=3) == []


def test_cluster_levels_groups_nearby():
    pivots = [
        {"price": 100.0, "kind": "resistance", "i": 5},
        {"price": 101.0, "kind": "resistance", "i": 10},
        {"price": 150.0, "kind": "resistance", "i": 15},
    ]
    levels = cluster_levels(pivots, tolerance=0.02, last_price=100.0)
    # first two should cluster (within 2% of 100)
    assert len(levels) == 2
    cluster1 = [l for l in levels if l["price"] < 110][0]
    assert cluster1["strength"] == 2


def test_cluster_levels_support_resistance_kind_majority():
    pivots = [
        {"price": 50.0, "kind": "support", "i": 1},
        {"price": 50.5, "kind": "support", "i": 5},
        {"price": 51.0, "kind": "resistance", "i": 9},
    ]
    levels = cluster_levels(pivots, tolerance=0.05, last_price=50.0)
    assert len(levels) == 1
    assert levels[0]["kind"] == "support"  # majority wins


def test_cluster_empty():
    assert cluster_levels([], tolerance=0.02) == []


def test_cluster_sorted_by_price():
    pivots = [
        {"price": 200.0, "kind": "resistance", "i": 1},
        {"price": 100.0, "kind": "support", "i": 5},
        {"price": 150.0, "kind": "resistance", "i": 9},
    ]
    levels = cluster_levels(pivots, tolerance=0.005, last_price=150.0)
    prices = [l["price"] for l in levels]
    assert prices == sorted(prices)
