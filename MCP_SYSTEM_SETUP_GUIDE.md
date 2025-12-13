# System-Wide MCP Server Setup Guide

## 🎯 Overview

This guide sets up MCP (Model Context Protocol) servers to run **system-wide** on your computer, making them accessible from any application, not just VS Code.

## 📋 Available Options

### 1. **Background PowerShell Jobs** (Recommended for Development)
- Lightweight, easy to manage
- Runs in current user session
- Perfect for development/testing

### 2. **Windows Service** (Recommended for Production)
- Runs as system service
- Starts automatically on boot
- Survives user logouts
- Requires Administrator privileges

### 3. **Task Scheduler Auto-Start**
- Starts when you log in
- User-level permissions
- Easy to configure

## 🚀 Quick Start Options

### Option A: Background Jobs (Simplest)

```powershell
# Start all servers
.\mcp-system-launcher.ps1 -Start

# Check status
.\mcp-system-launcher.ps1 -Status

# Stop servers
.\mcp-system-launcher.ps1 -Stop
```

### Option B: Windows Service (Most Robust)

```powershell
# Run as Administrator
.\mcp-service-installer.ps1 -Install
.\mcp-service-installer.ps1 -Start

# Check status
.\mcp-service-installer.ps1 -Status
```

### Option C: Task Scheduler (Auto-Start)

1. Open Task Scheduler
2. Create new task:
   - Name: "MCP Servers"
   - Trigger: "At log on"
   - Action: Start program
     - Program: `powershell.exe`
     - Arguments: `-ExecutionPolicy Bypass -File "C:\Drox_AI\mcp-startup.ps1"`
   - Run with highest privileges

## 🔧 Manual Commands

### Install Dependencies
```bash
npm install -g @modelcontextprotocol/server-filesystem mcp-server-code-runner chrome-devtools-mcp
```

### Start Individual Servers System-Wide

**Filesystem Server (Port 3001):**
```bash
Start-Process -NoNewWindow -FilePath "npx" -ArgumentList "-y", "@modelcontextprotocol/server-filesystem", "C:\Drox_AI"
```

**Code Runner Server (Port 3002):**
```bash
Start-Process -NoNewWindow -FilePath "npx" -ArgumentList "-y", "mcp-server-code-runner"
```

**Chrome DevTools Server (Port 3003):**
```bash
Start-Process -NoNewWindow -FilePath "npx" -ArgumentList "-y", "chrome-devtools-mcp"
```

## 🌐 Network Access

Once running, servers are accessible at:
- **Filesystem:** `http://localhost:3001` or `http://YOUR_IP:3001`
- **Code Runner:** `http://localhost:3002` or `http://YOUR_IP:3002`
- **Chrome DevTools:** `http://localhost:3003` or `http://YOUR_IP:3003`

### Allow External Access (Optional)
```powershell
# Allow through Windows Firewall
New-NetFirewallRule -DisplayName "MCP Filesystem" -Direction Inbound -Protocol TCP -LocalPort 3001 -Action Allow
New-NetFirewallRule -DisplayName "MCP Code Runner" -Direction Inbound -Protocol TCP -LocalPort 3002 -Action Allow
New-NetFirewallRule -DisplayName "MCP Chrome DevTools" -Direction Inbound -Protocol TCP -LocalPort 3003 -Action Allow
```

## 📊 Monitoring & Management

### Check Server Status
```powershell
# Background jobs
.\mcp-system-launcher.ps1 -Status

# Windows service
.\mcp-service-installer.ps1 -Status
```

### View Logs
```powershell
# Service logs
Get-Content .\mcp-service.log -Tail 20

# Individual server logs
Get-Content .\filesystem-server_out.log -Tail 10
Get-Content .\code-runner-server_error.log -Tail 10
```

### Restart Servers
```powershell
# Background jobs
.\mcp-system-launcher.ps1 -Restart

# Windows service
.\mcp-service-installer.ps1 -Stop
.\mcp-service-installer.ps1 -Start
```

## 🔧 Configuration

Edit `mcp-system-config.yaml` to customize:
- Server ports
- Allowed directories
- Security settings
- Logging options

## 🛠️ Troubleshooting

### Servers Won't Start
```powershell
# Check npm installation
npm --version
node --version

# Reinstall packages
npm install -g @modelcontextprotocol/server-filesystem mcp-server-code-runner chrome-devtools-mcp
```

### Port Conflicts
```powershell
# Find what's using ports
netstat -ano | findstr :3001
netstat -ano | findstr :3002
netstat -ano | findstr :3003

# Kill conflicting processes
Stop-Process -Id <PID>
```

### Permission Issues
```powershell
# Run as Administrator
Start-Process powershell -Verb RunAs -ArgumentList "-File .\mcp-system-launcher.ps1 -Start"
```

### Service Installation Issues
```powershell
# Check service status
Get-Service -Name "MCP-Servers"

# Remove and reinstall
.\mcp-service-installer.ps1 -Uninstall
.\mcp-service-installer.ps1 -Install
```

## 📁 Files Created

- `mcp-system-launcher.ps1` - Background job manager
- `mcp-service-installer.ps1` - Windows service installer
- `mcp-service-runner.ps1` - Service execution script
- `mcp-system-config.yaml` - System configuration
- `mcp-startup.ps1` - Auto-start script

## 🔗 Integration Examples

### Connect from Python
```python
import requests

# Filesystem operations
response = requests.post("http://localhost:3001/filesystem/list", json={"path": "/"})
print(response.json())

# Code execution
response = requests.post("http://localhost:3002/execute", json={"code": "print('Hello')", "language": "python"})
print(response.json())
```

### Connect from JavaScript/Node.js
```javascript
const fetch = require('node-fetch');

async function testMCP() {
    // Test filesystem server
    const fsResponse = await fetch('http://localhost:3001/filesystem/list', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: '/' })
    });
    console.log(await fsResponse.json());
}

testMCP();
```

## 🎯 Next Steps

1. **Choose your deployment method** (background jobs, service, or scheduled task)
2. **Configure security** if exposing to network
3. **Test connectivity** from different applications
4. **Set up monitoring** for production use
5. **Add more MCP servers** as needed

Your MCP servers are now running **system-wide** and accessible from any application on your computer! 🚀