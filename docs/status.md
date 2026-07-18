---
type: Status
title: Project Status
description: Current phase, completed work, next tasks, blockers, and roadmap for stock-research.
tags: [status, roadmap]
timestamp: 2026-07-18T00:00:00Z
---

# Status: Phase 1 Shipped

## Completed (Phase 1)

- Repo bootstrap: `pyproject.toml`, src layout, venv, click CLI, 32 unit tests.
- Config: token path auto-resolution with MCP fallback.
- Models: `Quote`, `Fundamentals`, `Technical`, `Level`, `OptionsSnapshot`, `NewsItem`, `Report` (pydantic v2).
- Data layer:
  - Schwab quote + fundamentals parser (with fixture test).
  - Daily + intraday candles via typed schwab-py helpers.
  - Options snapshot: ATM IV, implied move, put/call OI walls.
  - Google News RSS fetcher (title + date + source).
- Analysis layer:
  - SMA(8/20/50/200), ATR(14), regime score (-100 to +100), range position.
  - Fractal pivot detection + tolerance-based level clustering.
- Report layer:
  - `build_report()` orchestrator with graceful degradation for optional sections.
  - Jinja2 markdown template + JSON output.
- CLI: `stock-research report SYMBOL`, `stock-research show PATH`.
- Live end-to-end verified with KMI (real Schwab data).
- Pushed to GitHub: https://github.com/wink-/stock-research

## Current Phase

Phase 1 done. Phase 2 (LLM narrative + enrichment) is next.

## Next Tasks (Phase 2)

1. **LLM narrative layer** — `stock-research narrative KMI` reads the JSON, calls Gemini Flash Lite (cheap) to synthesize prose, appends a "## Analyst Narrative" section. Prompt compact (~800 tokens of data in, ~500 tokens out).
2. **Analyst PT scraper** — MarketBeat forecast page → consensus PT / high / low, injected into JSON. Respectful, cached 24h.
3. **Compare mode** — `stock-research compare KMI WMB ENB` side-by-side table from multiple JSON reports.
4. **GBrain publisher** — `stock-research publish KMI` writes the markdown to GBrain as `trading/research/{symbol}`, linking to `trading/{symbol}-thesis` if it exists.

## Future (Phase 3)

- Hugo static site render (markdown → `site/content/research/`), optional deploy to streetcats.tech.
- Consensus radar integration (LLM panel for crowd-sentiment read).

## Blockers / Risks

- **schwab-py API drift**: the typed helpers (`get_price_history_every_day`) and enum locations (`Client.Options.ContractType`) are not in older docs. If schwab-py updates, these may move. Mitigation: warnings logged to stderr, graceful degradation.
- **Options chain size**: full chain is ~350KB JSON. Currently parsed in memory. If we expand to multi-expiry GEX walls, may need streaming or temp-file persistence (see `references/0dte-gex-walls.md` pattern in the trading skill).
- **News RSS rate limits**: Google News will throttle aggressive polling. Current use is one pull per report; fine.

## Verification

```bash
.venv/bin/pytest -v                              # 32/32 unit tests
set -a && . ~/tools/schwab-marketdata-mcp/.env && set +a
.venv/bin/stock-research report KMI              # live end-to-end
```
