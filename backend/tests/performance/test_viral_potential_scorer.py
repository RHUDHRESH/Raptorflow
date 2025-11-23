"""
Unit tests for ViralPotentialScorer.
"""

import pytest
from backend.performance.viral_potential_scorer import ViralPotentialScorer


@pytest.fixture
def scorer():
    """Create viral potential scorer instance."""
    return ViralPotentialScorer()


@pytest.mark.asyncio
async def test_score_viral_potential_basic(scorer):
    """Test basic viral potential scoring."""
    content = """
    You won't believe what happened next! This shocking discovery will change everything.
    Here are 5 amazing secrets that experts don't want you to know.
    """

    result = await scorer.score_viral_potential(
        content=content,
        title="5 Shocking Secrets That Will Change Your Life",
        content_type="article",
        platform="general"
    )

    assert "viral_score" in result
    assert "emotion_analysis" in result
    assert "viral_elements" in result
    assert "optimization_suggestions" in result
    assert 0.0 <= result["viral_score"] <= 1.0


def test_emotion_analysis(scorer):
    """Test emotional trigger analysis."""
    emotional_content = "This is absolutely amazing and shocking! You won't believe this incredible discovery!"
    neutral_content = "This is a product description with technical specifications."

    emotional_analysis = scorer._analyze_emotions(emotional_content)
    neutral_analysis = scorer._analyze_emotions(neutral_content)

    assert emotional_analysis["high_arousal_score"] > neutral_analysis["high_arousal_score"]
    assert emotional_analysis["has_strong_emotion"] is True
    assert emotional_analysis["total_triggers"] > 0


def test_shareability_analysis(scorer):
    """Test shareability factor analysis."""
    shareable_content = """
    How to master this skill: A step-by-step guide.
    Exclusive insider secrets revealed for the first time.
    The controversial truth about this topic.
    """

    analysis = scorer._analyze_shareability(shareable_content)

    assert analysis["practical_value"]["score"] > 0
    assert analysis["social_currency"]["score"] > 0
    assert analysis["novelty"]["score"] > 0


def test_storytelling_analysis(scorer):
    """Test storytelling element detection."""
    story_content = """
    When I first started, I struggled with this challenge.
    Then I discovered a solution that changed everything.
    After implementing these steps, I achieved remarkable results.
    The lesson I learned was invaluable.
    """

    non_story_content = "Product features: A, B, C. Price: $99."

    story_score = scorer._analyze_storytelling(story_content)
    non_story_score = scorer._analyze_storytelling(non_story_content)

    assert story_score > non_story_score
    assert story_score > 0.3


def test_format_analysis(scorer):
    """Test viral format detection."""
    list_title = "7 Ways to Boost Your Productivity"
    how_to_title = "How to Master Python in 30 Days"
    question_title = "Is AI Taking Over Your Job?"
    normal_title = "Product Update"

    list_analysis = scorer._analyze_format("", list_title)
    how_to_analysis = scorer._analyze_format("", how_to_title)
    question_analysis = scorer._analyze_format("", question_title)
    normal_analysis = scorer._analyze_format("", normal_title)

    assert list_analysis["is_list_format"] is True
    assert how_to_analysis["is_how_to"] is True
    assert question_analysis["formats_found"]["question"] is True
    assert list_analysis["score"] > normal_analysis["score"]


def test_practical_value_scoring(scorer):
    """Test practical value scoring."""
    practical_content = """
    Here's a step-by-step guide to solve this problem:
    1. First, do this
    2. Next, do that
    3. Finally, complete this
    These proven tips will help you achieve results.
    """

    non_practical_content = "This is an opinion piece about trends."

    practical_score = scorer._score_practical_value(practical_content)
    non_practical_score = scorer._score_practical_value(non_practical_content)

    assert practical_score > non_practical_score
    assert practical_score > 0.3


def test_social_currency_scoring(scorer):
    """Test social currency scoring."""
    exclusive_content = "Exclusive insider secrets revealed! Behind-the-scenes VIP access."
    normal_content = "Regular product information."

    exclusive_score = scorer._score_social_currency(exclusive_content)
    normal_score = scorer._score_social_currency(normal_content)

    assert exclusive_score > normal_score


@pytest.mark.asyncio
async def test_viral_elements_identification(scorer):
    """Test identification of viral elements."""
    highly_viral = """
    SHOCKING: 10 Secrets That Will Change Your Life!

    You won't believe what happened when I discovered these game-changing strategies.
    Here's the step-by-step guide that helped me achieve amazing results.
    """

    result = await scorer.score_viral_potential(
        content=highly_viral,
        title="10 Shocking Secrets",
        platform="general"
    )

    viral_elements = result["viral_elements"]

    assert len(viral_elements) > 0
    assert isinstance(viral_elements, list)


@pytest.mark.asyncio
async def test_optimization_suggestions(scorer):
    """Test viral optimization suggestions."""
    weak_content = "This is basic information about a topic."

    result = await scorer.score_viral_potential(
        content=weak_content,
        platform="general"
    )

    suggestions = result["optimization_suggestions"]

    assert len(suggestions) > 0
    for suggestion in suggestions:
        assert "priority" in suggestion
        assert "category" in suggestion
        assert "suggestion" in suggestion
        assert "impact" in suggestion


@pytest.mark.asyncio
async def test_platform_specific_suggestions(scorer):
    """Test platform-specific optimization."""
    content = "Generic content"

    twitter_result = await scorer.score_viral_potential(
        content=content,
        platform="twitter"
    )

    linkedin_result = await scorer.score_viral_potential(
        content=content,
        platform="linkedin"
    )

    # Different platforms should get different suggestions
    twitter_suggestions = [s["category"] for s in twitter_result["optimization_suggestions"]]
    linkedin_suggestions = [s["category"] for s in linkedin_result["optimization_suggestions"]]

    assert "Platform" in twitter_suggestions or "Platform" in linkedin_suggestions
