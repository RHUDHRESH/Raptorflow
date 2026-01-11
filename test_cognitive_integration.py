#!/usr/bin/env python3
"""
Comprehensive integration test for cognitive modules
Verifies that EntityExtractor and IntentDetector work together properly
"""

import asyncio
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from cognitive.models import (
    ContextSignals,
    DetectedIntent,
    Entity,
    EntityType,
    IntentType,
    PerceivedInput,
    Sentiment,
    SentimentResult,
    UrgencyResult,
)
from cognitive.perception.entity_extractor import EntityExtractor
from cognitive.perception.intent_detector import IntentDetector


async def test_perception_integration():
    """Test that perception modules work together to create PerceivedInput."""
    entity_extractor = EntityExtractor()
    intent_detector = IntentDetector()

    test_text = "Apple Inc. announced earnings of $5.2 billion, up 15% from last year. Create a blog post about this."

    print(f"Testing integration with: {test_text}")

    # Extract entities
    entities = await entity_extractor.extract(test_text)
    print(f"Found {len(entities)} entities:")
    for entity in entities:
        print(
            f"  - {entity.text} ({entity.type.value}) confidence: {entity.confidence:.2f}"
        )

    # Detect intent
    intent = await intent_detector.detect(test_text)
    print(
        f"\nDetected intent: {intent.intent_type.value} (confidence: {intent.confidence:.2f})"
    )
    print(f"Parameters: {intent.parameters}")
    print(f"Sub-intents: {intent.sub_intents}")

    # Create mock sentiment, urgency, and context for full PerceivedInput
    sentiment = SentimentResult(
        sentiment=Sentiment.POSITIVE,
        confidence=0.75,
        emotional_signals=["optimistic", "excited"],
    )

    urgency = UrgencyResult(
        level=3,
        signals=["earnings", "announcement"],
        reasoning="Financial announcement with urgency",
    )

    context = ContextSignals(
        topic_continuity=False,
        reference_to_prior=[],
        new_topic=True,
        implicit_assumptions=["user follows tech news"],
    )

    # Create complete PerceivedInput
    perceived_input = PerceivedInput(
        raw_text=test_text,
        entities=entities,
        intent=intent,
        sentiment=sentiment,
        urgency=urgency,
        context_signals=context,
    )

    print(f"\n✓ Successfully created PerceivedInput with:")
    print(f"  - {len(perceived_input.entities)} entities")
    print(f"  - Intent: {perceived_input.intent.intent_type.value}")
    print(f"  - Sentiment: {perceived_input.sentiment.sentiment.value}")
    print(f"  - Urgency: {perceived_input.urgency.level}/5")
    print(f"  - Context signals: {perceived_input.context_signals.new_topic} new topic")

    return True


async def test_data_flow_validation():
    """Test that data flows correctly between modules."""
    entity_extractor = EntityExtractor()
    intent_detector = IntentDetector()

    test_cases = [
        {
            "text": "John Doe from Microsoft Corp invested $1,000,000 in startup XYZ. Update his profile.",
            "expected_entities": 3,  # person, company, money
            "expected_intent": IntentType.UPDATE,
            "should_have_target": True,
        },
        {
            "text": "Research competitor strategies and analyze market trends.",
            "expected_entities": 0,  # No clear entities
            "expected_intent": IntentType.RESEARCH,
            "should_have_target": True,
        },
        {
            "text": "Delete the old campaign and create a new one.",
            "expected_entities": 0,
            "expected_intent": IntentType.DELETE,
            "should_have_target": True,
        },
    ]

    passed = 0
    failed = 0

    for i, test_case in enumerate(test_cases):
        print(f"\n--- Test Case {i+1} ---")
        print(f"Text: {test_case['text']}")

        try:
            # Extract entities
            entities = await entity_extractor.extract(test_case["text"])
            entity_count_ok = len(entities) >= test_case["expected_entities"]
            print(
                f"Entities: {len(entities)} found (expected ≥{test_case['expected_entities']}) {'✓' if entity_count_ok else '✗'}"
            )

            # Detect intent
            intent = await intent_detector.detect(test_case["text"])
            intent_ok = intent.intent_type == test_case["expected_intent"]
            print(
                f"Intent: {intent.intent_type.value} (expected {test_case['expected_intent'].value}) {'✓' if intent_ok else '✗'}"
            )

            # Check for target parameter if expected
            if test_case["should_have_target"]:
                has_target = "target" in intent.parameters
                print(f"Has target parameter: {'✓' if has_target else '✗'}")
            else:
                has_target = True  # Not required

            # Overall success
            success = entity_count_ok and intent_ok and has_target
            if success:
                passed += 1
                print("✓ Test case passed")
            else:
                failed += 1
                print("✗ Test case failed")

        except Exception as e:
            print(f"✗ Error: {e}")
            failed += 1

    print(f"\nData flow validation: {passed} passed, {failed} failed")
    return failed == 0


