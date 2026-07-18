"""Technical indicators: SMA, ATR, regime score."""
from __future__ import annotations
from typing import Sequence


def compute_sma(closes: Sequence[float], n: int) -> float | None:
    """Simple moving average of last n closes. None if not enough data."""
    if len(closes) < n:
        return None
    return sum(closes[-n:]) / n


def compute_atr(candles: Sequence[dict], n: int = 14) -> float | None:
    """Average True Range over last n candles.

    Each candle dict must have: high, low, close.
    Uses prior close for true range calculation.
    """
    if len(candles) < n + 1:
        return None
    trs = []
    for i in range(-n, 0):
        h = candles[i]["high"]
        l = candles[i]["low"]
        pc = candles[i - 1]["close"]
        tr = max(h - l, abs(h - pc), abs(l - pc))
        trs.append(tr)
    return sum(trs) / len(trs)


def regime_score(candles: Sequence[dict]) -> tuple[int, str]:
    """Simplified regime score from -100 to +100.

    Returns (score, label). Labels:
      score >= 40  -> "bullish"
      score >= 10  -> "neutral-bullish"
      score >= -10 -> "neutral"
      score >= -40 -> "neutral-bearish"
      else         -> "bearish"
    """
    if len(candles) < 5:
        return 0, "neutral"

    last = candles[-1]
    prev = candles[-2]
    closes = [c["close"] for c in candles]
    highs = [c["high"] for c in candles]
    lows = [c["low"] for c in candles]

    score = 0
    # close > open (+10)
    if last["close"] > last["open"]:
        score += 10
    elif last["close"] < last["open"]:
        score -= 5
    # close in upper half of range (+10)
    rng = last["high"] - last["low"]
    if rng > 0 and last["close"] > last["low"] + rng / 2:
        score += 10
    elif rng > 0 and last["close"] < last["low"] + rng / 2:
        score -= 5
    # close > sma20 (+15)
    sma20 = compute_sma(closes, 20) if len(closes) >= 20 else None
    if sma20 and last["close"] > sma20:
        score += 15
    elif sma20 and last["close"] < sma20:
        score -= 10
    # close > sma50 (+10)
    sma50 = compute_sma(closes, 50) if len(closes) >= 50 else None
    if sma50 and last["close"] > sma50:
        score += 10
    elif sma50 and last["close"] < sma50:
        score -= 5
    # sma8 > sma20 (+10)
    sma8 = compute_sma(closes, 8) if len(closes) >= 8 else None
    if sma8 and sma20 and sma8 > sma20:
        score += 10
    elif sma8 and sma20 and sma8 < sma20:
        score -= 5
    # rising sma20 (slope over last 3 periods) (+5)
    if sma20 and len(closes) >= 23:
        prior_sma = sum(closes[-23:-3]) / 20
        if sma20 > prior_sma:
            score += 5
    # higher high + higher low vs prior (+10)
    if last["high"] > prev["high"] and last["low"] > prev["low"]:
        score += 10
    elif last["high"] < prev["high"] and last["low"] < prev["low"]:
        score -= 10
    # long upper wick (-10): rejection from highs
    body_top = max(last["open"], last["close"])
    upper_wick = last["high"] - body_top
    if rng > 0 and upper_wick > rng * 0.4:
        score -= 10

    if score >= 40:
        label = "bullish"
    elif score >= 10:
        label = "neutral-bullish"
    elif score >= -10:
        label = "neutral"
    elif score >= -40:
        label = "neutral-bearish"
    else:
        label = "bearish"
    return score, label


def range_position_pct(candles: Sequence[dict], n: int = 20) -> float | None:
    """Where the close sits in the last n-period range, as 0-100.

    100 = at the high, 0 = at the low.
    """
    if len(candles) < n:
        return None
    window = candles[-n:]
    hi = max(c["high"] for c in window)
    lo = min(c["low"] for c in window)
    close = candles[-1]["close"]
    if hi == lo:
        return 50.0
    return (close - lo) / (hi - lo) * 100
