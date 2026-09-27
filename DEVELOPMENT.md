# Development guide

## Prerequisites

- Python 3.11+
- Node.js 20+
- (Optional) Docker + Docker Compose

## Backend

```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app.main:app --reload --port 8000
```

Run tests:

```bash
cd backend
.venv/bin/python -m pytest -q
```

The backend needs no `.env` file to run — every setting in
`app/core/config.py` has a demo-safe default. Copy `.env.example` to `.env`
only when you want to override something (log level, CORS origins, a real
provider once one exists).

## Frontend

```bash
cd frontend
npm install
npm run dev
```

Runs on http://localhost:3000 and proxies `/api` and `/ws` to
`http://localhost:8000` (see `vite.config.ts`) — start the backend first.

Other scripts:

```bash
npm run test    # vitest
npm run lint    # oxlint
npm run build   # tsc -b && vite build
```

## Adding a new analytics function

1. Add a pure function to the relevant module in `backend/app/analytics/` —
   no I/O, no provider calls. Take plain lists/values in, return plain
   values/dicts out.
2. Write a unit test in `backend/tests/` first for the edge cases (empty
   input, insufficient history, all-zero variance).
3. Wire it into the relevant endpoint in `backend/app/api/v1/endpoints/`.
4. If the frontend needs it, add the field to the matching interface in
   `frontend/src/lib/api.ts` and render it.

## Adding a new provider implementation

1. Implement the abstract class from `backend/app/providers/base.py`.
2. Add a `..._API_KEY` and `..._PROVIDER` setting in `app/core/config.py`
   following the existing pattern — never hardcode a key.
3. Wire selection logic so that missing credentials fall back to the demo
   provider (see `Settings._resolve` and `Settings.provider_status`).
4. Never remove the demo provider — it is the CI and offline-development
   baseline.

## Conventional commits

`feat:` `fix:` `refactor:` `test:` `docs:` `chore:` `perf:` `security:` —
used for every commit in this repository's history.

## Resource-conscious iteration

Before editing, read the specific file you're changing rather than
regenerating whole modules. Run the targeted test file for what you
touched; run the full suite (`pytest -q` / `npm run test`) before a
milestone commit. Don't rebuild working modules from scratch.
