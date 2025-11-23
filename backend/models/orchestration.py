"""
Data models for memory-aware orchestration.

This module defines the data structures used by the intelligent supervisor
for context propagation, workflow checkpoints, and adaptive agent selection.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class AgentContext(BaseModel):
    """
    Comprehensive context passed to all agents for intelligent execution.

    This context carries all relevant information through the agent hierarchy,
    enabling agents to make informed decisions based on workspace history,
    user preferences, and past performance.

    Attributes:
        workspace_id: Workspace identifier for multi-tenancy
        correlation_id: Unique ID for tracking this execution
        user_id: User who initiated this request
        brand_voice: Brand voice profile for content generation
        target_icps: Target customer profiles for this execution
        past_successes: List of similar successful tasks
        user_preferences: User-specific preferences and settings
        task_history: Recent task executions in this workspace
        performance_data: Performance metrics for agents in this workspace
        budget_constraints: Optional budget/resource limits
        quality_thresholds: Minimum quality scores required
        custom_metadata: Additional workspace-specific data
    """

    workspace_id: UUID = Field(
        ...,
        description="Workspace identifier for multi-tenant isolation",
    )
    correlation_id: str = Field(
        ...,
        description="Unique ID for tracking this execution across services",
    )
    user_id: Optional[UUID] = Field(
        None,
        description="User who initiated this request",
    )
    brand_voice: Optional[Dict[str, Any]] = Field(
        None,
        description="Brand voice profile (tone, style, vocabulary)",
    )
    target_icps: List[UUID] = Field(
        default_factory=list,
        description="Target customer profile IDs for this execution",
    )
    past_successes: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Similar successful tasks from memory",
    )
    user_preferences: Dict[str, Any] = Field(
        default_factory=dict,
        description="User-specific preferences and settings",
    )
    task_history: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Recent task executions in this workspace",
    )
    performance_data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Performance metrics for agents (success rate, quality, speed)",
    )
    budget_constraints: Optional[Dict[str, Any]] = Field(
        None,
        description="Budget/resource limits (API calls, time, cost)",
    )
    quality_thresholds: Dict[str, float] = Field(
        default_factory=lambda: {
            "content_quality": 0.7,
            "strategy_viability": 0.8,
            "research_depth": 0.75,
        },
        description="Minimum quality scores required for approval",
    )
    custom_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional workspace-specific data",
    )

    class Config:
        """Pydantic model configuration."""
        from_attributes = True
        json_encoders = {
            UUID: lambda v: str(v),
            datetime: lambda v: v.isoformat(),
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return self.model_dump(mode='python')


class CheckpointCondition(str, Enum):
    """Conditions that can trigger a workflow checkpoint."""

    AFTER_STAGE = "after_stage"  # After completing a specific stage
    BEFORE_EXECUTION = "before_execution"  # Before publishing/executing
    QUALITY_THRESHOLD = "quality_threshold"  # When quality is below threshold
    BUDGET_LIMIT = "budget_limit"  # When approaching budget limits
    MANUAL = "manual"  # Manually defined checkpoint
    ERROR_OCCURRED = "error_occurred"  # When an error occurs


class CheckpointAction(str, Enum):
    """Actions that can be taken at a checkpoint."""

    REQUEST_APPROVAL = "request_approval"  # Pause and request user approval
    AUTO_APPROVE = "auto_approve"  # Automatically approve if conditions met
    AUTO_REJECT = "auto_reject"  # Automatically reject if conditions met
    NOTIFY_ONLY = "notify_only"  # Just notify, don't pause


class WorkflowCheckpoint(BaseModel):
    """
    A single checkpoint in the workflow.

    Checkpoints allow for human-in-the-loop oversight at critical stages
    while supporting auto-approval for routine cases.

    Attributes:
        name: Unique checkpoint identifier
        description: Human-readable description
        condition: What triggers this checkpoint
        condition_params: Parameters for the condition (e.g., stage name, threshold)
        action: What to do when checkpoint is reached
        timeout_seconds: How long to wait for approval before auto-action
        auto_approve_if: Conditions that enable auto-approval
        required_approvers: User IDs who can approve (empty = any user)
        notify_users: User IDs to notify when checkpoint is reached
    """

    name: str = Field(
        ...,
        description="Unique checkpoint identifier",
    )
    description: str = Field(
        ...,
        description="Human-readable description of this checkpoint",
    )
    condition: CheckpointCondition = Field(
        ...,
        description="What triggers this checkpoint",
    )
    condition_params: Dict[str, Any] = Field(
        default_factory=dict,
        description="Parameters for the condition",
    )
    action: CheckpointAction = Field(
        default=CheckpointAction.REQUEST_APPROVAL,
        description="What to do when checkpoint is reached",
    )
    timeout_seconds: Optional[int] = Field(
        None,
        description="Timeout for approval (None = no timeout)",
    )
    auto_approve_if: Optional[Dict[str, Any]] = Field(
        None,
        description="Conditions that enable auto-approval",
    )
    required_approvers: List[UUID] = Field(
        default_factory=list,
        description="User IDs who can approve (empty = any user)",
    )
    notify_users: List[UUID] = Field(
        default_factory=list,
        description="User IDs to notify when checkpoint is reached",
    )

    class Config:
        """Pydantic model configuration."""
        from_attributes = True
        json_encoders = {UUID: lambda v: str(v)}


class WorkflowCheckpoints(BaseModel):
    """
    Complete checkpoint configuration for a workflow.

    Defines all checkpoints, their triggers, and approval rules for
    human-in-the-loop workflow management.

    Attributes:
        workspace_id: Workspace these checkpoints belong to
        checkpoints: List of checkpoint definitions
        default_timeout: Default timeout for all checkpoints
        auto_approve_for_user: Users who get auto-approval
        enabled: Whether checkpoints are enabled
    """

    workspace_id: UUID = Field(
        ...,
        description="Workspace these checkpoints belong to",
    )
    checkpoints: List[WorkflowCheckpoint] = Field(
        default_factory=list,
        description="List of checkpoint definitions",
    )
    default_timeout: int = Field(
        default=3600,
        description="Default timeout in seconds (1 hour)",
    )
    auto_approve_for_users: List[UUID] = Field(
        default_factory=list,
        description="Users who automatically get approvals",
    )
    enabled: bool = Field(
        default=True,
        description="Whether checkpoints are enabled for this workspace",
    )

    class Config:
        """Pydantic model configuration."""
        from_attributes = True
        json_encoders = {UUID: lambda v: str(v)}

    def get_checkpoint(self, name: str) -> Optional[WorkflowCheckpoint]:
        """Get a checkpoint by name."""
        for checkpoint in self.checkpoints:
            if checkpoint.name == name:
                return checkpoint
        return None

    def should_pause(
        self,
        checkpoint_name: str,
        context: Dict[str, Any],
    ) -> bool:
        """
        Determine if workflow should pause at this checkpoint.

        Args:
            checkpoint_name: Name of the checkpoint
            context: Current execution context

        Returns:
            True if should pause for approval, False if can auto-approve
        """
        checkpoint = self.get_checkpoint(checkpoint_name)
        if not checkpoint or not self.enabled:
            return False

        # Check if auto-approve conditions are met
        if checkpoint.action == CheckpointAction.AUTO_APPROVE:
            return False

        if checkpoint.auto_approve_if:
            if self._check_auto_approve_conditions(checkpoint.auto_approve_if, context):
                return False

        # Check if user has auto-approval
        user_id = context.get("user_id")
        if user_id and UUID(user_id) in self.auto_approve_for_users:
            return False

        return checkpoint.action == CheckpointAction.REQUEST_APPROVAL

    def _check_auto_approve_conditions(
        self,
        conditions: Dict[str, Any],
        context: Dict[str, Any],
    ) -> bool:
        """
        Check if auto-approve conditions are satisfied.

        Args:
            conditions: Auto-approve condition rules
            context: Current execution context

        Returns:
            True if all conditions are met
        """
        for key, expected_value in conditions.items():
            # Check quality thresholds
            if key == "quality_above":
                quality = context.get("quality_score", 0.0)
                if quality < expected_value:
                    return False

            # Check success rate
            elif key == "success_rate_above":
                success_rate = context.get("agent_success_rate", 0.0)
                if success_rate < expected_value:
                    return False

            # Check budget
            elif key == "budget_remaining_above":
                budget_pct = context.get("budget_remaining_pct", 0.0)
                if budget_pct < expected_value:
                    return False

            # Custom conditions
            elif key in context:
                if context[key] != expected_value:
                    return False

        return True


class SelfCorrectionConfig(BaseModel):
    """
    Configuration for self-correction loops in content/strategy generation.

    Attributes:
        max_iterations: Maximum number of correction iterations
        min_quality_score: Minimum quality score to accept (0.0-1.0)
        critique_model: Model to use for critique (default: same as generation)
        improvement_threshold: Minimum improvement needed to continue (0.0-1.0)
        critique_aspects: Specific aspects to critique (clarity, persuasiveness, etc.)
        store_failures: Whether to store failed attempts in memory
    """

    max_iterations: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Maximum number of correction iterations",
    )
    min_quality_score: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        description="Minimum quality score to accept",
    )
    critique_model: Optional[str] = Field(
        None,
        description="Model to use for critique (None = same as generation)",
    )
    improvement_threshold: float = Field(
        default=0.1,
        ge=0.0,
        le=1.0,
        description="Minimum improvement needed to continue iterating",
    )
    critique_aspects: List[str] = Field(
        default_factory=lambda: [
            "clarity",
            "persuasiveness",
            "brand_alignment",
            "factual_accuracy",
            "engagement_potential",
        ],
        description="Aspects to critique",
    )
    store_failures: bool = Field(
        default=True,
        description="Store failed attempts in memory for learning",
    )

    class Config:
        """Pydantic model configuration."""
        from_attributes = True
