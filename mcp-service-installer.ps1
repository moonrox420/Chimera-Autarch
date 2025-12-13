# MCP Server Windows Service Installer
# Run this as Administrator to install MCP servers as Windows services

#Requires -RunAsAdministrator

param(
    [switch]$Install,
    [switch]$Uninstall,
    [switch]$Start,
    [switch]$Stop,
    [switch]$Status
)

$serviceName = "MCP-Servers"
$displayName = "MCP Server Suite"
$description = "Model Context Protocol Servers for system-wide AI assistance"

$scriptPath = Join-Path $PSScriptRoot "mcp-service-runner.ps1"
$servicePath = Join-Path $PSScriptRoot "mcp-service-runner.ps1"

function Install-Service {
    Write-Host "Installing MCP Servers as Windows Service..." -ForegroundColor Cyan

    # Create the service
    $params = @{
        Name = $serviceName
        BinaryPathName = "powershell.exe -ExecutionPolicy Bypass -File `"$servicePath`""
        DisplayName = $displayName
        Description = $description
        StartupType = "Automatic"
        Credential = "LocalSystem"
    }

    try {
        New-Service @params
        Write-Host "✓ Service '$displayName' installed successfully" -ForegroundColor Green

        # Set service description
        sc.exe description $serviceName $description

        Write-Host "✓ Service configured to start automatically" -ForegroundColor Green
        Write-Host ""
        Write-Host "To start the service manually:" -ForegroundColor Yellow
        Write-Host "  Start-Service -Name '$serviceName'"
        Write-Host ""
        Write-Host "To start automatically on boot:" -ForegroundColor Yellow
        Write-Host "  Set-Service -Name '$serviceName' -StartupType Automatic"

    } catch {
        Write-Error "Failed to install service: $_"
    }
}

function Uninstall-Service {
    Write-Host "Uninstalling MCP Servers service..." -ForegroundColor Yellow

    try {
        # Stop service if running
        Stop-Service -Name $serviceName -ErrorAction SilentlyContinue

        # Remove service
        sc.exe delete $serviceName

        Write-Host "✓ Service '$displayName' uninstalled successfully" -ForegroundColor Green
    } catch {
        Write-Error "Failed to uninstall service: $_"
    }
}

function Start-MCPService {
    Write-Host "Starting MCP Servers service..." -ForegroundColor Green
    try {
        Start-Service -Name $serviceName
        Write-Host "✓ Service started successfully" -ForegroundColor Green
    } catch {
        Write-Error "Failed to start service: $_"
    }
}

function Stop-MCPService {
    Write-Host "Stopping MCP Servers service..." -ForegroundColor Yellow
    try {
        Stop-Service -Name $serviceName
        Write-Host "✓ Service stopped successfully" -ForegroundColor Green
    } catch {
        Write-Error "Failed to stop service: $_"
    }
}

function Get-ServiceStatus {
    Write-Host "MCP Servers Service Status:" -ForegroundColor Cyan
    Write-Host "===========================" -ForegroundColor Cyan

    try {
        $service = Get-Service -Name $serviceName -ErrorAction Stop
        Write-Host "Service Name: $($service.Name)" -ForegroundColor White
        Write-Host "Display Name: $($service.DisplayName)" -ForegroundColor White
        Write-Host "Status: $($service.Status)" -ForegroundColor $(if ($service.Status -eq "Running") { "Green" } else { "Red" })
        Write-Host "Startup Type: $($service.StartupType)" -ForegroundColor White
    } catch {
        Write-Host "Service '$serviceName' is not installed" -ForegroundColor Red
    }
}

# Main logic
switch {
    $Install { Install-Service }
    $Uninstall { Uninstall-Service }
    $Start { Start-MCPService }
    $Stop { Stop-MCPService }
    $Status { Get-ServiceStatus }
    default {
        Write-Host "MCP Server Windows Service Manager" -ForegroundColor Cyan
        Write-Host "==================================" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Usage (run as Administrator):" -ForegroundColor White
        Write-Host "  .\mcp-service-installer.ps1 -Install   # Install as Windows service"
        Write-Host "  .\mcp-service-installer.ps1 -Uninstall # Remove Windows service"
        Write-Host "  .\mcp-service-installer.ps1 -Start     # Start the service"
        Write-Host "  .\mcp-service-installer.ps1 -Stop      # Stop the service"
        Write-Host "  .\mcp-service-installer.ps1 -Status    # Show service status"
        Write-Host ""
        Get-ServiceStatus
    }
}