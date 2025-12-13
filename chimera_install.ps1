# chimera_install.ps1 - Chimera God CLI Auto Installer
#Requires -RunAsAdministrator

Write-Host "Chimera God CLI - Auto Installer" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan

$InstallPath = "$env:USERPROFILE\ChimeraGodCLI"

# Check Docker
Write-Host "[1/7] Checking Docker..." -ForegroundColor Yellow
if (!(Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "Installing Docker Desktop..." -ForegroundColor Red
    winget install Docker.DockerDesktop --silent --accept-package-agreements
    Write-Host "Docker installed. Please restart and re-run." -ForegroundColor Green
    exit
}
Write-Host "âœ“ Docker found" -ForegroundColor Green

# Check Python
Write-Host "[2/7] Checking Python..." -ForegroundColor Yellow
if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Installing Python 3.11..." -ForegroundColor Red
    winget install Python.Python.3.11 --silent --accept-package-agreements
}
Write-Host "âœ“ Python found" -ForegroundColor Green

# Create directory
Write-Host "[3/7] Creating project structure..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path $InstallPath | Out-Null
Set-Location $InstallPath
Write-Host "âœ“ Directory created: $InstallPath" -ForegroundColor Green

# Create DroxAI_Core.py
Write-Host "[4/7] Creating backend..." -ForegroundColor Yellow
@'
import os
import json
import time
import asyncio
import logging
import threading
import webbrowser
import websockets
from http.server import HTTPServer, BaseHTTPRequestHandler

os.environ["HTTP_HOST"] = "127.0.0.1"
os.environ["HTTP_PORT"] = "3000"
os.environ["WS_HOST"] = "127.0.0.1"
os.environ["WS_PORT"] = "3000"

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")
log = logging.getLogger("droxai")

log.info("DroxAI Core v1.0.0 - Fortress Edition")

DASHBOARD_HTML = open('dashboard.html', 'r', encoding='utf-8').read()

class UIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", "/dashboard"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(DASHBOARD_HTML.encode())
        elif self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status":"ok"}')
        else:
            self.send_response(404)
            self.end_headers()
    def log_message(self, format, *args):
        pass

async def ws_handler(websocket):
    async for message in websocket:
        await websocket.send(f"echo: {message}")

async def ws_main():
    async with websockets.serve(ws_handler, "127.0.0.1", 3000):
        log.info("WebSocket live on 127.0.0.1:3000")
        await asyncio.Future()

threading.Thread(target=HTTPServer(("127.0.0.1", 3000), UIHandler).serve_forever, daemon=True).start()
log.info("Dashboard live -> http://127.0.0.1:3000")

asyncio.run(ws_main())
'@ | Out-File -FilePath "DroxAI_Core.py" -Encoding UTF8
Write-Host "âœ“ Backend created" -ForegroundColor Green

# Download dashboard
Write-Host "[5/7] Downloading dashboard UI..." -ForegroundColor Yellow
Invoke-WebRequest -Uri "https://ppl-ai-code-interpreter-files.s3.amazonaws.com/web/direct-files/968dcc553f0161431d00dec5506d450a/fdfefc30-efc8-43a6-b468-5255460984fa/canvas-app/index.html" -OutFile "dashboard.html"
Write-Host "âœ“ Dashboard downloaded" -ForegroundColor Green

# Create Docker files
Write-Host "[6/7] Creating Docker configuration..." -ForegroundColor Yellow

# Dockerfile
@'
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 3000 3000
CMD ["python", "DroxAI_Core.py"]
'@ | Out-File -FilePath "Dockerfile" -Encoding UTF8

# requirements.txt
@'
websockets==12.0
'@ | Out-File -FilePath "requirements.txt" -Encoding UTF8

# docker-compose.yml
@'
version: '3.8'
services:
  chimera-fortress:
    build: .
    container_name: chimera-fortress
    ports:
      - "3000:3000"
      - "3000:3000"
    restart: unless-stopped
'@ | Out-File -FilePath "docker-compose.yml" -Encoding UTF8

Write-Host "âœ“ Docker config created" -ForegroundColor Green

# Deploy
Write-Host "[7/7] Deploying fortress..." -ForegroundColor Yellow
docker compose up -d --build

Write-Host ""
Write-Host "================================================================" -ForegroundColor Green
Write-Host "Installation completed successfully" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Installation Path: $InstallPath" -ForegroundColor Cyan
Write-Host "Dashboard URL: http://127.0.0.1:3000" -ForegroundColor Cyan
Write-Host ""

Start-Sleep -Seconds 8
Start-Process "http://127.0.0.1:3000"

Write-Host "System operational" -ForegroundColor Cyan
