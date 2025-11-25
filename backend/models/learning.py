"""
Self-Improving Loops Models

Pydantic models for agent recommendations, patterns, trust scoring,
and meta-learning state.
"""

from typing import Dict, List, Any, Optional, Literal
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


# ============================================================================
# ENUMS
# ============================================================================

class RecommendationStatus(str, Enum):
    """Status of a recommendation"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    PARTIAL = "partial"
    IMPLEMENTED = "implemented"


class RecommendationType(str, Enum):
    """Types of recommendations agents make"""
    STRATEGY = "strategy"
    CONTENT = "content"
    CREATIVE = "creative"
    SAFETY = "safety"
    OPTIMIZATION = "optimization"
    RISK = "risk"
    POLICY = "policy"


class TrustTrend(str, Enum):
    """Trust score trend direction"""
    IMPROVING = "improving"
    STABLE = "stable"
    DECLINING = "declining"


class PatternCategory(str, Enum):
    """Categories of discovered patterns"""
    HIGH_CONFIDENCE = "high_confidence"
    CONSENSUS = "consensus"
    EXPERT_OPINION = "expert_opinion"
    FAILURE_AVOIDANCE = "failure_avoidance"
    SUCCESS_INDICATOR = "success_indicator"
    CONTEXTUAL = "contextual"


class RecommendationStrength(str, Enum):
    """Strength of a pattern recommendation"""
    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"
    VERY_STRONG = "very_strong"


# ============================================================================
# RECOMMENDATION MODELS
# ============================================================================

class AgentRecommendation(BaseModel):
    """A single recommendation made by an agent"""

    id: Optional[str] = None
    workspace_id: str

    # Agent and Context
    agent_id: str
    agent_name: str
    correlation_id: str
    workflow_id: str

    # Recommendation Details
    recommendation_type: RecommendationType
    recommendation_content: Dict[str, Any]
    confidence_score: float = Field(ge=0.0, le=1.0, default=0.5)

    # Supporting Reasoning
    reasoning: Optional[str] = None
    evidence: Optional[Dict[str, Any]] = None

    # Outcome Tracking
    outcome_status: Optional[RecommendationStatus] = None
    outcome_quality_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    outcome_notes: Optional[str] = None

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    evaluated_at: Optional[datetime] = None

    class Config:
        use_enum_values = True


class RecommendationOutcome(BaseModel):
    """Evaluation of a recommendation's outcome"""

    id: Optional[str] = None
    workspace_id: str
    recommendation_id: str
    agent_id: str

    # Quality Assessment
    quality_dimensions: Dict[str, str]  # {relevance, accuracy, timing, creativity, compliance}
    quality_scores: Dict[str, float]  # Scores for each dimension (0-100)
    overall_quality_score: float = Field(ge=0.0, le=100.0)

    # Comparative Assessment
    compared_against: Optional[int] = None
    ranked_position: Optional[int] = None
    outperformed_count: int = 0

    # Human Feedback
    evaluator_feedback: Optional[str] = None
    evaluator_id: Optional[str] = None

    # Temporal Context
    evaluation_date: datetime = Field(default_factory=datetime.utcnow)
    impact_observed_date: Optional[datetime] = None
    impact_duration_days: Optional[int] = None

    class Config:
        use_enum_values = True


# ============================================================================
# PATTERN MODELS
# ============================================================================

class PatternCondition(BaseModel):
    """A condition in a recommendation pattern"""

    field: str  # e.g., "agent_confidence", "agent_type", "workflow_stage"
    operator: Literal["equals", "gt", "lt", "gte", "lte", "in", "contains"]
    value: Any


class PatternAction(BaseModel):
    """Recommended action when pattern is detected"""

    action: str  # e.g., "prioritize", "veto", "escalate", "boost_confidence"
    confidence_modifier: float = 0.0  # How much to modify confidence
    reasoning: Optional[str] = None


class RecommendationPattern(BaseModel):
    """A pattern discovered in successful recommendations"""

    id: Optional[str] = None
    workspace_id: str

    # Pattern Identification
    pattern_name: str
    pattern_category: PatternCategory
    agent_ids: List[str]

    # Pattern Specification
    pattern_definition: Dict[str, Any]  # IF conditions, THEN action
    conditions: List[PatternCondition] = []
    action: Optional[PatternAction] = None

    # Pattern Statistics
    success_rate: float = Field(ge=0.0, le=1.0, default=0.0)
    frequency_count: int = 0
    confidence_level: float = Field(ge=0.0, le=1.0, default=0.0)
    recommendation_strength: RecommendationStrength = RecommendationStrength.WEAK

    # Timestamps
    discovered_at: datetime = Field(default_factory=datetime.utcnow)
    last_confirmed_at: Optional[datetime] = None
    next_review_at: Optional[datetime] = None

    class Config:
        use_enum_values = True


# ============================================================================
# TRUST SCORING MODELS
# ============================================================================

class AgentTrustScores(BaseModel):
    """Trust metrics for an agent"""

    id: Optional[str] = None
    workspace_id: str

    # Agent Reference
    agent_id: str
    agent_name: str

    # Trust Metrics (0-1)
    overall_trust_score: float = Field(default=0.5, ge=0.0, le=1.0)
    accuracy_score: float = Field(default=0.5, ge=0.0, le=1.0)
    consistency_score: float = Field(default=0.5, ge=0.0, le=1.0)
    timeliness_score: float = Field(default=0.5, ge=0.0, le=1.0)
    reliability_score: float = Field(default=0.5, ge=0.0, le=1.0)

    # Performance Metrics
    total_recommendations: int = 0
    approved_recommendations: int = 0
    rejected_recommendations: int = 0
    partial_recommendations: int = 0

    approval_rate: float = Field(default=0.0, ge=0.0, le=1.0)
    avg_quality_score: float = Field(default=0.0, ge=0.0, le=100.0)

    # Trend Analysis
    trust_trend: TrustTrend = TrustTrend.STABLE
    improvement_rate: float = 0.0  # Trust change per week

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_evaluated_at: Optional[datetime] = None

    class Config:
        use_enum_values = True


