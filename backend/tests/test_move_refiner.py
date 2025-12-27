import pytest
from unittest.mock import AsyncMock, patch
from graphs.council import move_refiner_node
from models.council import CouncilBlackboardState

@pytest.mark.asyncio
async def test_move_refiner_node():
    """Verify that suggested moves are refined with tools and prompts."""
    state: CouncilBlackboardState = {
        "workspace_id": "ws_123",
        "suggested_moves": [
            {"title": "Podcast Launch", "description": "Launch the show", "type": "ops"}
        ],
        "parallel_thoughts": [],
        "debate_history": [],
        "consensus_metrics": {},
        "messages": [],
        "status": "complete",
        "synthesis": "Synthesis text",
        "rejected_paths": [],
        "radar_signals": []
    }
    
    # Mock agent to return refinement data
    mock_agent_res = {
        "messages": [
            type("obj", (object,), {"content": '{"tool_requirements": ["search", "content_gen"], "muse_prompt": "Create a podcast plan."}'})
        ]
    }
    
    with patch("graphs.council.get_council_agents") as mock_get_agents:
        agents = [AsyncMock(return_value=mock_agent_res) for _ in range(12)]
        mock_get_agents.return_value = agents
        
        result = await move_refiner_node(state)
        
        assert "refined_moves" in result
        assert len(result["refined_moves"]) == 1
        assert "tool_requirements" in result["refined_moves"][0]
        assert "muse_prompt" in result["refined_moves"][0]
