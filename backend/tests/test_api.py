def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_system_status(client):
    resp = client.get("/api/v1/system/status")
    assert resp.status_code == 200
    body = resp.json()
    assert body["version"]
    assert body["providers"]["market_data"]["mode"] == "demo"


def test_market_indices_flagged_demo(client):
    resp = client.get("/api/v1/market/indices")
    assert resp.status_code == 200
    body = resp.json()
    assert body["is_demo"] is True
    assert len(body["items"]) == 5


def test_market_breadth(client):
    resp = client.get("/api/v1/market/breadth")
    assert resp.status_code == 200
    body = resp.json()
    assert body["advances"] + body["declines"] + body["unchanged"] > 0


def test_market_movers(client):
    resp = client.get("/api/v1/market/movers?limit=3")
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["gainers"]) == 3
    assert len(body["losers"]) == 3


def test_market_sectors(client):
    resp = client.get("/api/v1/market/sectors")
    assert resp.status_code == 200
    assert len(resp.json()["items"]) > 0


def test_stocks_list(client):
    resp = client.get("/api/v1/stocks")
    assert resp.status_code == 200
    body = resp.json()
    assert body["is_demo"] is True
    assert len(body["items"]) > 10


def test_stock_detail_known_symbol(client):
    resp = client.get("/api/v1/stocks/RELIANCE")
    assert resp.status_code == 200
    assert resp.json()["symbol"] == "RELIANCE"


def test_stock_detail_unknown_symbol_404(client):
    resp = client.get("/api/v1/stocks/NOT_REAL")
    assert resp.status_code == 404


def test_stock_candles(client):
    resp = client.get("/api/v1/stocks/TCS/candles?days=30")
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["items"]) == 30


def test_stock_analysis_contains_indicators(client):
    resp = client.get("/api/v1/stocks/TCS/analysis")
    assert resp.status_code == 200
    body = resp.json()
    assert "rsi_14" in body["indicators"]
    assert "52w_high" in body["levels"]


def test_screener_returns_items(client):
    resp = client.get("/api/v1/screener?min_relative_volume=0")
    assert resp.status_code == 200
    assert resp.json()["is_demo"] is True


def test_signal_for_symbol(client):
    resp = client.get("/api/v1/signals/RELIANCE")
    assert resp.status_code == 200
    body = resp.json()
    assert 0 <= body["score"] <= 100
    assert len(body["contributions"]) == 8


def test_signal_unknown_symbol_404(client):
    resp = client.get("/api/v1/signals/NOT_REAL")
    assert resp.status_code == 404


def test_news_endpoint(client):
    resp = client.get("/api/v1/news?limit=5")
    assert resp.status_code == 200
    assert len(resp.json()["items"]) <= 5


def test_risk_calculate_endpoint(client):
    resp = client.post(
        "/api/v1/risk/calculate",
        json={"account_size": 100000, "max_risk_pct": 1, "entry": 100, "stop_loss": 95, "target": 115, "lot_size": 1},
    )
    assert resp.status_code == 200
    assert resp.json()["max_quantity"] == 200


def test_risk_calculate_invalid_returns_400(client):
    resp = client.post(
        "/api/v1/risk/calculate",
        json={"account_size": 100000, "max_risk_pct": 1, "entry": 100, "stop_loss": 100, "lot_size": 1},
    )
    assert resp.status_code == 400
