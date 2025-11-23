"""
Unit tests for ABTestOrchestrator.
"""

import pytest
from backend.performance.ab_test_orchestrator import ABTestOrchestrator


@pytest.fixture
def orchestrator():
    """Create AB test orchestrator instance."""
    return ABTestOrchestrator()


@pytest.mark.asyncio
async def test_create_test_basic(orchestrator):
    """Test basic A/B test creation."""
    base_content = "Discover how to improve your marketing results with proven strategies."

    result = await orchestrator.create_test(
        base_content=base_content,
        content_type="social_post",
        platform="linkedin",
        workspace_id="test-workspace",
        num_variants=3
    )

    assert "test_id" in result
    assert "variants" in result
    assert "recommended_variants" in result
    assert "test_configuration" in result
    assert "expected_winner" in result
    assert len(result["variants"]) <= 3


@pytest.mark.asyncio
async def test_variant_generation(orchestrator):
    """Test content variant generation."""
    base_content = "Learn marketing strategies"

    variants = await orchestrator._generate_variants(
        base_content=base_content,
        content_type="email",
        platform="email",
        num_variants=4,
        strategies=["baseline", "emotional", "conversion", "viral"]
    )

    assert len(variants) == 4
    assert any(v["strategy"] == "baseline" for v in variants)
    assert any(v["strategy"] == "emotional" for v in variants)
    assert any(v["strategy"] == "conversion" for v in variants)
    assert any(v["strategy"] == "viral" for v in variants)


def test_emotional_variant_creation(orchestrator):
    """Test emotional variant creation."""
    base_content = "Our product helps you work faster."

    emotional_variant = orchestrator._create_emotional_variant(base_content)

    assert len(emotional_variant) > len(base_content)
    # Should add emotional hook


def test_conversion_variant_creation(orchestrator):
    """Test conversion variant creation."""
    base_content = "Check out our product features."

    conversion_variant = orchestrator._create_conversion_variant(base_content)

    # Should have stronger CTA
    assert len(conversion_variant) >= len(base_content)


def test_viral_variant_creation(orchestrator):
    """Test viral variant creation."""
    base_content = "Product information"

    viral_variant = orchestrator._create_viral_variant(base_content)

    # Should add viral elements
    assert len(viral_variant) >= len(base_content)


def test_concise_variant_creation(orchestrator):
    """Test concise variant creation."""
    base_content = " ".join(["word"] * 100)

    concise_variant = orchestrator._create_concise_variant(base_content)

    # Should be shorter
    assert len(concise_variant.split()) < len(base_content.split())


@pytest.mark.asyncio
async def test_variant_prediction(orchestrator):
    """Test prediction on variants."""
    variants = [
        {"variant_id": "v1", "strategy": "baseline", "content": "Test content", "description": "Test"}
    ]

    predictions = await orchestrator._predict_variant_performance(
        variants=variants,
        content_type="social_post",
        platform="linkedin",
        workspace_id="test-workspace",
        objective="engagement"
    )

    assert len(predictions) == 1
    assert "composite_score" in predictions[0]
    assert "engagement_prediction" in predictions[0]
    assert "conversion_analysis" in predictions[0]
    assert "viral_score" in predictions[0]


def test_composite_score_calculation(orchestrator):
    """Test composite score calculation."""
    engagement_pred = {"confidence_level": 0.8}
    conversion_analysis = {"conversion_score": 0.7}
    viral_score = {"viral_score": 0.6}

    engagement_score = orchestrator._calculate_composite_score(
        engagement_pred, conversion_analysis, viral_score, "engagement"
    )

    conversion_score = orchestrator._calculate_composite_score(
        engagement_pred, conversion_analysis, viral_score, "conversion"
    )

    viral_composite = orchestrator._calculate_composite_score(
        engagement_pred, conversion_analysis, viral_score, "viral"
    )

    assert 0.0 <= engagement_score <= 1.0
    assert 0.0 <= conversion_score <= 1.0
    assert 0.0 <= viral_composite <= 1.0


def test_top_candidate_selection(orchestrator):
    """Test selection of top candidates."""
    variants = [
        {"variant_id": "baseline", "strategy": "baseline", "composite_score": 0.6},
        {"variant_id": "v1", "strategy": "emotional", "composite_score": 0.8},
        {"variant_id": "v2", "strategy": "viral", "composite_score": 0.7},
        {"variant_id": "v3", "strategy": "conversion", "composite_score": 0.5}
    ]

    top_candidates = orchestrator._select_top_candidates(variants, "engagement", max_variants=2)

    assert len(top_candidates) == 2
    # Should include baseline if present
    assert any(v["variant_id"] == "baseline" for v in top_candidates)


def test_expected_winner_identification(orchestrator):
    """Test expected winner identification."""
    variants = [
        {"variant_id": "v1", "strategy": "emotional", "composite_score": 0.9},
        {"variant_id": "v2", "strategy": "baseline", "composite_score": 0.5}
    ]

    winner = orchestrator._identify_expected_winner(variants, "engagement")

    assert winner["variant_id"] == "v1"
    assert winner["confidence"] == "high"


def test_traffic_split_calculation(orchestrator):
    """Test traffic split calculation."""
    split_2 = orchestrator._calculate_traffic_split(2)
    split_3 = orchestrator._calculate_traffic_split(3)

    assert len(split_2) == 2
    assert len(split_3) == 3
    assert sum(split_2.values()) == pytest.approx(1.0, 0.01)
    assert sum(split_3.values()) == pytest.approx(1.0, 0.01)


def test_monitoring_metrics_definition(orchestrator):
    """Test monitoring metrics definition."""
    engagement_metrics = orchestrator._define_monitoring_metrics("engagement")
    conversion_metrics = orchestrator._define_monitoring_metrics("conversion")
    viral_metrics = orchestrator._define_monitoring_metrics("viral")

    assert "engagement_rate" in engagement_metrics
    assert "conversion_rate" in conversion_metrics
    assert "shares" in viral_metrics
    assert "impressions" in engagement_metrics  # Base metric


def test_current_leader_calculation(orchestrator):
    """Test current leader calculation."""
    results = [
        {"variant_id": "v1", "metrics": {"engagement_rate": 0.05}},
        {"variant_id": "v2", "metrics": {"engagement_rate": 0.08}},
        {"variant_id": "v3", "metrics": {"engagement_rate": 0.03}}
    ]

    leader = orchestrator._calculate_current_leader(results, "engagement")

    assert leader["variant_id"] == "v2"
    assert leader["score"] == 0.08


def test_should_end_test(orchestrator):
    """Test test end determination."""
    from datetime import datetime, timedelta, timezone

    # Test with time-based end
    past_test = {
        "end_time": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
    }

    future_test = {
        "end_time": (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat()
    }

    results_low_sample = [
        {"variant_id": "v1", "metrics": {"impressions": 100}}
    ]

    results_high_sample = [
        {"variant_id": "v1", "metrics": {"impressions": 5000}}
    ]

    assert orchestrator._should_end_test(past_test, results_low_sample) is True
    assert orchestrator._should_end_test(future_test, results_high_sample) is True
    assert orchestrator._should_end_test(future_test, results_low_sample) is False
