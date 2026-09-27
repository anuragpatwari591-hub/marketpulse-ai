"""Provider interfaces.

MarketPulse is provider-independent: every external integration is defined
as an abstract interface here. Concrete implementations (demo or live) are
selected at runtime via environment variables (see app.core.config).

Rule: if live credentials are missing, the application MUST fall back to
the demo implementation rather than failing. Demo data is always clearly
labeled as such by the API (see `Candle.source` / `is_demo` flags).
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from app.schemas.market import Candle, IndexQuote, NewsArticle, Quote


class MarketDataProvider(ABC):
    """Source of quotes, candles and instrument metadata."""

    name: str = "base"
    is_demo: bool = True

    @abstractmethod
    async def list_symbols(self) -> list[str]:
        ...

    @abstractmethod
    async def get_quote(self, symbol: str) -> Quote:
        ...

    @abstractmethod
    async def get_quotes(self, symbols: list[str]) -> list[Quote]:
        ...

    @abstractmethod
    async def get_candles(self, symbol: str, days: int = 180, interval: str = "1d") -> list[Candle]:
        ...

    @abstractmethod
    async def get_index_quotes(self) -> list[IndexQuote]:
        ...


class NewsProvider(ABC):
    name: str = "base"
    is_demo: bool = True

    @abstractmethod
    async def get_latest(self, limit: int = 20, symbol: Optional[str] = None) -> list[NewsArticle]:
        ...


class CorporateDataProvider(ABC):
    """Corporate actions / events (results, dividends, board meetings, etc.)."""

    name: str = "base"
    is_demo: bool = True

    @abstractmethod
    async def get_events(self, start: datetime, end: datetime, symbol: Optional[str] = None) -> list[dict]:
        ...


class LLMProvider(ABC):
    """Chat/completion abstraction. Implementations must never fabricate
    structured market facts - callers are responsible for retrieving real
    data and passing it into the prompt context (see app.ai when built)."""

    name: str = "base"
    is_demo: bool = True

    @abstractmethod
    async def complete(self, prompt: str, context: Optional[dict] = None) -> str:
        ...


class BrokerProvider(ABC):
    """Placeholder interface for future real-money broker integration.
    MarketPulse never places real orders in this version (paper trading only).
    """

    name: str = "none"
    is_demo: bool = True

    @abstractmethod
    async def is_configured(self) -> bool:
        ...


class NotificationProvider(ABC):
    name: str = "none"

    @abstractmethod
    async def send(self, title: str, message: str, channel: str = "default") -> bool:
        ...
