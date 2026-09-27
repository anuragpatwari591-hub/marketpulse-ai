"""Rule-based market regime detection.

Deliberately NOT delegated to an LLM (section 22 of the spec forbids
that) - regime is derived from measurable inputs only: trend (price vs
moving averages), realized volatility, and breadth.
"""
from __future__ import annotations

import numpy as np

from app.analytics.indicators import sma


def realized_volatility(closes: list[float], window: int = 20) -> float | None:
    if len(closes) <= window:
        return None
    rets = np.diff(np.log(closes[-(window + 1) :]))
    return float(np.std(rets) * np.sqrt(252) * 100)  # annualized %


def detect_regime(closes: list[float], breadth_advances: int = 0, breadth_declines: int = 0) -> dict:
    sma_50 = sma(closes, 50)
    sma_200 = sma(closes, 200) if len(closes) >= 200 else sma(closes, min(100, len(closes)))
    vol = realized_volatility(closes, 20)
    long_vol = realized_volatility(closes, 60) or vol

    price = closes[-1]
    s50 = sma_50[-1]
    s200 = sma_200[-1]

    trend = "rangebound"
    if s50 is not None and s200 is not None:
        if price > s50 > s200:
            trend = "trending_bull"
        elif price < s50 < s200:
            trend = "trending_bear"

    volatility_state = "normal_volatility"
    if vol is not None and long_vol:
        if vol > long_vol * 1.3:
            volatility_state = "high_volatility"
        elif vol < long_vol * 0.7:
            volatility_state = "low_volatility"

    risk_state = "neutral"
    total = breadth_advances + breadth_declines
    if total > 0:
        adv_ratio = breadth_advances / total
        if adv_ratio > 0.6 and trend != "trending_bear":
            risk_state = "risk_on"
        elif adv_ratio < 0.4 or trend == "trending_bear":
            risk_state = "risk_off"

    return {
        "trend": trend,
        "volatility_state": volatility_state,
        "risk_state": risk_state,
        "realized_volatility_20d_pct": round(vol, 2) if vol is not None else None,
        "sma_50": round(s50, 2) if s50 is not None else None,
        "sma_200": round(s200, 2) if s200 is not None else None,
        "inputs": {
            "price": round(price, 2),
            "breadth_advances": breadth_advances,
            "breadth_declines": breadth_declines,
        },
        "disclaimer": "Regime is computed from measurable price/volatility/breadth inputs, not inferred by an AI model.",
    }
