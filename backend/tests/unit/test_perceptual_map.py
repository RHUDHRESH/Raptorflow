import pytest
from unittest.mock import AsyncMock, patch
from backend.agents.specialists.perceptual_map_generator import PerceptualMapGenerator

@pytest.mark.asyncio
async def test_perceptual_map_execution():
    """Test PerceptualMapGenerator agent execution."""
    agent = PerceptualMapGenerator()
    
    state = {
        "business_context": {
            "identity": {"company_name": "RaptorFlow"}
        },
        "step_data": {
            "market_intelligence": {
                "discovered_competitors": ["Hubspot", "Salesforce"]
            },
            "capability_rating": {
                "ratings": [{"capability": "Swarm", "tier": 4}]
            }
        }
    }
    
    # Mock LLM call
    with patch.object(PerceptualMapGenerator, "_call_llm", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = '{"primary_axis": "Innovation", "secondary_axis": "Simplicity", "competitors": [{"name": "Hubspot", "x": 0.3, "y": 0.8}], "positioning_options": [{"name": "The Surgical Operator", "coordinates": [0.9, 0.1]}], "only_you_quadrant": "Top Right"}'
        
        result = await agent.execute(state)
        
        assert "output" in result
        output = result["output"]
        assert "primary_axis" in output
        assert "competitors" in output
        assert "positioning_options" in output
