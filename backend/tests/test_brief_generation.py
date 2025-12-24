import pytest

from backend.agents.specialists.campaign_planner import (
    CampaignArcOutput,
    MonthlyArc,
    StrategicMilestone,
)
from backend.core.briefing import BriefGenerator


def test_brief_generation_logic():
    """
    Phase 57: Verify that the BriefGenerator creates markdown correctly.
    """
    arc = CampaignArcOutput(
        campaign_title="Launch",
        overall_objective="Awareness",
        monthly_arcs=[
            MonthlyArc(
                month_number=1,
                theme="Foundations",
                milestones=[
                    StrategicMilestone(title="BK", description="Ext", target_kpi="Done")
                ],
            )
        ],
        success_metrics=["Metric 1"],
    )

    md = BriefGenerator.generate_markdown(arc)

    assert "# 📋 CAMPAIGN BRIEF: Launch" in md
    assert "Foundations" in md
    assert "Metric 1" in md
