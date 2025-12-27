from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tools.product_marketing import BenefitToFeatureMapperTool


@pytest.mark.asyncio
async def test_benefit_to_feature_mapper_tool():
    """Verify that BenefitToFeatureMapperTool can map features to benefits."""
    # Mock the LLM and its response
    mock_response = MagicMock()
    json_content = (
        '{"mappings": [{"feature": "Automated SEO", '
        '"benefit": "Save 10 hours a week on content optimization"}]}'
    )
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

        tool = BenefitToFeatureMapperTool()

        result = await tool._execute(
            features=["Automated SEO"], target_persona="SaaS Founder"
        )

        assert result["success"] is True
        assert len(result["mappings"]) == 1
        assert result["mappings"][0]["feature"] == "Automated SEO"
        assert "Save 10 hours" in result["mappings"][0]["benefit"]
