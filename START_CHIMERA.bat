@echo off
REM CHIMERA AUTARCH - Windows Launcher
REM Double-click this file to start

title CHIMERA AUTARCH v3.0

echo ================================================
echo    CHIMERA AUTARCH v3.0 - Starting Up...
echo ================================================
echo.

cd /d C:\Drox_AI

echo [1/3] Activating environment...
call droxai-env\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Could not activate virtual environment
    pause
    exit /b 1
)
echo OK - Environment activated

echo [2/3] Checking dependencies...
python -c "import aiohttp, websockets" 2>nul
if errorlevel 1 (
    echo Installing dependencies...
    pip install aiohttp websockets --quiet
)
echo OK - Dependencies ready

echo [3/3] Starting CHIMERA AUTARCH...
echo.
echo ================================================
echo    Dashboard: http://localhost:3000
echo    WebSocket: ws://localhost:3001
echo ================================================
echo.
echo Press Ctrl+C to stop the server
echo.

python src\chimera\chimera_main.py

pause
