import pytest
from unittest.mock import AsyncMock, patch
from backend.agents.specialists.insight_extractor import InsightExtractor

@pytest.mark.asyncio
async def test_insight_extractor_execution():
    """Test InsightExtractor agent execution."""
    agent = InsightExtractor()
    
    state = {
        "step_data": {
            "reddit_scraper": {
                "threads": [
                    {
                        "title": "I hate my current CRM",
                        "selftext": "It's too expensive and the UI is terrible.",
                        "comments": [
                            {"body": "Try Salesforce, it's better but still complex."},
                            {"body": "I prefer Hubspot for its simplicity."}
                        ]
                    }
                ]
            }
        }
    }
    
    # Mock LLM call
    with patch.object(InsightExtractor, "_call_llm", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = '{"pain_points": [{"category": "UX", "description": "Terrible UI", "sentiment": -0.9}], "desires": [], "objections": [], "discovered_competitors": ["Salesforce", "Hubspot"]}'
        
        result = await agent.execute(state)
        
        assert "output" in result
        output = result["output"]
        assert "pain_points" in output
        assert "discovered_competitors" in output
        assert "Salesforce" in output["discovered_competitors"]
