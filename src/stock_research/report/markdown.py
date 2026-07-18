"""Markdown renderer using Jinja2 template."""
from __future__ import annotations
from datetime import datetime
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

TEMPLATE_DIR = Path(__file__).parent.parent / "templates"


def render_markdown(report) -> str:
    """Render a Report model to markdown via the preliminary template."""
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        autoescape=select_autoescape([]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    # Register a filter for friendly date formatting
    env.filters["datetime"] = lambda d: d.strftime("%Y-%m-%d %H:%M UTC") if d else ""

    template = env.get_template("preliminary.md.j2")
    return template.render(
        symbol=report.symbol,
        generated_at=report.generated_at.strftime("%Y-%m-%d %H:%M UTC"),
        quote=report.quote,
        fundamentals=report.fundamentals,
        technical=report.technical,
        levels=report.levels,
        options=report.options,
        news=report.news,
    )
