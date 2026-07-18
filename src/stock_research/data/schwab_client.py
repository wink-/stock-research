"""Schwab client wrapper using existing token file."""
from __future__ import annotations
from stock_research.config import Config


def get_client(config: Config | None = None):
    """Return an authenticated schwab-py client.

    Reads from existing token file at config.token_path. Requires
    SCHWAB_APP_KEY / SCHWAB_APP_SECRET env vars for the app credentials.
    """
    cfg = config or Config.from_env()
    if not cfg.token_exists:
        raise FileNotFoundError(
            f"Schwab token not found at {cfg.token_path}. "
            f"Run the MCP auth flow first."
        )
    if not cfg.app_key or not cfg.app_secret:
        raise RuntimeError(
            "SCHWAB_APP_KEY / SCHWAB_APP_SECRET env vars not set. "
            "Get them from Schwab Developer Portal."
        )
    # Lazy import — keeps test collection fast and isolates schwab-py dep.
    from schwab.auth import client_from_token_file

    return client_from_token_file(
        token_path=str(cfg.token_path),
        api_key=cfg.app_key,
        app_secret=cfg.app_secret,
    )
