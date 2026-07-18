---
okf_version: "0.1"
---

# Stock Research Documentation

## Overview

* [Architecture](architecture.md) - Runtime shape, subsystems, and file layout.
* [Setup](setup.md) - How to get running locally.
* [Status](status.md) - Current phase and roadmap.
* [Notes](notes.md) - Gotchas and tribal knowledge.
* [Log](log.md) - Chronological history of changes.

## Project Info

- **Repository**: [stock-research](https://github.com/wink-/stock-research)
- **Language**: Python 3.11+
- **Description**: Programmatic stock research report generator. Pulls Schwab market data + news, computes technicals locally, renders markdown + JSON.

## Public Surfaces

- CLI: `stock-research report SYMBOL`, `stock-research show PATH`
- Report outputs: `reports/SYMBOL_YYYYMMDD.md`, `reports/SYMBOL_YYYYMMDD.json`
- No web server, no HTTP API. CLI-only in v1.

## Data Sources

- Schwab API via `schwab-py` (quotes, fundamentals, price history, options chain)
- Google News RSS (titles + dates only, no article content)
- Future: analyst PT scraper, LLM narrative layer (Phase 2)
