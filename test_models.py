#!/usr/bin/env python3
"""
Empirical test for cognitive models - verifies dataclass instantiation and type validation
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from cognitive.models import (
    CognitiveResult,
    ContextSignals,
    DetectedIntent,
    Entity,
    EntityType,
    ExecutionPlan,
    IntentType,
    Issue,
    PerceivedInput,
    PlanStep,
    QualityScore,
    ReflectionResult,
    RiskLevel,
    Sentiment,
    SentimentResult,
    UrgencyResult,
)


def test_entity_creation():
    """Test Entity dataclass creation."""
    entity = Entity(
        text="Apple Inc.",
        type=EntityType.COMPANY,
        confidence=0.95,
        start_pos=10,
        end_pos=19,
        metadata={"stock_ticker": "AAPL"},
    )

    assert entity.text == "Apple Inc."
    assert entity.type == EntityType.COMPANY
    assert entity.confidence == 0.95
    assert entity.metadata["stock_ticker"] == "AAPL"
    print("✓ Entity creation works")
    return True


def test_intent_detection():
    """Test DetectedIntent dataclass."""
    intent = DetectedIntent(
        intent_type=IntentType.CREATE,
        confidence=0.88,
        sub_intents=["generate_content", "blog_post"],
        parameters={"topic": "AI trends", "length": "1000 words"},
        reasoning="User wants to create a blog post about AI trends",
    )

    assert intent.intent_type == IntentType.CREATE
    assert intent.confidence == 0.88
    assert "generate_content" in intent.sub_intents
    assert intent.parameters["topic"] == "AI trends"
    print("✓ Intent detection works")
    return True


def test_perceived_input():
    """Test PerceivedInput aggregation."""
    entity = Entity(
        text="John Doe", type=EntityType.PERSON, confidence=0.92, start_pos=0, end_pos=8
    )

    intent = DetectedIntent(
        intent_type=IntentType.GENERATE,
        confidence=0.85,
        parameters={"content_type": "email"},
    )

    sentiment = SentimentResult(
        sentiment=Sentiment.POSITIVE,
        confidence=0.78,
        emotional_signals=["excited", "optimistic"],
    )

    urgency = UrgencyResult(
        level=3, signals=["ASAP", "urgent"], reasoning="User mentioned urgency"
    )

    context = ContextSignals(
        topic_continuity=True,
        reference_to_prior=["previous discussion"],
        new_topic=False,
        implicit_assumptions=["user has context"],
    )

    perceived = PerceivedInput(
        raw_text="John Doe needs an urgent email ASAP",
        entities=[entity],
        intent=intent,
        sentiment=sentiment,
        urgency=urgency,
        context_signals=context,
    )

    assert len(perceived.entities) == 1
    assert perceived.entities[0].text == "John Doe"
    assert perceived.intent.intent_type == IntentType.GENERATE
    assert perceived.sentiment.sentiment == Sentiment.POSITIVE
    assert perceived.urgency.level == 3
    assert perceived.context_signals.topic_continuity == True
    print("✓ PerceivedInput aggregation works")
    return True


def test_execution_plan():
    """Test ExecutionPlan creation."""
    step1 = PlanStep(
        id="step_1",
        description="Extract key topics from user input",
        agent="perception_module",
        tools=["entity_extractor", "intent_detector"],
        estimated_tokens=500,
        estimated_cost=0.001,
        estimated_time_seconds=2,
        risk_level=RiskLevel.LOW,
    )

    step2 = PlanStep(
        id="step_2",
        description="Generate content based on extracted topics",
        agent="muse_engine",
        tools=["content_generator"],
        dependencies=["step_1"],
        estimated_tokens=1000,
        estimated_cost=0.002,
        estimated_time_seconds=5,
        risk_level=RiskLevel.MEDIUM,
    )

    plan = ExecutionPlan(
        goal="Generate blog post about AI trends",
        steps=[step1, step2],
        total_cost=None,  # Will be calculated
        total_time_seconds=7,
        risk_level=RiskLevel.MEDIUM,
        requires_approval=False,
    )

    assert len(plan.steps) == 2
    assert plan.steps[0].agent == "perception_module"
    assert plan.steps[1].dependencies == ["step_1"]
    assert plan.risk_level == RiskLevel.MEDIUM
    print("✓ ExecutionPlan creation works")
    return True


def test_reflection_result():
    """Test ReflectionResult with quality scoring."""
    issue = Issue(
        severity="medium",
        dimension="coherence",
        description="Paragraph lacks clear transition",
        location="paragraph 2",
        suggestion="Add transition sentence",
        confidence=0.82,
    )

    quality_score = QualityScore(
        overall=72,
        dimensions={
            "accuracy": 85,
            "relevance": 78,
            "coherence": 65,
            "brand_compliance": 90,
        },
        issues=[issue],
        passed=True,
        threshold=70,
    )

    reflection = ReflectionResult(
        quality_score=quality_score,
        initial_output="Initial generated content...",
        final_output="Improved content with transitions...",
        iterations=2,
        corrections_made=["Added transition sentences", "Improved coherence"],
        approved=True,
    )

    assert reflection.quality_score.overall == 72
    assert reflection.quality_score.passed == True
    assert len(reflection.quality_score.issues) == 1
    assert reflection.iterations == 2
    print("✓ ReflectionResult works")
    return True


def test_cognitive_result():
    """Test complete CognitiveResult."""
    # Create minimal perceived input
    entity = Entity(
        text="test", type=EntityType.PRODUCT, confidence=0.9, start_pos=0, end_pos=4
    )
    intent = DetectedIntent(intent_type=IntentType.CREATE, confidence=0.8)
    sentiment = SentimentResult(sentiment=Sentiment.NEUTRAL, confidence=0.7)
    urgency = UrgencyResult(level=2)
    context = ContextSignals(topic_continuity=False, new_topic=True)

    perceived = PerceivedInput(
        raw_text="Create test content",
        entities=[entity],
        intent=intent,
        sentiment=sentiment,
        urgency=urgency,
        context_signals=context,
    )

    # Create minimal execution plan
    step = PlanStep(id="step1", description="Test step", agent="test_agent")
    plan = ExecutionPlan(
        goal="Test goal",
        steps=[step],
        total_cost=None,
        total_time_seconds=5,
        risk_level=RiskLevel.LOW,
    )

    # Create reflection result
    quality = QualityScore(overall=85, passed=True)
    reflection = ReflectionResult(
        quality_score=quality,
        initial_output="test",
        final_output="test improved",
        iterations=1,
        approved=True,
    )

    result = CognitiveResult(
        perceived_input=perceived,
        execution_plan=plan,
        reflection_result=reflection,
        success=True,
        total_tokens_used=1500,
        total_cost_usd=0.003,
        processing_time_seconds=7.2,
    )

    assert result.success == True
    assert result.perceived_input.raw_text == "Create test content"
    assert result.execution_plan.goal == "Test goal"
    assert result.reflection_result.approved == True
    assert result.total_tokens_used == 1500
    print("✓ CognitiveResult integration works")
    return True


def run_all_tests():
    """Run all empirical tests."""
    print("Running empirical tests for cognitive models...")
    print("=" * 50)

    tests = [
        test_entity_creation,
        test_intent_detection,
        test_perceived_input,
        test_execution_plan,
        test_reflection_result,
        test_cognitive_result,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
                print(f"✗ {test.__name__} failed")
        except Exception as e:
            failed += 1
            print(f"✗ {test.__name__} failed with error: {e}")

    print("=" * 50)
    print(f"Tests passed: {passed}")
    print(f"Tests failed: {failed}")
    print(f"Success rate: {passed/(passed+failed)*100:.1f}%")

    if failed == 0:
        print("🎉 All empirical tests passed! Models work correctly.")
    else:
        print("❌ Some tests failed. Fix issues before proceeding.")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
