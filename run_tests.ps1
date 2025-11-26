#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Run CHIMERA AUTARCH test suite

.DESCRIPTION
    Runs unit tests with coverage reporting

.PARAMETER Coverage
    Generate coverage report

.PARAMETER Verbose
    Show verbose test output

.EXAMPLE
    .\run_tests.ps1
    Run tests without coverage

.EXAMPLE
    .\run_tests.ps1 -Coverage
    Run tests with coverage report
#>

param(
  [switch]$Coverage,
  [switch]$Verbose
)

$ErrorActionPreference = "Stop"

Write-Host "🧪 CHIMERA AUTARCH Test Suite" -ForegroundColor Cyan
Write-Host "=============================" -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment
$VenvActivate = ".\droxai-env\Scripts\Activate.ps1"
if (Test-Path $VenvActivate) {
  & $VenvActivate
  Write-Host "✅ Virtual environment activated" -ForegroundColor Green
}
else {
  Write-Host "❌ Virtual environment not found" -ForegroundColor Red
  exit 1
}

# Install test dependencies if needed
$TestPackages = @("pytest", "pytest-asyncio", "pytest-cov")
$MissingPackages = @()

foreach ($Package in $TestPackages) {
  $Installed = pip show $Package 2>$null
  if (-not $Installed) {
    $MissingPackages += $Package
  }
}

if ($MissingPackages.Count -gt 0) {
  Write-Host "📦 Installing test dependencies..." -ForegroundColor Yellow
  pip install $MissingPackages --quiet
  Write-Host "✅ Test dependencies installed" -ForegroundColor Green
}

Write-Host ""

# Build test command
$TestArgs = @("tests/")

if ($Verbose) {
  $TestArgs += "-v"
}

if ($Coverage) {
  $TestArgs += "--cov=."
  $TestArgs += "--cov-report=term-missing"
  $TestArgs += "--cov-report=html"
}

# Run tests
Write-Host "🚀 Running tests..." -ForegroundColor Green
Write-Host ""

$argsList = @('-m', 'pytest') + $TestArgs
$proc = Start-Process -FilePath (Get-Command python).Source -ArgumentList $argsList -NoNewWindow -Wait -PassThru
$exitCode = $proc.ExitCode
if ($exitCode -eq 0) {
  Write-Host ""
  Write-Host "✅ All tests passed!" -ForegroundColor Green
  if ($Coverage) {
    Write-Host ""
    Write-Host "📊 Coverage report generated in htmlcov/" -ForegroundColor Cyan
  }
}
else {
  Write-Host ""
  Write-Host "❌ Some tests failed" -ForegroundColor Red
  exit 1
}
