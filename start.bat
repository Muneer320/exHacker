@echo off
REM ============================================================
REM  exHacker — Single Start Script
REM  Starts backend (FastAPI) + frontend (Next.js) in one click
REM ============================================================

title exHacker — Starting...
echo.
echo  =========================================
echo   exHacker AI Hackathon Platform
echo   Starting all services...
echo  =========================================
echo.

REM ── Check Python ────────────────────────────────────────────
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python not found. Install Python 3.11+ and try again.
    pause
    exit /b 1
)

REM ── Check Node ──────────────────────────────────────────────
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js not found. Install Node.js 18+ and try again.
    pause
    exit /b 1
)

REM ── Navigate to project root ─────────────────────────────────
cd /d "%~dp0"

REM ── Setup backend .env if missing ───────────────────────────
if not exist "backend\.env" (
    echo [INFO] Creating backend\.env from example...
    copy "backend\.env.example" "backend\.env" >nul
    echo [INFO] Please fill in API keys in backend\.env
)

REM ── Install backend deps if venv missing ────────────────────
if not exist "backend\.venv" (
    echo [INFO] Setting up Python virtual environment...
    python -m venv backend\.venv
    echo [INFO] Installing backend dependencies...
    call backend\.venv\Scripts\activate.bat
    pip install -r backend\requirements.txt --quiet
) else (
    call backend\.venv\Scripts\activate.bat
)

REM ── Install frontend deps if node_modules missing ───────────
if not exist "frontend\node_modules" (
    echo [INFO] Installing frontend dependencies...
    cd frontend
    npm install --silent
    cd ..
)

echo.
echo  [1/2] Starting Backend ^(FastAPI on :8000^)...
start "exHacker Backend" /min cmd /c "call backend\.venv\Scripts\activate.bat && cd backend && python -m uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload"

REM Wait for backend to boot
timeout /t 3 /nobreak >nul

echo  [2/2] Starting Frontend ^(Next.js on :3000^)...
start "exHacker Frontend" /min cmd /c "cd frontend && npm run dev"

echo.
echo  =========================================
echo   Services Started!
echo  
echo   Frontend:  http://localhost:3000
echo   Backend:   http://localhost:8000
echo   API Docs:  http://localhost:8000/docs
echo   Health:    http://localhost:8000/health
echo  =========================================
echo.

REM Open browser after delay
timeout /t 4 /nobreak >nul
start "" "http://localhost:3000"

echo  Press any key to stop all services...
pause >nul

REM Kill background processes
taskkill /f /fi "WINDOWTITLE eq exHacker Backend" >nul 2>nul
taskkill /f /fi "WINDOWTITLE eq exHacker Frontend" >nul 2>nul
echo  All services stopped.
