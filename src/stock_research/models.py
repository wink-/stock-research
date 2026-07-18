"""Pydantic models for quotes, fundamentals, technicals, reports."""
from __future__ import annotations
from datetime import date, datetime, timezone
from pydantic import BaseModel, Field


class Quote(BaseModel):
    symbol: str
    last: float
    bid: float
    ask: float
    open: float
    high: float
    low: float
    close_prior: float
    change_pct: float
    volume: int
    high_52wk: float
    low_52wk: float
    description: str = ""


class Fundamentals(BaseModel):
    pe_ratio: float | None = None
    eps: float | None = None
    div_yield: float | None = None
    div_amount: float | None = None
    div_ex_date: date | None = None
    shares_out: int | None = None
    market_cap: float | None = None
    avg_volume_10d: float | None = None
    last_earnings: date | None = None


class Technical(BaseModel):
    sma_8: float | None = None
    sma_20: float | None = None
    sma_50: float | None = None
    sma_200: float | None = None
    above_20: bool = False
    above_50: bool = False
    regime_score: int = 0
    regime_label: str = "neutral"
    atr_14: float | None = None
    range_position_pct: float | None = None  # where close sits in last N range


class Level(BaseModel):
    price: float
    kind: str  # "support" | "resistance" | "pivot"
    strength: int = 1


class OptionsSnapshot(BaseModel):
    expiry: date
    dte: int
    atm_iv: float | None = None
    implied_move: float | None = None
    put_oi_cluster: float | None = None
    call_oi_cluster: float | None = None
    put_wall: float | None = None
    call_wall: float | None = None


class NewsItem(BaseModel):
    title: str
    published: datetime
    source: str = ""


class Report(BaseModel):
    symbol: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    quote: Quote
    fundamentals: Fundamentals | None = None
    technical: Technical
    levels: list[Level] = []
    options: OptionsSnapshot | None = None
    news: list[NewsItem] = []
    notes: list[str] = []
