# Data Sources

## Today: demo only

`backend/app/providers/demo_market_data.py` generates deterministic OHLCV
series with a seeded geometric-random-walk model (annualized volatility per
symbol, small upward drift, ~4%/day chance of a fat-tail jump to simulate
news/earnings events) for:

- **Indices**: NIFTY, BANKNIFTY, FINNIFTY, MIDCAP, INDIA VIX
- **25 stocks** across IT, Banking, Financial Services, Auto, Pharma, FMCG,
  Energy, Metals, Realty, Defence, Railways, Renewables, Telecom, Chemicals

`backend/app/providers/demo_news.py` generates 40 seeded synthetic articles
across 13 corporate-event categories (Earnings, Order, Contract,
Acquisition, Fundraising, Regulation, Management, Product launch, Dividend,
Buyback, Credit rating, Capacity expansion, Partnership).

Determinism: the same `(symbol, seed)` always returns the same historical
series (`tests/test_demo_provider.py`), so analytics and signal scores are
reproducible run to run. A "live" jitter reseeds from the current minute
bucket so `/ws/market` and repeated quote calls feel like they're moving,
without breaking determinism within a given minute.

**None of this is real market data.** Every payload is flagged `is_demo: true`.

## Plugging in a real provider

Implement `MarketDataProvider` / `NewsProvider` / `CorporateDataProvider`
from `backend/app/providers/base.py`, then point the relevant
`*_PROVIDER` environment variable at it (see `.env.example`). If its API key
is missing at startup, `Settings._resolve()` reports it as still running in
demo mode rather than crashing — see `SECURITY.md`.

## Candidate real providers (not integrated - names only, no code depends on any of these)

- **Market data**: NSE/BSE data vendors, a broker's market-data API
- **News**: a financial news API, RSS aggregation with NLP classification
- **Corporate actions**: exchange corporate-announcement feeds
- **Broker** (paper/live trading): any broker offering an order API - out of
  scope until paper trading itself is built

Choosing/integrating a specific vendor is a business decision left to the
user; this codebase only needs the interface implemented once one is picked.
