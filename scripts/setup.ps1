# exHacker Development Setup Script
Write-Host "Setting up exHacker development environment..." -ForegroundColor Cyan

# Backend setup
Write-Host "`nSetting up backend..." -ForegroundColor Yellow
Set-Location backend
uv sync
Write-Host "Backend dependencies installed" -ForegroundColor Green

# Backend setup complete
Set-Location ..

# Frontend setup
Write-Host "`nSetting up frontend..." -ForegroundColor Yellow
Set-Location frontend
npm install
Write-Host "Frontend dependencies installed" -ForegroundColor Green
Set-Location ..

Write-Host "`nSetup complete! See README.md for instructions." -ForegroundColor Green
