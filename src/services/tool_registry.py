"""
Tool registry service.
"""

import asyncio
import time
from collections import defaultdict, deque
from typing import Dict, Any, Callable, Optional, List
from dataclasses import dataclass, field

from models.intent import IntentResult
from core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ToolResult:
    """Result of tool execution."""
    success: bool
    data: Any = None
    metrics: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


@dataclass
class Tool:
    """Registered tool."""
    name: str
    func: Callable[..., asyncio.Future[Any]]
    description: str = ""
    version: str = "1.0.0"
    dependencies: List[str] = field(default_factory=list)
    _latency_samples: deque = field(default_factory=lambda: deque(maxlen=200))

    async def execute(self, **kwargs) -> ToolResult:
        """Execute the tool."""
        start = time.monotonic()
        try:
            result = await self.func(**kwargs)
            latency = time.monotonic() - start
            self._latency_samples.append(latency)
            return ToolResult(
                success=True,
                data=result,
                metrics={"latency": latency, "version": self.version},
            )
        except Exception as exc:
            logger.error(f"[TOOL:{self.name}] {exc!r}")
            return ToolResult(
                success=False,
                data=str(exc),
                metrics={"error": str(exc)},
            )


class ToolRegistry:
    """Registry for tools."""

    def __init__(self):
        self._tools: Dict[str, Tool] = {}
        self._metrics: defaultdict = defaultdict(list)

    @property
    def tools(self) -> Dict[str, Tool]:
        return self._tools

    def register(self, tool: Tool) -> None:
        """Register a tool."""
        self._tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name} v{tool.version}")

    async def execute(self, name: str, **kwargs) -> ToolResult:
        """Execute a tool."""
        tool = self._tools.get(name)
        if not tool:
            return ToolResult(False, f"Tool '{name}' not found", {"error": "not_found"})

        result = await tool.execute(**kwargs)
        self._metrics[name].append(
            {
                "ts": time.time(),
                "success": result.success,
                "latency": result.metrics.get("latency", 0),
            }
        )
        return result

    def stats(self, name: str, window: Optional[int] = None) -> Dict[str, float]:
        """Get tool statistics."""
        history = self._metrics[name][-window:] if window else self._metrics[name]
        if not history:
            return {"success_rate": 1.0, "avg_latency": 0.0}
        successes = sum(e["success"] for e in history)
        return {
            "success_rate": successes / len(history),
            "avg_latency": sum(e["latency"] for e in history) / len(history),
        }
