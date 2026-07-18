"""News fetcher: Google News RSS (titles + dates only)."""
from __future__ import annotations
import urllib.request
import urllib.parse
from datetime import datetime, timezone
from xml.etree import ElementTree as ET
from stock_research.models import NewsItem


NS = {"atom": "http://www.w3.org/2005/Atom", "media": "http://search.yahoo.com/mrss/"}


def fetch_news(symbol: str, query: str | None = None, limit: int = 12) -> list[NewsItem]:
    """Pull Google News RSS items for a symbol.

    Args:
        symbol: ticker, e.g. "KMI"
        query: optional full-text query (defaults to symbol alone)
        limit: max items
    """
    q = query or symbol
    url = (
        "https://news.google.com/rss/search?q="
        + urllib.parse.quote(q)
        + "&hl=en-US&gl=US&ceid=US:en"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "stock-research/0.1"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            xml = resp.read().decode("utf-8", errors="ignore")
    except Exception:
        return []

    items: list[NewsItem] = []
    try:
        root = ET.fromstring(xml)
    except ET.ParseError:
        return []

    for item in root.iter("item"):
        title_el = item.find("title")
        pub_el = item.find("pubDate")
        src_el = item.find("source")
        if title_el is None or title_el.text is None:
            continue
        title = title_el.text
        # Google News titles often end with " - Source Name"
        source = ""
        if src_el is not None and src_el.text:
            source = src_el.text
        published = datetime.now(timezone.utc)
        if pub_el is not None and pub_el.text:
            try:
                # RFC 822: "Wed, 08 Jul 2026 07:00:00 GMT"
                published = datetime.strptime(
                    pub_el.text, "%a, %d %b %Y %H:%M:%S %Z"
                ).replace(tzinfo=timezone.utc)
            except ValueError:
                pass
        items.append(NewsItem(title=title, published=published, source=source))
        if len(items) >= limit:
            break
    return items
