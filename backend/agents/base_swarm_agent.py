"""
Base Swarm Agent Class

All swarm agents inherit from this class to get event bus integration,
registry management, and standard message handling.
"""

import asyncio
import time
from abc import ABC, abstractmethod
from typing import Callable, Dict, Any, List, Optional
from datetime import datetime
import redis

from backend.messaging.event_bus import EventBus, AgentMessage, EventType
from backend.messaging.context_bus import ContextBus
from backend.messaging.agent_registry import AgentRegistry, AgentCapability
from backend.models.agent_messages import AgentHeartbeat


class BaseSwarmAgent(ABC):
    """Base class for all swarm agents"""

    # Override in subclass
    AGENT_ID: str = "AGENT-00"
    AGENT_NAME: str = "UnnamedAgent"
    CAPABILITIES: List[str] = []
    POD: str = ""  # "strategy", "creation", "signals", "risk"
    MAX_CONCURRENT: int = 5

    def __init__(
        self,
        redis_client: redis.Redis,
        db_client,
        llm_client
    ):
        """Initialize swarm agent"""

        self.redis = redis_client
        self.db = db_client
        self.llm = llm_client

        # Initialize communication layers
        self.event_bus = EventBus(redis_client)
        self.context_bus = ContextBus(redis_client)
        self.registry = AgentRegistry(redis_client)

        # Agent state
        self.current_load = 0
        self.running = False
        self.message_handlers: Dict[EventType, Callable] = {}

        # Register agent
        self._register()

    def _register(self):
        """Register agent in the swarm"""

        capability = AgentCapability(
            agent_id=self.AGENT_ID,
            agent_name=self.AGENT_NAME,
            capabilities=self.CAPABILITIES,
            current_load=0,
            max_concurrent=self.MAX_CONCURRENT,
            success_rate=0.9,
            pod=self.POD
        )

        self.registry.register(capability)
        print(f"[{self.AGENT_ID}] Registered with capabilities: {self.CAPABILITIES}")

    async def start(self):
        """Start listening for messages"""

        self.running = True

        print(f"[{self.AGENT_ID}] Starting...")

        # Start message listener
        listener_task = asyncio.create_task(
            self.event_bus.subscribe(self.AGENT_ID, self._handle_incoming_message)
        )

        # Start heartbeat
        heartbeat_task = asyncio.create_task(self._heartbeat_loop())

        await asyncio.gather(listener_task, heartbeat_task)

    async def stop(self):
        """Stop listening for messages"""

        self.running = False
        self.registry.unregister(self.AGENT_ID)
        print(f"[{self.AGENT_ID}] Stopped")

    def register_handler(self, event_type: EventType, handler: Callable):
        """Register a handler for specific message type"""

        self.message_handlers[event_type] = handler

    async def _handle_incoming_message(self, message: AgentMessage):
        """Internal message handler"""

        correlation_id = message.correlation_id
        task_start = time.time()

        try:
            # Update load
            self.current_load += 1
            self.registry.update_load(self.AGENT_ID, +1)

            # Set status in context
            self.context_bus.set_context(
                correlation_id,
                f"{self.AGENT_ID}_status",
                "working"
            )

            print(f"[{self.AGENT_ID}] Processing {message.type.value}")

            # Dispatch to handler
            if message.type in self.message_handlers:
                handler = self.message_handlers[message.type]
                if asyncio.iscoroutinefunction(handler):
                    await handler(message)
                else:
                    handler(message)
            else:
                # Try generic handler
                await self.handle_message(message)

            # Set status done
            self.context_bus.set_context(
                correlation_id,
                f"{self.AGENT_ID}_status",
                "done"
            )

            # Update metrics
            latency = (time.time() - task_start) * 1000  # ms
            self.registry.update_metrics(self.AGENT_ID, latency, success=True)

            print(f"[{self.AGENT_ID}] Completed {message.type.value} in {latency:.0f}ms")

        except Exception as e:
            # Log error
            self.context_bus.set_context(
                correlation_id,
                f"{self.AGENT_ID}_error",
                str(e)
            )
            self.context_bus.set_context(
                correlation_id,
                f"{self.AGENT_ID}_status",
                "error"
            )

            # Update metrics
            latency = (time.time() - task_start) * 1000
            self.registry.update_metrics(self.AGENT_ID, latency, success=False)

            # Publish error event
            error_message = AgentMessage(
                type=EventType.AGENT_ERROR,
                origin=self.AGENT_ID,
                targets=["APEX"],  # Send to master
                payload={
                    "error": str(e),
                    "message_type": message.type.value,
                    "correlation_id": correlation_id
                },
                correlation_id=correlation_id,
                priority="HIGH"
            )

            self.event_bus.publish(error_message)

            print(f"[{self.AGENT_ID}] ERROR: {str(e)}")

        finally:
            # Update load
            self.current_load = max(0, self.current_load - 1)
            self.registry.update_load(self.AGENT_ID, -1)

    async def _heartbeat_loop(self):
        """Send periodic heartbeat"""

        while self.running:
            try:
                heartbeat = AgentHeartbeat(
                    agent_id=self.AGENT_ID,
                    current_load=self.current_load,
                    status="healthy" if self.current_load < self.MAX_CONCURRENT else "degraded"
                )

                # Update registry
                self.registry.heartbeat(self.AGENT_ID)

                await asyncio.sleep(30)  # Send heartbeat every 30 seconds

            except Exception as e:
                print(f"[{self.AGENT_ID}] Heartbeat error: {e}")
                await asyncio.sleep(30)

    # ========================================================================
    # Helper Methods for Agent Development
    # ========================================================================

    def publish_message(
        self,
        message_type: EventType,
        payload: Dict[str, Any],
        targets: List[str],
        correlation_id: str,
        priority: str = "MEDIUM",
        broadcast: bool = False
    ):
        """Publish a message to other agents"""

        message = AgentMessage(
            type=message_type,
            origin=self.AGENT_ID,
            targets=targets,
            payload=payload,
            correlation_id=correlation_id,
            priority=priority,
            broadcast=broadcast
        )

        self.event_bus.publish(message)
        return message.id

    def request_context(
        self,
        correlation_id: str,
        key: str,
        timeout: float = 30.0
    ) -> Any:
        """Request context value from bus with timeout"""

        return self.context_bus.watch_context(
            correlation_id,
            key,
            timeout=timeout
        )

    def set_result(
        self,
        correlation_id: str,
        result: Dict[str, Any]
    ):
        """Store result in context for requester to fetch"""

        self.context_bus.set_context(
            correlation_id,
            f"{self.AGENT_ID}_result",
            result
        )

    def acquire_resource_lock(
        self,
        correlation_id: str,
        resource: str,
        timeout: int = 60
    ) -> bool:
        """Acquire exclusive lock on a resource"""

        return self.context_bus.lock(correlation_id, resource, self.AGENT_ID, timeout)

    def release_resource_lock(
        self,
        correlation_id: str,
        resource: str
    ):
        """Release a resource lock"""

        self.context_bus.unlock(correlation_id, resource, self.AGENT_ID)

    def get_shared_context(self, correlation_id: str) -> Dict[str, Any]:
        """Get entire shared context for a workflow"""

        return self.context_bus.get_all_context(correlation_id)

    async def find_best_agent_for_task(
        self,
        required_capabilities: List[str],
        prefer_pod: Optional[str] = None
    ) -> Optional[AgentCapability]:
        """Find the best available agent for a task"""

        return self.registry.find_best_agent(required_capabilities, prefer_pod)

    def log_event(
        self,
        correlation_id: str,
        event_type: str,
        details: Dict[str, Any]
    ):
        """Log an event for audit trail"""

        self.context_bus.set_context(
            correlation_id,
            f"{self.AGENT_ID}_event_{int(time.time() * 1000)}",
            {
                "event_type": event_type,
                "details": details,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    # ========================================================================
    # Abstract Methods - Override in Subclass
    # ========================================================================

    async def handle_message(self, message: AgentMessage):
        """
        Default message handler

        Override register_handler() for specific message types,
        or override this for a catch-all handler.
        """

        print(f"[{self.AGENT_ID}] Received unhandled message type: {message.type}")

    # ========================================================================
    # Utility Methods
    # ========================================================================

    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""

        agent = self.registry.get_agent(self.AGENT_ID)

        if agent:
            return {
                "agent_id": self.AGENT_ID,
                "agent_name": self.AGENT_NAME,
                "status": "running" if self.running else "stopped",
                "current_load": agent.current_load,
                "max_concurrent": agent.max_concurrent,
                "load_percentage": agent.load_percentage,
                "success_rate": agent.success_rate,
                "avg_latency_ms": agent.avg_latency_ms,
                "capabilities": agent.capabilities,
                "pod": agent.pod
            }

        return {"status": "not_registered"}


# ============================================================================
# Example Usage
# ============================================================================

"""
class MyCustomAgent(BaseSwarmAgent):
    AGENT_ID = "CUSTOM-01"
    AGENT_NAME = "MyAgent"
    CAPABILITIES = ["custom_task", "analysis"]
    POD = "strategy"
    MAX_CONCURRENT = 5

    def __init__(self, redis_client, db_client, llm_client):
        super().__init__(redis_client, db_client, llm_client)

        # Register handlers for specific message types
        self.register_handler(EventType.GOAL_REQUEST, self.handle_goal)
        self.register_handler(EventType.MOVE_PLAN, self.handle_move_plan)

    async def handle_goal(self, message: AgentMessage):
        # Handle goal request
        goal = message.payload
        result = await self.process_goal(goal)

        # Publish result
        self.publish_message(
            EventType.MOVE_PLAN,
            result,
            targets=["IDEA-01", "COPY-01"],
            correlation_id=message.correlation_id
        )

    async def handle_move_plan(self, message: AgentMessage):
        # Handle move plan
        pass

    async def process_goal(self, goal):
        # Custom logic
        return {"result": "..."}


# Usage:
agent = MyCustomAgent(redis_client, db_client, llm_client)
await agent.start()  # Runs in background
# ... agent processes messages ...
await agent.stop()
"""
