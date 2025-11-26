@echo off
REM DroxAI Stop Script
REM This batch file is intended to find and kill the DroxAI backend process.

echo ========================================
echo     DroxAI - Initiating Shutdown
echo ========================================

REM Check if the backend is running by looking for the Python process running the script
REM We search for the process running 'chimera_autarch_v4_tuned.py' or 'DroxAI_Core.py'

tasklist /FI "IMAGENAME eq python.exe" /V /FO CSV | findstr /I "chimera_autarch_v4_tuned.py" > nul
if not errorlevel 1 (
    echo Attempting graceful shutdown via DroxAI_Launcher.py...
    REM Note: The DroxAI_Launcher.py waits for the process, so killing the launcher
    REM requires finding the subprocess PID, which is complex in batch.
    
    REM Simpler method: Find the process running the backend file and kill it.
    for /f "tokens=2" %%i in ('tasklist /nh /fi "imagename eq python.exe" /v ^| findstr /i "chimera_autarch_v4_tuned.py"') do (
        echo Found backend PID: %%i
        taskkill /PID %%i /T /F > nul
        echo Backend process terminated.
        goto success
    )
)

echo.
echo DroxAI backend process not found or already stopped.
goto end

:success
echo.
echo DroxAI Fortress Offline.

:end
pause