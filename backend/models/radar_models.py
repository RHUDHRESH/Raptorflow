"""
Radar Signal Models - Core data structures for competitive intelligence
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class SignalCategory(str, Enum):
    """Signal categories for competitive intelligence"""

    OFFER = "offer"
    HOOK = "hook"
    PROOF = "proof"
    CTA = "cta"
    OBJECTION = "objection"
    TREND = "trend"


class SignalStrength(str, Enum):
    """Signal strength levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class SignalFreshness(str, Enum):
    """Signal freshness based on age"""

    FRESH = "fresh"  # 0-7 days
    WARM = "warm"  # 8-30 days
    STALE = "stale"  # 31-90 days


class ScanFrequency(str, Enum):
    """Scan frequency for scheduled radar scans"""

    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"


class EvidenceType(str, Enum):
    """Types of evidence supporting signals"""

    URL = "url"
    SCREENSHOT = "screenshot"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    PDF = "pdf"
    REVIEW = "review"


class MoveObjective(str, Enum):
    """Campaign objectives for signal mapping"""

    ACQUIRE = "acquire"
    ACTIVATE = "activate"
    RETAIN = "retain"
    MONETIZE = "monetize"


class MoveStage(str, Enum):
    """Campaign stages for signal mapping"""

    ATTENTION = "attention"
    CONSIDERATION = "consideration"
    CONVERSION = "conversion"


class Evidence(BaseModel):
    """Evidence supporting a signal"""

    id: str = Field(default_factory=lambda: str(uuid4()))
    type: EvidenceType
    source: str
    url: Optional[str] = None
    content: str
    confidence: float = Field(ge=0.0, le=1.0)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Signal(BaseModel):
    """Core signal entity"""

    id: str = Field(default_factory=lambda: str(uuid4()))
    tenant_id: str
    category: SignalCategory
    title: str
    content: str
    strength: SignalStrength
    freshness: SignalFreshness
    evidence: List[Evidence] = Field(default_factory=list)
    action_suggestion: Optional[str] = None
    source_competitor: Optional[str] = None
    source_url: Optional[str] = None
    cluster_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class SignalCluster(BaseModel):
    """Cluster of similar signals"""

    id: str = Field(default_factory=lambda: str(uuid4()))
    tenant_id: str
    category: SignalCategory
    theme: str
    signal_count: int = 0
    strength: SignalStrength
    signals: List[str] = Field(default_factory=list)  # Signal IDs
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class SignalMoveMapping(BaseModel):
    """Mapping between signals and campaign moves"""

    id: str = Field(default_factory=lambda: str(uuid4()))
    signal_id: str
    move_id: str
    objective: MoveObjective
    stage: MoveStage
    channel: str
    relevance_score: float = Field(ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class RadarSource(BaseModel):
    """Source configuration for Radar scanning"""

    id: str = Field(default_factory=lambda: str(uuid4()))
    tenant_id: str
    name: str
    type: str  # competitor_website, social, review_site, community, own_content
    url: str
    scan_frequency: str = "daily"  # hourly, daily, weekly
    health_score: int = Field(default=100, ge=0, le=100)
    last_checked: Optional[datetime] = None
    last_success: Optional[datetime] = None
    is_active: bool = True
    config: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Dossier(BaseModel):
    """Intelligence dossier for campaigns"""

    id: str = Field(default_factory=lambda: str(uuid4()))
    tenant_id: str
    campaign_id: Optional[str] = None
    title: str
    summary: List[str] = Field(default_factory=list)
    pinned_signals: List[str] = Field(default_factory=list)  # Signal IDs
    hypotheses: List[str] = Field(default_factory=list)
    recommended_experiments: List[str] = Field(default_factory=list)
    copy_snippets: List[Dict[str, str]] = Field(default_factory=list)
    market_narrative: Dict[str, str] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_published: bool = False


class ScanJob(BaseModel):
    """Background scan job configuration"""

    id: str = Field(default_factory=lambda: str(uuid4()))
    tenant_id: str
    source_ids: List[str]
    scan_type: str  # recon, full, targeted
    status: str = "pending"  # pending, running, completed, failed
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    signals_found: int = 0
    errors: List[str] = Field(default_factory=list)
    config: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SignalCreateRequest(BaseModel):
    """Request model for creating signals"""

    category: SignalCategory
    title: str
    content: str
    source_competitor: Optional[str] = None
    source_url: Optional[str] = None
    evidence: List[Evidence] = Field(default_factory=list)


class SignalUpdateRequest(BaseModel):
    """Request model for updating signals"""

    title: Optional[str] = None
    content: Optional[str] = None
    strength: Optional[SignalStrength] = None
    action_suggestion: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class SignalResponse(BaseModel):
    """Response model for signal data"""

    id: str
    tenant_id: str
    category: SignalCategory
    title: str
    content: str
    strength: SignalStrength
    freshness: SignalFreshness
    evidence_count: int
    action_suggestion: Optional[str] = None
    source_competitor: Optional[str] = None
    cluster_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class RadarReconRequest(BaseModel):
    """Request model for radar recon scans."""

    icp_id: str
    source_urls: Optional[List[str]] = None


class RadarDossierRequest(BaseModel):
    """Request model for dossier generation."""

    campaign_id: str
    signal_ids: Optional[List[str]] = None


class RadarManualScanRequest(BaseModel):
    """Request model for manual scan scheduling."""

    source_ids: List[str]
    scan_type: str = "recon"


class RadarNotificationRequest(BaseModel):
    """Request model for notification processing."""

    signal_ids: List[str]
    tenant_preferences: Optional[Dict[str, Any]] = None
