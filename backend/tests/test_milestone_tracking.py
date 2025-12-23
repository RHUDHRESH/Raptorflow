import pytest
from backend.core.tracking import MilestoneTracker

def test_milestone_tracking_logic():
    """
    Phase 58: Verify that the MilestoneTracker correctly audits progress.
    """
    milestones = [
        {"title": "Brand Kit"},
        {"title": "ICP Profiling"}
    ]
    completed_tasks = ["Extract surgical Brand Kit"]
    
    statuses = MilestoneTracker.audit_milestones(milestones, completed_tasks)
    
    assert statuses[0].is_completed is True
    assert statuses[1].is_completed is False
    assert "Pending" in statuses[1].blocking_issues[0]
