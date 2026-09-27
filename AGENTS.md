# Notes for AI agents working on this repository

- Read `PROJECT_STATUS.md` first — it is the authoritative list of what's
  implemented vs. roadmap. Don't assume a spec section is done just because
  it's mentioned somewhere; check the status table.
- Never fabricate market data. All real-data code paths go through the
  provider interfaces in `backend/app/providers/base.py`; the only
  implementations that exist today are the `demo_*` ones, and every one of
  their responses must keep carrying `is_demo: true`.
- Never let a signal, alert, or AI response claim something is "guaranteed",
  "certain", "100% accurate", or "risk-free". There's a test for this
  (`backend/tests/test_signals_and_risk.py::test_generate_signal_never_says_guaranteed`)
  — keep it passing.
- `backend/app/analytics/` must stay pure (no I/O, no provider calls) and
  causal (no lookahead) — see `docs/backtesting.md` for why this matters
  even before a backtester exists.
- Before adding a new feature, check whether a provider interface or schema
  already exists for it in `providers/base.py` / `schemas/` before creating
  a new one.
- Run `cd backend && .venv/bin/python -m pytest -q` and
  `cd frontend && npm run test && npm run build` before considering a
  change complete. Don't commit a broken build.
- Follow conventional commits (`feat:`, `fix:`, `refactor:`, `test:`,
  `docs:`, `chore:`, `perf:`, `security:`).
- Update `PROJECT_STATUS.md` and `CHANGELOG.md` when you complete a
  roadmap item — don't leave them stale.
