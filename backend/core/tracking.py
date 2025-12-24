import logging
from typing import Any, Dict, List

from pydantic import BaseModel, Field

logger = logging.getLogger("raptorflow.core.tracking")


class MilestoneStatus(BaseModel):
    """SOTA structured milestone status."""

    title: str
    is_completed: bool
    completion_percentage: float
    blocking_issues: List[str]


class MilestoneTracker:
    """
    Industrial Milestone Tracking Agent helper.
    Audits campaign progress against strategic milestones.
    """

    @staticmethod
    def audit_milestones(
        milestones: List[Dict[str, Any]], completed_tasks: List[str]
    ) -> List[MilestoneStatus]:
        """Surgically audits milestones based on task completion."""
        statuses = []
        for ms in milestones:
            # SOTA Heuristic: If milestone title matches any completed task description (partial)
            is_done = any(
                ms["title"].lower() in task.lower() for task in completed_tasks
            )
            statuses.append(
                MilestoneStatus(
                    title=ms["title"],
                    is_completed=is_done,
                    completion_percentage=100.0 if is_done else 0.0,
                    blocking_issues=[] if is_done else ["Pending dependent tasks"],
                )
            )

        logger.info(f"Milestone audit complete for {len(milestones)} milestones.")
        return statuses
