from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.agents.base import BaseCognitiveAgent
from backend.models.cognitive import AgentMessage, CognitiveIntelligenceState


class ConcreteAgent(BaseCognitiveAgent):
    def __init__(self, llm):
        super().__init__(
            name="TestAgent",
            role="strategist",
            system_prompt="You are a test agent.",
            model_tier="driver",
        )
        self.llm = llm
        self.llm_with_tools = llm  # Simplified for test


@pytest.mark.asyncio
async def test_base_agent_execution():
    """
    Phase 31: Verify base agent formatting and execution.
    """
    mock_llm = AsyncMock()
    mock_llm.ainvoke.return_value = MagicMock(content="Test response")

    with patch("backend.agents.base.InferenceProvider") as mock_inference:
        mock_inference.get_model.return_value = mock_llm

        agent = ConcreteAgent(mock_llm)
        state: CognitiveIntelligenceState = {
            "tenant_id": "test-tenant",
            "messages": [AgentMessage(role="human", content="Hello")],
            "raw_prompt": "Hello",
        }

        result = await agent(state)

        assert result["last_agent"] == "TestAgent"
        assert result["messages"][0].content == "Test response"
        assert result["messages"][0].role == "strategist"

        # Verify LC messages were formatted
        args, _ = mock_llm.ainvoke.call_args
        messages = args[0]
        assert messages[0].content == "You are a test agent."
        assert messages[1].content == "Hello"
