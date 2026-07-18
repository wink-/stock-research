---
type: Setup
title: Quick Start
description: How to install, run, test, and smoke-test stock-research locally.
tags: [setup, python, schwab]
timestamp: 2026-07-18T00:00:00Z
---

# Quick Start

## Requirements

- Python 3.11+
- Schwab Developer Portal app (for API credentials)
- Existing Schwab OAuth token (created via the `schwab-marketdata-mcp` auth flow)

## Install

```bash
cd ~/projects/stock-research
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
```

## Configure

Schwab app credentials (from [Schwab Developer Portal](https://developer.schwab.com/)):

```bash
export SCHWAB_APP_KEY=your_app_key
export SCHWAB_APP_SECRET=your_app_secret
```

Or source the existing MCP env file:

```bash
set -a && . ~/tools/schwab-marketdata-mcp/.env && set +a
```

The tool auto-discovers an OAuth token at:
- `~/.local/state/schwab-marketdata-mcp/token.json` (primary)
- `~/.hermes/profiles/trader/home/.local/state/schwab-marketdata-mcp/token.json` (fallback)

## Run

```bash
# Full report
.venv/bin/stock-research report KMI

# Skip options/news for speed
.venv/bin/stock-research report KMI --no-options --no-news

# Re-render a saved JSON as markdown
.venv/bin/stock-research show reports/KMI_20260718.json
```

Outputs:
- `reports/SYMBOL_YYYYMMDD.md` — human-readable report
- `reports/SYMBOL_YYYYMMDD.json` — structured data for downstream tools

## Test

```bash
.venv/bin/pytest -v           # 32 unit tests
.venv/bin/pytest --cov=src    # coverage
```

## Smoke Test (requires live Schwab access)

```bash
set -a && . ~/tools/schwab-marketdata-mcp/.env && set +a
.venv/bin/stock-research report KMI
cat reports/KMI_$(date +%Y%m%d).md
```

Expect: quote, fundamentals, technicals, support/resistance table, options snapshot (IV + implied move + walls), and recent news — all populated.

## Troubleshooting

- **`FileNotFoundError: Schwab token not found`** — run the `schwab-marketdata-mcp` manual auth flow, then check the token path.
- **`ModuleNotFoundError: No module named 'stock_research'`** after moving the repo — rebuild the venv: `rm -rf .venv && python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"`.
- **Options section empty** — check stderr for `[warn] options snapshot failed`. Most likely an enum path drift in schwab-py; see `docs/notes.md`.
