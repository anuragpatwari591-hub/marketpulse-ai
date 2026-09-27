@echo off
REM MarketPulse AI - start backend + frontend for local development on Windows
setlocal

echo Starting MarketPulse AI backend on http://localhost:8000 ...
start "MarketPulse Backend" cmd /k "cd backend && call .venv\Scripts\activate.bat && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

timeout /t 3 /nobreak >nul

echo Starting MarketPulse AI frontend on http://localhost:3000 ...
start "MarketPulse Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo MarketPulse AI is starting in two new windows:
echo   Frontend:  http://localhost:3000
echo   Backend:   http://localhost:8000
echo   API docs:  http://localhost:8000/docs
echo.
echo Close those windows (or run stop.bat) to stop the application.
endlocal
