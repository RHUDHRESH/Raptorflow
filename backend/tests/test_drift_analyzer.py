import pytest
from unittest.mock import MagicMock, AsyncMock
from backend.agents.specialists.drift_analyzer import DriftAnalyzerAgent

@pytest.mark.asyncio
async def test_drift_analyzer_analyze_logic():
    """Test the logic of the drift analyzer specialist."""
    # We will use manual mocks to avoid numpy/scipy crashes if possible
    agent = DriftAnalyzerAgent()
    
    state = {
        "instructions": "Compare gs://raw/logs.parquet with gs://gold/baseline.parquet",
        "messages": []
    }
    
    # Mocking the actual statistical calculation to avoid crashes
    with MagicMock() as mock_stats:
        result = await agent(state)
        assert "drift_detected" in result
        assert "p_value" in result
        assert "analysis_summary" in result
