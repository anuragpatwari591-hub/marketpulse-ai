"""Price anomaly detection and a composite 0-100 anomaly score.

Uses simple, explainable statistical methods (z-scores on returns/volume/
VWAP deviation) rather than an opaque model, so every anomaly can be
explained to the user. This is intentionally conservative: it flags
*measurable statistical deviation*, not a prediction of future direction.
"""
from __future__ import annotations

import numpy as np

from app.analytics.indicators import atr as atr_fn
from app.analytics.indicators import returns as returns_fn
from app.analytics.volume import volume_zscore


def price_return_zscore(closes: list[float], window: int = 20) -> float | None:
    rets = returns_fn(closes)
    if len(rets) <= window:
        return None
    history = rets[-(window + 1) : -1]
    mean = float(np.mean(history))
    std = float(np.std(history))
    if std == 0:
        if rets[-1] == mean:
            return 0.0
        return 10.0 if rets[-1] > mean else -10.0
    return (rets[-1] - mean) / std


def vwap_deviation_pct(price: float, vwap_value: float | None) -> float | None:
    if not vwap_value:
        return None
    return (price - vwap_value) / vwap_value * 100


def atr_expansion(highs: list[float], lows: list[float], closes: list[float], window: int = 14) -> float | None:
    atr_series = atr_fn(highs, lows, closes, window)
    valid = [v for v in atr_series if v is not None]
    if len(valid) < window:
        return None
    baseline = float(np.mean(valid[-window - 5 : -5])) if len(valid) > window + 5 else valid[0]
    current = valid[-1]
    if not baseline:
        return None
    return (current - baseline) / baseline


def composite_anomaly_score(
    price_z: float | None,
    volume_z: float | None,
    vwap_dev_pct: float | None,
    atr_expansion_pct: float | None,
) -> dict:
    """Combine multiple z-score-like signals into a 0-100 anomaly score.

    Method: each feature contributes up to 25 points based on |value|
    saturating at a reasonable cap, then summed. This is a transparent,
    additive heuristic - not a black box model - so every point can be
    attributed to a specific feature.
    """

    def scaled(value: float | None, cap: float) -> float:
        if value is None:
            return 0.0
        return min(abs(value), cap) / cap * 25

    breakdown = {
        "price_return": scaled(price_z, 3.0),
        "volume": scaled(volume_z, 3.0),
        "vwap_deviation": scaled(vwap_dev_pct, 5.0),
        "volatility_expansion": scaled(atr_expansion_pct, 1.0),
    }
    score = sum(breakdown.values())
    return {
        "score": round(score, 1),
        "breakdown": {k: round(v, 1) for k, v in breakdown.items()},
    }


def detect_price_anomalies(
    closes: list[float],
    highs: list[float],
    lows: list[float],
    volumes: list[int],
    vwap_series: list[float | None],
) -> dict:
    price_z = price_return_zscore(closes)
    vol_z = volume_zscore(volumes)
    vwap_dev = vwap_deviation_pct(closes[-1], vwap_series[-1] if vwap_series else None)
    atr_exp = atr_expansion(highs, lows, closes)
    composite = composite_anomaly_score(price_z, vol_z, vwap_dev, atr_exp)

    flags = []
    if price_z is not None and abs(price_z) >= 2:
        flags.append("rapid_price_movement")
    if vwap_dev is not None and abs(vwap_dev) >= 3:
        flags.append("vwap_deviation")
    if atr_exp is not None and atr_exp >= 0.3:
        flags.append("volatility_expansion")

    return {
        "price_return_zscore": round(price_z, 3) if price_z is not None else None,
        "volume_zscore": round(vol_z, 3) if vol_z is not None else None,
        "vwap_deviation_pct": round(vwap_dev, 3) if vwap_dev is not None else None,
        "atr_expansion_pct": round(atr_exp, 3) if atr_exp is not None else None,
        "flags": flags,
        "anomaly_score": composite["score"],
        "anomaly_breakdown": composite["breakdown"],
    }
