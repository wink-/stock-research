"""Support/resistance: pivot detection and clustering."""
from __future__ import annotations
from typing import Sequence


def pivot_points(candles: Sequence[dict], window: int = 3) -> list[dict]:
    """Find fractal pivot highs/lows.

    A pivot high at i means candles[i].high is the max high in
    [i-window, i+window]. Symmetric for pivot lows.

    Returns list of {price, kind, i, date?}.
    """
    pivots: list[dict] = []
    if len(candles) < 2 * window + 1:
        return pivots
    for i in range(window, len(candles) - window):
        h = candles[i]["high"]
        l = candles[i]["low"]
        is_high = all(
            h >= candles[j]["high"] for j in range(i - window, i + window + 1) if j != i
        )
        is_low = all(
            l <= candles[j]["low"] for j in range(i - window, i + window + 1) if j != i
        )
        item = {"i": i}
        if "datetime" in candles[i]:
            item["datetime"] = candles[i]["datetime"]
        if is_high:
            pivots.append({"price": h, "kind": "resistance", **item})
        if is_low:
            pivots.append({"price": l, "kind": "support", **item})
    return pivots


def cluster_levels(
    pivots: Sequence[dict],
    tolerance: float = 0.02,
    last_price: float | None = None,
) -> list[dict]:
    """Cluster pivots within tolerance into levels.

    tolerance is a fraction (0.02 = 2%). Returns sorted list of
    {price, kind, strength, count} where strength is touch count.
    """
    if not pivots:
        return []
    # sort by price
    sorted_pivots = sorted(pivots, key=lambda p: p["price"])
    ref = last_price if last_price else sorted_pivots[0]["price"]

    clusters: list[list[dict]] = []
    current: list[dict] = []
    for p in sorted_pivots:
        if not current:
            current = [p]
            continue
        # cluster if within tolerance of current cluster mean
        mean = sum(x["price"] for x in current) / len(current)
        if abs(p["price"] - mean) <= tolerance * ref:
            current.append(p)
        else:
            clusters.append(current)
            current = [p]
    if current:
        clusters.append(current)

    levels: list[dict] = []
    for cluster in clusters:
        # majority kind wins
        kinds = [x["kind"] for x in cluster]
        kind = max(set(kinds), key=kinds.count)
        mean_price = sum(x["price"] for x in cluster) / len(cluster)
        levels.append({
            "price": round(mean_price, 4),
            "kind": kind,
            "strength": len(cluster),
        })
    return sorted(levels, key=lambda l: l["price"])
