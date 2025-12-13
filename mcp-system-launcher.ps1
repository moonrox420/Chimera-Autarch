# System-Wide MCP Server Launcher
# This script runs MCP servers as background services accessible from any application

param(
    [switch]$Start,
    [switch]$Stop,
    [switch]$Status,
    [switch]$Restart
)

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

function Start-Servers {
    Write-Host "Starting MCP Servers System-Wide..." -ForegroundColor Green

    foreach ($server in $servers) {
        $jobName = "MCP_$($server.Name)"

        # Check if already running
        $existingJob = Get-Job -Name $jobName -ErrorAction SilentlyContinue
        if ($existingJob) {
            Write-Host "$($server.Name) is already running" -ForegroundColor Yellow
            continue
        }

        Write-Host "Starting $($server.Name)..." -ForegroundColor Cyan

        # Start as background job
        $job = Start-Job -Name $jobName -ScriptBlock {
            param($cmd, $args, $port)
            try {
                # Set environment for system-wide access
                $env:NODE_ENV = "production"
                $env:MCP_SERVER_PORT = $port

                # Run the server
                & $cmd @args
            } catch {
                Write-Error "Failed to start server: $_"
            }
        } -ArgumentList $server.Command, $server.Args, $server.Port

        Start-Sleep -Seconds 2

        # Verify server is running
        if (Get-Job -Name $jobName | Where-Object { $_.State -eq "Running" }) {
            Write-Host "✓ $($server.Name) started successfully (Port: $($server.Port))" -ForegroundColor Green
        } else {
            Write-Host "✗ $($server.Name) failed to start" -ForegroundColor Red
        }
    }

    Write-Host "`nMCP Servers are now running system-wide!" -ForegroundColor Green
    Write-Host "They can be accessed from any application on your computer." -ForegroundColor Cyan
}

function Stop-Servers {
    Write-Host "Stopping MCP Servers..." -ForegroundColor Yellow

    foreach ($server in $servers) {
        $jobName = "MCP_$($server.Name)"
        $job = Get-Job -Name $jobName -ErrorAction SilentlyContinue

        if ($job) {
            Stop-Job -Name $jobName -ErrorAction SilentlyContinue
            Remove-Job -Name $jobName -ErrorAction SilentlyContinue
            Write-Host "✓ $($server.Name) stopped" -ForegroundColor Green
        } else {
            Write-Host "$($server.Name) was not running" -ForegroundColor Yellow
        }
    }
}

function Get-ServerStatus {
    Write-Host "MCP Server Status:" -ForegroundColor Cyan
    Write-Host "==================" -ForegroundColor Cyan

    foreach ($server in $servers) {
        $jobName = "MCP_$($server.Name)"
        $job = Get-Job -Name $jobName -ErrorAction SilentlyContinue

        if ($job) {
            $status = $job.State
            $color = if ($status -eq "Running") { "Green" } else { "Red" }
            Write-Host "$($server.Name): " -NoNewline
            Write-Host $status -ForegroundColor $color -NoNewline
            Write-Host " (Port: $($server.Port))"
        } else {
            Write-Host "$($server.Name): " -NoNewline
            Write-Host "Not Running" -ForegroundColor Red -NoNewline
            Write-Host " (Port: $($server.Port))"
        }
    }
}

function Restart-Servers {
    Write-Host "Restarting MCP Servers..." -ForegroundColor Yellow
    Stop-Servers
    Start-Sleep -Seconds 3
    Start-Servers
}

# Main logic
switch {
    $Start { Start-Servers }
    $Stop { Stop-Servers }
    $Status { Get-ServerStatus }
    $Restart { Restart-Servers }
    default {
        Write-Host "MCP Server System Manager" -ForegroundColor Cyan
        Write-Host "Usage:" -ForegroundColor White
        Write-Host "  .\mcp-system-launcher.ps1 -Start    # Start all servers"
        Write-Host "  .\mcp-system-launcher.ps1 -Stop     # Stop all servers"
        Write-Host "  .\mcp-system-launcher.ps1 -Status   # Show server status"
        Write-Host "  .\mcp-system-launcher.ps1 -Restart  # Restart all servers"
        Write-Host ""
        Get-ServerStatus
    }
}