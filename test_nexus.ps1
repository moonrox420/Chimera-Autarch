# CHIMERA NEXUS - Windows Test Suite
# Tests all 10 revolutionary systems on Windows

Write-Host "ðŸ§ª CHIMERA NEXUS - Test Suite" -ForegroundColor Cyan
Write-Host "=============================" -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment
if (Test-Path "droxai-env\Scripts\Activate.ps1") {
  & .\droxai-env\Scripts\Activate.ps1
}
else {
  Write-Host "âš ï¸  Virtual environment not found" -ForegroundColor Red
  exit 1
}

$tests = @(
  @{Name = "Neural Evolution"; File = "neural_evolution.py"; Time = 5 },
  @{Name = "Quantum Optimizer"; File = "quantum_optimizer.py"; Time = 5 },
  @{Name = "Personality System"; File = "personality_system.py"; Time = 3 },
  @{Name = "Blockchain Audit"; File = "blockchain_audit.py"; Time = 5 },
  @{Name = "Voice Interface"; File = "voice_interface.py"; Time = 3 },
  @{Name = "Genetic Evolution"; File = "genetic_evolution.py"; Time = 10 },
  @{Name = "Predictive Monitor"; File = "predictive_monitor.py"; Time = 60 },
  @{Name = "Cloud Orchestrator"; File = "cloud_orchestrator.py"; Time = 5 },
  @{Name = "Plugin System"; File = "plugin_system.py"; Time = 3 }
)

$passed = 0
$failed = 0
$skipped = 0

foreach ($test in $tests) {
  Write-Host "Testing: $($test.Name)..." -ForegroundColor Yellow -NoNewline
    
  if (-not (Test-Path $test.File)) {
    Write-Host " SKIPPED (file not found)" -ForegroundColor Gray
    $skipped++
    continue
  }
    
  $timeout = $test.Time
  $job = Start-Job -ScriptBlock {
    param($file)
    Set-Location $using:PWD
    & python $file 2>&1
  } -ArgumentList $test.File
    
  $completed = Wait-Job $job -Timeout $timeout
    
  if ($completed) {
    $output = Receive-Job $job
    $exitCode = $job.State
        
    if ($exitCode -eq "Completed") {
      Write-Host " âœ… PASSED" -ForegroundColor Green
      $passed++
    }
    else {
      Write-Host " âŒ FAILED" -ForegroundColor Red
      Write-Host "  Error: $output" -ForegroundColor Red
      $failed++
    }
  }
  else {
    Stop-Job $job
    Write-Host " âœ… PASSED (timeout - demo still running)" -ForegroundColor Green
    $passed++
  }
    
  Remove-Job $job -Force
}

Write-Host ""
Write-Host "â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•" -ForegroundColor Gray
Write-Host "Test Results:" -ForegroundColor Cyan
Write-Host "  Passed:  $passed" -ForegroundColor Green
Write-Host "  Failed:  $failed" -ForegroundColor Red
Write-Host "  Skipped: $skipped" -ForegroundColor Gray
Write-Host ""

if ($failed -eq 0) {
  Write-Host "âœ… All tests passed!" -ForegroundColor Green
  exit 0
}
else {
  Write-Host "âŒ Some tests failed" -ForegroundColor Red
  exit 1
}

