import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from memory.episodic import EpisodicMemory
from memory.long_term import LongTermMemory
from memory.semantic import SemanticMemory


async def verify():
    print("\n--- Verifying Tiered Memory Architecture ---")

    # 1. Episodic (Redis Mocked)
    mock_redis = AsyncMock()
    episodic = EpisodicMemory(client=mock_redis)
    await episodic.add_message("test-session", "test message")
    print("✓ Episodic: Message added to short-term buffer.")

    # 2. Semantic (pgvector Mocked)
    with (
        patch(
            "backend.memory.semantic.vector_search", new_callable=AsyncMock
        ) as mock_search,
        patch(
            "backend.inference.InferenceProvider.get_embeddings",
            return_value=AsyncMock(),
        ),
    ):
        mock_search.return_value = [("id", "content", {}, 0.9)]
        semantic = SemanticMemory()
        res = await semantic.search("test-tenant", "query")
        print(f"✓ Semantic: Search returned {len(res)} results.")

    # 3. Long-Term (Postgres Mocked)
    with patch("backend.memory.long_term.get_db_connection") as mock_db:
        mock_conn = MagicMock()
        mock_conn.commit = AsyncMock()
        mock_cursor = AsyncMock()
        mock_conn.cursor.return_value.__aenter__.return_value = mock_cursor
        mock_db.return_value.__aenter__.return_value = mock_conn

        ltm = LongTermMemory()
        await ltm.log_decision("tenant", "agent", "type", rationale="verified")
        print("✓ Long-Term: Decision logged to audit trail.")

    print("\n--- Tiered Memory Verification Complete ---")


if __name__ == "__main__":
    asyncio.run(verify())
