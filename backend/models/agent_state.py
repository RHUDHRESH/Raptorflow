"""
LangGraph state schemas shared across supervisors and agents.

This module defines typed state schemas for all LangGraph workflows in RaptorFlow.
Each supervisor (Research, Content, Strategy, Execution, Analytics) has a
corresponding state schema that defines the data passed between nodes in the graph.

Key Features:
- Type-safe state transitions between LangGraph nodes
- Serialization helpers for Redis/database persistence
- Common base state with correlation_id, workspace_id, and error tracking
- Supervisor-specific state extensions for domain-specific data

State Lifecycle:
1. State is initialized when a workflow starts
2. Each node reads current state, performs work, and updates state
3. State can be checkpointed to Redis for durability
4. State can be serialized to JSON for logging/debugging
5. State carries through the entire workflow until completion

Models in this module are used by all LangGraph supervisors to ensure
type safety and provide structured data access across node boundaries.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from backend.models.content import BlogRequest, EmailRequest, SocialPostRequest
from backend.models.persona import ICPRequest, ICPResponse, PersonaNarrative


class BaseAgentState(BaseModel):
    """
    Common fields carried through every graph execution.

    This base state is extended by all supervisor-specific states to provide
    consistent tracking, error handling, and serialization across all LangGraph
    workflows.

    All state updates should call touch() to update the updated_at timestamp,
    and record_error() to track errors without crashing the workflow.

    Attributes:
        correlation_id: Unique ID for tracking this workflow across services
        workspace_id: Workspace identifier for multi-tenancy
        goal: High-level objective for this workflow
        context: Arbitrary key-value context for node communication
        history: Chronological log of node executions and decisions
        errors: Non-fatal errors encountered during execution
        completed: Whether the workflow has finished successfully
        updated_at: Timestamp of last state modification
    """

    correlation_id: Optional[str] = Field(
        None,
        description="Unique ID for tracking this workflow across services",
    )
    workspace_id: Optional[UUID] = Field(
        None,
        description="Workspace identifier for multi-tenant isolation",
    )
    goal: Optional[str] = Field(
        None,
        description="High-level objective for this workflow execution",
    )
    context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary key-value context shared between nodes",
    )
    history: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Chronological log of node executions and decisions",
    )
    errors: List[str] = Field(
        default_factory=list,
        description="Non-fatal errors encountered during execution",
    )
    completed: bool = Field(
        default=False,
        description="Whether the workflow has finished successfully",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp of last state modification",
    )

    class Config:
        """Pydantic model configuration."""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }

    def touch(self) -> None:
        """
        Update the updated_at timestamp to mark state as modified.

        Call this method after any state update to track when changes occurred.
        """
        self.updated_at = datetime.now(timezone.utc)

    def record_error(self, error: str, node_name: Optional[str] = None) -> None:
        """
        Record a non-fatal error in the state.

        Use this to track errors that don't require halting the workflow,
        allowing graceful degradation and error recovery.

        Args:
            error: Error message or description
            node_name: Name of the node where error occurred (optional)
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        error_entry = f"[{timestamp}]"
        if node_name:
            error_entry += f" [{node_name}]"
        error_entry += f" {error}"
        self.errors.append(error_entry)
        self.touch()

    def add_history(
        self,
        node_name: str,
        action: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Add an entry to the execution history.

        Use this to create an audit trail of what happened during workflow
        execution, useful for debugging and observability.

        Args:
            node_name: Name of the node performing the action
            action: Description of what was done
            metadata: Additional context about the action
        """
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "node": node_name,
            "action": action,
        }
        if metadata:
            entry["metadata"] = metadata
        self.history.append(entry)
        self.touch()

    def to_json(self, indent: Optional[int] = None) -> str:
        """
        Serialize state to JSON string.

        Useful for logging, debugging, or storing state in text-based storage.

        Args:
            indent: Number of spaces for indentation (None for compact)

        Returns:
            JSON string representation of the state
        """
        return self.model_dump_json(indent=indent)

    @classmethod
    def from_json(cls, json_str: str) -> "BaseAgentState":
        """
        Deserialize state from JSON string.

        Args:
            json_str: JSON string to deserialize

        Returns:
            Reconstituted state object

        Raises:
            ValueError: If JSON is invalid or doesn't match schema
        """
        return cls.model_validate_json(json_str)

    def to_redis_value(self) -> str:
        """
        Serialize state for Redis storage.

        Redis stores values as strings, so this converts the state to a
        compact JSON representation suitable for Redis.

        Returns:
            Compact JSON string for Redis storage
        """
        return self.model_dump_json()

    @classmethod
    def from_redis_value(cls, redis_value: str) -> "BaseAgentState":
        """
        Deserialize state from Redis storage.

        Args:
            redis_value: JSON string retrieved from Redis

        Returns:
            Reconstituted state object

        Raises:
            ValueError: If Redis value is invalid or doesn't match schema
        """
        return cls.model_validate_json(redis_value)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert state to dictionary.

        Returns Python dict representation, useful for LangGraph native
        state management or database storage.

        Returns:
            Dictionary representation of the state
        """
        return self.model_dump(mode='python')


class ResearchState(BaseAgentState):
    """
    State for customer intelligence / ICP generation graphs.

    Used by the Research Supervisor to orchestrate ICP generation, tag
    enrichment, pain point mining, and persona narrative creation.

    Workflow Nodes:
        1. ICP Builder: Generates initial ICP from request
        2. Tag Enricher: Adds 50+ demographic/psychographic tags
        3. Pain Point Miner: Scrapes web sources for pain points
        4. Narrative Generator: Creates storytelling persona narrative

    Attributes:
        icp_request: Input request with company/product details
        icp: Generated ICP profile with demographics/psychographics
        persona_narrative: Storytelling narrative for the persona
        tags: Enriched tags from tag assignment agents
        past_successes: Memory references to similar successful ICPs
        preferences: User/workspace preferences for ICP generation
    """

    icp_request: Optional[ICPRequest] = Field(
        None,
        description="Input request with company/product details",
    )
    icp: Optional[ICPResponse] = Field(
        None,
        description="Generated ICP profile with demographics/psychographics",
    )
    persona_narrative: Optional[PersonaNarrative] = Field(
        None,
        description="Storytelling narrative for the persona",
    )
    tags: List[str] = Field(
        default_factory=list,
        description="Enriched tags from tag assignment agents",
    )
    past_successes: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Memory references to similar successful ICPs from agent memory",
    )
    preferences: Dict[str, Any] = Field(
        default_factory=dict,
        description="User/workspace preferences for ICP generation (e.g., preferred detail level, industry focus)",
    )


