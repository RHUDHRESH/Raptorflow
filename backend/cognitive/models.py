"""
Cognitive Engine Data Models

Defines the core data structures used throughout the cognitive processing pipeline.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union


class IntentType(Enum):
    """Types of user intents."""

    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    ANALYZE = "analyze"
    GENERATE = "generate"
    RESEARCH = "research"
    APPROVE = "approve"
    CLARIFY = "clarify"


class EntityType(Enum):
    """Types of entities that can be extracted."""

    PERSON = "person"
    COMPANY = "company"
    PRODUCT = "product"
    LOCATION = "location"
    DATE = "date"
    MONEY = "money"
    PERCENTAGE = "percentage"


class Sentiment(Enum):
    """Sentiment classifications."""

    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"


class RiskLevel(Enum):
    """Risk levels for plans and actions."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Entity:
    """Extracted entity with confidence."""

    text: str
    type: EntityType
    confidence: float
    start_pos: int
    end_pos: int
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DetectedIntent:
    """Detected user intent."""

    intent_type: IntentType
    confidence: float
    sub_intents: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    reasoning: str = ""


@dataclass
class SentimentResult:
    """Sentiment analysis result."""

    sentiment: Sentiment
    confidence: float
    emotional_signals: List[str] = field(default_factory=dict)


@dataclass
class UrgencyResult:
    """Urgency classification result."""

    level: int  # 1-5 scale
    signals: List[str] = field(default_factory=list)
    deadline_mentioned: Optional[datetime] = None
    reasoning: str = ""


@dataclass
class ContextSignals:
    """Context signals from conversation history."""

    topic_continuity: bool
    reference_to_prior: List[str] = field(default_factory=list)
    new_topic: bool = False
    implicit_assumptions: List[str] = field(default_factory=list)


@dataclass
class PerceivedInput:
    """Complete perception of user input."""

    raw_text: str
    entities: List[Entity]
    intent: DetectedIntent
    sentiment: SentimentResult
    urgency: UrgencyResult
    context_signals: ContextSignals
    timestamp: datetime = field(default_factory=datetime.now)
    preprocessing_applied: List[str] = field(default_factory=list)


@dataclass
class PlanStep:
    """Individual step in an execution plan."""

    id: str
    description: str
    agent: str
    tools: List[str] = field(default_factory=list)
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)  # step ids
    estimated_tokens: int = 0
    estimated_cost: float = 0.0
    estimated_time_seconds: int = 0
    risk_level: RiskLevel = RiskLevel.LOW


@dataclass
class CostEstimate:
    """Cost estimation for a plan."""

    total_tokens: int
    total_cost_usd: float
    total_time_seconds: int
    breakdown_by_agent: Dict[str, float] = field(default_factory=dict)
    breakdown_by_step: Dict[str, float] = field(default_factory=dict)


@dataclass
class RiskAssessment:
    """Risk assessment for a plan."""

    level: RiskLevel
    factors: List[str] = field(default_factory=list)
    mitigations: List[str] = field(default_factory=list)
    probability_of_failure: float = 0.0
    impact_of_failure: str = ""


@dataclass
class ExecutionPlan:
    """Complete execution plan."""

    goal: str
    steps: List[PlanStep]
    total_cost: CostEstimate
    total_time_seconds: int
    risk_level: RiskLevel
    requires_approval: bool = False
    approval_reason: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Issue:
    """Issue found during reflection."""

    severity: str  # "low", "medium", "high", "critical"
    dimension: str
    description: str
    location: str  # where in the output
    suggestion: str
    confidence: float


@dataclass
class QualityScore:
    """Quality assessment result."""

    overall: int  # 0-100
    dimensions: Dict[str, int] = field(default_factory=dict)
    issues: List[Issue] = field(default_factory=list)
    passed: bool = False
    threshold: int = 70


@dataclass
class ReflectionResult:
    """Result of reflection process."""

    quality_score: QualityScore
    initial_output: str
    final_output: str
    iterations: int
    corrections_made: List[str] = field(default_factory=list)
    approved: bool = False
    requires_human_approval: bool = False
    approval_reason: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class CognitiveResult:
    """Complete result of cognitive processing."""

    perceived_input: PerceivedInput
    execution_plan: Optional[ExecutionPlan]
    reflection_result: Optional[ReflectionResult]
    success: bool
    error: Optional[str] = None
    total_tokens_used: int = 0
    total_cost_usd: float = 0.0
    processing_time_seconds: float = 0.0
    requires_approval: bool = False
    approval_gate_id: Optional[str] = None
    trace_id: str = ""
