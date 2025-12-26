import operator
from datetime import datetime
from enum import Enum
from typing import Annotated, Any, Dict, List, Optional

from pydantic import BaseModel, Field

from models.cognitive import CognitiveIntelligenceState
from models.queue_controller import CapabilityProfile, QueueController

__all__ = [
    "SwarmSubtaskSpec",
    "SwarmTask",
    "SwarmTaskStatus",
    "SwarmState",
    "CompetitorProfile",
    "CompetitorGroup",
    "CompetitorInsight",
    "CompetitorAnalysis",
    "CompetitorType",
    "CompetitorThreatLevel",
]


class SwarmTaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class CompetitorType(str, Enum):
    DIRECT = "direct"
    INDIRECT = "indirect"
    EMERGING = "emerging"
    MARKET_LEADER = "market_leader"
    NICHE_PLAYER = "niche_player"


class CompetitorThreatLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CompetitorProfile(BaseModel):
    """Enhanced competitor profile for swarm intelligence."""
    
    id: str
    name: str
    competitor_type: CompetitorType
    threat_level: CompetitorThreatLevel
    website: Optional[str] = None
    description: Optional[str] = None
    
    # Market positioning
    market_share: Optional[float] = None
    target_audience: List[str] = Field(default_factory=list)
    value_proposition: Optional[str] = None
    
    # Product/service analysis
    key_features: List[str] = Field(default_factory=list)
    pricing_model: Optional[str] = None
    pricing_tiers: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Marketing intelligence
    messaging_strategy: Optional[str] = None
    marketing_channels: List[str] = Field(default_factory=list)
    content_themes: List[str] = Field(default_factory=list)
    brand_voice: Optional[str] = None
    
    # Technical intelligence
    tech_stack: List[str] = Field(default_factory=list)
    apis_offered: List[str] = Field(default_factory=list)
    integrations: List[str] = Field(default_factory=list)
    
    # Competitive advantages
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    opportunities: List[str] = Field(default_factory=list)
    threats: List[str] = Field(default_factory=list)
    
    # Tracking metadata
    last_updated: datetime = Field(default_factory=datetime.now)
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    data_sources: List[str] = Field(default_factory=list)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class CompetitorGroup(BaseModel):
    """Represents a group of similar competitors for analysis."""
    
    id: str
    name: str
    description: str
    competitor_ids: List[str] = Field(default_factory=list)
    common_characteristics: List[str] = Field(default_factory=list)
    market_segment: Optional[str] = None
    analysis_summary: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class CompetitorInsight(BaseModel):
    """Individual insight about a competitor."""
    
    id: str
    competitor_id: str
    insight_type: str  # "pricing_change", "feature_launch", "marketing_campaign", etc.
    title: str
    description: str
    impact_assessment: str  # "low", "medium", "high"
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    source: str
    discovered_at: datetime = Field(default_factory=datetime.now)
    tags: List[str] = Field(default_factory=list)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class CompetitorAnalysis(BaseModel):
    """Comprehensive competitor analysis result."""
    
    id: str
    analysis_type: str  # "swot", "pricing", "feature_comparison", etc.
    competitor_ids: List[str] = Field(default_factory=list)
    summary: str
    key_findings: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    competitive_gaps: List[str] = Field(default_factory=list)
    market_opportunities: List[str] = Field(default_factory=list)
    threat_level: CompetitorThreatLevel
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    analyzed_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SwarmSubtaskSpec(BaseModel):
    """Structured specification for a swarm subtask."""

    id: str
    specialist_type: str
    objective: str
    success_criteria: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    inputs: Dict[str, Any] = Field(default_factory=dict)
    competitor_focus: Optional[str] = None  # Optional competitor ID to focus on


class SwarmTask(BaseModel):
    """Represents a sub-task delegated to a swarm specialist."""

    id: str
    specialist_type: str  # researcher, architect, critic, etc.
    description: str
    status: SwarmTaskStatus = SwarmTaskStatus.PENDING
    result: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    competitor_targets: List[str] = Field(default_factory=list)  # Competitor IDs targeted


class SwarmState(CognitiveIntelligenceState, total=False):
    """
    SOTA Swarm Intelligence State.
    Extends the base cognitive state with multi-agent coordination fields.
    """

    subtask_specs: Annotated[List[SwarmSubtaskSpec], operator.add]

    # List of delegated sub-tasks
    swarm_tasks: Annotated[List[SwarmTask], operator.add]

    # Shared pool of knowledge discovered during the run
    shared_knowledge: Annotated[Dict[str, Any], dict]

    # History of delegations and specialist interactions
    delegation_history: Annotated[List[Dict[str, Any]], operator.add]

    # Concurrency management
    capability_profile: CapabilityProfile
    queue_controller: QueueController
    
    # Competitor intelligence tracking
    competitor_profiles: Annotated[Dict[str, CompetitorProfile], dict]
    competitor_groups: Annotated[Dict[str, CompetitorGroup], dict]
    competitor_insights: Annotated[List[CompetitorInsight], operator.add]
    competitor_analyses: Annotated[List[CompetitorAnalysis], operator.add]
    
    # Competitor monitoring configuration
    active_competitor_watchlist: Annotated[List[str], operator.add]
    competitor_monitoring_frequency: int = Field(default=24)  # hours
    last_competitor_scan: Optional[datetime] = None
    
    # Competitive intelligence context
    competitive_landscape_summary: Optional[str] = None
    market_positioning_analysis: Optional[str] = None
    competitive_advantages: List[str] = Field(default_factory=list)
    competitive_threats: List[str] = Field(default_factory=list)
