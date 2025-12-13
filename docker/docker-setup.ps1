#!/usr/bin/env pwsh
<#
.SYNOPSIS
    CHIMERA AUTARCH – Docker deployment & management script
.DESCRIPTION
    Full lifecycle control: setup, build, start, stop, logs, status, shell, and clean.
.PARAMETER Action
    setup | build | start | stop | restart | logs | status | shell | clean
.PARAMETER Follow
    Follow logs in real-time (used with -Action logs)
.EXAMPLE
    .\docker-setup.ps1 setup     # First-time build
    .\docker-setup.ps1 start     # Launch containers
    .\docker-setup.ps1 logs -Follow
#>

param(
    [Parameter(Mandatory, Position = 0)]
    [ValidateSet("setup","build","start","stop","restart","logs","status","shell","clean")]
    [string]$Action,

    [switch]$Follow
)

$ErrorActionPreference = "Stop"

function Write-Status {
    param([string]$Message, [string]$Type = "INFO")
    $color = switch ($Type) {
        "SUCCESS" { "Green" }
        "ERROR"   { "Red" }
        "WARN"    { "Yellow" }
        default   { "Cyan" }
    }
    Write-Host "[$Type] " -NoNewline -ForegroundColor $color
    Write-Host $Message
}

# ── Docker prerequisites ─────────────────────────────────────
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Status "Docker not found in PATH" "ERROR"
    Start-Process "https://www.docker.com/products/docker-desktop/"
    exit 1
}
if (-not (docker info >$null 2>&1)) {
    Write-Status "Docker daemon is not running – start Docker Desktop first" "ERROR"
    exit 1
}

Write-Host "`n🐳 CHIMERA AUTARCH Docker Manager" -ForegroundColor Cyan
Write-Host "================================`n" -ForegroundColor Cyan

switch ($Action) {

    "setup" {
        Write-Status "Setting up Docker environment"

        $required = @("Dockerfile", "docker-compose.yml", "requirements.txt", "src/droxai_root")
        foreach ($f in $required) {
            if (Test-Path $f) { Write-Status "$f → found" "SUCCESS" }
            else { Write-Status "$f → missing" "ERROR"; exit 1 }
        }

        Write-Status "Building image (no cache)"
        docker-compose build --no-cache
        if ($LASTEXITCODE -ne 0) { Write-Status "Build failed" "ERROR"; exit 1 }

        Write-Status "Setup complete!" "SUCCESS"
        Write-Host "`nNext → .\docker-setup.ps1 start`n" -ForegroundColor Green
    }

    "build" {
        Write-Status "Building image"
        docker-compose build
        if ($LASTEXITCODE -eq 0) { Write-Status "Build successful" "SUCCESS" }
    }

    "start" {
        Write-Status "Starting containers (detached)"
        docker-compose up -d
        if ($LASTEXITCODE -ne 0) { Write-Status "Failed to start" "ERROR"; exit 1 }

        Write-Status "CHIMERA AUTARCH is LIVE" "SUCCESS"
        Write-Host @"
    Dashboard  → http://localhost:3000
    God CLI    → http://localhost:3000/chimera_god_cli.html
    WebSocket  → ws://localhost:3001/ws/god
    Metrics    → http://localhost:3000/metrics
"@ -ForegroundColor White

        Start-Sleep -Seconds 4
        $health = docker inspect --format='{{.State.Health.Status}}' drox_ai-chimera-1 2>$null
        if ($health -eq "healthy") { Write-Status "Health check: healthy" "SUCCESS" }
    }

    "stop"   { docker-compose stop; Write-Status "Containers stopped" "SUCCESS" }
    "restart"{ docker-compose restart; Write-Status "Containers restarted" "SUCCESS" }

    "logs" {
        if ($Follow) { docker-compose logs -f }
        else { docker-compose logs --tail=100 }
    }

    "status" {
        docker-compose ps
        $c = "drox_ai-chimera-1"
        $state  = docker inspect --format='{{.State.Status}}' $c 2>$null
        $health = docker inspect --format='{{.State.Health.Status}}' $c 2>$null
        if ($state) {
            Write-Host "`nState:  $state" -ForegroundColor $(if($state -eq "running"){"Green"}else{"Yellow"})
            if ($health) { Write-Host "Health: $health`n" -ForegroundColor $(if($health -eq "healthy"){"Green"}else{"Red"}) }
            docker stats --no-stream $c
        }
    }

    "shell" {
        $c = "drox_ai-chimera-1"
        if ((docker inspect --format='{{.State.Status}}' $c) -eq "running") {
            docker exec -it $c /bin/bash
        } else {
            Write-Status "Container not running – start it first" "ERROR"
        }
    }

    "clean" {
        Write-Host "`nThis will:" -ForegroundColor Yellow
        Write-Host " • Stop & remove containers`n • Remove CHIMERA images`n • Prune unused resources`n"
        if ((Read-Host "Continue? (y/N)") -ne "y") { exit }

        docker-compose down
        docker-compose down --rmi local
        docker system prune -f --volumes
        Write-Status "Cleanup complete" "SUCCESS"
    }
}

Write-Host ""