from fastapi import APIRouter, HTTPException, Query

from app.analytics.indicators import (
    atr,
    bollinger_bands,
    detect_gap,
    ema,
    macd,
    rolling_high_low,
    rsi,
    sma,
    support_resistance,
    vwap,
)
from app.analytics.volume import analyze_volume
from app.providers.demo_market_data import get_demo_market_data_provider
from app.providers.demo_news import get_demo_news_provider

router = APIRouter(prefix="/stocks", tags=["stocks"])


@router.get("")
async def list_stocks():
    provider = get_demo_market_data_provider()
    symbols = await provider.list_symbols()
    quotes = await provider.get_quotes(symbols)
    return {"is_demo": True, "items": quotes}


@router.get("/{symbol}")
async def get_stock(symbol: str):
    provider = get_demo_market_data_provider()
    try:
        quote = await provider.get_quote(symbol)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Unknown symbol '{symbol}'")
    return quote


@router.get("/{symbol}/candles")
async def get_stock_candles(symbol: str, days: int = Query(180, ge=10, le=1000)):
    provider = get_demo_market_data_provider()
    try:
        candles = await provider.get_candles(symbol, days=days)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Unknown symbol '{symbol}'")
    return {"is_demo": True, "symbol": symbol, "items": candles}


@router.get("/{symbol}/analysis")
async def get_stock_analysis(symbol: str, days: int = Query(180, ge=60, le=1000)):
    provider = get_demo_market_data_provider()
    try:
        candles = await provider.get_candles(symbol, days=days)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Unknown symbol '{symbol}'")

    closes = [c.close for c in candles]
    highs = [c.high for c in candles]
    lows = [c.low for c in candles]
    volumes = [c.volume for c in candles]

    sma_20 = sma(closes, 20)
    sma_50 = sma(closes, 50)
    ema_20 = ema(closes, 20)
    rsi_14 = rsi(closes, 14)
    macd_line, macd_signal, macd_hist = macd(closes)
    atr_14 = atr(highs, lows, closes, 14)
    bb_upper, bb_mid, bb_lower = bollinger_bands(closes, 20, 2.0)
    vwap_series = vwap(highs, lows, closes, volumes)
    high_52w, low_52w = rolling_high_low(highs, lows, min(252, len(highs)))
    support, resistance = support_resistance(highs, lows, 20)
    gap = detect_gap(closes[-2], candles[-1].open, atr_14[-1])
    volume_analysis = analyze_volume(volumes)

    def last(series):
        for v in reversed(series):
            if v is not None:
                return round(v, 2)
        return None

    return {
        "is_demo": True,
        "symbol": symbol,
        "as_of": candles[-1].timestamp,
        "price": closes[-1],
        "indicators": {
            "sma_20": last(sma_20),
            "sma_50": last(sma_50),
            "ema_20": last(ema_20),
            "rsi_14": last(rsi_14),
            "macd": last(macd_line),
            "macd_signal": last(macd_signal),
            "macd_histogram": last(macd_hist),
            "atr_14": last(atr_14),
            "bollinger_upper": last(bb_upper),
            "bollinger_mid": last(bb_mid),
            "bollinger_lower": last(bb_lower),
            "vwap": last(vwap_series),
        },
        "levels": {
            "52w_high": round(max(high_52w[-252:]) if high_52w else closes[-1], 2),
            "52w_low": round(min(low_52w[-252:]) if low_52w else closes[-1], 2),
            "support": round(support, 2),
            "resistance": round(resistance, 2),
        },
        "gap": gap,
        "volume": volume_analysis,
    }


@router.get("/{symbol}/news")
async def get_stock_news(symbol: str, limit: int = 10):
    news_provider = get_demo_news_provider()
    articles = await news_provider.get_latest(limit=limit, symbol=symbol)
    return {"is_demo": True, "symbol": symbol, "items": articles}
