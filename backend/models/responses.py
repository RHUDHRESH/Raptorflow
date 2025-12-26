from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


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


# Campaign Response Models
class CampaignResponse(BaseModel):
    id: str
    title: str
    objective: str
    status: str
    tenant_id: str
    created_at: str
    updated_at: str
    arc_data: Optional[Dict[str, Any]] = None
    kpi_targets: Optional[Dict[str, Any]] = None


class MoveResponse(BaseModel):
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


# Asset Response Models
class AssetResponse(BaseModel):
    id: str
    content: str
    asset_type: str
    metadata: Dict[str, Any]
    created_at: str
    workspace_id: str


# Health Check Response Models
class HealthCheckResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    components: Dict[str, str]


class DetailedHealthCheckResponse(HealthCheckResponse):
    database: str
    cache: str
    supabase_auth: Optional[str] = None
    gcp_secrets: Optional[str] = None
    rate_limiter: Optional[str] = None


# Metrics Response Models
class MetricsResponse(BaseModel):
    counters: Dict[str, float]
    gauges: Dict[str, float]
    histograms: Dict[str, int]


class HistogramSummaryResponse(BaseModel):
    count: int
    sum: float
    min: float
    max: float
    avg: float
    p50: float
    p95: float
    p99: float


# Task Queue Response Models
class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None
    retry_count: int = 0


class QueueStatsResponse(BaseModel):
    pending: int
    running: int
    completed: int
    failed: int
    total_workers: int
    active_workers: int


# Foundation Response Models
class FoundationStateResponse(BaseModel):
    workspace_id: str
    state_data: Dict[str, Any]
    updated_at: str


class BrandKitResponse(BaseModel):
    id: str
    workspace_id: str
    brand_data: Dict[str, Any]
    created_at: str
    updated_at: str


class PositioningResponse(BaseModel):
    id: str
    workspace_id: str
    positioning_data: Dict[str, Any]
    is_active: bool
    created_at: str
    updated_at: str


# Blackbox Response Models
class BlackboxIdeaResponse(BaseModel):
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
    idea_id: str
    simulation_results: Dict[str, Any]
    confidence_score: float
    recommendations: List[str]


# Matrix Response Models
class MatrixSignalResponse(BaseModel):
    id: str
    signal_type: str
    strength: float
    source: str
    timestamp: str
    metadata: Dict[str, Any]


class MatrixInsightResponse(BaseModel):
    id: str
    insight_text: str
    confidence: float
    actionable: bool
    created_at: str
    tags: List[str]


# Muse Response Models
class MuseAssetResponse(BaseModel):
    id: str
    content: str
    asset_type: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None
    created_at: str


class MuseGenerationResponse(BaseModel):
    task_id: str
    status: str
    generated_assets: Optional[List[MuseAssetResponse]] = None
    error: Optional[str] = None


# Radar Response Models
class RadarSignalResponse(BaseModel):
    id: str
    signal_data: Dict[str, Any]
    signal_type: str
    confidence: float
    timestamp: str
    processed: bool


class RadarAlertResponse(BaseModel):
    id: str
    alert_type: str
    severity: str
    message: str
    created_at: str
    acknowledged: bool


# Payment Response Models
class PaymentIntentResponse(BaseModel):
    id: str
    amount: int
    currency: str
    status: str
    created_at: str
    metadata: Dict[str, Any]


class SubscriptionResponse(BaseModel):
    id: str
    plan_id: str
    status: str
    current_period_start: str
    current_period_end: str
    cancel_at_period_end: bool
