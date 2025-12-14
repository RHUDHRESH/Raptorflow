# backend/events.py
# RaptorFlow Codex - Event Type Definitions
# Week 3 Tuesday - Event Schema Specifications

from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum

# ============================================================================
# EVENT PAYLOADS
# ============================================================================

class AgentStartPayload(BaseModel):
    """Agent execution start event"""
    agent_name: str
    agent_type: str
    task: str
    parameters: Dict[str, Any] = {}
    context: Dict[str, Any] = {}
    priority: int = 5

class AgentCompletePayload(BaseModel):
    """Agent execution completion event"""
    agent_name: str
    task: str
    duration_seconds: float
    tokens_used: int
    cost: float
    result_summary: str
    success: bool = True

class AgentErrorPayload(BaseModel):
    """Agent execution error event"""
    agent_name: str
    task: str
    error_message: str
    error_type: str
    duration_seconds: float
    retry_attempt: int = 0
    max_retries: int = 3

class CampaignActivatePayload(BaseModel):
    """Campaign activation event"""
    campaign_id: str
    campaign_name: str
    positioning: str
    target_audience: str
    start_date: str
    assigned_agents: List[str] = []

class CampaignPausePayload(BaseModel):
    """Campaign pause event"""
    campaign_id: str
    campaign_name: str
    reason: str
    current_progress_percent: int

class MoveExecutePayload(BaseModel):
    """Move execution event"""
    move_id: str
    move_name: str
    move_type: str
    assigned_agent: str
    context: Dict[str, Any] = {}
    expected_outcome: str

class SignalDetectedPayload(BaseModel):
    """Market signal detection event"""
    signal_id: str
    signal_type: str
    data_source: str
    market_segment: str
    relevance_score: float
    signal_data: Dict[str, Any]

class InsightGeneratedPayload(BaseModel):
    """Insight generation event"""
    insight_id: str
    insight_type: str
    generating_agent: str
    confidence_score: float
    summary: str
    detailed_analysis: Dict[str, Any]
    actionable_recommendations: List[str] = []

class AlertCreatedPayload(BaseModel):
    """Alert creation event"""
    alert_id: str
    alert_type: str
    severity: str  # "critical", "high", "medium", "low"
    title: str
    description: str
    affected_campaigns: List[str] = []
    recommended_action: str

class WorkspaceUpdatePayload(BaseModel):
    """Workspace state update event"""
    workspace_id: str
    update_type: str  # "settings", "members", "billing", "limits"
    changed_fields: Dict[str, Any]
    previous_values: Dict[str, Any]
    actor_user_id: str

# ============================================================================
# GUILD-SPECIFIC EVENTS
# ============================================================================

class ResearchGuildEventPayload(BaseModel):
    """Research guild internal event"""
    research_id: str
    research_topic: str
    research_stage: str  # "discovery", "analysis", "synthesis", "reporting"
    progress_percent: int
    key_findings: List[str] = []
    next_steps: List[str] = []

class MuseGuildEventPayload(BaseModel):
    """Muse guild creative output event"""
    content_id: str
    content_type: str  # "copy", "design", "video", "strategy"
    content_status: str  # "draft", "review", "approved", "published"
    creator_agent: str
    content_summary: str
    performance_metrics: Dict[str, Any] = {}

class MatrixGuildEventPayload(BaseModel):
    """Matrix guild intelligence event"""
    intelligence_id: str
    intelligence_type: str
    competitive_insight: str
    market_opportunity: str
    threat_assessment: str
    confidence_level: float
    recommended_response: str

class GuardianGuildEventPayload(BaseModel):
    """Guardian guild compliance event"""
    check_id: str
    check_type: str  # "policy", "legal", "ethical", "brand"
    status: str  # "pass", "fail", "warn"
    issues_found: List[str] = []
    recommendations: List[str] = []

# ============================================================================
# COORDINATION EVENTS (Agent-to-Agent Communication)
# ============================================================================

