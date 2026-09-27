from app.analytics.indicators import (
    atr,
    bollinger_bands,
    detect_gap,
    ema,
    macd,
    rsi,
    sma,
    support_resistance,
    vwap,
)


def test_sma_basic():
    values = [1, 2, 3, 4, 5]
    result = sma(values, 3)
    assert result[:2] == [None, None]
    assert result[2] == 2.0
    assert result[3] == 3.0
    assert result[4] == 4.0


def test_ema_converges_toward_recent_values():
    values = [10] * 30 + [20] * 30
    result = ema(values, 10)
    assert result[-1] > 15  # should have moved toward the new regime
    assert result[-1] < 20


def test_rsi_bounds():
    values = [100 + (i % 5) - 2 for i in range(60)]
    result = rsi(values, 14)
    for v in result:
        if v is not None:
            assert 0 <= v <= 100


def test_rsi_strong_uptrend_is_high():
    values = [100 + i for i in range(30)]
    result = rsi(values, 14)
    assert result[-1] > 70


def test_macd_shapes_match_input_length():
    values = [100 + i * 0.5 for i in range(60)]
    macd_line, signal_line, hist = macd(values)
    assert len(macd_line) == len(values)
    assert len(signal_line) == len(values)
    assert len(hist) == len(values)


def test_atr_non_negative():
    highs = [i + 2 for i in range(30)]
    lows = [i - 2 for i in range(30)]
    closes = [i for i in range(30)]
    result = atr(highs, lows, closes, 14)
    for v in result:
        if v is not None:
            assert v >= 0


def test_bollinger_bands_ordering():
    values = [100 + (i % 7) for i in range(40)]
    upper, mid, lower = bollinger_bands(values, 20, 2.0)
    for u, m, low in zip(upper, mid, lower):
        if u is not None:
            assert u >= m >= low


def test_vwap_is_between_low_and_high_when_flat_volume():
    highs = [105, 106, 107]
    lows = [95, 96, 97]
    closes = [100, 101, 102]
    volumes = [1000, 1000, 1000]
    result = vwap(highs, lows, closes, volumes)
    for i in range(len(result)):
        assert lows[i] <= result[i] <= highs[i]


def test_support_resistance():
    highs = [10, 12, 15, 11, 9]
    lows = [8, 9, 10, 7, 6]
    support, resistance = support_resistance(highs, lows, window=5)
    assert support == 6
    assert resistance == 15


def test_detect_gap_up():
    result = detect_gap(prev_close=100, open_price=105, atr_value=2)
    assert result["gap_type"] == "gap_up"


def test_detect_gap_down():
    result = detect_gap(prev_close=100, open_price=95, atr_value=2)
    assert result["gap_type"] == "gap_down"


def test_detect_gap_none():
    result = detect_gap(prev_close=100, open_price=100.1, atr_value=2)
    assert result["gap_type"] == "none"


def test_indicators_have_no_lookahead():
    """Value at index i must be identical whether or not future data exists."""
    base = [100 + (i % 9) * 0.7 for i in range(50)]
    extended = base + [999, 998, 1000, 5, 5000]  # wild future values

    sma_base = sma(base, 10)
    sma_ext = sma(extended, 10)
    assert sma_base == sma_ext[: len(base)]

    rsi_base = rsi(base, 14)
    rsi_ext = rsi(extended, 14)
    assert rsi_base == rsi_ext[: len(base)]

    atr_base = atr(base, [v - 1 for v in base], base, 14)
    atr_ext = atr(extended, [v - 1 for v in extended], extended, 14)
    assert atr_base == atr_ext[: len(base)]
