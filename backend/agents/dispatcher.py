"""
Agent Dispatcher for routing requests to appropriate agents.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from .base import BaseAgent
from .config import ModelTier
from .exceptions import RoutingError, ValidationError, WorkspaceError
from .routing.pipeline import RoutingDecision, RoutingPipeline
from .specialists.analytics_agent import AnalyticsAgent
from .specialists.blackbox_strategist import BlackboxStrategist
from .specialists.campaign_planner import CampaignPlanner
from .specialists.content_creator import ContentCreator
from .specialists.daily_wins import DailyWinsGenerator
from .specialists.email_specialist import EmailSpecialist
from .specialists.evidence_processor import EvidenceProcessor
from .specialists.fact_extractor import FactExtractor
from .specialists.icp_architect import ICPArchitect
from .specialists.market_research import MarketResearch
from .specialists.move_strategist import MoveStrategist
from .specialists.onboarding_orchestrator import OnboardingOrchestrator
from .state import AgentState, add_message, create_initial_state, update_state

logger = logging.getLogger(__name__)


class AgentRegistry:
    """Registry for managing available agents."""

    def __init__(self):
        self._agents: Dict[str, BaseAgent] = {}
        self._agent_metadata: Dict[str, Dict[str, Any]] = {}

        # Register default agents
        self._register_default_agents()

    def _register_default_agents(self):
        """Register default specialist agents."""
        # Register core agents
        onboarding_agent = OnboardingOrchestrator()
        self.register_agent(onboarding_agent)

        # Register business strategy agents
        move_agent = MoveStrategist()
        self.register_agent(move_agent)

        content_agent = ContentCreator()
        self.register_agent(content_agent)

        blackbox_agent = BlackboxStrategist()
        self.register_agent(blackbox_agent)

        # Register research and analytics agents
        research_agent = MarketResearch()
        self.register_agent(research_agent)

        analytics_agent = AnalyticsAgent()
        self.register_agent(analytics_agent)

        # Register content and marketing agents
        email_agent = EmailSpecialist()
        self.register_agent(email_agent)

        # Register campaign and daily wins agents
        campaign_agent = CampaignPlanner()
        self.register_agent(campaign_agent)

        daily_wins_agent = DailyWinsGenerator()
        self.register_agent(daily_wins_agent)

        # Register ICP and foundation agents
        icp_agent = ICPArchitect()
        self.register_agent(icp_agent)

        evidence_agent = EvidenceProcessor()
        self.register_agent(evidence_agent)

        fact_agent = FactExtractor()
        self.register_agent(fact_agent)

    def register_agent(self, agent: BaseAgent):
        """Register an agent in the registry."""
        self._agents[agent.name] = agent
        self._agent_metadata[agent.name] = agent._get_agent_info()
        logger.info(f"Registered agent: {agent.name}")

    def get_agent(self, name: str) -> Optional[BaseAgent]:
        """Get an agent by name."""
        return self._agents.get(name)

    def get_all_agents(self) -> Dict[str, BaseAgent]:
        """Get all registered agents."""
        return self._agents.copy()

    def get_agent_metadata(self, name: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a specific agent."""
        return self._agent_metadata.get(name)

    def list_agents(self) -> List[str]:
        """List all registered agent names."""
        return list(self._agents.keys())

    def validate_agent_exists(self, agent_name: str) -> bool:
        """Check if an agent exists."""
        return agent_name in self._agents


