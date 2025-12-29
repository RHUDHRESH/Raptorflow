import asyncio
import time
from unittest.mock import AsyncMock, patch

import pytest

from memory.semantic import SemanticMemory


@pytest.mark.asyncio
async def test_retrieval_latency_target():
    """Verify that semantic lookup meets the <150ms target."""
    mock_embedder = AsyncMock()
    mock_embedder.aembed_query.return_value = [0.1] * 768

    # Simulate a realistic 50ms DB response time
    async def slow_search(*args, **kwargs):
        await asyncio.sleep(0.05)
        return [("id", "content", {}, 0.9)]

    with (
        patch(
            "backend.inference.InferenceProvider.get_embeddings",
            return_value=mock_embedder,
        ),
        patch("backend.memory.semantic.vector_search", side_effect=slow_search),
    ):

        memory = SemanticMemory()

        start_time = time.perf_counter()
        await memory.search("test-tenant", "query")
        end_time = time.perf_counter()

        latency_ms = (end_time - start_time) * 1000
        print(f"\nDEBUG: Semantic Retrieval Latency: {latency_ms:.2f}ms")

        # Target: < 150ms
        assert latency_ms < 150
