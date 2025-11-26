@echo off
REM CHIMERA AUTARCH - Windows Batch Launcher
REM Run this in Windows Command Prompt or PowerShell

echo ========================================
echo CHIMERA AUTARCH v3.0 - Starting...
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found
    pause
    exit /b 1
)

echo [OK] Python found

REM Check Ollama
ollama list >nul 2>&1
if errorlevel 1 (
    echo WARNING: Ollama not running - starting...
    start /B ollama serve
    timeout /t 3 >nul
)

echo [OK] Ollama running

REM Install dependencies
echo Installing dependencies...
python -m pip install -q httpx aiosqlite websockets pyyaml

REM Start CHIMERA
echo.
echo ========================================
echo Starting CHIMERA AUTARCH...
echo Dashboard: http://localhost:8000
echo WebSocket: ws://localhost:8765
echo ========================================
echo.

python chimera_autarch.py

pause
