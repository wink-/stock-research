---
type: Notes
title: Notes and Gotchas
description: Non-obvious quirks, decisions, and tribal knowledge for stock-research.
tags: [notes, gotchas, schwab-py, jinja]
timestamp: 2026-07-18T00:00:00Z
---

# Notes

## schwab-py API Surface

The typed client does NOT use a generic `get_price_history_everywhere` method. It uses per-frequency helpers:

- `client.get_price_history_every_day(symbol, start_datetime=..., end_datetime=...)`
- `client.get_price_history_every_minute(...)`
- `client.get_price_history_every_five_minutes(...)`
- `client.get_price_history_every_ten_minutes(...)`
- `client.get_price_history_every_fifteen_minutes(...)`
- `client.get_price_history_every_thirty_minutes(...)`
- `client.get_price_history_every_week(...)`

These take `start_datetime` / `end_datetime` (timezone-aware datetime objects), NOT `period_type` / `period` enums. The `period_type`/`period` kwargs belong to the raw `get_price_history()` method only.

### Option Chain Enums

Enums live at `Client.Options.*`, NOT `Client.ContractType`:

- `Client.Options.ContractType.ALL`
- `Client.Options.ContractType.CALL`
- `Client.Options.ContractType.PUT`
- `Client.Options.Strategy.SINGLE`
- `Client.Options.Strategy.COVERED`
- etc.

`Client.PriceHistory.PeriodType.MONTH` is real and is used for the raw `get_price_history()` method.

### Auth

```python
from schwab.auth import client_from_token_file
client = client_from_token_file(token_path=..., api_key=..., app_secret=...)
```

App credentials live in `~/tools/schwab-marketdata-mcp/.env` (`SCHWAB_APP_KEY`, `SCHWAB_APP_SECRET`). Token at:
- `~/.local/state/schwab-marketdata-mcp/token.json` (primary)
- `~/.hermes/profiles/trader/home/.local/state/schwab-marketdata-mcp/token.json` (fallback — the MCP-vs-trader-profile path mismatch quirk)

Token refresh lifetime is ~7 days. After that, re-run the manual OAuth flow.

## Jinja2 + trim_blocks

`Environment(trim_blocks=True, lstrip_blocks=True)` is the right default for markdown templates — it strips the newline after `{% block %}` tags so you don't get blank lines.

BUT: inline `{% if x %}...{% endif %}` blocks also eat the trailing newline, which merges the line with the next one. Example that broke:

```jinja
- **Div yield:** {{ x }}{% if y %} (extra){% endif %}
- **Shares:** {{ z }}      ← this merged onto the div line
```

Fix: use inline conditional expressions instead of block tags when the content stays on one line:

```jinja
- **Div yield:** {{ x }}{{ " (extra)" if y else "" }}
- **Shares:** {{ z }}
```

## venv Path Sensitivity

The venv has absolute paths baked into `bin/python`, `bin/pip`, and the `stock-research` console script. If you move the repo (e.g. `~/stock-research` → `~/projects/stock-research`), the venv breaks with `ModuleNotFoundError`. Fix:

```bash
rm -rf .venv && python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"
```

## Options Snapshot Failure Modes

The snapshot picks the first standard monthly expiry ≥ 21 DTE. If a ticker has no monthly expiries (some ETFs, low-volume names), it falls back to the first available. OI walls look for max open interest below spot (put wall) and above spot (call wall); if all OI is on one side, the other wall is `None`.

Always wrap `fetch_options_snapshot` in try/except and log to stderr — never let it crash the whole report. Options data is enrichment, not core.

## News RSS Quirks

Google News titles often end with ` - Source Name`. We pull `<source>` element separately when present, so the title retains the suffix. Not a bug — just don't be surprised.

Publication dates are RFC 822 format (`Wed, 08 Jul 2026 07:00:00 GMT`). The parser is strict; bad dates fall back to `datetime.now(UTC)`.

## Regime Score Calibration

The regime score (-100 to +100) is a simplified version of the candle-analyzer logic. Components:

| Signal | Points |
|--------|--------|
| close > open | +10 (−5 if down) |
| close in upper half of range | +10 (−5 if lower) |
| close > SMA20 | +15 (−10 if below) |
| close > SMA50 | +10 (−5 if below) |
| SMA8 > SMA20 | +10 (−5 if below) |
| rising SMA20 (3-period slope) | +5 |
| higher high + higher low | +10 (−10 if both lower) |
| long upper wick (>40% of range) | −10 |

Labels: ≥40 bullish, ≥10 neutral-bullish, ≥−10 neutral, ≥−40 neutral-bearish, else bearish.

This is intentionally simpler than candle-analyzer's full profile system. For the agent's deeper analysis, defer to the `candle-analyzer` MCP tool.
