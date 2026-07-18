---
type: Architecture
title: Architecture
description: Runtime shape, subsystems, data flow, and key files for stock-research.
tags: [architecture, python, cli]
timestamp: 2026-07-18T00:00:00Z
---

# Architecture

## Shape

CLI tool. One command per concern. No long-running process, no server, no state between runs. Each `report SYMBOL` invocation is a fresh pipeline: fetch → analyze → render → write.

## Subsystems

```
src/stock_research/
├── cli.py                 # click CLI: report, show
├── config.py              # token path resolution, env creds
├── models.py              # pydantic v2 models (Report schema)
├── data/                  # fetchers (network calls live here)
│   ├── schwab_client.py   # auth from token file
│   ├── fundamentals.py    # quote + fundamentals parser
│   ├── price_history.py   # daily + intraday candles
│   ├── options_snapshot.py# chain → IV, implied move, OI walls
│   └── news_rss.py        # Google News RSS
├── analysis/              # deterministic math (no network)
│   ├── technical.py       # SMA, ATR, regime score, range position
│   └── levels.py          # fractal pivots, level clustering
├── report/                # assembly + rendering
│   ├── builder.py         # orchestrates fetchers → Report model
│   └── markdown.py        # Jinja2 render
└── templates/
    └── preliminary.md.j2  # the report template
```

## Data Flow

```
cli.report(SYMBOL)
  → config.from_env()                      # resolves SCHWAB_APP_KEY/SECRET, token path
  → get_client(cfg)                        # schwab-py client_from_token_file
  → build_report(SYMBOL, cfg, client)
      ├─ fetch_quote(client, SYMBOL)       → Quote, Fundamentals
      ├─ fetch_daily_candles(client, ...)  → list[dict]
      │     └─ compute_sma/atr/regime      → Technical
      │     └─ pivot_points/cluster_levels → list[Level]
      ├─ fetch_options_snapshot(client,..) → OptionsSnapshot (optional, warns on fail)
      └─ fetch_news(SYMBOL)                → list[NewsItem] (optional)
  → render_markdown(report)                → string
  → write reports/SYMBOL_DATE.md + .json
```

## Key Files

- `models.py` — single source of truth for report shape. Add fields here first.
- `report/builder.py` — orchestrator. The seam where fetchers compose into a Report.
- `data/options_snapshot.py` — most fragile; Schwab enums live at `Client.Options.*`, expiry parsing handles multiple string formats.
- `templates/preliminary.md.j2` — Jinja2 with `trim_blocks=True`; inline conditionals preferred over `{% if %}` blocks to preserve newlines.

## Token Strategy

Each report costs ~0 LLM tokens for the data layer (all local computation). The markdown output is ~2-3k tokens vs. 50-80k tokens of raw API JSON that the agent would otherwise pull into context. Phase 2 adds an optional LLM narrative pass that reads the JSON and writes prose — one cheap call vs. many.

## Failure Modes

- Schwab token expired → `FileNotFoundError` from `get_client`. Re-run the MCP auth flow.
- Options chain enum mismatch → caught, logged to stderr, `options=None` in report.
- News RSS down → caught, empty list, section renders as "No recent news items."
- Rate limit (429) → schwab-py retries internally; propagates as HTTPError if exhausted.
