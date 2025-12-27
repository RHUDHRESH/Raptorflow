import pytest

from tools.partnership_incentives import WinWinIncentiveTool


@pytest.mark.asyncio
async def test_win_win_incentive_tool_metadata():
    """Verify WinWinIncentiveTool has correct metadata."""
    assert WinWinIncentiveTool is not None, "WinWinIncentiveTool not implemented yet"
    tool = WinWinIncentiveTool()
    assert tool.name == "win_win_incentive_modeling"
    assert "incentive" in tool.description.lower()


@pytest.mark.asyncio
async def test_win_win_incentive_tool_execution():
    """Verify WinWinIncentiveTool returns modeling data."""
    assert WinWinIncentiveTool is not None, "WinWinIncentiveTool not implemented yet"
    tool = WinWinIncentiveTool()
    result = await tool._execute(
        workspace_id="test-ws",
        partner_name="Partner X",
        offer_value=1000,
    )

    assert result["success"] is True
    assert "proposed_incentives" in result
    assert len(result["proposed_incentives"]) > 0
    assert "win_win_score" in result
