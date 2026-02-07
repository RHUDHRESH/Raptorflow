from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from core.tool_registry import BaseRaptorTool


class FailingTool(BaseRaptorTool):
    @property
    def name(self):
        return "failing_tool"

    @property
    def description(self):
        return "Fails always"

    async def _execute(self, **kwargs):
        raise ValueError("Simulated Tool Failure")


@pytest.mark.asyncio
async def test_tool_error_catching():
    """
    Task 63: Write failing tests for Tool Sandbox execution and error catching.
    Tests that BaseRaptorTool catch exceptions in _execute.
    """
    tool = FailingTool()
    result = await tool.run()

    assert result["success"] is False
    assert "Simulated Tool Failure" in result["error"]
    assert result["latency_ms"] == 0


@pytest.mark.asyncio
async def test_toolbelt_missing_tool_handling():
    """
    Verify Toolbelt handles missing tools gracefully.
    """
    from core.toolbelt import ToolbeltV2

    belt = ToolbeltV2()
    result = await belt.run_tool("non_existent_tool")

    assert result["success"] is False
    assert "not found" in result["error"]
