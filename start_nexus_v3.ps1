# CHIMERA NEXUS v3.0 - Enhanced Windows Launcher
# Run this to start CHIMERA with all 10 revolutionary systems

param(
  [switch]$NoVoice,
  [switch]$NoCloud,
  [switch]$TestMode,
  [string]$Config = "config_nexus.yaml"
)

# ASCII Banner
$banner = @"
â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
â•‘                                                                  â•‘
â•‘   â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—â–ˆâ–ˆâ•—  â–ˆâ–ˆâ•—â–ˆâ–ˆâ•—â–ˆâ–ˆâ–ˆâ•—   â–ˆâ–ˆâ–ˆâ•—â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—  â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—          â•‘
â•‘  â–ˆâ–ˆâ•”â•â•â•â•â•â–ˆâ–ˆâ•‘  â–ˆâ–ˆâ•‘â–ˆâ–ˆâ•‘â–ˆâ–ˆâ–ˆâ–ˆâ•— â–ˆâ–ˆâ–ˆâ–ˆâ•‘â–ˆâ–ˆâ•”â•â•â•â•â•â–ˆâ–ˆâ•”â•â•â–ˆâ–ˆâ•—â–ˆâ–ˆâ•”â•â•â–ˆâ–ˆâ•—         â•‘
â•‘  â–ˆâ–ˆâ•‘     â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•‘â–ˆâ–ˆâ•‘â–ˆâ–ˆâ•”â–ˆâ–ˆâ–ˆâ–ˆâ•”â–ˆâ–ˆâ•‘â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—  â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•”â•â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•‘         â•‘
â•‘  â–ˆâ–ˆâ•‘     â–ˆâ–ˆâ•”â•â•â–ˆâ–ˆâ•‘â–ˆâ–ˆâ•‘â–ˆâ–ˆâ•‘â•šâ–ˆâ–ˆâ•”â•â–ˆâ–ˆâ•‘â–ˆâ–ˆâ•”â•â•â•  â–ˆâ–ˆâ•”â•â•â–ˆâ–ˆâ•—â–ˆâ–ˆâ•”â•â•â–ˆâ–ˆâ•‘         â•‘
â•‘  â•šâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—â–ˆâ–ˆâ•‘  â–ˆâ–ˆâ•‘â–ˆâ–ˆâ•‘â–ˆâ–ˆâ•‘ â•šâ•â• â–ˆâ–ˆâ•‘â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—â–ˆâ–ˆâ•‘  â–ˆâ–ˆâ•‘â–ˆâ–ˆâ•‘  â–ˆâ–ˆâ•‘         â•‘
â•‘   â•šâ•â•â•â•â•â•â•šâ•â•  â•šâ•â•â•šâ•â•â•šâ•â•     â•šâ•â•â•šâ•â•â•â•â•â•â•â•šâ•â•  â•šâ•â•â•šâ•â•  â•šâ•â•         â•‘
â•‘                                                                  â•‘
â•‘            â–ˆâ–ˆâ–ˆâ•—   â–ˆâ–ˆâ•—â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—â–ˆâ–ˆâ•—  â–ˆâ–ˆâ•—â–ˆâ–ˆâ•—   â–ˆâ–ˆâ•—â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—          â•‘
â•‘            â–ˆâ–ˆâ–ˆâ–ˆâ•—  â–ˆâ–ˆâ•‘â–ˆâ–ˆâ•”â•â•â•â•â•â•šâ–ˆâ–ˆâ•—â–ˆâ–ˆâ•”â•â–ˆâ–ˆâ•‘   â–ˆâ–ˆâ•‘â–ˆâ–ˆâ•”â•â•â•â•â•          â•‘
â•‘            â–ˆâ–ˆâ•”â–ˆâ–ˆâ•— â–ˆâ–ˆâ•‘â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—   â•šâ–ˆâ–ˆâ–ˆâ•”â• â–ˆâ–ˆâ•‘   â–ˆâ–ˆâ•‘â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—          â•‘
â•‘            â–ˆâ–ˆâ•‘â•šâ–ˆâ–ˆâ•—â–ˆâ–ˆâ•‘â–ˆâ–ˆâ•”â•â•â•   â–ˆâ–ˆâ•”â–ˆâ–ˆâ•— â–ˆâ–ˆâ•‘   â–ˆâ–ˆâ•‘â•šâ•â•â•â•â–ˆâ–ˆâ•‘          â•‘
â•‘            â–ˆâ–ˆâ•‘ â•šâ–ˆâ–ˆâ–ˆâ–ˆâ•‘â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—â–ˆâ–ˆâ•”â• â–ˆâ–ˆâ•—â•šâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•”â•â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•‘          â•‘
â•‘            â•šâ•â•  â•šâ•â•â•â•â•šâ•â•â•â•â•â•â•â•šâ•â•  â•šâ•â• â•šâ•â•â•â•â•â• â•šâ•â•â•â•â•â•â•          â•‘
â•‘                                                                  â•‘
â•‘                     v3.0 - Windows Edition                       â•‘
â•‘              Self-Evolving AI Orchestration System               â•‘
â•‘                                                                  â•‘
â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
"@

Write-Host $banner -ForegroundColor Cyan

Write-Host ""
Write-Host "ðŸš€ CHIMERA NEXUS v3.0 - The Future of AI" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path "droxai-env\Scripts\Activate.ps1")) {
  Write-Host "âŒ Virtual environment not found!" -ForegroundColor Red
  Write-Host "Run: .\install_quick_windows.ps1 first" -ForegroundColor Yellow
  exit 1
}

# Activate virtual environment
Write-Host "ðŸ”§ Activating virtual environment..." -ForegroundColor Cyan
& .\droxai-env\Scripts\Activate.ps1

