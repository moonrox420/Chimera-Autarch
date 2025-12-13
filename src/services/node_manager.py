"""
Node manager service for distributed nodes.
"""

import asyncio
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

from config.settings import NodeSettings
from core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class NodeInfo:
    """Information about a connected node."""
    node_id: str
    connected_at: float = field(default_factory=time.time)
    last_heartbeat: float = field(default_factory=time.time)
    reputation: float = 1.0
    resources: Dict[str, Any] = field(default_factory=dict)
    status: str = "active"


class NodeManager:
    """Manages distributed nodes."""

    def __init__(self, settings: NodeSettings):
        self.settings = settings
        self.nodes: Dict[str, NodeInfo] = {}

    async def register_node(self, node_id: str, resources: Dict[str, Any]) -> None:
        """Register a new node."""
        self.nodes[node_id] = NodeInfo(
            node_id=node_id,
            resources=resources
        )
        logger.info(f"Node registered: {node_id}")

    async def unregister_node(self, node_id: str) -> None:
        """Unregister a node."""
        if node_id in self.nodes:
            del self.nodes[node_id]
            logger.info(f"Node unregistered: {node_id}")

    async def update_heartbeat(self, node_id: str) -> None:
        """Update node heartbeat."""
        if node_id in self.nodes:
            self.nodes[node_id].last_heartbeat = time.time()

    async def health_check_loop(self) -> None:
        """Background health check loop."""
        while True:
            try:
                await asyncio.sleep(self.settings.heartbeat_interval)
                await self._check_node_health()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check error: {e}")

    async def _check_node_health(self) -> None:
        """Check health of all nodes."""
        now = time.time()
        timeout_nodes = []

        for node_id, node in self.nodes.items():
            if (now - node.last_heartbeat) > self.settings.node_timeout:
                timeout_nodes.append(node_id)
                node.status = "timeout"

        for node_id in timeout_nodes:
            logger.warning(f"Node timeout: {node_id}")
            # TODO: Handle node timeout (retry, remove, etc.)

    def get_active_nodes(self) -> List[str]:
        """Get list of active nodes."""
        return [node_id for node_id, node in self.nodes.items() if node.status == "active"]

    def get_node_info(self, node_id: str) -> Optional[NodeInfo]:
        """Get information about a node."""
        return self.nodes.get(node_id)
