"""
Comprehensive test suite for Language Excellence Engine.
Tests all modules: grammar, style, readability, tone, and diversity.
"""

import pytest
import asyncio
from datetime import datetime

from backend.language import (
    optimize_language,
    grammar_orchestrator,
    style_enforcer,
    readability_optimizer,
    tone_adapter,
    linguistic_diversity_analyzer,
    BrandStyleGuide,
    ToneProfile
)


# Test content samples
SAMPLE_CONTENT_GOOD = """
The modern marketing landscape requires a data-driven approach. Companies that leverage
analytics and customer insights consistently outperform their competitors. By analyzing
user behavior patterns, businesses can create targeted campaigns that resonate with
their audience and drive measurable results.
"""

SAMPLE_CONTENT_GRAMMAR_ERRORS = """
The companys new product is their best yet. Its important to note that they has been
working on this for years. The team dont have any doubts about it's success. Me and
my colleague thinks this will be revolutionary.
"""

SAMPLE_CONTENT_STYLE_VIOLATIONS = """
But this is important. And we need to act fast. So let's get started. Basically, we
need to leverage our synergies and utilize our paradigm shift to optimize the customer
journey. It's gonna be awesome!!! We should of done this sooner.
"""

SAMPLE_CONTENT_COMPLEX = """
The implementation of a comprehensive, multi-faceted organizational restructuring
initiative necessitates the utilization of sophisticated methodologies and frameworks
that facilitate the optimization of cross-functional collaborative synergies whilst
simultaneously maintaining operational continuity throughout the transitional phase.
"""

SAMPLE_CONTENT_REPETITIVE = """
We need to improve our product. Our product is important. The product must be better.
Product quality is everything. We should make the product better. Better products win.
Our product team is working hard. They work on product improvements daily.
"""

SAMPLE_CONTENT_CASUAL = """
Hey there! We're super excited to share this with you. It's gonna be awesome, trust me.
You'll love it! We've been working really hard on this and can't wait for you to try it.
Don't miss out on this amazing opportunity!
"""


class TestGrammarOrchestrator:
    """Test grammar checking functionality."""

    @pytest.mark.asyncio
    async def test_grammar_check_clean_content(self):
        """Test grammar check on clean content."""
        result = await grammar_orchestrator.check_grammar(SAMPLE_CONTENT_GOOD)

        assert result is not None
        assert "total_issues" in result
        assert "issues" in result
        assert "engine_stats" in result
        assert result["total_issues"] >= 0

    @pytest.mark.asyncio
    async def test_grammar_check_errors(self):
        """Test grammar check detects errors."""
        result = await grammar_orchestrator.check_grammar(SAMPLE_CONTENT_GRAMMAR_ERRORS)

        assert result is not None
        assert result["total_issues"] > 0
        assert "critical_count" in result
        assert "issues" in result
        assert len(result["issues"]) > 0

        # Check issue structure
        first_issue = result["issues"][0]
        assert "message" in first_issue
        assert "severity" in first_issue
        assert "offset" in first_issue
        assert "engine" in first_issue

    @pytest.mark.asyncio
    async def test_grammar_auto_fixes(self):
        """Test auto-fix generation."""
        result = await grammar_orchestrator.check_grammar(SAMPLE_CONTENT_GRAMMAR_ERRORS)

        assert "auto_fixes" in result
        if result["total_issues"] > 0:
            assert len(result["auto_fixes"]) > 0
            first_fix = result["auto_fixes"][0]
            assert "original" in first_fix
            assert "suggestion" in first_fix
            assert "confidence" in first_fix

    @pytest.mark.asyncio
    async def test_custom_rules(self):
        """Test custom grammar rules."""
        content_with_passive = "The report was written by the team."

        result = await grammar_orchestrator.check_grammar(content_with_passive)

        assert result is not None
        # Should detect passive voice via custom rules
        assert "engine_stats" in result
        assert "custom_rules" in result["engine_stats"]


