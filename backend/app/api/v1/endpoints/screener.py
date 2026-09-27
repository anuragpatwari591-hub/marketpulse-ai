from typing import Optional

from fastapi import APIRouter, Query

from app.analytics.indicators import rsi, vwap
from app.analytics.volume import analyze_volume
from app.providers.demo_market_data import get_demo_market_data_provider

router = APIRouter(prefix="/screener", tags=["screener"])


@router.get("")
async def run_screener(
    sector: Optional[str] = None,
    min_change_pct: Optional[float] = None,
    max_change_pct: Optional[float] = None,
    min_relative_volume: Optional[float] = None,
    min_rsi: Optional[float] = None,
    max_rsi: Optional[float] = None,
    above_vwap: Optional[bool] = None,
    volume_classification: Optional[str] = Query(None, description="normal|elevated|unusual|extreme"),
    limit: int = 50,
):
    """Structured screener. A natural-language front-end that translates
    free text into these same filters is planned (see docs/ai.md) but not
    yet implemented in this build."""
    provider = get_demo_market_data_provider()
    symbols = await provider.list_symbols()
    results = []
    for symbol in symbols:
        quote = await provider.get_quote(symbol)
        if sector and quote.sector.lower() != sector.lower():
            continue
        if min_change_pct is not None and quote.change_pct < min_change_pct:
            continue
        if max_change_pct is not None and quote.change_pct > max_change_pct:
            continue
        if min_relative_volume is not None and quote.relative_volume < min_relative_volume:
            continue

        candles = await provider.get_candles(symbol, days=90)
        closes = [c.close for c in candles]
        highs = [c.high for c in candles]
        lows = [c.low for c in candles]
        volumes = [c.volume for c in candles]

        latest_rsi = rsi(closes, 14)[-1]
        if min_rsi is not None and (latest_rsi is None or latest_rsi < min_rsi):
            continue
        if max_rsi is not None and (latest_rsi is None or latest_rsi > max_rsi):
            continue

        vwap_series = vwap(highs, lows, closes, volumes)
        latest_vwap = vwap_series[-1]
        if above_vwap is not None and latest_vwap is not None:
            is_above = quote.price > latest_vwap
            if is_above != above_vwap:
                continue

        vol_analysis = analyze_volume(volumes)
        if volume_classification and vol_analysis["classification"] != volume_classification:
            continue

        results.append(
            {
                "symbol": symbol,
                "name": quote.name,
                "sector": quote.sector,
                "price": quote.price,
                "change_pct": quote.change_pct,
                "relative_volume": quote.relative_volume,
                "rsi_14": round(latest_rsi, 1) if latest_rsi is not None else None,
                "above_vwap": (quote.price > latest_vwap) if latest_vwap is not None else None,
                "volume_classification": vol_analysis["classification"],
            }
        )
    results.sort(key=lambda r: r["change_pct"], reverse=True)
    return {"is_demo": True, "count": len(results), "items": results[:limit]}
