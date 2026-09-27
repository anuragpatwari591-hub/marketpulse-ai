from app.analytics.anomaly import composite_anomaly_score, detect_price_anomalies
from app.analytics.regime import detect_regime
from app.analytics.indicators import vwap


def test_detect_regime_trending_bull():
    closes = [100 + i * 1.2 for i in range(220)]
    result = detect_regime(closes, breadth_advances=30, breadth_declines=10)
    assert result["trend"] == "trending_bull"
    assert result["risk_state"] == "risk_on"


def test_detect_regime_trending_bear():
    closes = [300 - i * 1.2 for i in range(220)]
    result = detect_regime(closes, breadth_advances=5, breadth_declines=25)
    assert result["trend"] == "trending_bear"
    assert result["risk_state"] == "risk_off"


def test_composite_anomaly_score_bounds():
    result = composite_anomaly_score(price_z=5, volume_z=5, vwap_dev_pct=10, atr_expansion_pct=2)
    assert 0 <= result["score"] <= 100


def test_composite_anomaly_score_zero_when_no_signal():
    result = composite_anomaly_score(price_z=0, volume_z=0, vwap_dev_pct=0, atr_expansion_pct=0)
    assert result["score"] == 0


def test_detect_price_anomalies_flags_spike():
    closes = [100] * 40 + [130]  # sudden 30% jump
    highs = [c + 1 for c in closes]
    lows = [c - 1 for c in closes]
    volumes = [100_000] * 40 + [800_000]
    vwap_series = vwap(highs, lows, closes, volumes)
    result = detect_price_anomalies(closes, highs, lows, volumes, vwap_series)
    assert result["anomaly_score"] > 0
    assert len(result["flags"]) > 0
