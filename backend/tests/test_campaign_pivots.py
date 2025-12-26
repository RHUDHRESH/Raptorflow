from unittest.mock import AsyncMock, MagicMock

import pytest

from agents.strategists import StrategyReplanner


@pytest.mark.asyncio
async def test_strategy_replanner_pivot():
    """Verify that StrategyReplanner triggers a pivot on low alignment."""
    mock_llm = MagicMock()
    mock_res = MagicMock()
    mock_res.content = "PIVOT: Focus more on luxury."
    mock_llm.ainvoke = AsyncMock(return_value=mock_res)

    replanner = StrategyReplanner(mock_llm)
    # Mock the chain directly since it's created in __init__
    replanner.chain = AsyncMock()
    replanner.chain.ainvoke.return_value = mock_res

    # Simulate low alignment score
    state = {"context_brief": {"brand_alignment": {"alignments": [{"score": 0.2}]}}}

    result = await replanner(state)

    assert result["next_node"] == "pivot"
    assert "luxury" in result["context_brief"]["pivot_instruction"]
    replanner.chain.ainvoke.assert_called_once()


@pytest.mark.asyncio
async def test_strategy_replanner_success():
    """Verify that StrategyReplanner proceeds on high alignment."""
    replanner = StrategyReplanner(MagicMock())

    # Simulate high alignment score
    state = {"context_brief": {"brand_alignment": {"alignments": [{"score": 0.9}]}}}

    result = await replanner(state)
    assert result["next_node"] == "finalize"
