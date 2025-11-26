set HTTP_PORT=3000
WS_PORT=3001
HTTP_PORT=3000
WS_PORT=3001
HTTP_PORT=3000
WS_PORT=3001
HTTP_PORT=3000
WS_PORT=3001
set HTTP_PORT=3000
WS_PORT=3001
HTTP_PORT=3000
WS_PORT=3001
HTTP_PORT=3000
WS_PORT=3001
HTTP_PORT=3000
WS_PORT=3001

@echo off
title DroxAI Consumer Launcher
echo ============================================================
echo    DroxAI - Advanced AI Orchestration System
echo    Consumer Edition v1.0.0
echo ============================================================
echo.
echo Starting DroxAI Consumer...
echo.

REM Try to find Python and run the consumer
WHERE python >nul 2>&1
IF %ERRORLEVEL% EQU 0 (
    echo Found Python - Starting DroxAI Consumer
    python DroxAI_Consumer_Ready.py
) ELSE (
    echo Python not found in PATH
    echo Please install Python 3.8+ and add it to PATH
    pause
)
