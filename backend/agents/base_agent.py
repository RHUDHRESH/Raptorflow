"""
Abstract base classes for all agents and supervisors in RaptorFlow 2.0.

This module provides the foundational interfaces for the hierarchical multi-agent system:
- BaseAgent: Core interface for all agent types
- BaseSupervisor: Extended interface for supervisor agents
- BaseAgentEnhanced: Memory-enabled base agent
- BaseSupervisorEnhanced: Memory-enabled supervisor agent

Responsibilities:
- Define contract that all agents must implement
- Provide correlation ID propagation for distributed tracing
- Offer structured logging with contextual metadata
- Enforce separation between leaf agents and supervisor agents
- Provide integrated memory capabilities (Enhanced classes)
"""

from __future__ import annotations

import logging
import time
import asyncio
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from backend.utils.correlation import get_correlation_id
from backend.bus.raptor_bus import get_bus
from backend.services.memory_manager import MemoryManager


class BaseAgent(ABC):
    """
    Base contract for all agents in the RaptorFlow system.

    All agents (supervisors and leaf agents) must extend this class (or BaseAgentEnhanced)
    and implement the execute method.
    """

    def __init__(self, name: str):
        """
        Initialize base agent.

        Args:
            name: Unique agent identifier (e.g., "onboarding_supervisor", "hook_generator")
        """
        self.name = name
        self.logger = logging.getLogger(name)

    @abstractmethod
    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent's primary task.

        Args:
            payload: Input data containing task parameters, context, and metadata

        Returns:
            Dictionary containing:
                - status: "success" | "error" | "partial"
                - result: Agent-specific output data
                - metadata: Optional execution metadata
                - correlation_id: Propagated correlation ID
        """
        raise NotImplementedError(f"{self.name}.execute() must be implemented")

    def log(self, message: str, level: str = "info", **kwargs: Any) -> None:
        """
        Structured logging with automatic correlation ID injection.
        """
        correlation_id = get_correlation_id()
        log_data = {"correlation_id": correlation_id, **kwargs}

        log_method = getattr(self.logger, level.lower(), self.logger.info)
        log_method(message, extra=log_data)

    async def publish_event(self, event_type: str, payload: Dict[str, Any]) -> None:
        """
        Publish an event to the RaptorBus.
        """
        bus = await get_bus()
        await bus.publish(event_type, payload, correlation_id=get_correlation_id())


class BaseSupervisor(BaseAgent):
    """
    Base class for all supervisor agents that coordinate sub-agents.
    """

    def __init__(self, name: str):
        """
        Initialize supervisor agent.
        """
        super().__init__(name)
        self.sub_agents: Dict[str, BaseAgent] = {}

    def register_agent(self, agent_name: str, agent: BaseAgent) -> None:
        """
        Register a sub-agent that this supervisor can route tasks to.
        """
        self.sub_agents[agent_name] = agent
        self.log(f"Registered sub-agent: {agent_name}", level="debug")

    def get_agent(self, agent_name: str) -> Optional[BaseAgent]:
        """
        Retrieve a registered sub-agent by name.
        """
        return self.sub_agents.get(agent_name)

    def list_agents(self) -> list[str]:
        """
        Get list of all registered sub-agent names.
        """
        return list(self.sub_agents.keys())

    @abstractmethod
    async def execute(self, goal: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Coordinate sub-agents to achieve a high-level goal.
        """
        raise NotImplementedError(f"{self.name}.execute(goal, context) must be implemented")


