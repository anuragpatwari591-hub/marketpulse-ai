# Deployment

## Local (current, supported)

- **Windows**: `setup.bat` then `start.bat` (PowerShell equivalents:
  `setup.ps1` / `start.ps1`).
- **macOS/Linux**: `scripts/dev.sh` after installing backend/frontend deps
  (see `DEVELOPMENT.md`).
- **Docker**: `docker compose up --build` builds `backend` (FastAPI on
  :8000) and `frontend` (static build served on :3000), and also starts
  `postgres`/`redis` even though the backend doesn't use them yet (see
  `docs/database.md`).

## Ports

| Service | Port |
|---|---|
| Frontend | 3000 |
| Backend | 8000 |
| Postgres | 5432 |
| Redis | 6379 |

## Environment

Copy `.env.example` to `.env`. Every variable has a demo-safe default; the
app starts and runs fully without any of them set. See `SECURITY.md` for
the secrets-handling rules and `PROJECT_STATUS.md` for which credentials
are required vs. optional for which (not-yet-built) feature.

## Production hosting (not yet set up)

This build has no authentication, rate limiting, or TLS termination
configured, and is intended for local/demo use. Before deploying it
anywhere reachable from the public internet: add an auth layer, put it
behind a reverse proxy with TLS, set restrictive `CORS_ORIGINS`, and add the
rate limiting / audit logging described in `SECURITY.md`'s roadmap section.

## CI

`.github/workflows/ci.yml` runs backend pytest and frontend lint/test/build
on every push and PR, entirely against demo providers - no secrets are
required for CI to pass.
