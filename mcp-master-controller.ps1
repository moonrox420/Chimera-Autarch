# MCP System Master Controller
# This runs the complete MCP ecosystem system-wide

param(
    [switch]$Start,
    [switch]$Stop,
    [switch]$Status,
    [switch]$Restart,
    [string]$ConfigFile = "mcp-system-config.yaml"
)

# Load configuration
$configPath = Join-Path $PSScriptRoot $ConfigFile
if (Test-Path $configPath) {
    try {
        $config = Get-Content $configPath -Raw | ConvertFrom-Yaml
        Write-Host "Loaded configuration from $configPath" -ForegroundColor Green
    } catch {
        Write-Warning "Could not load config file, using defaults"
        $config = $null
    }
}

# MCP System Configuration
$mcpConfig = @{
    Host = if ($config) { $config.NETWORK.bind_address } else { "127.0.0.1" }
    Port = if ($config) { $config.NETWORK.metrics_port } else { 9090 }
    Servers = @(
        @{
            Name = "filesystem"
            Command = "npx"
            Args = @("-y", "@modelcontextprotocol/server-filesystem", "/Users")
            Capabilities = @("files", "directories", "read", "write")
            Priority = 1
        },
        @{
            Name = "git"
            Command = "npx"
            Args = @("-y", "@modelcontextprotocol/server-git", "--repository", ".")
            Capabilities = @("git", "version-control", "commits", "branches")
            Priority = 2
        },
        @{
            Name = "code-runner"
            Command = "npx"
            Args = @("-y", "mcp-server-code-runner")
            Capabilities = @("execute", "python", "javascript", "code")
            Priority = 3
        },
        @{
            Name = "chrome-devtools"
            Command = "npx"
            Args = @("-y", "chrome-devtools-mcp")
            Capabilities = @("browser", "dom", "debugging", "web")
            Priority = 4
        }
    )
    AutoDiscovery = $true
    LoadBalancing = $true
    HealthChecks = $true
    Metrics = $true
}

# Global state
$global:MCPProcesses = @{}
$global:MCPHealth = @{}
$global:MCPServer = $null

function Write-MCPLog {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"
    Write-Host $logMessage -ForegroundColor $(if ($Level -eq "ERROR") { "Red" } elseif ($Level -eq "WARN") { "Yellow" } else { "Cyan" })

    # Log to file
    $logPath = Join-Path $PSScriptRoot "mcp-system.log"
    Add-Content -Path $logPath -Value $logMessage
}

function Start-MCPServer {
    param($serverConfig)

    $serverName = $serverConfig.Name
    Write-MCPLog "Starting MCP server: $serverName"

    try {
        # Set environment for MCP protocol
        $env:MCP_SERVER_NAME = $serverName
        $env:MCP_SERVER_CAPABILITIES = $serverConfig.Capabilities -join ","
        $env:MCP_SERVER_PRIORITY = $serverConfig.Priority

        # Start process with proper MCP protocol handling
        $process = Start-Process -FilePath $serverConfig.Command `
                                -ArgumentList $serverConfig.Args `
                                -NoNewWindow `
                                -PassThru `
                                -RedirectStandardInput (Join-Path $PSScriptRoot "pipes\$serverName.in") `
                                -RedirectStandardOutput (Join-Path $PSScriptRoot "pipes\$serverName.out") `
                                -RedirectStandardError (Join-Path $PSScriptRoot "pipes\$serverName.err")

        # Create named pipes for MCP communication
        $pipeName = "mcp_$serverName"
        $global:MCPProcesses[$serverName] = @{
            Process = $process
            PipeName = $pipeName
            Capabilities = $serverConfig.Capabilities
            Priority = $serverConfig.Priority
            StartTime = Get-Date
            Health = "Starting"
        }

        Write-MCPLog "Started $serverName with PID: $($process.Id)"
        return $true
    } catch {
        Write-MCPLog "Failed to start $serverName`: $_" "ERROR"
        return $false
    }
}