async def test_performance_integration():
    """Test performance of integrated perception pipeline."""
    entity_extractor = EntityExtractor()
    intent_detector = IntentDetector()

    # Test with complex text
    complex_text = """
    Apple Inc. CEO Tim Cook announced record earnings of $123.45 billion,
    up 25% from last year. The company's stock price increased by 15%
    following the announcement. Microsoft Corp also reported strong results
    with $87.6 billion in revenue. Create a detailed analysis report
    comparing both companies' performance metrics and market positioning.
    """

    import time

    start_time = time.time()

    # Run both extractions
    entities = await entity_extractor.extract(complex_text)
    intent = await intent_detector.detect(complex_text)

    end_time = time.time()
    processing_time = end_time - start_time

    print(f"Complex text processing:")
    print(f"  - Length: {len(complex_text)} characters")
    print(f"  - Entities found: {len(entities)}")
    print(f"  - Intent detected: {intent.intent_type.value}")
    print(f"  - Processing time: {processing_time:.3f}s")

    # Performance should be reasonable (< 1 second for complex text)
    performance_ok = processing_time < 1.0
    print(f"  - Performance: {'✓' if performance_ok else '✗'}")

    return performance_ok


async def test_error_handling():
    """Test error handling in integrated pipeline."""
    entity_extractor = EntityExtractor()
    intent_detector = IntentDetector()

    error_cases = [
        "",  # Empty string
        "   ",  # Whitespace only
        "Invalid text with no clear intent or entities",  # Ambiguous
        "x" * 10000,  # Very long text
    ]

    passed = 0
    failed = 0

    for i, test_text in enumerate(error_cases):
        print(f"\n--- Error Case {i+1} ---")
        print(f"Input: '{test_text[:50]}{'...' if len(test_text) > 50 else ''}'")

        try:
            # Both should handle gracefully
            entities = await entity_extractor.extract(test_text)
            intent = await intent_detector.detect(test_text)

            print(f"Entities: {len(entities)}")
            print(
                f"Intent: {intent.intent_type.value} (confidence: {intent.confidence:.2f})"
            )

            # Should not crash and should return valid results
            if entities is not None and intent is not None:
                passed += 1
                print("✓ Handled gracefully")
            else:
                failed += 1
                print("✗ Returned None")

        except Exception as e:
            print(f"✗ Crashed with error: {e}")
            failed += 1

    print(f"\nError handling: {passed} passed, {failed} failed")
    return failed == 0


async def run_thorough_check():
    """Run comprehensive integration tests."""
    print("Running thorough integration check for cognitive modules...")
    print("=" * 60)

    tests = [
        ("Perception Integration", test_perception_integration),
        ("Data Flow Validation", test_data_flow_validation),
        ("Performance Integration", test_performance_integration),
        ("Error Handling", test_error_handling),
    ]

    total_passed = 0
    total_failed = 0

    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            result = await test_func()
            if result:
                total_passed += 1
                print(f"✓ {test_name} passed")
            else:
                total_failed += 1
                print(f"✗ {test_name} failed")
        except Exception as e:
            total_failed += 1
            print(f"✗ {test_name} failed with error: {e}")

    print("\n" + "=" * 60)
    print(f"Integration tests passed: {total_passed}")
    print(f"Integration tests failed: {total_failed}")

    if total_failed == 0:
        print(
            "🎉 All integration tests passed! Cognitive modules work together correctly."
        )
        print("\nKey findings:")
        print("- EntityExtractor and IntentDetector integrate seamlessly")
        print("- Data flows correctly between modules")
        print("- Performance is acceptable for complex texts")
        print("- Error handling is robust")
        print("- All modules produce valid, well-structured outputs")

        print("\nSystem is ready for:")
        print("- Full cognitive pipeline implementation")
        print("- Integration with planning and reflection modules")
        print("- Production deployment with confidence")
    else:
        print("❌ Some integration tests failed. Review issues before proceeding.")

    return total_failed == 0


if __name__ == "__main__":
    success = asyncio.run(run_thorough_check())
    sys.exit(0 if success else 1)
