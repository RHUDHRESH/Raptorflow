"""
Fallback Handler for Integration Components

Graceful degradation and human escalation for critical failures.
Implements PROMPT 70 from STREAM_3_COGNITIVE_ENGINE.
"""

import asyncio
import json
import logging
import traceback
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from ..models import ExecutionPlan, PlanStep


class FallbackLevel(Enum):
    """Levels of fallback strategies."""
    RETRY = "retry"
    ALTERNATIVE = "alternative"
    DEGRADED = "degraded"
    HUMAN_ESCALATION = "human_escalation"
    CRITICAL_FAILURE = "critical_failure"


class FallbackTrigger(Enum):
    """Triggers for fallback activation."""
    TIMEOUT = "timeout"
    ERROR_RATE = "error_rate"
    COST_EXCEEDED = "cost_exceeded"
    RESOURCE_EXHAUSTED = "resource_exhausted"
    DEPENDENCY_FAILURE = "dependency_failure"
    QUALITY_THRESHOLD = "quality_threshold"
    APPROVAL_TIMEOUT = "approval_timeout"
    SYSTEM_OVERLOAD = "system_overload"


@dataclass
class FallbackAction:
    """A fallback action to take."""
    action_id: str
    level: FallbackLevel
    trigger: FallbackTrigger
    description: str
    condition: str
    action: Callable
    priority: int  # Lower numbers = higher priority
    max_attempts: int
    cooldown_seconds: int
    metadata: Dict[str, Any] = field(default_factory=dict)
    last_used: Optional[datetime] = field(default=None)


@dataclass
class FallbackResult:
    """Result of a fallback action."""
    action_id: str
    success: bool
    result: Any
    error: Optional[Exception]
    execution_time_ms: int
    attempts_used: int
    level: FallbackLevel
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FallbackReport:
    """Complete report of fallback handling."""
    original_error: Exception
    trigger: FallbackTrigger
        actions_attempted: List[FallbackResult]
        final_result: Any
        total_time_ms: int
        escalated: bool
        human_contacted: bool
        metadata: Dict[str, Any] = field(default_factory=dict)


