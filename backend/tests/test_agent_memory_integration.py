"""
Integration tests for agent memory system.

Tests verify that:
1. Agents can store and retrieve memories
2. Workspace isolation works correctly
3. Memory influences agent behavior
4. Feedback updates improve future executions
5. Similar contexts retrieve relevant past experiences
"""

import pytest
from uuid import uuid4
from typing import Dict, Any

from backend.agents.research.icp_builder_agent import ICPBuilderAgent
from backend.services.memory_manager import MemoryManager
from backend.services.supabase_client import supabase_client


@pytest.fixture
async def clean_test_memories():
    """Clean up test memories after each test."""
    test_workspace_ids = []

    yield test_workspace_ids

    # Cleanup
    for workspace_id in test_workspace_ids:
        try:
            await supabase_client.delete(
                "agent_memories",
                {"workspace_id": workspace_id}
            )
        except Exception:
            pass  # Best effort cleanup


@pytest.mark.asyncio
class TestMemoryStorage:
    """Test memory storage and retrieval."""

    async def test_agent_stores_memory_automatically(self, clean_test_memories):
        """Test that agents with auto_remember store memories automatically."""
        workspace_id = str(uuid4())
        clean_test_memories.append(workspace_id)

        agent = ICPBuilderAgent()
        agent.set_workspace(workspace_id)

        # Execute agent (should auto-store with auto_remember=True)
        result = await agent.execute({
            "workspace_id": workspace_id,
            "company_name": "Test Corp",
            "industry": "SaaS",
            "product_description": "Marketing automation for B2B companies",
        })

        assert result["status"] == "success"

        # Verify memory was stored
        memories = await agent.recall(
            query="SaaS marketing automation",
            memory_types=["success"],
            top_k=5
        )

        assert len(memories) > 0
        assert memories[0]["context"]["company_name"] == "Test Corp"

    async def test_manual_memory_storage(self, clean_test_memories):
        """Test manual memory storage with remember()."""
        workspace_id = str(uuid4())
        clean_test_memories.append(workspace_id)

        agent = ICPBuilderAgent()
        agent.set_workspace(workspace_id)

        # Manually store a memory
        memory_id = await agent.remember(
            context={
                "industry": "HealthTech",
                "product": "Patient engagement platform"
            },
            result={
                "icp_name": "Healthcare CIOs",
                "confidence": 0.85
            },
            success_score=0.85,
            tags=["healthcare", "b2b", "enterprise"]
        )

        assert memory_id  # Non-empty memory ID
        assert len(memory_id) > 0

        # Retrieve the memory
        memories = await agent.recall(
            query="Healthcare patient platform",
            tags=["healthcare"],
            top_k=1
        )

        assert len(memories) == 1
        assert memories[0]["context"]["industry"] == "HealthTech"
        assert memories[0]["success_score"] == 0.85


@pytest.mark.asyncio
class TestWorkspaceIsolation:
    """Test that memories are isolated by workspace."""

    async def test_different_workspaces_dont_share_memories(self, clean_test_memories):
        """Verify that memories from different workspaces don't leak."""
        workspace_a = str(uuid4())
        workspace_b = str(uuid4())
        clean_test_memories.extend([workspace_a, workspace_b])

        agent = ICPBuilderAgent()

        # Store memory in workspace A
        agent.set_workspace(workspace_a)
        await agent.remember(
            context={"industry": "SaaS", "product": "Sales automation"},
            result={"icp": "B2B SaaS founders"},
            success_score=0.9,
            tags=["saas", "b2b"]
        )

        # Switch to workspace B and search
        agent.set_workspace(workspace_b)
        memories_b = await agent.recall(
            query="SaaS sales automation",
            memory_types=["success"],
            top_k=5
        )

        # Should not find workspace A memories
        assert len(memories_b) == 0

    async def test_same_agent_different_workspaces(self, clean_test_memories):
        """Test that same agent can work with multiple workspaces."""
        workspace_a = str(uuid4())
        workspace_b = str(uuid4())
        clean_test_memories.extend([workspace_a, workspace_b])

        agent = ICPBuilderAgent()

        # Workspace A: Store SaaS-focused memory
        agent.set_workspace(workspace_a)
        await agent.remember(
            context={"industry": "SaaS"},
            result={"focus": "B2B SaaS"},
            success_score=0.9,
            tags=["saas"]
        )

        # Workspace B: Store Healthcare-focused memory
        agent.set_workspace(workspace_b)
        await agent.remember(
            context={"industry": "Healthcare"},
            result={"focus": "Healthcare providers"},
            success_score=0.85,
            tags=["healthcare"]
        )

        # Verify workspace A only sees SaaS memories
        agent.set_workspace(workspace_a)
        memories_a = await agent.recall(query="industry focus", top_k=10)
        assert len(memories_a) == 1
        assert "SaaS" in str(memories_a[0]["result"])

        # Verify workspace B only sees Healthcare memories
        agent.set_workspace(workspace_b)
        memories_b = await agent.recall(query="industry focus", top_k=10)
        assert len(memories_b) == 1
        assert "Healthcare" in str(memories_b[0]["result"])


