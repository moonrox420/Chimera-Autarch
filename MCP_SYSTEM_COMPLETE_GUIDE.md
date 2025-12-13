# 🚀 MCP System - Complete Setup Guide

## What is This?

This is a **complete MCP (Model Context Protocol) ecosystem** that runs system-wide on your computer. It provides AI applications with access to:

- **File System Operations** - Read, write, search files and directories
- **Git Version Control** - Repository management, commits, branches
- **Code Execution** - Run Python, JavaScript, PowerShell code
- **Browser Automation** - Chrome DevTools, DOM manipulation, screenshots

## 🎯 Quick Start (3 Steps)

### Step 1: Install Dependencies
```bash
npm install -g @modelcontextprotocol/server-filesystem mcp-server-code-runner chrome-devtools-mcp
```

### Step 2: Start the Complete System
```powershell
# Start everything (Master Controller)
.\mcp-master-controller.ps1 -Start

# Or install as Windows Service (Recommended)
.\mcp-system-service.ps1 -Install
.\mcp-system-service.ps1 -Start
```

### Step 3: Test the System
```powershell
# Run comprehensive tests
.\test-mcp-system.ps1
```

## 📋 System Architecture

```
┌─────────────────┐    ┌──────────────────┐
│   Applications  │────│  MCP Router      │
│   (Any AI app)  │    │  (Port 9090)     │
└─────────────────┘    └──────────────────┘
                                │
                ┌───────────────┼───────────────┐
                │               │               │
        ┌───────▼──────┐ ┌──────▼──────┐ ┌─────▼─────┐
        │ Filesystem   │ │ Git Server  │ │ Code Runner│
        │ Server       │ │             │ │            │
        └──────────────┘ └─────────────┘ └────────────┘
                                                │
                                        ┌───────▼──────┐
                                        │ Chrome       │
                                        │ DevTools     │
                                        └─────────────┘
```

## 🛠️ Usage Examples

### PowerShell Integration
```powershell
# Import the client
Import-Module .\MCPClient.psm1

# Connect to MCP system
$client = Connect-MCPSystem

# Use filesystem
$files = $client.ListDirectory("C:\Projects")

# Execute code
$result = $client.ExecuteCode("print('Hello World')", "python")

# Git operations
$status = $client.GitStatus()
```

### Python Integration
```python
import socket
import json

def send_mcp_request(method, params=None):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('127.0.0.1', 9090))

    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params or {}
    }

    client.send(json.dumps(request).encode() + b'\n')
    response = client.recv(4096)
    client.close()

    return json.loads(response.decode())

# Example usage
servers = send_mcp_request("system.listServers")
print("Available servers:", servers['result']['servers'])
```

### JavaScript/Node.js Integration
```javascript
const net = require('net');

function sendMCPRequest(method, params = {}) {
    return new Promise((resolve, reject) => {
        const client = net.createConnection({ host: '127.0.0.1', port: 9090 });

        client.on('connect', () => {
            const request = {
                jsonrpc: '2.0',
                id: Date.now(),
                method: method,
                params: params
            };
            client.write(JSON.stringify(request) + '\n');
        });

        client.on('data', (data) => {
            try {
                const response = JSON.parse(data.toString());
                resolve(response);
                client.end();
            } catch (err) {
                reject(err);
            }
        });

        client.on('error', reject);
    });
}

// Usage
sendMCPRequest('system.listServers')
    .then(response => console.log('Servers:', response.result.servers))
    .catch(console.error);
```

## 🎛️ Management Commands

### System Control
```powershell
# Start complete system
.\mcp-master-controller.ps1 -Start

# Check status
.\mcp-master-controller.ps1 -Status

# Stop everything
.\mcp-master-controller.ps1 -Stop

# Restart system
.\mcp-master-controller.ps1 -Restart
```

### Service Management (Recommended)
```powershell
# Install as Windows service
.\mcp-system-service.ps1 -Install

# Start service
.\mcp-system-service.ps1 -Start

# Check service status
.\mcp-system-service.ps1 -Status

# Test functionality
.\mcp-system-service.ps1 -Test
```