class ContentState(BaseAgentState):
    """
    State for content generation graphs.

    Used by the Content Supervisor to orchestrate multi-variant content
    generation with quality assessment and brand voice application.

    Workflow Nodes:
        1. Hook Generator: Creates 3-5 hook options
        2. Content Writer: Generates 3 content variants
        3. Brand Voice Stylist: Applies brand voice to content
        4. Content Critic: Assesses quality and provides feedback
        5. Content Refiner: Revises content based on critique

    Attributes:
        content_type: Type of content to generate (blog, email, social)
        blog_request: Blog-specific request parameters
        email_request: Email-specific request parameters
        social_request: Social post-specific request parameters
        generated_assets: List of generated content variants
        brand_voice: Brand voice profile to apply
        approval_status: Content approval status (draft|review|approved|rejected)
        past_successes: Memory of high-performing content for same ICP/topic
        preferences: Content generation preferences (tone, style, length)
    """

    content_type: Optional[str] = Field(
        None,
        description="Type of content to generate (blog, email, social)",
    )
    blog_request: Optional[BlogRequest] = Field(
        None,
        description="Blog-specific request parameters",
    )
    email_request: Optional[EmailRequest] = Field(
        None,
        description="Email-specific request parameters",
    )
    social_request: Optional[SocialPostRequest] = Field(
        None,
        description="Social post-specific request parameters",
    )
    generated_assets: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of generated content variants with metadata",
    )
    brand_voice: Optional[str] = Field(
        None,
        description="Brand voice profile to apply to content",
    )
    approval_status: Optional[str] = Field(
        default="draft",
        description="Content approval status: draft|review|approved|rejected",
    )
    past_successes: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Memory of high-performing content (hooks, blog structures) for same ICP/topic",
    )
    preferences: Dict[str, Any] = Field(
        default_factory=dict,
        description="Content generation preferences (tone, style, length, formatting)",
    )


