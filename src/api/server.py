"""
FastAPI server for CHIMERA AUTARCH.

Provides HTTP API, WebSocket endpoints, and web dashboard.
"""

import asyncio
import json
import ssl
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

import uvicorn
import websockets
from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from config.settings import Settings
from core.logging import get_logger
from services.orchestrator import OrchestratorService

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting CHIMERA AUTARCH server")

    # Initialize services
    app.state.orchestrator = OrchestratorService(app.state.settings)
    await app.state.orchestrator.initialize()

    yield

    # Shutdown
    logger.info("Shutting down CHIMERA AUTARCH server")
    await app.state.orchestrator.shutdown()


def create_app(settings: Settings) -> FastAPI:
    """Create FastAPI application."""
    app = FastAPI(
        title="CHIMERA AUTARCH",
        description="Self-evolving AI orchestration system",
        version="3.0.0",
        lifespan=lifespan
    )

    # Store settings in app state
    app.state.settings = settings

    # Mount static files if directory exists
    static_dir = Path("web/static")
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    # Setup templates
    templates_dir = Path("web/templates")
    if templates_dir.exists():
        templates = Jinja2Templates(directory=str(templates_dir))

        @app.get("/", response_class=HTMLResponse)
        async def dashboard(request: Request):
            """Serve the web dashboard."""
            return templates.TemplateResponse("dashboard.html", {"request": request})
    else:
        @app.get("/", response_class=JSONResponse)
        async def dashboard():
            """API info when no dashboard available."""
            return {
                "message": "CHIMERA AUTARCH API",
                "version": "3.0.0",
                "docs": "/docs",
                "health": "/api/health"
            }

    @app.get("/api/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "version": "3.0.0"}

    @app.get("/api/status")
    async def system_status():
        """Get system status."""
        orchestrator: OrchestratorService = app.state.orchestrator
        return await orchestrator.get_status()

    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        """WebSocket endpoint for real-time communication."""
        await websocket.accept()

        orchestrator: OrchestratorService = app.state.orchestrator
        client_id = await orchestrator.register_client(websocket)

        try:
            while True:
                data = await websocket.receive_text()
                response = await orchestrator.handle_message(client_id, data)
                await websocket.send_text(json.dumps(response))
        except Exception as e:
            logger.error(f"WebSocket error for client {client_id}: {e}")
        finally:
            await orchestrator.unregister_client(client_id)

    @app.post("/api/intent")
    async def process_intent(request: Request):
        """Process an intent via HTTP."""
        data = await request.json()
        intent = data.get("intent", "")

        orchestrator: OrchestratorService = app.state.orchestrator
        result = await orchestrator.process_intent(intent)

        return JSONResponse(content=result)

    return app


async def run_server(settings: Settings) -> None:
    """Run the FastAPI server with WebSocket support."""
    app = create_app(settings)

    # SSL configuration
    ssl_config = None
    if settings.server.ssl_enabled:
        cert_path = Path(settings.server.ssl_cert_path or "ssl/cert.pem")
        key_path = Path(settings.server.ssl_key_path or "ssl/key.pem")

        if cert_path.exists() and key_path.exists():
            ssl_config = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ssl_config.load_cert_chain(str(cert_path), str(key_path))
            logger.info(f"SSL enabled with cert: {cert_path}")
        else:
            logger.warning("SSL enabled but certificates not found")

    # Start server
    config = uvicorn.Config(
        app,
        host=settings.server.http_host,
        port=settings.server.http_port,
        ssl_keyfile=settings.server.ssl_key_path if ssl_config else None,
        ssl_certfile=settings.server.ssl_cert_path if ssl_config else None,
        log_level=settings.logging.level.lower(),
    )

    server = uvicorn.Server(config)

    logger.info(f"Starting server on {settings.server.http_host}:{settings.server.http_port}")
    if ssl_config:
        logger.info("SSL/TLS enabled")

    await server.serve()
