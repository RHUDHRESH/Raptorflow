import re
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator


class BaseRequestModel(BaseModel):
    """Base model for all API requests with common validation."""

    class Config:
        extra = "forbid"  # Prevent unknown fields
        validate_assignment = True


class BaseResponseModel(BaseModel):
    """Base response model for all API responses."""

    success: bool = True
    message: Optional[str] = None
    data: Optional[Any] = None

    class Config:
        json_encoders = {
            # Add any custom encoders if needed
        }


class ErrorResponseModel(BaseModel):
    """Error response model."""

    success: bool = False
    error: str
    message: Optional[str] = None
    status_code: Optional[int] = None


class PaginatedResponseModel(BaseModel):
    """Paginated response model."""

    success: bool = True
    data: List[Any]
    pagination: Dict[str, Any]
    message: Optional[str] = None


# Campaign Models
class CampaignCreateRequest(BaseRequestModel):
    """Request model for creating campaigns."""

    title: str = Field(..., min_length=1, max_length=200, description="Campaign title")
    objective: str = Field(
        ..., min_length=10, max_length=1000, description="Campaign objective"
    )
    status: Optional[str] = Field("draft", regex="^(draft|active|paused|completed)$")

    @validator("title")
    def validate_title(cls, v):
        if not v or not v.strip():
            raise ValueError("Title cannot be empty")
        # Remove any potentially harmful characters
        return re.sub(r'[<>"\']', "", v.strip())


class CampaignUpdateRequest(BaseRequestModel):
    """Request model for updating campaigns."""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    objective: Optional[str] = Field(None, min_length=10, max_length=1000)
    status: Optional[str] = Field(None, regex="^(draft|active|paused|completed)$")
    arc_data: Optional[Dict[str, Any]] = None
    kpi_targets: Optional[Dict[str, Any]] = None


class CampaignResponse(BaseModel):
    """Response model for campaign data."""

    id: str
    title: str
    objective: str
    status: str
    tenant_id: str
    created_at: str
    updated_at: str
    arc_data: Optional[Dict[str, Any]] = None
    kpi_targets: Optional[Dict[str, Any]] = None


# Move Models
class MoveCreateRequest(BaseRequestModel):
    """Request model for creating moves."""

    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=10, max_length=2000)
    priority: Optional[int] = Field(3, ge=1, le=5)
    move_type: str = Field(..., regex="^(content|paid|organic|technical|research)$")
    tool_requirements: Optional[List[Dict[str, Any]]] = Field(default_factory=list)


class MoveResponse(BaseModel):
    """Response model for move data."""

    id: str
    campaign_id: str
    title: str
    description: str
    status: str
    priority: int
    move_type: str
    created_at: str
    updated_at: str
    tool_requirements: Optional[List[Dict[str, Any]]] = None
    execution_result: Optional[Dict[str, Any]] = None


# Asset Models
class AssetCreateRequest(BaseRequestModel):
    """Request model for creating assets."""

    content: str = Field(..., min_length=1, max_length=50000)
    asset_type: str = Field(..., regex="^(image|text|video|document|creative)$")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    @validator("content")
    def validate_content(cls, v):
        if not v or not v.strip():
            raise ValueError("Content cannot be empty")
        return v.strip()


class AssetResponse(BaseModel):
    """Response model for asset data."""

    id: str
    content: str
    asset_type: str
    metadata: Dict[str, Any]
    created_at: str
    workspace_id: str


# Vector Search Models
class VectorSearchRequest(BaseRequestModel):
    """Request model for vector search."""

    embedding: List[float] = Field(..., min_items=1, max_items=1536)
    limit: Optional[int] = Field(10, ge=1, le=100)
    memory_type: Optional[str] = Field("semantic", regex="^(semantic|episodic)$")
    filters: Optional[Dict[str, Any]] = Field(default_factory=dict)

    @validator("embedding")
    def validate_embedding(cls, v):
        if len(v) == 0:
            raise ValueError("Embedding cannot be empty")
        # Check for valid float values
        for i, val in enumerate(v):
            if not isinstance(val, (int, float)):
                raise ValueError(f"Embedding value at index {i} is not a number: {val}")
            if abs(val) > 10:  # Basic sanity check
                raise ValueError(f"Embedding value at index {i} seems invalid: {val}")
        return v


class VectorSearchResponse(BaseModel):
    """Response model for vector search results."""

    results: List[Dict[str, Any]]
    total_found: int
    search_time_ms: float


# Memory Models
class MemorySaveRequest(BaseRequestModel):
    """Request model for saving memory."""

    content: str = Field(..., min_length=1, max_length=10000)
    embedding: List[float] = Field(..., min_items=1, max_items=1536)
    memory_type: str = Field("semantic", regex="^(semantic|episodic)$")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    @validator("content")
    def validate_content(cls, v):
        if not v or not v.strip():
            raise ValueError("Content cannot be empty")
        return v.strip()


class MemoryResponse(BaseModel):
    """Response model for memory data."""

    id: str
    content: str
    memory_type: str
    metadata: Dict[str, Any]
    created_at: str
    similarity_score: Optional[float] = None


# Health Check Models
class HealthCheckRequest(BaseRequestModel):
    """Request model for health checks (minimal)."""

    detailed: Optional[bool] = Field(False)


