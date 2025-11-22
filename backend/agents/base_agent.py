"""
Abstract base classes for all agents and supervisors in RaptorFlow 2.0.

This module provides the foundational interfaces for the hierarchical multi-agent system:
- BaseAgent: Core interface for all agent types (Tier 0, 1, and 2)
- BaseSupervisor: Extended interface for supervisor agents that coordinate sub-agents

Responsibilities:
- Define contract that all agents must implement
- Provide correlation ID propagation for distributed tracing
- Offer structured logging with contextual metadata
- Enforce separation between leaf agents and supervisor agents

Assumptions:
- Sub-agents must be registered before supervisor can route to them
- All agents operate asynchronously (async/await)
- Correlation IDs are managed at the request middleware level
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from backend.utils.correlation import get_correlation_id


class BaseAgent(ABC):
    """
    Base contract for all agents in the RaptorFlow system.

    All agents (supervisors and leaf agents) must extend this class and implement
    the execute method. This ensures a consistent interface across the entire
    multi-agent hierarchy.

    Attributes:
        name: Unique identifier for the agent (used in logging and routing)
        logger: Configured logger instance with agent name

    Usage:
        class MyAgent(BaseAgent):
            async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
                self.log("Processing request")
                # Agent logic here
                return {"status": "success", "result": result}
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

        This is the main entry point for all agents. Implementations should:
        1. Validate the payload
        2. Perform the agent's core logic
        3. Return a structured result with status and data

        Args:
            payload: Input data containing task parameters, context, and metadata

        Returns:
            Dictionary containing:
                - status: "success" | "error" | "partial"
                - result: Agent-specific output data
                - metadata: Optional execution metadata (timing, tokens used, etc.)
                - correlation_id: Propagated correlation ID for tracing

        Raises:
            NotImplementedError: Must be implemented by subclasses
        """
        raise NotImplementedError(f"{self.name}.execute() must be implemented")

    def log(self, message: str, level: str = "info", **kwargs: Any) -> None:
        """
        Structured logging with automatic correlation ID injection.

        This method automatically includes the current request's correlation ID
        in all log messages, enabling distributed tracing across the agent hierarchy.

        Args:
            message: Log message text
            level: Log level (debug, info, warning, error, critical)
            **kwargs: Additional structured fields to include in log

        Example:
            self.log("Generated 5 hook variants", hook_count=5, persona_id="p123")
        """
        correlation_id = get_correlation_id()
        log_data = {"correlation_id": correlation_id, **kwargs}

        log_method = getattr(self.logger, level.lower(), self.logger.info)
        log_method(message, extra=log_data)


class BaseSupervisor(BaseAgent):
    """
    Base class for all supervisor agents that coordinate sub-agents.

    Supervisors are higher-level agents that:
    - Maintain a registry of sub-agents
    - Route tasks to appropriate sub-agents based on goals
    - Aggregate results from multiple sub-agents
    - Propagate correlation IDs throughout the execution chain

    Attributes:
        name: Supervisor identifier
        sub_agents: Dictionary mapping agent names to agent instances

    Sub-agent Registration:
        Supervisors must register their sub-agents before routing tasks:

        class MySupervisor(BaseSupervisor):
            def __init__(self):
                super().__init__("my_supervisor")
                self.register_agent("agent1", Agent1())
                self.register_agent("agent2", Agent2())

    Usage:
        class OnboardingSupervisor(BaseSupervisor):
            async def execute(self, goal: str, context: Dict[str, Any]) -> Dict[str, Any]:
                # Determine which sub-agent to invoke
                if "generate_questions" in goal:
                    return await self.sub_agents["question_agent"].execute(context)
                # ...
    """

    def __init__(self, name: str):
        """
        Initialize supervisor agent.

        Args:
            name: Unique supervisor identifier (e.g., "strategy_supervisor")
        """
        super().__init__(name)
        self.sub_agents: Dict[str, BaseAgent] = {}

    def register_agent(self, agent_name: str, agent: BaseAgent) -> None:
        """
        Register a sub-agent that this supervisor can route tasks to.

        Args:
            agent_name: Unique identifier for the agent (used in routing)
            agent: Agent instance to register

        Example:
            supervisor.register_agent("hook_generator", HookGeneratorAgent())
        """
        self.sub_agents[agent_name] = agent
        self.log(f"Registered sub-agent: {agent_name}", level="debug")

    def get_agent(self, agent_name: str) -> Optional[BaseAgent]:
        """
        Retrieve a registered sub-agent by name.

        Args:
            agent_name: Name of the agent to retrieve

        Returns:
            The agent instance, or None if not registered
        """
        return self.sub_agents.get(agent_name)

    def list_agents(self) -> list[str]:
        """
        Get list of all registered sub-agent names.

        Returns:
            List of agent names
        """
        return list(self.sub_agents.keys())

    @abstractmethod
    async def execute(self, goal: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Coordinate sub-agents to achieve a high-level goal.

        Supervisors analyze the goal, determine which sub-agents to invoke,
        route tasks appropriately, and aggregate results.

        Args:
            goal: High-level objective (e.g., "generate campaign strategy")
            context: Execution context containing:
                - workspace_id: User's workspace
                - user_profile: Onboarding data
                - icps: Available customer profiles
                - previous_results: Output from prior stages
                - correlation_id: Request tracing ID

        Returns:
            Dictionary containing:
                - status: "success" | "error" | "partial"
                - result: Aggregated output from sub-agents
                - agents_invoked: List of sub-agents that were called
                - correlation_id: Propagated correlation ID

        Raises:
            NotImplementedError: Must be implemented by subclasses
        """
        raise NotImplementedError(f"{self.name}.execute(goal, context) must be implemented")
