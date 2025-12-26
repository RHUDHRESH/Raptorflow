from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from memory.compressor import ContextWindowCompressor


@pytest.mark.asyncio
async def test_compressor_no_compression_needed():
    """Verify that compressor returns original text if within limit."""
    compressor = ContextWindowCompressor(max_tokens=100)
    text = "Short text"
    compressed = await compressor.compress(text)
    assert compressed == text


@pytest.mark.asyncio
async def test_compressor_summarization_trigger():
    """Verify that compressor triggers summarization if text is too long."""
    with patch(
        "backend.memory.compressor.summarize_recursively", new_callable=AsyncMock
    ) as mock_summarize, patch(
        "backend.memory.compressor.InferenceProvider"
    ) as mock_inference:

        mock_summarize.return_value = "Summary"
        mock_inference.get_model.return_value = MagicMock()

        compressor = ContextWindowCompressor(max_tokens=5)  # Very small limit
        text = "This is a much longer text that definitely exceeds five tokens."
        compressed = await compressor.compress(text)

        assert compressed == "Summary"
        mock_summarize.assert_called_once()
