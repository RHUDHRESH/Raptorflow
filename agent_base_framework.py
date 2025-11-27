# backend/agents/base_agent.py
# RaptorFlow Codex - Base Agent Framework
# Week 3 - Agent Architecture Foundation

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio
import logging
import json
from uuid import UUID

logger = logging.getLogger(__name__)

# ============================================================================
# AGENT ENUMS & TYPES
# ============================================================================

class AgentType(str, Enum):
    """Agent type classification"""
    LORD = "lord"
    RESEARCHER = "researcher"
    CREATIVE = "creative"
    INTELLIGENCE = "intelligence"
    GUARDIAN = "guardian"

class AgentStatus(str, Enum):
    """Agent execution status"""
    IDLE = "idle"
    THINKING = "thinking"
    EXECUTING = "executing"
    WAITING = "waiting"
    ERROR = "error"
    COMPLETE = "complete"

class CapabilityCategory(str, Enum):
    """Capability classification"""
    RESEARCH = "research"
    ANALYSIS = "analysis"
    CREATION = "creation"
    OPTIMIZATION = "optimization"
    MONITORING = "monitoring"

# ============================================================================
# CAPABILITY SYSTEM
# ============================================================================

@dataclass
class Capability:
    """Agent capability definition"""
    name: str
    category: CapabilityCategory
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    requires_context: bool = False
    handler: Optional[Callable] = None

    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute capability with parameters"""
        if not self.handler:
            raise NotImplementedError(f"Handler not implemented for {self.name}")
        return await self.handler(**kwargs)

# ============================================================================
# PERFORMANCE METRICS
# ============================================================================

@dataclass
class ExecutionMetrics:
    """Track agent execution performance"""
    executions: int = 0
    successes: int = 0
    failures: int = 0
    total_duration_seconds: float = 0
    total_tokens_used: int = 0
    total_cost: float = 0

    avg_duration: float = 0
    success_rate: float = 0
    avg_tokens_per_execution: int = 0
    avg_cost_per_execution: float = 0

    updated_at: datetime = field(default_factory=datetime.utcnow)

    def calculate_stats(self):
        """Calculate aggregated statistics"""
        if self.executions > 0:
            self.avg_duration = self.total_duration_seconds / self.executions
            self.success_rate = (self.successes / self.executions) * 100
            self.avg_tokens_per_execution = self.total_tokens_used // self.executions
            self.avg_cost_per_execution = self.total_cost / self.executions

    def record_execution(self, duration: float, tokens: int, cost: float, success: bool):
        """Record single execution"""
        self.executions += 1
        self.total_duration_seconds += duration
        self.total_tokens_used += tokens
        self.total_cost += cost
        if success:
            self.successes += 1
        else:
            self.failures += 1
        self.updated_at = datetime.utcnow()
        self.calculate_stats()

# ============================================================================
# BASE AGENT CLASS
# ============================================================================

class BaseAgent(ABC):
    """
    Abstract base class for all agents in RaptorFlow Codex.

    Provides:
    - Capability registration and execution
    - Context management
    - Performance tracking
    - Error handling
    - Async execution
    """

    def __init__(
        self,
        name: str,
        agent_type: AgentType,
        guild_name: str,
        description: str = "",
        personality_traits: List[str] = None,
        model_config: Dict[str, Any] = None
    ):
        """Initialize base agent"""
        self.id: Optional[UUID] = None
        self.name = name
        self.agent_type = agent_type
        self.guild_name = guild_name
        self.description = description
        self.personality_traits = personality_traits or []

        # Model configuration
        self.model_config = model_config or {
            "model": "claude-sonnet-4",
            "temperature": 0.7,
            "max_tokens": 2000
        }

        # Capabilities
        self.capabilities: Dict[str, Capability] = {}

        # State management
        self.status = AgentStatus.IDLE
        self.context: Dict[str, Any] = {}
        self.current_task: Optional[str] = None

        # Performance tracking
        self.metrics = ExecutionMetrics()

        # Logging
        self.logger = logging.getLogger(f"agent.{self.name}")

    # ========================================================================
    # CAPABILITY MANAGEMENT
    # ========================================================================

    def register_capability(
        self,
        name: str,
        category: CapabilityCategory,
        handler: Callable,
        description: str = "",
        input_schema: Dict = None,
        output_schema: Dict = None,
        requires_context: bool = False
    ) -> "BaseAgent":
        """
        Register a new capability for this agent.

        Example:
            async def search_research(query: str) -> Dict:
                return await external_search_service.search(query)

            agent.register_capability(
                name="search_research",
                category=CapabilityCategory.RESEARCH,
                handler=search_research,
                input_schema={"query": "string"},
                output_schema={"results": "array"}
            )
        """
        capability = Capability(
            name=name,
            category=category,
            description=description,
            input_schema=input_schema or {},
            output_schema=output_schema or {},
            requires_context=requires_context,
            handler=handler
        )
        self.capabilities[name] = capability
        self.logger.info(f"📌 Registered capability: {name}")
        return self

    def get_capability(self, name: str) -> Optional[Capability]:
        """Get capability by name"""
        return self.capabilities.get(name)

    def list_capabilities(self) -> List[Capability]:
        """List all registered capabilities"""
        return list(self.capabilities.values())

    # ========================================================================
    # CONTEXT MANAGEMENT
    # ========================================================================

    def set_context(self, context: Dict[str, Any]) -> "BaseAgent":
        """Set execution context"""
        self.context = context
        self.logger.debug(f"📦 Context set: {list(context.keys())}")
        return self

    def update_context(self, **kwargs) -> "BaseAgent":
        """Update specific context values"""
        self.context.update(kwargs)
        return self

    def get_context(self, key: str, default: Any = None) -> Any:
        """Get context value"""
        return self.context.get(key, default)

    # ========================================================================
    # EXECUTION INTERFACE
    # ========================================================================

    async def execute(
        self,
        task: str,
        parameters: Dict[str, Any] = None,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Execute agent task.

        Args:
            task: Task name / capability to execute
            parameters: Task parameters
            context: Execution context

        Returns:
            Execution result with status and data
        """
        import time

        start_time = time.time()
        self.current_task = task
        self.status = AgentStatus.THINKING

        try:
            # Update context if provided
            if context:
                self.set_context(context)

            # Get capability
            capability = self.get_capability(task)
            if not capability:
                raise ValueError(f"Unknown capability: {task}")

            # Check context requirements
            if capability.requires_context and not self.context:
                raise ValueError(f"Capability {task} requires context")

            # Set status to executing
            self.status = AgentStatus.EXECUTING

            # Execute capability
            self.logger.info(f"🚀 Executing: {task}")
            result = await capability.execute(**(parameters or {}))

            # Calculate metrics
            duration = time.time() - start_time
            tokens_used = result.get("tokens_used", 0)
            cost = result.get("cost", 0)

            # Record success
            self.metrics.record_execution(
                duration=duration,
                tokens=tokens_used,
                cost=cost,
                success=True
            )

            self.status = AgentStatus.COMPLETE

            return {
                "success": True,
                "data": result,
                "duration_seconds": duration,
                "tokens_used": tokens_used,
                "cost": cost,
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            self.logger.error(f"❌ Execution failed: {e}", exc_info=True)

            duration = time.time() - start_time
            self.metrics.record_execution(
                duration=duration,
                tokens=0,
                cost=0,
                success=False
            )

            self.status = AgentStatus.ERROR

            return {
                "success": False,
                "error": str(e),
                "duration_seconds": duration,
                "timestamp": datetime.utcnow().isoformat()
            }

        finally:
            self.current_task = None
            self.status = AgentStatus.IDLE

    # ========================================================================
    # PERFORMANCE METRICS
    # ========================================================================

    def get_metrics(self) -> ExecutionMetrics:
        """Get performance metrics"""
        return self.metrics

    def get_metrics_dict(self) -> Dict[str, Any]:
        """Get metrics as dictionary"""
        metrics = self.metrics
        return {
            "executions": metrics.executions,
            "successes": metrics.successes,
            "failures": metrics.failures,
            "success_rate_percent": round(metrics.success_rate, 2),
            "avg_duration_seconds": round(metrics.avg_duration, 3),
            "avg_tokens_per_execution": metrics.avg_tokens_per_execution,
            "avg_cost_per_execution": round(metrics.avg_cost_per_execution, 4),
            "total_cost": round(metrics.total_cost, 4),
            "updated_at": metrics.updated_at.isoformat()
        }

    # ========================================================================
    # AGENT INFORMATION
    # ========================================================================

    def to_dict(self) -> Dict[str, Any]:
        """Convert agent to dictionary"""
        return {
            "id": str(self.id) if self.id else None,
            "name": self.name,
            "type": self.agent_type.value,
            "guild": self.guild_name,
            "description": self.description,
            "status": self.status.value,
            "personality_traits": self.personality_traits,
            "capabilities": [
                {
                    "name": cap.name,
                    "category": cap.category.value,
                    "description": cap.description
                }
                for cap in self.list_capabilities()
            ],
            "metrics": self.get_metrics_dict(),
            "model_config": self.model_config
        }

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} "
            f"name={self.name} "
            f"type={self.agent_type.value} "
            f"capabilities={len(self.capabilities)}>"
        )

    # ========================================================================
    # ABSTRACT METHODS (Override in subclasses)
    # ========================================================================

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize agent - called once during setup"""
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        """Shutdown agent - called during cleanup"""
        pass

# ============================================================================
# AGENT FACTORY
# ============================================================================

class AgentFactory:
    """Factory for creating agent instances"""

    _agent_registry: Dict[str, type] = {}

    @classmethod
    def register(cls, agent_type: str, agent_class: type):
        """Register agent class"""
        cls._agent_registry[agent_type] = agent_class

    @classmethod
    def create(cls, agent_type: str, **kwargs) -> BaseAgent:
        """Create agent instance"""
        if agent_type not in cls._agent_registry:
            raise ValueError(f"Unknown agent type: {agent_type}")

        agent_class = cls._agent_registry[agent_type]
        return agent_class(**kwargs)

    @classmethod
    def get_registered_types(cls) -> List[str]:
        """List registered agent types"""
        return list(cls._agent_registry.keys())
