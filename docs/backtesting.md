# Backtesting (design — not yet implemented)

No backtesting engine exists in this build. This document records the
design constraints it must satisfy when built, so the eventual
implementation isn't designed in a vacuum.

## Mandatory anti-lookahead rule

A simulated signal at timestamp `T` may only use price, volume, news, OI,
corporate-event, indicator, or fundamental data that was actually available
at `T`. Concretely:

- Indicator functions must remain pure and causal (already true today - see
  `backend/app/analytics/indicators.py` and
  `tests/test_indicators.py::test_indicators_have_no_lookahead`, which
  proves output at index `i` is unaffected by data appended after `i`).
- A backtest driver must iterate forward in time and only ever pass the
  engine a slice `data[:i+1]`, never the full series.
- News/corporate-event timestamps used in a backtest must be the
  *publication* timestamp, not any later "effective" date.
- Any point-in-time restated fundamental/financial data (e.g. a later
  restatement of a quarterly result) must use the value as it was first
  reported, not the corrected value.

The test suite for the eventual engine should include an explicit
lookahead-bias test: run the same backtest twice, once with the full
dataset available and once with future rows deleted before each simulated
day, and assert identical trade-by-trade results.

## Planned metrics

Return, CAGR, win rate, average win/loss, profit factor, expectancy, max
drawdown, Sharpe, Sortino, Calmar, longest losing streak, trade count —
computed from a position ledger that itself accounts for slippage,
brokerage, and position sizing (reusing `backend/app/analytics/risk.py` for
the sizing math).

## Relationship to the signal engine

The composite score in `docs/signal-engine.md` has not been backtested and
must not be described as calibrated until this engine exists and has been
run against it.
