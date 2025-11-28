#!/usr/bin/env pwsh
<# 
.SYNOPSIS
Build script for DroxAI Consumer Release
Packages the application into a consumer-ready format
#>

param(
  [switch]$Portable,
  [switch]$Installer,
  [string]$Version = "1.0.0"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   DroxAI Consumer Release Builder" -ForegroundColor Cyan  
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$APP_NAME = "DroxAI"
$RELEASE_DIR = "release"
$BUILD_DIR = "build"
$APP_DIR = "$RELEASE_DIR\$APP_NAME"

# Clean previous builds
Write-Host "[BUILD] Cleaning previous builds..." -ForegroundColor Yellow
if (Test-Path $BUILD_DIR) { Remove-Item $BUILD_DIR -Recurse -Force }
if (Test-Path "$RELEASE_DIR\$APP_NAME`_Portable_$Version.zip") { 
  Remove-Item "$RELEASE_DIR\$APP_NAME`_Portable_$Version.zip" -Force 
}

# Create build directory
New-Item -ItemType Directory -Path $BUILD_DIR -Force | Out-Null

Write-Host "[BUILD] Building DroxAI Consumer Package..." -ForegroundColor Green
Write-Host "Version: $Version" -ForegroundColor Gray
Write-Host "Output: $APP_DIR" -ForegroundColor Gray
Write-Host ""

# Copy configuration files
Write-Host "[BUILD] Copying configuration..." -ForegroundColor Yellow
Copy-Item "$APP_DIR\config\appsettings.json" "$BUILD_DIR\" -Force

# Copy consumer config module
Write-Host "[BUILD] Copying configuration module..." -ForegroundColor Yellow
Copy-Item "droxai_config.py" "$BUILD_DIR\" -Force

# Copy launcher script
Write-Host "[BUILD] Copying launcher..." -ForegroundColor Yellow
Copy-Item "$APP_DIR\DroxAI_Launcher.py" "$BUILD_DIR\" -Force

# Copy core engine
Write-Host "[BUILD] Copying core engine..." -ForegroundColor Yellow
Copy-Item "$APP_DIR\bin\DroxAI_Core.py" "$BUILD_DIR\" -Force

# Copy directory structure
Write-Host "[BUILD] Creating directory structure..." -ForegroundColor Yellow
$dirs = @("config", "data", "logs", "temp", "plugins", "runtime\models", "runtime\certificates")
foreach ($dir in $dirs) {
  $fullDir = "$BUILD_DIR\$dir"
  New-Item -ItemType Directory -Path $fullDir -Force | Out-Null
    
  # Create a .gitkeep file to preserve empty directories
  "$APP_NAME Runtime Directory" | Out-File -FilePath "$fullDir\.keep" -Encoding UTF8
}

# Create requirements.txt for consumer installation
Write-Host "[BUILD] Creating requirements..." -ForegroundColor Yellow
$requirements = @"
# DroxAI Consumer Requirements
websockets>=11.0.0
aiosqlite>=0.19.0
numpy>=1.24.0
aiofiles>=23.0.0
pyyaml>=6.0
"@

$requirements | Out-File -FilePath "$BUILD_DIR\requirements.txt" -Encoding UTF8

# Create a simple consumer executable stub
Write-Host "[BUILD] Creating executable launcher..." -ForegroundColor Yellow
$launcherStub = @"
@echo off
REM DroxAI Consumer Launcher Stub
REM This batch file provides a simple Windows launcher

echo ========================================
echo    DroxAI v$Version - Consumer Edition
echo ========================================
echo.

REM Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Change to script directory
cd /d "%~dp0"

REM Run the Python launcher
python DroxAI_Launcher.py %*

if errorlevel 1 (
    echo.
    echo An error occurred. Check the logs directory for details.
    pause
)
"@

$launcherStub | Out-File -FilePath "$BUILD_DIR\DroxAI.bat" -Encoding ASCII

# Create a user guide
Write-Host "[BUILD] Creating user guide..." -ForegroundColor Yellow
$readme = @"
# DroxAI v$Version - Consumer Edition

## Quick Start

1. **Prerequisites**
   - Windows 10/11
   - Python 3.8 or later (download from python.org)

2. **Installation**
   - No installation required - this is a portable application
   - Extract to any folder on your computer

3. **Running DroxAI**
   - Double-click `DroxAI.bat` to start
   - Or run: `python DroxAI_Launcher.py`

4. **Accessing the Interface**
   - Web Dashboard: http://localhost:3000
   - WebSocket API: ws://localhost:3001

## Features

- **Advanced AI Orchestration**: Self-evolving AI system with metacognitive capabilities
- **Web Dashboard**: Real-time monitoring and control interface
- **WebSocket API**: Programmatic access for developers
- **Plugin System**: Extensible architecture for custom functionality
- **Federated Learning**: Distributed AI training capabilities

## Configuration

- Main configuration: `config\appsettings.json`
- Logs: `logs\droxai.log`
- Data: `data\droxai_memory.db`
- Plugins: `plugins\` directory

## Troubleshooting

### Port Already in Use
- Edit `config\appsettings.json` to change ports
- Default HTTP port: 3000
- Default WebSocket port: 3001

### Python Not Found
- Install Python 3.8+ from python.org
- Ensure "Add Python to PATH" is checked during installation

### Permission Errors
- Run as Administrator if needed
- Check antivirus software isn't blocking the application

## System Requirements

- Windows 10/11
- 4GB RAM minimum (8GB recommended)
- 1GB disk space
- Internet connection (for initial setup)

## Support

For issues and support, check the logs directory for error details.

---
Â© 2025 DroxAI - Advanced AI Orchestration System
Built with consumer-friendly packaging
"@

$readme | Out-File -FilePath "$BUILD_DIR\README.md" -Encoding UTF8

# Copy necessary files to build directory
Write-Host "[BUILD] Finalizing build..." -ForegroundColor Yellow

# Create portable ZIP if requested
if ($Portable) {
  Write-Host "[BUILD] Creating portable ZIP..." -ForegroundColor Green
    
  $zipName = "$RELEASE_DIR\$APP_NAME`_Portable_$Version.zip"
    
  # Use PowerShell's built-in compression
  Get-ChildItem $BUILD_DIR | ForEach-Object {
    Compress-Archive -Path $_.FullName -DestinationPath $zipName -Update
  }
    
  Write-Host "[BUILD] Portable package created: $zipName" -ForegroundColor Green
}

