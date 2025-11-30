"""
Campaign and Move models.
"""

from typing import List, Optional, Dict, Any, Literal
from uuid import UUID
from datetime import date, datetime
from enum import Enum
from pydantic import BaseModel, Field, validator

# --- Enums ---

class ObjectiveType(str, Enum):
    AWARENESS = "awareness"
    CONSIDERATION = "consideration"
    CONVERSION = "conversion"
    RETENTION = "retention"
    ADVOCACY = "advocacy"

class MoveType(str, Enum):
    AUTHORITY = "authority"
    CONSIDERATION = "consideration"
    OBJECTION = "objection"
    CONVERSION = "conversion"
    RETENTION = "retention"
    LAUNCH = "launch"
    NURTURE = "nurture"
    CUSTOM = "custom"

class ChannelRole(str, Enum):
    REACH = "reach"
    ENGAGE = "engage"
    CONVERT = "convert"
    RETAIN = "retain"

class MoveStatus(str, Enum):
    PLANNED = "planned"
    PREFLIGHT_FAILED = "preflight_failed"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class AssetStatus(str, Enum):
    DRAFT = "draft"
    GENERATING = "generating"
    READY = "ready"
    PUBLISHED = "published"
    ERROR = "error"

# --- Positioning & Messaging (Partial models for linkage) ---

class PositioningSummary(BaseModel):
    id: UUID
    name: str
    market_segment: str
    problem_statement: Optional[str] = None
    primary_claim: Optional[str] = None # from message_architecture

# --- Campaign Models ---

class CampaignChannel(BaseModel):
    channel: str
    role: ChannelRole
    budget_allocation: Optional[float] = None

class CampaignCohortTarget(BaseModel):
    cohort_id: UUID
    journey_stage_target: str # Where we want them to end up
    priority: int = 1

class CampaignBase(BaseModel):
    name: str
    description: Optional[str] = None
    objective: str
    objective_type: ObjectiveType
    target_metric: Optional[str] = None
    target_value: Optional[float] = None
    budget: Optional[float] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    positioning_id: Optional[UUID] = None

class CampaignCreate(CampaignBase):
    cohorts: List[CampaignCohortTarget] = []
    channels: List[CampaignChannel] = []

class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    objective: Optional[str] = None
    status: Optional[str] = None
    target_value: Optional[float] = None
    # Add other fields as needed

class Campaign(CampaignBase):
    id: UUID
    workspace_id: UUID
    status: str
    created_at: datetime
    updated_at: datetime
    
    # Relationships (optional, fetched if needed)
    cohorts: Optional[List[CampaignCohortTarget]] = None
    channels: Optional[List[CampaignChannel]] = None

# --- Move Models ---

class MoveBase(BaseModel):
    name: str
    move_type: MoveType
    cohort_id: Optional[UUID] = None
    journey_stage_from: Optional[str] = None
    journey_stage_to: Optional[str] = None
    message_variant_id: Optional[UUID] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    success_metric: Optional[str] = None
    success_target: Optional[float] = None

class MoveCreate(MoveBase):
    campaign_id: UUID

MoveRequest = MoveCreate

class MoveUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[MoveStatus] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    success_target: Optional[float] = None

class Move(MoveBase):
    id: UUID
    workspace_id: UUID
    campaign_id: UUID
    status: MoveStatus
    created_at: datetime
    updated_at: datetime

# --- Asset Models ---

class CreativeBrief(BaseModel):
    single_minded_proposition: str
    target_cohort_slice: Optional[str] = None
    objection_to_handle: Optional[str] = None
    tone: Optional[str] = None
    mandatories: Optional[List[str]] = None
    founder_override: Optional[str] = None

class AssetBase(BaseModel):
    name: Optional[str] = None
    format: str
    channel: str
    single_minded_proposition: Optional[str] = None
    creative_brief: Optional[CreativeBrief] = None

class AssetCreate(AssetBase):
    move_id: UUID

class Asset(AssetBase):
    id: UUID
    workspace_id: UUID
    move_id: UUID
    status: AssetStatus
    external_url: Optional[str] = None
    performance_metrics: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime

# --- Agent Exchange Models ---

class MovePlanSkeleton(BaseModel):
    """Output from CampaignPlanner agent"""
    name: str
    move_type: MoveType
    journey_stage_from: str
    journey_stage_to: str
    cohort_id: Optional[UUID]
    channels: List[str]
    duration_weeks: int
    focus_message: Optional[str] = None

class PreflightIssue(BaseModel):
    code: str
    message: str
    severity: Literal["warn", "fail"]
    recommendation: Optional[str] = None

class PreflightResult(BaseModel):
    status: Literal["pass", "warn", "fail"]
    issues: List[PreflightIssue] = []

# --- Aliases for backward compatibility ---
MoveRequest = MoveCreate
MoveResponse = Move

# --- Missing Models (Restored/Stubbed) ---
class MoveMetrics(BaseModel):
    pass
class Task(BaseModel):
    pass
class Sprint(BaseModel):
    pass
class LineOfOperation(BaseModel):
    pass
class AssetRequirement(BaseModel):
    pass
class ChecklistItem(BaseModel):
    pass
class TaskUpdateRequest(BaseModel):
    pass
class MoveDecision(BaseModel):
    pass
class MoveAnomaly(BaseModel):
    pass
