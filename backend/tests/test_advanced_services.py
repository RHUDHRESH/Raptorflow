"""
Tests for Advanced Services - Semantic Memory, Language Engine, Performance Prediction, Meta-Learning, Agent Swarm
"""

import pytest
import asyncio
from backend.services.semantic_memory import semantic_memory, SemanticMemoryService
from backend.services.language_engine import language_engine, LanguageEngineService
from backend.services.performance_prediction import performance_predictor, PerformancePredictionService
from backend.services.meta_learning import meta_learner, MetaLearningService
from backend.services.agent_swarm import agent_swarm, AgentSwarmService


# ========== Semantic Memory Tests ==========

@pytest.mark.asyncio
async def test_semantic_memory_store_and_retrieve():
    """Test storing and retrieving context from semantic memory."""
    service = SemanticMemoryService(use_chromadb=False)  # Use in-memory for testing

    # Store context
    context_id = await service.store_context(
        workspace_id="test-workspace-1",
        context_type="icp",
        content="Target audience: B2B SaaS founders aged 30-45, focused on growth and scaling",
        metadata={"industry": "SaaS"},
        correlation_id="test-correlation-1"
    )

    assert context_id is not None
    assert "test-workspace-1" in context_id

    # Retrieve context with semantic search
    results = await service.retrieve_context(
        workspace_id="test-workspace-1",
        query="Who is our target audience?",
        context_type="icp",
        limit=5,
        correlation_id="test-correlation-1"
    )

    assert len(results) > 0
    assert results[0]["content"] == "Target audience: B2B SaaS founders aged 30-45, focused on growth and scaling"
    assert results[0]["context_type"] == "icp"


@pytest.mark.asyncio
async def test_semantic_memory_workspace_isolation():
    """Test that workspaces are isolated in semantic memory."""
    service = SemanticMemoryService(use_chromadb=False)

    # Store in workspace 1
    await service.store_context(
        workspace_id="workspace-1",
        context_type="strategy",
        content="Workspace 1 strategy content",
        correlation_id="test"
    )

    # Store in workspace 2
    await service.store_context(
        workspace_id="workspace-2",
        context_type="strategy",
        content="Workspace 2 strategy content",
        correlation_id="test"
    )

    # Retrieve from workspace 1
    results = await service.retrieve_context(
        workspace_id="workspace-1",
        query="strategy",
        limit=10,
        correlation_id="test"
    )

    # Should only get workspace 1 content
    assert len(results) == 1
    assert "Workspace 1" in results[0]["content"]


@pytest.mark.asyncio
async def test_semantic_memory_delete_workspace():
    """Test deleting all context for a workspace."""
    service = SemanticMemoryService(use_chromadb=False)

    # Store multiple contexts
    for i in range(3):
        await service.store_context(
            workspace_id="test-workspace-delete",
            context_type="test",
            content=f"Test content {i}",
            correlation_id="test"
        )

    # Delete workspace
    deleted_count = await service.delete_workspace_context(
        workspace_id="test-workspace-delete",
        correlation_id="test"
    )

    assert deleted_count == 3

    # Verify deletion
    results = await service.get_workspace_context(
        workspace_id="test-workspace-delete",
        correlation_id="test"
    )

    assert len(results) == 0


# ========== Language Engine Tests ==========

@pytest.mark.asyncio
async def test_language_engine_readability_analysis():
    """Test readability analysis."""
    service = LanguageEngineService()

    text = """
    This is a simple sentence. It is easy to read. The content is clear.
    Anyone can understand it. Short words work best.
    """

    result = await service.analyze_readability(text, correlation_id="test")

    assert "flesch_reading_ease" in result
    assert "flesch_kincaid_grade" in result
    assert "readability_level" in result
    assert result["flesch_reading_ease"] > 60  # Should be fairly readable
    assert result["sentences"] == 5
    assert result["words"] > 0


@pytest.mark.asyncio
async def test_language_engine_grammar_check():
    """Test grammar checking."""
    service = LanguageEngineService()

    text = "This is  a test with  double spaces."

    result = await service.check_grammar(text, correlation_id="test")

    assert "issues" in result
    assert "issue_count" in result
    assert result["language"] == "en-US"
    # Should detect double spaces
    assert result["issue_count"] > 0


@pytest.mark.asyncio
async def test_language_engine_tone_optimization():
    """Test tone analysis and optimization."""
    service = LanguageEngineService()

    casual_text = "Hey, we're gonna make this work! Yeah, it's gonna be awesome!"

    result = await service.optimize_tone(
        text=casual_text,
        target_tone="professional",
        correlation_id="test"
    )

    assert "suggestions" in result
    assert "tone_match_score" in result
    assert "current_tone_analysis" in result
    # Casual text shouldn't match professional tone well
    assert result["tone_match_score"] < 80


@pytest.mark.asyncio
async def test_language_engine_suggest_improvements():
    """Test comprehensive content analysis."""
    service = LanguageEngineService()

    text = """
    This is a test document. It has some content. The content is okay.
    We want to check the quality of this text and get suggestions for improvement.
    """

    result = await service.suggest_improvements(text, correlation_id="test")

    assert "grammar_check" in result
    assert "readability_analysis" in result
    assert "suggestions" in result
    assert "quality_score" in result
    assert 0 <= result["quality_score"] <= 100


# ========== Performance Prediction Tests ==========

@pytest.mark.asyncio
async def test_performance_prediction_insufficient_data():
    """Test prediction with insufficient historical data."""
    service = PerformancePredictionService()

    result = await service.predict_performance(
        workspace_id="new-workspace",
        content_type="blog",
        platform="linkedin",
        content_features={"word_count": 500, "has_media": True},
        correlation_id="test"
    )

    assert result["prediction_available"] is False
    assert result["reason"] == "insufficient_data"
    assert "min_required" in result