# Create installer if requested (placeholder for now)
if ($Installer) {
  Write-Host "[BUILD] Creating installer stub..." -ForegroundColor Yellow
    
  $installerScript = @"
; DroxAI Installer Script (for Inno Setup)
; This is a placeholder - actual installer would be created with Inno Setup

[Setup]
AppName=DroxAI
AppVersion=$Version
DefaultDirName={pf}\DroxAI
DefaultGroupName=DroxAI

[Files]
Source: "$BUILD_DIR\*"; DestDir: "{app}"; Flags: recursesubdirs

[Icons]
Name: "{group}\DroxAI"; Filename: "{app}\DroxAI.bat"
Name: "{commondesktop}\DroxAI"; Filename: "{app}\DroxAI.bat"

[Run]
Filename: "{app}\python.exe"; Parameters: "-m pip install -r requirements.txt"; Flags: runascurrentuser
"@

  $installerScript | Out-File -FilePath "$BUILD_DIR\installer.iss" -Encoding ASCII
  Write-Host "[BUILD] Installer script created: $BUILD_DIR\installer.iss" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[BUILD] ========================================" -ForegroundColor Cyan
Write-Host "[BUILD] Build Complete!" -ForegroundColor Green
Write-Host "[BUILD] ========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Consumer Package Location: $BUILD_DIR" -ForegroundColor White

if ($Portable) {
  Write-Host "Portable ZIP: $RELEASE_DIR\$APP_NAME`_Portable_$Version.zip" -ForegroundColor Green
}

if ($Installer) {
  Write-Host "Installer Script: $BUILD_DIR\installer.iss" -ForegroundColor Yellow
  Write-Host "  To create installer: Install Inno Setup and compile installer.iss" -ForegroundColor Gray
}

Write-Host ""
Write-Host "To test the package:" -ForegroundColor Cyan
Write-Host "1. Copy $BUILD_DIR to a test location" -ForegroundColor Gray
Write-Host "2. Run DroxAI.bat" -ForegroundColor Gray
Write-Host "3. Open http://localhost:3000" -ForegroundColor Gray
Write-Host ""

