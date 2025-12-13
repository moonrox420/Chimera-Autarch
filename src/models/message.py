"""
Message models for communication.
"""

import json
from enum import Enum
from typing import Dict, Any
from dataclasses import dataclass


class MessageType(Enum):
    """Types of messages."""
    INTENT = "intent"
    HEARTBEAT = "heartbeat"
    STATUS_REQUEST = "status_request"
    RESULT = "result"


@dataclass
class Message:
    """Message container."""
    type: MessageType
    data: Dict[str, Any]
    timestamp: float
    client_id: str = ""

    @classmethod
    def from_json(cls, json_str: str) -> "Message":
        """Create message from JSON string."""
        data = json.loads(json_str)
        return cls(
            type=MessageType(data["type"]),
            data=data.get("data", {}),
            timestamp=data.get("timestamp", 0.0),
            client_id=data.get("client_id", "")
        )

    def to_json(self) -> str:
        """Convert message to JSON string."""
        return json.dumps({
            "type": self.type.value,
            "data": self.data,
            "timestamp": self.timestamp,
            "client_id": self.client_id
        })