class TestStyleEnforcer:
    """Test style guide enforcement."""

    @pytest.mark.asyncio
    async def test_style_check_basic(self):
        """Test basic style checking."""
        result = await style_enforcer.enforce_style(SAMPLE_CONTENT_GOOD)

        assert result is not None
        assert "total_violations" in result
        assert "violations" in result
        assert "violations_by_type" in result
        assert "style_guide" in result

    @pytest.mark.asyncio
    async def test_style_violations_detection(self):
        """Test detection of style violations."""
        result = await style_enforcer.enforce_style(SAMPLE_CONTENT_STYLE_VIOLATIONS)

        assert result is not None
        assert result["total_violations"] > 0

        # Check for specific violation types
        violations_by_type = result["violations_by_type"]
        assert len(violations_by_type) > 0

    @pytest.mark.asyncio
    async def test_custom_style_guide(self):
        """Test custom style guide enforcement."""
        custom_guide = BrandStyleGuide(
            name="test_guide",
            voice="professional",
            use_oxford_comma=True,
            allow_contractions=False,
            forbidden_words={"awesome": "excellent", "gonna": "going to"}
        )

        enforcer = style_enforcer.__class__(custom_guide)
        result = await enforcer.enforce_style(SAMPLE_CONTENT_CASUAL)

        assert result is not None
        assert result["total_violations"] > 0

        # Should detect forbidden words
        violations = result["violations"]
        forbidden_violations = [v for v in violations if v["type"] == "word_choice"]
        assert len(forbidden_violations) > 0

    @pytest.mark.asyncio
    async def test_oxford_comma_check(self):
        """Test Oxford comma enforcement."""
        content_with_oxford = "We sell apples, oranges, and bananas."
        content_without_oxford = "We sell apples, oranges and bananas."

        # Guide requiring Oxford comma
        guide_oxford = BrandStyleGuide(use_oxford_comma=True)
        enforcer_oxford = style_enforcer.__class__(guide_oxford)

        result_with = await enforcer_oxford.enforce_style(content_with_oxford)
        result_without = await enforcer_oxford.enforce_style(content_without_oxford)

        # Content without Oxford comma should have violations
        assert result_without["total_violations"] > result_with["total_violations"]


class TestReadabilityOptimizer:
    """Test readability analysis."""

    @pytest.mark.asyncio
    async def test_readability_analysis_basic(self):
        """Test basic readability analysis."""
        result = await readability_optimizer.analyze_readability(SAMPLE_CONTENT_GOOD)

        assert result is not None
        assert "metrics" in result
        assert "average_grade_level" in result
        assert "text_statistics" in result

        # Check all metrics are present
        metrics = result["metrics"]
        assert "flesch_reading_ease" in metrics
        assert "flesch_kincaid_grade" in metrics
        assert "gunning_fog" in metrics
        assert "smog_index" in metrics
        assert "coleman_liau" in metrics
        assert "automated_readability" in metrics

    @pytest.mark.asyncio
    async def test_readability_with_target(self):
        """Test readability with target grade level."""
        result = await readability_optimizer.analyze_readability(
            SAMPLE_CONTENT_GOOD,
            target_grade_level=10
        )

        assert result is not None
        assert "suggestions" in result
        assert "meets_target" in result
        assert result["target_grade_level"] == 10

    @pytest.mark.asyncio
    async def test_complex_content_readability(self):
        """Test readability of complex content."""
        result = await readability_optimizer.analyze_readability(SAMPLE_CONTENT_COMPLEX)

        assert result is not None
        # Complex content should have higher grade level
        assert result["average_grade_level"] > 12

        # Should have suggestions to simplify
        if result.get("suggestions"):
            assert len(result["suggestions"]) > 0

    @pytest.mark.asyncio
    async def test_text_statistics(self):
        """Test text statistics extraction."""
        result = await readability_optimizer.analyze_readability(SAMPLE_CONTENT_GOOD)

        stats = result["text_statistics"]
        assert stats["total_words"] > 0
        assert stats["total_sentences"] > 0
        assert stats["total_syllables"] > 0
        assert stats["avg_sentence_length"] > 0
        assert stats["avg_word_length"] > 0


