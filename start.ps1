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

#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Start CHIMERA AUTARCH system with the new unified architecture

.DESCRIPTION
    This script activates the virtual environment and starts the
    CHIMERA AUTARCH system using the new modular architecture.

.PARAMETER Mode
    Run mode: server (default), client, or cli

.PARAMETER Config
    Path to configuration file (default: config.yaml)

.PARAMETER LogLevel
    Override logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

.EXAMPLE
    .\start.ps1
    Start the server with default configuration

.EXAMPLE
    .\start.ps1 -Mode client
    Start the WebSocket client

.EXAMPLE
    .\start.ps1 -LogLevel DEBUG
    Start with debug logging
#>

param(
  [ValidateSet("server", "client", "cli")]
  [string]$Mode = "server",
  [string]$Config = "config.yaml",
  [ValidateSet("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")]
  [string]$LogLevel
)

# Set error action preference
$ErrorActionPreference = "Stop"

# Script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host "🧠 CHIMERA AUTARCH v3.0" -ForegroundColor Cyan
Write-Host "========================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
$venvPath = ".\.venv\Scripts\Activate.ps1"
if (-not (Test-Path $venvPath)) {
  Write-Host "❌ Virtual environment not found at $venvPath" -ForegroundColor Red
  Write-Host "Please run setup script first." -ForegroundColor Yellow
  exit 1
}

# Activate virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow
& $venvPath

# Check Python
try {
  $pythonVersion = python --version 2>&1
  Write-Host "🐍 $pythonVersion" -ForegroundColor Green
}
catch {
  Write-Host "❌ Python not found in PATH" -ForegroundColor Red
  exit 1
}

# Check if src directory exists
if (-not (Test-Path "src")) {
  Write-Host "❌ Source directory 'src' not found" -ForegroundColor Red
  Write-Host "Please ensure you're in the correct directory." -ForegroundColor Yellow
  exit 1
}

# Build command arguments
$args = @("-m", "src.main", $Mode, "--config", $Config)
if ($LogLevel) {
  $args += @("--log-level", $LogLevel)
}

Write-Host "🚀 Starting CHIMERA AUTARCH in $Mode mode..." -ForegroundColor Green
Write-Host "Command: python $($args -join ' ')" -ForegroundColor Gray
Write-Host ""

try {
  # Start the application
  & python $args
}
catch {
  Write-Host "❌ Failed to start CHIMERA AUTARCH: $($_.Exception.Message)" -ForegroundColor Red
  exit 1
}