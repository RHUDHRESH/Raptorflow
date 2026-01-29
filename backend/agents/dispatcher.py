"""
Enhanced Agent Dispatcher for routing requests to appropriate agents.
Includes comprehensive health monitoring, metrics collection, and error recovery.
"""

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from .core.metrics import (
    RequestStatus,
    end_request_tracking,
    start_request_tracking,
)
from .core.security import get_security_validator
from .core.validation import get_validator

from .base import BaseAgent
from .config import ModelTier
from .exceptions import RoutingError, ValidationError, WorkspaceError
from .routing.pipeline import RoutingDecision, RoutingPipeline

# Import specialist agents
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
    """Enhanced dispatcher with health monitoring and comprehensive metrics."""

    def __init__(self):
        self.registry = AgentRegistry()
        self.routing_pipeline = RoutingPipeline()
        self.request_history: List[Dict[str, Any]] = []

        # Health monitoring
        self.agent_health_status: Dict[str, Dict[str, Any]] = {}
        self.last_health_check = datetime.now()
        self.health_check_interval = 300  # 5 minutes

        # Security and validation
        self.security_validator = get_security_validator()
        self.request_validator = get_validator()

        # Dispatcher configuration
        self.max_history = 1000
        self.default_agent = "GeneralAgent"
        self.fallback_agent = "OnboardingOrchestrator"

        # Performance tracking
        self.performance_metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "routing_time_total": 0.0,
            "validation_time_total": 0.0,
            "security_time_total": 0.0,
        }

        # Initialize health status for all agents
        self._initialize_agent_health()

    def _initialize_agent_health(self):
        """Initialize health status for all registered agents."""
        for agent_name in self.registry.list_agents():
            self.agent_health_status[agent_name] = {
                "status": "unknown",
                "last_check": None,
                "consecutive_failures": 0,
                "response_times": [],
                "error_count": 0,
                "last_error": None,
                "is_available": True,
            }

    async def dispatch(
        self,
        request: str,
        workspace_id: str,
        user_id: str,
        session_id: str,
        context: Optional[Dict[str, Any]] = None,
        agent_hint: Optional[str] = None,
        fast_mode: bool = False,
        client_ip: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Enhanced dispatch with comprehensive monitoring and validation."""
        request_id = str(uuid.uuid4())
        start_time = datetime.now()

        # Start request tracking
        tracking_start = start_request_tracking(
            request_id,
            "dispatcher",
            user_id,
            workspace_id,
            session_id,
            client_ip,
            user_agent,
        )

        try:
            # Update performance counters
            self.performance_metrics["total_requests"] += 1

            # Enhanced validation with timing
            validation_start = datetime.now()
            self._validate_dispatch_request(request, workspace_id, user_id, session_id)
            validation_time = (datetime.now() - validation_start).total_seconds()
            self.performance_metrics["validation_time_total"] += validation_time

            # Security validation with timing
            security_start = datetime.now()
            is_secure, security_error = await self.security_validator.validate_request(
                {
                    "request": request,
                    "user_id": user_id,
                    "workspace_id": workspace_id,
                    "session_id": session_id,
                    "context": context,
                },
                client_ip=client_ip,
                user_id=user_id,
                workspace_id=workspace_id,
            )
            security_time = (datetime.now() - security_start).total_seconds()
            self.performance_metrics["security_time_total"] += security_time

            if not is_secure:
                self.performance_metrics["failed_requests"] += 1
                end_request_tracking(
                    request_id,
                    "dispatcher",
                    user_id,
                    workspace_id,
                    session_id,
                    len(request),
                    0,
                    RequestStatus.SECURITY_BLOCKED,
                    error_code="SECURITY_VALIDATION_FAILED",
                    error_message=security_error,
                    client_ip=client_ip,
                    user_agent=user_agent,
                    validation_time=validation_time,
                    security_time=security_time,
                )
                return self._create_error_response(
                    security_error or "Security validation failed",
                    "SECURITY_BLOCKED",
                    request,
                    workspace_id,
                    user_id,
                    session_id,
                )

            # Create enhanced initial state
            state = create_initial_state(
                workspace_id=workspace_id,
                user_id=user_id,
                session_id=session_id,
                error_recovery_attempts=0,
            )

            # Add context with validation
            if context:
                try:
                    state = update_state(state, **context)
                except Exception as e:
                    logger.warning(f"Failed to add context to state: {e}")
                    state = update_state(state, context_error=str(e))

            # Add user message
            try:
                state = add_message(state, "user", request)
            except Exception as e:
                logger.error(f"Failed to add user message to state: {e}")
                state = update_state(state, message_error=str(e))

            # Enhanced agent determination with health checks
            routing_start = datetime.now()
            target_agent = await self._determine_target_agent_with_health_checks(
                request, state, agent_hint, fast_mode
            )
            routing_time = (datetime.now() - routing_start).total_seconds()
            self.performance_metrics["routing_time_total"] += routing_time

            # Get healthy agent instance
            agent = await self._get_healthy_agent(target_agent)
            if not agent:
                self.performance_metrics["failed_requests"] += 1
                end_request_tracking(
                    request_id,
                    "dispatcher",
                    user_id,
                    workspace_id,
                    session_id,
                    len(request),
                    0,
                    RequestStatus.ERROR,
                    error_code="NO_HEALTHY_AGENT_AVAILABLE",
                    error_message=f"No healthy agent available for: {target_agent}",
                    client_ip=client_ip,
                    user_agent=user_agent,
                    validation_time=validation_time,
                    security_time=security_time,
                    routing_time=routing_time,
                )
                return self._create_error_response(
                    f"No healthy agent available: {target_agent}",
                    "AGENT_UNAVAILABLE",
                    request,
                    workspace_id,
                    user_id,
                    session_id,
                )

            # Add system message
            try:
                state = add_message(
                    state, "system", f"Request routed to {target_agent} agent"
                )
            except Exception as e:
                logger.error(f"Failed to add system message: {e}")

            # Execute agent with enhanced monitoring
            execution_start = datetime.now()
            result_state = await self._execute_agent_with_health_monitoring(
                agent, state, target_agent, request_id
            )
            execution_time = (datetime.now() - execution_start).total_seconds()

            # Calculate response length
            response_length = len(str(result_state.get("response", "")))

            # Update agent health status
            self._update_agent_health(agent.name, True, execution_time)

            # Record request with enhanced metadata
            self._record_enhanced_request(
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
                fallback_used=agent.name != target_agent,
                error_recovery_attempts=result_state.get("error_recovery_attempts", 0),
                request_id=request_id,
            )

            # Update performance counters
            self.performance_metrics["successful_requests"] += 1

            # End request tracking
            end_request_tracking(
                request_id,
                target_agent,
                user_id,
                workspace_id,
                session_id,
                len(request),
                response_length,
                RequestStatus.SUCCESS,
                client_ip=client_ip,
                user_agent=user_agent,
                validation_time=validation_time,
                security_time=security_time,
                routing_time=routing_time,
                llm_tokens_used=result_state.get("token_usage"),
                tools_used=result_state.get("tools_used", []),
                memory_operations=result_state.get("memory_operations", 0),
            )

            # Prepare enhanced response
            response = {
                "success": result_state.get("error") is None,
                "agent": target_agent,
                "workspace_id": workspace_id,
                "user_id": user_id,
                "session_id": session_id,
                "request_id": request_id,
                "execution_time_seconds": execution_time,
                "timestamp": datetime.now().isoformat(),
                "routing_decision": result_state.get("routing_decision"),
                "state": result_state,
                "performance": {
                    "validation_time": validation_time,
                    "security_time": security_time,
                    "routing_time": routing_time,
                },
            }

            if result_state.get("error"):
                response["error"] = result_state["error"]
                response["error_code"] = "AGENT_EXECUTION_FAILED"
                response["fallback_used"] = agent.name != target_agent

            return response

        except ValidationError as e:
            logger.error(f"Validation error in dispatch: {e}")
            self.performance_metrics["failed_requests"] += 1
            end_request_tracking(
                request_id,
                "dispatcher",
                user_id,
                workspace_id,
                session_id,
                len(request),
                0,
                RequestStatus.ERROR,
                error_code="VALIDATION_ERROR",
                error_message=str(e),
                client_ip=client_ip,
                user_agent=user_agent,
            )
            return self._create_error_response(
                str(e), "VALIDATION_ERROR", request, workspace_id, user_id, session_id
            )
        except RoutingError as e:
            logger.error(f"Routing error in dispatch: {e}")
            self.performance_metrics["failed_requests"] += 1
            end_request_tracking(
                request_id,
                "dispatcher",
                user_id,
                workspace_id,
                session_id,
                len(request),
                0,
                RequestStatus.ERROR,
                error_code="ROUTING_ERROR",
                error_message=str(e),
                client_ip=client_ip,
                user_agent=user_agent,
            )
            return self._create_error_response(
                str(e), "ROUTING_ERROR", request, workspace_id, user_id, session_id
            )
        except Exception as e:
            logger.error(f"Unexpected error in dispatch: {e}")
            self.performance_metrics["failed_requests"] += 1
            end_request_tracking(
                request_id,
                "dispatcher",
                user_id,
                workspace_id,
                session_id,
                len(request),
                0,
                RequestStatus.ERROR,
                error_code="DISPATCH_ERROR",
                error_message=str(e),
                client_ip=client_ip,
                user_agent=user_agent,
            )
            return self._create_error_response(
                str(e), "DISPATCH_ERROR", request, workspace_id, user_id, session_id
            )

    async def _determine_target_agent_with_health_checks(
        self,
        request: str,
        state: AgentState,
        agent_hint: Optional[str] = None,
        fast_mode: bool = False,
    ) -> str:
        """Determine target agent with health checks."""
        # If agent hint is provided, check if it's healthy
        if agent_hint:
            agent = self.registry.get_agent(agent_hint)
            if agent and self._is_agent_healthy(agent_hint):
                logger.info(f"Using hinted healthy agent: {agent_hint}")
                return agent_hint
            else:
                logger.warning(
                    f"Hinted agent '{agent_hint}' not available or unhealthy"
                )

        # Use routing pipeline to determine agent
        try:
            routing_decision = await self.routing_pipeline.route(request, fast_mode)
            target_agent = routing_decision.target_agent

            # Check if the routed agent is healthy
            if self._is_agent_healthy(target_agent):
                logger.info(f"Routed to healthy agent: {target_agent}")
                return target_agent
            else:
                logger.warning(
                    f"Routed agent '{target_agent}' unhealthy, finding alternative"
                )
                return await self._find_healthy_alternative(target_agent)

        except Exception as e:
            logger.error(f"Routing pipeline failed: {e}")
            return await self._find_healthy_alternative(self.fallback_agent)

    async def _find_healthy_alternative(self, preferred_agent: str) -> str:
        """Find a healthy alternative agent."""
        # Try preferred agent first
        if self._is_agent_healthy(preferred_agent):
            return preferred_agent

        # Try fallback agent
        if self._is_agent_healthy(self.fallback_agent):
            logger.info(f"Using fallback agent: {self.fallback_agent}")
            return self.fallback_agent

        # Find any healthy agent
        for agent_name in self.registry.list_agents():
            if self._is_agent_healthy(agent_name):
                logger.info(f"Using alternative healthy agent: {agent_name}")
                return agent_name

        # No healthy agents available
        logger.error("No healthy agents available")
        return self.fallback_agent

    def _is_agent_healthy(self, agent_name: str) -> bool:
        """Check if an agent is healthy."""
        if agent_name not in self.agent_health_status:
            return False

        health = self.agent_health_status[agent_name]

        # Check if agent is marked as unavailable
        if not health.get("is_available", True):
            return False

        # Check consecutive failures
        if health.get("consecutive_failures", 0) >= 3:
            return False

        # Check if recently checked and healthy
        last_check = health.get("last_check")
        if last_check and (datetime.now() - last_check).total_seconds() < 60:
            return health.get("status") == "healthy"

        return True  # Assume healthy if no recent negative data

    async def _get_healthy_agent(self, agent_name: str) -> Optional[BaseAgent]:
        """Get a healthy agent instance."""
        agent = self.registry.get_agent(agent_name)
        if not agent:
            return None

        # Perform quick health check
        try:
            is_healthy = await self._perform_agent_health_check(agent_name)
            if is_healthy:
                return agent
            else:
                logger.warning(f"Agent {agent_name} failed health check")
                return None
        except Exception as e:
            logger.error(f"Health check failed for agent {agent_name}: {e}")
            return None

    async def _perform_agent_health_check(self, agent_name: str) -> bool:
        """Perform health check on an agent."""
        agent = self.registry.get_agent(agent_name)
        if not agent:
            return False

        try:
            # Check agent's built-in health method
            if hasattr(agent, "is_healthy") and callable(agent.is_healthy):
                is_healthy = agent.is_healthy()
                self._update_agent_health(agent_name, is_healthy)
                return is_healthy

            # Fallback: basic checks
            is_healthy = (
                hasattr(agent, "name")
                and hasattr(agent, "execute")
                and agent.name == agent_name
            )

            self._update_agent_health(agent_name, is_healthy)
            return is_healthy

        except Exception as e:
            logger.error(f"Health check error for agent {agent_name}: {e}")
            self._update_agent_health(agent_name, False, error=str(e))
            return False

    def _update_agent_health(
        self,
        agent_name: str,
        is_healthy: bool,
        response_time: Optional[float] = None,
        error: Optional[str] = None,
    ):
        """Update agent health status."""
        if agent_name not in self.agent_health_status:
            self.agent_health_status[agent_name] = {
                "status": "unknown",
                "last_check": None,
                "consecutive_failures": 0,
                "response_times": [],
                "error_count": 0,
                "last_error": None,
                "is_available": True,
            }

        health = self.agent_health_status[agent_name]
        health["last_check"] = datetime.now()

        if is_healthy:
            health["status"] = "healthy"
            health["consecutive_failures"] = 0
            health["is_available"] = True

            if response_time is not None:
                health["response_times"].append(response_time)
                # Keep only last 10 response times
                if len(health["response_times"]) > 10:
                    health["response_times"] = health["response_times"][-10:]
        else:
            health["status"] = "unhealthy"
            health["consecutive_failures"] += 1
            health["error_count"] += 1
            health["last_error"] = error

            # Mark as unavailable after 3 consecutive failures
            if health["consecutive_failures"] >= 3:
                health["is_available"] = False
                logger.warning(
                    f"Agent {agent_name} marked as unavailable after {health['consecutive_failures']} consecutive failures"
                )

    async def _execute_agent_with_health_monitoring(
        self,
        agent: BaseAgent,
        state: AgentState,
        target_agent: str,
        request_id: str,
    ) -> AgentState:
        """Execute agent with health monitoring."""
        try:
            # Validate input using enhanced method
            is_valid, validation_error = await agent.validate_input(state)
            if not is_valid:
                self._update_agent_health(agent.name, False, error=validation_error)
                raise ValidationError(
                    f"Agent input validation failed: {validation_error}"
                )

            # Execute agent
            result_state = await agent.execute(state)

            # Check execution result
            if result_state.get("error"):
                self._update_agent_health(
                    agent.name, False, error=result_state["error"]
                )
            else:
                self._update_agent_health(agent.name, True)

            return result_state

        except Exception as e:
            logger.error(f"Agent execution failed for {agent.name}: {e}")
            self._update_agent_health(agent.name, False, error=str(e))
            raise

    async def check_all_agents_health(self) -> Dict[str, Dict[str, Any]]:
        """Perform health check on all agents."""
        logger.info("Performing health check on all agents")

        health_results = {}
        for agent_name in self.registry.list_agents():
            try:
                is_healthy = await self._perform_agent_health_check(agent_name)
                health_results[agent_name] = {
                    "healthy": is_healthy,
                    "status": self.agent_health_status[agent_name]["status"],
                    "last_check": self.agent_health_status[agent_name]["last_check"],
                    "consecutive_failures": self.agent_health_status[agent_name][
                        "consecutive_failures"
                    ],
                }
            except Exception as e:
                health_results[agent_name] = {
                    "healthy": False,
                    "error": str(e),
                    "status": "error",
                }

        self.last_health_check = datetime.now()
        return health_results

    def get_agent_health_status(
        self, agent_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get health status for agents."""
        if agent_name:
            if agent_name not in self.agent_health_status:
                return {"error": f"Agent {agent_name} not found"}

            health = self.agent_health_status[agent_name].copy()
            # Calculate average response time
            if health["response_times"]:
                health["avg_response_time"] = sum(health["response_times"]) / len(
                    health["response_times"]
                )
            else:
                health["avg_response_time"] = None

            return health

        # Return all agents' health status
        return {
            name: {
                "status": data["status"],
                "is_available": data["is_available"],
                "consecutive_failures": data["consecutive_failures"],
                "error_count": data["error_count"],
                "last_check": data["last_check"],
                "avg_response_time": (
                    sum(data["response_times"]) / len(data["response_times"])
                    if data["response_times"]
                    else None
                ),
            }
            for name, data in self.agent_health_status.items()
        }

    def get_enhanced_dispatcher_stats(self) -> Dict[str, Any]:
        """Get enhanced dispatcher statistics with health information."""
        base_stats = self.get_dispatcher_stats()

        # Add health information
        healthy_agents = sum(
            1
            for health in self.agent_health_status.values()
            if health["status"] == "healthy"
        )
        unavailable_agents = sum(
            1
            for health in self.agent_health_status.values()
            if not health["is_available"]
        )

        # Add performance metrics
        total_requests = self.performance_metrics["total_requests"]
        avg_times = {}
        if total_requests > 0:
            avg_times = {
                "avg_validation_time": self.performance_metrics["validation_time_total"]
                / total_requests,
                "avg_security_time": self.performance_metrics["security_time_total"]
                / total_requests,
                "avg_routing_time": self.performance_metrics["routing_time_total"]
                / total_requests,
            }

        return {
            **base_stats,
            "health": {
                "total_agents": len(self.agent_health_status),
                "healthy_agents": healthy_agents,
                "unavailable_agents": unavailable_agents,
                "last_health_check": self.last_health_check.isoformat(),
                "health_check_interval": self.health_check_interval,
            },
            "performance": {
                **self.performance_metrics,
                "success_rate": (
                    (
                        self.performance_metrics["successful_requests"]
                        / total_requests
                        * 100
                    )
                    if total_requests > 0
                    else 0
                ),
                **avg_times,
            },
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
