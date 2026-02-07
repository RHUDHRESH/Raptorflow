from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agents.specialists.researcher import ResearcherAgent


def test_researcher_agent_tool_binding():
    """
    Phase 49: Verify that ResearcherAgent has search tools bound.
    """
    with patch("backend.agents.base.InferenceProvider"):
        with patch("backend.tools.search.TavilyMultiHopTool") as mock_tool:
            # Mock the name property on the tool instance
            mock_tool_instance = mock_tool.return_value
            mock_tool_instance.name = "tavily_search"

            agent = ResearcherAgent()
            assert len(agent.tools) > 0
            assert any("tavily_search" in t.name.lower() for t in agent.tools)