class TestToneAdapter:
    """Test tone analysis and adaptation."""

    @pytest.mark.asyncio
    async def test_tone_analysis_basic(self):
        """Test basic tone analysis."""
        result = await tone_adapter.analyze_tone(SAMPLE_CONTENT_GOOD)

        assert result is not None
        assert "detected_characteristics" in result
        assert "profile_matches" in result
        assert "best_match" in result

    @pytest.mark.asyncio
    async def test_tone_characteristics(self):
        """Test tone characteristic detection."""
        result = await tone_adapter.analyze_tone(SAMPLE_CONTENT_CASUAL)

        characteristics = result["detected_characteristics"]
        assert "formality_level" in characteristics
        assert "has_contractions" in characteristics
        assert "emoji_count" in characteristics
        assert "jargon_density" in characteristics

        # Casual content should have lower formality
        assert characteristics["formality_level"] < 7
        assert characteristics["has_contractions"] is True

    @pytest.mark.asyncio
    async def test_tone_profile_matching(self):
        """Test tone profile matching."""
        result = await tone_adapter.analyze_tone(SAMPLE_CONTENT_GOOD)

        assert "profile_matches" in result
        assert len(result["profile_matches"]) > 0

        # Check match structure
        first_match = result["profile_matches"][0]
        assert "profile" in first_match
        assert "confidence" in first_match
        assert 0 <= first_match["confidence"] <= 100

    @pytest.mark.asyncio
    async def test_tone_adaptation(self):
        """Test tone adaptation (rewriting)."""
        result = await tone_adapter.adapt_tone(
            SAMPLE_CONTENT_GOOD,
            target_tone="conversational"
        )

        assert result is not None
        assert "original_content" in result
        assert "adapted_content" in result
        assert "target_tone" in result
        assert result["target_tone"] == "conversational"
        assert result["adapted_content"] != result["original_content"]

    @pytest.mark.asyncio
    async def test_all_tone_profiles(self):
        """Test all predefined tone profiles."""
        profiles = tone_adapter.tone_profiles.keys()

        for profile_name in profiles:
            result = await tone_adapter.adapt_tone(
                "This is a test message about our product.",
                target_tone=profile_name
            )

            assert result is not None
            assert result["target_tone"] == profile_name
            assert "adapted_content" in result


class TestLinguisticDiversityAnalyzer:
    """Test linguistic diversity analysis."""

    @pytest.mark.asyncio
    async def test_diversity_analysis_basic(self):
        """Test basic diversity analysis."""
        result = await linguistic_diversity_analyzer.analyze_diversity(SAMPLE_CONTENT_GOOD)

        assert result is not None
        assert "diversity_score" in result
        assert "vocabulary_metrics" in result
        assert "sentence_variety" in result
        assert "repetition_analysis" in result
        assert "rhetorical_devices" in result

    @pytest.mark.asyncio
    async def test_vocabulary_metrics(self):
        """Test vocabulary richness metrics."""
        result = await linguistic_diversity_analyzer.analyze_diversity(SAMPLE_CONTENT_GOOD)

        vocab = result["vocabulary_metrics"]
        assert "total_words" in vocab
        assert "unique_words" in vocab
        assert "lexical_diversity" in vocab
        assert 0 <= vocab["lexical_diversity"] <= 1

    @pytest.mark.asyncio
    async def test_repetition_detection(self):
        """Test repetition detection."""
        result = await linguistic_diversity_analyzer.analyze_diversity(SAMPLE_CONTENT_REPETITIVE)

        repetition = result["repetition_analysis"]
        assert "overused_words" in repetition
        assert "repeated_phrases" in repetition
        assert "repetition_score" in repetition

        # Repetitive content should have low repetition score
        assert repetition["repetition_score"] < 80
        assert len(repetition["overused_words"]) > 0

    @pytest.mark.asyncio
    async def test_sentence_variety(self):
        """Test sentence variety analysis."""
        result = await linguistic_diversity_analyzer.analyze_diversity(SAMPLE_CONTENT_GOOD)

        variety = result["sentence_variety"]
        assert "total_sentences" in variety
        assert "average_length" in variety
        assert "variety_score" in variety
        assert "sentence_length_distribution" in variety

    @pytest.mark.asyncio
    async def test_rhetorical_devices(self):
        """Test rhetorical device detection."""
        content_with_devices = """
        Isn't it amazing how technology transforms our lives? We must embrace change.
        We must adapt. We must innovate! The future is bright, bold, and boundless.
        """

        result = await linguistic_diversity_analyzer.analyze_diversity(content_with_devices)

        devices = result["rhetorical_devices"]
        assert "devices_found" in devices
        assert "total_count" in devices
        assert "rhetorical_richness" in devices


