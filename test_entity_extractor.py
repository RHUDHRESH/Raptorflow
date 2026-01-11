#!/usr/bin/env python3
"""
Empirical test for EntityExtractor - verifies it actually extracts entities correctly
"""

import asyncio
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from cognitive.models import Entity, EntityType
from cognitive.perception.entity_extractor import EntityExtractor


def test_entity_extraction():
    """Test entity extraction with sample texts."""
    extractor = EntityExtractor()

    test_cases = [
        {
            "text": "Apple Inc. announced earnings of $5.2 billion, up 15% from last year.",
            "expected_entities": [
                ("Apple Inc.", EntityType.COMPANY),
                ("$5.2 billion", EntityType.MONEY),
                ("15%", EntityType.PERCENTAGE),
            ],
        },
        {
            "text": "John Doe from Microsoft Corp invested $1,000,000 in startup XYZ.",
            "expected_entities": [
                ("John Doe", EntityType.PERSON),
                ("Microsoft Corp", EntityType.COMPANY),
                ("$1,000,000", EntityType.MONEY),
            ],
        },
        {
            "text": "The meeting is scheduled for January 15, 2024 at 10% capacity.",
            "expected_entities": [
                ("January 15, 2024", EntityType.DATE),
                ("10%", EntityType.PERCENTAGE),
            ],
        },
        {"text": "No entities here, just plain text.", "expected_entities": []},
    ]

    passed = 0
    failed = 0

    for i, test_case in enumerate(test_cases):
        print(f"\nTest case {i+1}: {test_case['text']}")

        try:
            # Test synchronous extraction
            entities = asyncio.run(extractor.extract(test_case["text"]))

            print(f"Found {len(entities)} entities:")
            for entity in entities:
                print(
                    f"  - {entity.text} ({entity.type.value}) confidence: {entity.confidence:.2f}"
                )

            # Validate expected entities are found
            expected_found = 0
            for expected_text, expected_type in test_case["expected_entities"]:
                found = False
                for entity in entities:
                    # Check for exact match or substantial overlap
                    text_match = expected_text.lower() == entity.text.lower()
                    overlap_match = (
                        expected_text.lower() in entity.text.lower()
                        or entity.text.lower() in expected_text.lower()
                    )

                    if entity.type == expected_type and (text_match or overlap_match):
                        found = True
                        if entity.confidence >= 0.5:  # Minimum confidence threshold
                            expected_found += 1
                            print(
                                f"  ✓ Found expected: {expected_text} (matched as: {entity.text})"
                            )
                        else:
                            print(
                                f"  ⚠ Found but low confidence: {expected_text} ({entity.confidence:.2f})"
                            )
                        break

                if not found:
                    print(f"  ✗ Missing expected: {expected_text}")

            # Check for unexpected entities (shouldn't fail test, just note)
            if len(entities) > len(test_case["expected_entities"]):
                print(
                    f"  ℹ Found {len(entities) - len(test_case['expected_entities'])} additional entities"
                )

            # Calculate success rate for this test case
            if len(test_case["expected_entities"]) == 0:
                # Should find no entities
                if len(entities) == 0:
                    print("  ✓ Correctly found no entities")
                    passed += 1
                else:
                    print("  ✗ Found entities when none expected")
                    failed += 1
            else:
                success_rate = expected_found / len(test_case["expected_entities"])
                if success_rate >= 0.7:  # 70% success rate threshold
                    print(f"  ✓ Success rate: {success_rate*100:.1f}%")
                    passed += 1
                else:
                    print(f"  ✗ Low success rate: {success_rate*100:.1f}%")
                    failed += 1

        except Exception as e:
            print(f"  ✗ Error: {e}")
            failed += 1

    return passed, failed


def test_entity_validation():
    """Test entity validation logic."""
    extractor = EntityExtractor()

    # Test valid entity
    valid_entity = Entity(
        text="Apple Inc.",
        type=EntityType.COMPANY,
        confidence=0.85,
        start_pos=0,
        end_pos=10,
    )

    assert extractor.validate_entity(
        valid_entity
    ), "Valid entity should pass validation"
    print("✓ Entity validation works for valid entity")

    # Test invalid entity (low confidence)
    invalid_entity = Entity(
        text="Test",
        type=EntityType.COMPANY,
        confidence=0.3,  # Below threshold
        start_pos=0,
        end_pos=4,
    )

    assert not extractor.validate_entity(
        invalid_entity
    ), "Low confidence entity should fail validation"
    print("✓ Entity validation rejects low confidence")

    # Test invalid entity (bad positions)
    bad_entity = Entity(
        text="Test",
        type=EntityType.COMPANY,
        confidence=0.8,
        start_pos=5,
        end_pos=3,  # End before start
    )

    assert not extractor.validate_entity(
        bad_entity
    ), "Bad position entity should fail validation"
    print("✓ Entity validation rejects bad positions")

    return True


