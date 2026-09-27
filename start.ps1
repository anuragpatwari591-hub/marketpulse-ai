#!/usr/bin/env pwsh
# MarketPulse AI - start backend + frontend for local development (PowerShell)

Write-Host "Starting MarketPulse AI backend on http://localhost:8000 ..." -ForegroundColor Cyan
Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd backend; .\.venv\Scripts\Activate.ps1; uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

Start-Sleep -Seconds 3

Write-Host "Starting MarketPulse AI frontend on http://localhost:3000 ..." -ForegroundColor Cyan
Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"

Write-Host "`nMarketPulse AI is starting in two new windows:" -ForegroundColor Green
Write-Host "  Frontend:  http://localhost:3000"
Write-Host "  Backend:   http://localhost:8000"
Write-Host "  API docs:  http://localhost:8000/docs"
