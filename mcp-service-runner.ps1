# MCP Server Service Runner
# This script runs the MCP servers as a Windows service

param(
    [switch]$Debug
)

# Service configuration
$servers = @(
    @{
        Name = "filesystem-server"
        Command = "npx"
        Args = @("-y", "@modelcontextprotocol/server-filesystem", "C:\Drox_AI")
        Port = 3001
    },
    @{
        Name = "code-runner-server"
        Command = "npx"
        Args = @("-y", "mcp-server-code-runner")
        Port = 3002
    },
    @{
        Name = "chrome-devtools-server"
        Command = "npx"
        Args = @("-y", "chrome-devtools-mcp")
        Port = 3003
    }
)

# Logging function
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"

    if ($Debug) {
        Write-Host $logMessage -ForegroundColor $(if ($Level -eq "ERROR") { "Red" } elseif ($Level -eq "WARN") { "Yellow" } else { "White" })
    }

    # Log to file
    $logPath = Join-Path $PSScriptRoot "mcp-service.log"
    Add-Content -Path $logPath -Value $logMessage
}

# Function to start a server process
function Start-ServerProcess {
    param($server)

    Write-Log "Starting $($server.Name) on port $($server.Port)"

    try {
        # Set environment variables
        $env:NODE_ENV = "production"
        $env:MCP_SERVER_PORT = $server.Port
        $env:PATH = "$env:PATH;$env:APPDATA\npm"

        # Start the process
        $process = Start-Process -FilePath $server.Command `
                                -ArgumentList $server.Args `
                                -NoNewWindow `
                                -PassThru `
                                -RedirectStandardOutput (Join-Path $PSScriptRoot "$($server.Name)_out.log") `
                                -RedirectStandardError (Join-Path $PSScriptRoot "$($server.Name)_error.log")

        Write-Log "Started $($server.Name) with PID: $($process.Id)"
        return $process
    } catch {
        Write-Log "Failed to start $($server.Name): $_" "ERROR"
        return $null
    }
}

# Function to monitor and restart servers
function Monitor-Servers {
    param($serverProcesses)

    while ($true) {
        foreach ($server in $servers) {
            $process = $serverProcesses[$server.Name]

            if ($null -eq $process -or $process.HasExited) {
                Write-Log "$($server.Name) is not running, restarting..." "WARN"
                $newProcess = Start-ServerProcess $server
                if ($newProcess) {
                    $serverProcesses[$server.Name] = $newProcess
                }
            }
        }

        # Check every 30 seconds
        Start-Sleep -Seconds 30
    }
}

# Main service logic
function Start-MCPService {
    Write-Log "Starting MCP Server Service"

    # Ensure npm is available
    try {
        $npmVersion = & npm --version 2>$null
        Write-Log "npm version: $npmVersion"
    } catch {
        Write-Log "npm not found in PATH. Please ensure Node.js is installed." "ERROR"
        exit 1
    }

    # Start all servers
    $serverProcesses = @{}

    foreach ($server in $servers) {
        $process = Start-ServerProcess $server
        if ($process) {
            $serverProcesses[$server.Name] = $process
        }
        Start-Sleep -Seconds 5  # Stagger startup
    }

    Write-Log "All MCP servers started. Beginning monitoring..."

    # Monitor and restart servers as needed
    Monitor-Servers $serverProcesses
}

# Handle service stop signals
$global:ServiceRunning = $true

$handler = {
    Write-Log "Received stop signal, shutting down servers..."
    $global:ServiceRunning = $false

    # Stop all server processes
    Get-Process | Where-Object { $_.Name -like "*node*" -or $_.Name -like "*npx*" } | Stop-Process -Force -ErrorAction SilentlyContinue

    Write-Log "MCP Server Service stopped"
}

# Register the handler for common stop signals
Register-EngineEvent -SourceIdentifier PowerShell.Exiting -Action $handler

# Start the service
try {
    if ($Debug) {
        Write-Host "Running in debug mode..." -ForegroundColor Yellow
    }

    Start-MCPService
} catch {
    Write-Log "Service error: $_" "ERROR"
} finally {
    Write-Log "Service shutting down"
}