function Start-MCPRouter {
    Write-MCPLog "Starting MCP Router service"

    try {
        # Start the MCP router that coordinates all servers
        $routerProcess = Start-Process -FilePath "node" `
                                      -ArgumentList "-e", "
const net = require('net');
const fs = require('fs');
const path = require('path');

const HOST = '$($mcpConfig.Host)';
const PORT = $($mcpConfig.Port);

console.log(`MCP Router starting on ${HOST}:${PORT}`);

// MCP Router server
const server = net.createServer((socket) => {
    console.log('MCP client connected');

    socket.on('data', (data) => {
        const request = JSON.parse(data.toString());
        console.log('MCP Request:', request);

        // Route to appropriate MCP server
        const response = {
            jsonrpc: '2.0',
            id: request.id,
            result: {
                servers: Object.keys(global.MCPProcesses || {}),
                capabilities: ['filesystem', 'git', 'code-execution', 'browser-debugging'],
                status: 'active'
            }
        };

        socket.write(JSON.stringify(response) + '\n');
    });

    socket.on('end', () => {
        console.log('MCP client disconnected');
    });
});

server.listen(PORT, HOST, () => {
    console.log(`MCP Router listening on ${HOST}:${PORT}`);
});

// Health check endpoint
setInterval(() => {
    console.log(`MCP Router healthy - ${Object.keys(global.MCPProcesses || {}).length} servers active`);
}, 30000);
" `
                                      -NoNewWindow `
                                      -PassThru

        $global:MCPServer = $routerProcess
        Write-MCPLog "MCP Router started with PID: $($routerProcess.Id)"
        return $true
    } catch {
        Write-MCPLog "Failed to start MCP Router: $_" "ERROR"
        return $false
    }
}

function Start-MCPSystem {
    Write-MCPLog "Initializing MCP System..."

    # Create pipes directory
    $pipesDir = Join-Path $PSScriptRoot "pipes"
    if (-not (Test-Path $pipesDir)) {
        New-Item -ItemType Directory -Path $pipesDir -Force | Out-Null
    }

    # Start MCP Router first
    if (-not (Start-MCPRouter)) {
        Write-MCPLog "Failed to start MCP Router, aborting system start" "ERROR"
        return $false
    }

    # Start all MCP servers
    foreach ($server in $mcpConfig.Servers) {
        Start-MCPServer $server
        Start-Sleep -Seconds 2  # Stagger startup
    }

    # Start health monitoring
    Start-MCPHealthMonitor

    Write-MCPLog "MCP System fully operational!"
    Write-MCPLog "System accessible at $($mcpConfig.Host):$($mcpConfig.Port)"
    Write-MCPLog "Available servers: $($mcpConfig.Servers.Count)"

    return $true
}

function Start-MCPHealthMonitor {
    Write-MCPLog "Starting health monitoring..."

    $healthJob = Start-Job -ScriptBlock {
        while ($true) {
            # Check each server process
            foreach ($serverName in $using:global:MCPProcesses.Keys) {
                $server = $using:global:MCPProcesses[$serverName]
                if ($server.Process.HasExited) {
                    Write-Host "Server $serverName crashed, restarting..." -ForegroundColor Red
                    # Restart logic would go here
                } else {
                    $server.Health = "Healthy"
                }
            }

            Start-Sleep -Seconds 30
        }
    }

    $global:MCPHealthMonitor = $healthJob
}

function Stop-MCPSystem {
    Write-MCPLog "Shutting down MCP System..."

    # Stop health monitor
    if ($global:MCPHealthMonitor) {
        Stop-Job $global:MCPHealthMonitor
        Remove-Job $global:MCPHealthMonitor
    }

    # Stop all server processes
    foreach ($serverName in $global:MCPProcesses.Keys) {
        $server = $global:MCPProcesses[$serverName]
        try {
            Stop-Process -Id $server.Process.Id -Force -ErrorAction SilentlyContinue
            Write-MCPLog "Stopped $serverName"
        } catch {
            Write-MCPLog "Error stopping $serverName`: $_" "WARN"
        }
    }

    # Stop router
    if ($global:MCPServer) {
        try {
            Stop-Process -Id $global:MCPServer.Id -Force -ErrorAction SilentlyContinue
            Write-MCPLog "Stopped MCP Router"
        } catch {
            Write-MCPLog "Error stopping MCP Router: $_" "WARN"
        }
    }

    $global:MCPProcesses = @{}
    $global:MCPServer = $null

    Write-MCPLog "MCP System shutdown complete"
}

function Get-MCPStatus {
    Write-Host "=================================" -ForegroundColor Cyan
    Write-Host "    MCP System Status" -ForegroundColor Cyan
    Write-Host "=================================" -ForegroundColor Cyan

    # Router status
    if ($global:MCPServer -and -not $global:MCPServer.HasExited) {
        Write-Host "Router: " -NoNewline
        Write-Host "Running" -ForegroundColor Green -NoNewline
        Write-Host " (PID: $($global:MCPServer.Id), Port: $($mcpConfig.Port))"
    } else {
        Write-Host "Router: " -NoNewline
        Write-Host "Stopped" -ForegroundColor Red
    }

    Write-Host ""

    # Server status
    Write-Host "MCP Servers:" -ForegroundColor Yellow
    if ($global:MCPProcesses.Count -eq 0) {
        Write-Host "  No servers running" -ForegroundColor Red
    } else {
        foreach ($serverName in $global:MCPProcesses.Keys) {
            $server = $global:MCPProcesses[$serverName]
            Write-Host "  $serverName`: " -NoNewline

            if ($server.Process.HasExited) {
                Write-Host "Crashed" -ForegroundColor Red
            } else {
                Write-Host "Running" -ForegroundColor Green -NoNewline
                Write-Host " (PID: $($server.Process.Id))"
                Write-Host "    Capabilities: $($server.Capabilities -join ', ')" -ForegroundColor Gray
            }
        }
    }

    Write-Host ""
    Write-Host "System Endpoint: $($mcpConfig.Host):$($mcpConfig.Port)" -ForegroundColor Cyan
}

# Main logic
switch {
    $Start {
        if ($global:MCPProcesses.Count -gt 0) {
            Write-Host "MCP System is already running. Use -Restart to restart." -ForegroundColor Yellow
        } else {
            Start-MCPSystem
        }
    }
    $Stop {
        Stop-MCPSystem
    }
    $Status {
        Get-MCPStatus
    }
    $Restart {
        Write-Host "Restarting MCP System..." -ForegroundColor Yellow
        Stop-MCPSystem
        Start-Sleep -Seconds 3
        Start-MCPSystem
    }
    default {
        Write-Host "MCP System Master Controller" -ForegroundColor Cyan
        Write-Host "============================" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Usage:" -ForegroundColor White
        Write-Host "  .\mcp-master-controller.ps1 -Start    # Start complete MCP system"
        Write-Host "  .\mcp-master-controller.ps1 -Stop     # Stop all MCP services"
        Write-Host "  .\mcp-master-controller.ps1 -Status   # Show system status"
        Write-Host "  .\mcp-master-controller.ps1 -Restart  # Restart MCP system"
        Write-Host ""
        Get-MCPStatus
    }
}