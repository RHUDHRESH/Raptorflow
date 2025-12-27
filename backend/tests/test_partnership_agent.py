from unittest.mock import MagicMock, patch

import pytest

from agents.specialists.partnership import PartnershipAgent
from tools.audience_overlap import AudienceOverlapDetectorTool


@pytest.mark.asyncio
async def test_partnership_agent_initialization():
    """Verify PartnershipAgent initializes with correct persona and tools."""
    assert PartnershipAgent is not None, "PartnershipAgent not implemented yet"
    with patch("agents.base.InferenceProvider.get_model") as mock_get_model:
        mock_get_model.return_value = MagicMock()

        agent = PartnershipAgent()
        assert agent.name == "PartnershipAgent"
        assert "Partnership & Affiliate Hunter" in agent.system_prompt
        assert any(tool.name == "audience_overlap_detector" for tool in agent.tools)


@pytest.mark.asyncio
async def test_audience_overlap_detector_tool():
    """Verify AudienceOverlapDetectorTool returns overlap data."""
    assert (
        AudienceOverlapDetectorTool is not None
    ), "AudienceOverlapDetectorTool not implemented yet"
    tool = AudienceOverlapDetectorTool()
    result = await tool._execute(
        workspace_id="test-ws", potential_partner="competitor-x"
    )

    assert result["success"] is True
    assert "overlap_percentage" in result
    assert "mutual_interests" in result
