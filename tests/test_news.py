"""Tests for the news RSS parser (uses fixture)."""
from pathlib import Path
from stock_research.data.news_rss import fetch_news

# Test the parser by monkeypatching urlopen
FIXTURE = Path(__file__).parent / "fixtures" / "sample_news.xml"


def test_fetch_news_parses_fixture(monkeypatch):
    xml = FIXTURE.read_text()

    class FakeResp:
        def __init__(self, data): self.data = data.encode()
        def __enter__(self): return self
        def __exit__(self, *a): pass
        def read(self): return self.data

    import stock_research.data.news_rss as mod
    monkeypatch.setattr(
        mod.urllib.request, "urlopen",
        lambda req, timeout=15: FakeResp(xml)
    )

    items = fetch_news("KMI")
    assert len(items) == 3
    assert "Natural Gas" in items[0].title
    assert items[0].published.year == 2026
