# CHIMERA AUTARCH - Simple Launcher
# Double-click this file or run in PowerShell

Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "   CHIMERA AUTARCH v3.0 - Starting Up...       " -ForegroundColor Green
Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Go to project directory
Set-Location C:\Drox_AI

# Activate virtual environment
Write-Host "[1/3] Activating environment..." -ForegroundColor Yellow
& .\droxai-env\Scripts\Activate.ps1

# Check if activation worked
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to activate virtual environment" -ForegroundColor Red
    Write-Host "Try running: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host "✓ Environment activated" -ForegroundColor Green

# Check dependencies
Write-Host "[2/3] Checking dependencies..." -ForegroundColor Yellow
$deps = python -c "import aiohttp, websockets; print('OK')" 2>$null

if ($deps -ne "OK") {
    Write-Host "❌ Missing dependencies. Installing..." -ForegroundColor Yellow
    pip install aiohttp websockets --quiet
    Write-Host "✓ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "✓ Dependencies OK" -ForegroundColor Green
}

# Start the server
Write-Host "[3/3] Starting CHIMERA AUTARCH..." -ForegroundColor Yellow
Write-Host ""
Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "   Dashboard: http://localhost:3000           " -ForegroundColor Green
Write-Host "   WebSocket: ws://localhost:3001             " -ForegroundColor Green
Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

python src\chimera\chimera_main.py
