# MCP Server Launch Guide

## 🚀 Quick Start

### Option 1: Batch Script (Windows)
```cmd
launch_mcp_servers.bat
```

### Option 2: PowerShell Script
```powershell
.\launch_mcp_servers.ps1
```

### Option 3: Manual Commands

#### Install Servers
```bash
npm install -g @modelcontextprotocol/server-filesystem mcp-server-code-runner chrome-devtools-mcp
```

#### Launch Individual Servers

**Filesystem Server:**
```bash
npx -y @modelcontextprotocol/server-filesystem "C:\Drox_AI"
```

**Code Runner Server:**
```bash
npx -y mcp-server-code-runner
```

**Chrome DevTools Server:**
```bash
npx -y chrome-devtools-mcp
```

#### Launch All Servers
```bash
# Windows PowerShell
Start-Process -NoNewWindow -FilePath "npx" -ArgumentList "-y", "@modelcontextprotocol/server-filesystem", "C:\Drox_AI"
Start-Process -NoNewWindow -FilePath "npx" -ArgumentList "-y", "mcp-server-code-runner"
Start-Process -NoNewWindow -FilePath "npx" -ArgumentList "-y", "chrome-devtools-mcp"
```

### Option 4: NPM Scripts
```bash
# Install concurrently for parallel execution
npm install -g concurrently

# Install servers
npm run install-servers

# Start all servers
npm run start:all

# Development mode (with auto-restart)
npm run dev
```

## 📋 Server Details

### Filesystem Server
- **Package:** `@modelcontextprotocol/server-filesystem`
- **Purpose:** File system operations
- **Root Directory:** `C:\Drox_AI`
- **Capabilities:** Read, write, list files and directories

### Code Runner Server
- **Package:** `mcp-server-code-runner`
- **Purpose:** Execute code snippets
- **Capabilities:** Run code in various languages

### Chrome DevTools Server
- **Package:** `chrome-devtools-mcp`
- **Purpose:** Chrome browser debugging and inspection
- **Capabilities:** DOM inspection, network monitoring, console access

## 🔧 Configuration

The servers are configured in `.continue/mcpServers/new-mcp-server.yaml`:

```yaml
name: MCP Server Suite
version: 1.0.0
schema: v1
mcpServers:
  - name: filesystem-server
    command: npx
    args: [-y, "@modelcontextprotocol/server-filesystem", "C:\\Drox_AI"]
    env: {NODE_ENV: production}
  - name: code-runner-server
    command: npx
    args: [-y, "mcp-server-code-runner"]
    env: {NODE_ENV: production}
  - name: chrome-devtools-server
    command: npx
    args: [-y, "chrome-devtools-mcp"]
    env: {NODE_ENV: production}
```

## 🛠️ Troubleshooting

### Port Conflicts
If servers fail to start due to port conflicts:
1. Check what's using the ports: `netstat -ano | findstr :PORT`
2. Kill conflicting processes: `taskkill /PID <PID> /F`

### Permission Issues
Run PowerShell as Administrator or use:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Node.js Issues
Ensure Node.js is installed:
```bash
node --version
npm --version
```

## 📚 Additional MCP Servers

Available MCP servers you can add:

- `@notionhq/notion-mcp-server` - Notion integration
- `@sentry/mcp-server` - Error monitoring
- `@heroku/mcp-server` - Heroku deployment
- `@supabase/mcp-server-supabase` - Database operations
- `@hubspot/mcp-server` - CRM integration

Add them to your config and install with npm!