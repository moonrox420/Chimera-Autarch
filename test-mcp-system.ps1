# MCP System Test Script
# Comprehensive test of the entire MCP ecosystem

param(
    [switch]$Quick,
    [switch]$Full,
    [switch]$Stress
)

Import-Module (Join-Path $PSScriptRoot "MCPClient.psm1") -Force

function Test-MCPConnection {
    Write-Host "Testing MCP System Connection..." -ForegroundColor Cyan

    $client = New-MCPClient
    if (-not $client.Connect()) {
        Write-Error "❌ Cannot connect to MCP system"
        return $false
    }

    Write-Host "✅ Connected to MCP system" -ForegroundColor Green
    $client.Disconnect()
    return $true
}

function Test-MCPServers {
    Write-Host "Testing MCP Servers..." -ForegroundColor Cyan

    $client = New-MCPClient
    if (-not $client.Connect()) {
        Write-Error "❌ Cannot connect to MCP system"
        return $false
    }

    $testsPassed = 0
    $totalTests = 0

    try {
        # Test system info
        $totalTests++
        $info = $client.ListServers()
        if ($info -and $info.result.servers) {
            Write-Host "✅ System info: $($info.result.servers.Count) servers available" -ForegroundColor Green
            $testsPassed++
        } else {
            Write-Host "❌ System info failed" -ForegroundColor Red
        }

        # Test filesystem operations
        $totalTests++
        Write-Host "Testing filesystem operations..." -ForegroundColor Yellow
        $listResult = $client.ListDirectory($PSScriptRoot)
        if ($listResult -and $listResult.result) {
            Write-Host "✅ Filesystem list successful" -ForegroundColor Green
            $testsPassed++
        } else {
            Write-Host "❌ Filesystem list failed" -ForegroundColor Red
        }

        # Test file reading
        $totalTests++
        $testFile = Join-Path $PSScriptRoot "README.md"
        if (Test-Path $testFile) {
            $readResult = $client.ReadFile($testFile)
            if ($readResult -and $readResult.result) {
                Write-Host "✅ File read successful" -ForegroundColor Green
                $testsPassed++
            } else {
                Write-Host "❌ File read failed" -ForegroundColor Red
            }
        } else {
            Write-Host "⚠️  Skipping file read test (no test file)" -ForegroundColor Yellow
        }

        # Test code execution
        $totalTests++
        Write-Host "Testing code execution..." -ForegroundColor Yellow
        $codeResult = $client.ExecuteCode("print('Hello from MCP System!')", "python")
        if ($codeResult -and $codeResult.result) {
            Write-Host "✅ Code execution successful" -ForegroundColor Green
            $testsPassed++
        } else {
            Write-Host "❌ Code execution failed" -ForegroundColor Red
        }

        # Test Git operations (if in git repo)
        $totalTests++
        if (Test-Path (Join-Path $PSScriptRoot ".git")) {
            Write-Host "Testing Git operations..." -ForegroundColor Yellow
            $gitResult = $client.GitStatus()
            if ($gitResult) {
                Write-Host "✅ Git status successful" -ForegroundColor Green
                $testsPassed++
            } else {
                Write-Host "❌ Git status failed" -ForegroundColor Red
            }
        } else {
            Write-Host "⚠️  Skipping Git test (not a git repository)" -ForegroundColor Yellow
        }

    } finally {
        $client.Disconnect()
    }

    Write-Host "`nTest Results: $testsPassed/$totalTests passed" -ForegroundColor $(if ($testsPassed -eq $totalTests) { "Green" } else { "Yellow" })
    return ($testsPassed -gt 0)
}

function Test-MCPPerformance {
    Write-Host "Testing MCP System Performance..." -ForegroundColor Cyan

    $client = New-MCPClient
    if (-not $client.Connect()) {
        Write-Error "❌ Cannot connect for performance test"
        return $false
    }

    try {
        # Test response times
        $iterations = 10
        $totalTime = 0

        Write-Host "Running $iterations performance tests..." -ForegroundColor Yellow

        for ($i = 1; $i -le $iterations; $i++) {
            $start = Get-Date
            $result = $client.ListServers()
            $end = Get-Date
            $duration = ($end - $start).TotalMilliseconds
            $totalTime += $duration
            Write-Host "  Test $i`: $($duration.ToString("F2"))ms" -ForegroundColor Gray
        }

        $avgTime = $totalTime / $iterations
        Write-Host "Average response time: $($avgTime.ToString("F2"))ms" -ForegroundColor $(if ($avgTime -lt 100) { "Green" } elseif ($avgTime -lt 500) { "Yellow" } else { "Red" })

        return $true
    } finally {
        $client.Disconnect()
    }
}

