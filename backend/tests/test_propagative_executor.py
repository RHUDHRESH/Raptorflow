import pytest
from unittest.mock import AsyncMock, patch
from graphs.council import propagative_executor_node
from models.council import CouncilBlackboardState

@pytest.mark.asyncio
async def test_propagative_executor_node():
    """Verify that refined moves are saved to the database."""
    state: CouncilBlackboardState = {
        "workspace_id": "ws_123",
        "campaign_id": "camp_123",
        "refined_moves": [
            {
                "title": "Move 1",
                "description": "Desc 1",
                "type": "ops",
                "tool_requirements": ["search"],
                "muse_prompt": "Prompt 1"
            }
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
    
    with patch("graphs.council.save_move", new_callable=AsyncMock) as mock_save:
        mock_save.return_value = "move_123"
        result = await propagative_executor_node(state)
        
        assert "move_ids" in result
        assert result["move_ids"] == ["move_123"]
        mock_save.assert_awaited_once()