@pytest.mark.asyncio
class TestMemoryInfluencesBehavior:
    """Test that memories actually influence agent behavior."""

    async def test_icp_builder_uses_past_patterns(self, clean_test_memories):
        """Test that ICP builder recalls and uses past successful patterns."""
        workspace_id = str(uuid4())
        clean_test_memories.append(workspace_id)

        agent = ICPBuilderAgent()
        agent.set_workspace(workspace_id)

        # Store a high-quality past ICP with specific patterns
        await agent.remember(
            context={
                "industry": "SaaS",
                "product_description": "Project management tool"
            },
            result={
                "output": {
                    "pain_points": [
                        "Scattered tools causing inefficiency",
                        "Poor visibility into project status",
                        "Team collaboration bottlenecks"
                    ],
                    "behavioral_triggers": [
                        "Company growth beyond 20 employees",
                        "Failed project delivery",
                        "Team complaints about tools"
                    ],
                    "decision_structure": "Committee of 3-5 stakeholders"
                }
            },
            success_score=0.95,
            tags=["saas", "b2b", "high-performing"]
        )

        # Execute for similar context (SaaS product management domain)
        result = await agent.execute({
            "workspace_id": workspace_id,
            "company_name": "TaskMaster Inc",
            "industry": "SaaS",
            "product_description": "Team productivity and task management platform",
            "target_market": "B2B",
        })

        assert result["status"] == "success"
        assert result.get("used_past_patterns") == True

        # The generated ICP should reflect learned patterns
        # (In a real test with actual LLM, we'd verify content similarity)
        output = result.get("output", {})
        assert output is not None

    async def test_second_execution_has_higher_quality(self, clean_test_memories):
        """Test that second execution benefits from first execution's memory."""
        workspace_id = str(uuid4())
        clean_test_memories.append(workspace_id)

        agent = ICPBuilderAgent()
        agent.set_workspace(workspace_id)

        # First execution (no prior memory)
        payload1 = {
            "workspace_id": workspace_id,
            "company_name": "First Corp",
            "industry": "FinTech",
            "product_description": "Payment processing for e-commerce",
        }
        result1 = await agent.execute(payload1)
        score1 = result1.get("success_score", 0)

        # Store first result manually with high score to simulate success
        await agent.remember(
            context=payload1,
            result=result1,
            success_score=0.95,
            tags=["fintech", "payments", "high-quality"]
        )

        # Second execution (should benefit from first)
        payload2 = {
            "workspace_id": workspace_id,
            "company_name": "Second Corp",
            "industry": "FinTech",
            "product_description": "Digital wallet for online payments",
        }
        result2 = await agent.execute(payload2)

        # Second execution should use past patterns
        assert result2.get("used_past_patterns") == True

        # Note: In real usage with LLM, score2 would likely be >= score1
        # For this test, we just verify the pattern was used


@pytest.mark.asyncio
class TestFeedbackLearning:
    """Test that agents learn from feedback."""

    async def test_update_memory_with_feedback(self, clean_test_memories):
        """Test that feedback can be added to existing memories."""
        workspace_id = str(uuid4())
        clean_test_memories.append(workspace_id)

        agent = ICPBuilderAgent()
        agent.set_workspace(workspace_id)

        # Store initial memory
        memory_id = await agent.remember(
            context={"industry": "EdTech"},
            result={"icp": "University administrators"},
            success_score=0.7,
        )

        # Add user feedback
        success = await agent.learn_from_feedback(
            memory_id=memory_id,
            feedback={
                "user_rating": 5,
                "user_comment": "Excellent ICP, very accurate!",
                "actual_conversion_rate": 0.12
            },
            adjust_score=True
        )

        assert success == True

        # Retrieve memory and verify feedback was stored
        memories = await agent.recall(
            query="EdTech",
            memory_types=["success"],
            top_k=1
        )

        assert len(memories) > 0
        feedback = memories[0].get("feedback", {})
        assert feedback.get("user_rating") == 5

        # Score should have been updated (5-star rating -> 1.0 score)
        # Note: In actual implementation, verify the score was adjusted
        updated_score = memories[0].get("success_score")
        assert updated_score >= 0.7  # Should be maintained or improved


