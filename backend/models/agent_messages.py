"""
Agent Message Models for Swarm Communication

These models define the structure of all messages exchanged between agents.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Literal, Optional
from datetime import datetime
from enum import Enum


# ============================================================================
# GOAL & STRATEGY MESSAGES
# ============================================================================

class GoalRequest(BaseModel):
    """Goal request from user or system"""

    goal_type: Literal[
        "reach",
        "engagement",
        "conversion",
        "revenue",
        "retention",
        "authority",
        "insight"
    ]
    description: str
    cohorts: List[str] = []  # cohort_ids
    timeframe_days: int = 14
    intensity: Literal["light", "standard", "aggressive"] = "standard"
    constraints: Dict[str, Any] = {}
    budget_constraint: Optional[float] = None


class MovePlan(BaseModel):
    """Campaign move plan from Strategy sector"""

    move_id: str
    name: str
    objective: str
    target_cohorts: List[str]
    channels: List[str]  # ["linkedin", "email", "twitter"]
    kpi_primary: str  # "conversions", "reach", "engagement"
    kpi_target: float
    start_date: datetime
    end_date: datetime
    content_needs: List[Dict[str, Any]]
    cadence: Dict[str, int] = {}  # {"linkedin": 3, "email": 2}
    messaging_theme: str = ""
    created_by_agent: str = ""


# ============================================================================
# CONTENT CREATION MESSAGES
# ============================================================================

class ContentBrief(BaseModel):
    """Brief for content creation"""

    brief_id: str
    move_id: str
    cohort_id: str
    channel: str  # "linkedin", "email", "twitter"
    format: str  # "post", "carousel", "email", "blog"
    objective: str
    tone_tags: List[str] = []  # ["professional", "empathetic"]
    hook_type: Optional[str] = None  # "question", "proof", "pain", "urgency"
    hard_constraints: Dict[str, Any] = {}  # {"max_length": 280}
    context: Dict[str, Any] = {}  # market research, cohort psychographics


class SkeletonDesign(BaseModel):
    """Content structure/skeleton before copy"""

    brief_id: str
    skeleton: List[Dict[str, Any]]  # [{"role": "hook", "description": "..."}]
    estimated_reading_time_sec: int = 0
    estimated_engagement: str = ""  # "low", "medium", "high"


class DraftAsset(BaseModel):
    """Content draft from creation agents"""

    asset_id: str
    brief_id: str
    move_id: str
    channel: str
    format: str
    body: str
    media_urls: List[str] = []
    metadata: Dict[str, Any] = {}
    status: Literal["draft", "under_review", "approved", "rejected"] = "draft"
    created_by_agent: str
    quality_score: Optional[float] = None


class AssetVariant(BaseModel):
    """Content variant for A/B testing"""

    variant_id: str
    asset_id: str
    variant_type: str  # "a", "b", "c"
    variation: str  # What changed: "hook", "cta", "tone"
    body: str
    created_by_agent: str


# ============================================================================
# PERFORMANCE & METRICS MESSAGES
# ============================================================================

class PerformanceUpdate(BaseModel):
    """Performance metrics from platforms"""

    move_id: str
    asset_id: Optional[str]
    metrics: Dict[str, float]
    verdict: Literal["winner", "average", "dead"] = "average"
    patterns: List[str] = []
    confidence: float = 0.5
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class MoveMetrics(BaseModel):
    """Aggregated metrics for a move"""

    move_id: str
    total_impressions: int
    total_clicks: int
    total_conversions: int
    engagement_rate: float
    conversion_rate: float
    estimated_roi: float
    top_performing_assets: List[str]
    underperforming_assets: List[str]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# INTELLIGENCE & TREND MESSAGES
# ============================================================================

class TrendAlert(BaseModel):
    """Trend detected by PulseSeer"""

    trend_id: str
    topic: str
    platforms: List[str]
    velocity: float  # Growth rate
    lifecycle_stage: Literal["emerging", "peak", "declining"]
    relevant_cohorts: List[str]
    opportunity_score: float
    expiry_date: datetime
    first_seen: datetime = Field(default_factory=datetime.utcnow)


class PatternIdentified(BaseModel):
    """Content pattern identified by analytics"""

    pattern_id: str
    pattern_type: str  # "hook_type", "emotional_tone", "structure"
    pattern_name: str
    performing_assets: List[str]
    success_rate: float
    recommended_for_cohorts: List[str]
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CompetitorIntel(BaseModel):
    """Competitor analysis from MirrorScout"""

    competitor_id: str
    competitor_name: str
    content_patterns: List[str]
    primary_channels: List[str]
    posting_frequency: Dict[str, float]
    top_performing_hooks: List[str]
    estimated_strategy: str
    risk_level: Literal["low", "medium", "high"]


class CohortDrift(BaseModel):
    """Cohort behavioral drift alert"""

    cohort_id: str
    metric_name: str
    previous_value: float
    current_value: float
    change_percentage: float
    significance: Literal["low", "medium", "high"]
    recommended_action: str


# ============================================================================
# RISK & QUALITY MESSAGES
# ============================================================================

class RiskAlert(BaseModel):
    """Risk alert from FirewallMaven"""

    asset_id: str
    risk_type: Literal[
        "brand_misalignment",
        "legal",
        "toxicity",
        "backlash_potential",
        "quality_issue"
    ]
    severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    details: str
    recommended_action: Literal["approve", "revise", "reject", "escalate"]
    blocking: bool = False  # If True, blocks publishing


class ContentReview(BaseModel):
    """Content review request"""

    asset_id: str
    brief_id: str
    content: str
    review_type: Literal["brand_check", "quality", "compliance", "final"]


class ReviewComplete(BaseModel):
    """Review completion from Guardian agent"""

    asset_id: str
    review_type: str
    approved: bool
    issues: List[str] = []
    suggestions: List[str] = []
    reviewer_agent: str
    reviewed_at: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# EXPERIMENT MESSAGES
# ============================================================================

class ExperimentDesign(BaseModel):
    """A/B test design from SplitMind"""

    experiment_id: str
    move_id: str
    hypothesis: str
    variants: List[Dict[str, Any]]  # [{"variant": "A", "asset_id": "..."}, ...]
    sample_size_per_variant: int
    duration_days: int
    success_metric: str
    stop_conditions: Dict[str, Any]
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ExperimentResult(BaseModel):
    """Experiment results from SplitMind"""

    experiment_id: str
    winner_variant: str
    confidence: float
    winner_metric_value: float
    loser_metric_value: float
    estimated_lift: float
    statistical_significance: float
    completed_at: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# EXECUTION MESSAGES
# ============================================================================

class PublishRequest(BaseModel):
    """Request to publish content"""

    asset_id: str
    move_id: str
    channel: str
    scheduled_time: Optional[datetime] = None
    priority: Literal["LOW", "MEDIUM", "HIGH"] = "MEDIUM"


class PublishComplete(BaseModel):
    """Publication confirmation"""

    asset_id: str
    channel: str
    post_url: str
    published_at: datetime
    platform_id: str


# ============================================================================
# POLICY & CONSENSUS MESSAGES
# ============================================================================

class ConflictAlert(BaseModel):
    """Agent conflict detected"""

    conflict_id: str
    agents_involved: List[str]
    issue: str
    recommendations: Dict[str, Any]  # agent_id -> recommendation
    urgency: Literal["LOW", "MEDIUM", "HIGH"]


class PolicyDecision(BaseModel):
    """Decision from Policy Arbiter"""

    decision_id: str
    conflict_id: str
    agents_involved: List[str]
    decision: str  # "approve", "reject", "tweak", "escalate"
    reasoning: str
    overrides: Dict[str, Any] = {}  # Which agent's rec was chosen
    binding: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)


class DebateRequest(BaseModel):
    """Request for multi-agent debate"""

    debate_id: str
    topic: str
    question: str
    participants: List[str]
    context: Dict[str, Any]
    rounds: int = 2
    voting_threshold: float = 0.7


class DebateRound(BaseModel):
    """Single debate round"""

    debate_id: str
    round_number: int
    positions: Dict[str, Any]  # agent_id -> position


class DebateResult(BaseModel):
    """Final debate result"""

    debate_id: str
    decision: str
    confidence: float
    votes: Dict[str, str]  # agent_id -> vote
    reasoning: Dict[str, str]  # agent_id -> their reasoning
    consensus_reached: bool
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# SYSTEM MESSAGES
# ============================================================================

class AgentHeartbeat(BaseModel):
    """Agent heartbeat for health monitoring"""

    agent_id: str
    current_load: int
    status: Literal["healthy", "degraded", "unhealthy"]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class WorkflowStart(BaseModel):
    """Workflow initiation"""

    workflow_id: str
    correlation_id: str
    workflow_type: str
    initiator: str  # user_id or agent_id
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class WorkflowComplete(BaseModel):
    """Workflow completion"""

    workflow_id: str
    correlation_id: str
    status: Literal["success", "partial", "failed"]
    result: Dict[str, Any]
    duration_seconds: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AgentError(BaseModel):
    """Error from agent"""

    agent_id: str
    correlation_id: str
    error_type: str
    error_message: str
    stack_trace: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
