"""
Human-in-the-Loop (HITL) Module - Human Approval System

Manages approval gates, feedback collection, and human oversight
for critical operations and high-risk actions.
"""

from audit import ApprovalAudit
from auto_approve import AutoApprover
from escalation import EscalationManager
from feedback import FeedbackCollector
from gate import ApprovalGate
from notifications import ApprovalNotifier
from override import HumanOverride
from risk_rules import ApprovalRiskRules
from timeout_handler import TimeoutHandler

from ..models import ApprovalRequest, ApprovalResponse

__all__ = [
    "ApprovalGate",
    "ApprovalRequest",
    "ApprovalResponse",
    "ApprovalRiskRules",
    "FeedbackCollector",
    "HumanOverride",
    "ApprovalNotifier",
    "AutoApprover",
    "EscalationManager",
    "TimeoutHandler",
    "ApprovalAudit",
]
