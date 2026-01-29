"""
Onboarding Business Context Schema
Pydantic validators for ensuring required sections before finalization
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, root_validator, validator


class BusinessContextSection(str, Enum):
    """Required business context sections"""

    FOUNDATION = "foundation"
    ICP = "icp"
    COMPETITIVE = "competitive"
    MESSAGING = "messaging"
    GO_TO_MARKET = "go_to_market"
    ANALYTICS = "analytics"
    IMPLEMENTATION = "implementation"


class OnboardingStatus(str, Enum):
    """Onboarding progress status"""

    PENDING = "pending"
    PAYMENT_CONFIRMED = "payment_confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class StepMetadata(BaseModel):
    """Metadata for individual onboarding steps"""

    step_id: int
    completed_at: Optional[datetime] = None
    data_hash: Optional[str] = None
    validation_warnings: List[str] = Field(default_factory=list)


class BusinessContextMetadata(BaseModel):
    """Metadata for business context"""

    version: str = "2.0"
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    session_id: str
    workspace_id: str
    user_id: Optional[str] = None
    total_steps: int = 23
    completed_steps: int
    completion_percentage: float
    steps: Dict[str, StepMetadata] = Field(default_factory=dict)

    @validator("completion_percentage")
    def validate_completion_percentage(cls, v):
        if not 0 <= v <= 100:
            raise ValueError("Completion percentage must be between 0 and 100")
        return v


class FoundationSection(BaseModel):
    """Foundation section validation"""

    company_name: Optional[str] = None
    industry: Optional[str] = None
    stage: Optional[str] = None
    description: Optional[str] = None
    value_proposition: Optional[str] = None
    problem_statement: Optional[str] = None
    solution: Optional[str] = None

    @validator("company_name")
    def validate_company_name(cls, v):
        if v and len(v.strip()) < 2:
            raise ValueError("Company name must be at least 2 characters")
        return v


class ICPSection(BaseModel):
    """ICP section validation"""

    icps: List[Dict[str, Any]] = Field(default_factory=list)
    pain_points: List[Dict[str, Any]] = Field(default_factory=list)
    goals: List[Dict[str, Any]] = Field(default_factory=list)
    trigger_events: List[Dict[str, Any]] = Field(default_factory=list)

    @validator("icps")
    def validate_icps(cls, v):
        if len(v) > 3:
            raise ValueError("Maximum 3 ICPs allowed")
        return v


class CompetitiveSection(BaseModel):
    """Competitive analysis section validation"""

    competitors: List[Dict[str, Any]] = Field(default_factory=list)
    positioning: Optional[Dict[str, Any]] = None
    market_landscape: Optional[Dict[str, Any]] = None


class MessagingSection(BaseModel):
    """Messaging section validation"""

    value_proposition: Optional[str] = None
    key_messages: List[Dict[str, Any]] = Field(default_factory=list)
    taglines: List[str] = Field(default_factory=list)
    soundbites: List[Dict[str, Any]] = Field(default_factory=list)
    brand_values: List[str] = Field(default_factory=list)


class GoToMarketSection(BaseModel):
    """Go-to-market section validation"""

    channels: List[Dict[str, Any]] = Field(default_factory=list)
    pricing_strategy: Optional[Dict[str, Any]] = None
    sales_strategy: Optional[Dict[str, Any]] = None
    content_strategy: Optional[Dict[str, Any]] = None


class AnalyticsSection(BaseModel):
    """Analytics section validation"""

    market_sizing: Optional[Dict[str, Any]] = None
    kpis: List[Dict[str, Any]] = Field(default_factory=list)
    metrics: List[Dict[str, Any]] = Field(default_factory=list)
    performance_targets: Optional[Dict[str, Any]] = None


class ImplementationSection(BaseModel):
    """Implementation section validation"""

    roadmap: Optional[Dict[str, Any]] = None
    milestones: List[Dict[str, Any]] = Field(default_factory=list)
    resources: List[Dict[str, Any]] = Field(default_factory=list)
    risks: List[Dict[str, Any]] = Field(default_factory=list)


class BusinessContext(BaseModel):
    """Complete business context validation schema"""

    metadata: BusinessContextMetadata
    foundation: FoundationSection
    icp: ICPSection
    competitive: CompetitiveSection
    messaging: MessagingSection
    go_to_market: GoToMarketSection
    analytics: AnalyticsSection
    implementation: ImplementationSection

    @root_validator
    def validate_required_sections(cls, values):
        """Ensure all required sections are present and valid"""
        required_sections = [
            BusinessContextSection.FOUNDATION,
            BusinessContextSection.ICP,
            BusinessContextSection.COMPETITIVE,
            BusinessContextSection.MESSAGING,
            BusinessContextSection.GO_TO_MARKET,
            BusinessContextSection.ANALYTICS,
            BusinessContextSection.IMPLEMENTATION,
        ]

        missing_sections = []
        for section in required_sections:
            if section.value not in values or values[section.value] is None:
                missing_sections.append(section.value)

        if missing_sections:
            raise ValueError(
                f"Missing required sections: {', '.join(missing_sections)}"
            )

        return values

    @validator("metadata")
    def validate_completion_threshold(cls, v):
        """Ensure minimum completion threshold is met"""
        if v.completed_steps < 20:  # Require at least 20/23 steps
            raise ValueError(
                f"Insufficient steps completed: {v.completed_steps}/23 (minimum 20 required)"
            )
        return v


class OnboardingFinalizationRequest(BaseModel):
    """Schema for onboarding finalization request"""

    session_id: str
    workspace_id: str
    user_id: Optional[str] = None
    force_finalize: bool = False  # Override validation if True


class OnboardingFinalizationResponse(BaseModel):
    """Schema for onboarding finalization response"""

    success: bool
    session_id: str
    business_context: Optional[BusinessContext] = None
    bcm: Optional[Dict[str, Any]] = None
    completed_steps: int
    total_steps: int
    finalized_at: datetime
    validation_errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


# Step validation schemas for each onboarding step
STEP_VALIDATION_SCHEMAS = {
    1: {
        "required_fields": ["company_name", "industry", "stage"],
        "optional_fields": [
            "website",
            "description",
            "founded_year",
            "employee_count",
            "revenue_range",
        ],
    },
    2: {
        "required_fields": ["value_proposition"],
        "optional_fields": ["differentiators", "unique_value"],
    },
    3: {
        "required_fields": ["contradictions"],
        "optional_fields": ["resolutions", "impact_assessment"],
    },
    4: {
        "required_fields": ["target_audience"],
        "optional_fields": ["audience_segments", "personas"],
    },
    5: {
        "required_fields": ["problem_statement"],
        "optional_fields": ["problem_severity", "affected_groups"],
    },
    6: {
        "required_fields": ["solution"],
        "optional_fields": ["solution_features", "benefits"],
    },
    7: {
        "required_fields": ["competitors"],
        "optional_fields": ["competitive_analysis", "market_position"],
    },
    8: {
        "required_fields": ["positioning"],
        "optional_fields": ["positioning_map", "differentiation"],
    },
    9: {
        "required_fields": ["revenue_model"],
        "optional_fields": ["revenue_streams", "pricing_model"],
    },
    10: {
        "required_fields": ["pricing_strategy"],
        "optional_fields": ["price_points", "value_based_pricing"],
    },
    11: {
        "required_fields": ["go_to_market"],
        "optional_fields": ["channels", "sales_strategy"],
    },
    12: {
        "required_fields": ["values"],
        "optional_fields": ["value_hierarchy", "value_examples"],
    },
    13: {
        "required_fields": ["personality"],
        "optional_fields": ["personality_traits", "tone_of_voice"],
    },
    14: {
        "required_fields": ["icps"],
        "optional_fields": ["icp_validation", "icp_prioritization"],
    },
    15: {
        "required_fields": ["pain_points"],
        "optional_fields": ["pain_severity", "pain_frequency"],
    },
    16: {
        "required_fields": ["goals"],
        "optional_fields": ["goal_priorities", "success_metrics"],
    },
    17: {
        "required_fields": ["messaging"],
        "optional_fields": ["message_hierarchy", "channel_adaptation"],
    },
    18: {
        "required_fields": ["content_strategy"],
        "optional_fields": ["content_pillars", "content_calendar"],
    },
    19: {
        "required_fields": ["sales_strategy"],
        "optional_fields": ["sales_process", "sales_tools"],
    },
    20: {
        "required_fields": ["channels"],
        "optional_fields": ["channel_prioritization", "channel_mix"],
    },
    21: {
        "required_fields": ["analytics"],
        "optional_fields": ["kpi_definitions", "measurement_framework"],
    },
    22: {
        "required_fields": ["implementation"],
        "optional_fields": ["timeline", "resource_allocation"],
    },
    23: {
        "required_fields": ["final_review"],
        "optional_fields": ["next_steps", "success_criteria"],
    },
}


def validate_step_data(step_id: int, data: Dict[str, Any]) -> tuple[bool, List[str]]:
    """
    Validate step data against schema requirements

    Args:
        step_id: Step number (1-23)
        data: Step data to validate

    Returns:
        Tuple of (is_valid, error_messages)
    """
    if step_id not in STEP_VALIDATION_SCHEMAS:
        return False, [f"Invalid step ID: {step_id}"]

    schema = STEP_VALIDATION_SCHEMAS[step_id]
    errors = []

    # Check required fields
    for field in schema["required_fields"]:
        if (
            field not in data
            or data[field] is None
            or (isinstance(data[field], str) and not data[field].strip())
        ):
            errors.append(f"Missing required field: {field}")

    # Validate data types for common fields
    if "company_name" in data and data["company_name"]:
        if len(data["company_name"].strip()) < 2:
            errors.append("Company name must be at least 2 characters")

    if "icps" in data and data["icps"]:
        if len(data["icps"]) > 3:
            errors.append("Maximum 3 ICPs allowed")

    return len(errors) == 0, errors


def extract_business_context_from_steps(step_data: Dict[str, Any]) -> BusinessContext:
    """
    Extract and validate business context from raw step data

    Args:
        step_data: Dictionary containing all step data

    Returns:
        Validated BusinessContext object
    """
    # Extract metadata
    metadata = step_data.get("metadata", {})
    session_id = metadata.get("session_id", "unknown")
    workspace_id = metadata.get("workspace_id", "unknown")
    user_id = metadata.get("user_id")

    # Count completed steps
    completed_steps = len(
        [k for k in step_data.keys() if k.startswith("step_") and step_data[k]]
    )
    completion_percentage = (completed_steps / 23) * 100

    # Build metadata
    business_metadata = BusinessContextMetadata(
        session_id=session_id,
        workspace_id=workspace_id,
        user_id=user_id,
        completed_steps=completed_steps,
        completion_percentage=completion_percentage,
    )

    # Extract sections (simplified for now - would need more sophisticated extraction)
    foundation = FoundationSection(
        company_name=step_data.get("step_1", {}).get("company_name"),
        industry=step_data.get("step_1", {}).get("industry"),
        stage=step_data.get("step_1", {}).get("stage"),
        description=step_data.get("step_1", {}).get("description"),
        value_proposition=step_data.get("step_2", {}).get("value_proposition"),
        problem_statement=step_data.get("step_5", {}).get("problem_statement"),
        solution=step_data.get("step_6", {}).get("solution"),
    )

    icp = ICPSection(
        icps=step_data.get("step_14", {}).get("icps", []),
        pain_points=step_data.get("step_15", {}).get("pain_points", []),
        goals=step_data.get("step_16", {}).get("goals", []),
        trigger_events=step_data.get("step_16", {}).get("trigger_events", []),
    )

    competitive = CompetitiveSection(
        competitors=step_data.get("step_7", {}).get("competitors", []),
        positioning=step_data.get("step_8", {}).get("positioning"),
        market_landscape=step_data.get("step_7", {}).get("market_landscape"),
    )

    messaging = MessagingSection(
        value_proposition=step_data.get("step_2", {}).get("value_proposition"),
        key_messages=step_data.get("step_17", {}).get("key_messages", []),
        taglines=step_data.get("step_17", {}).get("taglines", []),
        soundbites=step_data.get("step_17", {}).get("soundbites", []),
        brand_values=step_data.get("step_12", {}).get("values", []),
    )

    go_to_market = GoToMarketSection(
        channels=step_data.get("step_20", {}).get("channels", []),
        pricing_strategy=step_data.get("step_10", {}).get("pricing_strategy"),
        sales_strategy=step_data.get("step_19", {}).get("sales_strategy"),
        content_strategy=step_data.get("step_18", {}).get("content_strategy"),
    )

    analytics = AnalyticsSection(
        market_sizing=step_data.get("step_21", {}).get("market_sizing"),
        kpis=step_data.get("step_21", {}).get("kpis", []),
        metrics=step_data.get("step_21", {}).get("metrics", []),
        performance_targets=step_data.get("step_21", {}).get("performance_targets"),
    )

    implementation = ImplementationSection(
        roadmap=step_data.get("step_22", {}).get("implementation"),
        milestones=step_data.get("step_22", {}).get("milestones", []),
        resources=step_data.get("step_22", {}).get("resources", []),
        risks=step_data.get("step_22", {}).get("risks", []),
    )

    return BusinessContext(
        metadata=business_metadata,
        foundation=foundation,
        icp=icp,
        competitive=competitive,
        messaging=messaging,
        go_to_market=go_to_market,
        analytics=analytics,
        implementation=implementation,
    )
