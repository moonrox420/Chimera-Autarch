@echo off
REM DroxAI Consumer Launcher Stub
REM This batch file provides a simple Windows launcher

echo ========================================
echo     DroxAI v1.0.0 - Consumer Edition
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
REM %* passes any command line arguments to the Python script
python DroxAI_Launcher.py %*

if errorlevel 1 (
    echo.
    echo An error occurred. Check the logs directory for details.
    pause
)
