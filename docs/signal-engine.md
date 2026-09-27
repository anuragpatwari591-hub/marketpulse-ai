# Signal Engine

Implementation: `backend/app/analytics/signals.py`.

## Weights (configurable via `SignalWeights`)

| Factor | Weight | Source today |
|---|---|---|
| Technical | 20% | RSI(14), MACD vs signal, price vs EMA20 |
| Volume | 15% | Relative volume classification (normal/elevated/unusual/extreme) |
| Price Action | 15% | Percentile position within the recent 60-day range |
| Derivatives | 15% | **Unavailable** — options/futures engine not built; defaulted to neutral 50 |
| News Catalyst | 15% | Sentiment × importance of the most relevant recent demo news |
| Market Regime | 10% | Rule-based trend classification (see `docs/backtesting.md` for why this is not LLM-derived) |
| Sector Strength | 5% | Today's average change of the stock's sector peers |
| Fundamentals | 5% | **Unavailable** — no fundamentals data source; defaulted to neutral 50 |

Weights must sum to 1.0 (`SignalWeights.validate()` raises otherwise).

## Why unavailable factors default to neutral instead of being dropped

Silently renormalizing the remaining weights to 100% when a factor is
missing would let a strong technical/volume push masquerade as a
stronger composite score than it should be. Defaulting to 50 (neutral)
keeps the factor's weight "spent" without pushing the score in either
direction, and the evidence string says explicitly why
(`"derivatives data not available in this build ... defaulted neutral"`).
This is surfaced to the frontend and shown in the signal detail view's
Risks section.

## Output contract

Every `Signal` (see `backend/app/schemas/signals.py`) includes:

- `score` (0-100) and `label` (Very Strong / Strong / Watch / Weak / Neutral)
- `direction` (bullish / bearish / neutral) — never a bare BUY/SELL
- `contributions`: one `FactorContribution` per factor with raw score,
  weight, weighted score, and a human-readable evidence string
- `risks`, `invalidation`, `scenarios` — required, not optional
- `disclaimer` — a fixed string that the codebase enforces never claims a
  guarantee (`tests/test_signals_and_risk.py::test_generate_signal_never_says_guaranteed`)

## Calibration status

The composite score is **not** a calibrated probability of anything. No
backtesting has been run against it yet (the backtesting engine itself is
not built - see `docs/backtesting.md`), so it should be read purely as "how
many of these eight measurable factors currently point the same way, and by
how much," not as a win-rate estimate.
