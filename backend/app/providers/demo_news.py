"""Deterministic demo news provider.

Produces a fixed, seeded set of synthetic news articles tagged against the
demo stock universe so the News engine, event-reaction features and AI
research assistant have something realistic to work with. Clearly flagged
`is_demo=True` - this is not real news.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import numpy as np

from app.core.config import get_settings
from app.providers.base import NewsProvider
from app.providers.demo_market_data import DEMO_STOCKS
from app.schemas.market import NewsArticle

EVENT_TEMPLATES = [
    ("Earnings", "{name} reports quarterly results", "neutral", 3),
    ("Order", "{name} wins large order from public sector client", "positive", 4),
    ("Contract", "{name} signs multi-year supply contract", "positive", 3),
    ("Acquisition", "{name} announces acquisition of smaller peer", "positive", 4),
    ("Fundraising", "{name} board approves fundraising via QIP", "neutral", 3),
    ("Regulation", "Regulator opens inquiry into {name} business practices", "negative", 4),
    ("Management", "{name} announces new CEO appointment", "neutral", 2),
    ("Product launch", "{name} launches new product line", "positive", 2),
    ("Dividend", "{name} board declares interim dividend", "positive", 2),
    ("Buyback", "{name} announces share buyback program", "positive", 3),
    ("Credit rating", "Rating agency revises {name} outlook", "negative", 3),
    ("Capacity expansion", "{name} to expand manufacturing capacity", "positive", 3),
    ("Partnership", "{name} enters strategic partnership", "positive", 2),
]


def _rng(seed: int) -> np.random.Generator:
    return np.random.default_rng(seed + 777)


class DemoNewsProvider(NewsProvider):
    name = "demo"
    is_demo = True

    def __init__(self) -> None:
        self.seed = get_settings().demo_random_seed
        self._articles = self._generate()

    def _generate(self) -> list[NewsArticle]:
        rng = _rng(self.seed)
        now = datetime.now(timezone.utc)
        articles: list[NewsArticle] = []
        for i in range(40):
            symbol, name, sector, *_ = DEMO_STOCKS[i % len(DEMO_STOCKS)]
            event_type, headline_tpl, sentiment, importance = EVENT_TEMPLATES[
                int(rng.integers(0, len(EVENT_TEMPLATES)))
            ]
            hours_ago = float(rng.uniform(0, 96))
            articles.append(
                NewsArticle(
                    id=f"demo-news-{i}",
                    headline=headline_tpl.format(name=name),
                    source="MarketPulse Demo Wire",
                    timestamp=now - timedelta(hours=hours_ago),
                    symbol=symbol,
                    sector=sector,
                    event_type=event_type,
                    sentiment=sentiment,
                    importance=int(importance),
                    summary=(
                        f"Demo synthetic article: {headline_tpl.format(name=name)}. "
                        f"Classified as a '{event_type}' event with {sentiment} sentiment. "
                        "This is deterministic demo content, not real news."
                    ),
                    is_demo=True,
                )
            )
        articles.sort(key=lambda a: a.timestamp, reverse=True)
        return articles

    async def get_latest(self, limit: int = 20, symbol: str | None = None) -> list[NewsArticle]:
        items = self._articles
        if symbol:
            items = [a for a in items if a.symbol == symbol]
        return items[:limit]


_singleton: DemoNewsProvider | None = None


def get_demo_news_provider() -> DemoNewsProvider:
    global _singleton
    if _singleton is None:
        _singleton = DemoNewsProvider()
    return _singleton
