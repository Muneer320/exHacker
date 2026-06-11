@echo off
title exHacker Launcher
color 0A

echo.
echo  ==========================================
echo   exHacker — Starting All Services
echo  ==========================================
echo.

REM ── Backend ──────────────────────────────────
echo  [1/2] Starting Backend  (FastAPI on :8000)
start "exHacker Backend" cmd /k "cd /d %~dp0backend && uvicorn api.main:app --reload --host 0.0.0.0 --port 8000 --timeout-keep-alive 300 --env-file %~dp0.env"

REM Wait 3 seconds for backend to initialise
timeout /t 3 /nobreak >nul

REM ── Frontend ─────────────────────────────────
echo  [2/2] Starting Frontend (Next.js on :3000)
start "exHacker Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo  Both servers are starting in separate windows.
echo  Open http://localhost:3000 in your browser.
echo.
pause
