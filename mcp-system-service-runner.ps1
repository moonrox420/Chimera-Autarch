# MCP System Service Runner
# This script runs the complete MCP ecosystem as a Windows service

# Service configuration
$serviceConfig = @{
    ServiceName = "MCP-System"
    DisplayName = "MCP System Service"
    Description = "Complete Model Context Protocol ecosystem"
    LogFile = Join-Path $PSScriptRoot "mcp-system-service.log"
    PipeDirectory = Join-Path $PSScriptRoot "pipes"
    Host = "127.0.0.1"
    Port = 9090
}

# Global state
$global:MCPProcesses = @{}
$global:MCPRouter = $null
$global:ServiceRunning = $true
$global:HealthMonitor = $null

# MCP Servers configuration
$mcpServers = @(
    @{
        Name = "filesystem"
        Command = "npx"
        Args = @("-y", "@modelcontextprotocol/server-filesystem", "C:\Drox_AI")
        Capabilities = @("files", "directories", "read", "write", "search")
        Priority = 1
        HealthCheck = $true
    },
    @{
        Name = "git"
        Command = "npx"
        Args = @("-y", "@modelcontextprotocol/server-git", "--repository", "C:\Drox_AI")
        Capabilities = @("git", "version-control", "commits", "branches", "diff")
        Priority = 2
        HealthCheck = $true
    },
    @{
        Name = "code-runner"
        Command = "npx"
        Args = @("-y", "mcp-server-code-runner")
        Capabilities = @("execute", "python", "javascript", "powershell", "code")
        Priority = 3
        HealthCheck = $true
    },
    @{
        Name = "chrome-devtools"
        Command = "npx"
        Args = @("-y", "chrome-devtools-mcp")
        Capabilities = @("browser", "dom", "debugging", "web", "network")
        Priority = 4
        HealthCheck = $true
    }
)

function Write-ServiceLog {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"

    # Write to console if interactive
    if ($Host.UI.RawUI) {
        $color = switch ($Level) {
            "ERROR" { "Red" }
            "WARN" { "Yellow" }
            "DEBUG" { "Gray" }
            default { "White" }
        }
        Write-Host $logMessage -ForegroundColor $color
    }

    # Always log to file
    Add-Content -Path $serviceConfig.LogFile -Value $logMessage
}

function Initialize-Service {
    Write-ServiceLog "Initializing MCP System Service"

    # Create necessary directories
    @($serviceConfig.PipeDirectory) | ForEach-Object {
        if (-not (Test-Path $_)) {
            New-Item -ItemType Directory -Path $_ -Force | Out-Null
            Write-ServiceLog "Created directory: $_"
        }
    }

    # Clean up any leftover processes
    Get-Process | Where-Object { $_.Name -like "*node*" -or $_.Name -like "*npx*" } | Stop-Process -Force -ErrorAction SilentlyContinue
}

function Start-MCPServer {
    param($serverConfig)

    $serverName = $serverConfig.Name
    Write-ServiceLog "Starting MCP server: $serverName"

    try {
        # Set environment variables
        $env:MCP_SERVER_NAME = $serverName
        $env:MCP_SERVER_CAPABILITIES = $serverConfig.Capabilities -join ","
        $env:MCP_SERVER_PRIORITY = $serverConfig.Priority
        $env:NODE_ENV = "production"

        # Start the server process
        $process = Start-Process -FilePath $serverConfig.Command `
                                -ArgumentList $serverConfig.Args `
                                -NoNewWindow `
                                -PassThru `
                                -WorkingDirectory $PSScriptRoot `
                                -RedirectStandardOutput (Join-Path $serviceConfig.PipeDirectory "$serverName.out") `
                                -RedirectStandardError (Join-Path $serviceConfig.PipeDirectory "$serverName.err")

        # Store process info
        $global:MCPProcesses[$serverName] = @{
            Process = $process
            Config = $serverConfig
            StartTime = Get-Date
            Restarts = 0
            LastHealthCheck = Get-Date
            Status = "Starting"
        }

        Write-ServiceLog "Started $serverName with PID: $($process.Id)"
        return $true

    } catch {
        Write-ServiceLog "Failed to start $serverName`: $_" "ERROR"
        return $false
    }
}

