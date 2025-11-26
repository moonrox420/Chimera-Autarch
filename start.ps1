# Find where your project is
cd ~
Get-ChildItem -Recurse -Filter "chimera_autarch.py" -ErrorAction SilentlyContinue | Select-Object -First 1

# Then cd to that directory and run:
.\start.bat

#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Start CHIMERA AUTARCH system with proper environment setup

.DESCRIPTION
    This script activates the virtual environment, checks dependencies,
    and starts the CHIMERA AUTARCH orchestration system.

.PARAMETER Config
    Path to configuration file (default: config.yaml)

.PARAMETER LogLevel
    Override logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

.PARAMETER NoBrowser
    Don't automatically open the dashboard in browser

.EXAMPLE
    .\start.ps1
    Start with default configuration

.EXAMPLE
    .\start.ps1 -LogLevel DEBUG
    Start with debug logging

.EXAMPLE
    .\start.ps1 -Config custom-config.yaml -NoBrowser
    Start with custom config without opening browser
#>

param(
  [string]$Config = "config.yaml",
  [ValidateSet("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")]
  [string]$LogLevel,
  [switch]$NoBrowser
)

# Set error action preference
$ErrorActionPreference = "Stop"

# Script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host "🧠 CHIMERA AUTARCH Startup Script" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
$VenvPath = Join-Path $ScriptDir "droxai-env"
$VenvActivate = Join-Path $VenvPath "Scripts\Activate.ps1"

if (-not (Test-Path $VenvActivate)) {
  Write-Host "❌ Virtual environment not found at: $VenvPath" -ForegroundColor Red
  Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    
  python -m venv $VenvPath
    
  if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
    exit 1
  }
    
  Write-Host "✅ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow
& $VenvActivate

if ($LASTEXITCODE -ne 0) {
  Write-Host "❌ Failed to activate virtual environment" -ForegroundColor Red
  exit 1
}

Write-Host "✅ Virtual environment activated" -ForegroundColor Green

# Check if requirements.txt exists and install dependencies
$RequirementsFile = Join-Path $ScriptDir "requirements.txt"
if (Test-Path $RequirementsFile) {
  Write-Host "📦 Checking dependencies..." -ForegroundColor Yellow
    
  # Check if dependencies are installed
  $PipList = pip list --format=freeze 2>$null
  $RequiredPackages = Get-Content $RequirementsFile | Where-Object { $_ -notmatch '^\s*#' -and $_ -notmatch '^\s*$' }
    
  $MissingPackages = @()
  foreach ($Package in $RequiredPackages) {
    $PackageName = ($Package -split '[><=!]')[0].Trim()
    if ($PipList -notmatch "^$PackageName==") {
      $MissingPackages += $Package
    }
  }
    
  if ($MissingPackages.Count -gt 0) {
    Write-Host "📥 Installing missing dependencies..." -ForegroundColor Yellow
    pip install -r $RequirementsFile --quiet
        
    if ($LASTEXITCODE -ne 0) {
      Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
      exit 1
    }
        
    Write-Host "✅ Dependencies installed" -ForegroundColor Green
  }
  else {
    Write-Host "✅ All dependencies satisfied" -ForegroundColor Green
  }
}

# Check Ollama and Qwen model
Write-Host "🤖 Checking Ollama and LLM..." -ForegroundColor Yellow
$OllamaCheck = Get-Command ollama -ErrorAction SilentlyContinue
if ($OllamaCheck) {
  try {
    $OllamaModels = ollama list 2>&1 | Out-String
    if ($OllamaModels -match "qwen2.5-coder-14b-instruct-abliterated") {
      Write-Host "✅ Qwen 2.5 Coder ready (GPU-accelerated)" -ForegroundColor Green
    }
    else {
      Write-Host "⚠️  Qwen model not found - code generation will be limited" -ForegroundColor Yellow
      Write-Host "   Install: ollama pull dagbs/qwen2.5-coder-14b-instruct-abliterated:q5_k_m" -ForegroundColor Gray
    }
  }
  catch {
    Write-Host "⚠️  Ollama not running - starting..." -ForegroundColor Yellow
    Start-Process -NoNewWindow ollama -ArgumentList "serve"
    Start-Sleep -Seconds 2
  }
}
else {
  Write-Host "⚠️  Ollama not installed - AI code generation disabled" -ForegroundColor Yellow
  Write-Host "   Install from: https://ollama.com" -ForegroundColor Gray
}

# Set environment variables if specified
if ($LogLevel) {
  $env:CHIMERA_LOGGING_LEVEL = $LogLevel
  Write-Host "🔧 Log level set to: $LogLevel" -ForegroundColor Yellow
}

if ($Config -ne "config.yaml" -and (Test-Path $Config)) {
  $env:CHIMERA_CONFIG_FILE = $Config
  Write-Host "🔧 Using config file: $Config" -ForegroundColor Yellow
}

# Check if chimera_autarch.py exists
$MainScript = Join-Path $ScriptDir "chimera_autarch.py"
if (-not (Test-Path $MainScript)) {
  Write-Host "❌ Main script not found: $MainScript" -ForegroundColor Red
  exit 1
}

# Start the system
Write-Host ""
Write-Host "🚀 Starting CHIMERA AUTARCH..." -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📊 Dashboard: http://localhost:8000" -ForegroundColor Cyan
Write-Host "🔌 WebSocket: ws://localhost:8765" -ForegroundColor Cyan
Write-Host "📈 Metrics API: http://localhost:8000/metrics" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the system" -ForegroundColor Yellow
Write-Host ""

# Open browser if not disabled
if (-not $NoBrowser) {
  Start-Sleep -Seconds 2
  Start-Process "http://localhost:8000"
}

# Start CHIMERA
try {
  python $MainScript
}
catch {
  Write-Host ""
  Write-Host "❌ Error starting CHIMERA: $_" -ForegroundColor Red
  exit 1
}
finally {
  Write-Host ""
  Write-Host "👋 CHIMERA AUTARCH stopped" -ForegroundColor Yellow
}
