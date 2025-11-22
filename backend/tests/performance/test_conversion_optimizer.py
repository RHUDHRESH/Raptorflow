"""
Unit tests for ConversionOptimizer.
"""

import pytest
from backend.performance.conversion_optimizer import ConversionOptimizer


@pytest.fixture
def optimizer():
    """Create conversion optimizer instance."""
    return ConversionOptimizer()


@pytest.mark.asyncio
async def test_analyze_conversion_potential_basic(optimizer):
    """Test basic conversion analysis."""
    content = """
    Get started with our amazing product today!
    Join thousands of satisfied customers.
    Click here to claim your free trial - no credit card required.
    """

    result = await optimizer.analyze_conversion_potential(
        content=content,
        content_type="landing_page",
        workspace_id="test-workspace"
    )

    assert "conversion_score" in result
    assert "cta_analysis" in result
    assert "urgency_score" in result
    assert "trust_score" in result
    assert "recommendations" in result
    assert 0.0 <= result["conversion_score"] <= 1.0


@pytest.mark.asyncio
async def test_cta_analysis(optimizer):
    """Test CTA analysis."""
    content_with_cta = "Click here to get started now!"
    content_without_cta = "This is just some information about our product."

    analysis_with = optimizer._analyze_cta(content_with_cta)
    analysis_without = optimizer._analyze_cta(content_without_cta)

    assert analysis_with["score"] > analysis_without["score"]
    assert len(analysis_with["all_ctas"]) > 0


def test_urgency_signals(optimizer):
    """Test urgency signal detection."""
    urgent_content = "Limited time offer! Only 24 hours left. Act now!"
    normal_content = "Our product is available for purchase."

    urgent_analysis = optimizer._analyze_urgency_signals(urgent_content)
    normal_analysis = optimizer._analyze_urgency_signals(normal_content)

    assert urgent_analysis["score"] > normal_analysis["score"]
    assert urgent_analysis["has_urgency"] is True
    assert len(urgent_analysis["signals"]) > 0


def test_trust_signals(optimizer):
    """Test trust signal detection."""
    trusted_content = "100% money-back guarantee. Certified and verified by industry experts. Join 10,000+ customers."
    untrusted_content = "Buy our product."

    trusted_analysis = optimizer._analyze_trust_signals(trusted_content)
    untrusted_analysis = optimizer._analyze_trust_signals(untrusted_content)

    assert trusted_analysis["score"] > untrusted_analysis["score"]
    assert trusted_analysis["has_trust_signals"] is True


def test_objection_handling(optimizer):
    """Test objection handling detection."""
    objection_content = "No credit card required. Cancel anytime. Risk-free trial."
    normal_content = "Sign up for our service."

    objection_analysis = optimizer._analyze_objection_handling(objection_content)
    normal_analysis = optimizer._analyze_objection_handling(normal_content)

    assert objection_analysis["score"] > normal_analysis["score"]
    assert objection_analysis["addresses_objections"] is True


def test_conversion_flow_analysis(optimizer):
    """Test conversion flow analysis."""
    good_flow = """
    Imagine doubling your revenue in 30 days.

    Our proven system has helped thousands achieve remarkable results.
    Here's how it works: Step 1, Step 2, Step 3.

    Ready to get started? Download our free guide now.
    """

    poor_flow = "Product information here."

    good_analysis = optimizer._analyze_conversion_flow(good_flow, "landing_page")
    poor_analysis = optimizer._analyze_conversion_flow(poor_flow, "landing_page")

    assert good_analysis["has_hook"] is True
    assert good_analysis["has_final_cta"] is True
    assert good_analysis["optimal_structure"] is True
    assert poor_analysis["optimal_structure"] is False


@pytest.mark.asyncio
async def test_optimized_cta_generation(optimizer):
    """Test CTA optimization suggestions."""
    result = await optimizer.analyze_conversion_potential(
        content="Check out our product",
        content_type="email",
        workspace_id="test-workspace"
    )

    optimized_ctas = result["optimized_ctas"]

    assert len(optimized_ctas) > 0
    for cta in optimized_ctas:
        assert "cta_text" in cta
        assert "rationale" in cta


@pytest.mark.asyncio
async def test_recommendation_generation(optimizer):
    """Test recommendation generation."""
    weak_content = "Product available."

    result = await optimizer.analyze_conversion_potential(
        content=weak_content,
        content_type="landing_page",
        workspace_id="test-workspace"
    )

    recommendations = result["recommendations"]

    assert len(recommendations) > 0
    for rec in recommendations:
        assert "priority" in rec
        assert "category" in rec
        assert "recommendation" in rec
