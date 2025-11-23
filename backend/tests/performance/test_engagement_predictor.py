"""
Unit tests for EngagementPredictor.
"""

import pytest
from backend.performance.engagement_predictor import EngagementPredictor


@pytest.fixture
def predictor():
    """Create engagement predictor instance."""
    return EngagementPredictor()


@pytest.mark.asyncio
async def test_predict_engagement_basic(predictor):
    """Test basic engagement prediction."""
    content = """
    Discover the amazing secrets of successful marketing!
    Learn how to 10x your engagement with these proven strategies.
    Click here to get started today!
    """

    result = await predictor.predict_engagement(
        content=content,
        content_type="social_post",
        platform="linkedin",
        workspace_id="test-workspace"
    )

    assert "predictions" in result
    assert "confidence_level" in result
    assert "recommendations" in result
    assert 0.0 <= result["confidence_level"] <= 1.0
    assert "likes" in result["predictions"]
    assert "shares" in result["predictions"]
    assert "comments" in result["predictions"]


@pytest.mark.asyncio
async def test_predict_engagement_with_keywords(predictor):
    """Test engagement prediction with keywords."""
    content = "AI and machine learning are transforming digital marketing."
    keywords = ["AI", "machine learning", "marketing"]

    result = await predictor.predict_engagement(
        content=content,
        content_type="blog",
        platform="blog",
        workspace_id="test-workspace",
        keywords=keywords
    )

    assert result["feature_scores"]["keyword_density"] > 0


@pytest.mark.asyncio
async def test_content_length_scoring(predictor):
    """Test content length scoring for different platforms."""
    short_content = "Short post"
    optimal_content = " ".join(["word"] * 200)
    long_content = " ".join(["word"] * 5000)

    # LinkedIn optimal range
    short_score = predictor._score_content_length(len(short_content.split()), "article", "linkedin")
    optimal_score = predictor._score_content_length(len(optimal_content.split()), "article", "linkedin")
    long_score = predictor._score_content_length(len(long_content.split()), "article", "linkedin")

    assert optimal_score >= short_score
    assert optimal_score >= long_score


def test_sentiment_analysis(predictor):
    """Test sentiment analysis."""
    positive_content = "This is amazing, wonderful, and fantastic!"
    negative_content = "This is terrible, awful, and horrible!"
    neutral_content = "This is a product description."

    positive_score = predictor._analyze_sentiment(positive_content)
    negative_score = predictor._analyze_sentiment(negative_content)
    neutral_score = predictor._analyze_sentiment(neutral_content)

    assert positive_score > negative_score
    assert 0.4 <= neutral_score <= 0.7  # Neutral range


def test_platform_fit_scoring(predictor):
    """Test platform fit scoring."""
    twitter_content = "Check out this #amazing post @user! #trending"
    linkedin_content = "Strategic insights on professional business growth and innovation."

    twitter_score = predictor._score_platform_fit(twitter_content, "social_post", "twitter")
    linkedin_score = predictor._score_platform_fit(linkedin_content, "article", "linkedin")

    assert twitter_score > 0.5  # Has hashtags and mentions
    assert linkedin_score > 0.5  # Has professional language


@pytest.mark.asyncio
async def test_confidence_intervals(predictor):
    """Test confidence interval calculation."""
    content = "Test content for predictions"

    result = await predictor.predict_engagement(
        content=content,
        content_type="social_post",
        platform="linkedin",
        workspace_id="test-workspace"
    )

    intervals = result["confidence_intervals"]

    for metric, interval in intervals.items():
        assert "min" in interval
        assert "max" in interval
        assert "predicted" in interval
        assert interval["min"] <= interval["predicted"] <= interval["max"]
