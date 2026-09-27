# Security

## Secrets

- No API key, token, password, or broker credential is ever committed to
  this repository. `.env` is git-ignored; `.env.example` documents variable
  *names* only, never values.
- Every provider interface (`backend/app/providers/base.py`) falls back to
  its demo implementation when credentials are absent — the application is
  never blocked from starting by a missing secret, and never guesses or
  invents one.
- Structured logs (`backend/app/core/logging.py`) redact any field whose key
  matches `api_key`, `token`, `password`, `secret`, or `authorization`
  (case-insensitive) before writing it out.

## Current security posture (demo build)

This build has **no authentication/authorization layer, no rate limiting,
and no audit logging** yet — it is a local-first demo application. Do not
expose it directly to the public internet without adding those first. They
are on the roadmap (see PROJECT_STATUS.md) alongside real trading/broker
integration, which additionally requires explicit user-authorized risk
controls before any real order could ever be placed (paper trading only in
this build; no real-money order path exists in the codebase at all).

## Input validation

All request bodies are validated by Pydantic models (`backend/app/schemas/`)
before reaching business logic; the risk calculator additionally rejects
non-physical inputs (zero/negative account size, entry == stop-loss, etc.)
with a 400 rather than propagating a divide-by-zero or nonsensical result.

## CORS

`CORS_ORIGINS` in `.env` controls allowed origins for the API; it defaults
to `localhost:3000` only.

## Reporting

This is a demo/educational project. If you find a real vulnerability,
please open a GitHub issue describing it without including any live
credentials or private data.
