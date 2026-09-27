# Project Status

Version: **0.1.0**. This document is the honest source of truth for what's
implemented vs. planned. It maps directly to the sections of the original
build spec.

## Implemented

| Spec section | Status |
|---|---|
| §1-2 Project setup, autonomous build | Done for this pass — repo scaffolded, dependencies installed, frontend+backend built, tested, run, and verified end-to-end |
| §7 Core pages | Dashboard, Markets, Stock Detail, Screener, Signals, Risk Calculator implemented and functional. Options, Futures, News (dedicated page), Corporate Events, Sectors (dedicated page), IPO Intelligence, AI Research, Backtesting, Strategy Lab, Paper Trading, Portfolio, Alerts, Settings are **not built** — see Roadmap. The sidebar lists these explicitly as "Roadmap (not yet built)" rather than linking to empty pages. |
| §9 Dashboard | Indices, breadth, top gainers/losers, sector heatmap, volume/price anomalies, latest news, market regime, watchlist all live on real (demo) data |
| §10 Demo mode | `DemoMarketDataProvider` / `DemoNewsProvider`, deterministic seeded generation, persistent "DEMO MODE — NOT LIVE MARKET DATA" banner on every page |
| §11 Real data architecture | Provider interfaces exist (`MarketDataProvider`, `NewsProvider`, `CorporateDataProvider`, `LLMProvider`, `BrokerProvider`, `NotificationProvider`); only demo implementations exist today; credential-missing fallback logic implemented and tested |
| §12 Stock analytics | Price/OHLC/volume/relative volume/VWAP/SMA/EMA/RSI/MACD/ATR/Bollinger/52w high-low/support/resistance/gap all implemented |
| §13 Volume intelligence | 5/20/50-day averages, relative volume, acceleration, z-score, normal/elevated/unusual/extreme classification (thresholds configurable via `VolumeThresholds`) |
| §14 Price anomaly engine | Rapid price movement, VWAP deviation, ATR/volatility expansion, composite 0-100 score with itemized breakdown |
| §21 Sector engine | Performance, breadth, ranking by sector (descriptive, not prescriptive) |
| §22 Market regime engine | Rule-based (not LLM-arbitrated, per spec): trending bull/bear, rangebound, high/low volatility, risk-on/off |
| §23 Anomaly detection | Z-score-based, explainable, 0-100 score |
| §24-25 Signal engine + output | 8-factor weighted engine, full evidence per factor, never a bare BUY/SELL, risks/invalidation/scenarios always present |
| §26 Risk engine | Position sizing, max quantity/lots, potential loss/profit, risk/reward, warnings; never places orders |
| §40-41 Performance/WebSockets | TanStack Query polling + caching, `/ws/market` simulated live stream |
| §43 Security (partial) | No secrets in code, `.env.example`, provider fallback, input validation via Pydantic, log redaction. Auth/authz/rate-limiting/audit-logging **not implemented** (see SECURITY.md) |
| §44-45 Error handling / freshness | Loading/error/empty states throughout the frontend; `DataFreshness` component flags stale data; global exception handler on the backend |
| §47-48 Testing / CI | 54 backend + 12 frontend tests; GitHub Actions running both plus lint/build, demo-mode only, no secrets required |
| §49 Documentation | README, ARCHITECTURE, DEVELOPMENT, SECURITY, PROJECT_STATUS, CHANGELOG, docs/{data-sources,signal-engine,backtesting,ai,api,database,deployment,testing} |
| §50-52 Windows/Docker/localhost | `setup.bat`/`start.bat`/`stop.bat`/`setup.ps1`/`start.ps1`, `docker-compose.yml`, runs on localhost:3000 (frontend) / localhost:8000 (backend) |
| §53 Health | `/health` and `/api/v1/system/status` implemented |
| §54 Observability | Structured JSON logs with request IDs, durations, secret redaction |
| §60-62 Safety rules | No fabricated real market data; demo labeled everywhere; no "guaranteed"/"certain"/"risk-free" language (enforced by test); no real-money order path exists in the codebase |

## Not implemented (explicit roadmap, not silently skipped)

These are large subsystems that were not built in this pass. Each has a
provider interface, schema stub, or design doc already in place to make
future work additive rather than a rewrite:

- **Options & Futures engines** (§16-17): strikes, OI, PCR, max pain,
  Greeks, buildup classification — no data source or engine yet.
- **Corporate Events calendar** (§20): interface exists (`CorporateDataProvider`), no implementation.
- **News + market-reaction classification** (§19): would build on the
  existing demo news + candle data but the before/after price-reaction
  analysis itself isn't implemented.
- **IPO Intelligence** (§38).
- **AI Research Engine / RAG / natural-language screener** (§27-30): see `docs/ai.md` for the design and the non-negotiable data-safety rule it must follow.
- **Backtesting engine** (§31-32): see `docs/backtesting.md` for the mandatory anti-lookahead design; the indicator layer is already lookahead-safe and tested for it.
- **Paper trading, Strategy Lab, AI Strategy Lab** (§33-35).
- **Alert engine** (§36): no scheduled workers, no notification delivery.
- **Portfolio** (§37).
- **Postgres/Redis persistence** (§42, §51): `docker-compose.yml` provisions both; the backend doesn't use them yet (see `docs/database.md`) since the demo data volume doesn't require it.
- **Auth/authz/rate limiting/audit logging** (§43): see `SECURITY.md`.

## Acceptance checklist (§63) — current state

Working: frontend starts (1), backend starts (2), dashboard renders (5),
stock search/list works (6), charts work (7), indicators work (8), screener
works (9), volume anomaly works (10), news works (13), sector analysis
works (15), signals work (16), signal explanations work (17), GitHub CI
passes (22), frontend build passes (23), backend tests pass (24), no
console errors observed in manual Playwright smoke test (25), documentation
exists (26), git repository clean at each commit (27), latest version
committed and pushed (28).

Not applicable yet (feature not built): database starts as a distinct step
(3 — no DB dependency yet), options demo (11), futures demo (12), events
(14), backtesting (18), paper trading (19), AI interface (20), alerts (21).

## Required external credentials

**None.** The application runs fully in demo mode with zero external
accounts.

## Optional external credentials (only needed once a real provider is implemented)

- `MARKET_DATA_API_KEY` — for a live market data vendor (not yet integrated)
- `NEWS_API_KEY` — for a live news vendor (not yet integrated)
- `LLM_API_KEY` — for the AI research assistant (not yet integrated)
- `TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID` — for Telegram alert delivery (alert engine not yet integrated)

None of these are read unless the matching `*_PROVIDER` setting is switched
away from `demo`/`none`, and none are required for anything currently built
to work.

## Suggested next milestones (in priority order)

1. Corporate events + news/market-reaction classification (extends existing demo news/candles, no new infra)
2. Options/futures demo engine (mirrors the existing demo-provider pattern)
3. Backtesting engine against the existing indicator/signal layer (anti-lookahead tests first)
4. Paper trading (depends on #3's position/ledger model)
5. Postgres persistence for watchlists/portfolios/alerts (currently client-localStorage-only for watchlist)
6. Alert engine + notification providers
7. AI/RAG research assistant (highest effort, needs a real corpus + LLM vendor decision)
