from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.agents.supervisor import HierarchicalSupervisor


@pytest.mark.asyncio
async def test_delegate_to_specialist_logic():
    """Test that the supervisor can delegate work to a specialist node."""
    mock_llm = MagicMock()
    supervisor = HierarchicalSupervisor(
        llm=mock_llm, team_members=["DriftAnalyzer"], system_prompt="..."
    )

    # Mock specialist node
    mock_specialist = AsyncMock()
    mock_specialist.return_value = {"analysis_summary": "No drift detected"}

    # In a real build, LangGraph handles node execution.
    # Here we define the method that PREPARES the delegation or handles it manually for testing.

    state = {"next": "DriftAnalyzer", "instructions": "Check for drift"}

    result = await supervisor.delegate_to_specialist(
        "DriftAnalyzer", state, mock_specialist
    )
    assert result["analysis_summary"] == "No drift detected"
    assert mock_specialist.called
