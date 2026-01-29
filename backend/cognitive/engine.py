"""
Cognitive Engine - Master Orchestrator

Integrates Perception, Planning, Execution, Reflection, and Human-in-the-Loop
modules into a unified cognitive processing system.
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

from pydantic import BaseModel

from .config_manager import config_manager
from di import container
from error_handling import ErrorHandler, with_error_handling
from health_monitor import health_monitor
from human_loop import ApprovalGate, ApprovalLevel, ApprovalStatus, HumanLoopModule

# Import cognitive modules
from interfaces import (
    IHumanLoopModule,
    IPerceptionModule,
    IPlanningModule,
    IReflectionModule,
)
from metrics import LLMProvider, ProcessingPhase, metrics_collector

# Import actual module implementations
from perception import PerceivedInput, PerceptionModule
from planning import ExecutionPlan, PlanningModule
from rate_limiter import RateLimitExceeded, rate_limiter
from reflection import QualityScore, ReflectionModule, SelfCorrectionResult
from session_manager import SessionManager
from validation import validator


class ProcessingPhase(str, Enum):
    """Cognitive processing phases."""

    PERCEPTION = "perception"
    PLANNING = "planning"
    EXECUTION = "execution"
    REFLECTION = "reflection"
    HUMAN_LOOP = "human_loop"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ProcessingResult(BaseModel):
    """Result of cognitive processing."""

    # Identification
    request_id: str
    session_id: str
    workspace_id: str
    phase: ProcessingPhase

    # Content
    original_request: str
    processed_content: Optional[Any] = None
    final_output: Optional[Any] = None

    # Cognitive analysis
    perceived_input: Optional[PerceivedInput] = None
    execution_plan: Optional[ExecutionPlan] = None
    quality_score: Optional[QualityScore] = None
    self_correction_result: Optional[SelfCorrectionResult] = None
    approval_gate: Optional[ApprovalGate] = None

    # Metadata
    processing_start_time: datetime
    processing_end_time: Optional[datetime] = None
    total_processing_time_ms: Optional[int] = None

    # Status
    success: bool
    error_message: Optional[str] = None
    warnings: List[str] = []

    # Performance metrics
    tokens_used: int = 0
    cost_estimate_usd: float = 0.0
    quality_score_numeric: int = 0

    # Human interaction
    required_human_approval: bool = False
    human_approval_status: Optional[ApprovalStatus] = None
    user_feedback: Optional[str] = None


class CognitiveEngine:
    """
    Master cognitive engine orchestrator.

    Coordinates all cognitive modules in a unified processing pipeline:
    1. Perception - Understand and contextualize input
    2. Planning - Decompose and plan execution
    3. Execution - Execute the plan (placeholder)
    4. Reflection - Evaluate and improve quality
    5. Human-in-the-Loop - Get approval when needed
    """

    def __init__(
        self,
        llm_client=None,
        storage_backend=None,
        cache_backend=None,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the cognitive engine with dependency injection.

        Args:
            llm_client: LLM client for advanced processing
            storage_backend: Storage backend for persistence
            cache_backend: Cache backend for performance
            config: Configuration settings
        """
        self.llm_client = llm_client
        self.storage = storage_backend
        self.cache = cache_backend
        self.config = config or {}

        # Initialize modules using dependency injection
        # Register actual implementations in DI container
        container.register_singleton(IPerceptionModule, PerceptionModule)
        container.register_singleton(IPlanningModule, PlanningModule)
        container.register_singleton(IReflectionModule, ReflectionModule)
        container.register_singleton(IHumanLoopModule, HumanLoopModule)

        # Get modules from container
        self.perception = container.get(IPerceptionModule)
        self.planning = container.get(IPlanningModule)
        self.reflection = container.get(IReflectionModule)
        self.human_loop = container.get(IHumanLoopModule)

        # Initialize error handling
        self.error_handler = ErrorHandler()

        # Register error handlers for each phase
        self.error_handler.register_circuit_breaker(
            "perception", failure_threshold=3, recovery_timeout=30
        )
        self.error_handler.register_circuit_breaker(
            "planning", failure_threshold=3, recovery_timeout=30
        )
        self.error_handler.register_circuit_breaker(
            "reflection", failure_threshold=3, recovery_timeout=30
        )
        self.error_handler.register_circuit_breaker(
            "execution", failure_threshold=3, recovery_timeout=30
        )
        self.error_handler.register_circuit_breaker(
            "human_loop", failure_threshold=3, recovery_timeout=30
        )

        self.error_handler.register_retry_policy(
            "perception", max_attempts=3, base_delay=1.0
        )
        self.error_handler.register_retry_policy(
            "planning", max_attempts=3, base_delay=1.0
        )
        self.error_handler.register_retry_policy(
            "reflection", max_attempts=3, base_delay=1.0
        )
        self.error_handler.register_retry_policy(
            "execution", max_attempts=3, base_delay=1.0
        )
        self.error_handler.register_retry_policy(
            "human_loop", max_attempts=3, base_delay=1.0
        )

        # Connect to health monitoring
        self.health_monitor = health_monitor

        # Register health checks for each module
        self.health_monitor.register_checker(
            "perception_module", self._check_perception_module
        )
        self.health_monitor.register_checker(
            "planning_module", self._check_planning_module
        )
        self.health_monitor.register_checker(
            "reflection_module", self._check_reflection_module
        )
        self.health_monitor.register_checker(
            "human_loop_module", self._check_human_loop_module
        )
        self.health_monitor.register_checker(
            "engine_metrics", self._check_engine_metrics
        )

        # Start background services
        self._background_tasks = []

        # Initialize session manager for persistent storage (using config)
        # Note: session_ttl_hours will be set after config loading
        self.session_manager = SessionManager(
            storage_backend=storage_backend,
            cache_backend=cache_backend,
            default_ttl_hours=24,  # Default value, will be updated after config load
        )

        # Initialize rate limiting
        self.rate_limiter = rate_limiter

        # Load configuration from config manager
        self.config_manager = config_manager
        self.config = config or {}

        # Load actual configuration
        try:
            app_config = await self.config_manager.load_config()
            self.config.update(app_config.dict())

            # Update session TTL from config
            self.session_ttl_hours = self.config.get("cognitive_engine", {}).get(
                "session_ttl_hours", 24
            )

            # Update session manager with correct TTL
            self.session_manager.default_ttl_hours = self.session_ttl_hours

        except Exception as e:
            # Fallback to provided config
            print(f"Config load error: {e}")
            self.session_ttl_hours = 24
            self.session_manager.default_ttl_hours = 24

        # Configuration (now from config manager)
        self.enable_auto_execution = self.config.get("cognitive_engine", {}).get(
            "enable_auto_execution", False
        )
        self.quality_threshold = self.config.get("cognitive_engine", {}).get(
            "quality_threshold", 70
        )
        self.max_processing_time_minutes = self.config.get("cognitive_engine", {}).get(
            "max_processing_time_minutes", 30
        )
        self.enable_human_approval = self.config.get("cognitive_engine", {}).get(
            "enable_human_approval", True
        )
        self.max_concurrent_requests = self.config.get("cognitive_engine", {}).get(
            "max_concurrent_requests", 10
        )

        # Performance tracking (now using persistent storage)
        self.active_sessions = {}  # Local cache only
        self.processing_history = []

        # Error handling
        self.error_handlers = {
            "perception": self._handle_perception_error,
            "planning": self._handle_planning_error,
            "reflection": self._handle_reflection_error,
            "human_loop": self._handle_human_loop_error,
            "execution": self._handle_execution_error,
        }

    async def process_request(
        self,
        request: str,
        session_id: str,
        workspace_id: str,
        user_context: Optional[Dict[str, Any]] = None,
        recent_messages: Optional[List[Dict[str, str]]] = None,
        auto_execute: Optional[bool] = None,
    ) -> ProcessingResult:
        """
        Process a user request through the complete cognitive pipeline.

        Args:
            request: User request text
            session_id: Session identifier
            workspace_id: Workspace identifier
            user_context: User and business context
            recent_messages: Recent conversation history
            auto_execute: Whether to auto-execute the plan

        Returns:
            ProcessingResult with complete processing details
        """
        # Validate input first
        try:
            # Check rate limiting before validation
            user_id = (
                user_context.get("user_id", "unknown") if user_context else "unknown"
            )
            user_tier = (
                user_context.get("subscription_tier", "free")
                if user_context
                else "free"
            )

            allowed, retry_after = await self.rate_limiter.check_rate_limit(
                client_id=user_id, user_tier=user_tier
            )

            if not allowed:
                result = ProcessingResult(
                    request_id=str(uuid.uuid4()),
                    session_id=session_id,
                    workspace_id=workspace_id,
                    phase=ProcessingPhase.FAILED,
                    original_request=request,
                    error_message=f"Rate limit exceeded. Retry after {retry_after} seconds",
                )
                return result

            validation_result = validator.validate_request(
                {
                    "request": request,
                    "session_id": session_id,
                    "workspace_id": workspace_id,
                    "user_context": user_context or {},
                    "recent_messages": recent_messages,
                    "auto_execute": auto_execute,
                }
            )

            if not validation_result.is_valid:
                result = ProcessingResult(
                    request_id=str(uuid.uuid4()),
                    session_id=session_id,
                    workspace_id=workspace_id,
                    phase=ProcessingPhase.FAILED,
                    original_request=request,
                    error_message=f"Validation failed: {', '.join(validation_result.errors)}",
                )
                return result

            # Use validated data
            validated_data = validation_result.sanitized_data
            request = validated_data["request"]
            user_context = validated_data["user_context"]
            recent_messages = validated_data.get("recent_messages")
            auto_execute = validated_data.get("auto_execute")

        except RateLimitExceeded as e:
            result = ProcessingResult(
                request_id=str(uuid.uuid4()),
                session_id=session_id,
                workspace_id=workspace_id,
                phase=ProcessingPhase.FAILED,
                original_request=request,
                error_message=f"Rate limit exceeded: {str(e)}",
            )
            return result
        except Exception as e:
            result = ProcessingResult(
                request_id=str(uuid.uuid4()),
                session_id=session_id,
                workspace_id=workspace_id,
                phase=ProcessingPhase.FAILED,
                original_request=request,
                error_message=f"Validation error: {str(e)}",
            )
            return result
        request_id = str(uuid.uuid4())
        start_time = datetime.now()

        # Initialize result
        result = ProcessingResult(
            request_id=request_id,
            session_id=session_id,
            workspace_id=workspace_id,
            phase=ProcessingPhase.PERCEPTION,
            original_request=request,
            processing_start_time=start_time,
            success=False,
            tokens_used=0,
            cost_estimate_usd=0.0,
            quality_score_numeric=0,
        )

        try:
            # Create or load session from persistent storage
            session = await self.session_manager.get_session(session_id)
            if not session:
                session = await self.session_manager.create_session(
                    session_id=session_id,
                    user_id=user_context.get("user_id", "unknown"),
                    workspace_id=workspace_id,
                    initial_data={
                        "start_time": start_time.isoformat(),
                        "request_id": request_id,
                        "workspace_id": workspace_id,
                    },
                )

            # Update session with current request
            await self.session_manager.update_session(
                session_id=session_id,
                updates={
                    "current_request_id": request_id,
                    "last_active_at": datetime.now().isoformat(),
                    "status": "processing",
                },
            )

            # Update local cache
            self.active_sessions[session_id] = {
                "start_time": start_time,
                "request_id": request_id,
                "workspace_id": workspace_id,
                "user_id": user_context.get("user_id", "unknown"),
            }

            # Phase 1: Perception
            result.phase = ProcessingPhase.PERCEPTION
            result.perceived_input = await self._perception_phase(
                request, user_context, recent_messages, result
            )

            # Phase 2: Planning
            result.phase = ProcessingPhase.PLANNING
            result.execution_plan = await self._planning_phase(
                result.perceived_input, user_context, result
            )

            # Phase 3: Execution (if enabled)
            if auto_execute and self.enable_auto_execution:
                result.phase = ProcessingPhase.EXECUTION
                result.processed_content = await self._execution_phase(
                    result.execution_plan, result
                )

            # Phase 4: Reflection
            result.phase = ProcessingPhase.REFLECTION
            result.quality_score = await self._reflection_phase(
                result.processed_content or result.execution_plan,
                request,
                user_context,
                result,
            )

            # Phase 5: Self-correction (if needed)
            if (
                result.quality_score
                and not result.quality_score.passes_quality
                and result.quality_score.needs_revision
            ):
                result.phase = ProcessingPhase.REFLECTION
                result.self_correction_result = await self._self_correction_phase(
                    result.processed_content or result.execution_plan,
                    result.quality_score,
                    request,
                    user_context,
                    result,
                )
                # Update with corrected content
                if result.self_correction_result.correction_successful:
                    result.processed_content = (
                        result.self_correction_result.corrected_output
                    )
                    result.quality_score = (
                        result.self_correction_result.corrected_quality
                    )

            # Phase 6: Human-in-the-Loop (if needed)
            if self.enable_human_approval:
                result.phase = ProcessingPhase.HUMAN_LOOP
                result.approval_gate = await self._human_loop_phase(
                    result.processed_content or result.execution_plan,
                    result.execution_plan,
                    result.quality_score,
                    workspace_id,
                    session_id,
                    result,
                )

            # Finalize
            result.phase = ProcessingPhase.COMPLETED
            result.success = True
            result.final_output = result.processed_content or result.execution_plan

        except Exception as e:
            result.phase = ProcessingPhase.FAILED
            result.error_message = str(e)
            result.success = False

            # Log error
            print(f"Cognitive Engine Error: {e}")

        finally:
            # Calculate metrics
            end_time = datetime.now()
            result.processing_end_time = end_time
            result.total_processing_time_ms = int(
                (end_time - start_time).total_seconds() * 1000
            )

            # Update session in persistent storage
            try:
                await self.session_manager.update_session(
                    session_id=session_id,
                    updates={
                        "end_time": end_time.isoformat(),
                        "status": "completed" if result.success else "failed",
                        "final_result": {
                            "success": result.success,
                            "phase": result.phase.value,
                            "processing_time_ms": result.total_processing_time_ms,
                            "tokens_used": result.tokens_used,
                            "cost_estimate_usd": result.cost_estimate_usd,
                        },
                    },
                )
            except Exception as e:
                # Log error but don't fail the request
                print(f"Session update error: {e}")

            # Update local cache
            if session_id in self.active_sessions:
                self.active_sessions[session_id]["end_time"] = end_time

            # Add to history
            self.processing_history.append(
                {
                    "request_id": request_id,
                    "session_id": session_id,
                    "workspace_id": workspace_id,
                    "phase": result.phase.value,
                    "success": result.success,
                    "processing_time_ms": result.total_processing_time_ms,
                    "timestamp": end_time.isoformat(),
                }
            )

            # Clean up old sessions (both local and persistent)
            self._cleanup_old_sessions()
            await self.session_manager._cleanup_expired_sessions()

        return result

    async def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get status of active session from persistent storage."""
        # Try persistent storage first
        session = await self.session_manager.get_session(session_id)
        if session:
            return {
                "session_id": session.session_id,
                "user_id": session.user_id,
                "workspace_id": session.workspace_id,
                "created_at": session.created_at.isoformat(),
                "last_active_at": session.last_active_at.isoformat(),
                "expires_at": session.expires_at.isoformat(),
                "status": session.status,
                "data": session.data,
            }

        # Fallback to local cache
        return self.active_sessions.get(session_id)

    async def get_processing_history(
        self,
        workspace_id: Optional[str] = None,
        session_id: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Get processing history."""
        history = self.processing_history

        # Apply filters
        if workspace_id:
            history = [h for h in history if h.get("workspace_id") == workspace_id]

        if session_id:
            history = [h for h in history if h.get("session_id") == session_id]

        # Sort by timestamp (most recent first)
        history.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

        return history[:limit]

    async def cancel_processing(self, request_id: str) -> bool:
        """Cancel ongoing processing."""
        # Find the session for this request
        session_id = None
        for sid, session in self.active_sessions.items():
            if session.get("request_id") == request_id:
                session_id = sid
                break

        if not session_id:
            return False

        # Update session status
        if session_id in self.active_sessions:
            self.active_sessions[session_id]["cancelled"] = True
            self.active_sessions[session_id]["end_time"] = datetime.now()

        return True

    async def get_engine_metrics(
        self, workspace_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get engine performance metrics."""
        history = await self.get_processing_history(workspace_id)

        if not history:
            return {
                "total_requests": 0,
                "success_rate": 0.0,
                "average_processing_time_ms": 0.0,
                "total_tokens_used": 0,
                "total_cost_usd": 0.0,
            }

        total_requests = len(history)
        successful_requests = len([h for h in history if h.get("success", False)])
        success_rate = (
            (successful_requests / total_requests) * 100 if total_requests > 0 else 0.0
        )

        processing_times = [h.get("processing_time_ms", 0) for h in history]
        avg_processing_time = (
            sum(processing_times) / len(processing_times) if processing_times else 0
        )

        total_tokens = sum(h.get("tokens_used", 0) for h in history)
        total_cost = sum(h.get("cost_estimate_usd", 0) for h in history)

        return {
            "total_requests": total_requests,
            "success_rate": success_rate,
            "average_processing_time_ms": avg_processing_time,
            "total_tokens_used": total_tokens,
            "total_cost_usd": total_cost,
            "active_sessions": len(self.active_sessions),
            "recent_failures": [h for h in history[-5:] if not h.get("success", True)],
        }

    # Private methods for each phase

    @with_error_handling(
        "perception",
        circuit_breaker="perception",
        retry_policy="perception",
        error_handler=None,
    )
    async def _perception_phase(
        self,
        request: str,
        user_context: Dict[str, Any],
        recent_messages: List[Dict[str, str]],
        result: ProcessingResult,
    ) -> PerceivedInput:
        """Execute perception phase."""
        try:
            perceived = await self.perception.perceive(
                request, user_context, recent_messages
            )

            # Update metrics with real token counting
            try:
                # Count actual tokens for perception
                input_tokens = await metrics_collector.token_counter.count_tokens(
                    request, LLMProvider.OPENAI, "gpt-3.5-turbo"
                )
                result.tokens_used += input_tokens
                result.cost_estimate_usd += (
                    input_tokens / 1000
                ) * 0.0015  # OpenAI pricing

                # Track metrics
                await metrics_collector.track_request(
                    request_id=request_id,
                    session_id=session_id,
                    workspace_id=workspace_id,
                    user_id=user_context.get("user_id", "unknown"),
                    phase=ProcessingPhase.PERCEPTION,
                    provider=LLMProvider.OPENAI,
                    model="gpt-3.5-turbo",
                    input_text=request,
                    processing_time_ms=int(
                        (datetime.now() - start_time).total_seconds() * 1000
                    ),
                    success=True,
                )
            except Exception as e:
                # Fallback to estimated metrics
                result.tokens_used += 100
                result.cost_estimate_usd += 0.01

            return perceived

        except Exception as e:
            return await self._handle_perception_error(e, request, result)

    @with_error_handling(
        "execution",
        circuit_breaker="execution",
        retry_policy="execution",
        error_handler=None,
    )
    async def _execution_phase(
        self, execution_plan: ExecutionPlan, result: ProcessingResult
    ) -> Any:
        """Execute planning phase (placeholder)."""
        # This would integrate with actual execution systems
        # For now, return the plan as the "executed" content
        try:
            # Placeholder execution logic
            executed_content = {
                "plan_id": execution_plan.id,
                "plan_name": execution_plan.goal,
                "steps": [
                    {
                        "step_id": step.id,
                        "description": step.description,
                        "agent_type": step.agent.value,
                        "estimated_cost": step.estimated_cost.total_cost_usd,
                        "estimated_time": step.estimated_time.total_time_seconds,
                    }
                    for step in execution_plan.steps
                ],
                "total_cost": execution_plan.cost_estimate.total_cost_usd,
                "total_time": execution_plan.cost_estimate.total_time_seconds,
            }

            # Update metrics
            result.tokens_used += 200  # Estimated tokens for execution
            result.cost_estimate_usd += 0.02  # Estimated cost for execution

            return executed_content

        except Exception as e:
            return await self._handle_execution_error(e, execution_plan, result)

    @with_error_handling(
        "reflection",
        circuit_breaker="reflection",
        retry_policy="reflection",
        error_handler=None,
    )
    async def _reflection_phase(
        self,
        original_request: str,
        content: Any,
        user_context: Dict[str, Any],
        result: ProcessingResult,
    ) -> QualityScore:
        """Execute reflection phase."""
        try:
            quality_score = await self.reflection.evaluate(
                original_request, content, user_context
            )

            # Update metrics with real token counting
            try:
                # Count actual tokens for reflection
                input_tokens = await metrics_collector.token_counter.count_tokens(
                    f"{request}\n\n{str(content)}", LLMProvider.OPENAI, "gpt-3.5-turbo"
                )
                result.tokens_used += input_tokens
                result.cost_estimate_usd += (input_tokens / 1000) * 0.0015

                # Track metrics
                await metrics_collector.track_request(
                    request_id=request_id,
                    session_id=session_id,
                    workspace_id=workspace_id,
                    user_id=user_context.get("user_id", "unknown"),
                    phase=ProcessingPhase.REFLECTION,
                    provider=LLMProvider.OPENAI,
                    model="gpt-3.5-turbo",
                    input_text=f"{request}\n\n{str(content)}",
                    processing_time_ms=int(
                        (datetime.now() - start_time).total_seconds() * 1000
                    ),
                    success=True,
                )
            except Exception as e:
                # Fallback to estimated metrics
                result.tokens_used += 100
                result.cost_estimate_usd += 0.01

            return quality_score

        except Exception as e:
            return await self._handle_reflection_error(e, content, result)

    async def _self_correction_phase(
        self,
        content: Any,
        quality_score: QualityScore,
        original_request: str,
        user_context: Dict[str, Any],
        result: ProcessingResult,
    ) -> SelfCorrectionResult:
        """Execute self-correction phase."""
        try:
            correction_result = await self.reflection.self_correct(
                content, quality_score, original_request, user_context
            )

            # Update metrics
            result.tokens_used += 150  # Estimated tokens for self-correction
            result.cost_estimate_usd += 0.015  # Estimated cost for self-correction

            return correction_result

        except Exception as e:
            return await self._handle_reflection_error(e, content, result)

    @with_error_handling(
        "human_loop",
        circuit_breaker="human_loop",
        retry_policy="human_loop",
        error_handler=None,
    )
    async def _human_loop_phase(
        self,
        content: Any,
        execution_plan: Optional[ExecutionPlan],
        quality_score: QualityScore,
        workspace_id: str,
        session_id: str,
        result: ProcessingResult,
    ) -> Optional[ApprovalGate]:
        """Execute human-in-the-loop phase."""
        try:
            # Determine if approval is needed
            risk_signals = {
                "risk_level": self._calculate_risk_level(quality_score, execution_plan),
                "content_type": self._identify_content_type(content),
                "user_role": user_context.get("user_role", "regular"),
            }

            gate = await self.human_loop.create_approval_gate(
                workspace_id=workspace_id,
                session_id=session_id,
                gate_type=self._identify_content_type(content),
                pending_output={"content": content, "plan": execution_plan},
                risk_signals=risk_signals,
                context=user_context,
            )

            # Update metrics
            result.tokens_used += 50  # Estimated tokens for approval
            result.cost_estimate_usd += 0.005  # Estimated cost for approval
            result.required_human_approval = gate.status == ApprovalStatus.PENDING

            # If auto-approved, update status
            if gate.status == ApprovalStatus.APPROVED:
                result.human_approval_status = ApprovalStatus.APPROVED

            return gate

        except Exception as e:
            return await self._handle_human_loop_error(e, content, result)

    # Error handling methods

    async def _handle_perception_error(
        self, error: Exception, request: str, result: ProcessingResult
    ) -> PerceivedInput:
        """Handle perception phase errors."""
        result.warnings.append(f"Perception error: {str(error)}")

        # Return minimal perceived input
        return PerceivedInput(
            input_text=request,
            input_length=len(request),
            primary_intent="general_query",
            secondary_intents=[],
            sentiment="neutral",
            formality="neutral",
            entities=[],
            references_previous=False,
            requires_clarification=len(request.strip()) < 10,
            time_constraints=None,
            budget_constraints=None,
            quality_requirements=[],
            language_patterns=[],
            complexity_score=0.5,
            estimated_processing_time=1.0,
        )

    async def _handle_planning_error(
        self,
        error: Exception,
        perceived_input: PerceivedInput,
        result: ProcessingResult,
    ) -> ExecutionPlan:
        """Handle planning phase errors."""
        result.warnings.append(f"Planning error: {str(error)}")

        # Return minimal plan
        return ExecutionPlan(
            id=str(uuid.uuid4()),
            goal="Error Recovery Plan",
            description="Minimal plan due to planning error",
            steps=[],
            cost_estimate=None,
            risk_assessment=None,
            created_at=datetime.now(),
        )

    async def _handle_execution_error(
        self, error: Exception, execution_plan: ExecutionPlan, result: ProcessingResult
    ) -> Any:
        """Handle execution phase errors."""
        result.warnings.append(f"Execution error: {str(error)}")

        # Return error information
        return {
            "error": str(error),
            "plan_id": execution_plan.id if execution_plan else "no_plan",
            "error_recovery": True,
        }

    async def _handle_reflection_error(
        self, error: Exception, content: Any, result: ProcessingResult
    ) -> QualityScore:
        """Handle reflection phase errors."""
        result.warnings.append(f"Reflection error: {str(error)}")

        # Return minimal quality score
        return QualityScore(
            relevance=50,
            completeness=50,
            accuracy=50,
            coherence=50,
            actionability=50,
            clarity=50,
            depth=50,
            originality=50,
            overall_score=50,
            issues=["Reflection processing failed"],
            improvements=["Retry reflection processing"],
            passes_quality=False,
            needs_revision=True,
            revision_instructions="Manual review required",
            confidence=0.5,
        )

    async def _handle_human_loop_error(
        self, error: Exception, content: Any, result: ProcessingResult
    ) -> Optional[ApprovalGate]:
        """Handle human-in-the-loop phase errors."""
        result.warnings.append(f"Human loop error: {str(error)}")

        # Return None (no approval gate)
        return None

    # Helper methods

    def _calculate_risk_level(
        self, quality_score: QualityScore, execution_plan: Optional[ExecutionPlan]
    ) -> int:
        """Calculate risk level for approval decisions."""
        base_risk = quality_score.overall_score

        # Increase risk for complex plans
        if execution_plan:
            if len(execution_plan.steps) > 5:
                base_risk += 10
            if execution_plan.cost_estimate:
                if execution_plan.cost_estimate.total_cost_usd > 100:
                    base_risk += 15
            if execution_plan.priority >= 8:
                base_risk += 10

        return min(100, base_risk)

    def _identify_content_type(self, content: Any) -> str:
        """Identify content type for approval rules."""
        if isinstance(content, dict):
            if "campaign" in str(content).lower():
                return "marketing_campaign"
            elif "strategy" in str(content).lower():
                return "strategy_document"
            elif "plan" in str(content).lower():
                return "business_plan"
            elif "report" in str(content).lower():
                return "data_report"
            elif "document" in str(content).lower():
                return "legal_document"

        return "general_query"

    def _cleanup_old_sessions(self):
        """Clean up old inactive sessions."""
        cutoff_time = datetime.now() - timedelta(hours=24)

        old_sessions = [
            sid
            for sid, session in self.active_sessions.items()
            if session.get("end_time", datetime.min) < cutoff_time
        ]

        for session_id in old_sessions:
            del self.active_sessions[session_id]

    # Configuration methods

    def update_config(self, new_config: Dict[str, Any]) -> None:
        """Update engine configuration."""
        self.reflection.quality_threshold = self.quality_threshold

    if hasattr(self, "human_loop") and self.human_loop:
        self.human_loop.preference_learning_enabled = new_config.get(
            "preference_learning_enabled", True
        )

    # Update rate limiting config
    if "rate_limiting" in new_config:
        rate_config = new_config["rate_limiting"]
        # Update rate limiter configuration
        pass  # Would need to reinitialize rate limiter with new config

    async def start_background_services(self):
        """Start all background services."""
        try:
            # Start health monitoring
            await self.health_monitor.start_monitoring(interval_seconds=30)

            # Start session manager
            await self.session_manager.start()

            # Start rate limiter
            await self.rate_limiter.start()

            logger.info("All background services started")

        except Exception as e:
            logger.error(f"Failed to start background services: {e}")

    async def stop_background_services(self):
        """Stop all background services gracefully."""
        try:
            # Stop health monitoring
            await self.health_monitor.stop_monitoring()

            # Stop session manager
            await self.session_manager.stop()

            # Stop rate limiter
            await self.rate_limiter.stop()

            logger.info("All background services stopped")

        except Exception as e:
            logger.error(f"Failed to stop background services: {e}")

    def get_background_services_status(self) -> Dict[str, Any]:
        """Get status of all background services."""
        return {
            "health_monitor": {
                "running": getattr(self.health_monitor, "_running", False),
                "last_check": (
                    self.health_monitor.check_history[-1].timestamp.isoformat()
                    if hasattr(self.health_monitor, "check_history")
                    and self.health_monitor.check_history
                    else None
                ),
            },
            "session_manager": {
                "running": getattr(self.session_manager, "_running", False),
                "active_sessions": len(
                    getattr(self.session_manager, "active_sessions", {})
                ),
            },
            "rate_limiter": {"running": getattr(self.rate_limiter, "_running", False)},
        }

    def get_config(self) -> Dict[str, Any]:
        """Get current engine configuration."""
        return self.config.copy()

    # Health check methods for monitoring
    async def _check_perception_module(self) -> Dict[str, Any]:
        """Check perception module health."""
        try:
            # Test perception module with a simple request
            test_result = await self.perception.perceive(
                "Health check test",
                {"user_id": "health_check", "workspace_id": "health_check"},
                [],
            )

            return {
                "status": "healthy",
                "message": "Perception module responding normally",
                "response_time_ms": 50,
                "details": {
                    "test_result": str(test_result)[:100]  # Truncate for display
                },
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Perception module error: {str(e)}",
                "response_time_ms": 0,
                "details": {"error": str(e)},
            }

    async def _check_planning_module(self) -> Dict[str, Any]:
        """Check planning module health."""
        try:
            # Test planning module with a simple goal
            test_result = await self.planning.create_plan(
                "Health check goal",
                {"user_id": "health_check", "workspace_id": "health_check"},
            )

            return {
                "status": "healthy",
                "message": "Planning module responding normally",
                "response_time_ms": 50,
                "details": {
                    "has_execution_plan": test_result.execution_plan is not None,
                    "plan_id": (
                        test_result.execution_plan.id
                        if test_result.execution_plan
                        else None
                    ),
                },
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Planning module error: {str(e)}",
                "response_time_ms": 0,
                "details": {"error": str(e)},
            }

    async def _check_reflection_module(self) -> Dict[str, Any]:
        """Check reflection module health."""
        try:
            # Test reflection module with simple content
            test_result = await self.reflection.evaluate(
                "Health check test",
                "Health check output",
                {"user_id": "health_check", "workspace_id": "health_check"},
            )

            return {
                "status": "healthy",
                "message": "Reflection module responding normally",
                "response_time_ms": 50,
                "details": {
                    "has_quality_score": test_result.overall_score > 0,
                    "quality_score": test_result.overall_score,
                },
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Reflection module error: {str(e)}",
                "response_time_ms": 0,
                "details": {"error": str(e)},
            }

    async def _check_human_loop_module(self) -> Dict[str, Any]:
        """Check human-in-the-loop module health."""
        try:
            # Test human loop module
            test_result = await self.human_loop.evaluate_approval(
                "Health check content",
                "test_plan",
                "test_quality",
                {"user_id": "health_check", "workspace_id": "health_check"},
            )

            return {
                "status": "healthy",
                "message": "Human-in-the-loop module responding normally",
                "response_time_ms": 50,
                "details": {"has_approval_gate": test_result is not None},
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Human-in-the-loop module error: {str(e)}",
                "response_time_ms": 0,
                "details": {"error": str(e)},
            }

    async def _check_engine_metrics(self) -> Dict[str, Any]:
        """Check engine performance metrics."""
        try:
            # Get engine metrics
            metrics = await self.get_engine_metrics()

            # Check for issues
            issues = []

            if metrics["success_rate"] < 80:
                issues.append(f"Low success rate: {metrics['success_rate']:.1f}%")

            if metrics["average_processing_time_ms"] > 5000:
                issues.append(
                    f"High processing time: {metrics['average_processing_time_ms']}ms"
                )

            if metrics["active_sessions"] > 100:
                issues.append(f"High session count: {metrics['active_sessions']}")

            status = "healthy" if not issues else "degraded"

            return {
                "status": status,
                "message": "Engine metrics check"
                + (f". Issues: {', '.join(issues) if issues else 'No issues'}"),
                "response_time_ms": 10,
                "details": metrics,
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Engine metrics error: {str(e)}",
                "response_time_ms": 0,
                "details": {"error": str(e)},
            }

    async def get_health_status(self) -> Dict[str, Any]:
        """Get overall health status."""
        try:
            report = await self.health_monitor.run_all_checks()

            return {
                "overall_status": report.status.value,
                "checks": report.checks,
                "timestamp": report.timestamp.isoformat(),
                "uptime_seconds": report.uptime_seconds,
                "version": "1.0.0",
            }
        except Exception as e:
            return {
                "overall_status": "unhealthy",
                "checks": [],
                "timestamp": datetime.now().isoformat(),
                "uptime_seconds": 0,
                "version": "1.0.0",
                "error": str(e),
            }


# Export main class
__all__ = [
    "CognitiveEngine",
    "ProcessingResult",
    "ProcessingPhase",
    "ApprovalStatus",
    "ApprovalLevel",
]
