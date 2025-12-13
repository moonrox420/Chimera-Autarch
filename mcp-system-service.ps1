# MCP System Service
# Windows service that manages the complete MCP ecosystem

param(
    [switch]$Install,
    [switch]$Uninstall,
    [switch]$Start,
    [switch]$Stop,
    [switch]$Test
)

$serviceName = "MCP-System"
$displayName = "MCP System Service"
$description = "Complete Model Context Protocol ecosystem for system-wide AI assistance"

$scriptPath = Join-Path $PSScriptRoot "mcp-system-service.ps1"

function Install-MCPService {
    Write-Host "Installing MCP System Service..." -ForegroundColor Cyan

    # Create the service
    $params = @{
        Name = $serviceName
        BinaryPathName = "powershell.exe -ExecutionPolicy Bypass -File `"$scriptPath`""
        DisplayName = $displayName
        Description = $description
        StartupType = "Automatic"
        Credential = "LocalSystem"
    }

    try {
        New-Service @params
        Write-Host "✓ MCP System Service installed successfully" -ForegroundColor Green

        # Configure service recovery
        sc.exe failure $serviceName reset= 86400 actions= restart/5000/restart/10000/restart/60000

        # Set service description
        sc.exe description $serviceName $description

        Write-Host "✓ Service configured with automatic restart on failure" -ForegroundColor Green
        Write-Host ""
        Write-Host "To start the service manually:" -ForegroundColor Yellow
        Write-Host "  Start-Service -Name '$serviceName'"
        Write-Host ""
        Write-Host "The service will start automatically on system boot" -ForegroundColor Yellow

    } catch {
        Write-Error "Failed to install service: $_"
    }
}

function Uninstall-MCPService {
    Write-Host "Uninstalling MCP System Service..." -ForegroundColor Yellow

    try {
        # Stop service if running
        Stop-Service -Name $serviceName -ErrorAction SilentlyContinue

        # Remove service
        sc.exe delete $serviceName

        Write-Host "✓ MCP System Service uninstalled successfully" -ForegroundColor Green
    } catch {
        Write-Error "Failed to uninstall service: $_"
    }
}

function Start-MCPService {
    Write-Host "Starting MCP System Service..." -ForegroundColor Green
    try {
        Start-Service -Name $serviceName
        Write-Host "✓ Service started successfully" -ForegroundColor Green
        Start-Sleep -Seconds 5
        Get-MCPServiceStatus
    } catch {
        Write-Error "Failed to start service: $_"
    }
}

function Stop-MCPService {
    Write-Host "Stopping MCP System Service..." -ForegroundColor Yellow
    try {
        Stop-Service -Name $serviceName
        Write-Host "✓ Service stopped successfully" -ForegroundColor Green
    } catch {
        Write-Error "Failed to stop service: $_"
    }
}

function Get-MCPServiceStatus {
    Write-Host "MCP System Service Status:" -ForegroundColor Cyan
    Write-Host "==========================" -ForegroundColor Cyan

    try {
        $service = Get-Service -Name $serviceName -ErrorAction Stop
        Write-Host "Service Name: $($service.Name)" -ForegroundColor White
        Write-Host "Display Name: $($service.DisplayName)" -ForegroundColor White
        Write-Host "Status: $($service.Status)" -ForegroundColor $(if ($service.Status -eq "Running") { "Green" } else { "Red" })
        Write-Host "Startup Type: $($service.StartupType)" -ForegroundColor White

        # Check if MCP system is actually responding
        try {
            $mcpClient = & (Join-Path $PSScriptRoot "MCPClient.psm1")
            Import-Module (Join-Path $PSScriptRoot "MCPClient.psm1") -Force
            $client = New-MCPClient
            if ($client.Connect()) {
                Write-Host "MCP System: Responding" -ForegroundColor Green
                $client.Disconnect()
            } else {
                Write-Host "MCP System: Not responding" -ForegroundColor Red
            }
        } catch {
            Write-Host "MCP System: Unable to check" -ForegroundColor Yellow
        }

    } catch {
        Write-Host "Service '$serviceName' is not installed" -ForegroundColor Red
    }
}

function Test-MCPSystem {
    Write-Host "Testing MCP System..." -ForegroundColor Cyan

    try {
        # Import the client module
        Import-Module (Join-Path $PSScriptRoot "MCPClient.psm1") -Force

        # Create client and connect
        $client = New-MCPClient
        if (-not $client.Connect()) {
            Write-Error "Cannot connect to MCP system"
            return
        }

        Write-Host "✓ Connected to MCP system" -ForegroundColor Green

        # Test system info
        $info = $client.ListServers()
        Write-Host "✓ System info retrieved" -ForegroundColor Green
        Write-Host "  Available servers: $($info.result.servers -join ', ')" -ForegroundColor White

        # Test filesystem operations
        Write-Host "Testing filesystem operations..." -ForegroundColor Yellow
        $listResult = $client.ListDirectory($PSScriptRoot)
        if ($listResult) {
            Write-Host "✓ Filesystem list successful" -ForegroundColor Green
        } else {
            Write-Host "⚠ Filesystem list failed" -ForegroundColor Yellow
        }

        # Test code execution
        Write-Host "Testing code execution..." -ForegroundColor Yellow
        $codeResult = $client.ExecuteCode("print('Hello from MCP!')", "python")
        if ($codeResult) {
            Write-Host "✓ Code execution successful" -ForegroundColor Green
        } else {
            Write-Host "⚠ Code execution failed" -ForegroundColor Yellow
        }

        $client.Disconnect()
        Write-Host "✓ All tests completed" -ForegroundColor Green

    } catch {
        Write-Error "Test failed: $_"
    }
}

# Main logic
switch {
    $Install { Install-MCPService }
    $Uninstall { Uninstall-MCPService }
    $Start { Start-MCPService }
    $Stop { Stop-MCPService }
    $Test { Test-MCPSystem }
    default {
        Write-Host "MCP System Service Manager" -ForegroundColor Cyan
        Write-Host "===========================" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Usage (run as Administrator):" -ForegroundColor White
        Write-Host "  .\mcp-system-service.ps1 -Install   # Install as Windows service"
        Write-Host "  .\mcp-system-service.ps1 -Uninstall # Remove Windows service"
        Write-Host "  .\mcp-system-service.ps1 -Start     # Start the service"
        Write-Host "  .\mcp-system-service.ps1 -Stop      # Stop the service"
        Write-Host "  .\mcp-system-service.ps1 -Test      # Test MCP system functionality"
        Write-Host ""
        Get-MCPServiceStatus
    }
}