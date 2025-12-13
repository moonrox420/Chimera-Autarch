"""
Intent compiler service.
"""

from typing import List, Dict, Any
from dataclasses import dataclass

from models.intent import Intent
from core.logging import get_logger

logger = get_logger(__name__)


class IntentCompiler:
    """Compiles natural language intents into executable action plans."""

    def __init__(self):
        self.patterns = {
            "federated": ["federated", "learning", "train", "model"],
            "optimize": ["optimize", "improve", "fix", "code"],
            "analyze": ["analyze", "check", "review", "examine"],
            "deploy": ["deploy", "run", "start", "launch"],
            "monitor": ["monitor", "status", "health", "check"],
        }

    async def compile(self, intent_text: str) -> Intent:
        """Compile intent text into executable actions."""
        intent_text = intent_text.lower().strip()

        # Determine intent type
        intent_type = self._classify_intent(intent_text)

        # Generate action plan
        actions = self._generate_actions(intent_type, intent_text)

        return Intent(
            text=intent_text,
            actions=actions,
            priority=self._calculate_priority(intent_type)
        )

    def _classify_intent(self, text: str) -> str:
        """Classify the intent type."""
        for intent_type, keywords in self.patterns.items():
            if any(keyword in text for keyword in keywords):
                return intent_type
        return "general"

    def _generate_actions(self, intent_type: str, text: str) -> List[Dict[str, Any]]:
        """Generate action plan for intent type."""
        if intent_type == "federated":
            return [
                {
                    "tool": "start_federated_training",
                    "args": {"rounds": 3, "intent": text}
                }
            ]
        elif intent_type == "optimize":
            return [
                {
                    "tool": "analyze_code",
                    "args": {"target": text}
                },
                {
                    "tool": "optimize_code",
                    "args": {"target": text}
                }
            ]
        elif intent_type == "analyze":
            return [
                {
                    "tool": "analyze_system",
                    "args": {"aspect": text}
                }
            ]
        elif intent_type == "deploy":
            return [
                {
                    "tool": "deploy_service",
                    "args": {"service": text}
                }
            ]
        elif intent_type == "monitor":
            return [
                {
                    "tool": "get_status",
                    "args": {}
                }
            ]
        else:
            return [
                {
                    "tool": "process_general_intent",
                    "args": {"intent": text}
                }
            ]

    def _calculate_priority(self, intent_type: str) -> int:
        """Calculate execution priority."""
        priorities = {
            "monitor": 1,
            "analyze": 2,
            "optimize": 3,
            "deploy": 4,
            "federated": 5,
        }
        return priorities.get(intent_type, 1)