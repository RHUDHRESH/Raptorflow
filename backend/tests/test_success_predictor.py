import pytest
from unittest.mock import AsyncMock, patch
from graphs.council import success_predictor_node
from models.council import CouncilBlackboardState

@pytest.mark.asyncio
async def test_success_predictor_node():
    """Verify that moves are assigned success confidence scores."""
    state: CouncilBlackboardState = {
        "workspace_id": "ws_123",
        "refined_moves": [
            {"title": "Move 1", "description": "Launch ads", "type": "ops"}
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
    
    # Mock agent to return score
    mock_agent_res = {
        "messages": [
            type("obj", (object,), {"content": '{"confidence_score": 85, "reasoning": "High alignment with trends."}'})
        ]
    }
    
    with patch("graphs.council.get_council_agents") as mock_get_agents:
        agents = [AsyncMock(return_value=mock_agent_res) for _ in range(12)]
        mock_get_agents.return_value = agents
        
        result = await success_predictor_node(state)
        
        assert "evaluated_moves" in result
        assert result["evaluated_moves"][0]["confidence_score"] == 85
