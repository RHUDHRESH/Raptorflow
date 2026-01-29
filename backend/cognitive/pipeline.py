"""
Cognitive Pipeline for Integration Components

Orchestrates the complete cognitive processing pipeline.
Implements PROMPT 62 from STREAM_3_COGNITIVE_ENGINE.
"""

import asyncio
import json
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

from critic import AdversarialCritic
from hitl import ApprovalGate
from .models import CognitiveResult, ExecutionPlan, PerceivedInput, ReflectionResult
from perception import PerceptionModule
from planning import PlanningModule
from reflection import ReflectionModule


class PipelineStage(Enum):
    """Stages in the cognitive processing pipeline."""

    PRE_PERCEPTION = "pre_perception"
    PERCEPTION = "perception"
    POST_PERCEPTION = "post_perception"
    PRE_PLANNING = "pre_planning"
    PLANNING = "planning"
    POST_PLANNING = "post_planning"
    PRE_EXECUTION = "pre_execution"
    EXECUTION = "execution"
    POST_EXECUTION = "post_execution"
    PRE_REFLECTION = "pre_reflection"
    REFLECTION = "reflection"
    POST_REFLECTION = "post_reflection"
    PRE_APPROVAL = "pre_approval"
    APPROVAL = "approval"
    POST_APPROVAL = "post_approval"
    COMPLETED = "completed"
    FAILED = "failed"


class PipelineStatus(Enum):
    """Pipeline execution status."""

    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class PipelineHook:
    """Hook for pipeline stage processing."""

    stage: PipelineStage
    hook_type: str  # "before", "after", "error"
    function: Callable
    priority: int = 0  # Higher priority runs first


@dataclass
class PipelineContext:
    """Context passed through pipeline stages."""

    request_id: str
    workspace_id: str
    user_id: str
    original_input: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    start_time: datetime = field(default_factory=datetime.now)

    # Pipeline state
    current_stage: PipelineStage = PipelineStage.PRE_PERCEPTION
    status: PipelineStatus = PipelineStatus.PENDING

    # Results from each stage
    perceived_input: Optional[PerceivedInput] = None
    execution_plan: Optional[ExecutionPlan] = None
    reflection_result: Optional[ReflectionResult] = None
    approval_result: Optional[Dict[str, Any]] = None

    # Performance tracking
    stage_timings: Dict[str, float] = field(default_factory=dict)
    error_log: List[Dict[str, Any]] = field(default_factory=list)

    # Configuration
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PipelineResult:
    """Result of pipeline execution."""

    request_id: str
    status: PipelineStatus
    cognitive_result: Optional[CognitiveResult]
    processing_time_ms: int
    stage_results: Dict[str, Any]
    errors: List[Dict[str, Any]]
    metadata: Dict[str, Any]


