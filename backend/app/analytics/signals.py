"""Multi-factor signal engine.

Combines technical, volume, price-action, derivatives, news, market-regime
and sector-strength factors into a single 0-100 composite score with a
fully itemized breakdown. Weights are configurable. Factors for which no
real data source exists yet in this build (derivatives, fundamentals) are
explicitly marked "unavailable" and contribute a neutral 50 rather than
being silently omitted or fabricated.

The resulting score is an ANALYTICAL score, not a probability of profit,
and is never rendered as a bare BUY/SELL instruction (see app.schemas.signals.Signal).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.analytics import regime as regime_engine
from app.analytics import volume as volume_engine
from app.analytics.indicators import ema, macd, rsi, sma
from app.schemas.market import NewsArticle
from app.schemas.signals import FactorContribution, Signal


@dataclass
class SignalWeights:
    technical: float = 0.20
    volume: float = 0.15
    price_action: float = 0.15
    derivatives: float = 0.15
    news_catalyst: float = 0.15
    market_regime: float = 0.10
    sector_strength: float = 0.05
    fundamentals: float = 0.05

    def as_dict(self) -> dict:
        return {
            "technical": self.technical,
            "volume": self.volume,
            "price_action": self.price_action,
            "derivatives": self.derivatives,
            "news_catalyst": self.news_catalyst,
            "market_regime": self.market_regime,
            "sector_strength": self.sector_strength,
            "fundamentals": self.fundamentals,
        }

    def validate(self) -> None:
        total = sum(self.as_dict().values())
        if abs(total - 1.0) > 1e-6:
            raise ValueError(f"Signal weights must sum to 1.0, got {total}")


DEFAULT_WEIGHTS = SignalWeights()


def _technical_score(closes: list[float]) -> tuple[float, str]:
    rsi_series = rsi(closes, 14)
    macd_line, signal_line, _ = macd(closes)
    ema20 = ema(closes, 20)
    latest_rsi = rsi_series[-1]
    latest_price = closes[-1]

    score = 50.0
    evidence_parts = []
    if latest_rsi is not None:
        if latest_rsi > 70:
            score += 15
            evidence_parts.append(f"RSI {latest_rsi:.1f} overbought")
        elif latest_rsi < 30:
            score -= 15
            evidence_parts.append(f"RSI {latest_rsi:.1f} oversold")
        else:
            evidence_parts.append(f"RSI {latest_rsi:.1f} neutral")

    if macd_line[-1] is not None and signal_line[-1] is not None:
        if macd_line[-1] > signal_line[-1]:
            score += 15
            evidence_parts.append("MACD above signal (bullish crossover state)")
        else:
            score -= 15
            evidence_parts.append("MACD below signal (bearish crossover state)")

    if ema20[-1] is not None:
        if latest_price > ema20[-1]:
            score += 10
            evidence_parts.append("price above EMA20")
        else:
            score -= 10
            evidence_parts.append("price below EMA20")

    score = max(0.0, min(100.0, score))
    return score, "; ".join(evidence_parts) if evidence_parts else "insufficient history"


def _volume_score(volumes: list[int]) -> tuple[float, str]:
    analysis = volume_engine.analyze_volume(volumes)
    classification = analysis["classification"]
    rel = analysis["relative_volume"] or 1.0
    base = {"normal": 50, "elevated": 65, "unusual": 80, "extreme": 92, "unknown": 50}[classification]
    return float(base), f"relative volume {rel:.2f}x, classified '{classification}'"


def _price_action_score(closes: list[float], highs: list[float], lows: list[float]) -> tuple[float, str]:
    price = closes[-1]
    lookback = min(60, len(highs))
    recent_high = max(highs[-lookback:])
    recent_low = min(lows[-lookback:])
    rng = recent_high - recent_low or 1.0
    position = (price - recent_low) / rng * 100
    score = position
    evidence = f"price sits at {position:.0f}th percentile of {lookback}-day range"
    return score, evidence


def _news_score(articles: list[NewsArticle]) -> tuple[float, str]:
    if not articles:
        return 50.0, "no recent news catalyst found"
    weights = {"positive": 1, "negative": -1, "neutral": 0}
    total = sum(weights.get(a.sentiment, 0) * a.importance for a in articles)
    score = max(0.0, min(100.0, 50 + total * 4))
    top = articles[0]
    return score, f"latest: '{top.headline}' ({top.sentiment}, importance {top.importance}/5)"


def _regime_score(regime: dict) -> tuple[float, str]:
    mapping = {"trending_bull": 75, "trending_bear": 25, "rangebound": 50}
    score = mapping.get(regime["trend"], 50)
    return float(score), f"regime: {regime['trend']} / {regime['volatility_state']} / {regime['risk_state']}"


def _sector_score(sector_change_pct: float | None) -> tuple[float, str]:
    if sector_change_pct is None:
        return 50.0, "sector data unavailable"
    score = max(0.0, min(100.0, 50 + sector_change_pct * 8))
    return score, f"sector moved {sector_change_pct:+.2f}% today"


def generate_signal(
    symbol: str,
    closes: list[float],
    highs: list[float],
    lows: list[float],
    volumes: list[int],
    news: list[NewsArticle],
    sector_change_pct: float | None = None,
    breadth_advances: int = 0,
    breadth_declines: int = 0,
    weights: SignalWeights = DEFAULT_WEIGHTS,
) -> Signal:
    weights.validate()
    regime = regime_engine.detect_regime(closes, breadth_advances, breadth_declines)

    tech_score, tech_ev = _technical_score(closes)
    vol_score, vol_ev = _volume_score(volumes)
    pa_score, pa_ev = _price_action_score(closes, highs, lows)
    news_score, news_ev = _news_score(news)
    regime_score, regime_ev = _regime_score(regime)
    sector_score, sector_ev = _sector_score(sector_change_pct)

    deriv_score, deriv_ev = 50.0, "derivatives data not available in this build (options/futures engine pending) - defaulted neutral"
    fund_score, fund_ev = 50.0, "fundamentals data not available in this build - defaulted neutral"

    factors = [
        ("technical", tech_score, tech_ev, weights.technical),
        ("volume", vol_score, vol_ev, weights.volume),
        ("price_action", pa_score, pa_ev, weights.price_action),
        ("derivatives", deriv_score, deriv_ev, weights.derivatives),
        ("news_catalyst", news_score, news_ev, weights.news_catalyst),
        ("market_regime", regime_score, regime_ev, weights.market_regime),
        ("sector_strength", sector_score, sector_ev, weights.sector_strength),
        ("fundamentals", fund_score, fund_ev, weights.fundamentals),
    ]

    contributions = []
    composite = 0.0
    for name, raw, evidence, weight in factors:
        weighted = raw * weight
        composite += weighted
        contributions.append(
            FactorContribution(
                factor=name,
                weight_pct=round(weight * 100, 1),
                raw_score=round(raw, 1),
                weighted_score=round(weighted, 2),
                evidence=evidence,
            )
        )

    direction = "bullish" if composite > 55 else "bearish" if composite < 45 else "neutral"
    if composite >= 80:
        label = "Very Strong"
    elif composite >= 65:
        label = "Strong"
    elif composite >= 55:
        label = "Watch"
    elif composite >= 40:
        label = "Weak"
    else:
        label = "Neutral"

    risks = [
        "Demo/synthetic data - not a live market signal.",
        "Derivatives and fundamentals factors are currently unavailable and defaulted to neutral, which understates conviction either way.",
        "Composite score is not a calibrated probability of a profitable outcome.",
    ]
    recent_low = min(lows[-20:]) if len(lows) >= 20 else min(lows)
    recent_high = max(highs[-20:]) if len(highs) >= 20 else max(highs)
    invalidation = (
        f"Thesis weakens if price closes below {recent_low:.2f} (bullish case) "
        f"or above {recent_high:.2f} (bearish case)."
    )
    scenarios = [
        "Continuation: regime and technical factors persist, move extends in the signal direction.",
        "Mean reversion: price action factor reverses toward the mid-range, score decays toward Neutral.",
        "Catalyst fade: news-driven component loses weight as the story ages past ~48 hours.",
    ]

    return Signal(
        symbol=symbol,
        direction=direction,
        score=round(composite, 1),
        label=label,
        contributions=contributions,
        risks=risks,
        invalidation=invalidation,
        scenarios=scenarios,
        timestamp=datetime.now(timezone.utc),
        data_freshness="demo data generated at request time",
        sources=["demo_market_data_provider", "demo_news_provider"],
        is_demo=True,
    )