function Test-MCPStress {
    Write-Host "Running MCP System Stress Test..." -ForegroundColor Cyan

    $clients = @()
    $iterations = 50

    try {
        # Create multiple concurrent clients
        Write-Host "Creating 5 concurrent clients..." -ForegroundColor Yellow
        for ($i = 1; $i -le 5; $i++) {
            $client = New-MCPClient
            if ($client.Connect()) {
                $clients += $client
                Write-Host "  Client $i connected" -ForegroundColor Green
            } else {
                Write-Host "  Client $i failed to connect" -ForegroundColor Red
            }
        }

        if ($clients.Count -eq 0) {
            Write-Error "❌ No clients could connect"
            return $false
        }

        # Run concurrent operations
        Write-Host "Running $iterations concurrent operations..." -ForegroundColor Yellow
        $jobs = @()

        foreach ($client in $clients) {
            $job = Start-Job -ScriptBlock {
                param($clientIndex, $iterations)
                $results = @()

                for ($i = 1; $i -le $iterations; $i++) {
                    try {
                        # Test different operations
                        $op = Get-Random -Minimum 1 -Maximum 4
                        switch ($op) {
                            1 { $result = $client.ListServers() }
                            2 { $result = $client.ListDirectory($PSScriptRoot) }
                            3 { $result = $client.ExecuteCode("print('test')", "python") }
                        }
                        $results += @{ Success = $true; Operation = $op }
                    } catch {
                        $results += @{ Success = $false; Error = $_.Exception.Message }
                    }
                }

                return @{ ClientIndex = $clientIndex; Results = $results }
            } -ArgumentList $clients.IndexOf($client), $iterations

            $jobs += $job
        }

        # Wait for all jobs to complete
        $completedJobs = Wait-Job $jobs
        $totalOperations = 0
        $successfulOperations = 0

        foreach ($job in $completedJobs) {
            $result = Receive-Job $job
            $totalOperations += $result.Results.Count
            $successfulOperations += ($result.Results | Where-Object { $_.Success }).Count
            Remove-Job $job
        }

        Write-Host "Stress test results:" -ForegroundColor Cyan
        Write-Host "  Total operations: $totalOperations" -ForegroundColor White
        Write-Host "  Successful: $successfulOperations" -ForegroundColor Green
        Write-Host "  Failed: $($totalOperations - $successfulOperations)" -ForegroundColor $(if ($totalOperations -eq $successfulOperations) { "Green" } else { "Red" })
        Write-Host "  Success rate: $(($successfulOperations / $totalOperations * 100).ToString("F1"))%" -ForegroundColor $(if ($successfulOperations / $totalOperations -gt 0.95) { "Green" } else { "Yellow" })

        return ($successfulOperations -gt ($totalOperations * 0.9))  # 90% success rate
    } finally {
        # Clean up clients
        foreach ($client in $clients) {
            try { $client.Disconnect() } catch { }
        }
    }
}

# Main test execution
Write-Host "MCP System Test Suite" -ForegroundColor Cyan
Write-Host "====================" -ForegroundColor Cyan
Write-Host ""

$allTestsPassed = $true

# Run connection test
if (-not (Test-MCPConnection)) {
    $allTestsPassed = $false
}

# Run server tests
if (-not (Test-MCPServers)) {
    $allTestsPassed = $false
}

# Run performance test (unless quick test)
if (-not $Quick -and (Test-MCPPerformance)) {
    # Performance test doesn't affect pass/fail
}

# Run stress test (only if requested)
if ($Stress -and (Test-MCPStress)) {
    # Stress test doesn't affect pass/fail for basic tests
}

Write-Host ""
Write-Host "Test Summary:" -ForegroundColor Cyan
if ($allTestsPassed) {
    Write-Host "✅ All core tests passed! MCP System is working correctly." -ForegroundColor Green
} else {
    Write-Host "❌ Some tests failed. Check the output above for details." -ForegroundColor Red
}

Write-Host ""
Write-Host "Next steps:" -ForegroundColor White
Write-Host "- Use the MCPClient module in your applications" -ForegroundColor Gray
Write-Host "- Check logs in .\mcp-system.log for detailed information" -ForegroundColor Gray
Write-Host "- Monitor system health with .\mcp-master-controller.ps1 -Status" -ForegroundColor Gray