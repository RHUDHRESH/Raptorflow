"""
End-to-end workflow orchestrators for RaptorFlow.

Keep this package lightweight: importing `workflows` should not eagerly import
all workflow modules (which may pull optional dependencies).
"""

from __future__ import annotations

from importlib import import_module
from typing import Any

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

_WORKFLOW_EXPORTS: dict[str, tuple[str, str]] = {
    "OnboardingWorkflow": (".onboarding", "OnboardingWorkflow"),
    "MoveWorkflow": (".move", "MoveWorkflow"),
    "ContentWorkflow": (".content", "ContentWorkflow"),
    "ResearchWorkflow": (".research", "ResearchWorkflow"),
    "BlackboxWorkflow": (".blackbox", "BlackboxWorkflow"),
    "DailyWinsWorkflow": (".daily_wins", "DailyWinsWorkflow"),
    "CampaignWorkflow": (".campaign", "CampaignWorkflow"),
    "ApprovalWorkflow": (".approval", "ApprovalWorkflow"),
    "FeedbackWorkflow": (".feedback", "FeedbackWorkflow"),
}


def __getattr__(name: str) -> Any:
    if name in _WORKFLOW_EXPORTS:
        module_name, attr_name = _WORKFLOW_EXPORTS[name]
        module = import_module(module_name, package=__name__)
        return getattr(module, attr_name)
    raise AttributeError(name)


class WorkflowManager:
    """Workflow manager with lazy workflow lookup."""

    def __init__(self):
        self.workflows = {
            "onboarding": "OnboardingWorkflow",
            "move": "MoveWorkflow",
            "content": "ContentWorkflow",
            "research": "ResearchWorkflow",
            "blackbox": "BlackboxWorkflow",
            "daily_wins": "DailyWinsWorkflow",
            "campaign": "CampaignWorkflow",
            "approval": "ApprovalWorkflow",
            "feedback": "FeedbackWorkflow",
        }

    def get_workflow(self, name: str):
        export_name = self.workflows.get(name)
        if not export_name:
            return None
        return getattr(__import__(__name__, fromlist=[export_name]), export_name)