class FallbackHandler:
    """
    Graceful degradation and human escalation for critical failures.

    Provides multiple levels of fallback strategies.
    """

    def __init__(self, notification_client=None, escalation_client=None):
        """
        Initialize the fallback handler.

        Args:
            notification_client: Client for notifications
            escalation_client: Client for human escalation
        """
        self.notification_client = notification_client
        self.escalation_client = escalation_client

        # Fallback actions registry
        self.fallback_actions: List[FallbackAction] = []
        self.action_registry: Dict[str, Callable] = {}

        # Fallback statistics
        self.stats = {
            "total_fallbacks": 0,
            "successful_fallbacks": 0,
            "escalations": 0,
            "human_contacts": 0,
            "retry_fallbacks": 0,
            "alternative_fallbacks": 0,
            "degraded_fallbacks": 0,
            "critical_failures": 0
        }

        # Configuration
        self.config = {
            "enable_fallback": True,
            "enable_escalation": True,
            "max_escalation_level": 3,
            "default_timeout_seconds": 300,
            "error_rate_threshold": 0.1,  # 10%
            "cost_threshold_usd": 10.0,
            "resource_threshold": 0.9,
            "quality_threshold": 0.5
            "enable_auto_retry": True,
            "enable_alternative": True,
            "enable_degraded_mode": True
        }

        # Setup default fallback actions
        self._setup_default_actions()

        # Setup action registry
        self._setup_action_registry()

        # Cooldown tracking
        self.action_cooldowns: Dict[str, datetime] = {}

    async def handle_failure(self, error: Exception, context: Dict[str, Any] = None,
                           trigger: FallbackTrigger = None,
                           max_level: FallbackLevel = None) -> FallbackReport:
        """
        Handle a failure with appropriate fallback strategy.

        Args:
            error: The error that occurred
            context: Execution context
            trigger: What triggered the fallback
            max_level: Maximum fallback level to attempt

        Returns:
            Fallback report
        """
        if not self.config["enable_fallback"]:
            return FallbackReport(
                original_error=error,
                trigger=trigger or FallbackTrigger.ERROR_RATE,
                actions_attempted=[],
                final_result=None,
                total_time_ms=0,
                escalated=False,
                human_contacted=False,
                metadata={"fallback_disabled": True}
            )

        start_time = datetime.now()
        actions_attempted = []
        final_result = None
        escalated = False
        human_contacted = False

        # Determine trigger if not provided
        if trigger is None:
            trigger = self._determine_trigger(error, context)

        # Determine max level if not provided
        if max_level is None:
            max_level = self._determine_max_level(error, trigger, context)

        # Try fallback actions in order of priority
        for action in self._get_applicable_actions(trigger, max_level):
            if action.level > max_level:
                continue

            # Check cooldown
            if self._is_in_cooldown(action.action_id):
                continue

            try:
                    # Execute fallback action
                    result = await self._execute_fallback_action(action, error, context)
                    actions_attempted.append(result)

                    if result.success:
                        final_result = result.result
                        break
                    else:
                        # Action failed, continue to next level
                        continue

                except Exception as fallback_error:
                    # Fallback action itself failed
                    actions_attempted.append(FallbackResult(
                        action_id=action.action_id,
                        success=False,
                        result=None,
                        error=fallback_error,
                        execution_time_ms=0,
                        attempts_used=1,
                        level=action.level,
                        metadata={"fallback_action_failed": True}
                    )
                    continue

            except Exception as e:
                # Unexpected error during fallback
                print(f"Fallback execution error: {e}")
                continue

        # Calculate total time
        total_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)

        # Check if human was contacted
        human_contacted = any(
            result.metadata.get("human_contacted", False)
            for result in actions_attempted
        )

        # Check if escalation occurred
        escalated = any(
            result.metadata.get("escalated", False)
            for result in actions_attempted
        )

        # Create report
        report = FallbackReport(
            original_error=error,
            trigger=trigger,
            actions_attempted=actions_attempted,
            final_result=final_result,
            total_time_ms=total_time_ms,
            escalated=escalated,
            human_contacted=human_contacted,
            metadata={
                "max_level": max_level.value if max_level else None,
                "trigger_determined": trigger is not None,
                "context_provided": context is not None
            }
        )

        # Update statistics
        self._update_stats(report)

        return report

    async def handle_step_failure(self, step: PlanStep, error: Exception,
                                 context: Dict[str, Any] = None) -> FallbackResult:
        """
        Handle a step-specific failure.

        Args:
            step: The failed step
            error: The error that occurred
            context: Execution context

        Returns:
            Fallback result
        """
        # Determine trigger for step failure
        trigger = self._determine_step_trigger(step, error, context)

        # Create fallback context
        step_context = {
            "step": step,
            "error": error,
            "context": context,
            "step_id": step.id,
            "step_description": step.description,
            "agent": step.agent,
            "tools": step.tools
        }

        # Use general failure handler
        report = await self.handle_failure(error, step_context, trigger)

        # Extract the last action result
        if report.actions_attempted:
            return report.actions_attempted[-1]

        return FallbackResult(
            action_id="",
            success=False,
            result=None,
            error=report.original_error,
            execution_time_ms=0,
            attempts_used=0,
            level=FallbackLevel.RETRY,
            metadata={"no_actions_available": True}
        )

    async def handle_plan_failure(self, plan: ExecutionPlan, error: Exception,
                                context: Dict[str, Any] = None) -> FallbackReport:
        """
        Handle a plan-level failure.

        Args:
            plan: The failed plan
            error: The error that occurred
            context: Execution context

        Returns:
            Fallback report
        """
        # Determine trigger for plan failure
        trigger = self._determine_plan_trigger(plan, error, context)

        # Create plan context
        plan_context = {
            "plan": plan,
            "error": error,
            "context": context,
            "plan_id": plan.metadata.get("plan_id", "unknown"),
            "plan_goal": plan.goal,
            "total_steps": len(plan.steps),
            "estimated_cost": plan.total_cost.total_cost_usd
        }

        # Use general failure handler
        return await self.handle_failure(error, plan_context, trigger)

    def _setup_default_actions(self) -> None:
        """Setup default fallback actions."""
        # Retry action
        self.fallback_actions.append(FallbackAction(
            action_id="retry_with_backoff",
            level=FallbackLevel.RETRY,
            trigger=FallbackTrigger.ERROR_RATE,
            description="Retry with exponential backoff",
            condition="error_count < 3 and error_type in retryable_exceptions",
            action=self._retry_with_backoff,
            priority=1,
            max_attempts=3,
            cooldown_seconds=5
        ))

        # Alternative action
        self.fallback_actions.append(FallbackAction(
            action_id="use_alternative_method",
            level=FallbackLevel.ALTERNATIVE,
            trigger=FallbackTrigger.DEPENDENCY_FAILURE,
            description="Use alternative method or approach",
            condition="alternative_available and not critical_path",
            action=self._use_alternative_method,
            priority=2,
            max_attempts=1,
            cooldown_seconds=0
        ))

        # Degraded mode action
        self.fallback_actions.append(FallbackAction(
            action_id="degraded_mode",
            level=FallbackLevel.DEGRADED,
            trigger=FallbackTrigger.RESOURCE_EXHAUSTED,
            description="Switch to degraded mode with reduced functionality",
            condition="resource_usage > 90% or system_overload",
            action=self._switch_degraded_mode,
            priority=3,
            max_attempts=1,
            cooldown_seconds=10
        ))

        # Human escalation action
        self.fallback_actions.append(FallbackAction(
            action_id="human_escalation",
            level=FallbackLevel.HUMAN_ESCALATION,
            trigger=FallbackLevel.CRITICAL_FAILURE,
            description="Escalate to human operator",
            condition="critical_failure or max_attempts_exceeded",
            action=self._escalate_to_human,
            priority=4,
            max_attempts=1,
            cooldown_seconds=0
        ))

        # Critical failure action
        self.fallback_actions.append(FallbackAction(
            action_id="critical_failure",
            level=FallbackLevel.CRITICAL_FAILURE,
            trigger=FallbackLevel.CRITICAL_FAILURE,
            description="Handle critical system failure",
            condition="always",
            action=self._handle_critical_failure,
            priority=5,
            max_attempts=1,
            cooldown_seconds=0
        ))

    def _setup_action_registry(self) -> None:
        """Setup action registry for common fallback actions."""
        self.action_registry = {
            "retry_with_backoff": self._retry_with_backoff_action,
            "use_alternative_method": self._use_alternative_method_action,
            "switch_degraded_mode": self._switch_degraded_mode_action,
            "escalate_to_human": self._escalate_to_human_action,
            "handle_critical_failure": self._handle_critical_failure_action
        }

    def _get_applicable_actions(self, trigger: FallbackTrigger,
                              max_level: FallbackLevel) -> List[FallbackAction]:
        """Get applicable fallback actions for trigger and level."""
        applicable = []

        for action in self.fallback_actions:
            if action.trigger == trigger and action.level <= max_level:
                # Check cooldown
                if not self._is_in_cooldown(action.action_id):
                    applicable.append(action)

        # Sort by priority (lower numbers = higher priority)
        applicable.sort(key=lambda a: a.priority)

        return applicable

    def _determine_trigger(self, error: Exception, context: Dict[str, Any] = None) -> FallbackTrigger:
        """Determine what triggered the fallback."""
        error_message = str(error).lower()
        error_type = type(error).__name__

        # Check error patterns
        if "timeout" in error_message:
            return FallbackTrigger.TIMEOUT
        elif "connection" in error_message:
            return FallbackTrigger.DEPENDENCY_FAILURE
        elif "permission" in error_message:
            return FallbackTrigger.DEPENDENCY_FAILURE
        elif "rate limit" in error_message:
            return FallbackTrigger.ERROR_RATE
        elif "cost" in error_message:
            return FallbackTrigger.COST_EXCEEDED
        elif "resource" in error_message:
            return FallbackTrigger.RESOURCE_EXHAUSTED
        elif "quality" in error_message:
            return FallbackTrigger.QUALITY_THRESHOLD
        elif "approval" in error_message:
            return FallbackTrigger.APPROVAL_TIMEOUT
        elif "system" in error_message:
            return FallbackTrigger.SYSTEM_OVERLOAD
        else:
            return FallbackTrigger.ERROR_RATE

    def _determine_max_level(self, error: Exception, trigger: FallbackTrigger,
                           context: Dict[str, Any] = None) -> FallbackLevel:
        """Determine maximum fallback level based on error and context."""
        # Critical errors always get highest level
        critical_errors = [
            SystemError, MemoryError, OverflowError, KeyboardInterrupt
        ]
        if type(error) in critical_errors:
            return FallbackLevel.CRITICAL_FAILURE

        # Context-based level determination
        if context:
            # High cost operations get lower max level
            if context.get("estimated_cost", 0) > 10.0:
                return FallbackLevel.DEGRADED

            # High risk operations get lower max level
            if context.get("risk_level") in ["high", "critical"]:
                return FallbackLevel.HUMAN_ESCALATION

            # User-facing operations get lower max level
            if context.get("user_facing", False):
                return FallbackLevel.ALTERNATIVE

        # Default based on trigger
        trigger_levels = {
            FallbackTrigger.TIMEOUT: FallbackLevel.ALTERNATIVE,
            FallbackTrigger.ERROR_RATE: FallbackLevel.RETRY,
            FallbackTrigger.COST_EXCEEDED: FallbackLevel.DEGRADED,
            FallbackTrigger.RESOURCE_EXHAUSTED: FallbackLevel.DEGRADED,
            FallbackTrigger.DEPENDENCY_FAILURE: FallbackLevel.ALTERNATIVE,
            FallbackTrigger.QUALITY_THRESHOLD: FallbackLevel.DEGRADED,
            FallbackTrigger.APPROVAL_TIMEOUT: FallbackLevel.HUMAN_ESCALATION,
            FallbackTrigger.SYSTEM_OVERLOAD: FallbackLevel.CRITICAL_FAILURE
        }

        return trigger_levels.get(trigger, FallbackLevel.RETRY)

    def _determine_step_trigger(self, step: PlanStep, error: Exception,
                             context: Dict[str, Any] = None) -> FallbackTrigger:
        """Determine trigger for step failure."""
        # Step-specific triggers
        if step.risk_level in ["high", "critical"]:
            return FallbackTrigger.DEPENDENCY_FAILURE

        error_message = str(error).lower()

        if "timeout" in error_message:
            return FallbackTrigger.TIMEOUT
        elif "dependency" in error_message:
            return FallbackTrigger.DEPENDENCY_FAILURE
        else:
            return FallbackTrigger.ERROR_RATE

    def _determine_plan_trigger(self, plan: ExecutionPlan, error: Exception,
                             context: Dict[str, Any] = None) -> FallbackTrigger:
        """Determine trigger for plan failure."""
        # Plan-specific triggers
        if plan.risk_level in ["high", "critical"]:
            return FallbackLevel.HUMAN_ESCALATION

        error_message = str(error).lower()

        if "dependency" in error_message:
            return FallbackTrigger.DEPENDENCY_FAILURE
        elif "timeout" in error_message:
            return FallbackTrigger.TIMEOUT
        elif "cost" in error_message:
            return FallbackTrigger.COST_EXCEEDED
        else:
            return FallbackTrigger.ERROR_RATE

    def _is_in_cooldown(self, action_id: str) -> bool:
        """Check if action is in cooldown period."""
        if action_id not in self.action_cooldowns:
            return False

        cooldown = self.action_cooldowns[action_id]
        return datetime.now() < cooldown

    def _set_cooldown(self, action_id: str, cooldown_seconds: int) -> None:
        """Set cooldown for an action."""
        self.action_cooldowns[action_id] = datetime.now() + timedelta(seconds=cooldown_seconds)

    async def _execute_fallback_action(self, action: FallbackAction, error: Exception,
                                context: Dict[str, Any]) -> FallbackResult:
        """Execute a fallback action."""
        start_time = time.time()

        try:
            # Get action from registry
            action_func = self.action_registry.get(action.action_id)
            if not action_func:
                raise Exception(f"Unknown fallback action: {action.action_id}")

            # Execute action
            if asyncio.iscoroutinefunction(action_func):
                result = await action_func(error, context)
            else:
                result = action_func(error, context)

            execution_time_ms = int((time.time() - start_time) * 1000)

            return FallbackResult(
                action_id=action.action_id,
                success=True,
                result=result,
                error=None,
                execution_time_ms=execution_time_ms,
                attempts_used=1,
                level=action.level,
                metadata={
                    "action_name": action.description,
                    "trigger": action.trigger.value
                }
            )

        except Exception as fallback_error:
            execution_time_ms = int((time.time() - start_time) * 1000)

            return FallbackResult(
                action_id=action.action_id,
                success=False,
                result=None,
                error=fallback_error,
                execution_time_ms=execution_time_ms,
                attempts_used=1,
                level=action.level,
                metadata={
                    "action_name": action.description,
                    "trigger": action.trigger.value,
                    "fallback_error": str(fallback_error)
                }
            )

    async def _retry_with_backoff_action(self, error: Exception,
                                      context: Dict[str, Any]) -> Any:
        """Retry with exponential backoff."""
        # This would integrate with the retry manager
        from .retry import RetryManager

        retry_manager = RetryManager()

        # Create retry config based on attempt count
        attempt_count = len(context.get("retry_attempts", [])) + 1
        base_delay = 1.0 * (2 ** (attempt_count - 1))
        max_delay = 60.0

        return await retry_manager.retry_with_backoff(
            lambda: None,  # Placeholder function that would retry the original operation
            max_retries=3,
            base_delay=base_delay,
            max_delay=max_delay
        )

    async def _use_alternative_method_action(self, error: Exception,
                                      context: Dict[str, Any]) -> Any:
        """Use alternative method or approach."""
        # This would implement alternative logic
        print(f"Using alternative method for: {error}")

        # Return mock alternative result
        return {
            "alternative": True,
            "original_error": str(error),
            "timestamp": datetime.now().isoformat()
        }

    def _switch_degraded_mode_action(self, error: Exception,
                                      context: Dict[str, Any]) -> Any:
        """Switch to degraded mode with reduced functionality."""
        # This would implement degraded mode logic
        print(f"Switching to degraded mode due to: {error}")

        return {
            "degraded": True,
            "original_error": str(error),
            "timestamp": datetime.now().isoformat(),
            "functionality": "reduced"
        }

    async def _escalate_to_human_action(self, error: Exception,
                                      context: Dict[str, Any]) -> Any:
        """Escalate to human operator."""
        if self.escalation_client:
            await self.escalation_client.escalate(
                error=error,
                context=context,
                priority="high",
                channel="email"
            )

        # Log escalation
        print(f"ESCALATED: {error}")

        return {
            "escalated": True,
            "original_error": str(error),
            "timestamp": datetime.now().isoformat(),
            "human_contacted": True
        }

    def _handle_critical_failure_action(self, error: Exception,
                                       context: Dict[str, Any]) -> Any:
        """Handle critical system failure."""
        # Log critical error
        print(f"CRITICAL FAILURE: {error}")

        # Try to save any remaining data
        try:
            if context and "trace_id" in context:
                # Save trace data
                pass  # Would integrate with trace storage
        except:
            pass

        return {
            "critical": True,
            "original_error": str(error),
            "timestamp": datetime.now().isoformat()
        }

    def _update_stats(self, report: FallbackReport) -> None:
        """Update fallback statistics."""
        self.stats["total_fallbacks"] += 1

        if report.success:
            self.stats["successful_fallbacks"] += 1

        if report.escalated:
            self.stats["escalations"] += 1

        if report.human_contacted:
            self.stats["human_contacts"] += 1

        # Update level-specific stats
        for action in report.actions_attempted:
            level = action.level.value
            if level == "retry":
                self.stats["retry_fallbacks"] += 1
            elif level == "alternative":
                self.stats["alternative_fallbacks"] += 1
            elif level == "degraded":
                self.stats["degraded_fallbacks"] += 1
            elif level == "critical":
                self.stats["critical_failures"] += 1

    def get_fallback_stats(self) -> Dict[str, Any]:
        """Get fallback statistics."""
        return self.stats

    def add_fallback_action(self, action: FallbackAction) -> None:
        """Add a custom fallback action."""
        self.fallback_actions.append(action)

        # Register in registry if function is provided
        if hasattr(action, 'action') and callable(action.action):
            self.action_registry[action.action_id] = action.action

    def remove_fallback_action(self, action_id: str) -> bool:
        """Remove a fallback action."""
        self.fallback_actions = [a for a in self.fallback_actions if a.action_id != action_id]
        return len(self.fallback_actions) < len(self.fallback_actions)

    def get_fallback_actions(self, trigger: FallbackTrigger = None,
                            level: FallbackLevel = None) -> List[FallbackAction]:
        """Get fallback actions by trigger and/or level."""
        actions = self.fallback_actions

        if trigger:
            actions = [a for a in actions if a.trigger == trigger]

        if level:
            actions = [a for a in actions if a.level == level]

        return actions

    def enable_fallback(self, enabled: bool = True) -> None:
        """Enable or disable fallback handling."""
        self.config["enable_fallback"] = enabled

    def enable_escalation(self, enabled: bool = True) -> None:
        """Enable or disable human escalation."""
        self.config["enable_escalation"] = enabled

    def set_config(self, **kwargs) -> None:
        """Update fallback configuration."""
        self.config.update(kwargs)

    def get_config(self) -> Dict[str, Any]:
        """Get current fallback configuration."""
        return self.config.copy()
