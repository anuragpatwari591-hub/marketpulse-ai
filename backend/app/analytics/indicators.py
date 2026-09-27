"""Technical indicators, computed purely from OHLCV candles.

All functions take a list of closes/highs/lows/volumes (oldest -> newest)
and are pure/deterministic. No look-ahead: every value at index i is
computed only from data at indices <= i.
"""
from __future__ import annotations

import numpy as np


def sma(values: list[float], period: int) -> list[float | None]:
    out: list[float | None] = [None] * len(values)
    for i in range(period - 1, len(values)):
        out[i] = float(np.mean(values[i - period + 1 : i + 1]))
    return out


def ema(values: list[float], period: int) -> list[float | None]:
    out: list[float | None] = [None] * len(values)
    if len(values) < period:
        return out
    k = 2 / (period + 1)
    seed = float(np.mean(values[:period]))
    out[period - 1] = seed
    prev = seed
    for i in range(period, len(values)):
        prev = values[i] * k + prev * (1 - k)
        out[i] = prev
    return out


def rsi(closes: list[float], period: int = 14) -> list[float | None]:
    out: list[float | None] = [None] * len(closes)
    if len(closes) <= period:
        return out
    gains = [0.0]
    losses = [0.0]
    for i in range(1, len(closes)):
        delta = closes[i] - closes[i - 1]
        gains.append(max(delta, 0.0))
        losses.append(abs(min(delta, 0.0)))

    avg_gain = float(np.mean(gains[1 : period + 1]))
    avg_loss = float(np.mean(losses[1 : period + 1]))
    out[period] = _rsi_from_avgs(avg_gain, avg_loss)

    for i in range(period + 1, len(closes)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        out[i] = _rsi_from_avgs(avg_gain, avg_loss)
    return out


def _rsi_from_avgs(avg_gain: float, avg_loss: float) -> float:
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def macd(
    closes: list[float], fast: int = 12, slow: int = 26, signal: int = 9
) -> tuple[list[float | None], list[float | None], list[float | None]]:
    ema_fast = ema(closes, fast)
    ema_slow = ema(closes, slow)
    macd_line: list[float | None] = [
        (f - s) if f is not None and s is not None else None for f, s in zip(ema_fast, ema_slow)
    ]
    valid = [v for v in macd_line if v is not None]
    signal_line: list[float | None] = [None] * len(macd_line)
    if len(valid) >= signal:
        first_valid_idx = next(i for i, v in enumerate(macd_line) if v is not None)
        sig_values = ema([v for v in macd_line if v is not None], signal)
        for offset, val in enumerate(sig_values):
            signal_line[first_valid_idx + offset] = val
    histogram: list[float | None] = [
        (m - s) if m is not None and s is not None else None for m, s in zip(macd_line, signal_line)
    ]
    return macd_line, signal_line, histogram


def atr(highs: list[float], lows: list[float], closes: list[float], period: int = 14) -> list[float | None]:
    out: list[float | None] = [None] * len(closes)
    trs = [0.0] * len(closes)
    for i in range(len(closes)):
        if i == 0:
            trs[i] = highs[i] - lows[i]
        else:
            trs[i] = max(
                highs[i] - lows[i],
                abs(highs[i] - closes[i - 1]),
                abs(lows[i] - closes[i - 1]),
            )
    if len(closes) <= period:
        return out
    avg = float(np.mean(trs[1 : period + 1]))
    out[period] = avg
    for i in range(period + 1, len(closes)):
        avg = (avg * (period - 1) + trs[i]) / period
        out[i] = avg
    return out


def bollinger_bands(
    closes: list[float], period: int = 20, num_std: float = 2.0
) -> tuple[list[float | None], list[float | None], list[float | None]]:
    mid = sma(closes, period)
    upper: list[float | None] = [None] * len(closes)
    lower: list[float | None] = [None] * len(closes)
    for i in range(period - 1, len(closes)):
        window = closes[i - period + 1 : i + 1]
        std = float(np.std(window))
        upper[i] = mid[i] + num_std * std
        lower[i] = mid[i] - num_std * std
    return upper, mid, lower


def vwap(highs: list[float], lows: list[float], closes: list[float], volumes: list[int]) -> list[float | None]:
    """Session-cumulative VWAP (single session assumed per call)."""
    out: list[float | None] = [None] * len(closes)
    cum_pv = 0.0
    cum_vol = 0.0
    for i in range(len(closes)):
        typical = (highs[i] + lows[i] + closes[i]) / 3
        cum_pv += typical * volumes[i]
        cum_vol += volumes[i]
        out[i] = cum_pv / cum_vol if cum_vol else None
    return out


def rolling_high_low(highs: list[float], lows: list[float], window: int) -> tuple[list[float | None], list[float | None]]:
    highest: list[float | None] = [None] * len(highs)
    lowest: list[float | None] = [None] * len(lows)
    for i in range(len(highs)):
        start = max(0, i - window + 1)
        highest[i] = max(highs[start : i + 1])
        lowest[i] = min(lows[start : i + 1])
    return highest, lowest


def support_resistance(highs: list[float], lows: list[float], window: int = 20) -> tuple[float, float]:
    """Simple pivot-based support/resistance from the most recent window."""
    recent_highs = highs[-window:]
    recent_lows = lows[-window:]
    resistance = max(recent_highs) if recent_highs else 0.0
    support = min(recent_lows) if recent_lows else 0.0
    return support, resistance


def detect_gap(prev_close: float, open_price: float, atr_value: float | None) -> dict:
    gap_pct = (open_price - prev_close) / prev_close * 100 if prev_close else 0.0
    threshold_pct = (atr_value / prev_close * 100 * 0.5) if atr_value and prev_close else 1.0
    gap_type = "none"
    if gap_pct > threshold_pct:
        gap_type = "gap_up"
    elif gap_pct < -threshold_pct:
        gap_type = "gap_down"
    return {"gap_pct": round(gap_pct, 3), "gap_type": gap_type}


def returns(closes: list[float]) -> list[float]:
    out = [0.0]
    for i in range(1, len(closes)):
        prev = closes[i - 1]
        out.append((closes[i] - prev) / prev if prev else 0.0)
    return out
