"""Options chain snapshot: ATM IV, implied move, OI walls."""
from __future__ import annotations
from datetime import date, datetime, timezone
import math
from schwab.client import Client
from stock_research.models import OptionsSnapshot


def _exp_to_date(exp_str: str) -> date:
    """Parse '2026-08-21T21:00:00.000+00:00' or '2026-08-21'."""
    try:
        return datetime.fromisoformat(exp_str).date()
    except Exception:
        try:
            return date.fromisoformat(exp_str[:10])
        except Exception:
            return date.today()


def snapshot_from_chain(chain: dict, today: date | None = None) -> OptionsSnapshot:
    """Build OptionsSnapshot from Schwab option chain JSON.

    Picks the first standard monthly expiry >= 21 DTE for IV/move,
    and identifies put/call OI walls.
    """
    today = today or date.today()
    underlying_price = float(chain.get("underlyingPrice") or 0.0)

    # Find first monthly expiry with >= 21 DTE
    call_map = chain.get("callExpDateMap", {})
    put_map = chain.get("putExpDateMap", {})
    all_exps = sorted(set(list(call_map.keys()) + list(put_map.keys())))

    target_exp_key = None
    target_dte = None
    for exp_key in all_exps:
        # exp_key looks like "2026-08-21:21"
        exp_str = exp_key.split(":")[0]
        exp_date = _exp_to_date(exp_str)
        dte = (exp_date - today).days
        if dte >= 21:
            target_exp_key = exp_key
            target_dte = dte
            break

    if target_exp_key is None and all_exps:
        target_exp_key = all_exps[0]
        exp_str = target_exp_key.split(":")[0]
        target_dte = (_exp_to_date(exp_str) - today).days

    if target_exp_key is None:
        return OptionsSnapshot(
            expiry=date.today(), dte=0, atm_iv=None,
            implied_move=None, put_oi_cluster=None, call_oi_cluster=None,
            put_wall=None, call_wall=None,
        )

    exp_date = _exp_to_date(target_exp_key.split(":")[0])

    # ATM IV: find call strike closest to underlying_price
    calls = call_map.get(target_exp_key, {})
    atm_iv = None
    if calls and underlying_price > 0:
        strikes = sorted(float(k) for k in calls.keys())
        atm_strike = min(strikes, key=lambda s: abs(s - underlying_price))
        atm_key = str(int(atm_strike)) if float(int(atm_strike)) == atm_strike else str(atm_strike)
        # try both int and float key forms
        atm_opt = calls.get(atm_key) or calls.get(str(atm_strike))
        if atm_opt:
            iv = atm_opt[0].get("volatility")
            if iv:
                atm_iv = float(iv)

    # Implied move: spot * IV * sqrt(dte/365)
    implied_move = None
    if atm_iv and target_dte and target_dte > 0:
        implied_move = round(
            underlying_price * (atm_iv / 100.0) * math.sqrt(target_dte / 365.0), 2
        )

    # OI walls: max OI strikes for puts (below) and calls (above)
    puts = put_map.get(target_exp_key, {})
    put_wall = _max_oi_strike(puts, below=underlying_price)
    call_wall = _max_oi_strike(calls, above=underlying_price)
    put_cluster = _max_oi_strike(puts)
    call_cluster = _max_oi_strike(calls)

    return OptionsSnapshot(
        expiry=exp_date,
        dte=target_dte or 0,
        atm_iv=atm_iv,
        implied_move=implied_move,
        put_oi_cluster=put_cluster,
        call_oi_cluster=call_cluster,
        put_wall=put_wall,
        call_wall=call_wall,
    )


def _max_oi_strike(
    strike_map: dict, below: float | None = None, above: float | None = None
) -> float | None:
    if not strike_map:
        return None
    best_strike = None
    best_oi = -1
    for strike, opts in strike_map.items():
        s = float(strike)
        if below is not None and s >= below:
            continue
        if above is not None and s <= above:
            continue
        oi = sum(int(o.get("openInterest", 0) or 0) for o in opts)
        if oi > best_oi:
            best_oi = oi
            best_strike = s
    return best_strike


def fetch_options_snapshot(client, symbol: str, today: date | None = None) -> OptionsSnapshot:
    """Live fetch nearest standard monthly chain."""
    resp = client.get_option_chain(
        symbol,
        contract_type=Client.Options.ContractType.ALL,
        strategy=Client.Options.Strategy.SINGLE,
        strike_count=30,
        include_underlying_quote=True,
    )
    chain = resp.json()
    return snapshot_from_chain(chain, today=today)
