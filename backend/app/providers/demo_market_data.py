"""Deterministic demo market data provider.

Generates synthetic-but-realistic OHLCV series for a fixed universe of
Indian indices and stocks using a seeded random walk. Nothing here is real
market data - every response is clearly flagged `is_demo=True` and the API
layer adds a `DEMO MODE` banner requirement on the frontend.

Determinism: for a given (symbol, seed) pair, `get_candles` always returns
the same historical series - this makes analytics and tests reproducible.
The most recent candle also mutates slightly every minute (seeded by the
minute bucket) to simulate a "live" tick without needing a real feed.
"""
from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone
from typing import Optional

import numpy as np

from app.core.config import get_settings
from app.providers.base import MarketDataProvider
from app.schemas.market import Candle, IndexQuote, Quote

# Universe: (symbol, name, sector, base_price, annualized_vol)
DEMO_STOCKS: list[tuple[str, str, str, float, float]] = [
    ("RELIANCE", "Reliance Industries", "Energy", 2950.0, 0.24),
    ("TCS", "Tata Consultancy Services", "IT", 4150.0, 0.20),
    ("INFY", "Infosys", "IT", 1850.0, 0.24),
    ("HDFCBANK", "HDFC Bank", "Banking", 1680.0, 0.22),
    ("ICICIBANK", "ICICI Bank", "Banking", 1240.0, 0.23),
    ("SBIN", "State Bank of India", "Banking", 830.0, 0.28),
    ("AXISBANK", "Axis Bank", "Banking", 1150.0, 0.27),
    ("BAJFINANCE", "Bajaj Finance", "Financial Services", 7200.0, 0.30),
    ("MARUTI", "Maruti Suzuki", "Auto", 12500.0, 0.24),
    ("TATAMOTORS", "Tata Motors", "Auto", 980.0, 0.34),
    ("M&M", "Mahindra & Mahindra", "Auto", 2950.0, 0.28),
    ("SUNPHARMA", "Sun Pharma", "Pharma", 1780.0, 0.22),
    ("CIPLA", "Cipla", "Pharma", 1520.0, 0.21),
    ("HINDUNILVR", "Hindustan Unilever", "FMCG", 2450.0, 0.18),
    ("ITC", "ITC Limited", "FMCG", 470.0, 0.19),
    ("NTPC", "NTPC Limited", "Energy", 380.0, 0.26),
    ("ONGC", "Oil & Natural Gas Corp", "Energy", 280.0, 0.30),
    ("TATASTEEL", "Tata Steel", "Metals", 165.0, 0.32),
    ("JSWSTEEL", "JSW Steel", "Metals", 970.0, 0.30),
    ("DLF", "DLF Limited", "Realty", 850.0, 0.36),
    ("BEL", "Bharat Electronics", "Defence", 310.0, 0.33),
    ("IRCTC", "Indian Railway Catering & Tourism", "Railways", 780.0, 0.35),
    ("ADANIGREEN", "Adani Green Energy", "Renewables", 1650.0, 0.42),
    ("BHARTIARTL", "Bharti Airtel", "Telecom", 1580.0, 0.23),
    ("UPL", "UPL Limited", "Chemicals", 550.0, 0.31),
]

DEMO_INDICES: list[tuple[str, str, float, float]] = [
    ("NIFTY", "Nifty 50", 24800.0, 0.15),
    ("BANKNIFTY", "Nifty Bank", 51500.0, 0.18),
    ("FINNIFTY", "Nifty Financial Services", 23600.0, 0.17),
    ("MIDCAP", "Nifty Midcap 100", 57200.0, 0.20),
    ("INDIAVIX", "India VIX", 13.5, 0.55),
]

TRADING_DAYS_PER_YEAR = 252


def _rng_for(symbol: str, seed: int, salt: str = "") -> np.random.Generator:
    key = abs(hash((symbol, seed, salt))) % (2**32)
    return np.random.default_rng(key)


def _generate_series(base_price: float, ann_vol: float, days: int, symbol: str, seed: int) -> list[dict]:
    """Geometric-Brownian-motion-style random walk, seeded for determinism."""
    rng = _rng_for(symbol, seed, "history")
    daily_vol = ann_vol / math.sqrt(TRADING_DAYS_PER_YEAR)
    drift = 0.02 / TRADING_DAYS_PER_YEAR  # tiny long-run upward drift, typical of equity indices

    closes = [base_price]
    for _ in range(days - 1):
        shock = rng.normal(drift, daily_vol)
        # occasional fat-tail jump (news/earnings style event) ~4% of days
        if rng.random() < 0.04:
            shock += rng.choice([-1, 1]) * rng.uniform(0.02, 0.06)
        new_close = max(1.0, closes[-1] * (1 + shock))
        closes.append(new_close)

    series = []
    today = datetime.now(timezone.utc).replace(hour=10, minute=0, second=0, microsecond=0)
    start = today - timedelta(days=days * 1.45)  # skip weekends roughly
    ts = start
    produced = 0
    idx = 0
    while produced < days:
        if ts.weekday() < 5:
            close = closes[idx]
            open_px = close * (1 + rng.normal(0, daily_vol * 0.3))
            high = max(open_px, close) * (1 + abs(rng.normal(0, daily_vol * 0.4)))
            low = min(open_px, close) * (1 - abs(rng.normal(0, daily_vol * 0.4)))
            base_vol = rng.uniform(0.6, 1.4) * 1_000_000
            # volume spikes correlate loosely with big moves
            move = abs(close / closes[idx - 1] - 1) if idx > 0 else 0
            volume = int(base_vol * (1 + move * 8))
            series.append(
                {
                    "timestamp": ts,
                    "open": round(open_px, 2),
                    "high": round(high, 2),
                    "low": round(low, 2),
                    "close": round(close, 2),
                    "volume": volume,
                }
            )
            produced += 1
            idx += 1
        ts += timedelta(days=1)
    return series


