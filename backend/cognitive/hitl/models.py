"""
HITL Module Data Models

Defines data structures for approval requests, responses, and related entities.
"""

import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


class RequestType(str, Enum):
    CONTENT_GENERATION = "content_generation"
    EXTERNAL_POST = "external_post"
    DATA_DELETION = "data_deletion"
    HIGH_COST_OPERATION = "high_cost_operation"
    SENSITIVE_ACCESS = "sensitive_access"
    SYSTEM_CHANGE = "system_change"


class RiskLevel(str, Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class ApprovalRequest:
    """Request for human approval."""

    gate_id: str
    workspace_id: str
    user_id: str
    request_type: RequestType
    output_preview: str
    risk_level: RiskLevel
    reason: str
    created_at: datetime
    expires_at: datetime
    status: ApprovalStatus = ApprovalStatus.PENDING
    response_feedback: Optional[str] = None
    responded_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if not self.gate_id:
            self.gate_id = str(uuid.uuid4())


@dataclass
class ApprovalResponse:
    """Response to approval request."""

    gate_id: str
    approved: bool
    feedback: Optional[str] = None
    modified_output: Optional[str] = None
    responded_by: Optional[str] = None
    responded_at: Optional[datetime] = None

    def __post_init__(self):
        if self.responded_at is None:
            self.responded_at = datetime.now()


@dataclass
class RateLimitResult:
    """Result of rate limit check."""

    allowed: bool
    remaining: int
    reset_at: datetime
    limit: int
    window_seconds: int


@dataclass
class BudgetCheck:
    """Result of budget check."""

    allowed: bool
    remaining: float
    warning: bool
    limit: float
    estimated_cost: float


@dataclass
class FeedbackData:
    """Collected feedback data."""

    gate_id: str
    rating: Optional[int] = None  # 1-5 scale
    comments: Optional[str] = None
    corrections: Optional[List[str]] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class EscalationInfo:
    """Information about escalation."""

    gate_id: str
    escalated_to: str
    reason: str
    escalated_at: datetime
    original_approver: str


@dataclass
class AuditEntry:
    """Audit trail entry."""

    gate_id: str
    action: str
    user_id: str
    timestamp: datetime
    details: Dict[str, Any]
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
