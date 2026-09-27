# AI Research Engine & RAG (design — not yet implemented)

`backend/app/providers/base.py` defines `LLMProvider` as an abstraction so
the eventual AI research assistant is not tied to one vendor. No concrete
LLM provider or RAG pipeline is implemented in this build.

## Non-negotiable data-safety rule (from the product spec)

The LLM must never invent prices, volume, OI, news, financial results,
corporate events, or market statistics. When a numeric answer is needed, the
assistant must call the structured API (`docs/api.md`) first and pass the
retrieved values into the prompt/context; when a source is needed, it must
retrieve the actual source. If the data genuinely isn't available, the
answer must say `DATA UNAVAILABLE` rather than approximate.

## Planned architecture

1. **Retrieval layer**: index corporate filings, news, internal analytics
   output (indicators/signals/anomalies), and historical records. Every
   answer exposes which sources it drew from.
2. **Natural-language screener**: parse a query like "F&O stocks with volume
   above 2x average, rising OI, price above VWAP, fresh positive catalyst"
   into the same structured filters the `/api/v1/screener` endpoint already
   accepts (see `docs/api.md`) — this is additive to the existing endpoint,
   not a replacement.
3. **Research capabilities**: explain price moves, summarize news, explain
   option-chain/OI behavior (once the options/futures engines exist),
   compare stocks/sectors, generate reports, find historical analogues.
4. **AI Strategy Lab** (self-improvement loop): analyze historical signals →
   propose improvements → backtest → validate → human approval → git branch
   → tests → optional merge. It must never silently modify the production
   signal weights.

## Why this isn't built yet

Building a credible RAG pipeline requires a real corpus (filings/news) and a
selected LLM vendor - both are provider decisions best left to whoever
deploys this, per the interface-first approach described in
`docs/data-sources.md`. The interface and the data-safety contract above are
in place so the implementation, once started, has clear rules to satisfy
and tests to write against (e.g. "assert every numeric claim in a response
matches a value returned by a structured endpoint").
