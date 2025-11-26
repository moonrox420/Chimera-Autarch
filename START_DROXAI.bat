@echo off
REM DroxAI Consumer Launcher - Single Double-Click Solution
REM This file provides a completely consumer-friendly experience

title DroxAI - Advanced AI Orchestration System

echo ================================================================
echo    🚀 DroxAI v1.0.0 - Consumer Edition
echo    Advanced AI Orchestration System
echo ================================================================
echo.

REM Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo.
    echo 📋 TO USE DroxAI:
    echo    1. Download and install Python 3.8+ from https://python.org
    echo    2. Make sure to check "Add Python to PATH" during installation
    echo    3. Restart your computer after installing Python
    echo    4. Double-click this file again
    echo.
    pause
    exit /b 1
)

echo ✅ Python detected
echo.

REM Install required packages automatically
echo 📦 Checking and installing required packages...
python -m pip install --upgrade pip >nul 2>&1
python -m pip install websockets aiohttp numpy pyyaml aiosqlite >nul 2>&1

if errorlevel 1 (
    echo ⚠️  Some packages failed to install automatically
    echo 📋 MANUAL INSTALLATION REQUIRED:
    echo    Open Command Prompt as Administrator and run:
    echo    pip install websockets aiohttp numpy pyyaml aiosqlite
    echo.
    pause
    exit /b 1
)

echo ✅ All packages installed
echo.

REM Start DroxAI with consumer-friendly interface
echo 🚀 Starting DroxAI...
echo.
echo ⏳ Initializing AI orchestration system...
echo    This may take a few moments on first startup...
echo.

REM Start the system and open web interface
start /wait python DroxAI_Consumer_Ready.py

echo.
echo 🛑 DroxAI has been stopped
echo.
pause