class AgentDispatcher:
    """Dispatches requests to appropriate agents."""

    def __init__(self):
        self.registry = AgentRegistry()
        self.routing_pipeline = RoutingPipeline()
        self.request_history: List[Dict[str, Any]] = []

        # Dispatcher configuration
        self.max_history = 1000
        self.default_agent = "GeneralAgent"
        self.fallback_agent = "OnboardingOrchestrator"

    async def dispatch(
        self,
        request: str,
        workspace_id: str,
        user_id: str,
        session_id: str,
        context: Optional[Dict[str, Any]] = None,
        agent_hint: Optional[str] = None,
        fast_mode: bool = False,
    ) -> Dict[str, Any]:
        """Dispatch a request to the appropriate agent."""
        start_time = datetime.now()

        try:
            # Validate inputs
            self._validate_dispatch_request(request, workspace_id, user_id, session_id)

            # Create initial state
            state = create_initial_state(
                workspace_id=workspace_id, user_id=user_id, session_id=session_id
            )

            # Add context if provided
            if context:
                state = update_state(state, **context)

            # Add user message
            state = add_message(state, "user", request)

            # Determine target agent
            target_agent = await self._determine_target_agent(
                request, state, agent_hint, fast_mode
            )

            # Get agent instance
            agent = self.registry.get_agent(target_agent)
            if not agent:
                # Fallback to OnboardingOrchestrator for unknown agents
                logger.warning(f"Agent '{target_agent}' not found, using fallback")
                agent = self.registry.get_agent(self.fallback_agent)
                if not agent:
                    raise RoutingError(f"No agent available: {target_agent}")

            # Add system message about routing
            state = add_message(
                state, "system", f"Request routed to {target_agent} agent"
            )

            # Execute agent
            result_state = await agent.execute(state)

            # Calculate execution metrics
            execution_time = (datetime.now() - start_time).total_seconds()

            # Record request in history
            self._record_request(
                request=request,
                workspace_id=workspace_id,
                user_id=user_id,
                session_id=session_id,
                agent_name=target_agent,
                execution_time=execution_time,
                success=result_state.get("error") is None,
                routing_decision=getattr(
                    result_state.get("routing_decision"), "to_dict", lambda: {}
                )(),
            )

            # Prepare response
            response = {
                "success": result_state.get("error") is None,
                "agent": target_agent,
                "workspace_id": workspace_id,
                "user_id": user_id,
                "session_id": session_id,
                "execution_time_seconds": execution_time,
                "timestamp": datetime.now().isoformat(),
                "routing_decision": result_state.get("routing_decision"),
                "state": result_state,
            }

            if result_state.get("error"):
                response["error"] = result_state["error"]
                response["error_code"] = "AGENT_EXECUTION_FAILED"
            else:
                response["output"] = result_state.get("output")

            return response

        except Exception as e:
            logger.error(f"Dispatch failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_code": "DISPATCH_FAILED",
                "workspace_id": workspace_id,
                "user_id": user_id,
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
            }

    async def _determine_target_agent(
        self,
        request: str,
        state: AgentState,
        agent_hint: Optional[str] = None,
        fast_mode: bool = False,
    ) -> str:
        """Determine the target agent for the request."""
        # If agent hint is provided, use it
        if agent_hint:
            agent = self.registry.get_agent(agent_hint)
            if agent:
                logger.info(f"Using hinted agent: {agent_hint}")
                return agent_hint
            else:
                logger.warning(f"Hinted agent '{agent_hint}' not found")

        # Use routing pipeline to determine agent
        try:
            routing_decision = await self.routing_pipeline.route(request, fast_mode)

            # Extract agent name from routing decision
            target_agent = routing_decision.target_agent

            # Validate agent exists
            if not self.registry.validate_agent_exists(target_agent):
                logger.warning(
                    f"Routed agent '{target_agent}' not found, using fallback"
                )
                return self.fallback_agent

            logger.info(f"Routed to agent: {target_agent}")
            return target_agent

        except Exception as e:
            logger.error(f"Routing pipeline failed: {e}")
            return self.fallback_agent

    def _validate_dispatch_request(
        self, request: str, workspace_id: str, user_id: str, session_id: str
    ):
        """Validate dispatch request parameters."""
        if not request or not request.strip():
            raise ValidationError("Request cannot be empty")

        if not workspace_id or not workspace_id.strip():
            raise ValidationError("Workspace ID is required")

        if not user_id or not user_id.strip():
            raise ValidationError("User ID is required")

        if not session_id or not session_id.strip():
            raise ValidationError("Session ID is required")

        # Validate workspace ID format
        if len(workspace_id) < 3:
            raise ValidationError("Workspace ID must be at least 3 characters")

        # Validate user ID format
        if len(user_id) < 3:
            raise ValidationError("User ID must be at least 3 characters")

        # Validate session ID format
        if len(session_id) < 3:
            raise ValidationError("Session ID must be at least 3 characters")

    def _record_request(
        self,
        request: str,
        workspace_id: str,
        user_id: str,
        session_id: str,
        agent_name: str,
        execution_time: float,
        success: bool,
        routing_decision: Dict[str, Any],
    ):
        """Record request in history."""
        request_record = {
            "timestamp": datetime.now().isoformat(),
            "request": request,
            "workspace_id": workspace_id,
            "user_id": user_id,
            "session_id": session_id,
            "agent_name": agent_name,
            "execution_time_seconds": execution_time,
            "success": success,
            "routing_decision": routing_decision,
        }

        self.request_history.append(request_record)

        # Trim history if too long
        if len(self.request_history) > self.max_history:
            self.request_history = self.request_history[-self.max_history :]

    def get_request_history(
        self,
        workspace_id: Optional[str] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get request history with optional filtering."""
        history = self.request_history.copy()

        # Apply filters
        if workspace_id:
            history = [req for req in history if req["workspace_id"] == workspace_id]

        if user_id:
            history = [req for req in history if req["user_id"] == user_id]

        if session_id:
            history = [req for req in history if req["session_id"] == session_id]

        # Sort by timestamp (most recent first) and limit
        history.sort(key=lambda x: x["timestamp"], reverse=True)

        return history[:limit]

    def get_dispatcher_stats(self) -> Dict[str, Any]:
        """Get dispatcher statistics."""
        total_requests = len(self.request_history)
        successful_requests = sum(1 for req in self.request_history if req["success"])

        # Calculate average execution time
        execution_times = [
            req["execution_time_seconds"] for req in self.request_history
        ]
        avg_execution_time = (
            sum(execution_times) / len(execution_times) if execution_times else 0
        )

        # Agent usage statistics
        agent_usage = {}
        for req in self.request_history:
            agent_name = req["agent_name"]
            agent_usage[agent_name] = agent_usage.get(agent_name, 0) + 1

        return {
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "success_rate": (
                (successful_requests / total_requests * 100)
                if total_requests > 0
                else 0
            ),
            "average_execution_time": avg_execution_time,
            "agent_usage": agent_usage,
            "registered_agents": self.registry.list_agents(),
            "max_history": self.max_history,
            "current_history_size": len(self.request_history),
        }

    def get_agent_info(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about an agent."""
        agent = self.registry.get_agent(agent_name)
        if not agent:
            return None

        metadata = self.registry.get_agent_metadata(agent_name)

        # Add usage statistics
        agent_requests = [
            req for req in self.request_history if req["agent_name"] == agent_name
        ]

        return {
            **metadata,
            "usage_stats": {
                "total_requests": len(agent_requests),
                "successful_requests": sum(
                    1 for req in agent_requests if req["success"]
                ),
                "average_execution_time": (
                    sum(req["execution_time_seconds"] for req in agent_requests)
                    / len(agent_requests)
                    if agent_requests
                    else 0
                ),
            },
        }

    def clear_history(self):
        """Clear request history."""
        self.request_history.clear()
        logger.info("Request history cleared")

    def get_health_status(self) -> Dict[str, Any]:
        """Get dispatcher health status."""
        try:
            # Check registry
            agents = self.registry.list_agents()

            # Check routing pipeline
            routing_stats = self.routing_pipeline.get_pipeline_stats()

            # Check request history
            recent_requests = self.get_request_history(limit=10)

            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "registered_agents": len(agents),
                "routing_pipeline": routing_stats,
                "recent_requests": len(recent_requests),
                "total_requests": len(self.request_history),
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
            }
