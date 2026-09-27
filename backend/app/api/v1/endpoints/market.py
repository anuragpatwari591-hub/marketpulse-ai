from fastapi import APIRouter

from app.analytics import regime as regime_engine
from app.analytics.anomaly import detect_price_anomalies
from app.analytics.indicators import vwap
from app.analytics.volume import analyze_volume
from app.providers.demo_market_data import get_demo_market_data_provider

router = APIRouter(prefix="/market", tags=["market"])


@router.get("/indices")
async def get_indices():
    provider = get_demo_market_data_provider()
    indices = await provider.get_index_quotes()
    return {"is_demo": True, "items": indices}


@router.get("/breadth")
async def get_breadth():
    provider = get_demo_market_data_provider()
    return await provider.get_market_breadth()


@router.get("/movers")
async def get_movers(limit: int = 5):
    provider = get_demo_market_data_provider()
    symbols = await provider.list_symbols()
    quotes = await provider.get_quotes(symbols)
    sorted_quotes = sorted(quotes, key=lambda q: q.change_pct, reverse=True)
    return {
        "is_demo": True,
        "gainers": sorted_quotes[:limit],
        "losers": sorted_quotes[-limit:][::-1],
    }


@router.get("/anomalies")
async def get_anomalies(kind: str = "all", limit: int = 10):
    """Cross-universe volume/price anomaly scan."""
    provider = get_demo_market_data_provider()
    symbols = await provider.list_symbols()
    results = []
    for symbol in symbols:
        candles = await provider.get_candles(symbol, days=90)
        closes = [c.close for c in candles]
        highs = [c.high for c in candles]
        lows = [c.low for c in candles]
        volumes = [c.volume for c in candles]
        vwap_series = vwap(highs, lows, closes, volumes)
        anomaly = detect_price_anomalies(closes, highs, lows, volumes, vwap_series)
        volume_analysis = analyze_volume(volumes)
        if kind == "volume" and volume_analysis["classification"] == "normal":
            continue
        if kind == "price" and not anomaly["flags"]:
            continue
        results.append(
            {
                "symbol": symbol,
                "anomaly_score": anomaly["anomaly_score"],
                "flags": anomaly["flags"],
                "volume_classification": volume_analysis["classification"],
                "relative_volume": volume_analysis["relative_volume"],
            }
        )
    results.sort(key=lambda r: r["anomaly_score"], reverse=True)
    return {"is_demo": True, "items": results[:limit]}


@router.get("/sectors")
async def get_sectors():
    provider = get_demo_market_data_provider()
    symbols = await provider.list_symbols()
    quotes = await provider.get_quotes(symbols)
    sectors: dict[str, list] = {}
    for q in quotes:
        sectors.setdefault(q.sector, []).append(q)
    out = []
    for sector, items in sectors.items():
        avg_change = sum(q.change_pct for q in items) / len(items)
        out.append(
            {
                "sector": sector,
                "avg_change_pct": round(avg_change, 2),
                "advances": sum(1 for q in items if q.change > 0),
                "declines": sum(1 for q in items if q.change < 0),
                "constituent_count": len(items),
            }
        )
    out.sort(key=lambda s: s["avg_change_pct"], reverse=True)
    return {"is_demo": True, "items": out}


@router.get("/regime")
async def get_regime():
    provider = get_demo_market_data_provider()
    candles = await provider.get_candles("NIFTY", days=260)
    closes = [c.close for c in candles]
    breadth = await provider.get_market_breadth()
    regime = regime_engine.detect_regime(closes, breadth["advances"], breadth["declines"])
    return {"is_demo": True, **regime}
