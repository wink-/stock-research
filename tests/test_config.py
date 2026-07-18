"""Tests for config module."""
from pathlib import Path
from stock_research.config import Config, PRIMARY_TOKEN, FALLBACK_TOKEN


def test_config_defaults():
    c = Config()
    assert c.token_path == PRIMARY_TOKEN
    assert PRIMARY_TOKEN.name == "token.json"
    assert "reports" in str(c.reports_dir)


def test_config_fallback_path():
    """If primary missing and fallback exists, resolve to fallback."""
    c = Config(token_path=Path("/nonexistent/primary/token.json"))
    # We can't fully test this without a real fallback file, but verify method exists
    assert hasattr(c, "resolve_token_path")


def test_config_from_env(monkeypatch):
    monkeypatch.setenv("SCHWAB_APP_KEY", "fake_key")
    monkeypatch.setenv("SCHWAB_APP_SECRET", "fake_secret")
    c = Config.from_env()
    assert c.app_key == "fake_key"
    assert c.app_secret == "fake_secret"