function Start-MCPRouter {
    Write-ServiceLog "Starting MCP Router"

    try {
        # Create a simple TCP router using PowerShell
        $routerScript = @"
# MCP Router Service
`$Host = '$($serviceConfig.Host)'
`$Port = $($serviceConfig.Port)
`$LogFile = '$($serviceConfig.LogFile)'

function Write-RouterLog {
    param([string]`$Message, [string]`$Level = "INFO")
    `$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    `$logMessage = "[$timestamp] [ROUTER] [`$Level] `$Message"
    Add-Content -Path `$LogFile -Value `$logMessage
}

Write-RouterLog "Starting MCP Router on `$Host`:`$Port"

try {
    `$listener = New-Object System.Net.Sockets.TcpListener `$Host, `$Port
    `$listener.Start()
    Write-RouterLog "Router listening on `$Host`:`$Port"

    while (`$true) {
        `$client = `$listener.AcceptTcpClient()
        Write-RouterLog "Client connected"

        `$stream = `$client.GetStream()
        `$reader = New-Object System.IO.StreamReader `$stream
        `$writer = New-Object System.IO.StreamWriter `$stream
        `$writer.AutoFlush = `$true

        try {
            while (`$client.Connected) {
                `$line = `$reader.ReadLine()
                if (-not `$line) { break }

                Write-RouterLog "Received: `$line"

                # Parse JSON request
                `$request = `$line | ConvertFrom-Json

                # Generate response based on request
                `$response = @{
                    jsonrpc = "2.0"
                    id = `$request.id
                    result = @{
                        servers = @($global:MCPProcesses.Keys)
                        capabilities = @("filesystem", "git", "code-execution", "browser-debugging")
                        status = "active"
                        timestamp = Get-Date -Format "o"
                    }
                }

                `$jsonResponse = `$response | ConvertTo-Json -Depth 10
                `$writer.WriteLine(`$jsonResponse)
                Write-RouterLog "Sent response"
            }
        } catch {
            Write-RouterLog "Client error: `$_" "ERROR"
        } finally {
            `$client.Close()
        }
    }
} catch {
    Write-RouterLog "Router error: `$_" "ERROR"
} finally {
    `$listener.Stop()
}
"@

        # Save router script
        $routerScriptPath = Join-Path $PSScriptRoot "mcp-router.ps1"
        $routerScript | Out-File -FilePath $routerScriptPath -Encoding UTF8

        # Start router
        $routerProcess = Start-Process -FilePath "powershell.exe" `
                                      -ArgumentList "-ExecutionPolicy", "Bypass", "-File", $routerScriptPath `
                                      -NoNewWindow `
                                      -PassThru

        $global:MCPRouter = $routerProcess
        Write-ServiceLog "MCP Router started with PID: $($routerProcess.Id)"
        return $true

    } catch {
        Write-ServiceLog "Failed to start MCP Router: $_" "ERROR"
        return $false
    }
}

function Start-HealthMonitor {
    Write-ServiceLog "Starting health monitoring"

    $healthScript = {
        while ($global:ServiceRunning) {
            try {
                # Check each MCP server
                foreach ($serverName in $global:MCPProcesses.Keys) {
                    $server = $global:MCPProcesses[$serverName]

                    if ($server.Process.HasExited) {
                        Write-ServiceLog "Server $serverName crashed (PID: $($server.Process.Id)), restarting..." "WARN"

                        # Restart server
                        $server.Restarts++
                        $server.LastHealthCheck = Get-Date

                        if ($server.Restarts -lt 5) {  # Max 5 restarts
                            Start-MCPServer $server.Config
                        } else {
                            Write-ServiceLog "Server $serverName exceeded max restarts, giving up" "ERROR"
                        }
                    } else {
                        $server.Status = "Healthy"
                        $server.LastHealthCheck = Get-Date
                    }
                }

                # Check router
                if ($global:MCPRouter -and $global:MCPRouter.HasExited) {
                    Write-ServiceLog "MCP Router crashed, restarting..." "WARN"
                    Start-MCPRouter
                }

                # Log system status every 5 minutes
                if ((Get-Date).Minute % 5 -eq 0 -and (Get-Date).Second -lt 30) {
                    $healthyServers = ($global:MCPProcesses.Values | Where-Object { $_.Status -eq "Healthy" }).Count
                    Write-ServiceLog "Health check: $healthyServers/$($global:MCPProcesses.Count) servers healthy"
                }

            } catch {
                Write-ServiceLog "Health monitor error: $_" "ERROR"
            }

            Start-Sleep -Seconds 30
        }
    }

    $global:HealthMonitor = Start-Job -ScriptBlock $healthScript
    Write-ServiceLog "Health monitor started"
}

