# MarketPulse AI

An Indian stock-market intelligence and research terminal: technical analysis, volume/price anomaly detection, a transparent multi-factor signal engine, a screener, and a risk calculator — running today entirely on deterministic **demo data**, with a provider-abstraction layer designed so real data sources can be plugged in later without touching the analytics or frontend.

> **DEMO MODE**: every number in this build (prices, volume, news, corporate events) is synthetic, seeded, and clearly labeled. Nothing here is real market data. See [PROJECT_STATUS.md](PROJECT_STATUS.md) for exactly what is and isn't implemented.

## Quickstart (Windows)

```
setup.bat
start.bat
```

Then open http://localhost:3000. Backend API docs: http://localhost:8000/docs.

## Quickstart (macOS/Linux)

```bash
cp .env.example .env
cd backend && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt && cd ..
cd frontend && npm install && cd ..
./scripts/dev.sh
```

## Quickstart (Docker)

```bash
docker compose up --build
```

## URLs

| Service      | URL                              |
|--------------|-----------------------------------|
| Frontend     | http://localhost:3000             |
| Backend API  | http://localhost:8000             |
| API docs     | http://localhost:8000/docs        |
| Health check | http://localhost:8000/health      |
| System status| http://localhost:8000/api/v1/system/status |

## What's actually built

- **Backend (FastAPI)**: demo market data provider (deterministic seeded OHLCV for 5 indices + 25 stocks across 14 sectors), demo news provider, technical indicators (SMA/EMA/RSI/MACD/ATR/Bollinger/VWAP/52w levels/support-resistance/gap), volume intelligence (rolling averages, relative volume, z-score classification), price anomaly detection (composite 0-100 score with itemized breakdown), rule-based market regime detection, a multi-factor signal engine with full evidence per factor, and a position-sizing risk calculator. All exposed over a REST API plus a simulated `/ws/market` WebSocket.
- **Frontend (React + TypeScript + Vite + Tailwind)**: a dark, dense "terminal" UI — Dashboard (indices, breadth, regime, movers, sector heatmap, anomalies, news, watchlist), Markets (sortable/searchable table), Stock Detail (candlestick chart via TradingView Lightweight Charts, indicators, levels, volume, news), Screener (structured filters), Signals (ranked list + full factor-attribution detail view), Risk Calculator.
- **Tests**: 54 backend pytest tests (indicators, volume, anomaly, regime, signals, risk, API, determinism, no-lookahead), 12 frontend Vitest tests.
- **CI**: GitHub Actions running backend pytest and frontend lint/test/build on every push, entirely against demo data (no secrets required).

## What is explicitly NOT built yet

Options/futures chains, corporate events calendar, IPO intelligence, AI research/RAG assistant, natural-language screener, backtesting engine, paper trading, Strategy Lab, alerting, portfolio tracking, and the Postgres/Redis persistence layer are all designed for (see `app/providers/base.py` interfaces and `docker-compose.yml`) but not implemented in this pass. See [PROJECT_STATUS.md](PROJECT_STATUS.md) for the full breakdown and rationale.

## Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) — system design and module layout
- [DEVELOPMENT.md](DEVELOPMENT.md) — local dev workflow
- [SECURITY.md](SECURITY.md) — secrets handling, provider fallback safety
- [PROJECT_STATUS.md](PROJECT_STATUS.md) — implemented vs roadmap, required/optional credentials
- [CHANGELOG.md](CHANGELOG.md)
- `docs/` — data sources, signal engine methodology, backtesting design, AI/RAG design, API reference, database plan, deployment, testing

## Disclaimer

MarketPulse AI is a decision-support / research tool. Signal scores are analytical, not probabilistic guarantees, and the application never claims a result is "guaranteed", "certain", or "risk-free". It does not place real trades in this version — paper trading only, and only once implemented.
