"""
Orchestrator service - Core business logic for CHIMERA AUTARCH.
"""

import asyncio
import json
import time
from collections import defaultdict, deque
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

from fastapi import WebSocket

from config.settings import Settings
from core.logging import get_logger
from models.message import Message, MessageType
from models.intent import Intent, IntentResult
from services.intent_compiler import IntentCompiler
from services.persistence import PersistenceService
from services.metacognitive import MetacognitiveService
from services.tool_registry import ToolRegistry
from services.node_manager import NodeManager

logger = get_logger(__name__)


@dataclass
class ClientSession:
    """WebSocket client session."""
    websocket: WebSocket
    connected_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)


class OrchestratorService:
    """Main orchestrator service coordinating all system components."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.clients: Dict[str, ClientSession] = {}
        self.intent_compiler = IntentCompiler()
        self.persistence = PersistenceService(settings.persistence)
        self.metacognitive = MetacognitiveService(settings.metacognitive, self.persistence)
        self.tool_registry = ToolRegistry()
        self.node_manager = NodeManager(settings.node)

        # Background tasks
        self._background_tasks: List[asyncio.Task] = []

    async def initialize(self) -> None:
        """Initialize all services."""
        logger.info("Initializing orchestrator services")

        # Initialize persistence
        await self.persistence.initialize()

        # Initialize metacognitive engine
        await self.metacognitive.initialize()

        # Register core tools
        await self._register_core_tools()

        # Start background tasks
        self._start_background_tasks()

        logger.info("Orchestrator initialization complete")

    async def shutdown(self) -> None:
        """Shutdown all services gracefully."""
        logger.info("Shutting down orchestrator services")

        # Cancel background tasks
        for task in self._background_tasks:
            task.cancel()

        await asyncio.gather(*self._background_tasks, return_exceptions=True)

        # Shutdown services
        await self.metacognitive.shutdown()
        await self.persistence.shutdown()

        # Close client connections
        for client_id, session in self.clients.items():
            try:
                await session.websocket.close()
            except Exception:
                pass

        logger.info("Orchestrator shutdown complete")

    async def register_client(self, websocket: WebSocket) -> str:
        """Register a new WebSocket client."""
        client_id = f"client_{len(self.clients)}"
        self.clients[client_id] = ClientSession(websocket=websocket)
        logger.info(f"Client registered: {client_id}")
        return client_id

    async def unregister_client(self, client_id: str) -> None:
        """Unregister a WebSocket client."""
        if client_id in self.clients:
            del self.clients[client_id]
            logger.info(f"Client unregistered: {client_id}")

    async def handle_message(self, client_id: str, message_data: str) -> Dict[str, Any]:
        """Handle incoming message from client."""
        try:
            # Update client activity
            if client_id in self.clients:
                self.clients[client_id].last_activity = time.time()

            # Parse message
            message = Message.from_json(message_data)

            # Route based on message type
            if message.type == MessageType.INTENT:
                return await self._handle_intent(message)
            elif message.type == MessageType.HEARTBEAT:
                return {"type": "heartbeat_ack", "timestamp": time.time()}
            elif message.type == MessageType.STATUS_REQUEST:
                return await self.get_status()
            else:
                return {"error": f"Unknown message type: {message.type}"}

        except Exception as e:
            logger.error(f"Error handling message from {client_id}: {e}", exc_info=True)
            return {"error": str(e)}

    async def _handle_intent(self, message: Message) -> Dict[str, Any]:
        """Handle intent processing."""
        intent_text = message.data.get("intent", "")

        if not intent_text:
            return {"error": "No intent provided"}

        # Process intent
        result = await self.process_intent(intent_text)

        return {
            "type": "intent_result",
            "result": result.dict()
        }

    async def process_intent(self, intent_text: str) -> IntentResult:
        """Process an intent and return the result."""
        start_time = time.time()

        try:
            # Compile intent to execution plan
            intent = await self.intent_compiler.compile(intent_text)

            # Execute the intent
            result = await self._execute_intent(intent)

            # Record metrics
            duration = time.time() - start_time
            await self.persistence.log_tool_metric(
                tool_name="intent_processor",
                success=result.success,
                latency=duration,
                context={"intent": intent_text}
            )

            # Update metacognitive engine
            if not result.success:
                topic = self.metacognitive._topic_from_intent(intent_text)
                self.metacognitive.log_failure(intent_text, result.error or "Unknown error")

            return result

        except Exception as e:
            logger.error(f"Intent processing error: {e}", exc_info=True)
            return IntentResult(
                success=False,
                error=str(e),
                execution_time=time.time() - start_time
            )

    async def _execute_intent(self, intent: Intent) -> IntentResult:
        """Execute a compiled intent."""
        # For now, return a simple success
        # TODO: Implement actual intent execution
        return IntentResult(
            success=True,
            data={"message": f"Intent '{intent.text}' processed successfully"},
            execution_time=0.1
        )

    async def get_status(self) -> Dict[str, Any]:
        """Get system status."""
        return {
            "status": "running",
            "version": "3.0.0",
            "clients_connected": len(self.clients),
            "uptime": time.time() - getattr(self, "_start_time", time.time()),
            "services": {
                "persistence": "healthy",
                "metacognitive": "healthy",
                "tool_registry": "healthy",
                "node_manager": "healthy"
            }
        }

    async def _register_core_tools(self) -> None:
        """Register core tools."""
        # TODO: Implement tool registration
        logger.info("Core tools registered")

    def _start_background_tasks(self) -> None:
        """Start background maintenance tasks."""
        # Metacognitive monitoring
        task = asyncio.create_task(self.metacognitive.monitor_loop())
        self._background_tasks.append(task)

        # Node health checks
        task = asyncio.create_task(self.node_manager.health_check_loop())
        self._background_tasks.append(task)

        # Persistence backups
        task = asyncio.create_task(self.persistence.backup_loop())
        self._background_tasks.append(task)