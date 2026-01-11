"""
Planning Module Data Models

Defines the core data structures for planning and execution.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from cognitive.models import RiskLevel


class TaskType(Enum):
    """Types of tasks that can be planned."""

    RESEARCH = "research"
    ANALYZE = "analyze"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    VALIDATE = "validate"
    APPROVE = "approve"
    NOTIFY = "notify"
    TRANSFORM = "transform"


class AgentType(Enum):
    """Types of agents that can execute tasks."""

    ONBOARDING = "onboarding"
    MOVES = "moves"
    CAMPAIGNS = "campaigns"
    MUSE = "muse"
    BLACKBOX = "blackbox"
    DAILY_WINS = "daily_wins"
    ANALYTICS = "analytics"
    FOUNDATION = "foundation"
    GENERAL = "general"


@dataclass
class SubTask:
    """A sub-task component of a larger goal."""

    id: str
    description: str
    task_type: TaskType
    agent: AgentType
    required_tools: List[str] = field(default_factory=list)
    input_data: Dict[str, Any] = field(default_factory=dict)
    expected_output: Dict[str, Any] = field(default_factory=dict)
    estimated_complexity: int = 1  # 1-10 scale
    priority: int = 5  # 1-10 scale


@dataclass
class PlanStep:
    """Individual step in an execution plan."""

    id: str
    description: str
    agent: AgentType
    tools: List[str] = field(default_factory=list)
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)  # step ids
    estimated_tokens: int = 0
    estimated_cost: float = 0.0
    estimated_time_seconds: int = 0
    risk_level: RiskLevel = RiskLevel.LOW
    retry_count: int = 0
    max_retries: int = 3
    timeout_seconds: int = 300
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CostEstimate:
    """Cost estimation for a plan."""

    total_tokens: int
    total_cost_usd: float
    total_time_seconds: int
    breakdown_by_agent: Dict[str, float] = field(default_factory=dict)
    breakdown_by_step: Dict[str, float] = field(default_factory=dict)
    breakdown_by_type: Dict[str, float] = field(default_factory=dict)
    confidence: float = 0.8  # Confidence in estimate


@dataclass
class RiskAssessment:
    """Risk assessment for a plan."""

    level: RiskLevel
    factors: List[str] = field(default_factory=list)
    mitigations: List[str] = field(default_factory=list)
    probability_of_failure: float = 0.0
    impact_of_failure: str = ""
    risk_score: float = 0.0  # 0-100 scale
    requires_approval: bool = False
    approval_reason: str = ""


@dataclass
class ValidationResult:
    """Result of plan validation."""

    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    validation_score: float = 0.0  # 0-100 scale


@dataclass
class ExecutionPlan:
    """Complete execution plan."""

    id: str
    goal: str
    description: str
    steps: List[PlanStep]
    cost_estimate: CostEstimate
    risk_assessment: RiskAssessment
    validation_result: Optional[ValidationResult] = None
    total_time_seconds: int = 0
    requires_approval: bool = False
    approval_reason: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Computed properties
    @property
    def total_steps(self) -> int:
        return len(self.steps)

    @property
    def parallel_steps(self) -> int:
        """Count steps that can run in parallel (no dependencies)."""
        return sum(1 for step in self.steps if not step.dependencies)

    @property
    def critical_path_steps(self) -> List[str]:
        """Steps on the critical path (must be executed sequentially)."""
        # Simplified critical path calculation
        critical = []
        for step in self.steps:
            if step.dependencies or any(
                step.id in other_step.dependencies for other_step in self.steps
            ):
                critical.append(step.id)
        return critical

    @property
    def total_cost(self) -> float:
        return self.cost_estimate.total_cost_usd

    @property
    def total_tokens(self) -> int:
        return self.cost_estimate.total_tokens


@dataclass
class PlanningContext:
    """Context information for planning."""

    workspace_id: str
    user_id: str
    foundation_data: Dict[str, Any] = field(default_factory=dict)
    icp_data: List[Dict[str, Any]] = field(default_factory=list)
    available_agents: List[AgentType] = field(default_factory=list)
    available_tools: List[str] = field(default_factory=list)
    budget_limit: float = 1.0
    time_limit_seconds: int = 3600
    risk_tolerance: RiskLevel = RiskLevel.MEDIUM
    preferences: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PlanningResult:
    """Result of planning process."""

    success: bool
    execution_plan: Optional[ExecutionPlan] = None
    sub_tasks: List[SubTask] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    processing_time_ms: int = 0
    tokens_used: int = 0
    cost_usd: float = 0.0


@dataclass
class PlanCheckpoint:
    """Checkpoint for plan execution progress."""

    id: str
    plan_id: str
    completed_steps: List[str]
    step_results: Dict[str, Any] = field(default_factory=dict)
    total_cost_sofar: float = 0.0
    tokens_used_sofar: int = 0
    time_elapsed_seconds: int = 0
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class PlanTemplate:
    """Template for common planning patterns."""

    id: str
    name: str
    description: str
    goal_pattern: str  # Regex pattern to match goals
    steps_template: List[Dict[str, Any]]  # Template steps
    default_agent: AgentType
    estimated_cost_range: tuple[float, float]  # min, max
    estimated_time_range: tuple[int, int]  # min, max seconds
    risk_level: RiskLevel = RiskLevel.LOW
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


# Utility functions for plan management
def create_plan_step(
    step_id: str,
    description: str,
    agent: AgentType,
    tools: List[str] = None,
    dependencies: List[str] = None,
    **kwargs,
) -> PlanStep:
    """Helper function to create a PlanStep with sensible defaults."""
    return PlanStep(
        id=step_id,
        description=description,
        agent=agent,
        tools=tools or [],
        dependencies=dependencies or [],
        **kwargs,
    )


def calculate_plan_metrics(plan: ExecutionPlan) -> Dict[str, Any]:
    """Calculate various metrics for a plan."""
    return {
        "total_steps": len(plan.steps),
        "parallel_steps": plan.parallel_steps,
        "critical_path_length": len(plan.critical_path_steps),
        "total_cost": plan.total_cost,
        "total_tokens": plan.total_tokens,
        "average_step_cost": plan.total_cost / len(plan.steps) if plan.steps else 0,
        "average_step_time": (
            plan.total_time_seconds / len(plan.steps) if plan.steps else 0
        ),
        "risk_score": plan.risk_assessment.risk_score,
        "validation_score": (
            plan.validation_result.validation_score if plan.validation_result else 0
        ),
    }


def validate_plan_structure(plan: ExecutionPlan) -> List[str]:
    """Validate the structure of a plan."""
    errors = []

    if not plan.steps:
        errors.append("Plan must have at least one step")

    # Check for duplicate step IDs
    step_ids = [step.id for step in plan.steps]
    if len(step_ids) != len(set(step_ids)):
        errors.append("Duplicate step IDs found")

    # Check for circular dependencies
    for step in plan.steps:
        if step.id in step.dependencies:
            errors.append(f"Step {step.id} has circular dependency on itself")

    # Check if all dependencies exist
    all_step_ids = set(step_ids)
    for step in plan.steps:
        for dep_id in step.dependencies:
            if dep_id not in all_step_ids:
                errors.append(f"Step {step.id} depends on non-existent step {dep_id}")

    return errors
