"""CLI: stock-research report SYMBOL."""
from __future__ import annotations
from pathlib import Path
import json
import click
from stock_research.config import Config
from stock_research.report.builder import build_report
from stock_research.report.markdown import render_markdown


@click.group()
def main():
    """Stock research report generator."""


@main.command()
@click.argument("symbol")
@click.option("--no-options", is_flag=True, help="Skip options snapshot")
@click.option("--no-news", is_flag=True, help="Skip news fetch")
@click.option("--out", type=click.Path(), default="reports", help="Output directory")
@click.option("--json-only", is_flag=True, help="Write JSON only, no markdown")
def report(symbol, no_options, no_news, out, json_only):
    """Generate a preliminary research report for SYMBOL."""
    cfg = Config.from_env()
    click.echo(f"Building report for {symbol.upper()}...", err=True)
    r = build_report(
        symbol.upper(),
        config=cfg,
        include_options=not no_options,
        include_news=not no_news,
    )
    outdir = Path(out)
    outdir.mkdir(exist_ok=True, parents=True)
    datestr = r.generated_at.strftime("%Y%m%d")
    base = outdir / f"{r.symbol}_{datestr}"

    if not json_only:
        md = render_markdown(r)
        md_path = Path(str(base) + ".md")
        md_path.write_text(md)
        click.echo(f"Wrote markdown: {md_path}", err=True)

    json_path = Path(str(base) + ".json")
    json_path.write_text(r.model_dump_json(indent=2))
    click.echo(f"Wrote JSON: {json_path}", err=True)

    # Short stdout summary
    click.echo(
        f"{r.symbol}: last=${r.quote.last:.2f} "
        f"({r.quote.change_pct:+.2f}%) "
        f"regime={r.technical.regime_label} "
        f"({r.technical.regime_score})"
    )


@main.command()
@click.argument("path", type=click.Path(exists=True))
def show(path):
    """Print a saved report JSON as markdown."""
    from stock_research.models import Report
    data = json.loads(Path(path).read_text())
    r = Report(**data)
    click.echo(render_markdown(r))


if __name__ == "__main__":
    main()
