"""
Pydantic models for Campaigns (Moves, Sprints, Tasks).

This module defines comprehensive schemas for campaign planning and execution
in RaptorFlow. It includes:

- Campaign (Move) planning with objectives, timelines, and KPIs
- Sprint-based execution with tasks and dependencies
- Lines of Operation (LOO) for multi-channel coordination
- Asset requirements and content planning
- Real-time performance metrics and analytics
- Anomaly detection and decision tracking

The campaign models follow military doctrine (Maneuver Warfare) adapted
for marketing: Moves represent campaigns, Sprints are execution cycles,
Lines of Operation organize work streams, and Tasks are actionable items.

Models in this module are used by the Strategy Supervisor and Execution
agents to orchestrate campaign planning, task management, and performance
monitoring.
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Optional, Literal, Any
from uuid import UUID
from datetime import datetime, date


class Task(BaseModel):
    """
    A single task within a campaign.

    Tasks are the atomic units of work in a campaign. They can be assigned
    to team members or agents, have dependencies on other tasks, and track
    completion status and effort.

    Task Types:
        - content_creation: Writing, designing, or producing content
        - publishing: Scheduling and posting content to channels
        - engagement: Community management and response
        - research: Market research or competitive analysis
        - analytics_review: Reviewing performance metrics
        - other: Miscellaneous tasks

    Status Workflow:
        pending → in_progress → completed
                ↓
              blocked (if dependencies not met)
                ↓
              cancelled (if no longer needed)

    Attributes:
        id: Unique task identifier
        move_id: Parent campaign/move identifier
        sprint_id: Parent sprint identifier (if sprint-based execution)
        title: Short task title
        description: Detailed task description
        task_type: Type of task (content_creation, publishing, etc.)
        status: Current status (pending, in_progress, completed, blocked, cancelled)
        priority: Task priority (high, medium, low)
        assigned_to: User or agent assigned to this task
        due_date: Target completion date
        estimated_hours: Estimated effort in hours
        completed_at: Actual completion timestamp
        dependencies: Task IDs that must complete before this task can start
        metadata: Additional task-specific metadata
        created_at: Timestamp when task was created
    """

    id: Optional[UUID] = Field(
        None,
        description="Unique task identifier",
    )
    move_id: UUID = Field(
        ...,
        description="Parent campaign/move identifier",
    )
    sprint_id: Optional[UUID] = Field(
        None,
        description="Parent sprint identifier (if applicable)",
    )
    title: str = Field(
        ...,
        description="Short, descriptive task title",
        min_length=1,
    )
    description: Optional[str] = Field(
        None,
        description="Detailed task description and acceptance criteria",
    )
    task_type: Literal[
        "content_creation",
        "publishing",
        "engagement",
        "research",
        "analytics_review",
        "other"
    ] = Field(
        default="other",
        description="Type of task for categorization and routing",
    )
    status: Literal["pending", "in_progress", "completed", "blocked", "cancelled"] = Field(
        default="pending",
        description="Current task status in workflow",
    )
    priority: Literal["high", "medium", "low"] = Field(
        default="medium",
        description="Task priority for resource allocation",
    )
    assigned_to: Optional[str] = Field(
        None,
        description="User or agent assigned to this task",
    )
    due_date: Optional[date] = Field(
        None,
        description="Target completion date",
    )
    estimated_hours: Optional[float] = Field(
        None,
        description="Estimated effort in hours",
        gt=0,
    )
    completed_at: Optional[datetime] = Field(
        None,
        description="Actual completion timestamp",
    )
    dependencies: List[UUID] = Field(
        default_factory=list,
        description="Task IDs that must complete before this task can start",
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional task-specific metadata",
    )
    created_at: Optional[datetime] = Field(
        None,
        description="Timestamp when task was created",
    )


class ChecklistItem(BaseModel):
    """A single checklist item for daily/weekly execution."""
    id: Optional[UUID] = None
    task_id: Optional[UUID] = None
    text: str
    completed: bool = Field(default=False)
    completed_at: Optional[datetime] = None
    order: int = Field(default=0)


class Sprint(BaseModel):
    """A sprint (1-2 week execution period) within a move."""
    id: Optional[UUID] = None
    move_id: UUID
    name: str
    start_date: date
    end_date: date
    goal: Optional[str] = Field(None, description="Sprint-specific goal")
    status: Literal["planned", "active", "completed", "paused"] = Field(default="planned")
    tasks: List[Task] = Field(default_factory=list)
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Sprint performance metrics")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class LineOfOperation(BaseModel):
    """
    A line of operation (LOO) represents a thematic stream of work within a campaign.
    Examples: "Thought Leadership", "Lead Generation", "Community Building"
    """
    id: Optional[UUID] = None
    move_id: UUID
    name: str
    description: Optional[str] = None
    channels: List[str] = Field(default_factory=list, description="Channels used for this LOO")
    cohort_ids: List[UUID] = Field(default_factory=list, description="Target cohorts for this LOO")
    weight: float = Field(default=1.0, ge=0.0, le=1.0, description="Percentage of effort allocated")
    created_at: Optional[datetime] = None


class AssetRequirement(BaseModel):
    """Required asset for campaign execution."""
    asset_type: Literal[
        "blog_post", 
        "email", 
        "social_post", 
        "video", 
        "infographic", 
        "carousel", 
        "meme",
        "landing_page",
        "ebook",
        "webinar",
        "case_study",
        "other"
    ]
    quantity: int = Field(default=1)
    specifications: Dict[str, Any] = Field(default_factory=dict, description="Format, length, etc.")
    assigned_cohort_ids: List[UUID] = Field(default_factory=list)
    due_date: Optional[date] = None


class MoveRequest(BaseModel):
    """Request to create a new campaign (move)."""
    workspace_id: UUID
    name: str
    goal: str
    timeframe_days: int = Field(ge=7, le=365, description="Campaign duration in days")
    target_cohort_ids: List[UUID] = Field(..., min_items=1, description="At least one target cohort required")
    channels: List[str] = Field(..., min_items=1, description="Marketing channels to use")
    constraints: Optional[Dict[str, Any]] = None
    budget: Optional[str] = None
    maneuver_type_id: Optional[UUID] = None  # Links to maneuver_types table
    
    class Config:
        json_schema_extra = {
            "example": {
                "workspace_id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "Q2 Demand Gen Sprint",
                "goal": "Generate 100 qualified leads from enterprise segment",
                "timeframe_days": 90,
                "target_cohort_ids": ["650e8400-e29b-41d4-a716-446655440000"],
                "channels": ["linkedin", "email", "blog"],
                "budget": "$10,000"
            }
        }


class MoveMetrics(BaseModel):
    """Real-time campaign performance metrics."""
    impressions: int = Field(default=0)
    engagements: int = Field(default=0)
    clicks: int = Field(default=0)
    leads: int = Field(default=0)
    conversions: int = Field(default=0)
    revenue: float = Field(default=0.0)
    engagement_rate: float = Field(default=0.0)
    conversion_rate: float = Field(default=0.0)
    cost_per_lead: Optional[float] = None
    roi: Optional[float] = None
    top_performing_content: List[str] = Field(default_factory=list)
    underperforming_channels: List[str] = Field(default_factory=list)


class MoveResponse(BaseModel):
    """Response containing a created/retrieved campaign."""
    move_id: UUID
    name: str
    goal: str
    status: Literal["planning", "active", "paused", "completed", "archived"] = Field(default="planning")
    start_date: date
    end_date: date
    target_cohort_ids: List[UUID]
    channels: List[str]
    
    # Execution plan
    sprints: List[Sprint] = Field(default_factory=list)
    lines_of_operation: List[LineOfOperation] = Field(default_factory=list)
    required_assets: List[AssetRequirement] = Field(default_factory=list)
    timeline: List[Task] = Field(default_factory=list, description="All tasks across sprints")
    daily_checklist: List[ChecklistItem] = Field(default_factory=list, description="Today's actionable items")
    
    # Performance
    metrics: MoveMetrics = Field(default_factory=MoveMetrics)
    
    # Metadata
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "move_id": "750e8400-e29b-41d4-a716-446655440000",
                "name": "Q2 Demand Gen Sprint",
                "goal": "Generate 100 qualified leads",
                "status": "active",
                "start_date": "2024-04-01",
                "end_date": "2024-06-30",
                "target_cohort_ids": ["650e8400-e29b-41d4-a716-446655440000"],
                "channels": ["linkedin", "email", "blog"],
                "sprints": [],
                "metrics": {
                    "impressions": 15000,
                    "leads": 23,
                    "engagement_rate": 0.045
                },
                "created_at": "2024-04-01T00:00:00Z"
            }
        }


class TaskUpdateRequest(BaseModel):
    """Request to update a task's status."""
    status: Literal["pending", "in_progress", "completed", "blocked", "cancelled"]
    notes: Optional[str] = None
    completed_at: Optional[datetime] = None


class MoveDecision(BaseModel):
    """A strategic decision or pivot made during campaign execution."""
    id: Optional[UUID] = None
    move_id: UUID
    decision_type: Literal["pivot", "double_down", "pause", "scale", "adjust_targeting", "other"]
    rationale: str
    actions_taken: List[str] = Field(default_factory=list)
    expected_impact: Optional[str] = None
    actual_impact: Optional[str] = None
    decided_at: datetime = Field(default_factory=datetime.utcnow)
    decided_by: Optional[str] = None


class MoveAnomaly(BaseModel):
    """An AI-detected anomaly or issue in campaign performance."""
    id: Optional[UUID] = None
    move_id: UUID
    anomaly_type: Literal["performance_drop", "unexpected_spike", "channel_failure", "budget_overrun", "other"]
    severity: Literal["low", "medium", "high", "critical"]
    description: str
    suggested_actions: List[str] = Field(default_factory=list)
    detected_at: datetime = Field(default_factory=datetime.utcnow)
    resolved: bool = Field(default=False)
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None

