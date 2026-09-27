#!/usr/bin/env pwsh
# MarketPulse AI - one-time setup for Windows (PowerShell)

Write-Host "=== MarketPulse AI setup ===" -ForegroundColor Cyan

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env from .env.example"
}

Write-Host "`n--- Backend: creating virtualenv and installing dependencies ---" -ForegroundColor Cyan
Push-Location backend
python -m venv .venv
& .\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
deactivate
Pop-Location

Write-Host "`n--- Frontend: installing dependencies ---" -ForegroundColor Cyan
Push-Location frontend
npm install
Pop-Location

Write-Host "`nSetup complete. Run .\start.ps1 to launch MarketPulse AI." -ForegroundColor Green
