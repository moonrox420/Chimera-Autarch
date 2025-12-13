@echo off
echo ========================================
echo   MCP Servers - System Wide Launcher
echo ========================================
echo.

echo Starting MCP Servers system-wide...
echo They will be accessible from any application on your computer.
echo.

echo Press Ctrl+C to stop all servers
echo.

REM Start filesystem server
echo Starting Filesystem Server (Port 3001)...
start "MCP-Filesystem" /B npx -y @modelcontextprotocol/server-filesystem "C:\Drox_AI"

REM Start code runner server
echo Starting Code Runner Server (Port 3002)...
start "MCP-CodeRunner" /B npx -y mcp-server-code-runner

REM Start Chrome DevTools server
echo Starting Chrome DevTools Server (Port 3003)...
start "MCP-ChromeDevTools" /B npx -y chrome-devtools-mcp

echo.
echo ========================================
echo   All MCP Servers Started!
echo ========================================
echo.
echo Servers are now running in the background and accessible at:
echo - Filesystem:    http://localhost:3001
echo - Code Runner:   http://localhost:3002
echo - Chrome DevTools: http://localhost:3003
echo.
echo You can access these from any application on your computer.
echo.
echo Press any key to exit (servers will keep running)...
pause >nul