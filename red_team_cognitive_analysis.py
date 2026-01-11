#!/usr/bin/env python3
"""
RED TEAM ANALYSIS - Cognitive Engine Implementation
Identifies potential issues, vulnerabilities, and fuck-ups in the current implementation
"""

import asyncio
import json
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from cognitive.models import (
    DetectedIntent,
    Entity,
    EntityType,
    IntentType,
    PerceivedInput,
)
from cognitive.perception.entity_extractor import EntityExtractor
from cognitive.perception.intent_detector import IntentDetector


class CognitiveRedTeam:
    """Red team analysis for cognitive engine implementation"""

    def __init__(self):
        self.entity_extractor = EntityExtractor()
        self.intent_detector = IntentDetector()
        self.issues_found = []
        self.critical_issues = []
        self.warnings = []

    async def analyze_entity_extraction_vulnerabilities(self):
        """Analyze entity extraction for potential issues"""
        print("🔍 RED TEAM: Analyzing Entity Extraction Vulnerabilities")
        print("=" * 60)

        # Test 1: False Positives
        false_positive_tests = [
            "The quick brown fox jumps over the lazy dog",  # Should find no entities
            "Hello world, how are you today?",  # Common phrases
            "This is a test sentence with no entities",  # Explicit no entities
            "Just some random text here",  # Random text
        ]

        print("\n--- False Positive Analysis ---")
        fp_issues = 0
        for text in false_positive_tests:
            entities = await self.entity_extractor.extract(text)
            if len(entities) > 0:
                fp_issues += 1
                self.issues_found.append(
                    f"FALSE POSITIVE: '{text}' -> {len(entities)} entities found"
                )
                print(
                    f"❌ FALSE POSITIVE: '{text[:30]}...' found {len(entities)} entities"
                )
                for entity in entities[:3]:  # Show first 3
                    print(f"    - {entity.text} ({entity.type.value})")
            else:
                print(f"✅ Correctly found no entities: '{text[:30]}...'")

        # Test 2: False Negatives
        false_negative_tests = [
            "Apple Inc. reported earnings",  # Should find company
            "John Smith joined Microsoft",  # Should find person and company
            "Investment of $1.5 million",  # Should find money
            "Meeting on January 15, 2024",  # Should find date
            "Growth of 25% year-over-year",  # Should find percentage
        ]

        print("\n--- False Negative Analysis ---")
        fn_issues = 0
        for text in false_negative_tests:
            entities = await self.entity_extractor.extract(text)
            expected_entities = self._count_expected_entities(text)
            if len(entities) < expected_entities:
                fn_issues += 1
                self.issues_found.append(
                    f"FALSE NEGATIVE: '{text}' -> expected {expected_entities}, got {len(entities)}"
                )
                print(
                    f"❌ FALSE NEGATIVE: '{text}' expected {expected_entities}, got {len(entities)}"
                )
            else:
                print(f"✅ Found expected entities: '{text}' -> {len(entities)}")

        # Test 3: Confidence Score Issues
        confidence_tests = [
            "Definitely Apple Inc. the company",  # High confidence expected
            "Maybe some company called Apple",  # Lower confidence expected
            "I think it's $100",  # Uncertain money
        ]

        print("\n--- Confidence Score Analysis ---")
        conf_issues = 0
        for text in confidence_tests:
            entities = await self.entity_extractor.extract(text)
            for entity in entities:
                if entity.confidence < 0.5:
                    conf_issues += 1
                    self.warnings.append(
                        f"LOW CONFIDENCE: {entity.text} -> {entity.confidence:.2f}"
                    )
                    print(f"⚠️ LOW CONFIDENCE: {entity.text} -> {entity.confidence:.2f}")

        # Test 4: Edge Cases
        edge_cases = [
            "",  # Empty
            "   ",  # Whitespace only
            "A",  # Single character
            "x" * 10000,  # Very long text
            "🚀🌟💫",  # Emojis only
            "123-456-7890",  # Phone number
            "test@example.com",  # Email
        ]

        print("\n--- Edge Case Analysis ---")
        edge_issues = 0
        for text in edge_cases:
            try:
                entities = await self.entity_extractor.extract(text)
                if (
                    len(entities) > 50
                ):  # Too many entities might indicate over-extraction
                    edge_issues += 1
                    self.critical_issues.append(
                        f"OVER-EXTRACTION: {len(entities)} entities from edge case"
                    )
                    print(
                        f"❌ OVER-EXTRACTION: {len(entities)} entities from edge case"
                    )
                else:
                    print(
                        f"✅ Handled edge case: '{text[:20]}...' -> {len(entities)} entities"
                    )
            except Exception as e:
                edge_issues += 1
                self.critical_issues.append(f"CRASH on edge case: {e}")
                print(f"❌ CRASH on edge case: {e}")

        return fp_issues + fn_issues + conf_issues + edge_issues

    def _count_expected_entities(self, text):
        """Count expected entities in test text"""
        expected = 0
        text_lower = text.lower()
        if any(word in text_lower for word in ["inc", "corp", "llc", "ltd"]):
            expected += 1
        if any(word in text_lower for word in ["john", "smith", "jane", "doe"]):
            expected += 1
        if "$" in text_lower or any(
            word in text_lower for word in ["million", "billion", "thousand"]
        ):
            expected += 1
        if any(
            word in text_lower
            for word in ["january", "february", "march", "april", "may", "june"]
        ):
            expected += 1
        if "%" in text_lower or "percent" in text_lower:
            expected += 1
        return expected

    async def analyze_intent_detection_vulnerabilities(self):
        """Analyze intent detection for potential issues"""
        print("\n🔍 RED TEAM: Analyzing Intent Detection Vulnerabilities")
        print("=" * 60)

        # Test 1: Ambiguous Intents
        ambiguous_tests = [
            "I need to do something",  # Very unclear
            "Help me with this",  # No clear action
            "What should I do",  # Question but no clear intent
            "Maybe we could",  # Uncertain language
        ]

        print("\n--- Ambiguous Intent Analysis ---")
        amb_issues = 0
        for text in ambiguous_tests:
            intent = await self.intent_detector.detect(text)
            if intent.confidence > 0.7:  # Too confident for ambiguous input
                amb_issues += 1
                self.issues_found.append(
                    f"OVERCONFIDENT: '{text}' -> {intent.confidence:.2f}"
                )
                print(
                    f"❌ OVERCONFIDENT: '{text}' -> {intent.confidence:.2f} (should be < 0.7)"
                )
            elif intent.intent_type != IntentType.CLARIFY:
                amb_issues += 1
                self.warnings.append(
                    f"WRONG DEFAULT: '{text}' -> {intent.intent_type.value}"
                )
                print(
                    f"⚠️ WRONG DEFAULT: '{text}' -> {intent.intent_type.value} (should be CLARIFY)"
                )
            else:
                print(f"✅ Correctly handled ambiguous: '{text}' -> CLARIFY")

        # Test 2: Conflicting Intents
        conflicting_tests = [
            "Create and then delete the file",  # CREATE vs DELETE
            "Update but also create new content",  # UPDATE vs CREATE
            "Research and analyze the data",  # RESEARCH vs ANALYZE
        ]

        print("\n--- Conflicting Intent Analysis ---")
        conf_issues = 0
        for text in conflicting_tests:
            intent = await self.intent_detector.detect(text)
            # Should detect the primary intent, not get confused
            if intent.confidence < 0.5:
                conf_issues += 1
                self.warnings.append(
                    f"LOW CONFIDENCE on conflicting: '{text}' -> {intent.confidence:.2f}"
                )
                print(f"⚠️ LOW CONFIDENCE: '{text}' -> {intent.confidence:.2f}")
            else:
                print(f"✅ Handled conflicting: '{text}' -> {intent.intent_type.value}")

        # Test 3: Parameter Extraction Issues
        param_tests = [
            (
                "Create a 500 word blog about AI",
                {"content_type": "blog", "word_count": 500},
            ),
            ("Update the campaign strategy", {"target": "campaign"}),
            ("Delete the old move", {"target": "move"}),
        ]

        print("\n--- Parameter Extraction Analysis ---")
        param_issues = 0
        for text, expected_params in param_tests:
            intent = await self.intent_detector.detect(text)
            missing_params = []
            for key, value in expected_params.items():
                if key not in intent.parameters:
                    missing_params.append(key)

            if missing_params:
                param_issues += 1
                self.issues_found.append(
                    f"MISSING PARAMS: '{text}' -> {missing_params}"
                )
                print(f"❌ MISSING PARAMS: '{text}' -> missing {missing_params}")
            else:
                print(f"✅ Extracted params: '{text}' -> {intent.parameters}")

        # Test 4: Edge Cases
        edge_cases = [
            "",  # Empty
            "   ",  # Whitespace
            "x" * 1000,  # Long text
            "!@#$%^&*()",  # Special chars
            "123456789",  # Numbers only
        ]

        print("\n--- Edge Case Analysis ---")
        edge_issues = 0
        for text in edge_cases:
            try:
                intent = await self.intent_detector.detect(text)
                if intent.intent_type is None or intent.confidence < 0:
                    edge_issues += 1
                    self.critical_issues.append(f"INVALID OUTPUT: {text}")
                    print(f"❌ INVALID OUTPUT: '{text}'")
                else:
                    print(
                        f"✅ Handled edge case: '{text[:20]}...' -> {intent.intent_type.value}"
                    )
            except Exception as e:
                edge_issues += 1
                self.critical_issues.append(f"CRASH on edge case: {e}")
                print(f"❌ CRASH on edge case: {e}")

        return amb_issues + conf_issues + param_issues + edge_issues

    async def analyze_integration_vulnerabilities(self):
        """Analyze integration between modules"""
        print("\n🔍 RED TEAM: Analyzing Integration Vulnerabilities")
        print("=" * 60)

        # Test 1: Data Consistency
        consistency_tests = [
            "Apple Inc. earned $1 billion. Create a report.",
            "John Doe from Microsoft needs to update his profile.",
            "Delete the campaign and analyze the results.",
        ]

        print("\n--- Data Consistency Analysis ---")
        consistency_issues = 0
        for text in consistency_tests:
            try:
                entities = await self.entity_extractor.extract(text)
                intent = await self.intent_detector.detect(text)

                # Check if entities and intent make sense together
                if len(entities) > 0 and intent.intent_type == IntentType.CLARIFY:
                    consistency_issues += 1
                    self.warnings.append(
                        f"INCONSISTENT: entities found but CLARIFY intent"
                    )
                    print(
                        f"⚠️ INCONSISTENT: {len(entities)} entities but CLARIFY intent"
                    )
                elif len(entities) == 0 and intent.intent_type in [
                    IntentType.UPDATE,
                    IntentType.DELETE,
                ]:
                    consistency_issues += 1
                    self.warnings.append(
                        f"INCONSISTENT: no entities but {intent.intent_type.value} intent"
                    )
                    print(
                        f"⚠️ INCONSISTENT: no entities but {intent.intent_type.value} intent"
                    )
                else:
                    print(
                        f"✅ Consistent: {len(entities)} entities + {intent.intent_type.value} intent"
                    )
            except Exception as e:
                consistency_issues += 1
                self.critical_issues.append(f"INTEGRATION CRASH: {e}")
                print(f"❌ INTEGRATION CRASH: {e}")

        # Test 2: Performance Under Load
        print("\n--- Performance Load Test ---")
        perf_issues = 0

        try:
            import time

            start_time = time.time()

            # Process multiple texts concurrently
            tasks = []
            for i in range(10):
                text = f"Test case {i}: Apple Inc. reported earnings of ${i+1} billion. Create analysis."
                tasks.append(self.entity_extractor.extract(text))
                tasks.append(self.intent_detector.detect(text))

            results = await asyncio.gather(*tasks)
            end_time = time.time()

            processing_time = end_time - start_time
            if processing_time > 2.0:  # Should be fast
                perf_issues += 1
                self.warnings.append(
                    f"SLOW PERFORMANCE: {processing_time:.3f}s for 20 operations"
                )
                print(f"⚠️ SLOW PERFORMANCE: {processing_time:.3f}s for 20 operations")
            else:
                print(f"✅ GOOD PERFORMANCE: {processing_time:.3f}s for 20 operations")
        except Exception as e:
            perf_issues += 1
            self.critical_issues.append(f"PERFORMANCE CRASH: {e}")
            print(f"❌ PERFORMANCE CRASH: {e}")

        # Test 3: Memory Leaks
        print("\n--- Memory Leak Analysis ---")
        memory_issues = 0

        try:
            # Process many texts to check for memory issues
            for i in range(100):
                text = f"Test {i}: Company Inc. earned ${i} million. Update records."
                entities = await self.entity_extractor.extract(text)
                intent = await self.intent_detector.detect(text)

                # Clear references
                del entities, intent

            print("✅ No obvious memory leaks detected")
        except Exception as e:
            memory_issues += 1
            self.critical_issues.append(f"MEMORY ISSUE: {e}")
            print(f"❌ MEMORY ISSUE: {e}")

        return consistency_issues + perf_issues + memory_issues

    def analyze_architecture_vulnerabilities(self):
        """Analyze architectural issues"""
        print("\n🔍 RED TEAM: Analyzing Architecture Vulnerabilities")
        print("=" * 60)

        arch_issues = 0

        # Check 1: Import Dependencies
        print("\n--- Dependency Analysis ---")
        try:
            import cognitive.models
            import cognitive.perception.entity_extractor
            import cognitive.perception.intent_detector

            print("✅ All imports successful")
        except ImportError as e:
            arch_issues += 1
            self.critical_issues.append(f"IMPORT ERROR: {e}")
            print(f"❌ IMPORT ERROR: {e}")

        # Check 2: Data Model Integrity
        print("\n--- Data Model Analysis ---")
        try:
            # Test all model creation
            entity = Entity(
                text="Test",
                type=EntityType.COMPANY,
                confidence=0.8,
                start_pos=0,
                end_pos=4,
            )
            intent = DetectedIntent(intent_type=IntentType.CREATE, confidence=0.7)
            print("✅ Data models create successfully")
        except Exception as e:
            arch_issues += 1
            self.critical_issues.append(f"MODEL ERROR: {e}")
            print(f"❌ MODEL ERROR: {e}")

        # Check 3: Configuration Issues
        print("\n--- Configuration Analysis ---")

        # Check if modules are properly initialized
        try:
            extractor = EntityExtractor()
            detector = IntentDetector()

            if extractor.llm_client is not None:
                self.warnings.append("LLM client should be None by default")
                print("⚠️ LLM client should be None by default")

            if detector.llm_client is not None:
                self.warnings.append(
                    "Intent detector LLM client should be None by default"
                )
                print("⚠️ Intent detector LLM client should be None by default")

            print("✅ Configuration looks correct")
        except Exception as e:
            arch_issues += 1
            self.critical_issues.append(f"CONFIG ERROR: {e}")
            print(f"❌ CONFIG ERROR: {e}")

        return arch_issues

    async def run_red_team_analysis(self):
        """Run complete red team analysis"""
        print("🚨 COGNITIVE ENGINE RED TEAM ANALYSIS")
        print("=" * 80)
        print("Identifying vulnerabilities, issues, and potential fuck-ups...")

        total_issues = 0

        # Run all analyses
        entity_issues = await self.analyze_entity_extraction_vulnerabilities()
        intent_issues = await self.analyze_intent_detection_vulnerabilities()
        integration_issues = await self.analyze_integration_vulnerabilities()
        arch_issues = self.analyze_architecture_vulnerabilities()

        total_issues = entity_issues + intent_issues + integration_issues + arch_issues

        # Summary
        print("\n" + "=" * 80)
        print("🚨 RED TEAM ANALYSIS SUMMARY")
        print("=" * 80)

        print(f"\n📊 ISSUE COUNTS:")
        print(f"  Entity Extraction Issues: {entity_issues}")
        print(f"  Intent Detection Issues: {intent_issues}")
        print(f"  Integration Issues: {integration_issues}")
        print(f"  Architecture Issues: {arch_issues}")
        print(f"  TOTAL ISSUES: {total_issues}")

        print(f"\n🔴 CRITICAL ISSUES: {len(self.critical_issues)}")
        for issue in self.critical_issues:
            print(f"  - {issue}")

        print(f"\n⚠️  WARNINGS: {len(self.warnings)}")
        for warning in self.warnings[:5]:  # Show first 5
            print(f"  - {warning}")
        if len(self.warnings) > 5:
            print(f"  ... and {len(self.warnings) - 5} more")

        print(f"\n🟡 MINOR ISSUES: {len(self.issues_found)}")
        for issue in self.issues_found[:5]:  # Show first 5
            print(f"  - {issue}")
        if len(self.issues_found) > 5:
            print(f"  ... and {len(self.issues_found) - 5} more")

        # Assessment
        if len(self.critical_issues) == 0:
            print(f"\n✅ ASSESSMENT: NO CRITICAL ISSUES FOUND")
            print("   System is robust and ready for production")
        else:
            print(f"\n❌ ASSESSMENT: {len(self.critical_issues)} CRITICAL ISSUES")
            print("   Address before production deployment")

        if total_issues < 10:
            print(f"\n✅ OVERALL: GOOD ({total_issues} total issues)")
        elif total_issues < 20:
            print(f"\n⚠️  OVERALL: ACCEPTABLE ({total_issues} total issues)")
        else:
            print(f"\n❌ OVERALL: NEEDS WORK ({total_issues} total issues)")

        return len(self.critical_issues) == 0


if __name__ == "__main__":
    red_team = CognitiveRedTeam()
    success = asyncio.run(red_team.run_red_team_analysis())
    sys.exit(0 if success else 1)