class TrustScoreUpdate(BaseModel):
    """Update to trust scores based on recommendation outcome"""

    agent_id: str
    recommendation_id: str
    outcome_quality_score: float = Field(ge=0.0, le=100.0)

    # Impact on different dimensions
    accuracy_impact: float = Field(default=0.0, ge=-1.0, le=1.0)
    consistency_impact: float = Field(default=0.0, ge=-1.0, le=1.0)
    timeliness_impact: float = Field(default=0.0, ge=-1.0, le=1.0)
    reliability_impact: float = Field(default=0.0, ge=-1.0, le=1.0)


# ============================================================================
# META-LEARNER MODELS
# ============================================================================

class AgentProfile(BaseModel):
    """Profile of an agent's strengths and weaknesses"""

    agent_id: str
    agent_name: str

    # Capability Assessment
    strong_areas: List[str]  # What this agent excels at
    weak_areas: List[str]  # Where this agent struggles
    learning_curve: str = "steady"  # improving, steady, declining

    # Specialization
    specialization_score: Dict[str, float]  # {recommendation_type: score}

    # Collaboration Profile
    works_well_with: List[str]  # Agent IDs
    conflicts_with: List[str]  # Agent IDs
    consensus_builder: bool = False


class DecisionRule(BaseModel):
    """Rule for agent selection based on context"""

    rule_id: str
    rule_name: str
    description: Optional[str] = None

    # Conditions
    conditions: List[PatternCondition]

    # Actions
    preferred_agents: List[str]  # Which agents to prefer
    avoid_agents: List[str] = []
    confidence_boost: float = 0.0

    # Rule effectiveness
    application_count: int = 0
    success_rate: float = 0.0


class MetaLearnerState(BaseModel):
    """State of the meta-learning agent"""

    id: Optional[str] = None
    workspace_id: str

    # Learner Configuration
    learner_version: str = "1.0"
    learning_rate: float = Field(default=0.1, ge=0.0, le=1.0)
    pattern_confidence_threshold: float = Field(default=0.7, ge=0.0, le=1.0)

    # Learned Knowledge
    learned_patterns: List[RecommendationPattern] = []
    agent_profiles: Dict[str, AgentProfile] = {}
    decision_rules: List[DecisionRule] = []

    # Learning Progress
    samples_processed: int = 0
    last_learning_iteration_at: Optional[datetime] = None
    next_learning_iteration_at: Optional[datetime] = None
    learning_cycles_completed: int = 0

    # Model Performance
    model_accuracy: float = Field(default=0.0, ge=0.0, le=1.0)
    model_coverage: float = Field(default=0.0, ge=0.0, le=1.0)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = True


class LearningIteration(BaseModel):
    """A single learning iteration of the meta-learner"""

    iteration_id: str
    workspace_id: str

    # Iteration Parameters
    samples_analyzed: int
    patterns_discovered: int
    patterns_confirmed: int
    rules_updated: int

    # Quality Metrics
    iteration_accuracy: float
    pattern_confidence_improvement: float
    rule_effectiveness_improvement: float

    # Insights
    key_insights: List[str]
    recommendations_for_swarm: List[str]

    # Timestamps
    started_at: datetime
    completed_at: datetime
    processing_time_seconds: float


# ============================================================================
# ANALYSIS VIEWS
# ============================================================================

class AgentRecommendationAnalysis(BaseModel):
    """Analysis of an agent's recommendations"""

    agent_id: str
    agent_name: str
    total_recommendations: int
    approved_count: int
    rejected_count: int
    avg_confidence: float
    avg_quality: float
    last_recommendation_at: Optional[datetime] = None


class PatternEffectiveness(BaseModel):
    """Analysis of pattern effectiveness"""

    pattern_name: str
    pattern_category: PatternCategory
    success_rate: float
    frequency_count: int
    confidence_level: float
    participating_agents: int
    avg_pattern_quality: float


# ============================================================================
# API REQUEST/RESPONSE MODELS
# ============================================================================

class RecommendationTrackingRequest(BaseModel):
    """Request to track a recommendation"""

    agent_id: str
    recommendation_type: RecommendationType
    recommendation_content: Dict[str, Any]
    confidence_score: float = 0.5
    reasoning: Optional[str] = None
    evidence: Optional[Dict[str, Any]] = None


class OutcomeEvaluationRequest(BaseModel):
    """Request to evaluate a recommendation outcome"""

    recommendation_id: str
    quality_scores: Dict[str, float]  # {dimension: score}
    overall_quality_score: float
    evaluator_feedback: Optional[str] = None
    impact_observed_date: Optional[datetime] = None


class TrustScoreResponse(BaseModel):
    """Response with agent trust scores"""

    agent_id: str
    agent_name: str
    overall_trust_score: float
    accuracy_score: float
    consistency_score: float
    approval_rate: float
    avg_quality_score: float
    trend: TrustTrend
    recommendation_strength: RecommendationStrength


class LearningInsightResponse(BaseModel):
    """Response with meta-learner insights"""

    iteration_id: str
    patterns_discovered: int
    key_insights: List[str]
    agent_recommendations: Dict[str, str]  # agent_id -> recommendation
    next_learning_at: datetime