def _live_jitter(symbol: str, seed: int, last_close: float, ann_vol: float) -> dict:
    """Simulate a 'live' intraday tick, stable within the same minute."""
    minute_bucket = datetime.now(timezone.utc).strftime("%Y%m%d%H%M")
    rng = _rng_for(symbol, seed, f"live-{minute_bucket}")
    daily_vol = ann_vol / math.sqrt(TRADING_DAYS_PER_YEAR)
    intraday_shock = rng.normal(0, daily_vol * 0.35)
    price = max(0.5, last_close * (1 + intraday_shock))
    return {"price": round(price, 2), "shock": intraday_shock}


class DemoMarketDataProvider(MarketDataProvider):
    name = "demo"
    is_demo = True

    def __init__(self) -> None:
        self.seed = get_settings().demo_random_seed
        self._universe = {s[0]: s for s in DEMO_STOCKS}
        self._index_universe = {i[0]: i for i in DEMO_INDICES}

    async def list_symbols(self) -> list[str]:
        return list(self._universe.keys())

    async def _series(self, symbol: str, days: int) -> list[dict]:
        if symbol in self._universe:
            _, _, _, base_price, vol = self._universe[symbol]
        elif symbol in self._index_universe:
            _, _, base_price, vol = self._index_universe[symbol]
        else:
            raise KeyError(f"Unknown demo symbol: {symbol}")
        return _generate_series(base_price, vol, days, symbol, self.seed)

    async def get_candles(self, symbol: str, days: int = 180, interval: str = "1d") -> list[Candle]:
        series = await self._series(symbol, days)
        return [Candle(**row) for row in series]

    async def get_quote(self, symbol: str) -> Quote:
        if symbol not in self._universe:
            raise KeyError(f"Unknown demo symbol: {symbol}")
        name, sector, _, base_price, vol = (
            self._universe[symbol][1],
            self._universe[symbol][2],
            self._universe[symbol][0],
            self._universe[symbol][3],
            self._universe[symbol][4],
        )
        series = await self._series(symbol, 60)
        prev_close = series[-2]["close"]
        last = series[-1]
        jitter = _live_jitter(symbol, self.seed, last["close"], vol)
        price = jitter["price"]
        volumes = [row["volume"] for row in series[-20:]]
        avg_volume_20d = sum(volumes) / len(volumes)
        today_volume = int(last["volume"] * (1 + abs(jitter["shock"]) * 3))
        change = price - prev_close
        change_pct = (change / prev_close) * 100 if prev_close else 0.0
        return Quote(
            symbol=symbol,
            name=name,
            sector=sector,
            price=price,
            change=round(change, 2),
            change_pct=round(change_pct, 2),
            open=last["open"],
            high=max(last["high"], price),
            low=min(last["low"], price),
            prev_close=prev_close,
            volume=today_volume,
            avg_volume_20d=avg_volume_20d,
            relative_volume=round(today_volume / avg_volume_20d, 2) if avg_volume_20d else 0.0,
            is_demo=True,
            last_updated=datetime.now(timezone.utc),
        )

    async def get_quotes(self, symbols: list[str]) -> list[Quote]:
        return [await self.get_quote(s) for s in symbols]

    async def get_index_quotes(self) -> list[IndexQuote]:
        results = []
        for symbol, name, base_price, vol in DEMO_INDICES:
            series = await self._series(symbol, 30)
            prev_close = series[-2]["close"]
            jitter = _live_jitter(symbol, self.seed, series[-1]["close"], vol)
            price = jitter["price"]
            change = price - prev_close
            change_pct = (change / prev_close) * 100 if prev_close else 0.0
            results.append(
                IndexQuote(
                    symbol=symbol,
                    name=name,
                    price=price,
                    change=round(change, 2),
                    change_pct=round(change_pct, 2),
                    is_demo=True,
                    last_updated=datetime.now(timezone.utc),
                )
            )
        return results

    async def get_market_breadth(self) -> dict:
        quotes = await self.get_quotes(list(self._universe.keys()))
        advances = sum(1 for q in quotes if q.change > 0)
        declines = sum(1 for q in quotes if q.change < 0)
        unchanged = len(quotes) - advances - declines
        return {
            "advances": advances,
            "declines": declines,
            "unchanged": unchanged,
            "is_demo": True,
            "last_updated": datetime.now(timezone.utc),
        }

    def stock_metadata(self, symbol: str) -> Optional[tuple]:
        return self._universe.get(symbol)


_provider_singleton: Optional[DemoMarketDataProvider] = None


def get_demo_market_data_provider() -> DemoMarketDataProvider:
    global _provider_singleton
    if _provider_singleton is None:
        _provider_singleton = DemoMarketDataProvider()
    return _provider_singleton
