# Changelog

All notable changes to this project are documented here.

## [0.1.0] - Initial build

### Added
- FastAPI backend with provider-independent architecture (`MarketDataProvider`,
  `NewsProvider`, `CorporateDataProvider`, `LLMProvider`, `BrokerProvider`,
  `NotificationProvider` interfaces).
- Deterministic demo market data provider: 5 indices, 25 stocks across 14
  sectors, seeded OHLCV history plus simulated live jitter.
- Deterministic demo news provider: 40 synthetic articles across 13 event
  categories.
- Technical analytics: SMA, EMA, RSI, MACD, ATR, Bollinger Bands, VWAP,
  52-week levels, support/resistance, gap detection.
- Volume intelligence: rolling averages, relative volume, z-score-based
  classification (normal/elevated/unusual/extreme).
- Price anomaly detection: composite 0-100 score with an itemized,
  explainable breakdown.
- Rule-based market regime detection (trend / volatility / risk stance).
- Multi-factor signal engine (technical/volume/price action/derivatives/
  news/regime/sector/fundamentals) with full per-factor evidence, risks,
  invalidation levels, and scenarios — never a bare BUY/SELL.
- Risk / position-sizing calculator.
- REST API under `/api/v1` plus a simulated `/ws/market` WebSocket.
- React + TypeScript + Vite + Tailwind frontend: Dashboard, Markets, Stock
  Detail (candlestick chart), Screener, Signals (list + detail),
  Risk Calculator — dark "terminal" styling, loading/error/empty states,
  a persistent DEMO MODE banner, and data-freshness indicators.
- 54 backend pytest tests, 12 frontend Vitest tests, GitHub Actions CI.
- Docker Compose (backend, frontend, postgres, redis), Windows batch/
  PowerShell launch scripts, macOS/Linux dev script.
- Full documentation set (README, ARCHITECTURE, DEVELOPMENT, SECURITY,
  PROJECT_STATUS, and `docs/` subsystem notes).

### Known limitations
See `PROJECT_STATUS.md` for the complete roadmap of unimplemented sections
(options/futures, corporate events, IPO intelligence, AI/RAG, backtesting,
paper trading, Strategy Lab, alerts, portfolio, persistence layer).