def test_overlapping_filter():
    """Test filtering of overlapping entities."""
    extractor = EntityExtractor()

    # Create overlapping entities
    entities = [
        Entity(
            text="Apple Inc.",
            type=EntityType.COMPANY,
            confidence=0.9,
            start_pos=0,
            end_pos=10,
        ),
        Entity(
            text="Apple",
            type=EntityType.COMPANY,
            confidence=0.7,
            start_pos=0,
            end_pos=5,
        ),  # Overlaps
        Entity(
            text="Inc.",
            type=EntityType.COMPANY,
            confidence=0.6,
            start_pos=6,
            end_pos=10,
        ),  # Overlaps
        Entity(
            text="Microsoft",
            type=EntityType.COMPANY,
            confidence=0.8,
            start_pos=15,
            end_pos=23,
        ),  # No overlap
    ]

    filtered = extractor.filter_overlapping_entities(entities)

    # Should keep the highest confidence non-overlapping entities
    assert len(filtered) == 2, f"Expected 2 entities, got {len(filtered)}"
    assert (
        filtered[0].text == "Apple Inc."
    ), "Should keep higher confidence overlapping entity"
    assert filtered[1].text == "Microsoft", "Should keep non-overlapping entity"

    print("✓ Overlapping entity filtering works")
    return True


def test_regex_fallback():
    """Test regex fallback extraction."""
    extractor = EntityExtractor()  # No LLM client, will use regex

    text = "Contact us at $100 or 25% by Jan 15, 2024"
    entities = asyncio.run(extractor.extract(text))

    # Should find money, percentage, and date
    found_types = {entity.type for entity in entities}

    assert EntityType.MONEY in found_types, "Should find money entity"
    assert EntityType.PERCENTAGE in found_types, "Should find percentage entity"
    assert EntityType.DATE in found_types, "Should find date entity"

    print("✓ Regex fallback extraction works")
    return True


async def test_processing_performance():
    """Test that extraction doesn't take too long."""
    extractor = EntityExtractor()

    # Test with longer text
    long_text = " ".join(
        [
            "Apple Inc. reported revenue of $123.45 billion, up 15.2% from last year.",
            "Microsoft Corp earned $87.6 billion, a 12% increase.",
            "Google LLC made $282.8 billion, up 10% year-over-year.",
            "Amazon.com Inc posted $513.9 billion in sales, up 12%.",
        ]
        * 10
    )  # Repeat 10 times for longer text

    import time

    start_time = time.time()
    entities = await extractor.extract(long_text)
    end_time = time.time()

    processing_time = end_time - start_time

    # Should complete within reasonable time (5 seconds for long text)
    assert processing_time < 5.0, f"Processing too slow: {processing_time:.2f}s"
    assert len(entities) > 0, "Should find entities in long text"

    print(
        f"✓ Performance test passed: {processing_time:.3f}s for {len(entities)} entities"
    )
    return True


def run_all_tests():
    """Run all empirical tests for EntityExtractor."""
    print("Running empirical tests for EntityExtractor...")
    print("=" * 60)

    tests = [
        ("Entity Extraction", test_entity_extraction),
        ("Entity Validation", test_entity_validation),
        ("Overlapping Filter", test_overlapping_filter),
        ("Regex Fallback", test_regex_fallback),
        ("Processing Performance", test_processing_performance),
    ]

    total_passed = 0
    total_failed = 0

    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = asyncio.run(test_func())
            else:
                result = test_func()

            if isinstance(result, tuple):
                passed, failed = result
                total_passed += passed
                total_failed += failed
            elif result:
                total_passed += 1
                print(f"✓ {test_name} passed")
            else:
                total_failed += 1
                print(f"✗ {test_name} failed")

        except Exception as e:
            total_failed += 1
            print(f"✗ {test_name} failed with error: {e}")

    print("\n" + "=" * 60)
    print(f"Tests passed: {total_passed}")
    print(f"Tests failed: {total_failed}")

    if total_failed == 0:
        print("🎉 All empirical tests passed! EntityExtractor works correctly.")
        print("\nKey findings:")
        print("- Extracts entities with proper confidence scoring")
        print(
            "- Handles multiple entity types (company, person, money, percentage, date)"
        )
        print("- Filters overlapping entities correctly")
        print("- Falls back to regex when LLM unavailable")
        print("- Processes text within reasonable time limits")
    else:
        print("❌ Some tests failed. Fix issues before proceeding.")

    return total_failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
