from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.memory.checkpoint import StateCheckpointManager


@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset the StateCheckpointManager singleton before each test."""
    StateCheckpointManager._instance = None
    StateCheckpointManager._checkpointer = None


@pytest.mark.asyncio
async def test_checkpoint_manager_initialization():
    """Verify that StateCheckpointManager initializes the checkpointer."""
    with patch(
        "backend.memory.checkpoint.init_checkpointer", new_callable=AsyncMock
    ) as mock_init:
        mock_init.return_value = MagicMock()

        manager = StateCheckpointManager()
        checkpointer = await manager.get_checkpointer()

        assert checkpointer is not None
        mock_init.assert_called_once()


@pytest.mark.asyncio
async def test_checkpoint_manager_singleton():
    """Verify that StateCheckpointManager returns the same checkpointer instance."""
    with patch(
        "backend.memory.checkpoint.init_checkpointer", new_callable=AsyncMock
    ) as mock_init:
        mock_cp = MagicMock()
        mock_init.return_value = mock_cp

        manager = StateCheckpointManager()
        cp1 = await manager.get_checkpointer()
        cp2 = await manager.get_checkpointer()

        assert cp1 is cp2
        assert mock_init.call_count == 1
