"""
Pydantic models for Campaigns (Moves, Sprints, Tasks).
These models define the structure for campaign planning and execution.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Literal, Any
from uuid import UUID
from datetime import datetime, date


class Task(BaseModel):
    """A single task within a campaign."""
    id: Optional[UUID] = None
    move_id: UUID
    sprint_id: Optional[UUID] = None
    title: str
    description: Optional[str] = None
    task_type: Literal[
        "content_creation", 
        "publishing", 
        "engagement", 
        "research", 
        "analytics_review", 
        "other"
    ] = Field(default="other")
    status: Literal["pending", "in_progress", "completed", "blocked", "cancelled"] = Field(default="pending")
    priority: Literal["high", "medium", "low"] = Field(default="medium")
    assigned_to: Optional[str] = None
    due_date: Optional[date] = None
    estimated_hours: Optional[float] = None
    completed_at: Optional[datetime] = None
    dependencies: List[UUID] = Field(default_factory=list, description="Task IDs that must complete first")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = None


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

