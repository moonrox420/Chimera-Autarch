#!/usr/bin/env python3
"""
DroxAI Core Engine - Consumer Version
Advanced AI Orchestration System with consumer-friendly configuration
"""
import asyncio
import json
import os
import sys
import time
import logging
import websockets
import traceback
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Optional, Dict, Any

# Add the app directory to Python path for imports
app_home = Path(__file__).parent.parent
sys.path.insert(0, str(app_home))

try:
    from droxai_config import ConfigManager, DroxAIConfig
except ImportError:
    print("[DroxAI] ERROR: Configuration module not found")
    sys.exit(1)

class ConsumerDroxAIEngine:
    """Consumer-friendly DroxAI engine with dynamic path resolution"""
    
    def __init__(self):
        self.config: Optional[DroxAIConfig] = None
        self.heart = None
        self.logger = None
        self.running = False
        
    async def initialize(self) -> bool:
        """Initialize the engine with consumer configuration"""
        try:
            # Load configuration
            self.config = ConfigManager.load_config()
            
            # Setup logging
            self._setup_logging()
            self.logger = logging.getLogger("droxai")
            
            # Initialize backend components
            if not await self._initialize_backend():
                return False
            
            self.running = True
            self.logger.info("[DroxAI] Engine initialized successfully")
            return True
            
        except Exception as e:
            print(f"[DroxAI] ERROR: Failed to initialize: {e}")
            traceback.print_exc()
            return False
    
    def _setup_logging(self) -> None:
        """Setup logging with consumer-friendly configuration"""
        log_config = self.config.logging
        
        # Ensure log directory exists
        log_config.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=getattr(logging, log_config.level.upper(), logging.INFO),
            format=log_config.format,
            datefmt=log_config.date_format,
            handlers=[
                logging.FileHandler(log_config.file_path) if log_config.file_enabled else logging.NullHandler(),
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    async def _initialize_backend(self) -> bool:
        """Initialize backend components"""
        try:
            # For consumer version, we'll create a simplified version
            # that uses the consumer config structure
            
            # Load additional modules if available
            self._load_optional_modules()
            
            self.logger.info("[DroxAI] Backend components initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"[DroxAI] Backend initialization failed: {e}")
            return False
    
    def _load_optional_modules(self) -> None:
        """Load optional backend modules if available"""
        # These are optional components that may not be available
        optional_modules = [
            'event_broker',
            'graphql_api',
            'neural_evolution',
            'quantum_optimizer'
        ]
        
        for module_name in optional_modules:
            try:
                module = __import__(module_name)
                self.logger.info(f"[DroxAI] Loaded optional module: {module_name}")
            except ImportError:
                self.logger.debug(f"[DroxAI] Optional module not available: {module_name}")
    
    async def start_services(self) -> bool:
        """Start the core services"""
        if not self.config:
            return False
        
        try:
            server_config = self.config.server
            
            # Start WebSocket server
            ws_server = await self._start_websocket_server(server_config)
            if not ws_server:
                return False
            
            # Start HTTP server
            http_server = await self._start_http_server(server_config)
            if not http_server:
                return False
            
            self.logger.info(f"[DroxAI] Services started on {server_config.http_host}:{server_config.http_port}")
            
            # Run both servers
            await asyncio.gather(
                ws_server.wait_closed(),
                asyncio.to_thread(http_server.serve_forever)
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"[DroxAI] Service startup failed: {e}")
            return False
    
    async def _start_websocket_server(self, server_config) -> Optional[object]:
        """Start WebSocket server"""
        try:
            async def websocket_handler(ws, path):
                await self._handle_websocket_message(ws, path)
            
            ws_server = await websockets.serve(
                websocket_handler,
                server_config.websocket_host,
                server_config.websocket_port
            )
            
            self.logger.info(f"[DroxAI] WebSocket server started on {server_config.websocket_host}:{server_config.websocket_port}")
            return ws_server
            
        except Exception as e:
            self.logger.error(f"[DroxAI] WebSocket server failed: {e}")
            return None
    
    async def _start_http_server(self, server_config) -> Optional[HTTPServer]:
        """Start HTTP server with consumer dashboard"""
        try:
            handler = lambda *a, **kw: ConsumerHTTPRequestHandler(self, *a, **kw)
            http_server = HTTPServer((server_config.http_host, server_config.http_port), handler)
            
            # Start server in background
            asyncio.create_task(self._run_http_server(http_server))
            
            self.logger.info(f"[DroxAI] HTTP server started on {server_config.http_host}:{server_config.http_port}")
            return http_server
            
        except Exception as e:
            self.logger.error(f"[DroxAI] HTTP server failed: {e}")
            return None
    
    async def _run_http_server(self, http_server: HTTPServer) -> None:
        """Run HTTP server"""
        try:
            http_server.serve_forever()
        except Exception as e:
            self.logger.error(f"[DroxAI] HTTP server error: {e}")
        finally:
            http_server.server_close()
    
    async def _handle_websocket_message(self, ws, path):
        """Handle WebSocket messages"""
        try:
            await ws.send(json.dumps({"type": "welcome", "version": "1.0.0"}))
            
            async for message in ws:
                data = json.loads(message)
                await self._process_websocket_data(ws, data)
                
        except Exception as e:
            self.logger.error(f"[DroxAI] WebSocket error: {e}")
    
    async def _process_websocket_data(self, ws, data):
        """Process incoming WebSocket data"""
        msg_type = data.get("type", "")
        
        if msg_type == "ping":
            await ws.send(json.dumps({"type": "pong", "timestamp": time.time()}))
        
        elif msg_type == "status":
            await self._send_status_update(ws)
        
        elif msg_type == "echo":
            message = data.get("message", "")
            await ws.send(json.dumps({"type": "echo", "message": f"Echo: {message}"}))
        
        else:
            await ws.send(json.dumps({"type": "error", "message": f"Unknown message type: {msg_type}"}))
    
    async def _send_status_update(self, ws):
        """Send system status to client"""
        status = {
            "type": "status",
            "data": {
                "version": "1.0.0",
                "status": "running",
                "uptime": time.time() - (getattr(self, 'start_time', time.time())),
                "config": {
                    "http_port": self.config.server.http_port,
                    "websocket_port": self.config.server.websocket_port
                }
            }
        }
        
        await ws.send(json.dumps(status))
    
    async def run(self) -> None:
        """Main run loop"""
        self.start_time = time.time()
        
        try:
            if not await self.initialize():
                return
            
            await self.start_services()
            
        except KeyboardInterrupt:
            self.logger.info("[DroxAI] Shutdown requested by user")
        except Exception as e:
            self.logger.error(f"[DroxAI] Fatal error: {e}")
            traceback.print_exc()
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """Clean shutdown"""
        self.running = False
        if self.logger:
            self.logger.info("[DroxAI] Shutdown complete")

class ConsumerHTTPRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for consumer dashboard"""
    
    def __init__(self, engine, *args, **kwargs):
        self.engine = engine
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == "/" or self.path == "/dashboard":
            self._serve_dashboard()
        elif self.path == "/api/status":
            self._serve_status()
        elif self.path == "/favicon.ico":
            self._serve_favicon()
        else:
            self.send_error(404)
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == "/api/command":
            self._handle_command()
        else:
            self.send_error(404)
    
    def _serve_dashboard(self):
        """Serve consumer dashboard"""
        html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DroxAI v1.0.0 - System Dashboard</title>
    <style>
        :root { --primary: #00ffcc; --bg-dark: #0a0a12; --card-bg: #151522; }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: var(--bg-dark);
            color: var(--primary);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            padding: 20px;
            background-image:
                radial-gradient(var(--primary) 1px, transparent 1px);
            background-size: 40px 40px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        header {
            text-align: center;
            padding: 30px 0;
            border-bottom: 2px solid var(--primary);
            margin-bottom: 30px;
        }
        h1 {
            font-size: 2.5em;
            text-shadow: 0 0 10px rgba(0, 255, 204, 0.3);
            margin-bottom: 10px;
        }
        .subtitle {
            color: #8892b0;
            font-size: 1.1em;
        }
        .dashboard {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }
        .card {
            background: var(--card-bg);
            border: 1px solid var(--primary);
            border-radius: 10px;
            padding: 25px;
        }
        .card h2 {
            color: var(--primary);
            margin-bottom: 20px;
            font-size: 1.3em;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .status-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }
        .status-item {
            background: rgba(0, 0, 0, 0.3);
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }
        .status-value {
            font-size: 2em;
            font-weight: bold;
            color: var(--primary);
        }
        .status-label {
            color: #8892b0;
            font-size: 0.9em;
            margin-top: 5px;
        }
        .controls {
            display: flex;
            gap: 15px;
            margin-top: 20px;
        }
        .btn {
            background: var(--primary);
            color: var(--bg-dark);
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 255, 204, 0.3);
        }
        .btn-secondary {
            background: transparent;
            color: var(--primary);
            border: 1px solid var(--primary);
        }
        .footer {
            text-align: center;
            margin-top: 30px;
            padding: 20px;
            color: #8892b0;
        }
        @media (max-width: 768px) {
            .dashboard { grid-template-columns: 1fr; }
            .status-grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>ðŸš€ DroxAI v1.0.0</h1>
            <div class="subtitle">Advanced AI Orchestration System</div>
        </header>
        
        <div class="dashboard">
            <div class="card">
                <h2>ðŸ“Š System Status</h2>
                <div class="status-grid">
                    <div class="status-item">
                        <div class="status-value" id="uptime">--</div>
                        <div class="status-label">Uptime (seconds)</div>
                    </div>
                    <div class="status-item">
                        <div class="status-value" id="status">Online</div>
                        <div class="status-label">System Status</div>
                    </div>
                </div>
                <div class="controls">
                    <button class="btn" onclick="refreshStatus()">Refresh Status</button>
                    <button class="btn btn-secondary" onclick="testConnection()">Test Connection</button>
                </div>
            </div>
            
            <div class="card">
                <h2>ðŸ”Œ Connection Info</h2>
                <div class="status-grid">
                    <div class="status-item">
                        <div class="status-value" id="http-port">3000</div>
                        <div class="status-label">HTTP Port</div>
                    </div>
                    <div class="status-item">
                        <div class="status-value" id="ws-port">3001</div>
                        <div class="status-label">WebSocket Port</div>
                    </div>
                </div>
                <div class="controls">
                    <button class="btn" onclick="openWebSocket()">Open WebSocket</button>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2>âš¡ Quick Actions</h2>
            <div class="controls">
                <button class="btn" onclick="sendEcho()">Send Echo Test</button>
                <button class="btn btn-secondary" onclick="checkHealth()">Health Check</button>
                <button class="btn btn-secondary" onclick="viewLogs()">View Logs</button>
            </div>
        </div>
        
        <div class="footer">
            <p>Â© 2025 DroxAI - Advanced AI Orchestration System</p>
            <p>Built with consumer-friendly packaging and dynamic configuration</p>
        </div>
    </div>
    
    <script>
        function refreshStatus() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('uptime').textContent = Math.floor(data.uptime);
                    document.getElementById('status').textContent = 'Online';
                })
                .catch(error => {
                    document.getElementById('status').textContent = 'Offline';
                });
        }
        
        function testConnection() {
            const ws = new WebSocket('ws://localhost:3001');
            ws.onopen = function() {
                ws.send(JSON.stringify({type: 'ping'}));
            };
            ws.onmessage = function(event) {
                alert('Connection test successful: ' + event.data);
                ws.close();
            };
            ws.onerror = function() {
                alert('Connection test failed');
            };
        }
        
        function sendEcho() {
            const message = prompt('Enter message to echo:');
            if (message) {
                const ws = new WebSocket('ws://localhost:3001');
                ws.onopen = function() {
                    ws.send(JSON.stringify({type: 'echo', message: message}));
                };
                ws.onmessage = function(event) {
                    alert('Echo response: ' + event.data);
                    ws.close();
                };
            }
        }
        
        function checkHealth() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    alert('Health check passed! System is running normally.');
                })
                .catch(error => {
                    alert('Health check failed: ' + error.message);
                });
        }
        
        function viewLogs() {
            window.open('/logs', '_blank');
        }
        
        function openWebSocket() {
            window.open('ws://localhost:3001', '_blank');
        }
        
        // Auto-refresh status every 5 seconds
        setInterval(refreshStatus, 5000);
        
        // Initial load
        refreshStatus();
    </script>
</body>
</html>'''
        
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())
    
    def _serve_status(self):
        """Serve JSON status"""
        if not self.engine.config:
            self.send_error(500)
            return
        
        status = {
            "status": "running",
            "version": "1.0.0",
            "uptime": time.time() - getattr(self.engine, 'start_time', time.time()),
            "config": {
                "http_port": self.engine.config.server.http_port,
                "websocket_port": self.engine.config.server.websocket_port
            }
        }
        
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(status).encode())
    
    def _serve_favicon(self):
        """Serve favicon"""
        self.send_response(204)
        self.end_headers()
    
    def _handle_command(self):
        """Handle POST command"""
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        
        try:
            data = json.loads(body.decode('utf-8'))
            command = data.get('command', '')
            
            if command == 'restart':
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "restarting"}).encode())
                # In a real implementation, this would trigger a restart
            else:
                self.send_error(400)
        except Exception:
            self.send_error(400)
    
    def log_message(self, format, *args):
        """Override to use engine logger"""
        if self.engine and self.engine.logger:
            self.engine.logger.info(format % args)

async def main():
    """Main entry point"""
    print("=" * 60)
    print("    DroxAI Core v1.0.0")
    print("    Consumer Edition - Advanced AI Orchestration")
    print("=" * 60)
    
    try:
        engine = ConsumerDroxAIEngine()
        await engine.run()
    except KeyboardInterrupt:
        print("\n[DroxAI] Shutdown requested")
    except Exception as e:
        print(f"[DroxAI] Fatal error: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

