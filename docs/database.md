# Database (design — not yet implemented)

The backend currently holds **no database**. `DemoMarketDataProvider` and
`DemoNewsProvider` compute everything on demand from a seeded RNG, which is
fast enough (single-digit milliseconds per request) that persistence hasn't
been necessary yet at this build's scale (5 indices + 25 stocks).

## Target design

- **PostgreSQL** as the system of record for anything that must persist
  across restarts once real providers exist: instrument metadata, corporate
  events, user watchlists/portfolios/alerts, paper-trading ledgers,
  backtest results.
- **Time-series storage** for OHLCV history, structured so it can migrate to
  a TimescaleDB hypertable (partitioned by time) without an application
  rewrite - i.e. keep the schema append-only and indexed by `(symbol,
  timestamp)`.
- **Indexes**: `(symbol, timestamp)` on any candles table;
  `(user_id, symbol)` on watchlist/alerts tables; avoid scanning full
  history for a dashboard refresh — use materialized views or precomputed
  daily aggregates for anything the dashboard polls frequently.
- **Redis** for caching computed indicators/signals per `(symbol, as_of
  minute)` so repeated dashboard polling doesn't recompute indicators from
  scratch on every request once real data volume makes that expensive.

## Why this order

`docker-compose.yml` already provisions Postgres and Redis so the
infrastructure is one command away, but wiring the backend to use them was
deprioritized in favor of getting the full vertical slice (data → analytics
→ API → UI) working and tested first. Adding persistence now is a matter of
introducing a repository layer under `app/providers/` / a new `app/db/`
module without changing `app/analytics/` (which is already pure/stateless)
or the API contracts in `app/schemas/`.