class BaseAgentEnhanced(BaseAgent):
    """
    Memory-enhanced base agent class.

    Extends BaseAgent with memory capabilities, enabling agents to:
    - Recall relevant memories from past executions
    - Enrich task context with historical data and user preferences
    - Store execution results with performance metrics
    - Learn from user feedback over time
    """

    def __init__(
        self,
        name: str,
        memory: Optional[MemoryManager] = None,
        workspace_id: Optional[str] = None,
        auto_remember: bool = False
    ):
        """
        Initialize enhanced agent with memory.

        Args:
            name: Unique agent identifier
            memory: Optional MemoryManager instance (can be initialized later)
            workspace_id: Optional workspace ID
            auto_remember: If True, automatically store memories after execute
        """
        super().__init__(name=name)
        self.workspace_id = workspace_id
        self.auto_remember = auto_remember
        self._memory = memory
        
        if workspace_id and not memory:
            self._initialize_memory()

    def set_workspace(self, workspace_id: str) -> None:
        """Set workspace context and initialize memory if needed."""
        if workspace_id != self.workspace_id:
            self.workspace_id = workspace_id
            self._initialize_memory()
            self.log("Workspace context updated", workspace_id=workspace_id, level="debug")

    def _initialize_memory(self) -> None:
        """Initialize memory manager for current workspace."""
        if self.workspace_id:
            self._memory = MemoryManager(
                workspace_id=self.workspace_id,
                agent_name=self.name
            )

    @property
    def memory(self) -> MemoryManager:
        """Get memory manager instance."""
        if not self._memory:
            raise RuntimeError(
                f"{self.name}: Memory not initialized. Call set_workspace(workspace_id) first."
            )
        return self._memory

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute agent task with memory-enhanced context.
        """
        start_time = time.time()
        workspace_id = payload.get("workspace_id") or self.workspace_id
        
        if workspace_id:
            self.set_workspace(workspace_id)

        # If memory is not available or configured, fallback to simple execution
        if not self._memory:
            try:
                return await self._execute_with_memory(payload)
            except NotImplementedError:
                # Try standard _execute_core if _execute_with_memory is not implemented
                # This handles cases where subclasses implement _execute_core directly
                pass

        try:
            # Step 1: Recall relevant memories
            recalled_memories = []
            user_preferences = {}
            
            if self._memory:
                try:
                    self.log("Recalling relevant memories", level="debug")
                    recalled_memories = await self._recall_memories(payload)
                    user_preferences = await self.memory.get_user_preferences()
                except Exception as e:
                    self.log(f"Memory recall failed: {e}", level="warning")

            # Step 2: Enrich context
            enriched_context = self._enrich_context(
                payload=payload,
                recalled_memories=recalled_memories,
                user_preferences=user_preferences
            )

            # Step 3: Execute core task logic
            result = await self._execute_core(enriched_context)

            # Step 4: Calculate metrics & Store result
            execution_time_ms = (time.time() - start_time) * 1000
            
            if self.auto_remember and self._memory:
                try:
                    performance_metrics = {
                        "execution_time_ms": execution_time_ms,
                        "recalled_memory_count": len(recalled_memories),
                        **self._extract_performance_metrics(result)
                    }
                    
                    memory_id = await self._store_result(
                        payload=payload,
                        result=result,
                        performance_metrics=performance_metrics
                    )
                    
                    # Add metadata
                    if "metadata" not in result:
                        result["metadata"] = {}
                    result["metadata"]["memory_id"] = memory_id
                    
                except Exception as e:
                    self.log(f"Memory storage failed: {e}", level="warning")

            # Add execution timing
            if "metadata" not in result:
                result["metadata"] = {}
            result["metadata"]["execution_time_ms"] = execution_time_ms

            return result

        except Exception as e:
            execution_time_ms = (time.time() - start_time) * 1000
            self.log(f"Task execution failed: {str(e)}", level="error", exc_info=True)
            
            if self.auto_remember and self._memory:
                await self._store_error(payload, str(e), execution_time_ms)
                
            raise

    async def _execute_with_memory(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Legacy method support. Subclasses should implement _execute_core.
        """
        return await self._execute_core(payload)

    @abstractmethod
    async def _execute_core(self, enriched_context: Dict[str, Any]) -> Dict[str, Any]:
        """Core agent logic to be implemented by subclasses."""
        raise NotImplementedError(f"{self.name}._execute_core() must be implemented")

    def _get_task_type(self) -> str:
        """Get task type identifier. Can be overridden by subclasses."""
        return "general_task"

    def _create_input_summary(self, payload: Dict[str, Any]) -> str:
        """Create input summary for memory. Can be overridden."""
        return str(payload)[:200]

    def _create_output_summary(self, result: Dict[str, Any]) -> str:
        """Create output summary for memory. Can be overridden."""
        return str(result.get("result", result))[:200]

    async def _recall_memories(self, payload: Dict[str, Any]) -> List[Any]:
        search_query = self._create_input_summary(payload)
        return await self.memory.search(
            query=search_query,
            agent_name=self.name,
            task_type=self._get_task_type(),
            limit=5
        )

    def _enrich_context(
        self,
        payload: Dict[str, Any],
        recalled_memories: List[Any],
        user_preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        enriched = payload.copy()
        enriched["recalled_memories"] = recalled_memories
        enriched["user_preferences"] = user_preferences
        enriched["original_payload"] = payload
        return enriched

    async def _store_result(
        self,
        payload: Dict[str, Any],
        result: Dict[str, Any],
        performance_metrics: Dict[str, Any]
    ) -> str:
        input_summary = self._create_input_summary(payload)
        output_summary = self._create_output_summary(result)
        
        return await self.memory.remember(
            agent_name=self.name,
            task_type=self._get_task_type(),
            input_summary=input_summary,
            output_summary=output_summary,
            result=result,
            performance_metrics=performance_metrics,
            metadata=self._extract_metadata(payload)
        )

    async def _store_error(self, payload: Dict[str, Any], error_msg: str, time_ms: float) -> None:
        try:
            await self.memory.remember(
                agent_name=self.name,
                task_type=f"{self._get_task_type()}_error",
                input_summary=self._create_input_summary(payload),
                output_summary=f"Error: {error_msg}",
                result={"error": error_msg},
                performance_metrics={"execution_time_ms": time_ms, "success": False}
            )
        except Exception:
            pass

    def _extract_performance_metrics(self, result: Dict[str, Any]) -> Dict[str, Any]:
        metrics = {}
        if "confidence" in result:
            metrics["confidence"] = result["confidence"]
        return metrics

    def _extract_metadata(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        meta = {}
        for key in ["workspace_id", "user_id", "cohort_id", "campaign_id"]:
            if key in payload:
                meta[key] = payload[key]
        return meta

    async def remember(
        self,
        context: Dict[str, Any],
        result: Dict[str, Any],
        success_score: Optional[float] = None,
        memory_type: str = "success",
        tags: Optional[List[str]] = None,
    ) -> str:
        """Convenience method to store memory manually."""
        if success_score is None:
            success_score = result.get("success_score", 0.5)
            
        return await self.memory.remember(
            context=context,
            result=result,
            success_score=success_score,
            memory_type=memory_type,
            tags=tags,
            agent_name=self.name
        )
        
    async def recall(
        self,
        query: str,
        memory_types: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        min_success_score: float = 0.6,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """Convenience method to recall memories manually."""
        return await self.memory.search(
            query=query,
            memory_types=memory_types or ["success"],
            tags=tags,
            min_success_score=min_success_score,
            top_k=top_k,
            agent_name=self.name
        )
        
    async def learn_from_feedback(self, memory_id: str, feedback: Dict[str, Any]) -> bool:
        """Update memory with feedback."""
        return await self.memory.update_feedback(memory_id=memory_id, feedback=feedback)


class BaseSupervisorEnhanced(BaseSupervisor):
    """
    Enhanced base supervisor with integrated memory capabilities.
    """

    def __init__(
        self,
        name: str,
        memory: Optional[MemoryManager] = None,
        workspace_id: Optional[str] = None,
        auto_remember: bool = False
    ):
        super().__init__(name)
        self.workspace_id = workspace_id
        self.auto_remember = auto_remember
        self._memory = memory
        
        if workspace_id and not memory:
            self._initialize_memory()

    def set_workspace(self, workspace_id: str) -> None:
        if workspace_id != self.workspace_id:
            self.workspace_id = workspace_id
            self._initialize_memory()
            self.log("Workspace context updated", workspace_id=workspace_id, level="debug")

    def _initialize_memory(self) -> None:
        if self.workspace_id:
            self._memory = MemoryManager(
                workspace_id=self.workspace_id,
                agent_name=self.name
            )

    @property
    def memory(self) -> MemoryManager:
        if not self._memory:
            raise RuntimeError(f"{self.name}: Memory not initialized.")
        return self._memory
    
    @memory.setter
    def memory(self, value: MemoryManager):
        self._memory = value

    async def invoke_agent(
        self,
        agent_name: str,
        payload: Dict[str, Any],
        pass_memory: bool = True
    ) -> Dict[str, Any]:
        """
        Invoke a sub-agent with optional memory context passing.
        """
        agent = self.get_agent(agent_name)
        if not agent:
            raise ValueError(f"Agent '{agent_name}' not registered with supervisor '{self.name}'")

        self.log(f"Invoking sub-agent: {agent_name}", level="debug")
        start_time = time.time()

        try:
            # If passing memory and sub-agent supports it, set workspace
            if pass_memory and hasattr(agent, 'set_workspace') and self.workspace_id:
                agent.set_workspace(self.workspace_id)

            result = await agent.execute(payload)
            execution_time_ms = (time.time() - start_time) * 1000

            self.log(
                f"Sub-agent '{agent_name}' completed in {execution_time_ms:.2f}ms",
                agent_name=agent_name,
                status=result.get("status", "unknown")
            )
            return result

        except Exception as e:
            self.log(f"Sub-agent '{agent_name}' failed: {e}", level="error", exc_info=True)
            raise

    async def execute(self, goal: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute supervisor task with automatic memory handling.
        """
        workspace_id = context.get("workspace_id")
        if workspace_id:
            self.set_workspace(workspace_id)

        result = await self._execute_with_memory(goal, context)

        if self.auto_remember and self._memory:
            try:
                await self.remember(
                    context={"goal": goal, **context},
                    result=result
                )
            except Exception as e:
                self.log(f"Auto-remember failed: {e}", level="warning")

        return result

    async def _execute_with_memory(self, goal: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Subclasses should implement this method.
        """
        raise NotImplementedError(f"{self.name}._execute_with_memory() must be implemented")
    
    async def remember(
        self,
        context: Dict[str, Any],
        result: Dict[str, Any],
        success_score: Optional[float] = None,
        memory_type: str = "success",
        tags: Optional[List[str]] = None,
    ) -> str:
        """Store supervisor memory."""
        if success_score is None:
            success_score = result.get("success_score", 0.5)
            
        return await self.memory.remember(
            context=context,
            result=result,
            success_score=success_score,
            memory_type=memory_type,
            tags=tags,
            agent_name=self.name
        )
