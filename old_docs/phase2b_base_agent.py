"""
Phase 2B - BaseSpecializedAgent Class
Extends Phase 2A BaseAgent with RaptorBus integration and advanced features
All 70+ specialized agents inherit from this class
"""

import asyncio
import uuid
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum
import json

# ============================================================================
# EVENT TYPES & CHANNELS
# ============================================================================

class EventType(str, Enum):
    """21 Event Types across Phase 2B"""
    # Agent Execution Events
    AGENT_STARTED = "agent_started"
    AGENT_COMPLETED = "agent_completed"
    AGENT_FAILED = "agent_failed"
    CAPABILITY_EXECUTED = "capability_executed"
    RESULT_GENERATED = "result_generated"

    # Data Events
    DATA_CREATED = "data_created"
    DATA_UPDATED = "data_updated"
    DATA_DELETED = "data_deleted"
    DATA_QUERIED = "data_queried"
    DATA_VALIDATED = "data_validated"

    # Communication Events
    MESSAGE_SENT = "message_sent"
    MESSAGE_RECEIVED = "message_received"
    NOTIFICATION_TRIGGERED = "notification_triggered"
    BROADCAST_INITIATED = "broadcast_initiated"
    RESPONSE_DELIVERED = "response_delivered"

    # System Events
    ERROR_OCCURRED = "error_occurred"
    WARNING_ISSUED = "warning_issued"
    METRIC_RECORDED = "metric_recorded"
    STATUS_UPDATED = "status_updated"
    RESOURCE_ALLOCATED = "resource_allocated"
    WORKFLOW_COMPLETED = "workflow_completed"


class Channel(str, Enum):
    """9 RaptorBus Pub/Sub Channels"""
    AGENT_EXECUTION = "agent_execution"
    DATA_OPERATIONS = "data_operations"
    AGENT_COMMUNICATION = "agent_communication"
    SYSTEM_EVENTS = "system_events"
    ERROR_HANDLING = "error_handling"
    METRICS = "metrics"
    WORKFLOWS = "workflows"
    NOTIFICATIONS = "notifications"
    ANALYTICS = "analytics"


# ============================================================================
# EVENT DATA STRUCTURES
# ============================================================================

@dataclass
class RaptorBusEvent:
    """Standard event structure for all RaptorBus events"""
    event_id: str
    timestamp: str  # ISO format
    lord: str  # Domain (architect, cognition, etc.)
    agent: str  # Agent name
    event_type: EventType
    channel: Channel
    data: Dict[str, Any]
    status: str  # 'success', 'error', 'warning'
    execution_time_ms: float = 0.0
    source_agent: Optional[str] = None
    target_agents: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp,
            "lord": self.lord,
            "agent": self.agent,
            "event_type": self.event_type.value,
            "channel": self.channel.value,
            "data": self.data,
            "status": self.status,
            "execution_time_ms": self.execution_time_ms,
            "source_agent": self.source_agent,
            "target_agents": self.target_agents,
            "metadata": self.metadata
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


@dataclass
class AgentCapability:
    """Capability definition for specialized agents"""
    name: str
    description: str
    handler: Optional[Callable] = None
    required_params: List[str] = field(default_factory=list)
    optional_params: List[str] = field(default_factory=list)
    timeout_seconds: float = 30.0
    retry_count: int = 3
    cache_enabled: bool = False
    cache_ttl_minutes: int = 5


@dataclass
class AgentMetrics:
    """Performance metrics for each agent"""
    agent_id: str
    executions_total: int = 0
    executions_successful: int = 0
    executions_failed: int = 0
    avg_execution_time_ms: float = 0.0
    min_execution_time_ms: float = float('inf')
    max_execution_time_ms: float = 0.0
    error_rate: float = 0.0
    last_execution: Optional[str] = None
    uptime_percentage: float = 100.0
    availability_status: str = "healthy"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ============================================================================
# RAPTOR BUS INTERFACE
# ============================================================================

class RaptorBusInterface(ABC):
    """Abstract interface for RaptorBus integration"""

    @abstractmethod
    async def publish(self, channel: Channel, event: RaptorBusEvent) -> bool:
        """Publish event to channel"""
        pass

    @abstractmethod
    async def subscribe(self, channel: Channel, callback: Callable) -> None:
        """Subscribe to channel events"""
        pass

    @abstractmethod
    async def broadcast(self, event: RaptorBusEvent, lord: Optional[str] = None) -> int:
        """Broadcast to all agents, optionally filtered by lord"""
        pass

    @abstractmethod
    async def get_event_history(self, agent_id: str, limit: int = 100) -> List[RaptorBusEvent]:
        """Get event history for agent"""
        pass


