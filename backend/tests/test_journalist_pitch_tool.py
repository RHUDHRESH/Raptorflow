from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tools.journalist_pitch import JournalistPitchArchitectTool


@pytest.mark.asyncio
async def test_journalist_pitch_tool_uses_frameworks():
    """Verify that JournalistPitchArchitectTool can use narrative hook frameworks."""
    # Mock the LLM and its response
    mock_response = MagicMock()
    json_content = '{"subject": "Test", "intro": "Test", "hook": "Test", "cta": "Test", "newsworthiness_score": 0.9}'
    mock_response.content = json_content

    # Mock the LLM object
    mock_llm = MagicMock()

    with (
        patch("inference.InferenceProvider.get_model", return_value=mock_llm),
        patch(
            "langchain_core.prompts.ChatPromptTemplate.from_messages"
        ) as mock_prompt_init,
    ):

        # Mock the chain and its | operator
        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(return_value=mock_response)
        mock_prompt_init.return_value.__or__.return_value = mock_chain

        tool = JournalistPitchArchitectTool()

        result = await tool._execute(
            story_angle="AI-powered marketing OS",
            target_outlet="TechCrunch",
            framework="NARRATIVE_HOOK",
        )

        assert result["success"] is True
        assert result["framework_used"] == "Narrative Hook"
        assert result["pitch"]["subject"] == "Test"
        assert result["newsworthiness_score"] == 0.9
