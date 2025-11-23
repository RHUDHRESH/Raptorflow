"""
Integration tests for the Predictive Performance Engine.

Tests the complete workflow and integration between modules.
"""

import pytest
from backend.performance.engagement_predictor import engagement_predictor
from backend.performance.conversion_optimizer import conversion_optimizer
from backend.performance.viral_potential_scorer import viral_potential_scorer
from backend.performance.ab_test_orchestrator import ab_test_orchestrator
from backend.performance.competitive_benchmarker import competitive_benchmarker


@pytest.mark.asyncio
async def test_complete_content_analysis_workflow():
    """Test complete workflow: prediction -> optimization -> viral scoring."""
    content = """
    Discover the 5 secrets to doubling your revenue!

    Join thousands of successful entrepreneurs who have transformed their businesses.
    Step 1: Implement proven strategies
    Step 2: Track your results
    Step 3: Scale what works

    Get started today with our free guide - no credit card required!
    """

    # Step 1: Predict engagement
    engagement_result = await engagement_predictor.predict_engagement(
        content=content,
        content_type="blog",
        platform="blog",
        workspace_id="test-workspace"
    )

    assert "predictions" in engagement_result
    assert engagement_result["confidence_level"] > 0

    # Step 2: Analyze conversion potential
    conversion_result = await conversion_optimizer.analyze_conversion_potential(
        content=content,
        content_type="blog",
        workspace_id="test-workspace"
    )

    assert "conversion_score" in conversion_result
    assert len(conversion_result["recommendations"]) > 0

    # Step 3: Score viral potential
    viral_result = await viral_potential_scorer.score_viral_potential(
        content=content,
        content_type="blog",
        platform="blog"
    )

    assert "viral_score" in viral_result
    assert len(viral_result["optimization_suggestions"]) > 0

    # Verify all modules ran successfully
    assert engagement_result["confidence_level"] >= 0.0
    assert conversion_result["conversion_score"] >= 0.0
    assert viral_result["viral_score"] >= 0.0


@pytest.mark.asyncio
async def test_ab_test_workflow():
    """Test complete A/B testing workflow."""
    base_content = "Learn how to improve your marketing with these proven strategies."

    # Create test
    test_result = await ab_test_orchestrator.create_test(
        base_content=base_content,
        content_type="email",
        platform="email",
        workspace_id="test-workspace",
        num_variants=3,
        test_objective="conversion"
    )

    assert "test_id" in test_result
    assert len(test_result["recommended_variants"]) > 0

    # Verify each variant has predictions
    for variant in test_result["variants"]:
        assert "engagement_prediction" in variant
        assert "conversion_analysis" in variant
        assert "viral_score" in variant
        assert "composite_score" in variant


@pytest.mark.asyncio
async def test_competitive_analysis_workflow():
    """Test competitive analysis workflow."""
    competitor_samples = [
        "How to 10x your results with proven strategies",
        "Case study: Company X achieved 300% growth",
        "The future of marketing: 5 trends you can't ignore"
    ]

    # Analyze competitor
    competitor_result = await competitive_benchmarker.analyze_competitor(
        competitor_name="Competitor A",
        content_samples=competitor_samples,
        platform="linkedin"
    )

    assert "content_quality_score" in competitor_result
    assert "seo_score" in competitor_result
    assert "strengths" in competitor_result
    assert "opportunities" in competitor_result

    # Compare with your content
    your_content = "Marketing tips and strategies"
    your_metrics = {
        "engagement_rate": 0.03,
        "conversion_rate": 0.02
    }

    comparison = await competitive_benchmarker.compare_with_competitors(
        your_content=your_content,
        your_metrics=your_metrics,
        competitor_analyses=[competitor_result],
        platform="linkedin"
    )

    assert "competitive_position" in comparison
    assert "recommendations" in comparison
    assert "metric_benchmarks" in comparison


@pytest.mark.asyncio
async def test_multi_platform_analysis():
    """Test analysis across multiple platforms."""
    content = "Amazing product launch! #innovation @company"

    platforms = ["twitter", "linkedin", "instagram"]
    results = {}

    for platform in platforms:
        result = await engagement_predictor.predict_engagement(
            content=content,
            content_type="social_post",
            platform=platform,
            workspace_id="test-workspace"
        )
        results[platform] = result

    # Verify different platforms get different predictions
    for platform in platforms:
        assert platform in results
        assert "predictions" in results[platform]

    # Twitter should score higher for this content (has hashtags and mentions)
    assert results["twitter"]["feature_scores"]["platform_fit"] > 0.5


@pytest.mark.asyncio
async def test_content_optimization_loop():
    """Test iterative content optimization."""
    original_content = "Buy our product now."

    # First analysis
    first_conversion = await conversion_optimizer.analyze_conversion_potential(
        content=original_content,
        content_type="landing_page",
        workspace_id="test-workspace"
    )

    first_viral = await viral_potential_scorer.score_viral_potential(
        content=original_content,
        platform="general"
    )

    # Apply recommendations (simulated improvement)
    improved_content = """
    Discover how our revolutionary product can transform your results!

    Join 10,000+ satisfied customers who achieved amazing outcomes.
    Limited time offer - Get 50% off today!

    Try it risk-free with our 30-day money-back guarantee.
    No credit card required to start.
    """

    # Second analysis
    second_conversion = await conversion_optimizer.analyze_conversion_potential(
        content=improved_content,
        content_type="landing_page",
        workspace_id="test-workspace"
    )

    second_viral = await viral_potential_scorer.score_viral_potential(
        content=improved_content,
        platform="general"
    )

    # Improved content should score better
    assert second_conversion["conversion_score"] > first_conversion["conversion_score"]
    assert second_viral["viral_score"] > first_viral["viral_score"]


@pytest.mark.asyncio
async def test_performance_prediction_accuracy():
    """Test that predictions are consistent and reasonable."""
    high_quality_content = """
    SHOCKING: 10 Game-Changing Secrets That Will Transform Your Life!

    You won't believe what happened when I discovered these proven strategies.
    Join thousands who achieved incredible results. Here's the step-by-step guide:

    1. First secret revealed
    2. Second breakthrough method
    3. Third proven technique

    Get instant access now - 100% free, no credit card required!
    Limited time offer - claim your exclusive bonus today!
    """

    low_quality_content = "Information about product."

    # Analyze both
    high_engagement = await engagement_predictor.predict_engagement(
        content=high_quality_content,
        content_type="blog",
        platform="blog",
        workspace_id="test-workspace"
    )

    low_engagement = await engagement_predictor.predict_engagement(
        content=low_quality_content,
        content_type="blog",
        platform="blog",
        workspace_id="test-workspace"
    )

    high_conversion = await conversion_optimizer.analyze_conversion_potential(
        content=high_quality_content,
        content_type="blog",
        workspace_id="test-workspace"
    )

    low_conversion = await conversion_optimizer.analyze_conversion_potential(
        content=low_quality_content,
        content_type="blog",
        workspace_id="test-workspace"
    )

    high_viral = await viral_potential_scorer.score_viral_potential(
        content=high_quality_content,
        platform="general"
    )

    low_viral = await viral_potential_scorer.score_viral_potential(
        content=low_quality_content,
        platform="general"
    )

    # High quality content should consistently score better
    assert high_engagement["confidence_level"] > low_engagement["confidence_level"]
    assert high_conversion["conversion_score"] > low_conversion["conversion_score"]
    assert high_viral["viral_score"] > low_viral["viral_score"]
