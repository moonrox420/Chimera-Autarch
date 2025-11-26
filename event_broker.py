#!/usr/bin/env python3
"""
Event Broker - Real-time event streaming for CHIMERA AUTARCH
Provides pub/sub pattern for broadcasting system events to all connected clients
"""
import asyncio
import json
import time
import logging
from typing import Dict, Set, Callable, Any, List
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger("chimera.events")


class EventType(Enum):
    """System event types"""
    EVOLUTION_APPLIED = "evolution_applied"
    NODE_REGISTERED = "node_registered"
    NODE_DISCONNECTED = "node_disconnected"
    NODE_HEARTBEAT = "node_heartbeat"
    TOOL_EXECUTED = "tool_executed"
    CONFIDENCE_CHANGED = "confidence_changed"
    LEARNING_STARTED = "learning_started"
    LEARNING_COMPLETED = "learning_completed"
    TASK_DISPATCHED = "task_dispatched"
    TASK_COMPLETED = "task_completed"
    SYSTEM_ALERT = "system_alert"


@dataclass
class Event:
    """Event data structure"""
    type: EventType
    data: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)
    id: str = field(default_factory=lambda: f"evt_{int(time.time()*1000)}")
    priority: int = 0  # Higher = more important

    def to_json(self) -> str:
        """Serialize event to JSON"""
        return json.dumps({
            "id": self.id,
            "type": self.type.value,
            "data": self.data,
            "timestamp": self.timestamp,
            "priority": self.priority
        })

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "type": self.type.value,
            "data": self.data,
            "timestamp": self.timestamp,
            "priority": self.priority
        }


class EventBroker:
    """
    Centralized event broker with pub/sub pattern
    Broadcasts events to all subscribed WebSocket clients
    """

    def __init__(self, max_history: int = 1000):
        self.subscribers: Dict[str, Set[asyncio.Queue]] = {
            event_type.value: set() for event_type in EventType
        }
        self.subscribers["*"] = set()  # Wildcard subscribers

        self.event_history: List[Event] = []
        self.max_history = max_history

        self.stats = {
            "total_events": 0,
            "events_by_type": {et.value: 0 for et in EventType},
            "active_subscribers": 0
        }

        logger.info("[EVENT_BROKER] Initialized with pub/sub pattern")

    async def publish(self, event: Event):
        """
        Publish an event to all subscribers

        Args:
            event: Event to broadcast
        """
        # Add to history
        self.event_history.append(event)
        if len(self.event_history) > self.max_history:
            self.event_history.pop(0)

        # Update stats
        self.stats["total_events"] += 1
        self.stats["events_by_type"][event.type.value] += 1

        # Get subscribers for this event type + wildcard subscribers
        subscribers = self.subscribers.get(event.type.value, set()).copy()
        subscribers.update(self.subscribers["*"])

        # Broadcast to all subscribers (non-blocking)
        failed_queues = []
        for queue in subscribers:
            try:
                # Use put_nowait to avoid blocking
                queue.put_nowait(event)
            except asyncio.QueueFull:
                logger.warning(
                    f"[EVENT_BROKER] Subscriber queue full, event dropped")
                failed_queues.append(queue)
            except Exception as e:
                logger.error(
                    f"[EVENT_BROKER] Failed to publish to subscriber: {e}")
                failed_queues.append(queue)

        # Clean up failed queues
        for queue in failed_queues:
            self.unsubscribe(queue, event.type.value)

        logger.debug(
            f"[EVENT_BROKER] Published {event.type.value} to {len(subscribers)} subscribers")

    def subscribe(self, queue: asyncio.Queue, event_type: str = "*") -> bool:
        """
        Subscribe to events

        Args:
            queue: Async queue to receive events
            event_type: Event type to subscribe to ("*" for all events)

        Returns:
            True if subscribed successfully
        """
        if event_type not in self.subscribers:
            logger.warning(f"[EVENT_BROKER] Unknown event type: {event_type}")
            return False

        self.subscribers[event_type].add(queue)
        self.stats["active_subscribers"] = sum(
            len(subs) for subs in self.subscribers.values())

        logger.info(
            f"[EVENT_BROKER] New subscriber for {event_type} (total: {len(self.subscribers[event_type])})")
        return True

    def unsubscribe(self, queue: asyncio.Queue, event_type: str = "*"):
        """
        Unsubscribe from events

        Args:
            queue: Queue to remove
            event_type: Event type to unsubscribe from
        """
        if event_type in self.subscribers:
            self.subscribers[event_type].discard(queue)
            self.stats["active_subscribers"] = sum(
                len(subs) for subs in self.subscribers.values())
            logger.info(f"[EVENT_BROKER] Subscriber removed from {event_type}")

    def unsubscribe_all(self, queue: asyncio.Queue):
        """Unsubscribe from all event types"""
        for event_type in self.subscribers:
            self.subscribers[event_type].discard(queue)
        self.stats["active_subscribers"] = sum(
            len(subs) for subs in self.subscribers.values())
        logger.info("[EVENT_BROKER] Subscriber removed from all events")

    def get_history(self, event_type: str = None, limit: int = 100) -> List[Event]:
        """
        Get event history

        Args:
            event_type: Filter by event type (None for all)
            limit: Maximum events to return

        Returns:
            List of historical events
        """
        if event_type:
            filtered = [
                e for e in self.event_history if e.type.value == event_type]
        else:
            filtered = self.event_history

        return filtered[-limit:]

    def get_stats(self) -> Dict[str, Any]:
        """Get broker statistics"""
        return {
            **self.stats,
            "history_size": len(self.event_history),
            "max_history": self.max_history,
            "subscriber_breakdown": {
                event_type: len(subs)
                for event_type, subs in self.subscribers.items()
            }
        }

    async def emit_evolution(self, topic: str, improvement: float, fix: str):
        """Helper: Emit evolution applied event"""
        await self.publish(Event(
            type=EventType.EVOLUTION_APPLIED,
            data={
                "topic": topic,
                "improvement": improvement,
                "fix": fix
            },
            priority=8
        ))

    async def emit_node_event(self, event_type: EventType, node_id: str, **kwargs):
        """Helper: Emit node-related event"""
        await self.publish(Event(
            type=event_type,
            data={"node_id": node_id, **kwargs},
            priority=5
        ))

    async def emit_confidence_change(self, topic: str, old_confidence: float, new_confidence: float):
        """Helper: Emit confidence change event"""
        await self.publish(Event(
            type=EventType.CONFIDENCE_CHANGED,
            data={
                "topic": topic,
                "old_confidence": old_confidence,
                "new_confidence": new_confidence,
                "delta": new_confidence - old_confidence
            },
            priority=7
        ))

    async def emit_tool_execution(self, tool_name: str, success: bool, latency: float):
        """Helper: Emit tool execution event"""
        await self.publish(Event(
            type=EventType.TOOL_EXECUTED,
            data={
                "tool": tool_name,
                "success": success,
                "latency": latency
            },
            priority=3
        ))

    async def emit_alert(self, level: str, message: str, context: Dict = None):
        """Helper: Emit system alert"""
        await self.publish(Event(
            type=EventType.SYSTEM_ALERT,
            data={
                "level": level,  # info, warning, error, critical
                "message": message,
                "context": context or {}
            },
            priority=10
        ))