# Placeholder for actual RaptorBus implementation
class MockRaptorBus(RaptorBusInterface):
    """Mock RaptorBus for development/testing"""

    def __init__(self):
        self.events: List[RaptorBusEvent] = []
        self.subscribers: Dict[Channel, List[Callable]] = {
            ch: [] for ch in Channel
        }

    async def publish(self, channel: Channel, event: RaptorBusEvent) -> bool:
        self.events.append(event)
        # Call subscribers
        for callback in self.subscribers.get(channel, []):
            try:
                await callback(event)
            except Exception as e:
                print(f"Subscriber error: {e}")
        return True

    async def subscribe(self, channel: Channel, callback: Callable) -> None:
        if channel not in self.subscribers:
            self.subscribers[channel] = []
        self.subscribers[channel].append(callback)

    async def broadcast(self, event: RaptorBusEvent, lord: Optional[str] = None) -> int:
        count = 0
        for channel in Channel:
            if await self.publish(channel, event):
                count += 1
        return count

    async def get_event_history(self, agent_id: str, limit: int = 100) -> List[RaptorBusEvent]:
        return [e for e in self.events if e.agent == agent_id][-limit:]


# ============================================================================
# BASE SPECIALIZED AGENT
# ============================================================================

class BaseSpecializedAgent(ABC):
    """
    Base class for all 70+ specialized agents in Phase 2B
    Each agent is specialized for a specific domain and function
    """

    def __init__(
        self,
        agent_id: str,
        agent_name: str,
        lord: str,
        description: str,
        raptor_bus: Optional[RaptorBusInterface] = None
    ):
        self.agent_id = agent_id or str(uuid.uuid4())
        self.agent_name = agent_name
        self.lord = lord  # Domain: architect, cognition, strategos, etc.
        self.description = description
        self.raptor_bus = raptor_bus or MockRaptorBus()

        # Agent state
        self.capabilities: Dict[str, AgentCapability] = {}
        self.state: Dict[str, Any] = {}
        self.metrics = AgentMetrics(agent_id=self.agent_id)
        self.is_active = True
        self.last_heartbeat = datetime.utcnow()

        # Cache management
        self.cache: Dict[str, tuple] = {}  # {key: (value, expiry_time)}

    # ========================================================================
    # CORE METHODS - MUST BE IMPLEMENTED BY SUBCLASSES
    # ========================================================================

    @abstractmethod
    async def register_capabilities(self) -> None:
        """Register all 5 capabilities for this agent"""
        pass

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize agent resources"""
        pass

    async def shutdown(self) -> None:
        """Shutdown agent gracefully"""
        self.is_active = False
        await self._publish_event(
            EventType.STATUS_UPDATED,
            Channel.SYSTEM_EVENTS,
            {"status": "shutdown"},
            "success"
        )

    # ========================================================================
    # CAPABILITY MANAGEMENT
    # ========================================================================

    def register_capability(self, capability: AgentCapability) -> None:
        """Register a single capability"""
        self.capabilities[capability.name] = capability

    def get_capability(self, capability_name: str) -> Optional[AgentCapability]:
        """Get capability by name"""
        return self.capabilities.get(capability_name)

    def list_capabilities(self) -> List[str]:
        """List all registered capabilities"""
        return list(self.capabilities.keys())

    # ========================================================================
    # EXECUTION METHODS
    # ========================================================================

    async def execute_capability(
        self,
        capability_name: str,
        params: Dict[str, Any],
        timeout_override: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Execute a capability with RaptorBus integration
        """
        capability = self.get_capability(capability_name)
        if not capability:
            raise ValueError(f"Capability {capability_name} not found")

        execution_id = str(uuid.uuid4())
        start_time = datetime.utcnow()

        # Publish: AGENT_STARTED
        await self._publish_event(
            EventType.AGENT_STARTED,
            Channel.AGENT_EXECUTION,
            {
                "execution_id": execution_id,
                "capability": capability_name,
                "params": params
            },
            "success"
        )

        try:
            # Validate parameters
            missing_params = [
                p for p in capability.required_params
                if p not in params
            ]
            if missing_params:
                raise ValueError(f"Missing required parameters: {missing_params}")

            # Check cache
            cache_key = f"{capability_name}:{json.dumps(params, sort_keys=True)}"
            if capability.cache_enabled:
                cached_result = self._get_from_cache(cache_key)
                if cached_result is not None:
                    await self._publish_event(
                        EventType.CAPABILITY_EXECUTED,
                        Channel.AGENT_EXECUTION,
                        {"execution_id": execution_id, "from_cache": True},
                        "success"
                    )
                    return cached_result

            # Execute capability with timeout
            timeout = timeout_override or capability.timeout_seconds
            result = await asyncio.wait_for(
                capability.handler(**params),
                timeout=timeout
            )

            # Publish: CAPABILITY_EXECUTED
            await self._publish_event(
                EventType.CAPABILITY_EXECUTED,
                Channel.AGENT_EXECUTION,
                {
                    "execution_id": execution_id,
                    "capability": capability_name,
                    "status": "success"
                },
                "success"
            )

            # Cache result if enabled
            if capability.cache_enabled:
                self._set_in_cache(cache_key, result, capability.cache_ttl_minutes)

            # Publish: RESULT_GENERATED
            await self._publish_event(
                EventType.RESULT_GENERATED,
                Channel.AGENT_EXECUTION,
                {
                    "execution_id": execution_id,
                    "result_type": type(result).__name__,
                    "result_size": len(str(result))
                },
                "success"
            )

            # Update metrics
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            self._update_metrics(execution_time, True)

            return result

        except asyncio.TimeoutError:
            await self._handle_execution_error(
                execution_id,
                f"Capability {capability_name} timeout after {timeout}s",
                EventType.AGENT_FAILED
            )
            self._update_metrics(0, False)
            raise

        except Exception as e:
            await self._handle_execution_error(
                execution_id,
                str(e),
                EventType.AGENT_FAILED
            )
            self._update_metrics(0, False)
            raise

        finally:
            # Publish: AGENT_COMPLETED
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            await self._publish_event(
                EventType.AGENT_COMPLETED,
                Channel.AGENT_EXECUTION,
                {
                    "execution_id": execution_id,
                    "execution_time_ms": execution_time
                },
                "success"
            )

    # ========================================================================
    # EVENT PUBLISHING
    # ========================================================================

    async def _publish_event(
        self,
        event_type: EventType,
        channel: Channel,
        data: Dict[str, Any],
        status: str = "success",
        target_agents: Optional[List[str]] = None
    ) -> bool:
        """Publish event to RaptorBus"""
        event = RaptorBusEvent(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow().isoformat(),
            lord=self.lord,
            agent=self.agent_name,
            event_type=event_type,
            channel=channel,
            data=data,
            status=status,
            target_agents=target_agents or []
        )
        return await self.raptor_bus.publish(channel, event)

    async def _handle_execution_error(
        self,
        execution_id: str,
        error_message: str,
        event_type: EventType
    ) -> None:
        """Handle execution error and publish event"""
        await self._publish_event(
            event_type,
            Channel.ERROR_HANDLING,
            {
                "execution_id": execution_id,
                "error": error_message
            },
            "error"
        )

    # ========================================================================
    # CACHE MANAGEMENT
    # ========================================================================

    def _set_in_cache(self, key: str, value: Any, ttl_minutes: int) -> None:
        """Set value in agent cache with TTL"""
        expiry = datetime.utcnow() + timedelta(minutes=ttl_minutes)
        self.cache[key] = (value, expiry)

    def _get_from_cache(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired"""
        if key not in self.cache:
            return None

        value, expiry = self.cache[key]
        if datetime.utcnow() > expiry:
            del self.cache[key]
            return None

        return value

    def clear_cache(self) -> None:
        """Clear all cache"""
        self.cache.clear()

    # ========================================================================
    # METRICS & MONITORING
    # ========================================================================

    def _update_metrics(self, execution_time_ms: float, success: bool) -> None:
        """Update agent metrics"""
        self.metrics.executions_total += 1
        self.metrics.last_execution = datetime.utcnow().isoformat()

        if success:
            self.metrics.executions_successful += 1
        else:
            self.metrics.executions_failed += 1

        # Update execution time metrics
        if execution_time_ms > 0:
            if self.metrics.executions_successful == 1:
                self.metrics.min_execution_time_ms = execution_time_ms
                self.metrics.max_execution_time_ms = execution_time_ms
                self.metrics.avg_execution_time_ms = execution_time_ms
            else:
                # Running average
                total_time = self.metrics.avg_execution_time_ms * (self.metrics.executions_successful - 1)
                self.metrics.avg_execution_time_ms = (total_time + execution_time_ms) / self.metrics.executions_successful
                self.metrics.min_execution_time_ms = min(self.metrics.min_execution_time_ms, execution_time_ms)
                self.metrics.max_execution_time_ms = max(self.metrics.max_execution_time_ms, execution_time_ms)

        # Calculate error rate
        if self.metrics.executions_total > 0:
            self.metrics.error_rate = self.metrics.executions_failed / self.metrics.executions_total

    def get_metrics(self) -> AgentMetrics:
        """Get current agent metrics"""
        return self.metrics

    # ========================================================================
    # HEALTH & STATUS
    # ========================================================================

    def heartbeat(self) -> None:
        """Record agent heartbeat"""
        self.last_heartbeat = datetime.utcnow()

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "status": "healthy" if self.is_active else "inactive",
            "last_heartbeat": self.last_heartbeat.isoformat(),
            "capabilities": len(self.capabilities),
            "metrics": self.metrics.to_dict()
        }

    # ========================================================================
    # STATE MANAGEMENT
    # ========================================================================

    def set_state(self, key: str, value: Any) -> None:
        """Set agent state"""
        self.state[key] = value

    def get_state(self, key: str, default: Any = None) -> Any:
        """Get agent state"""
        return self.state.get(key, default)

    def update_state(self, updates: Dict[str, Any]) -> None:
        """Update agent state with dict"""
        self.state.update(updates)

    def clear_state(self) -> None:
        """Clear all state"""
        self.state.clear()

    # ========================================================================
    # AGENT INFO
    # ========================================================================

    def to_dict(self) -> Dict[str, Any]:
        """Serialize agent to dict"""
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "lord": self.lord,
            "description": self.description,
            "capabilities": list(self.capabilities.keys()),
            "is_active": self.is_active,
            "metrics": self.metrics.to_dict(),
            "state_keys": list(self.state.keys())
        }

    def __repr__(self) -> str:
        return f"<{self.agent_name} ({self.lord})>"


# ============================================================================
# SPECIALIZED AGENT TEMPLATE
# ============================================================================

class SpecializedAgentTemplate(BaseSpecializedAgent):
    """Template for creating new specialized agents"""

    async def register_capabilities(self) -> None:
        """Register 5 capabilities for this agent"""
        self.register_capability(AgentCapability(
            name="capability_1",
            description="First capability",
            handler=self._capability_1,
            required_params=["param1"],
            timeout_seconds=10,
            cache_enabled=True
        ))

        self.register_capability(AgentCapability(
            name="capability_2",
            description="Second capability",
            handler=self._capability_2,
            required_params=["param2"],
            timeout_seconds=10
        ))

        # ... register 3 more capabilities (5 total required)

    async def initialize(self) -> None:
        """Initialize agent resources"""
        await self.register_capabilities()

    async def _capability_1(self, param1: str) -> Dict[str, Any]:
        """First capability implementation"""
        return {"result": f"Processing {param1}"}

    async def _capability_2(self, param2: str) -> Dict[str, Any]:
        """Second capability implementation"""
        return {"result": f"Processing {param2}"}


# ============================================================================
# AGENT FACTORY
# ============================================================================

class AgentFactory:
    """Factory for creating specialized agents"""

    def __init__(self, raptor_bus: Optional[RaptorBusInterface] = None):
        self.raptor_bus = raptor_bus or MockRaptorBus()
        self.agents: Dict[str, BaseSpecializedAgent] = {}

    def create_agent(
        self,
        agent_class: type,
        agent_id: str,
        agent_name: str,
        lord: str,
        description: str
    ) -> BaseSpecializedAgent:
        """Create a new specialized agent"""
        agent = agent_class(
            agent_id=agent_id,
            agent_name=agent_name,
            lord=lord,
            description=description,
            raptor_bus=self.raptor_bus
        )
        self.agents[agent_id] = agent
        return agent

    def get_agent(self, agent_id: str) -> Optional[BaseSpecializedAgent]:
        """Get agent by ID"""
        return self.agents.get(agent_id)

    def list_agents(self) -> List[BaseSpecializedAgent]:
        """List all agents"""
        return list(self.agents.values())

    def list_agents_by_lord(self, lord: str) -> List[BaseSpecializedAgent]:
        """List agents for a specific lord"""
        return [a for a in self.agents.values() if a.lord == lord]


if __name__ == "__main__":
    print("Phase 2B Base Specialized Agent Framework")
    print("Ready for agent implementation")
