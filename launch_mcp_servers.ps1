# Launch MCP Servers
Write-Host "Starting MCP Server Suite..." -ForegroundColor Green

# Start filesystem server
Write-Host "Starting filesystem server..." -ForegroundColor Yellow
Start-Process -NoNewWindow -FilePath "npx" -ArgumentList "-y", "@modelcontextprotocol/server-filesystem", "C:\Drox_AI"

# Start code runner server
Write-Host "Starting code runner server..." -ForegroundColor Yellow
Start-Process -NoNewWindow -FilePath "npx" -ArgumentList "-y", "mcp-server-code-runner"

# Start Chrome DevTools server
Write-Host "Starting Chrome DevTools server..." -ForegroundColor Yellow
Start-Process -NoNewWindow -FilePath "npx" -ArgumentList "-y", "chrome-devtools-mcp"

Write-Host "All MCP servers started!" -ForegroundColor Green
Read-Host "Press Enter to exit"