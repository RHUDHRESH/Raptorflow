import pytest

from tools.longitudinal_data import BlackboxLongitudinalDataTool


@pytest.mark.asyncio
async def test_longitudinal_data_tool_metadata():
    """Verify BlackboxLongitudinalDataTool has correct metadata."""
    assert (
        BlackboxLongitudinalDataTool is not None
    ), "BlackboxLongitudinalDataTool not implemented yet"
    tool = BlackboxLongitudinalDataTool()
    assert tool.name == "blackbox_longitudinal_data"
    assert "decay" in tool.description.lower()


@pytest.mark.asyncio
async def test_longitudinal_data_tool_execution():
    """Verify BlackboxLongitudinalDataTool returns decay analysis."""
    assert (
        BlackboxLongitudinalDataTool is not None
    ), "BlackboxLongitudinalDataTool not implemented yet"
    tool = BlackboxLongitudinalDataTool()
    result = await tool._execute(workspace_id="test-ws")

    assert result["success"] is True
    assert "decay_rate" in result
    assert "cohort_analysis" in result
    assert len(result["cohort_analysis"]) > 0
