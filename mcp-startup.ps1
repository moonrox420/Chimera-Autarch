# MCP Server Auto-Startup Script
# Add this to Windows Startup or Task Scheduler for automatic launch

# Set execution policy for this session
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process -Force

# Change to the script directory
Set-Location $PSScriptRoot

# Log startup
$logPath = Join-Path $PSScriptRoot "mcp-startup.log"
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
Add-Content -Path $logPath -Value "[$timestamp] Starting MCP servers..."

# Wait for network to be ready
$networkReady = $false
$attempts = 0
while (-not $networkReady -and $attempts -lt 30) {
    try {
        $testConnection = Test-NetConnection -ComputerName 8.8.8.8 -Port 53 -ErrorAction Stop
        if ($testConnection.TcpTestSucceeded) {
            $networkReady = $true
        }
    } catch {
        Start-Sleep -Seconds 2
        $attempts++
    }
}

if (-not $networkReady) {
    Add-Content -Path $logPath -Value "[$timestamp] Network not ready after 60 seconds, starting anyway..."
}

# Start MCP servers using the system launcher
try {
    & (Join-Path $PSScriptRoot "mcp-system-launcher.ps1") -Start
    Add-Content -Path $logPath -Value "[$timestamp] MCP servers started successfully"
} catch {
    Add-Content -Path $logPath -Value "[$timestamp] Failed to start MCP servers: $_"
}

# Optional: Start as Windows service if available
$serviceName = "MCP-Servers"
$service = Get-Service -Name $serviceName -ErrorAction SilentlyContinue
if ($service -and $service.Status -ne "Running") {
    try {
        Start-Service -Name $serviceName
        Add-Content -Path $logPath -Value "[$timestamp] MCP service started"
    } catch {
        Add-Content -Path $logPath -Value "[$timestamp] Failed to start MCP service: $_"
    }
}