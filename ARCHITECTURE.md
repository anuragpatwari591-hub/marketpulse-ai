# Architecture

## Overview

```
frontend/  React + TypeScript + Vite + Tailwind — the terminal UI
backend/   FastAPI — providers, analytics engines, REST + WebSocket API
docs/      design notes per subsystem
```

Two top-level services today (`backend`, `frontend`). `docker-compose.yml` also
wires up `postgres` and `redis` for the persistence/caching layer described
below, but the backend does not currently require either to run — see
"Current vs. target state".

## Backend layout

```
backend/app/
  core/            settings (env-driven), structured JSON logging
  providers/       provider interfaces + demo implementations
    base.py           abstract MarketDataProvider / NewsProvider / CorporateDataProvider / LLMProvider / BrokerProvider / NotificationProvider
    demo_market_data.py  deterministic seeded OHLCV generator (indices + stocks)
    demo_news.py          deterministic seeded synthetic news
  analytics/       pure, testable computation - no I/O
    indicators.py     SMA/EMA/RSI/MACD/ATR/Bollinger/VWAP/support-resistance/gap
    volume.py          rolling averages, relative volume, z-score classification
    anomaly.py         composite 0-100 anomaly score with itemized breakdown
    regime.py          rule-based trend/volatility/breadth regime detection
    signals.py         multi-factor weighted signal engine
    risk.py            position-sizing / risk calculator
  schemas/         Pydantic response/request models
  api/v1/
    endpoints/       one module per resource (system, market, stocks, screener, signals, news, risk)
    websockets.py    /ws/market simulated live stream
    router.py        combines endpoint routers under /api/v1
  main.py          FastAPI app, CORS, request-id middleware, structured logging, exception handler
```

### Why "demo" providers are first-class, not an afterthought

Every external integration point (`app/providers/base.py`) is an abstract
class. `app/core/config.py` selects an implementation per provider by
environment variable and **always falls back to the demo implementation**
if the selected mode's credentials are absent. This means:

- The app runs completely standalone, with zero external accounts, out of the box.
- Adding a real provider later is a matter of implementing the interface and
  wiring it into `get_settings().*_provider`, not rearchitecting analytics or the API.
- Every API response that originates from demo data carries `is_demo: true`,
  and the frontend renders a persistent "DEMO MODE" banner - the two are
  never allowed to drift apart silently.

### Signal engine design

`analytics/signals.py` computes eight weighted factors (technical 20%,
volume 15%, price action 15%, derivatives 15%, news catalyst 15%, market
regime 10%, sector strength 5%, fundamentals 5% — see `docs/signal-engine.md`).
Derivatives and fundamentals have no real data source in this build, so they
are explicitly defaulted to a neutral 50 with a note in their evidence
string, rather than silently dropped from the weighted sum (which would
overstate the confidence of the other factors) or fabricated.

The API/schema layer (`schemas/signals.py`) makes it structurally impossible
to return a bare direction without evidence: `Signal` always carries
`contributions`, `risks`, `invalidation`, `scenarios` and a `disclaimer`.

### Anti-lookahead discipline

All of `analytics/indicators.py` is written so that index `i` of any output
series depends only on inputs at indices `<= i`. `tests/test_indicators.py::test_indicators_have_no_lookahead`
asserts this directly by comparing indicator output on a truncated series vs.
the same series with wild future values appended. This matters most once a
backtesting engine is added (see `docs/backtesting.md` for the anti-lookahead
requirements that engine must satisfy); the indicator layer is already safe
for that use.

## Frontend layout

```
frontend/src/
  lib/api.ts             typed fetch client (one function + type per endpoint)
  store/watchlist.ts      zustand store, persisted to localStorage
  components/
    layout/Layout.tsx      sidebar + demo banner shell
    ui/primitives.tsx       Card, Badge, ChangeBadge, loading/empty/error states, DataFreshness
    StockChart.tsx           TradingView Lightweight Charts candlestick wrapper
  pages/                   one file per route (see App.tsx for the route table)
```

State is split deliberately: **TanStack Query** owns all server data
(caching, polling via `refetchInterval`, loading/error states); **Zustand**
owns the one piece of durable client-only state (the watchlist). There is no
Redux-style global store for server data - that would just be a second cache
fighting the first.

## Current vs. target state

| Layer | Target (per spec) | Current |
|---|---|---|
| Persistence | PostgreSQL + TimescaleDB-style time-series design | Not implemented — everything is computed on demand from the in-memory demo generator. `docker-compose.yml` provisions Postgres/Redis for when this lands. |
| Cache | Redis | Not implemented |
| Real-time | WebSocket fed by a live/broker feed | `/ws/market` pushes the demo provider's quotes on a timer — real transport, simulated data |
| AI/RAG | LLM abstraction + retrieval over filings/news | `LLMProvider` interface exists in `providers/base.py`; no implementation yet |
| Options/futures/backtesting/paper trading/alerts/portfolio | Full engines per spec | Not implemented — see PROJECT_STATUS.md roadmap |

The interfaces for all of the above already exist so that adding them is
additive rather than a rewrite.
