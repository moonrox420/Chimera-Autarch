# CHIMERA NEXUS - Windows Startup Script
# Starts the complete CHIMERA system on Windows

Write-Host "ðŸš€ Starting CHIMERA NEXUS v3.0" -ForegroundColor Cyan
Write-Host "===============================" -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment
if (Test-Path "droxai-env\Scripts\Activate.ps1") {
  Write-Host "ðŸ”§ Activating virtual environment..." -ForegroundColor Yellow
  & .\droxai-env\Scripts\Activate.ps1
}
else {
  Write-Host "âš ï¸  Virtual environment not found. Run install_nexus.ps1 first." -ForegroundColor Red
  exit 1
}

# Check if dependencies are installed
Write-Host "ðŸ” Checking dependencies..." -ForegroundColor Yellow

  $missingDeps = @()

  python -c "import tensorflow" 2>$null
  if ($LASTEXITCODE -ne 0) { $missingDeps += "tensorflow" }

  python -c "import sklearn" 2>$null
  if ($LASTEXITCODE -ne 0) { $missingDeps += "scikit-learn" }

  python -c "import websockets" 2>$null
  if ($LASTEXITCODE -ne 0) { $missingDeps += "websockets" }

  python -c "import aiosqlite" 2>$null
  if ($LASTEXITCODE -ne 0) { $missingDeps += "aiosqlite" }

  python -c "import numpy" 2>$null
  if ($LASTEXITCODE -ne 0) { $missingDeps += "numpy" }

  if ($missingDeps.Count -gt 0) {
    Write-Host "âš ï¸  Missing dependencies: $($missingDeps -join ', ')" -ForegroundColor Red
    Write-Host "Run: .\install_nexus.ps1" -ForegroundColor Yellow
    exit 1
  }

  Write-Host "âœ… All dependencies found!" -ForegroundColor Green
  Write-Host ""

  # Display banner
  Write-Host @"
    â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
    â•‘                                                       â•‘
    â•‘         â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—â–ˆâ–ˆâ•—  â–ˆâ–ˆâ•—â–ˆâ–ˆâ•—â–ˆâ–ˆâ–ˆâ•—   â–ˆâ–ˆâ–ˆâ•—â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—  â•‘
    â•‘        â–ˆâ–ˆâ•”â•â•â•â•â•â–ˆâ–ˆâ•‘  â–ˆâ–ˆâ•‘â–ˆâ–ˆâ•‘â–ˆâ–ˆâ–ˆâ–ˆâ•— â–ˆâ–ˆâ–ˆâ–ˆâ•‘â–ˆâ–ˆâ•”â•â•â•â•â•â–ˆâ–ˆâ•”â•â•â–ˆâ–ˆâ•— â•‘
    â•‘        â–ˆâ–ˆâ•‘     â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•‘â–ˆâ–ˆâ•‘â–ˆâ–ˆâ•”â–ˆâ–ˆâ–ˆâ–ˆâ•”â–ˆâ–ˆâ•‘â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—  â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•”â• â•‘
    â•‘        â–ˆâ–ˆâ•‘     â–ˆâ–ˆâ•”â•â•â–ˆâ–ˆâ•‘â–ˆâ–ˆâ•‘â–ˆâ–ˆâ•‘â•šâ–ˆâ–ˆâ•”â•â–ˆâ–ˆâ•‘â–ˆâ–ˆâ•”â•â•â•  â–ˆâ–ˆâ•”â•â•â–ˆâ–ˆâ•— â•‘
    â•‘        â•šâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—â–ˆâ–ˆâ•‘  â–ˆâ–ˆâ•‘â–ˆâ–ˆâ•‘â–ˆâ–ˆâ•‘ â•šâ•â• â–ˆâ–ˆâ•‘â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—â–ˆâ–ˆâ•‘  â–ˆâ–ˆâ•‘ â•‘
    â•‘         â•šâ•â•â•â•â•â•â•šâ•â•  â•šâ•â•â•šâ•â•â•šâ•â•     â•šâ•â•â•šâ•â•â•â•â•â•â•â•šâ•â•  â•šâ•â• â•‘
    â•‘                                                       â•‘
    â•‘              N E X U S   v 3 . 0                     â•‘
    â•‘         Revolutionary AI Orchestration               â•‘
    â•‘                                                       â•‘
    â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
"@ -ForegroundColor Magenta

  Write-Host ""
  Write-Host "ðŸ”® Features Active:" -ForegroundColor Cyan
Write-Host "  âœ… Self-Evolving Neural Code" -ForegroundColor Green
Write-Host "  âœ… Quantum-Inspired Optimization" -ForegroundColor Green
Write-Host "  âœ… AI Personality System (5 modes)" -ForegroundColor Green
Write-Host "  âœ… Blockchain Audit Trail" -ForegroundColor Green
Write-Host "  âœ… 3D VR Visualization" -ForegroundColor Green
Write-Host "  âœ… Voice Control Interface" -ForegroundColor Green
Write-Host "  âœ… Genetic Evolution Engine" -ForegroundColor Green
Write-Host "  âœ… LSTM Predictive Monitoring" -ForegroundColor Green
Write-Host "  âœ… Multi-Cloud Orchestration" -ForegroundColor Green
Write-Host "  âœ… Plugin Marketplace" -ForegroundColor Green
Write-Host ""

Write-Host "ðŸŒ Starting CHIMERA Heart Node..." -ForegroundColor Yellow
Write-Host ""
Write-Host "ðŸ“¡ Endpoints:" -ForegroundColor Cyan
  Write-Host "  - WebSocket:  ws://localhost:3001" -ForegroundColor White
  Write-Host "  - Dashboard:  http://localhost:3000" -ForegroundColor White
  Write-Host "  - 3D View:    http://localhost:3000/dashboard_3d.html" -ForegroundColor White
  Write-Host ""
  Write-Host "Press Ctrl+C to stop CHIMERA" -ForegroundColor Yellow
  Write-Host ""
  Write-Host "â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•" -ForegroundColor Gray
  Write-Host ""

  # Start CHIMERA
  try {
    python chimera_autarch.py
  }
  catch {
    Write-Host ""
    Write-Host "âŒ CHIMERA stopped with error: $_" -ForegroundColor Red
    exit 1
  }
  finally {
    Write-Host ""
    Write-Host "ðŸ›‘ CHIMERA NEXUS shutdown complete" -ForegroundColor Yellow
  }

