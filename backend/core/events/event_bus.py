
import asyncio
import logging
from typing import Any, Callable, Dict, List
from uuid import uuid4
from datetime import datetime

# In a real system, we would use Redis Pub/Sub or PostgreSQL Notify
# For this scaffold, we'll use a simple in-memory list and an observer pattern

logger = logging.getLogger(__name__)

class Event:
    def __init__(self, event_type: str, payload: Dict[str, Any], correlation_id: str = None):
        self.id = str(uuid4())
        self.event_type = event_type
        self.payload = payload
        self.correlation_id = correlation_id or str(uuid4())
        self.timestamp = datetime.utcnow().isoformat()

    def to_dict(self):
        return {
            "id": self.id,
            "event_type": self.event_type,
            "payload": self.payload,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp
        }

class RealTimeEventBus:
    """
    A robust event bus that supports:
    1. Internal agent communication (Pub/Sub)
    2. Real-time WebSocket streaming to frontend (via hooks)
    """
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.websocket_hooks: List[Callable] = [] # Functions to push to WS

    def subscribe(self, event_type: str, handler: Callable):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)

    def register_websocket_hook(self, hook: Callable):
        """
        Registers a function that will receive all events for frontend streaming.
        """
        self.websocket_hooks.append(hook)

    async def publish(self, event_type: str, payload: Dict[str, Any], correlation_id: str = None):
        event = Event(event_type, payload, correlation_id)
        
        # 1. Log event
        logger.info(f"📢 Event: {event_type} (ID: {event.id})")
        
        # 2. Notify internal subscribers
        if event_type in self.subscribers:
            for handler in self.subscribers[event_type]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(event)
                    else:
                        handler(event)
                except Exception as e:
                    logger.error(f"Error in event handler for {event_type}: {e}")

        # 3. Push to WebSocket stream
        # This is the key SOTA feature: "Visualizing the brain"
        for hook in self.websocket_hooks:
            try:
                if asyncio.iscoroutinefunction(hook):
                    await hook(event.to_dict())
                else:
                    hook(event.to_dict())
            except Exception as e:
                logger.error(f"Error pushing to websocket hook: {e}")

# Global Bus Instance
event_bus = RealTimeEventBus()
