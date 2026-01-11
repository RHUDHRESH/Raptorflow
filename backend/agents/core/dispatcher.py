"""
AgentDispatcher for Raptorflow agent system.
Handles intelligent routing and dispatching of requests to appropriate agents.
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from ..base import BaseAgent
from ..config import ModelTier
from ..exceptions import RoutingError, ValidationError
from ..state import AgentState
from .metrics import AgentMetricsCollector
from .registry import AgentRegistry

logger = logging.getLogger(__name__)


class DispatchStrategy(Enum):
    """Dispatch strategies for agent selection."""

    ROUND_ROBIN = "round_robin"
    LOAD_BALANCED = "load_balanced"
    PRIORITY_BASED = "priority_based"
    CAPABILITY_MATCH = "capability_match"
    COST_OPTIMIZED = "cost_optimized"


@dataclass
class DispatchRequest:
    """Request for agent dispatch."""

    request_type: str
    request_data: Dict[str, Any]
    workspace_id: str
    user_id: str
    priority: str = "normal"  # low, normal, high, urgent
    strategy: str = "capability_match"
    constraints: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class DispatchResult:
    """Result of agent dispatch."""

    agent_name: str
    agent_id: str
    execution_id: str
    strategy_used: str
    dispatch_time: datetime
    estimated_duration: float
    confidence_score: float
    routing_metadata: Dict[str, Any]


@dataclass
class AgentCapability:
    """Agent capability definition."""

    agent_name: str
    capabilities: List[str]
    model_tier: ModelTier
    max_concurrent: int
    current_load: int
    avg_response_time: float
    success_rate: float
    cost_per_request: float
    last_used: datetime
    health_status: str


class AgentDispatcher:
    """Intelligent agent dispatcher for routing requests to optimal agents."""

    def __init__(self, registry: AgentRegistry, metrics: AgentMetricsCollector):
        self.registry = registry
        self.metrics = metrics
        self._dispatch_history: List[DispatchResult] = []
        self._agent_capabilities: Dict[str, AgentCapability] = {}
        self._round_robin_counters: Dict[str, int] = {}
        self._dispatch_lock = asyncio.Lock()

        # Dispatch strategy weights
        self.strategy_weights = {
            "capability_match": 0.4,
            "load_balanced": 0.25,
            "cost_optimized": 0.2,
            "priority_based": 0.15,
        }

        # Request type to capability mapping
        self.request_capability_map = {
            "content_generation": ["content_gen", "writing", "creativity"],
            "data_analysis": ["analytics", "data_processing", "insights"],
            "market_research": ["research", "analysis", "market_intelligence"],
            "customer_service": ["communication", "support", "problem_solving"],
            "strategy_planning": ["strategy", "planning", "business_intelligence"],
            "persona_simulation": ["psychology", "behavior_analysis", "user_modeling"],
            "trend_analysis": ["trend_detection", "forecasting", "market_analysis"],
            "quality_assurance": ["quality_check", "review", "validation"],
            "competitor_intelligence": ["competitive_analysis", "market_research"],
            "social_media": ["content_creation", "social_strategy", "engagement"],
            "email_marketing": ["email_content", "campaign_strategy", "copywriting"],
            "blog_content": ["writing", "seo", "content_strategy"],
        }

    async def dispatch(self, request: DispatchRequest) -> DispatchResult:
        """Dispatch request to optimal agent."""
        try:
            async with self._dispatch_lock:
                # Validate request
                self._validate_dispatch_request(request)

                # Get available agents
                available_agents = await self._get_available_agents(request)

                if not available_agents:
                    raise RoutingError("No available agents for request")

                # Select optimal agent based on strategy
                selected_agent = await self._select_agent(available_agents, request)

                # Create dispatch result
                dispatch_result = self._create_dispatch_result(selected_agent, request)

                # Update agent capabilities
                await self._update_agent_load(selected_agent.agent_name, 1)

                # Record dispatch
                await self._record_dispatch(dispatch_result)

                # Update metrics
                await self.metrics.record_dispatch(dispatch_result)

                return dispatch_result

        except Exception as e:
            logger.error(f"Dispatch failed: {e}")
            raise RoutingError(f"Dispatch failed: {str(e)}")

    def _validate_dispatch_request(self, request: DispatchRequest):
        """Validate dispatch request."""
        if not request.request_type:
            raise ValidationError("Request type is required")

        if not request.workspace_id:
            raise ValidationError("Workspace ID is required")

        if not request.user_id:
            raise ValidationError("User ID is required")

        valid_strategies = [s.value for s in DispatchStrategy]
        if request.strategy not in valid_strategies:
            raise ValidationError(f"Invalid dispatch strategy: {request.strategy}")

        valid_priorities = ["low", "normal", "high", "urgent"]
        if request.priority not in valid_priorities:
            raise ValidationError(f"Invalid priority: {request.priority}")

    async def _get_available_agents(
        self, request: DispatchRequest
    ) -> List[AgentCapability]:
        """Get list of available agents for request."""
        available_agents = []

        # Get required capabilities
        required_capabilities = self._get_required_capabilities(request.request_type)

        # Filter agents by capabilities and availability
        for agent_name, capability in self._agent_capabilities.items():
            # Check if agent has required capabilities
            if not self._has_required_capabilities(capability, required_capabilities):
                continue

            # Check if agent is healthy
            if capability.health_status != "healthy":
                continue

            # Check if agent has capacity
            if capability.current_load >= capability.max_concurrent:
                continue

            # Check constraints
            if not self._meets_constraints(capability, request.constraints):
                continue

            available_agents.append(capability)

        return available_agents

    def _get_required_capabilities(self, request_type: str) -> List[str]:
        """Get required capabilities for request type."""
        return self.request_capability_map.get(request_type, ["general"])

    def _has_required_capabilities(
        self, capability: AgentCapability, required: List[str]
    ) -> bool:
        """Check if agent has required capabilities."""
        agent_caps = set(cap.capabilities)
        required_caps = set(required)
        return required_caps.issubset(agent_caps)

    def _meets_constraints(
        self, capability: AgentCapability, constraints: Optional[Dict[str, Any]]
    ) -> bool:
        """Check if agent meets constraints."""
        if not constraints:
            return True

        # Check model tier constraint
        if "model_tier" in constraints:
            required_tier = constraints["model_tier"]
            if capability.model_tier.value != required_tier:
                return False

        # Check cost constraint
        if "max_cost" in constraints:
            max_cost = constraints["max_cost"]
            if capability.cost_per_request > max_cost:
                return False

        # Check response time constraint
        if "max_response_time" in constraints:
            max_time = constraints["max_response_time"]
            if capability.avg_response_time > max_time:
                return False

        # Check success rate constraint
        if "min_success_rate" in constraints:
            min_rate = constraints["min_success_rate"]
            if capability.success_rate < min_rate:
                return False

        return True

    async def _select_agent(
        self, agents: List[AgentCapability], request: DispatchRequest
    ) -> AgentCapability:
        """Select optimal agent based on strategy."""
        strategy = DispatchStrategy(request.strategy)

        if strategy == DispatchStrategy.ROUND_ROBIN:
            return self._select_round_robin(agents, request.request_type)
        elif strategy == DispatchStrategy.LOAD_BALANCED:
            return self._select_load_balanced(agents)
        elif strategy == DispatchStrategy.PRIORITY_BASED:
            return self._select_priority_based(agents, request.priority)
        elif strategy == DispatchStrategy.CAPABILITY_MATCH:
            return self._select_capability_match(agents, request.request_type)
        elif strategy == DispatchStrategy.COST_OPTIMIZED:
            return self._select_cost_optimized(agents)
        else:
            # Default to capability match
            return self._select_capability_match(agents, request.request_type)

    def _select_round_robin(
        self, agents: List[AgentCapability], request_type: str
    ) -> AgentCapability:
        """Select agent using round-robin strategy."""
        # Get counter for request type
        if request_type not in self._round_robin_counters:
            self._round_robin_counters[request_type] = 0

        # Select agent
        index = self._round_robin_counters[request_type] % len(agents)
        selected_agent = agents[index]

        # Update counter
        self._round_robin_counters[request_type] += 1

        return selected_agent

    def _select_load_balanced(self, agents: List[AgentCapability]) -> AgentCapability:
        """Select agent with lowest load."""
        return min(agents, key=lambda a: a.current_load / a.max_concurrent)

    def _select_priority_based(
        self, agents: List[AgentCapability], priority: str
    ) -> AgentCapability:
        """Select agent based on request priority."""
        if priority == "urgent":
            # Select fastest agent
            return min(agents, key=lambda a: a.avg_response_time)
        elif priority == "high":
            # Select agent with highest success rate
            return max(agents, key=lambda a: a.success_rate)
        else:
            # Select agent with best balance
            return min(agents, key=lambda a: (a.current_load, a.avg_response_time))

    def _select_capability_match(
        self, agents: List[AgentCapability], request_type: str
    ) -> AgentCapability:
        """Select agent with best capability match."""
        required_capabilities = self._get_required_capabilities(request_type)

        best_agent = None
        best_score = 0

        for agent in agents:
            score = 0
            for capability in required_capabilities:
                if capability in agent.capabilities:
                    score += 1

            # Factor in success rate and load
            score = (
                score
                * agent.success_rate
                * (1 - agent.current_load / agent.max_concurrent)
            )

            if score > best_score:
                best_score = score
                best_agent = agent

        return best_agent or agents[0]

    def _select_cost_optimized(self, agents: List[AgentCapability]) -> AgentCapability:
        """Select agent with lowest cost."""
        return min(agents, key=lambda a: a.cost_per_request)

    def _create_dispatch_result(
        self, agent: AgentCapability, request: DispatchRequest
    ) -> DispatchResult:
        """Create dispatch result."""
        execution_id = f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(request.workspace_id) % 10000}"

        return DispatchResult(
            agent_name=agent.agent_name,
            agent_id=agent.agent_name,
            execution_id=execution_id,
            strategy_used=request.strategy,
            dispatch_time=datetime.now(),
            estimated_duration=agent.avg_response_time,
            confidence_score=self._calculate_confidence_score(agent, request),
            routing_metadata={
                "selected_capabilities": [
                    cap
                    for cap in agent.capabilities
                    if cap in self._get_required_capabilities(request.request_type)
                ],
                "agent_load": agent.current_load,
                "agent_capacity": agent.max_concurrent,
                "estimated_cost": agent.cost_per_request,
            },
        )

    def _calculate_confidence_score(
        self, agent: AgentCapability, request: DispatchRequest
    ) -> float:
        """Calculate confidence score for dispatch decision."""
        # Base score from success rate
        base_score = agent.success_rate

        # Adjust for load
        load_factor = 1 - (agent.current_load / agent.max_concurrent)

        # Adjust for capability match
        required_caps = self._get_required_capabilities(request.request_type)
        match_score = len(
            [cap for cap in required_caps if cap in agent.capabilities]
        ) / len(required_caps)

        # Adjust for priority
        priority_multiplier = {
            "urgent": 1.2,
            "high": 1.1,
            "normal": 1.0,
            "low": 0.9,
        }.get(request.priority, 1.0)

        # Calculate final score
        confidence = base_score * load_factor * match_score * priority_multiplier

        return min(confidence, 1.0)

    async def _update_agent_load(self, agent_name: str, load_delta: int):
        """Update agent load."""
        if agent_name in self._agent_capabilities:
            self._agent_capabilities[agent_name].current_load += load_delta

    async def _record_dispatch(self, result: DispatchResult):
        """Record dispatch in history."""
        self._dispatch_history.append(result)

        # Keep only last 1000 dispatches
        if len(self._dispatch_history) > 1000:
            self._dispatch_history = self._dispatch_history[-1000:]

    async def update_agent_capabilities(
        self, agent_name: str, capabilities: Dict[str, Any]
    ):
        """Update agent capabilities."""
        capability = AgentCapability(
            agent_name=agent_name,
            capabilities=capabilities.get("capabilities", []),
            model_tier=ModelTier(capabilities.get("model_tier", "flash")),
            max_concurrent=capabilities.get("max_concurrent", 5),
            current_load=capabilities.get("current_load", 0),
            avg_response_time=capabilities.get("avg_response_time", 1.0),
            success_rate=capabilities.get("success_rate", 0.95),
            cost_per_request=capabilities.get("cost_per_request", 0.01),
            last_used=capabilities.get("last_used", datetime.now()),
            health_status=capabilities.get("health_status", "healthy"),
        )

        self._agent_capabilities[agent_name] = capability

    async def get_dispatch_stats(self) -> Dict[str, Any]:
        """Get dispatch statistics."""
        if not self._dispatch_history:
            return {"total_dispatches": 0}

        recent_dispatches = self._dispatch_history[-100:]  # Last 100 dispatches

        strategy_usage = {}
        for dispatch in recent_dispatches:
            strategy = dispatch.strategy_used
            strategy_usage[strategy] = strategy_usage.get(strategy, 0) + 1

        avg_confidence = sum(d.confidence_score for d in recent_dispatches) / len(
            recent_dispatches
        )

        return {
            "total_dispatches": len(self._dispatch_history),
            "recent_dispatches": len(recent_dispatches),
            "strategy_usage": strategy_usage,
            "average_confidence": avg_confidence,
            "agents_available": len(self._agent_capabilities),
            "healthy_agents": len(
                [
                    a
                    for a in self._agent_capabilities.values()
                    if a.health_status == "healthy"
                ]
            ),
        }

    async def get_agent_load(self) -> Dict[str, Dict[str, Any]]:
        """Get current load for all agents."""
        load_info = {}

        for agent_name, capability in self._agent_capabilities.items():
            load_info[agent_name] = {
                "current_load": capability.current_load,
                "max_concurrent": capability.max_concurrent,
                "load_percentage": (capability.current_load / capability.max_concurrent)
                * 100,
                "health_status": capability.health_status,
                "avg_response_time": capability.avg_response_time,
            }

        return load_info