class HealthCheckResponse(BaseModel):
    """Response model for health check."""

    status: str
    timestamp: str
    version: str
    components: Dict[str, str]


class DetailedHealthCheckResponse(HealthCheckResponse):
    """Detailed health check response with external services."""

    database: str
    cache: str
    supabase_auth: Optional[str] = None
    gcp_secrets: Optional[str] = None
    rate_limiter: Optional[str] = None


# Metrics Models
class MetricsResponse(BaseModel):
    """Response model for metrics data."""

    counters: Dict[str, float]
    gauges: Dict[str, float]
    histograms: Dict[str, int]


class HistogramSummaryResponse(BaseModel):
    """Response model for histogram summary."""

    count: int
    sum: float
    min: float
    max: float
    avg: float
    p50: float
    p95: float
    p99: float


# Task Queue Models
class TaskStatusResponse(BaseModel):
    """Response model for task status."""

    task_id: str
    status: str
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None
    retry_count: int = 0


class QueueStatsResponse(BaseModel):
    """Response model for queue statistics."""

    pending: int
    running: int
    completed: int
    failed: int
    total_workers: int
    active_workers: int


# Foundation Models
class FoundationStateRequest(BaseRequestModel):
    """Request model for foundation state."""

    state_data: Dict[str, Any] = Field(..., description="Foundation state data")


class FoundationStateResponse(BaseModel):
    """Response model for foundation state."""

    workspace_id: str
    state_data: Dict[str, Any]
    updated_at: str


class BrandKitRequest(BaseRequestModel):
    """Request model for brand kit."""

    brand_data: Dict[str, Any] = Field(..., description="Brand kit data")


class BrandKitResponse(BaseModel):
    """Response model for brand kit."""

    id: str
    workspace_id: str
    brand_data: Dict[str, Any]
    created_at: str
    updated_at: str


class PositioningRequest(BaseRequestModel):
    """Request model for positioning."""

    positioning_data: Dict[str, Any] = Field(..., description="Positioning data")


class PositioningResponse(BaseModel):
    """Response model for positioning."""

    id: str
    workspace_id: str
    positioning_data: Dict[str, Any]
    is_active: bool
    created_at: str
    updated_at: str


# Blackbox Models
class BlackboxIdeaResponse(BaseModel):
    """Response model for Blackbox ideas."""

    id: str
    title: str
    summary: str
    novelty_score: float
    risk_score: float
    reach_score: float
    icp_alignment_score: float
    created_at: str
    metadata: Dict[str, Any]


class BlackboxSimulationResponse(BaseModel):
    """Response model for Blackbox simulations."""

    idea_id: str
    simulation_results: Dict[str, Any]
    confidence_score: float
    recommendations: List[str]


# Matrix Models
class MatrixSignalResponse(BaseModel):
    """Response model for Matrix signals."""

    id: str
    signal_type: str
    strength: float
    source: str
    timestamp: str
    metadata: Dict[str, Any]


class MatrixInsightResponse(BaseModel):
    """Response model for Matrix insights."""

    id: str
    insight_text: str
    confidence: float
    actionable: bool
    created_at: str
    tags: List[str]


# Muse Models
class MuseGenerationRequest(BaseRequestModel):
    """Request model for Muse asset generation."""

    prompt: str = Field(..., min_length=5, max_length=1000)
    asset_type: str = Field(..., regex="^(image|text|creative)$")
    style: Optional[str] = Field(
        "professional", regex="^(professional|casual|bold|minimal)$"
    )
    count: Optional[int] = Field(1, ge=1, le=5)


class MuseAssetResponse(BaseModel):
    """Response model for Muse assets."""

    id: str
    content: str
    asset_type: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None
    created_at: str


class MuseGenerationResponse(BaseModel):
    """Response model for Muse generation results."""

    task_id: str
    status: str
    generated_assets: Optional[List[MuseAssetResponse]] = None
    error: Optional[str] = None


# Radar Models
class RadarSignalResponse(BaseModel):
    """Response model for Radar signals."""

    id: str
    signal_data: Dict[str, Any]
    signal_type: str
    confidence: float
    timestamp: str
    processed: bool


class RadarAlertResponse(BaseModel):
    """Response model for Radar alerts."""

    id: str
    alert_type: str
    severity: str
    message: str
    created_at: str
    acknowledged: bool


# Payment Models
class PaymentIntentRequest(BaseRequestModel):
    """Request model for payment intent creation."""

    amount: int = Field(..., ge=100, description="Amount in cents")
    currency: Optional[str] = Field("usd", regex="^(usd|eur|gbp)$")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class PaymentIntentResponse(BaseModel):
    """Response model for payment intent."""

    id: str
    amount: int
    currency: str
    status: str
    created_at: str
    metadata: Dict[str, Any]


class SubscriptionResponse(BaseModel):
    """Response model for subscription data."""

    id: str
    plan_id: str
    status: str
    current_period_start: str
    current_period_end: str
    cancel_at_period_end: bool


# Feedback Models
class FeedbackRequest(BaseRequestModel):
    """Request model for user feedback."""

    feedback_type: str = Field(..., regex="^(bug|feature|general)$")
    content: str = Field(..., min_length=10, max_length=2000)
    rating: Optional[int] = Field(None, ge=1, le=5)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class FeedbackResponse(BaseModel):
    """Response model for feedback submission."""

    id: str
    feedback_type: str
    status: str
    created_at: str
