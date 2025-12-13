"""
Metacognitive service for self-evolution.
"""

import asyncio
import time
from collections import defaultdict, deque
from typing import Dict, Optional
from dataclasses import dataclass, field

from config.settings import MetacognitiveSettings
from services.persistence import PersistenceService
from core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class FailurePattern:
    """Tracks failure patterns for a topic."""
    topic: str
    count: int = 0
    first_seen: float = field(default_factory=time.time)
    last_seen: float = field(default_factory=time.time)
    success_history: deque = field(default_factory=lambda: deque(maxlen=100))
    confidence: float = 1.0
    learning_triggered: bool = False

    def record_attempt(self, success: bool) -> None:
        """Record an attempt."""
        self.record(success)

    def record(self, success: bool) -> None:
        """Record success/failure."""
        self.count += 1
        now = time.time()
        self.last_seen = now
        if not self.first_seen:
            self.first_seen = now
        self.success_history.append(success)
        recent = list(self.success_history)
        self.confidence = sum(recent) / len(recent) if recent else 1.0


@dataclass
class EvolutionRecord:
    """Evolution improvement record."""
    id: str
    topic: str
    failure_reason: str = ""
    applied_fix: str = ""
    observed_improvement: float = 0.0
    timestamp: float = field(default_factory=time.time)
    validation_metrics: Dict = field(default_factory=dict)


class MetacognitiveService:
    """Metacognitive engine for predictive self-improvement."""

    def __init__(self, settings: MetacognitiveSettings, persistence: PersistenceService):
        self.settings = settings
        self.persistence = persistence
        self.patterns: Dict[str, FailurePattern] = {}
        self.cooldown = settings.learning_cooldown
        self.predictive_threshold = settings.confidence_threshold
        self._running = False

    async def initialize(self) -> None:
        """Initialize the metacognitive engine."""
        self._running = True
        logger.info("Metacognitive engine initialized")

    async def shutdown(self) -> None:
        """Shutdown the metacognitive engine."""
        self._running = False
        logger.info("Metacognitive engine shutdown")

    def _topic_from_intent(self, intent: str) -> str:
        """Extract topic from intent."""
        intent = intent.lower()
        mapping = {
            "image": ["image", "vision", "pixel"],
            "hn": ["hacker news", "news", "article"],
            "fl": ["federated", "flower", "learning"],
            "symbiotic": ["symbiotic", "arm"],
            "file": ["file", "disk", "read", "write"],
            "code": ["code", "function", "optimize"],
        }
        for topic, keywords in mapping.items():
            if any(k in intent for k in keywords):
                return topic
        return "general"

    def log_failure(self, intent: str, reason: str) -> str:
        """Log a failure and return the topic."""
        topic = self._topic_from_intent(intent)
        pattern = self.patterns.setdefault(topic, FailurePattern(topic))
        pattern.record(False)
        logger.warning(f"[FAIL:{topic}] {reason} | confidence={pattern.confidence:.2%}")
        return topic

    def record_success(self, topic: str) -> None:
        """Record a success."""
        pattern = self.patterns.setdefault(topic, FailurePattern(topic))
        pattern.record(True)

    async def monitor_loop(self) -> None:
        """Main monitoring loop."""
        while self._running:
            try:
                await asyncio.sleep(self.settings.predictive_check_interval)
                await self._predictive_monitor()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Metacognitive monitor error: {e}")

    async def _predictive_monitor(self) -> None:
        """Monitor for patterns requiring intervention."""
        now = time.time()
        for topic, pattern in list(self.patterns.items()):
            if pattern.confidence < self.predictive_threshold:
                if (now - pattern.last_seen) > self.cooldown:
                    logger.info(f"[PREDICTIVE] Triggering learning for {topic}")
                    await self._trigger_learning(topic)

    async def _trigger_learning(self, topic: str) -> None:
        """Trigger learning for a topic."""
        # TODO: Implement actual learning triggers
        logger.info(f"Learning triggered for topic: {topic}")

        # Record the evolution attempt
        evolution = EvolutionRecord(
            id=f"evo_{int(time.time())}",
            topic=topic,
            failure_reason=f"Low confidence: {self.patterns[topic].confidence:.2%}",
            applied_fix="Triggered federated learning",
            observed_improvement=0.0,  # Will be updated later
            validation_metrics={"trigger": "predictive"}
        )

        await self.persistence.log_evolution(evolution.__dict__)

    async def get_topic_status(self, topic: str) -> Dict:
        """Get status for a topic."""
        pattern = self.patterns.get(topic)
        if not pattern:
            return {"topic": topic, "status": "unknown"}

        return {
            "topic": topic,
            "confidence": pattern.confidence,
            "attempts": pattern.count,
            "last_seen": pattern.last_seen,
            "learning_triggered": pattern.learning_triggered
        }

    async def get_all_topics_status(self) -> Dict[str, Dict]:
        """Get status for all topics."""
        return {topic: await self.get_topic_status(topic) for topic in self.patterns}