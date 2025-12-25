from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.agents.matrix_agents import SkillSelectorAgent
from backend.core.tool_registry import MatrixSkill
from backend.skills.matrix_skills import SkillRegistry


class MockSkill(MatrixSkill):
    @property
    def name(self) -> str:
        return "mock_skill"

    async def execute(self, params: dict) -> dict:
        return {"status": "executed"}


@pytest.fixture
def mock_llm():
    mock = MagicMock()
    mock_runnable = MagicMock()
    mock_runnable.ainvoke = AsyncMock()
    # Mocking the pipe operator behavior if needed,
    # but LangChain handles MagicMock if it has ainvoke and is not a coroutine.
    mock.with_structured_output.return_value = mock_runnable
    return mock


@pytest.fixture
def registry():
    reg = SkillRegistry()
    # Clear for tests
    reg._skills = {}
    reg.register(MockSkill())

    # Register real-sounding mock skills
    halt = MagicMock()
    halt.name = "emergency_halt"
    reg.register(halt)

    scale = MagicMock()
    scale.name = "resource_scaling"
    reg.register(scale)

    return reg


@pytest.mark.asyncio
async def test_skill_selector_pick_best_tool(mock_llm, registry):
    """Test that SkillSelectorAgent uses LLM to pick the right skill."""
    from backend.agents.matrix_agents import SkillSelection

    # Mock LLM output
    val = SkillSelection(
        skill_name="emergency_halt",
        reasoning="The user wants to stop everything immediately.",
    )
    mock_llm.with_structured_output.return_value.ainvoke.return_value = val
    mock_llm.with_structured_output.return_value.return_value = val

    agent = SkillSelectorAgent(llm=mock_llm, registry=registry)

    result = await agent.pick_best_tool("STOP EVERYTHING NOW!")

    assert result["skill_name"] == "emergency_halt"
    assert (
        "emergency_halt" in result["reasoning"].lower()
        or "stop" in result["reasoning"].lower()
    )


@pytest.mark.asyncio
async def test_skill_selector_pick_best_tool_scaling(mock_llm, registry):
    """Test picking a different skill."""
    from backend.agents.matrix_agents import SkillSelection

    val = SkillSelection(
        skill_name="resource_scaling", reasoning="The user wants to increase capacity."
    )
    mock_llm.with_structured_output.return_value.ainvoke.return_value = val
    mock_llm.with_structured_output.return_value.return_value = val

    agent = SkillSelectorAgent(llm=mock_llm, registry=registry)

    result = await agent.pick_best_tool("We need more power for the spine service.")

    assert result["skill_name"] == "resource_scaling"


@pytest.mark.asyncio
async def test_skill_selector_unsupported_intent(mock_llm, registry):
    """Test when no skill matches the intent."""
    from backend.agents.matrix_agents import SkillSelection

    val = SkillSelection(skill_name="none", reasoning="No relevant skill found.")
    mock_llm.with_structured_output.return_value.ainvoke.return_value = val
    mock_llm.with_structured_output.return_value.return_value = val

    agent = SkillSelectorAgent(llm=mock_llm, registry=registry)

    result = await agent.pick_best_tool("What is the weather today?")

    assert result["skill_name"] == "none"
