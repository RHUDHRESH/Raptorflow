import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from backend.agents.specialists.campaign_planner import CampaignPlannerAgent, CampaignArcOutput, MonthlyArc, StrategicMilestone
from backend.models.cognitive import AgentMessage

@pytest.mark.asyncio
async def test_campaign_planner_logic():
    """
    Phase 51: Verify that the CampaignPlannerAgent generates a 90-day arc correctly.
    """
    expected_arc = CampaignArcOutput(
        campaign_title="SOTA Launch",
        overall_objective="Establish market presence.",
        monthly_arcs=[
            MonthlyArc(
                month_number=1,
                theme="Foundation",
                milestones=[StrategicMilestone(title="Brand Kit", description="Extract values", target_kpi="Completed")]
            )
        ],
        success_metrics=["100 new leads"]
    )
    
    mock_runnable = AsyncMock()
    mock_runnable.ainvoke.return_value = expected_arc
    
    with patch("backend.agents.base.InferenceProvider") as mock_inference:
        mock_llm = MagicMock()
        mock_llm.with_structured_output.return_value = mock_runnable
        mock_inference.get_model.return_value = mock_llm
        
        agent = CampaignPlannerAgent()
        state = {
            "tenant_id": "test-tenant",
            "messages": [],
            "raw_prompt": "Create a 90-day launch plan."
        }
        
        result = await agent(state)
        
        assert result["last_agent"] == "CampaignPlanner"
        assert "SOTA Launch" in result["messages"][0].content