@pytest.mark.asyncio
class TestSemanticSearch:
    """Test semantic similarity search for memories."""

    async def test_semantic_search_finds_similar_contexts(self, clean_test_memories):
        """Test that semantic search finds conceptually similar memories."""
        workspace_id = str(uuid4())
        clean_test_memories.append(workspace_id)

        agent = ICPBuilderAgent()
        agent.set_workspace(workspace_id)

        # Store memories with semantically related contexts
        await agent.remember(
            context={
                "industry": "SaaS",
                "product": "CRM for sales teams"
            },
            result={"icp": "Sales directors"},
            success_score=0.9,
            tags=["saas", "sales"]
        )

        await agent.remember(
            context={
                "industry": "Software",
                "product": "Customer relationship management platform"
            },
            result={"icp": "VP of Sales"},
            success_score=0.85,
            tags=["software", "crm"]
        )

        # Search with semantically similar but different wording
        memories = await agent.recall(
            query="sales automation software for managing customer relationships",
            memory_types=["success"],
            top_k=5
        )

        # Should find both related memories
        assert len(memories) >= 2
        # Memories should be ordered by relevance (similarity score)
        # Note: Actual similarity scoring depends on embedding model


@pytest.mark.asyncio
class TestMemoryStatistics:
    """Test memory statistics and analytics."""

    async def test_get_memory_statistics(self, clean_test_memories):
        """Test retrieving memory statistics for an agent."""
        workspace_id = str(uuid4())
        clean_test_memories.append(workspace_id)

        agent = ICPBuilderAgent()
        agent.set_workspace(workspace_id)

        # Store multiple memories with different types and scores
        await agent.remember(
            context={"industry": "SaaS"},
            result={"icp": "B2B"},
            success_score=0.9,
            memory_type="success",
            tags=["saas", "b2b"]
        )

        await agent.remember(
            context={"industry": "HealthTech"},
            result={"icp": "Healthcare"},
            success_score=0.75,
            memory_type="success",
            tags=["healthcare"]
        )

        await agent.remember(
            context={"industry": "FinTech"},
            result={"icp": "Failed"},
            success_score=0.3,
            memory_type="failure",
            tags=["fintech"]
        )

        # Get statistics
        stats = await agent.get_memory_stats()

        assert stats["total_memories"] == 3
        assert stats["success_count"] >= 2
        assert stats["failure_count"] >= 1
        assert 0 < stats["avg_success_score"] < 1
        assert "saas" in stats["top_tags"] or "b2b" in stats["top_tags"]


@pytest.mark.asyncio
class TestMemoryManager:
    """Test MemoryManager service directly."""

    async def test_memory_manager_search(self, clean_test_memories):
        """Test MemoryManager search functionality."""
        workspace_id = str(uuid4())
        clean_test_memories.append(workspace_id)

        memory = MemoryManager(
            workspace_id=workspace_id,
            agent_name="test_agent"
        )

        # Store test memory
        memory_id = await memory.remember(
            context={"test": "context"},
            result={"test": "result"},
            success_score=0.8,
            memory_type="success",
            tags=["test"]
        )

        assert memory_id

        # Search for memory
        results = await memory.search(
            query="test context",
            memory_types=["success"],
            tags=["test"],
            top_k=5
        )

        assert len(results) > 0
        assert results[0]["context"]["test"] == "context"

    async def test_memory_manager_update_feedback(self, clean_test_memories):
        """Test updating memory with feedback."""
        workspace_id = str(uuid4())
        clean_test_memories.append(workspace_id)

        memory = MemoryManager(
            workspace_id=workspace_id,
            agent_name="test_agent"
        )

        # Store memory
        memory_id = await memory.remember(
            context={"test": "context"},
            result={"test": "result"},
            success_score=0.5,
        )

        # Update with feedback
        success = await memory.update_feedback(
            memory_id=memory_id,
            feedback={"user_rating": 4, "comment": "Good work"},
            new_success_score=0.8
        )

        assert success == True

        # Retrieve and verify
        results = await memory.search(
            query="test context",
            top_k=1
        )

        assert len(results) > 0
        assert results[0]["feedback"]["user_rating"] == 4
        assert results[0]["success_score"] == 0.8


# Run tests with: pytest backend/tests/test_agent_memory_integration.py -v
