import pytest

from tools.milestone_messaging import MilestoneMessagingTool


@pytest.mark.asyncio
async def test_milestone_messaging_tool_metadata():
    """Verify MilestoneMessagingTool has correct metadata."""
    assert (
        MilestoneMessagingTool is not None
    ), "MilestoneMessagingTool not implemented yet"
    tool = MilestoneMessagingTool()
    assert tool.name == "milestone_based_messaging"
    assert "milestone" in tool.description.lower()


@pytest.mark.asyncio
async def test_milestone_messaging_tool_execution():
    """Verify MilestoneMessagingTool returns messaging data."""
    assert (
        MilestoneMessagingTool is not None
    ), "MilestoneMessagingTool not implemented yet"
    tool = MilestoneMessagingTool()
    result = await tool._execute(
        workspace_id="test-ws",
        user_milestone="100th_execution",
    )

    assert result["success"] is True
    assert "messages" in result
    assert len(result["messages"]) > 0
    assert "celebration" in result["messages"][0]["tone"]
