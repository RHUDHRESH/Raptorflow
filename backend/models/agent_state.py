"""
LangGraph state schemas shared across supervisors and agents.
These models provide a typed contract for state transitions between nodes.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from backend.models.content import BlogRequest, EmailRequest, SocialPostRequest
from backend.models.persona import ICPRequest, ICPResponse, PersonaNarrative


class BaseAgentState(BaseModel):
    """Common fields carried through every graph execution."""

    correlation_id: Optional[str] = None
    workspace_id: Optional[UUID] = None
    goal: Optional[str] = None
    context: Dict[str, Any] = Field(default_factory=dict)
    history: List[Dict[str, Any]] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    completed: bool = False
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        from_attributes = True


class ResearchState(BaseAgentState):
    """State for customer intelligence / ICP generation graphs."""

    icp_request: Optional[ICPRequest] = None
    icp: Optional[ICPResponse] = None
    persona_narrative: Optional[PersonaNarrative] = None
    tags: List[str] = Field(default_factory=list)


class ContentState(BaseAgentState):
    """State for content generation graphs."""

    content_type: Optional[str] = None
    blog_request: Optional[BlogRequest] = None
    email_request: Optional[EmailRequest] = None
    social_request: Optional[SocialPostRequest] = None
    generated_assets: List[Dict[str, Any]] = Field(default_factory=list)
    brand_voice: Optional[str] = None
    approval_status: Optional[str] = Field(default="draft", description="draft|review|approved|rejected")


class StrategyState(BaseAgentState):
    """State for strategy/ADAPT supervisors."""

    selected_icps: List[UUID] = Field(default_factory=list)
    research_summaries: List[Dict[str, Any]] = Field(default_factory=list)
    campaign_plan: Optional[Dict[str, Any]] = None
    checkpoints: List[str] = Field(default_factory=list)


class ExecutionState(BaseAgentState):
    """State for execution/publishing supervisors."""

    move_id: Optional[UUID] = None
    scheduled_tasks: List[Dict[str, Any]] = Field(default_factory=list)
    publishing_log: List[Dict[str, Any]] = Field(default_factory=list)


class AnalyticsState(BaseAgentState):
    """State for analytics supervisors."""

    move_id: Optional[UUID] = None
    metrics: Dict[str, Any] = Field(default_factory=dict)
    insights: List[Dict[str, Any]] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)