@pytest.mark.asyncio
async def test_performance_prediction_ab_test_suggestions():
    """Test A/B test configuration suggestions."""
    service = PerformancePredictionService()

    variants = [
        {
            "name": "Variant A",
            "content_type": "social_post",
            "platform": "linkedin",
            "features": {"word_count": 100, "has_media": True}
        },
        {
            "name": "Variant B",
            "content_type": "social_post",
            "platform": "linkedin",
            "features": {"word_count": 200, "has_media": False}
        }
    ]

    result = await service.suggest_ab_tests(
        workspace_id="test-workspace",
        content_variants=variants,
        correlation_id="test"
    )

    # Even with insufficient data, should return structure
    assert "variants" in result
    assert len(result["variants"]) == 2


# ========== Meta-Learning Tests ==========

@pytest.mark.asyncio
async def test_meta_learning_insufficient_samples():
    """Test meta-learning with insufficient data."""
    service = MetaLearningService()

    result = await service.learn_from_performance(
        workspace_id="new-workspace",
        time_period_days=90,
        correlation_id="test"
    )

    assert result["learning_available"] is False
    assert result["reason"] == "insufficient_data"
    assert "samples_needed" in result


@pytest.mark.asyncio
async def test_meta_learning_strategy_tracking():
    """Test strategy effectiveness tracking."""
    service = MetaLearningService()

    result = await service.track_strategy_effectiveness(
        workspace_id="test-workspace",
        strategy_id="test-strategy-123",
        correlation_id="test"
    )

    # Without published content, should indicate no data
    assert result["tracking_available"] is False
    assert result["reason"] == "no_published_content"


# ========== Agent Swarm Tests ==========

@pytest.mark.asyncio
async def test_agent_swarm_debate():
    """Test multi-agent debate functionality."""
    service = AgentSwarmService()

    result = await service.debate(
        topic="Should we focus on LinkedIn or Twitter for B2B marketing?",
        context={"description": "We're a B2B SaaS company targeting enterprise clients"},
        agent_roles=["conservative_marketer", "innovative_disruptor"],
        correlation_id="test"
    )

    assert "topic" in result
    assert "debate_rounds" in result
    assert "transcript" in result
    assert "consensus" in result
    assert len(result["agent_roles"]) == 2


@pytest.mark.asyncio
async def test_agent_swarm_collaborative_decision():
    """Test collaborative decision making."""
    service = AgentSwarmService()

    options = [
        {"name": "Option A", "description": "Post daily"},
        {"name": "Option B", "description": "Post 3x per week"}
    ]

    result = await service.collaborative_decision(
        decision_type="timing",
        options=options,
        context={"description": "Deciding posting frequency"},
        correlation_id="test"
    )

    assert "decision_type" in result
    assert "agent_votes" in result
    assert "winning_option" in result
    assert "option_scores" in result


@pytest.mark.asyncio
async def test_agent_swarm_synthesize_perspectives():
    """Test perspective synthesis."""
    service = AgentSwarmService()

    result = await service.synthesize_perspectives(
        question="What's the best way to grow our audience?",
        context={"description": "B2B SaaS startup"},
        perspective_count=3,
        correlation_id="test"
    )

    assert "perspectives" in result
    assert "synthesis" in result
    assert len(result["perspectives"]) <= 3
    assert result["perspective_count"] <= 3


# ========== Integration Tests ==========

@pytest.mark.asyncio
async def test_full_workflow_semantic_memory():
    """Test a full workflow using semantic memory."""
    service = SemanticMemoryService(use_chromadb=False)

    workspace_id = "integration-test-workspace"

    # Store ICP context
    icp_id = await service.store_context(
        workspace_id=workspace_id,
        context_type="icp",
        content="Target: Tech-savvy B2B buyers, 35-50 years old, decision makers",
        metadata={"source": "research"},
        correlation_id="integration-test"
    )

    # Store strategy context
    strategy_id = await service.store_context(
        workspace_id=workspace_id,
        context_type="strategy",
        content="Focus on LinkedIn thought leadership and case studies",
        metadata={"source": "strategy_session"},
        correlation_id="integration-test"
    )

    # Retrieve all contexts
    all_contexts = await service.get_workspace_context(
        workspace_id=workspace_id,
        correlation_id="integration-test"
    )

    assert len(all_contexts) == 2

    # Semantic search for ICP
    icp_results = await service.retrieve_context(
        workspace_id=workspace_id,
        query="Who should we target?",
        limit=5,
        correlation_id="integration-test"
    )

    assert len(icp_results) > 0
    assert any("decision makers" in r["content"] for r in icp_results)


@pytest.mark.asyncio
async def test_content_quality_workflow():
    """Test a full content quality workflow."""
    lang_service = LanguageEngineService()

    draft_content = """
    This blog post is about marketing automation. It helps companies save time.
    Marketing automation tools are useful. They can improve efficiency. Many businesses use them.
    """

    # Step 1: Check readability
    readability = await lang_service.analyze_readability(draft_content, correlation_id="test")
    assert readability["readability_level"] in ["very_easy", "easy", "fairly_easy"]

    # Step 2: Check grammar
    grammar = await lang_service.check_grammar(draft_content, correlation_id="test")
    assert "issues" in grammar

    # Step 3: Get full analysis
    analysis = await lang_service.suggest_improvements(draft_content, correlation_id="test")
    assert "quality_score" in analysis
    assert "suggestions" in analysis


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
