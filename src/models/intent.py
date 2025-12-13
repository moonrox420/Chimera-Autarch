"""
Intent models.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class Intent:
    """Compiled intent with execution plan."""
    text: str
    actions: list[Dict[str, Any]]
    priority: int = 1
    timeout: Optional[float] = None


@dataclass
class IntentResult:
    """Result of intent execution."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time: float = 0.0

    def dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "execution_time": self.execution_time
        }