class InterGuildCoordinationPayload(BaseModel):
    """Coordination between guilds"""
    coordination_id: str
    source_guild: str
    target_guild: str
    action_required: str
    context: Dict[str, Any]
    deadline: Optional[str] = None
    priority: int = 5

class CouncilOfLordsDirectivePayload(BaseModel):
    """Directive from Council of Lords"""
    directive_id: str
    issuing_lord: str  # "architect", "cognition", "strategos", etc.
    directive_type: str  # "strategy", "resource_allocation", "priority_shift"
    affected_guilds: List[str]
    directive_details: Dict[str, Any]
    compliance_deadline: str

class PerformanceMetricsPayload(BaseModel):
    """Performance metrics broadcast"""
    metrics_id: str
    agent_name: str
    guild_name: str
    period: str  # "hourly", "daily", "weekly"
    metrics: Dict[str, float]
    anomalies: List[str] = []
    performance_trend: str  # "improving", "stable", "declining"

class ResourceAllocationPayload(BaseModel):
    """Resource request/allocation event"""
    request_id: str
    requesting_agent: str
    resource_type: str  # "tokens", "compute", "priority"
    current_allocation: float
    requested_allocation: float
    justification: str
    duration_minutes: int

# ============================================================================
# SYSTEM EVENTS
# ============================================================================

class RaptorBusHealthPayload(BaseModel):
    """RaptorBus health check event"""
    timestamp: str
    connected_channels: int
    active_subscriptions: int
    messages_processed: int
    dlq_size: int
    avg_latency_ms: float
    status: str  # "healthy", "degraded", "unhealthy"

class SystemMetricsPayload(BaseModel):
    """System-wide performance metrics"""
    timestamp: str
    total_agents_active: int
    total_messages_processed: int
    total_tokens_used: int
    total_cost_usd: float
    database_connections: int
    redis_memory_usage_mb: float
    avg_message_latency_ms: float

class ErrorAggregationPayload(BaseModel):
    """Aggregated error report"""
    report_id: str
    period: str
    total_errors: int
    errors_by_type: Dict[str, int]
    errors_by_agent: Dict[str, int]
    critical_errors: List[str]
    most_affected_component: str

# ============================================================================
# EVENT ROUTING TABLE
# ============================================================================

EVENT_PAYLOAD_MAPPING = {
    "agent:start": AgentStartPayload,
    "agent:complete": AgentCompletePayload,
    "agent:error": AgentErrorPayload,
    "campaign:activate": CampaignActivatePayload,
    "campaign:pause": CampaignPausePayload,
    "move:execute": MoveExecutePayload,
    "signal:detected": SignalDetectedPayload,
    "insight:generated": InsightGeneratedPayload,
    "alert:created": AlertCreatedPayload,
    "workspace:update": WorkspaceUpdatePayload,
    "guild:research": ResearchGuildEventPayload,
    "guild:muse": MuseGuildEventPayload,
    "guild:matrix": MatrixGuildEventPayload,
    "guild:guardian": GuardianGuildEventPayload,
    "coordination:inter_guild": InterGuildCoordinationPayload,
    "coordination:council_directive": CouncilOfLordsDirectivePayload,
    "metrics:performance": PerformanceMetricsPayload,
    "resource:allocation": ResourceAllocationPayload,
    "system:health": RaptorBusHealthPayload,
    "system:metrics": SystemMetricsPayload,
    "system:errors": ErrorAggregationPayload,
}

def validate_payload(event_type: str, payload: Dict[str, Any]) -> bool:
    """
    Validate payload against event type schema.

    Args:
        event_type: Event type name
        payload: Payload dictionary

    Returns:
        True if valid, raises ValidationError if invalid
    """
    if event_type not in EVENT_PAYLOAD_MAPPING:
        raise ValueError(f"Unknown event type: {event_type}")

    payload_class = EVENT_PAYLOAD_MAPPING[event_type]
    payload_class(**payload)  # Will raise ValidationError if invalid

    return True

