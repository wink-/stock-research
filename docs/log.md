---
type: Log
title: Change Log
description: Chronological history of significant changes to stock-research.
tags: [log, history]
timestamp: 2026-07-18T00:00:00Z
---

# Change Log

## 2026-07-18

### Phase 1 shipped (commit `ea04b30`)

- Built `stock-research` Python package + CLI from scratch.
- All Phase 1 modules: config, models, 5 data fetchers, 2 analysis modules, report builder, markdown renderer, Jinja2 template.
- 32 unit tests passing, live KMI report verified end-to-end with Schwab data.
- Repo moved from `~/stock-research` to `~/projects/stock-research` (projects workspace convention). venv rebuilt.
- OKF docs bootstrapped: `AGENTS.md`, `docs/{index,architecture,setup,status,notes,log}.md`.

### schwab-py compatibility fixes (commit `ea04b30`)

- Replaced non-existent `get_price_history_everywhere` with typed helpers (`get_price_history_every_day`, etc.).
- Fixed enum paths: `Client.Options.ContractType` / `Client.Options.Strategy` (not `Client.ContractType`).
- Switched price history from period enums to `start_datetime`/`end_datetime` kwargs.
- Added stderr warning on options snapshot failure (was silently swallowed).
- Fixed Jinja template newline merge between div yield and shares lines.
