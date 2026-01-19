import pytest
from unittest.mock import AsyncMock, patch
from backend.agents.specialists.strategic_grid_agent import StrategicGridGenerator

@pytest.mark.asyncio
async def test_strategic_grid_execution():
    """Test StrategicGrid orchestrator execution."""
    agent = StrategicGridGenerator()
    
    state = {
        "business_context": {
            "identity": {"company_name": "RaptorFlow"}
        },
        "step_data": {
            "perceptual_map": {
                "positioning_options": [
                    {"name": "The Surgical Operator", "coordinates": [0.9, 0.1]}
                ]
            }
        }
    }
    
    # Mock LLM call
    with patch.object(StrategicGridGenerator, "_call_llm", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = '{"selected_position": "The Surgical Operator", "milestones": [{"name": "Swarm Alpha", "timeline": "30 days"}], "threats": ["Copycat arrival"], "opportunities": ["Market expansion"]}'
        
        result = await agent.execute(state)
        
        assert "output" in result
        output = result["output"]
        assert output["selected_position"] == "The Surgical Operator"
        assert "milestones" in output