class TestUnifiedLanguageOptimization:
    """Test the unified optimize_language function."""

    @pytest.mark.asyncio
    async def test_optimize_language_all_engines(self):
        """Test running all language engines."""
        result = await optimize_language(SAMPLE_CONTENT_GOOD)

        assert result is not None
        assert "overall_score" in result
        assert "executive_summary" in result
        assert "results" in result
        assert "aggregated_suggestions" in result
        assert "metadata" in result

        # Check all engines ran
        results = result["results"]
        assert "grammar" in results
        assert "style" in results
        assert "readability" in results
        assert "tone" in results
        assert "diversity" in results

    @pytest.mark.asyncio
    async def test_optimize_language_with_target_grade(self):
        """Test optimization with target grade level."""
        result = await optimize_language(
            SAMPLE_CONTENT_COMPLEX,
            target_grade_level=10
        )

        assert result is not None
        assert result["metadata"]["target_grade_level"] == 10

        # Should have readability suggestions
        readability = result["results"]["readability"]
        assert "suggestions" in readability
        if readability.get("average_grade_level", 0) > 10:
            assert len(readability["suggestions"]) > 0

    @pytest.mark.asyncio
    async def test_optimize_language_with_tone_adaptation(self):
        """Test optimization with tone adaptation."""
        result = await optimize_language(
            SAMPLE_CONTENT_GOOD,
            target_tone="conversational"
        )

        assert result is not None
        assert "tone_adaptation" in result["results"]

        adaptation = result["results"]["tone_adaptation"]
        assert "adapted_content" in adaptation
        assert adaptation["target_tone"] == "conversational"

    @pytest.mark.asyncio
    async def test_optimize_language_selective_engines(self):
        """Test running selective engines."""
        result = await optimize_language(
            SAMPLE_CONTENT_GOOD,
            run_grammar=True,
            run_style=False,
            run_readability=True,
            run_tone=False,
            run_diversity=False
        )

        assert result is not None
        results = result["results"]

        # Only grammar and readability should run
        assert "grammar" in results
        assert "readability" in results
        assert "style" not in results
        assert "tone" not in results
        assert "diversity" not in results

    @pytest.mark.asyncio
    async def test_executive_summary(self):
        """Test executive summary generation."""
        result = await optimize_language(SAMPLE_CONTENT_GOOD)

        summary = result["executive_summary"]
        assert "overall_quality" in summary
        assert "key_strengths" in summary
        assert "key_issues" in summary
        assert "top_recommendations" in summary

        assert isinstance(summary["key_strengths"], list)
        assert isinstance(summary["key_issues"], list)
        assert isinstance(summary["top_recommendations"], list)

    @pytest.mark.asyncio
    async def test_aggregated_suggestions(self):
        """Test suggestion aggregation."""
        result = await optimize_language(SAMPLE_CONTENT_GRAMMAR_ERRORS)

        suggestions = result["aggregated_suggestions"]
        assert isinstance(suggestions, list)

        if len(suggestions) > 0:
            first_suggestion = suggestions[0]
            assert "source" in first_suggestion
            assert "type" in first_suggestion
            assert "priority" in first_suggestion
            assert "issue" in first_suggestion

    @pytest.mark.asyncio
    async def test_overall_score_calculation(self):
        """Test overall score calculation."""
        result_good = await optimize_language(SAMPLE_CONTENT_GOOD)
        result_poor = await optimize_language(SAMPLE_CONTENT_GRAMMAR_ERRORS)

        assert result_good["overall_score"] > result_poor["overall_score"]
        assert 0 <= result_good["overall_score"] <= 100
        assert 0 <= result_poor["overall_score"] <= 100


class TestIntegrationScenarios:
    """Test real-world integration scenarios."""

    @pytest.mark.asyncio
    async def test_blog_post_optimization(self):
        """Test optimization for blog post."""
        blog_content = """
        The Impact of AI on Modern Marketing

        Artificial intelligence is revolutionizing how businesses approach marketing.
        Companies can now analyze vast amounts of customer data to create personalized
        experiences at scale. This technology enables marketers to predict customer
        behavior, optimize campaigns in real-time, and deliver the right message to
        the right person at the right time.
        """

        result = await optimize_language(
            blog_content,
            target_grade_level=12,
            run_grammar=True,
            run_style=True,
            run_readability=True,
            run_diversity=True
        )

        assert result is not None
        assert result["overall_score"] > 0

    @pytest.mark.asyncio
    async def test_email_optimization(self):
        """Test optimization for email content."""
        email_content = """
        Hi Sarah,

        I hope this email finds you well. I wanted to reach out regarding our
        upcoming product launch. We've made significant improvements based on
        customer feedback, and I believe you'll be impressed with the results.

        Would you be available for a quick call next week to discuss?

        Best regards,
        John
        """

        result = await optimize_language(
            email_content,
            target_tone="professional",
            run_grammar=True,
            run_style=True,
            run_tone=True
        )

        assert result is not None
        assert "tone" in result["results"]

    @pytest.mark.asyncio
    async def test_performance_metrics(self):
        """Test that performance metrics are tracked."""
        result = await optimize_language(SAMPLE_CONTENT_GOOD)

        metadata = result["metadata"]
        assert "duration_ms" in metadata
        assert metadata["duration_ms"] > 0
        assert "analyzed_at" in metadata


# Run all tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])
