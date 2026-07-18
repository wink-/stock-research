"""Config: paths, Schwab app credentials, output dirs."""
from __future__ import annotations
import os
from pathlib import Path
from pydantic import BaseModel

# Primary and fallback token paths (known mismatch quirk between MCP and trader profile)
PRIMARY_TOKEN = Path.home() / ".local/state/schwab-marketdata-mcp/token.json"
FALLBACK_TOKEN = Path.home() / ".hermes/profiles/trader/home/.local/state/schwab-marketdata-mcp/token.json"


class Config(BaseModel):
    token_path: Path = PRIMARY_TOKEN
    reports_dir: Path = Path.cwd() / "reports"
    app_key: str = ""
    app_secret: str = ""

    @classmethod
    def from_env(cls) -> "Config":
        cfg = cls(
            app_key=os.environ.get("SCHWAB_APP_KEY", ""),
            app_secret=os.environ.get("SCHWAB_APP_SECRET", ""),
        )
        cfg.resolve_token_path()
        return cfg

    def resolve_token_path(self) -> None:
        """If primary token missing, try fallback path."""
        if not self.token_path.exists() and FALLBACK_TOKEN.exists():
            self.token_path = FALLBACK_TOKEN

    @property
    def token_exists(self) -> bool:
        return self.token_path.exists()
