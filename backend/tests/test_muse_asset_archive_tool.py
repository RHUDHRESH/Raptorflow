from unittest.mock import patch

import pytest

from agents.specialists.product_lead import ProductLeadAgent
from tools.muse_asset_archive import MuseAssetArchiveTool


@pytest.mark.asyncio
async def test_muse_asset_archive_tool_metadata():
    """Verify MuseAssetArchiveTool has correct metadata."""
    assert MuseAssetArchiveTool is not None, "MuseAssetArchiveTool not implemented yet"
    tool = MuseAssetArchiveTool()
    assert tool.name == "muse_asset_archive"
    assert "repurpose" in tool.description.lower()


@pytest.mark.asyncio
async def test_muse_asset_archive_tool_execution():
    """Verify MuseAssetArchiveTool returns assets."""
    assert MuseAssetArchiveTool is not None, "MuseAssetArchiveTool not implemented yet"
    tool = MuseAssetArchiveTool()
    result = await tool._execute(workspace_id="test-ws")

    assert result["success"] is True
    assert "assets" in result
    assert len(result["assets"]) > 0
    assert "demo" in result["assets"][0]["type"]


@pytest.mark.asyncio
async def test_product_lead_agent_has_muse_tool():
    """Verify ProductLeadAgent has access to MuseAssetArchiveTool."""
    with patch("agents.base.InferenceProvider.get_model"):
        agent = ProductLeadAgent()
        # This will also fail until we update the tool_integration.py
        assert any(
            tool.name == "muse_asset_archive" for tool in agent.tools
        ), "ProductLeadAgent missing muse_asset_archive tool"
