import pytest

from app.analytics.risk import calculate_risk
from app.analytics.signals import SignalWeights, generate_signal
from app.schemas.market import NewsArticle
from app.schemas.signals import RiskRequest
from datetime import datetime, timezone


def _fake_series(n=180, trend=0.5):
    closes = [100 + i * trend + (i % 5) for i in range(n)]
    highs = [c + 2 for c in closes]
    lows = [c - 2 for c in closes]
    volumes = [1_000_000 + (i % 7) * 10_000 for i in range(n)]
    return closes, highs, lows, volumes


def test_signal_weights_sum_to_one():
    SignalWeights().validate()


def test_signal_weights_invalid_raises():
    with pytest.raises(ValueError):
        SignalWeights(technical=0.5).validate()


def test_generate_signal_shape():
    closes, highs, lows, volumes = _fake_series()
    signal = generate_signal("TESTSTOCK", closes, highs, lows, volumes, news=[])
    assert 0 <= signal.score <= 100
    assert signal.direction in {"bullish", "bearish", "neutral"}
    assert len(signal.contributions) == 8
    total_weight = sum(c.weight_pct for c in signal.contributions)
    assert abs(total_weight - 100.0) < 0.01
    assert signal.is_demo is True
    assert "not" in signal.disclaimer.lower() or "no" in signal.disclaimer.lower()


def test_generate_signal_never_says_guaranteed():
    closes, highs, lows, volumes = _fake_series()
    signal = generate_signal("TESTSTOCK", closes, highs, lows, volumes, news=[])
    banned = ["guaranteed profit", "100% accurate", "risk-free", "is certain", "certain profit"]
    full_text = (signal.disclaimer + " ".join(signal.risks) + " ".join(signal.scenarios)).lower()
    for phrase in banned:
        assert phrase not in full_text


def test_generate_signal_with_positive_news_scores_higher_than_no_news():
    closes, highs, lows, volumes = _fake_series(trend=0.0)
    article = NewsArticle(
        id="1",
        headline="Company wins large order",
        source="test",
        timestamp=datetime.now(timezone.utc),
        symbol="TESTSTOCK",
        sector="IT",
        event_type="Order",
        sentiment="positive",
        importance=5,
        summary="test",
    )
    no_news_signal = generate_signal("TESTSTOCK", closes, highs, lows, volumes, news=[])
    news_signal = generate_signal("TESTSTOCK", closes, highs, lows, volumes, news=[article])
    assert news_signal.score > no_news_signal.score


def test_calculate_risk_basic():
    req = RiskRequest(account_size=100_000, max_risk_pct=1, entry=100, stop_loss=95, target=115, lot_size=1)
    result = calculate_risk(req)
    assert result.max_monetary_risk == 1000.0
    assert result.max_quantity == 200
    assert result.risk_reward_ratio == 3.0
    assert result.warnings == []


def test_calculate_risk_lot_size_rounding():
    req = RiskRequest(account_size=50_000, max_risk_pct=1, entry=100, stop_loss=98, target=110, lot_size=75)
    result = calculate_risk(req)
    assert result.max_quantity % 75 == 0


def test_calculate_risk_zero_risk_per_unit_raises():
    req = RiskRequest(account_size=50_000, max_risk_pct=1, entry=100, stop_loss=100, lot_size=1)
    with pytest.raises(ValueError):
        calculate_risk(req)


def test_calculate_risk_below_one_lot_warns():
    req = RiskRequest(account_size=1000, max_risk_pct=1, entry=100, stop_loss=50, lot_size=500)
    result = calculate_risk(req)
    assert result.max_quantity == 0
    assert result.warnings