class StrategyState(BaseAgentState):
    """
    State for strategy/ADAPT supervisors.

    Used by the Strategy Supervisor to orchestrate campaign planning using
    the ADAPT framework (Analyze, Design, Adapt, Plan, Test).

    Workflow Nodes:
        1. Analyzer: Analyzes market, competitors, and opportunities
        2. Designer: Designs campaign structure and Lines of Operation
        3. Adapter: Adapts strategy based on constraints
        4. Planner: Creates detailed task breakdown and timeline
        5. Tester: Validates plan for feasibility

    Attributes:
        selected_icps: ICPs/cohorts targeted by this campaign
        research_summaries: Market and competitive research findings
        campaign_plan: Structured campaign plan with tasks and timeline
        checkpoints: Strategic checkpoints for review and adaptation
    """

    selected_icps: List[UUID] = Field(
        default_factory=list,
        description="ICPs/cohorts targeted by this campaign",
    )
    research_summaries: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Market and competitive research findings",
    )
    campaign_plan: Optional[Dict[str, Any]] = Field(
        None,
        description="Structured campaign plan with tasks, timeline, and KPIs",
    )
    checkpoints: List[str] = Field(
        default_factory=list,
        description="Strategic checkpoints for review and adaptation",
    )


class ExecutionState(BaseAgentState):
    """
    State for execution/publishing supervisors.

    Used by the Execution Supervisor to orchestrate content scheduling,
    publishing, and distribution across channels.

    Workflow Nodes:
        1. Scheduler: Creates optimized publishing schedule
        2. Publisher: Posts content to channels (LinkedIn, Twitter, etc.)
        3. Monitor: Monitors publishing success/failures
        4. Responder: Handles engagement and responses

    Attributes:
        move_id: Campaign/move being executed
        scheduled_tasks: Scheduled publishing tasks with timestamps
        publishing_log: Chronological log of publish events and outcomes
    """

    move_id: Optional[UUID] = Field(
        None,
        description="Campaign/move being executed",
    )
    scheduled_tasks: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Scheduled publishing tasks with timestamps and channels",
    )
    publishing_log: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Chronological log of publish events and outcomes",
    )


class AnalyticsState(BaseAgentState):
    """
    State for analytics supervisors.

    Used by the Analytics Supervisor to collect metrics, generate insights,
    and provide strategic recommendations based on campaign performance.

    Workflow Nodes:
        1. Metrics Collector: Gathers performance data from all channels
        2. Insight Generator: Identifies patterns and anomalies
        3. Recommender: Provides strategic recommendations
        4. Report Builder: Creates executive summaries

    Attributes:
        move_id: Campaign/move being analyzed
        metrics: Real-time performance metrics (impressions, clicks, conversions)
        insights: AI-generated insights about performance patterns
        recommendations: Strategic recommendations for optimization
    """

    move_id: Optional[UUID] = Field(
        None,
        description="Campaign/move being analyzed",
    )
    metrics: Dict[str, Any] = Field(
        default_factory=dict,
        description="Real-time performance metrics (impressions, clicks, conversions)",
    )
    insights: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="AI-generated insights about performance patterns",
    )
    recommendations: List[str] = Field(
        default_factory=list,
        description="Strategic recommendations for campaign optimization",
    )

