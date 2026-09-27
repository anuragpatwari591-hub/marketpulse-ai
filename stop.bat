@echo off
REM MarketPulse AI - stop backend/frontend dev processes on Windows
setlocal

echo Stopping MarketPulse AI processes (uvicorn / vite / node) ...
taskkill /FI "WINDOWTITLE eq MarketPulse Backend*" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq MarketPulse Frontend*" /T /F >nul 2>&1

echo Done. If a window remains open, close it manually.
endlocal