class EventStream:
    """
    Event stream consumer for WebSocket clients
    Manages subscription lifecycle and message formatting
    """

    def __init__(self, broker: EventBroker, websocket, client_id: str):
        self.broker = broker
        self.websocket = websocket
        self.client_id = client_id
        self.queue = asyncio.Queue(maxsize=100)
        self.subscriptions: Set[str] = set()
        self.active = True

        logger.info(f"[EVENT_STREAM] Created for client {client_id}")

    async def subscribe(self, event_type: str = "*"):
        """Subscribe to event type"""
        if self.broker.subscribe(self.queue, event_type):
            self.subscriptions.add(event_type)
            logger.info(
                f"[EVENT_STREAM] Client {self.client_id} subscribed to {event_type}")

    async def unsubscribe(self, event_type: str):
        """Unsubscribe from event type"""
        self.broker.unsubscribe(self.queue, event_type)
        self.subscriptions.discard(event_type)

    async def start(self):
        """Start streaming events to WebSocket"""
        logger.info(
            f"[EVENT_STREAM] Starting stream for client {self.client_id}")

        try:
            while self.active:
                # Wait for next event
                event = await self.queue.get()

                # Send to WebSocket client
                try:
                    await self.websocket.send(json.dumps({
                        "type": "event",
                        "event": event.to_dict()
                    }))
                except Exception as e:
                    logger.error(
                        f"[EVENT_STREAM] Failed to send event to {self.client_id}: {e}")
                    self.active = False
                    break

        finally:
            # Cleanup subscriptions
            self.broker.unsubscribe_all(self.queue)
            logger.info(
                f"[EVENT_STREAM] Stopped stream for client {self.client_id}")

    async def stop(self):
        """Stop streaming"""
        self.active = False
        self.broker.unsubscribe_all(self.queue)
