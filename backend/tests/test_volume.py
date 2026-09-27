from app.analytics.volume import (
    analyze_volume,
    average_volume,
    classify_volume,
    relative_volume,
    volume_zscore,
)


def test_average_volume_none_when_insufficient_history():
    assert average_volume([1, 2, 3], 5) is None


def test_average_volume_basic():
    assert average_volume([10, 20, 30], 3) == 20


def test_relative_volume():
    assert relative_volume(200, 100) == 2.0
    assert relative_volume(100, None) is None


def test_classify_volume_thresholds():
    assert classify_volume(0.2) == "normal"
    assert classify_volume(1.5) == "elevated"
    assert classify_volume(2.5) == "unusual"
    assert classify_volume(3.5) == "extreme"
    assert classify_volume(None) == "unknown"


def test_volume_zscore_spike_detected():
    normal = [100_000] * 20
    spike = normal + [500_000]
    z = volume_zscore(spike, window=20)
    assert z is not None
    assert z > 2


def test_analyze_volume_returns_all_fields():
    volumes = [100_000 + i * 1000 for i in range(60)]
    result = analyze_volume(volumes)
    assert set(result.keys()) == {
        "current_volume",
        "avg_volume_5d",
        "avg_volume_20d",
        "avg_volume_50d",
        "relative_volume",
        "volume_zscore",
        "volume_acceleration",
        "classification",
    }
