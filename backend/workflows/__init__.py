"""
End-to-end workflow orchestrators for RaptorFlow.
Provides complete workflow implementations for all major processes.
"""

from approval import ApprovalWorkflow
from blackbox import BlackboxWorkflow
from campaign import CampaignWorkflow
from content import ContentWorkflow
from daily_wins import DailyWinsWorkflow
from feedback import FeedbackWorkflow
from move import MoveWorkflow
from onboarding import OnboardingWorkflow
from research import ResearchWorkflow


class WorkflowManager:
    """Minimal workflow manager placeholder to satisfy imports."""

    def __init__(self):
        # Map workflow names to classes for potential lookup
        self.workflows = {
            "onboarding": OnboardingWorkflow,
            "move": MoveWorkflow,
            "content": ContentWorkflow,
            "research": ResearchWorkflow,
            "blackbox": BlackboxWorkflow,
            "daily_wins": DailyWinsWorkflow,
            "campaign": CampaignWorkflow,
            "approval": ApprovalWorkflow,
            "feedback": FeedbackWorkflow,
        }

    def get_workflow(self, name: str):
        return self.workflows.get(name)


__all__ = [
    "OnboardingWorkflow",
    "MoveWorkflow",
    "ContentWorkflow",
    "ResearchWorkflow",
    "BlackboxWorkflow",
    "DailyWinsWorkflow",
    "CampaignWorkflow",
    "ApprovalWorkflow",
    "FeedbackWorkflow",
    "WorkflowManager",
]
