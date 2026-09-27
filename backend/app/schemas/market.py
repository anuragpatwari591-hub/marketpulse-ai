from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Candle(BaseModel):
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int


class Quote(BaseModel):
    symbol: str
    name: str
    sector: str
    price: float
    change: float
    change_pct: float
    open: float
    high: float
    low: float
    prev_close: float
    volume: int
    avg_volume_20d: float
    relative_volume: float
    is_demo: bool = True
    last_updated: datetime


class IndexQuote(BaseModel):
    symbol: str
    name: str
    price: float
    change: float
    change_pct: float
    is_demo: bool = True
    last_updated: datetime


class MarketBreadth(BaseModel):
    advances: int
    declines: int
    unchanged: int
    is_demo: bool = True
    last_updated: datetime


class NewsArticle(BaseModel):
    id: str
    headline: str
    source: str
    timestamp: datetime
    symbol: Optional[str] = None
    sector: Optional[str] = None
    event_type: str
    sentiment: str = Field(description="positive | negative | neutral")
    importance: int = Field(ge=1, le=5)
    summary: str
    is_demo: bool = True


class DataFreshness(BaseModel):
    last_updated: datetime
    is_stale: bool
    is_demo: bool
