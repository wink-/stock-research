# stock-research

Programmatic stock research report generator. Pulls quotes, fundamentals, price history, options chain, and news from free sources (Schwab API, Google News RSS), computes technical indicators locally, and renders clean markdown + JSON reports. Designed to save LLM tokens on equity research — read the 2-3k token markdown instead of 50-80k tokens of raw API JSON.

## Install

```bash
git clone https://github.com/wink-/stock-research.git
cd stock-research
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
```

## Configure

Set Schwab app credentials (get these from the [Schwab Developer Portal](https://developer.schwab.com/)):

```bash
export SCHWAB_APP_KEY=your_app_key
export SCHWAB_APP_SECRET=your_app_secret
```

The tool reads an existing OAuth token from one of:
- `~/.local/state/schwab-marketdata-mcp/token.json` (primary)
- `~/.hermes/profiles/trader/home/.local/state/schwab-marketdata-mcp/token.json` (fallback)

Run the [schwab-marketdata-mcp](https://github.com/your-org/schwab-marketdata-mcp) manual auth flow to create it.

## Usage

```bash
# Full report
stock-research report KMI

# Skip options/news for speed
stock-research report KMI --no-options --no-news

# Render a saved JSON back to markdown
stock-research show reports/KMI_20260717.json
```

Outputs:
- `reports/SYMBOL_YYYYMMDD.md` — human-readable preliminary report
- `reports/SYMBOL_YYYYMMDD.json` — structured data for downstream tools

## What the report contains

- **Quote** — last, bid/ask, day range, 52-week range, volume, name
- **Fundamentals** — P/E, EPS, div yield, shares outstanding, last earnings
- **Technical** — SMA(8/20/50/200), ATR(14), regime score (-100 to +100), range position
- **Support/Resistance** — fractal pivot clusters with touch counts
- **Options snapshot** — nearest monthly expiry, ATM IV, implied move, put/call OI walls
- **News** — recent Google News headlines (title + date + source)

## Development

```bash
.venv/bin/pytest -v          # 32 unit tests
.venv/bin/pytest --cov=src   # coverage
```

## Architecture

```
src/stock_research/
├── cli.py                    # click CLI
├── config.py                 # paths + Schwab app creds
├── models.py                 # pydantic v2 models
├── data/                     # fetchers (Schwab, news)
├── analysis/                 # indicators (SMA, ATR, regime, pivots)
├── report/                   # builder + markdown renderer
└── templates/                # Jinja2 templates
```

Read-only, no brokerage endpoints. Token cost per report: ~0 LLM tokens for the data layer (all local computation); optional LLM narrative layer in Phase 2.

<!-- PROJECT-DOCS:START -->
## Project Documentation

Supplemental OKF-style documentation lives in [docs/index.md](docs/index.md). Start with `README.md` (this file), then `docs/index.md` for progressive disclosure.

### Key Docs

- [docs/index.md](docs/index.md) - Entry point and navigation
- [docs/architecture.md](docs/architecture.md) - Structure, subsystems, key files
- [docs/setup.md](docs/setup.md) - How to get running locally
- [docs/status.md](docs/status.md) - Current phase, roadmap, what to work on next
- [docs/notes.md](docs/notes.md) - Gotchas, solutions, tribal knowledge
- [docs/log.md](docs/log.md) - Chronological history of changes
<!-- PROJECT-DOCS:END -->

## License

MIT
