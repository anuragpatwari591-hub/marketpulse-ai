#!/usr/bin/env bash
# Convenience launcher for macOS/Linux. Windows users should use start.bat / start.ps1.
set -euo pipefail
cd "$(dirname "$0")/.."

(cd backend && .venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000) &
BACKEND_PID=$!

(cd frontend && npm run dev -- --host 0.0.0.0 --port 3000) &
FRONTEND_PID=$!

trap 'kill $BACKEND_PID $FRONTEND_PID 2>/dev/null' EXIT INT TERM

echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "API docs: http://localhost:8000/docs"
wait