### Background Jobs (Development)
```powershell
# Start background jobs
.\mcp-system-launcher.ps1 -Start

# Monitor status
.\mcp-system-launcher.ps1 -Status

# Stop background jobs
.\mcp-system-launcher.ps1 -Stop
```

## 🔧 Configuration

Edit `mcp-system-config.yaml` to customize:

```yaml
SYSTEM:
  host: "127.0.0.1"          # Bind address
  port: 9090                 # Router port
  log_level: "INFO"          # Logging level
  auto_start: true           # Auto-start on boot

SERVERS:
  filesystem:
    enabled: true
    capabilities: ["files", "directories", "read", "write"]
    priority: 1

  git:
    enabled: true
    capabilities: ["git", "version-control"]
    priority: 2

  # ... more servers
```

## 📊 Monitoring

### Real-time Status
```powershell
# System status
.\mcp-master-controller.ps1 -Status

# Service status
.\mcp-system-service.ps1 -Status
```

### Logs
- System logs: `mcp-system.log`
- Individual server logs: `pipes\*.log`
- Service logs: `mcp-service.log`

### Health Checks
```powershell
# Run full test suite
.\test-mcp-system.ps1

# Quick connection test
.\test-mcp-system.ps1 -Quick

# Performance test
.\test-mcp-system.ps1 -Full

# Stress test
.\test-mcp-system.ps1 -Stress
```

## 🔒 Security

The system includes:
- Localhost-only binding by default
- No authentication (add as needed)
- Configurable rate limiting
- Request size limits
- SSL support (configurable)

## 🚨 Troubleshooting

### Connection Issues
```powershell
# Test basic connectivity
Test-NetConnection -ComputerName localhost -Port 9090

# Check if services are running
.\mcp-master-controller.ps1 -Status
```

### Service Won't Start
```powershell
# Check Windows Event Viewer
# Look for "MCP-System" service errors

# Manual start with debug
.\mcp-system-service-runner.ps1
```

### Performance Issues
```powershell
# Run performance test
.\test-mcp-system.ps1 -Full

# Check resource usage
Get-Process | Where-Object { $_.Name -like "*node*" -or $_.Name -like "*mcp*" }
```

## 📁 Files Overview

| File | Purpose |
|------|---------|
| `mcp-master-controller.ps1` | Main system controller |
| `mcp-system-service.ps1` | Windows service manager |
| `mcp-system-service-runner.ps1` | Service execution script |
| `mcp-system-launcher.ps1` | Background job manager |
| `MCPClient.psm1` | PowerShell client SDK |
| `mcp-system-config.yaml` | System configuration |
| `test-mcp-system.ps1` | Comprehensive test suite |
| `launch_mcp_system.bat` | Quick batch launcher |

## 🎯 Integration Examples

### VS Code Extension
```json
{
  "mcp": {
    "servers": {
      "system": {
        "command": "nc",
        "args": ["localhost", "9090"],
        "env": {}
      }
    }
  }
}
```

### Custom Application
```python
class MCPSystemClient:
    def __init__(self, host='127.0.0.1', port=9090):
        self.host = host
        self.port = port
        self.sock = None

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))

    def call(self, method, params=None):
        request = {
            'jsonrpc': '2.0',
            'id': random.randint(1, 1000),
            'method': method,
            'params': params or {}
        }
        self.sock.send(json.dumps(request).encode() + b'\n')
        response = self.sock.recv(4096)
        return json.loads(response.decode())

# Usage
client = MCPSystemClient()
client.connect()
servers = client.call('system.listServers')
print("Available MCP servers:", servers['result']['servers'])
```

## 🚀 Advanced Features

- **Load Balancing** - Automatic distribution across servers
- **Health Monitoring** - Automatic restart on failures
- **Metrics Collection** - Performance monitoring
- **Auto-scaling** - Dynamic server management (future)
- **Backup & Recovery** - Automatic system backups

## 🎉 You're All Set!

Your computer now has a **complete MCP ecosystem** running system-wide. Any application can connect to `localhost:9090` and access powerful AI capabilities across files, git, code execution, and browser automation.

**Happy coding! 🤖✨**