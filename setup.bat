@echo off
REM MarketPulse AI - one-time setup for Windows
setlocal

echo === MarketPulse AI setup ===

if not exist ".env" (
    copy ".env.example" ".env"
    echo Created .env from .env.example
)

echo.
echo --- Backend: creating virtualenv and installing dependencies ---
cd backend
python -m venv .venv
call .venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt
call .venv\Scripts\deactivate.bat
cd ..

echo.
echo --- Frontend: installing dependencies ---
cd frontend
call npm install
cd ..

echo.
echo Setup complete. Run start.bat to launch MarketPulse AI.
endlocal
