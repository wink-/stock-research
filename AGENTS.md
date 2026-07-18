# Agent Instructions: stock-research

## Project Purpose

`stock-research` is a Python CLI that generates preliminary stock research reports from programmatic data sources (Schwab API, Google News RSS), with deterministic technical analysis computed locally. It outputs clean markdown + JSON reports designed to save LLM tokens on equity research — read the 2-3k token markdown instead of 50-80k tokens of raw API JSON.

<!-- PROJECTS-DOCS-START -->
## Documentation

`README.md` remains the repository overview and should not be overwritten by documentation automation. Supplemental project documentation lives in `docs/`. Start with `README.md` when present, then use `docs/index.md` for progressive disclosure.

### Key Docs

- `docs/index.md` - Entry point and navigation
- `docs/architecture.md` - Structure, subsystems, key files
- `docs/setup.md` - How to get running locally
- `docs/status.md` - Current phase, roadmap, what to work on next
- `docs/notes.md` - Gotchas, solutions, tribal knowledge
- `docs/log.md` - Chronological history of changes

### Doc Workflow

1. Read `README.md`, then `docs/index.md` for an overview.
2. Check `docs/status.md` to see what is next.
3. Read `docs/notes.md` for guardrails and gotchas before starting work.
4. Update `docs/status.md` when you complete tasks.
5. Add notes to `docs/notes.md` if you learn something non-obvious.
6. Log significant changes in `docs/log.md`.
7. Do not overwrite `README.md`; only update a marked `PROJECT-DOCS` block if explicitly asked.
<!-- PROJECTS-DOCS-END -->

## Hard Guardrails

- Read-only market data only. No brokerage endpoints, no order placement, no account access.
- No buy/sell/hold recommendations. Reports present data, not advice.
- No secrets in repo, logs, screenshots, docs, or generated reports. `.env`, `token.json`, `*.key`, `secrets/` are gitignored.
- Schwab credentials come from env vars (`SCHWAB_APP_KEY`, `SCHWAB_APP_SECRET`) or `~/tools/schwab-marketdata-mcp/.env`. Never commit them.
- Options data is availability/context only and must not become a trade recommendation.
- All deterministic math (indicators, pivots, regime) must have unit tests.

## Key Files

- CLI entry: `src/stock_research/cli.py`
- Config + token resolution: `src/stock_research/config.py`
- Pydantic models: `src/stock_research/models.py`
- Data fetchers: `src/stock_research/data/{fundamentals,price_history,options_snapshot,news_rss,schwab_client}.py`
- Analysis: `src/stock_research/analysis/{technical,levels}.py`
- Report builder + renderer: `src/stock_research/report/{builder,markdown}.py`
- Template: `src/stock_research/templates/preliminary.md.j2`
- Tests: `tests/test_*.py` + `tests/fixtures/`

## Standard Commands

```bash
# Install
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"

# Run a report
set -a && . ~/tools/schwab-marketdata-mcp/.env && set +a
.venv/bin/stock-research report KMI

# Re-render a saved JSON as markdown
.venv/bin/stock-research show reports/KMI_20260718.json

# Tests
.venv/bin/pytest -v
```

Before handoff, run:

```bash
.venv/bin/pytest -v
```

## Architecture Rules

- Keep data fetching isolated in `data/` modules; one provider per file.
- Keep all deterministic analysis in `analysis/` — no network calls there.
- Models in `models.py` are the single source of truth for report shape; update the schema there, not in the template.
- Template (`*.j2`) renders a `Report` model — no business logic in templates.
- New data sources go behind a `fetch_*` function that returns model instances, never raw dicts.
- Failures in optional sections (options, news) must degrade gracefully — log a warning to stderr, leave the field None, keep the report rendering.
