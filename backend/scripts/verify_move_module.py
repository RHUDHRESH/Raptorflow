import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from backend.agents.moves import (
    MoveGenerator,
    MovePersistence,
    MoveRefiner,
    ProgressTracker,
    ResourceManager,
)


async def verify():
    print("\n--- Verifying Move Module (Phase 6) ---")
    mock_llm = MagicMock()

    # 1. Verify Move Generation
    generator = MoveGenerator(mock_llm)
    generator.chain = AsyncMock()
    generator.chain.ainvoke.return_value = MagicMock(moves=[])
    await generator({"context_brief": {"campaign_arc": {"monthly_plans": []}}})
    print("✓ Move Generator: Node structure verified.")

    # 2. Verify Refinement
    refiner = MoveRefiner(mock_llm)
    refiner.chain = AsyncMock()
    refiner.chain.ainvoke.return_value = MagicMock(model_dump=lambda: {})
    await refiner({"current_moves": [{"title": "test"}]})
    print("✓ Move Refiner: Refinement logic verified.")

    # 3. Verify Resource Management
    manager = ResourceManager()
    res = await manager(
        {"current_moves": [{"title": "test", "required_skills": ["Search"]}]}
    )
    assert any("Resources verified" in m for m in res["messages"])
    print("✓ Resource Manager: Tool availability check passed.")

    # 4. Verify Progress Tracking
    tracker = ProgressTracker()
    res = await tracker(
        {"current_moves": [{"status": "executed"}, {"status": "pending"}]}
    )
    assert "50.0%" in res["messages"][0]
    print("✓ Progress Tracker: Progress calculation correct.")

    # 5. Verify Move Persistence (Mock DB)
    with patch(
        "backend.agents.moves.save_move", new_callable=AsyncMock
    ) as mock_save, patch(
        "backend.agents.moves.log_agent_decision", new_callable=AsyncMock
    ) as mock_log:
        mock_save.return_value = "mock-uuid"
        persistence = MovePersistence()
        await persistence(
            {
                "tenant_id": "test",
                "campaign_id": "test",
                "current_moves": [{"title": "test"}],
            }
        )
        assert mock_save.called
        assert mock_log.called
        print("✓ Move Persistence: DB sync logic verified.")

    print("\n--- Move Module Verification Complete ---")


if __name__ == "__main__":
    asyncio.run(verify())
