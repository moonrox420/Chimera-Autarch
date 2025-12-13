# MCP System Client SDK
# PowerShell module for connecting to MCP system from any application

class MCPClient {
    [string]$Host
    [int]$Port
    [System.Net.Sockets.TcpClient]$Client
    [System.IO.StreamReader]$Reader
    [System.IO.StreamWriter]$Writer
    [int]$RequestId = 1

    MCPClient([string]$host = "127.0.0.1", [int]$port = 9090) {
        $this.Host = $host
        $this.Port = $port
    }

    [bool] Connect() {
        try {
            $this.Client = New-Object System.Net.Sockets.TcpClient
            $this.Client.Connect($this.Host, $this.Port)
            $stream = $this.Client.GetStream()
            $this.Reader = New-Object System.IO.StreamReader $stream
            $this.Writer = New-Object System.IO.StreamWriter $stream
            $this.Writer.AutoFlush = $true
            return $true
        } catch {
            Write-Error "Failed to connect to MCP system: $_"
            return $false
        }
    }

    [void] Disconnect() {
        if ($this.Client) {
            $this.Client.Close()
        }
    }

    [object] SendRequest([string]$method, [object]$params = $null) {
        $request = @{
            jsonrpc = "2.0"
            id = $this.RequestId++
            method = $method
            params = $params
        }

        $jsonRequest = $request | ConvertTo-Json -Depth 10
        $this.Writer.WriteLine($jsonRequest)

        # Read response
        $responseLine = $this.Reader.ReadLine()
        if ($responseLine) {
            return $responseLine | ConvertFrom-Json
        }

        return $null
    }

    [object] ListServers() {
        return $this.SendRequest("system.listServers")
    }

    [object] GetServerCapabilities([string]$serverName) {
        return $this.SendRequest("system.getServerCapabilities", @{ server = $serverName })
    }

    [object] ExecuteOnServer([string]$serverName, [string]$method, [object]$params = $null) {
        return $this.SendRequest("server.execute", @{
            server = $serverName
            method = $method
            params = $params
        })
    }

    # Filesystem operations
    [object] ListDirectory([string]$path) {
        return $this.ExecuteOnServer("filesystem", "list", @{ path = $path })
    }

    [object] ReadFile([string]$path) {
        return $this.ExecuteOnServer("filesystem", "read", @{ path = $path })
    }

    [object] WriteFile([string]$path, [string]$content) {
        return $this.ExecuteOnServer("filesystem", "write", @{
            path = $path
            content = $content
        })
    }

    # Git operations
    [object] GitStatus([string]$repoPath = ".") {
        return $this.ExecuteOnServer("git", "status", @{ repository = $repoPath })
    }

    [object] GitCommit([string]$message, [string]$repoPath = ".") {
        return $this.ExecuteOnServer("git", "commit", @{
            repository = $repoPath
            message = $message
        })
    }

    # Code execution
    [object] ExecuteCode([string]$code, [string]$language = "python") {
        return $this.ExecuteOnServer("code-runner", "execute", @{
            code = $code
            language = $language
        })
    }

    # Browser operations
    [object] GetPageSource([string]$url) {
        return $this.ExecuteOnServer("chrome-devtools", "getPageSource", @{ url = $url })
    }

    [object] TakeScreenshot([string]$url) {
        return $this.ExecuteOnServer("chrome-devtools", "screenshot", @{ url = $url })
    }
}

# Module functions
function New-MCPClient {
    param(
        [string]$Host = "127.0.0.1",
        [int]$Port = 9090
    )

    return [MCPClient]::new($Host, $Port)
}

function Connect-MCPSystem {
    param(
        [string]$Host = "127.0.0.1",
        [int]$Port = 9090
    )

    $client = New-MCPClient -Host $Host -Port $Port
    if ($client.Connect()) {
        Write-Host "Connected to MCP system at ${Host}:${Port}" -ForegroundColor Green
        return $client
    } else {
        Write-Error "Failed to connect to MCP system"
        return $null
    }
}

function Get-MCPSystemInfo {
    param([MCPClient]$Client)

    if (-not $Client) {
        Write-Error "No MCP client provided"
        return
    }

    $info = $Client.ListServers()
    Write-Host "MCP System Information:" -ForegroundColor Cyan
    Write-Host "=======================" -ForegroundColor Cyan
    Write-Host "Connected: Yes" -ForegroundColor Green
    Write-Host "Servers: $($info.result.servers -join ', ')" -ForegroundColor White
    Write-Host "Capabilities: $($info.result.capabilities -join ', ')" -ForegroundColor White
    Write-Host "Status: $($info.result.status)" -ForegroundColor $(if ($info.result.status -eq "active") { "Green" } else { "Red" })
}

# Export functions
Export-ModuleMember -Function New-MCPClient, Connect-MCPSystem, Get-MCPSystemInfo
Export-ModuleMember -Variable MCPClient