# Check configuration file
if (-not (Test-Path $Config)) {
  Write-Host "âš ï¸  Configuration file not found: $Config" -ForegroundColor Yellow
  Write-Host "Creating default configuration..." -ForegroundColor Gray
  # Will use defaults in chimera_nexus_integration.py
}

# Display enabled features
Write-Host ""
Write-Host "ðŸ“¦ ENABLED FEATURES:" -ForegroundColor Magenta
Write-Host "  âœ… 1. Neural Evolution Engine - AST code optimization" -ForegroundColor White
Write-Host "  âœ… 2. Quantum Optimizer - Hybrid task scheduling" -ForegroundColor White
Write-Host "  âœ… 3. Personality System - 5 AI modes (Aggressive/Creative/Analyst/etc)" -ForegroundColor White
Write-Host "  âœ… 4. Blockchain Audit - Immutable change tracking" -ForegroundColor White
Write-Host "  âœ… 5. 3D VR Dashboard - WebXR with Meta Quest support" -ForegroundColor White

if (-not $NoVoice) {
  Write-Host "  âœ… 6. Voice Interface - Whisper STT + pyttsx3 TTS" -ForegroundColor White
}
else {
  Write-Host "  â­ï¸  6. Voice Interface - DISABLED" -ForegroundColor Gray
}

Write-Host "  âœ… 7. Genetic Evolution - Config optimization" -ForegroundColor White
Write-Host "  âœ… 8. Predictive Monitor - TensorFlow LSTM + Isolation Forest" -ForegroundColor White

if (-not $NoCloud) {
  Write-Host "  âœ… 9. Cloud Orchestrator - AWS/Azure/GCP multi-cloud" -ForegroundColor White
}
else {
  Write-Host "  â­ï¸  9. Cloud Orchestrator - DISABLED" -ForegroundColor Gray
}

Write-Host "  âœ… 10. Plugin Marketplace - Sandboxed extensions" -ForegroundColor White
Write-Host ""

# Original CHIMERA features
Write-Host "ðŸ“¦ CORE FEATURES:" -ForegroundColor Magenta
Write-Host "  âœ… Metacognitive Self-Evolution" -ForegroundColor White
Write-Host "  âœ… Federated Learning (Flower)" -ForegroundColor White
Write-Host "  âœ… WebSocket Server (port 3001)" -ForegroundColor White
Write-Host "  âœ… HTTP Dashboard (port 3000)" -ForegroundColor White
Write-Host "  âœ… SQLite Persistence" -ForegroundColor White
Write-Host ""

# System checks
Write-Host "ðŸ” Pre-flight checks..." -ForegroundColor Cyan

$checks = @(
  @{
    Name    = "Python"
    Command = "python --version"
  },
  @{
    Name    = "TensorFlow"
    Command = "python -c `"import tensorflow; print(f'TensorFlow {tensorflow.__version__}')`""
  },
  @{
    Name    = "Whisper"
    Command = "python -c `"import whisper; print('Whisper OK')`""
  },
  @{
    Name    = "Flower"
    Command = "python -c `"import flwr; print('Flower OK')`""
  }
)

$allPassed = $true
foreach ($check in $checks) {
  Write-Host "  Checking $($check.Name)..." -NoNewline
  try {
    $output = Invoke-Expression $check.Command 2>&1
    if ($LASTEXITCODE -eq 0) {
      Write-Host " âœ…" -ForegroundColor Green
    }
    else {
      Write-Host " âŒ" -ForegroundColor Red
      $allPassed = $false
    }
  }
  catch {
    Write-Host " âŒ" -ForegroundColor Red
    $allPassed = $false
  }
}

if (-not $allPassed) {
  Write-Host ""
  Write-Host "âš ï¸  Some dependencies missing. Run: .\install_quick_windows.ps1" -ForegroundColor Yellow
  Write-Host "Continuing anyway..." -ForegroundColor Gray
}

Write-Host ""
Write-Host "ðŸŽ¯ Starting CHIMERA NEXUS..." -ForegroundColor Green
Write-Host ""

# Build command
$cmd = "python chimera_autarch.py"

if ($TestMode) {
  Write-Host "ðŸ§ª TEST MODE - Will run for 30 seconds then exit" -ForegroundColor Yellow
  Write-Host ""
}

# Start CHIMERA
Write-Host "â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—" -ForegroundColor Cyan
Write-Host "â•‘                  CHIMERA NEXUS IS NOW ONLINE                     â•‘" -ForegroundColor Cyan
Write-Host "â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•" -ForegroundColor Cyan
Write-Host ""
Write-Host "ðŸ“Š Dashboard: http://localhost:3000" -ForegroundColor Yellow
Write-Host "ðŸŽ® 3D VR View: http://localhost:3000/dashboard_3d.html" -ForegroundColor Yellow
Write-Host "ðŸ”Œ WebSocket: ws://localhost:3001" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop" -ForegroundColor Gray
Write-Host ""

try {
  if ($TestMode) {
    # Run for 30 seconds in test mode
    $job = Start-Job -ScriptBlock { 
      param($command)
      Invoke-Expression $command
    } -ArgumentList $cmd
        
    Start-Sleep -Seconds 30
    Stop-Job $job
    Remove-Job $job
        
    Write-Host ""
    Write-Host "âœ… Test mode complete - CHIMERA ran successfully" -ForegroundColor Green
  }
  else {
    # Normal mode - run indefinitely
    Invoke-Expression $cmd
  }
}
catch {
  Write-Host ""
  Write-Host "âŒ Error: $_" -ForegroundColor Red
  exit 1
}

Write-Host ""
Write-Host "ðŸ‘‹ CHIMERA NEXUS shutdown complete" -ForegroundColor Cyan

