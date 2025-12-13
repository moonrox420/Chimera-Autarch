@echo off
echo Starting MCP Server Suite...

echo Starting filesystem server...
start "filesystem-server" npx -y @modelcontextprotocol/server-filesystem "C:\Drox_AI"

echo Starting code runner server...
start "code-runner-server" npx -y mcp-server-code-runner

echo Starting Chrome DevTools server...
start "chrome-devtools-server" npx -y chrome-devtools-mcp

echo All MCP servers started!
pause