class CognitivePipeline:
    """
    Orchestrates the complete cognitive processing pipeline.

    Manages stage transitions, hooks, and error handling.
    """

    def __init__(
        self,
        perception_module: PerceptionModule,
        planning_module: PlanningModule,
        reflection_module: ReflectionModule,
        approval_gate: ApprovalGate,
        adversarial_critic: AdversarialCritic,
    ):
        """
        Initialize the cognitive pipeline.

        Args:
            perception_module: Perception processing module
            planning_module: Planning processing module
            reflection_module: Reflection processing module
            approval_gate: Human-in-the-loop approval gate
            adversarial_critic: Adversarial critic module
        """
        self.perception = perception_module
        self.planning = planning_module
        self.reflection = reflection_module
        self.approval = approval_gate
        self.critic = adversarial_critic

        # Pipeline hooks
        self.hooks: Dict[PipelineStage, List[PipelineHook]] = {
            stage: [] for stage in PipelineStage
        }

        # Active pipeline contexts
        self.active_contexts: Dict[str, PipelineContext] = {}

        # Pipeline configuration
        self.default_config = {
            "enable_reflection": True,
            "enable_approval": True,
            "enable_critic": True,
            "max_reflection_iterations": 3,
            "approval_timeout_seconds": 300,
            "enable_parallel_execution": True,
            "enable_caching": True,
            "enable_monitoring": True,
        }

    async def run_pipeline(
        self,
        input_text: str,
        workspace_id: str,
        user_id: str,
        config: Dict[str, Any] = None,
    ) -> PipelineResult:
        """
        Run the complete cognitive processing pipeline.

        Args:
            input_text: Input text to process
            workspace_id: Workspace ID
            user_id: User ID
            config: Pipeline configuration overrides

        Returns:
            Pipeline execution result
        """
        start_time = time.time()
        request_id = str(uuid.uuid4())

        # Merge configuration
        pipeline_config = {**self.default_config}
        if config:
            pipeline_config.update(config)

        # Create pipeline context
        context = PipelineContext(
            request_id=request_id,
            workspace_id=workspace_id,
            user_id=user_id,
            original_input=input_text,
            config=pipeline_config,
        )

        self.active_contexts[request_id] = context

        try:
            # Run pipeline stages
            result = await self._execute_pipeline(context)

            processing_time_ms = int((time.time() - start_time) * 1000)

            return PipelineResult(
                request_id=request_id,
                status=result.get("status", PipelineStatus.COMPLETED),
                cognitive_result=result.get("cognitive_result"),
                processing_time_ms=processing_time_ms,
                stage_results=result.get("stage_results", {}),
                errors=context.error_log,
                metadata={
                    "workspace_id": workspace_id,
                    "user_id": user_id,
                    "config": pipeline_config,
                },
            )

        except Exception as e:
            context.status = PipelineStatus.FAILED
            context.error_log.append(
                {
                    "stage": context.current_stage.value,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }
            )

            processing_time_ms = int((time.time() - start_time) * 1000)

            return PipelineResult(
                request_id=request_id,
                status=PipelineStatus.FAILED,
                cognitive_result=None,
                processing_time_ms=processing_time_ms,
                stage_results={},
                errors=context.error_log,
                metadata={
                    "workspace_id": workspace_id,
                    "user_id": user_id,
                    "config": pipeline_config,
                },
            )

        finally:
            # Clean up context
            self.active_contexts.pop(request_id, None)

    async def _execute_pipeline(self, context: PipelineContext) -> Dict[str, Any]:
        """Execute all pipeline stages."""
        stage_results = {}

        # Pre-perception hooks
        await self._run_stage_hooks(PipelineStage.PRE_PERCEPTION, "before", context)

        # Perception stage
        context.current_stage = PipelineStage.PERCEPTION
        context.status = PipelineStatus.RUNNING

        perception_result = await self._run_perception_stage(context)
        stage_results["perception"] = perception_result

        if perception_result.get("error"):
            raise Exception(f"Perception failed: {perception_result['error']}")

        # Post-perception hooks
        await self._run_stage_hooks(PipelineStage.POST_PERCEPTION, "after", context)

        # Pre-planning hooks
        await self._run_stage_hooks(PipelineStage.PRE_PLANNING, "before", context)

        # Planning stage
        context.current_stage = PipelineStage.PLANNING
        planning_result = await self._run_planning_stage(context)
        stage_results["planning"] = planning_result

        if planning_result.get("error"):
            raise Exception(f"Planning failed: {planning_result['error']}")

        # Post-planning hooks
        await self._run_stage_hooks(PipelineStage.POST_PLANNING, "after", context)

        # Pre-execution hooks
        await self._run_stage_hooks(PipelineStage.PRE_EXECUTION, "before", context)

        # Execution stage (placeholder for now)
        context.current_stage = PipelineStage.EXECUTION
        execution_result = await self._run_execution_stage(context)
        stage_results["execution"] = execution_result

        # Post-execution hooks
        await self._run_stage_hooks(PipelineStage.POST_EXECUTION, "after", context)

        # Pre-reflection hooks
        await self._run_stage_hooks(PipelineStage.PRE_REFLECTION, "before", context)

        # Reflection stage (if enabled)
        if context.config.get("enable_reflection", True):
            context.current_stage = PipelineStage.REFLECTION
            reflection_result = await self._run_reflection_stage(context)
            stage_results["reflection"] = reflection_result

        # Post-reflection hooks
        await self._run_stage_hooks(PipelineStage.POST_REFLECTION, "after", context)

        # Pre-approval hooks
        await self._run_stage_hooks(PipelineStage.PRE_APPROVAL, "before", context)

        # Approval stage (if required)
        if context.config.get("enable_approval", True) and self._requires_approval(
            context
        ):
            context.current_stage = PipelineStage.APPROVAL
            approval_result = await self._run_approval_stage(context)
            stage_results["approval"] = approval_result

        # Post-approval hooks
        await self._run_stage_hooks(PipelineStage.POST_APPROVAL, "after", context)

        # Create final cognitive result
        cognitive_result = CognitiveResult(
            perceived_input=context.perceived_input,
            execution_plan=context.execution_plan,
            reflection_result=context.reflection_result,
            success=True,
            total_tokens_used=self._calculate_total_tokens(stage_results),
            total_cost_usd=self._calculate_total_cost(stage_results),
            processing_time_seconds=self._calculate_total_time(stage_results),
            requires_approval=context.approval_result is not None,
            approval_gate_id=(
                context.approval_result.get("gate_id")
                if context.approval_result
                else None
            ),
        )

        context.status = PipelineStatus.COMPLETED

        return {
            "status": PipelineStatus.COMPLETED,
            "cognitive_result": cognitive_result,
            "stage_results": stage_results,
        }

    async def _run_perception_stage(self, context: PipelineContext) -> Dict[str, Any]:
        """Run the perception stage."""
        stage_start = time.time()

        try:
            # Run perception module
            perceived_input = await self.perception.perceive(
                text=context.original_input,
                history=[],  # TODO: Get conversation history
            )

            context.perceived_input = perceived_input
            context.stage_timings["perception"] = time.time() - stage_start

            return {
                "success": True,
                "perceived_input": perceived_input,
                "processing_time": context.stage_timings["perception"],
            }

        except Exception as e:
            context.error_log.append(
                {
                    "stage": "perception",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }
            )

            return {
                "success": False,
                "error": str(e),
                "processing_time": time.time() - stage_start,
            }

    async def _run_planning_stage(self, context: PipelineContext) -> Dict[str, Any]:
        """Run the planning stage."""
        stage_start = time.time()

        try:
            # Run planning module
            execution_plan = await self.planning.plan(
                goal=context.original_input,
                perceived=context.perceived_input,
                context={},  # TODO: Build workspace context
            )

            context.execution_plan = execution_plan
            context.stage_timings["planning"] = time.time() - stage_start

            return {
                "success": True,
                "execution_plan": execution_plan,
                "processing_time": context.stage_timings["planning"],
            }

        except Exception as e:
            context.error_log.append(
                {
                    "stage": "planning",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }
            )

            return {
                "success": False,
                "error": str(e),
                "processing_time": time.time() - stage_start,
            }

    async def _run_execution_stage(self, context: PipelineContext) -> Dict[str, Any]:
        """Run the execution stage."""
        stage_start = time.time()

        try:
            # For now, simulate execution
            # TODO: Implement actual plan execution
            await asyncio.sleep(0.1)  # Simulate processing time

            context.stage_timings["execution"] = time.time() - stage_start

            return {
                "success": True,
                "execution_result": "simulated",
                "processing_time": context.stage_timings["execution"],
            }

        except Exception as e:
            context.error_log.append(
                {
                    "stage": "execution",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }
            )

            return {
                "success": False,
                "error": str(e),
                "processing_time": time.time() - stage_start,
            }

    async def _run_reflection_stage(self, context: PipelineContext) -> Dict[str, Any]:
        """Run the reflection stage."""
        stage_start = time.time()

        try:
            # Get output from execution (simulated for now)
            output = "Simulated execution output"

            # Run reflection module
            reflection_result = await self.reflection.reflect(
                output=output,
                goal=context.original_input,
                context={},
                max_iterations=context.config.get("max_reflection_iterations", 3),
            )

            context.reflection_result = reflection_result
            context.stage_timings["reflection"] = time.time() - stage_start

            return {
                "success": True,
                "reflection_result": reflection_result,
                "processing_time": context.stage_timings["reflection"],
            }

        except Exception as e:
            context.error_log.append(
                {
                    "stage": "reflection",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }
            )

            return {
                "success": False,
                "error": str(e),
                "processing_time": time.time() - stage_start,
            }

    async def _run_approval_stage(self, context: PipelineContext) -> Dict[str, Any]:
        """Run the approval stage."""
        stage_start = time.time()

        try:
            # Determine if approval is needed
            if not self._requires_approval(context):
                return {
                    "success": True,
                    "approval_required": False,
                    "processing_time": time.time() - stage_start,
                }

            # Request approval
            gate_id = await self.approval.request_approval(
                workspace_id=context.workspace_id,
                user_id=context.user_id,
                output=(
                    context.reflection_result.final_output
                    if context.reflection_result
                    else context.original_input
                ),
                risk_level=self._calculate_risk_level(context),
                reason="Cognitive processing requires human approval",
            )

            # Wait for approval (with timeout)
            timeout = context.config.get("approval_timeout_seconds", 300)
            approval_response = await self.approval.wait_for_approval(
                gate_id, timeout=timeout
            )

            context.approval_result = {
                "gate_id": gate_id,
                "approved": approval_response.approved,
                "feedback": approval_response.feedback,
            }

            context.stage_timings["approval"] = time.time() - stage_start

            return {
                "success": True,
                "approval_required": True,
                "approval_result": context.approval_result,
                "processing_time": context.stage_timings["approval"],
            }

        except Exception as e:
            context.error_log.append(
                {
                    "stage": "approval",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }
            )

            return {
                "success": False,
                "error": str(e),
                "processing_time": time.time() - stage_start,
            }

    def _requires_approval(self, context: PipelineContext) -> bool:
        """Determine if approval is required."""
        # Check plan risk level
        if context.execution_plan and context.execution_plan.requires_approval:
            return True

        # Check reflection result
        if (
            context.reflection_result
            and context.reflection_result.requires_human_approval
        ):
            return True

        # Check configuration
        if context.config.get("force_approval", False):
            return True

        return False

    def _calculate_risk_level(self, context: PipelineContext) -> int:
        """Calculate risk level (1-5)."""
        risk_level = 1

        # Plan risk
        if context.execution_plan:
            plan_risk = {"low": 1, "medium": 2, "high": 3, "critical": 4}.get(
                context.execution_plan.risk_level.value, 2
            )
            risk_level = max(risk_level, plan_risk)

        # Cost risk
        if context.execution_plan:
            cost = context.execution_plan.total_cost.total_cost_usd
            if cost > 1.0:
                risk_level = max(risk_level, 3)
            elif cost > 0.5:
                risk_level = max(risk_level, 2)

        return min(5, risk_level)

    async def _run_stage_hooks(
        self, stage: PipelineStage, hook_type: str, context: PipelineContext
    ):
        """Run hooks for a specific stage."""
        hooks = self.hooks.get(stage, [])

        # Filter by hook type
        filtered_hooks = [h for h in hooks if h.hook_type == hook_type]

        # Sort by priority (higher first)
        filtered_hooks.sort(key=lambda h: h.priority, reverse=True)

        # Execute hooks
        for hook in filtered_hooks:
            try:
                if asyncio.iscoroutinefunction(hook.function):
                    await hook.function(context)
                else:
                    hook.function(context)
            except Exception as e:
                context.error_log.append(
                    {
                        "stage": stage.value,
                        "hook_type": hook_type,
                        "hook_error": str(e),
                        "timestamp": datetime.now().isoformat(),
                    }
                )

    def add_hook(
        self,
        stage: PipelineStage,
        hook_type: str,
        function: Callable,
        priority: int = 0,
    ):
        """Add a hook to a pipeline stage."""
        hook = PipelineHook(
            stage=stage, hook_type=hook_type, function=function, priority=priority
        )
        self.hooks[stage].append(hook)

    def remove_hook(self, stage: PipelineStage, hook_type: str, function: Callable):
        """Remove a hook from a pipeline stage."""
        hooks = self.hooks.get(stage, [])
        self.hooks[stage] = [
            h for h in hooks if h.function != function or h.hook_type != hook_type
        ]

    def get_pipeline_status(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a running pipeline."""
        context = self.active_contexts.get(request_id)
        if not context:
            return None

        return {
            "request_id": request_id,
            "current_stage": context.current_stage.value,
            "status": context.status.value,
            "start_time": context.start_time.isoformat(),
            "stage_timings": context.stage_timings,
            "error_count": len(context.error_log),
        }

    def cancel_pipeline(self, request_id: str) -> bool:
        """Cancel a running pipeline."""
        context = self.active_contexts.get(request_id)
        if context and context.status == PipelineStatus.RUNNING:
            context.status = PipelineStatus.CANCELLED
            return True
        return False

    def _calculate_total_tokens(self, stage_results: Dict[str, Any]) -> int:
        """Calculate total tokens used across all stages."""
        total = 0

        for stage_name, result in stage_results.items():
            if isinstance(result, dict) and "tokens_used" in result:
                total += result["tokens_used"]

        return total

    def _calculate_total_cost(self, stage_results: Dict[str, Any]) -> float:
        """Calculate total cost across all stages."""
        total = 0.0

        for stage_name, result in stage_results.items():
            if isinstance(result, dict) and "cost_usd" in result:
                total += result["cost_usd"]

        return total

    def _calculate_total_time(self, stage_results: Dict[str, Any]) -> float:
        """Calculate total processing time."""
        total = 0.0

        for stage_name, result in stage_results.items():
            if isinstance(result, dict) and "processing_time" in result:
                total += result["processing_time"]

        return total

    def get_pipeline_stats(self) -> Dict[str, Any]:
        """Get pipeline execution statistics."""
        # This would typically track historical data
        # For now, return current active pipelines
        return {
            "active_pipelines": len(self.active_contexts),
            "total_hooks": sum(len(hooks) for hooks in self.hooks.values()),
            "supported_stages": [stage.value for stage in PipelineStage],
        }
