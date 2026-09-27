# Testing

## Backend — pytest (`backend/tests/`, 54 tests)

| File | Covers |
|---|---|
| `test_indicators.py` | SMA/EMA/RSI/MACD/ATR/Bollinger/VWAP/support-resistance/gap correctness + **no-lookahead** proof |
| `test_volume.py` | Rolling averages, relative volume, z-score classification thresholds |
| `test_regime_and_anomaly.py` | Bull/bear regime detection, composite anomaly scoring, price-spike flagging |
| `test_signals_and_risk.py` | Signal weight validation, factor-count/shape, news moving the score, banned-language check (no "guaranteed"/"certain profit"/etc.), risk calculator math incl. lot-size rounding and edge cases |
| `test_demo_provider.py` | Determinism of the seeded generator, per-symbol distinctness, unknown-symbol error, demo flagging |
| `test_api.py` | Every endpoint: happy path, 404 on unknown symbol, 400 on invalid risk input, demo flags present |

Run: `cd backend && .venv/bin/python -m pytest -q`

## Frontend — Vitest (`frontend/src/**/*.test.tsx`, 12 tests)

- `components/ui/primitives.test.tsx` — ChangeBadge sign/formatting, DemoBanner always states "not live", Badge rendering
- `store/watchlist.test.ts` — add/remove/toggle/persist logic
- `lib/api.test.ts` — success parsing and `ApiError` propagation with the server's `detail` message
- `pages/Dashboard.test.tsx` — loading state renders before data resolves

Run: `cd frontend && npm run test`

## Manual/E2E verification performed during this build

A headless-Chromium smoke pass (Playwright) loaded `/`, `/markets`,
`/stocks/RELIANCE`, `/screener`, `/signals`, `/signals/RELIANCE`, `/risk`
against the real dev server + backend, asserted zero console/page errors,
confirmed the DEMO MODE banner renders on every page, and captured
screenshots of the dashboard, stock detail (candlestick chart), and signal
detail (factor breakdown) views for visual review. Playwright is not wired
into CI in this build (E2E would need the backend running as a CI service);
that's a reasonable next step once the app grows past this vertical slice.

## What's not covered yet

Anything not implemented (options/futures, backtesting, paper trading,
alerts, AI/RAG) has no tests because it has no code. `docs/backtesting.md`
specifies the lookahead-bias test that engine must include once built.