function Start-MCPSystem {
    Write-ServiceLog "Starting complete MCP system"

    # Start MCP Router first
    if (-not (Start-MCPRouter)) {
        Write-ServiceLog "Failed to start MCP Router, cannot continue" "ERROR"
        return $false
    }

    # Start all MCP servers
    $startedServers = 0
    foreach ($server in $mcpServers) {
        if (Start-MCPServer $server) {
            $startedServers++
        }
        Start-Sleep -Seconds 3  # Stagger startup
    }

    Write-ServiceLog "Started $startedServers/$($mcpServers.Count) MCP servers"

    # Start health monitoring
    Start-HealthMonitor

    Write-ServiceLog "MCP System fully operational"
    Write-ServiceLog "Router listening on $($serviceConfig.Host):$($serviceConfig.Port)"
    Write-ServiceLog "Available servers: $($global:MCPProcesses.Keys -join ', ')"

    return $true
}

function Stop-MCPSystem {
    Write-ServiceLog "Stopping MCP system"

    $global:ServiceRunning = $false

    # Stop health monitor
    if ($global:HealthMonitor) {
        Stop-Job $global:HealthMonitor -ErrorAction SilentlyContinue
        Remove-Job $global:HealthMonitor -ErrorAction SilentlyContinue
    }

    # Stop all MCP servers
    foreach ($serverName in $global:MCPProcesses.Keys) {
        $server = $global:MCPProcesses[$serverName]
        try {
            Stop-Process -Id $server.Process.Id -Force -ErrorAction SilentlyContinue
            Write-ServiceLog "Stopped server: $serverName"
        } catch {
            Write-ServiceLog "Error stopping $serverName`: $_" "WARN"
        }
    }

    # Stop router
    if ($global:MCPRouter) {
        try {
            Stop-Process -Id $global:MCPRouter.Id -Force -ErrorAction SilentlyContinue
            Write-ServiceLog "Stopped MCP Router"
        } catch {
            Write-ServiceLog "Error stopping MCP Router: $_" "WARN"
        }
    }

    # Clean up
    $global:MCPProcesses = @{}
    $global:MCPRouter = $null

    Write-ServiceLog "MCP System stopped"
}

# Service event handlers
$global:ServiceStopHandler = {
    Write-ServiceLog "Received service stop signal"
    Stop-MCPSystem
}

# Register service stop handler
Register-EngineEvent -SourceIdentifier PowerShell.Exiting -Action $global:ServiceStopHandler

# Main service execution
try {
    Initialize-Service

    if (Start-MCPSystem) {
        Write-ServiceLog "MCP System Service started successfully"

        # Keep service running
        while ($global:ServiceRunning) {
            Start-Sleep -Seconds 60

            # Periodic status log
            $uptime = (Get-Date) - (Get-Date).Date
            Write-ServiceLog "Service running - Uptime: $($uptime.Hours)h $($uptime.Minutes)m"
        }
    } else {
        Write-ServiceLog "Failed to start MCP system" "ERROR"
        exit 1
    }

} catch {
    Write-ServiceLog "Service error: $_" "ERROR"
    Stop-MCPSystem
    exit 1
} finally {
    Write-ServiceLog "Service shutting down"
}