import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from graphs.council import get_expert_council_graph


@pytest.mark.asyncio
@patch("graphs.council.RadarEventsTool")
@patch("graphs.council.RadarCompetitorsTool")
@patch("graphs.council.get_council_agents")
@patch("graphs.council.save_reasoning_chain")
@patch("graphs.council.save_rejections")
@patch("graphs.council.save_campaign")
@patch("graphs.council.save_move")
@patch("graphs.council.update_move_description")
async def test_council_e2e_simulation(
    m_update_move,
    m_save_move,
    m_save_campaign,
    m_save_rejections,
    m_save_chain,
    m_get_agents,
    m_comp_tool,
    m_events_tool,
):
    # Setup tools mocks
    mock_events_res = {
        "success": True,
        "data": {
            "found_events": [
                {"name": "Event 1", "type": "conference", "relevance": 0.9}
            ]
        },
    }
    m_events_tool.return_value.run = AsyncMock(return_value=mock_events_res)

    mock_comp_res = {
        "success": True,
        "data": {"competitors": [{"name": "Comp 1", "recent_changes": "Price hike"}]},
    }
    m_comp_tool.return_value.run = AsyncMock(return_value=mock_comp_res)

    # Setup database mocks
    m_save_chain.return_value = "chain_abc"
    m_save_rejections.return_value = None
    m_save_campaign.return_value = "camp_123"
    m_save_move.return_value = "move_456"
    m_update_move.return_value = None

    # Full JSON response that satisfies all nodes
    mock_json_response = json.dumps(
        {
            "alignment": 0.9,
            "confidence": 0.9,
            "confidence_score": 90,
            "risk": 0.1,
            "decree": "Execute surgical move.",
            "rationale": "High ROI",
            "impact": 0.8,
            "recommendation": "Go for it",
            "score": 0.9,
            "rejected_paths": [{"path": "Passive approach", "reason": "Too slow"}],
            "campaign_arc": {
                "title": "Surgical Strike 2026",
                "objective": "Dominate the niche",
                "arc_data": {"phases": ["Phase 1", "Phase 2"]},
            },
            "title": "Tactical Expansion",
            "objective": "Expand reach",
            "arc_data": {"phases": ["Phase 1", "Phase 2"]},
            "moves": [
                {"title": "Move A", "description": "Execute A", "type": "outreach"}
            ],
            "tool_requirements": ["brave_search"],
            "muse_prompt": "Create asset for Move A",
            "reasoning": "Data looks good",
        }
    )

    mock_agent = AsyncMock()
    mock_agent.name = "Expert_A"
    mock_agent.role = "strategist"
    mock_agent.side_effect = lambda s: {
        "messages": [MagicMock(content=mock_json_response)]
    }

    m_get_agents.return_value = [mock_agent] * 12

    graph = get_expert_council_graph().compile()

    initial_state = {
        "workspace_id": "ws_123",
        "brief": {"goals": "marketing opportunities", "target_icp": "founders"},
        "status": "idle",
        "messages": [],
        "parallel_thoughts": [],
        "debate_history": [],
        "consensus_metrics": {},
        "rejected_paths": [],
        "radar_signals": [],
        "suggested_moves": [],
        "refined_moves": [],
        "evaluated_moves": [],
        "approved_moves": [],
        "discarded_moves": [],
    }

    config = {"recursion_limit": 50}
    final_state = await graph.ainvoke(initial_state, config=config)

    assert final_state is not None
    assert "consensus_metrics" in final_state
    assert final_state["consensus_metrics"]["alignment"] >= 0.7
    assert "campaign_id" in final_state
    assert len(final_state.get("move_ids", [])) > 0
    assert final_state["last_agent"] == "Propagative_Executor"
