from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from core.validation import ResearchValidator, ValidationResult


@pytest.mark.asyncio
async def test_research_validator_rejects_fluff():
    """
    Phase 17: Verify that the validator flags low-density content.
    """
    low_quality_content = "Marketing is very important..."

    mock_chain = AsyncMock()
    mock_chain.ainvoke.return_value = ValidationResult(
        is_high_quality=False,
        score=0.3,
        issues=["Too generic"],
        improvement_suggestions=[],
    )

    with patch("backend.core.validation.InferenceProvider"):
        validator = ResearchValidator()
        with patch.object(validator, "chain", mock_chain):
            result = await validator.validate_content(low_quality_content)

    assert result["is_high_quality"] is False
    assert result["score"] == 0.3


@pytest.mark.asyncio
async def test_research_validator_passes_dense_content():
    high_quality_content = "Competitor X pricing is $49/mo..."

    mock_chain = AsyncMock()
    mock_chain.ainvoke.return_value = ValidationResult(
        is_high_quality=True, score=0.95, issues=[], improvement_suggestions=[]
    )

    with patch("backend.core.validation.InferenceProvider"):
        validator = ResearchValidator()
        with patch.object(validator, "chain", mock_chain):
            result = await validator.validate_content(high_quality_content)

    assert result["is_high_quality"] is True
    assert result["score"] == 0.95
