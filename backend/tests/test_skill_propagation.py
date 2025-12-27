from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from langchain_core.messages import SystemMessage

from agents.specialists.brand_philosopher import BrandPhilosopherAgent
from models.cognitive import AgentMessage


@pytest.mark.asyncio
@patch("agents.base.get_swarm_memory_coordinator")
@patch("inference.InferenceProvider.get_model")
@patch("agents.base.fetch_heuristics")
async def test_skill_propagation(m_fetch, m_get_model, m_get_memory):
    # Setup mocks
    mock_memory = MagicMock()
    mock_memory.initialize_agent_memory = AsyncMock()
    mock_memory.record_agent_memory = AsyncMock()
    m_get_memory.return_value = mock_memory

    mock_llm = MagicMock()
    mock_llm.bind_tools.return_value = AsyncMock()
    mock_llm.with_structured_output.return_value = AsyncMock()
    m_get_model.return_value = mock_llm

    # Mock heuristics in DB
    m_fetch.return_value = {
        "never_rules": ["Never use emojis"],
        "always_rules": ["Always use formal tone"],
    }

    agent = BrandPhilosopherAgent()

    state = {
        "workspace_id": "ws_123",
        "messages": [AgentMessage(role="human", content="Hello")],
    }

    # Mock LLM response
    mock_res = MagicMock()
    mock_res.content = "Response"
    mock_res.response_metadata = {}
    agent.llm_with_tools.ainvoke = AsyncMock(return_value=mock_res)

    await agent(state)

    # Verify that heuristics were injected into the call to LLM
    call_args = agent.llm_with_tools.ainvoke.call_args
    messages = call_args[0][0]

    system_msg = messages[0]
    assert isinstance(system_msg, SystemMessage)
    assert "# NEVER RULES:" in system_msg.content
    assert "- Never use emojis" in system_msg.content
    assert "# ALWAYS RULES:" in system_msg.content
    assert "- Always use formal tone" in system_msg.content
