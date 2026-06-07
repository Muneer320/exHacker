# Start development environment
Write-Host "Starting exHacker development environment..." -ForegroundColor Cyan

# Start PostgreSQL
Write-Host "`nStarting PostgreSQL..." -ForegroundColor Yellow
docker compose up -d postgres

# Start backend
Write-Host "`nStarting backend..." -ForegroundColor Yellow
$backendJob = Start-Job -ScriptBlock {
    Set-Location backend
    uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
}

# Start frontend
Write-Host "`nStarting frontend..." -ForegroundColor Yellow
$frontendJob = Start-Job -ScriptBlock {
    Set-Location frontend
    npm run dev
}

Write-Host "`nDevelopment environment is starting..." -ForegroundColor Green
Write-Host "Backend: http://localhost:8000" -ForegroundColor Green
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Green
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Green

Wait-Job $backendJob, $frontendJob
