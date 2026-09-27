from fastapi import APIRouter, HTTPException

from app.analytics.signals import generate_signal
from app.providers.demo_market_data import get_demo_market_data_provider
from app.providers.demo_news import get_demo_news_provider

router = APIRouter(prefix="/signals", tags=["signals"])


@router.get("/{symbol}")
async def get_signal(symbol: str):
    provider = get_demo_market_data_provider()
    news_provider = get_demo_news_provider()
    try:
        candles = await provider.get_candles(symbol, days=180)
        quote = await provider.get_quote(symbol)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Unknown symbol '{symbol}'")

    closes = [c.close for c in candles]
    highs = [c.high for c in candles]
    lows = [c.low for c in candles]
    volumes = [c.volume for c in candles]
    news = await news_provider.get_latest(limit=5, symbol=symbol)
    breadth = await provider.get_market_breadth()

    sector_quotes = [q for q in await provider.get_quotes(await provider.list_symbols()) if q.sector == quote.sector]
    sector_change = sum(q.change_pct for q in sector_quotes) / len(sector_quotes) if sector_quotes else None

    signal = generate_signal(
        symbol=symbol,
        closes=closes,
        highs=highs,
        lows=lows,
        volumes=volumes,
        news=news,
        sector_change_pct=sector_change,
        breadth_advances=breadth["advances"],
        breadth_declines=breadth["declines"],
    )
    return signal


@router.get("")
async def list_signals(limit: int = 10):
    """Top signals across the demo universe, ranked by composite score."""
    provider = get_demo_market_data_provider()
    symbols = await provider.list_symbols()
    signals = []
    for symbol in symbols:
        try:
            resp = await get_signal(symbol)
        except HTTPException:
            continue
        signals.append(resp)
    signals.sort(key=lambda s: s.score, reverse=True)
    return {"is_demo": True, "items": signals[:limit]}
