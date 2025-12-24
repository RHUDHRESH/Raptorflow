from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from backend.services.blackbox_service import BlackboxService


@pytest.mark.asyncio
async def test_learning_flywheel_output():
    """
    Task 66: Verify that the learning flywheel produces structured strategic learnings.
    """
    mock_vault = MagicMock()
    mock_vault.project_id = "test-project"

    service = BlackboxService(mock_vault)
    move_id = str(uuid4())

    # 1. Mock the LangGraph run
    mock_final_state = {
        "findings": ["SOTA Finding: Early founders prefer LinkedIn for ROI."],
        "confidence": 0.95,
        "status": ["complete"],
    }

    with patch("backend.graphs.blackbox_analysis.create_blackbox_graph") as mock_create:
        mock_graph = AsyncMock()
        mock_graph.ainvoke.return_value = mock_final_state
        mock_create.return_value = mock_graph

        # 2. Mock service dependencies for persistence
        service.categorize_learning = MagicMock(return_value="strategic")
        service.upsert_learning_embedding = MagicMock()

        # 3. Trigger cycle
        result = await service.trigger_learning_cycle(move_id)

        # 4. Assertions
        assert result["status"] == "cycle_complete"
        assert result["findings_count"] == 1
        assert result["confidence"] == 0.95

        service.categorize_learning.assert_called_with(
            "SOTA Finding: Early founders prefer LinkedIn for ROI."
        )
        service.upsert_learning_embedding.assert_called()
