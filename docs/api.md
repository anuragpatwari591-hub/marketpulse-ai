# API Reference

Interactive docs (always up to date with the running code): `GET /docs`
(Swagger UI) or `GET /redoc`. This file is a human-readable map of what
exists today.

Base URL: `http://localhost:8000`. All resource endpoints are under
`/api/v1`. Every response from a demo-backed endpoint includes `is_demo: true`
somewhere in its payload.

## System

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Liveness check |
| GET | `/api/v1/system/status` | Version, provider modes (demo/live), DB/Redis/worker status |

## Market

| Method | Path | Description |
|---|---|---|
| GET | `/api/v1/market/indices` | NIFTY, BANKNIFTY, FINNIFTY, MIDCAP, INDIA VIX |
| GET | `/api/v1/market/breadth` | Advances/declines/unchanged across the demo universe |
| GET | `/api/v1/market/movers?limit=5` | Top gainers/losers |
| GET | `/api/v1/market/sectors` | Sector-level average change, breadth |
| GET | `/api/v1/market/anomalies?kind=all\|volume\|price&limit=10` | Cross-universe anomaly scan |
| GET | `/api/v1/market/regime` | Rule-based regime (trend/volatility/risk stance) |

## Stocks

| Method | Path | Description |
|---|---|---|
| GET | `/api/v1/stocks` | All demo symbols with live-ish quotes |
| GET | `/api/v1/stocks/{symbol}` | Single quote (404 if unknown symbol) |
| GET | `/api/v1/stocks/{symbol}/candles?days=180` | OHLCV history |
| GET | `/api/v1/stocks/{symbol}/analysis?days=180` | Indicators, levels, gap, volume analysis in one call |
| GET | `/api/v1/stocks/{symbol}/news?limit=10` | News filtered to this symbol |

## Screener

| Method | Path | Description |
|---|---|---|
| GET | `/api/v1/screener` | Structured filters: `sector`, `min_change_pct`, `max_change_pct`, `min_relative_volume`, `min_rsi`, `max_rsi`, `above_vwap`, `volume_classification`, `limit` |

A natural-language front-end that compiles free text into these same query
parameters is planned (see `docs/ai.md`) but not implemented.

## Signals

| Method | Path | Description |
|---|---|---|
| GET | `/api/v1/signals/{symbol}` | Full multi-factor signal with evidence per factor |
| GET | `/api/v1/signals?limit=10` | Top signals across the universe, ranked by score |

## News

| Method | Path | Description |
|---|---|---|
| GET | `/api/v1/news?limit=20&symbol=` | Latest synthetic news, optionally filtered |

## Risk

| Method | Path | Description |
|---|---|---|
| POST | `/api/v1/risk/calculate` | Position sizing from account size / risk% / entry / stop / target / lot size |

## WebSocket

| Path | Description |
|---|---|
| `/ws/market` | Pushes `{ type: "market_update", is_demo: true, indices: [...] }` every 3s |
