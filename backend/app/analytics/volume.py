"""Volume intelligence: rolling averages, relative volume, z-score based
anomaly classification. Thresholds are configurable (see VolumeThresholds).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class VolumeThresholds:
    elevated_z: float = 1.0
    unusual_z: float = 2.0
    extreme_z: float = 3.0


DEFAULT_THRESHOLDS = VolumeThresholds()


def average_volume(volumes: list[int], window: int) -> float | None:
    if len(volumes) < window:
        return None
    return float(np.mean(volumes[-window:]))


def volume_zscore(volumes: list[int], window: int = 20) -> float | None:
    if len(volumes) <= window:
        return None
    history = volumes[-(window + 1) : -1]
    mean = float(np.mean(history))
    std = float(np.std(history))
    if std == 0:
        if volumes[-1] == mean:
            return 0.0
        return 10.0 if volumes[-1] > mean else -10.0
    return (volumes[-1] - mean) / std


def relative_volume(current_volume: int, avg_volume: float | None) -> float | None:
    if not avg_volume:
        return None
    return current_volume / avg_volume


def classify_volume(z_score: float | None, thresholds: VolumeThresholds = DEFAULT_THRESHOLDS) -> str:
    if z_score is None:
        return "unknown"
    az = abs(z_score)
    if az >= thresholds.extreme_z:
        return "extreme"
    if az >= thresholds.unusual_z:
        return "unusual"
    if az >= thresholds.elevated_z:
        return "elevated"
    return "normal"


def volume_acceleration(volumes: list[int], short_window: int = 5, long_window: int = 20) -> float | None:
    short_avg = average_volume(volumes, short_window)
    long_avg = average_volume(volumes, long_window)
    if not short_avg or not long_avg:
        return None
    return (short_avg - long_avg) / long_avg


def analyze_volume(volumes: list[int]) -> dict:
    avg_5 = average_volume(volumes, 5)
    avg_20 = average_volume(volumes, 20)
    avg_50 = average_volume(volumes, 50)
    z = volume_zscore(volumes, 20)
    rel = relative_volume(volumes[-1], avg_20) if volumes else None
    return {
        "current_volume": volumes[-1] if volumes else 0,
        "avg_volume_5d": avg_5,
        "avg_volume_20d": avg_20,
        "avg_volume_50d": avg_50,
        "relative_volume": round(rel, 3) if rel is not None else None,
        "volume_zscore": round(z, 3) if z is not None else None,
        "volume_acceleration": volume_acceleration(volumes),
        "classification": classify_volume(z),
    }
