import json
import asyncio
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Optional, Any, Dict
import os

logger = logging.getLogger("chimera.web")


# Dashboard HTML Template
DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>CHIMERA AUTARCH v3</title>
<style>
    :root{--primary:#00ffcc;--bg:#0a0a12;--card-bg:rgba(20,25,40,0.95);}
    body{font-family:Consolas,Menlo,monospace;background:var(--bg);color:#e0e0e0;margin:0;}
    .container{max-width:1600px;margin:0 auto;padding:20px;}
    header{display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid var(--primary);padding-bottom:15px;margin-bottom:25px;}
    h1{font-size:2.5em;margin:0;text-shadow:0 0 12px rgba(0,255,204,.4);}
    .status-indicator{width:16px;height:16px;background:#0f0;border-radius:50%;display:inline-block;animation:pulse 2s infinite;}
    @keyframes pulse{0%,100%{opacity:1}50%{opacity:.4}}
    .dashboard{display:grid;grid-template-columns:1fr 380px;gap:25px;}
    .main-panel{background:var(--card-bg);border:1px solid var(--primary);border-radius:10px;padding:20px;height:76vh;}
    .terminal{background:#0004;padding:15px;border-radius:8px;height:100%;overflow-y:auto;font-family:inherit;}
    #output{min-height:100%;white-space:pre-wrap;}
    .input-area{display:flex;margin-top:12px;gap:10px;}
    input{flex:1;background:#111;border:1px solid var(--primary);color:var(--primary);padding:12px;border-radius:6px;}
    button{background:var(--primary);color:#000;border:none;padding:12px 20px;border-radius:6px;cursor:pointer;font-weight:bold;}
    button:hover{transform:translateY(-2px);box-shadow:0 6px 12px rgba(0,255,204,.3);}
    .sidebar{display:flex;flex-direction:column;gap:20px;}
    .card{background:var(--card-bg);border:1px solid var(--primary);border-radius:10px;padding:20px;}
    .card h2{color:var(--primary);display:flex;align-items:center;gap:10px;}
    .metric-grid{display:grid;grid-template-columns:1fr 1fr;gap:15px;}
    .metric{background:#1114;padding:14px;border-radius:6px;text-align:center;}
    .metric-value{font-size:2em;font-weight:bold;color:var(--primary);}
    .confidence-bar{height:8px;background:#333;border-radius:4px;overflow:hidden;margin-top:6px;}
    .confidence-fill{height:100%;background:var(--primary);transition:width .6s;}
</style>
</head>
<body>
<div class="container">
    <header>
        <div><span class="status-indicator"></span><h1>CHIMERA AUTARCH v3</h1></div>
        <div>SYSTEM OPERATIONAL</div>
    </header>
    <div class="dashboard">
        <div class="main-panel">
            <div class="terminal"><div id="output"></div></div>
            <div class="input-area">
                <input type="text" id="cmd" placeholder="enter intent…" autocomplete="off">
                <button onclick="send()">EXECUTE</button>
            </div>
        </div>
        <div class="sidebar">
            <div class="card">
                <h2>⚡ METRICS</h2>
                <div class="metric-grid">
                    <div class="metric"><div class="metric-label">Nodes</div><div class="metric-value" id="nodes">0</div></div>
                    <div class="metric"><div class="metric-label">Confidence</div><div class="metric-value" id="conf">100%</div></div>
                </div>
            </div>
        </div>
    </div>
</div>
<script>
    const ws = new WebSocket(`ws://${location.hostname}:3001`);
    const out = document.getElementById('output');
    const inp = document.getElementById('cmd');
    function log(m){const d=document.createElement('div');d.textContent=m;out.appendChild(d);out.scrollTop=out.scrollHeight;}
    ws.onopen = () => log('[SYSTEM] Connected');
    ws.onmessage = e => log(`> ${e.data}`);
    function send(){if(!inp.value.trim())return;ws.send(JSON.stringify({type:'intent',intent:inp.value}));log(`$ ${inp.value}`);inp.value='';}
    inp.addEventListener('keypress',e=>{if(e.key==='Enter')send();});
</script>
</body>
</html>"""


class DashboardHandler(BaseHTTPRequestHandler):
    """HTTP handler for the CHIMERA dashboard"""

    def __init__(self, heart_node, *args, **kwargs):
        self.heart_node = heart_node
        super().__init__(*args, **kwargs)

    def do_GET(self):
        """Handle GET requests"""
        if self.path in {"", "/"}:
            self._serve_dashboard()
        elif self.path == "/graphql":
            self._serve_graphql_playground()
        elif self.path == "/metrics":
            self._serve_metrics()
        else:
            self.send_error(404)

    def do_POST(self):
        """Handle POST requests"""
        if self.path == "/graphql":
            self._handle_graphql()
        else:
            self.send_error(404)

    def _serve_dashboard(self):
        """Serve the main dashboard HTML"""
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(DASHBOARD_HTML.encode())

    def _serve_graphql_playground(self):
        """Serve GraphQL playground interface"""
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()

        playground_html = """<!DOCTYPE html>
<html>
<head>
    <title>GraphQL Playground</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/graphql-playground-react/build/static/css/index.css" />
    <link rel="shortcut icon" href="https://cdn.jsdelivr.net/npm/graphql-playground-react/build/favicon.png" />
    <script src="https://cdn.jsdelivr.net/npm/graphql-playground-react/build/static/js/middleware.js"></script>
</head>
<body>
    <div id="root"></div>
    <script src="https://cdn.jsdelivr.net/npm/graphql-playground-react/build/static/js/index.js"></script>
</body>
</html>"""

        self.wfile.write(playground_html.encode())

    def _serve_metrics(self):
        """Serve system metrics as JSON"""
        try:
            metrics = self.heart_node.get_system_metrics()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(metrics).encode())
        except Exception as e:
            logger.error(f"Metrics endpoint error: {e}")
            self.send_error(500, str(e))

    def _handle_graphql(self):
        """Handle GraphQL queries"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())

            query = data.get("query", "")
            variables = data.get("variables", {})

            # Run GraphQL query synchronously
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(
                    self.heart_node.graphql_resolver.resolve(query, variables)
                )
            finally:
                loop.close()

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())

        except Exception as e:
            logger.error(f"GraphQL error: {e}")
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"errors": [{"message": str(e)}]}).encode())


def create_dashboard_handler(heart_node):
    """Factory function to create dashboard handler with heart node reference"""
    class HandlerWithHeart(DashboardHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(heart_node, *args, **kwargs)
    return HandlerWithHeart


class WebInterface:
    """Web interface manager for HTTP and WebSocket servers"""

    def __init__(self, heart_node):
        self.heart_node = heart_node
        self.http_server = None
        self.ws_server = None
        self.http_port = int(os.getenv("HTTP_PORT", 3000))
        self.ws_port = int(os.getenv("WS_PORT", 3001))

    async def start_servers(self):
        """Start HTTP and WebSocket servers"""
        import websockets
        import ssl
        from pathlib import Path

        # TLS auto-detect
        ssl_ctx = None
        for base in ["ssl/", ""]:
            if Path(base + "cert.pem").exists() and Path(base + "key.pem").exists():
                ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                ssl_ctx.load_cert_chain(base + "cert.pem", base + "key.pem")
                logger.info(f"[TLS] Loaded certificates from {base}")
                break

        # WebSocket handler
        async def ws_handler(ws):
            await ws.send(json.dumps({"type": "welcome"}))
            async for msg in ws:
                await self.heart_node.handle_message(ws, msg)

        # Start WebSocket server
        self.ws_server = await websockets.serve(
            ws_handler,
            "127.0.0.1",
            self.ws_port,
            ssl=ssl_ctx,
        )

        # Start HTTP server
        handler_class = create_dashboard_handler(self.heart_node)
        self.http_server = HTTPServer(("127.0.0.1", self.http_port), handler_class)

        # Run HTTP server in thread
        import threading
        http_thread = threading.Thread(target=self.http_server.serve_forever, daemon=True)
        http_thread.start()

        logger.info(f"[WEB] Servers started - WS: ws://127.0.0.1:{self.ws_port}, HTTP: http://127.0.0.1:{self.http_port}")

    async def stop_servers(self):
        """Stop HTTP and WebSocket servers"""
        if self.http_server:
            self.http_server.shutdown()
            logger.info("[WEB] HTTP server stopped")

        if self.ws_server:
            self.ws_server.close()
            await self.ws_server.wait_closed()
            logger.info("[WEB] WebSocket server stopped")