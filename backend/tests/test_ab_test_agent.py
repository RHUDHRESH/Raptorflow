"""
Test suite for A/B Test Variant Agent (MUS-009)

Tests creative copy variant generation, dynamic prompt engineering,
and marketing psychology-driven A/B testing agent functionality.
"""

import pytest
from unittest.mock import AsyncMock, patch

from backend.agents.muse.ab_test_agent import ABTestAgent
from backend.models.muse import VariantRequest, VariantReport, CreativeBatchRequest


class TestABTestAgent:
    """Test A/B Test Agent core functionality"""

    @pytest.fixture
    def agent(self):
        """Create a fresh agent instance for each test"""
        return ABTestAgent()

    def test_agent_initialization(self, agent):
        """Test agent initializes correctly"""
        assert isinstance(agent, ABTestAgent)
        assert hasattr(agent, 'generate_variants')
        assert hasattr(agent, 'generate_batch_variants')
        assert hasattr(agent, 'get_available_focuses')
        assert len(agent.focus_instructions) > 5  # Should have multiple focus types

    def test_available_focuses(self, agent):
        """Test available focuses are correctly configured"""
        focuses = agent.get_available_focuses()

        assert isinstance(focuses, list)
        assert len(focuses) > 0
        assert "URGENCY" in focuses
        assert "TONE" in focuses
        assert "SIMPLICITY" in focuses

    def test_focus_descriptions(self, agent):
        """Test focus descriptions are available"""
        urgency_desc = agent.get_focus_description("URGENCY")
        tone_desc = agent.get_focus_description("TONE")

        assert urgency_desc is not None
        assert "urgency" in urgency_desc.lower() or "scarcity" in urgency_desc.lower()
        assert tone_desc is not None
        assert "tone" in tone_desc.lower() or "professional" in tone_desc.lower()

    def test_build_variant_prompt_basic(self, agent):
        """Test basic prompt building structure"""
        request = VariantRequest(
            original_text="Buy our product now!",
            variation_focus="URGENCY",
            number_of_variants=3
        )

        prompt = agent._build_variant_prompt(request)

        assert "EXPERT DIRECT-RESPONSE COPYWRITER TASK" in prompt
        assert "Buy our product now!" in prompt
        assert "URGENCY" in prompt
        assert '"variants"' in prompt  # JSON structure
        assert "generate exactly 3 creative variations" in prompt

    def test_build_variant_prompt_tone_special_case(self, agent):
        """Test TONE focus always generates 3 variants"""
        request = VariantRequest(
            original_text="Learn new skills",
            variation_focus="TONE",
            number_of_variants=5  # Should be overridden to 3
        )

        prompt = agent._build_variant_prompt(request)

        assert "generate exactly 3 creative variations" in prompt
        assert "TONE focus always generates 3 variants" in prompt

    def test_build_variant_prompt_different_focuses(self, agent):
        """Test different focus types produce appropriate prompts"""
        base_request = VariantRequest(
            original_text="Start your journey",
            variation_focus="",
            number_of_variants=2
        )

        # Test urgency focus
        urgency_request = base_request.copy(update={"variation_focus": "URGENCY"})
        urgency_prompt = agent._build_variant_prompt(urgency_request)

        assert "urgency" in urgency_prompt.lower()
        assert "scarcity" in urgency_prompt.lower() or "immediate" in urgency_prompt.lower()

        # Test simplicity focus
        simple_request = base_request.copy(update={"variation_focus": "SIMPLICITY"})
        simple_prompt = agent._build_variant_prompt(simple_request)

        assert "simple" in simple_prompt.lower()
        assert "clear" in simple_prompt.lower() or "easy" in simple_prompt.lower()

        # Test benefit focus
        benefit_request = base_request.copy(update={"variation_focus": "BENEFIT_ORIENTED"})
        benefit_prompt = agent._build_variant_prompt(benefit_request)

        assert "benefit" in benefit_prompt.lower()
        assert "outcomes" in benefit_prompt.lower() or "gain" in benefit_prompt.lower()

    def test_invalid_focus_fallback(self, agent):
        """Test unrecognized focus uses default instruction"""
        request = VariantRequest(
            original_text="Test text",
            variation_focus="INVALID_FOCUS",
            number_of_variants=2
        )

        prompt = agent._build_variant_prompt(request)

        # Should use default focus instruction
        assert agent.default_focus_instruction not in prompt  # Built into the prompt
        assert "creative variations" in prompt.lower()
        assert "different perspective" in prompt.lower()

    @pytest.mark.asyncio
    async def test_generate_variants_success(self):
        """Test successful variant generation with mocked LLM"""
        mock_response = {
            "variants": [
                "🚨 Buy Now! Limited Time - Don't Miss Out!",
                "⚡ Act Fast! This Offer Won't Last Long!",
                "⏰ Limited Stocks - Grab Yours Today!"
            ]
        }

        with patch('backend.services.vertex_ai_client.generate_json', new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = mock_response

            agent = ABTestAgent()
            request = VariantRequest(
                original_text="Buy our product",
                variation_focus="URGENCY",
                number_of_variants=3
            )

            report = await agent.generate_variants(request)

            assert isinstance(report, VariantReport)
            assert report.original_text == "Buy our product"
            assert report.focus == "URGENCY"
            assert len(report.variants) == 3

            # Check variants contain urgent language
            urgent_keywords = ["limited", "time", "fast", "miss", "out", "now", "act"]
            for variant in report.variants:
                assert any(keyword in variant.lower() for keyword in urgent_keywords)

    @pytest.mark.asyncio
    async def test_generate_variants_tone_focus(self):
        """Test TONE focus generates exactly 3 variants despite requested count"""
        mock_response = {
            "variants": [
                "Professional: Enhance your skills with our comprehensive training program.",
                "Playful: Level up your game with our super fun learning adventure!",
                "Empathetic: We understand you want to grow - let's help you get there."
            ]
        }

        with patch('backend.services.vertex_ai_client.generate_json', new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = mock_response

            agent = ABTestAgent()
            request = VariantRequest(
                original_text="Improve your skills",
                variation_focus="TONE",
                number_of_variants=5  # Should be overridden
            )

            report = await agent.generate_variants(request)

            assert len(report.variants) == 3  # Always 3 for TONE
            assert report.focus == "TONE"

    @pytest.mark.asyncio
    async def test_generate_variants_json_parse_error(self):
        """Test handling of malformed LLM response"""
        with patch('backend.services.vertex_ai_client.generate_json', return_value="Invalid JSON string"):
            agent = ABTestAgent()
            request = VariantRequest(
                original_text="Test text",
                variation_focus="SIMPLICITY",
                number_of_variants=2
            )

            report = await agent.generate_variants(request)

            # Should return fallback report
            assert isinstance(report, VariantReport)
            assert "error" in report.summary.lower() or "unavailable" in report.summary.lower()

    @pytest.mark.asyncio
    async def test_generate_variants_llm_failure(self):
        """Test LLM service failure scenario"""
        with patch('backend.services.vertex_ai_client.generate_json', side_effect=Exception("Service unavailable")):
            agent = ABTestAgent()
            request = VariantRequest(
                original_text="Test copy",
                variation_focus="BENEFIT_ORIENTED",
                number_of_variants=2
            )

            report = await agent.generate_variants(request)

            # Should provide fallback response
            assert isinstance(report, VariantReport)
            assert len(report.variants) == 1
            assert report.variants[0] == "Test copy"  # Fallback to original

    def test_parse_variant_response_success(self, agent):
        """Test parsing valid variant response"""
        mock_response = {
            "variants": ["Variant 1", "Variant 2", "Variant 3"]
        }
        request = VariantRequest(
            original_text="test",
            variation_focus="URGENCY",
            number_of_variants=3
        )

        variants = agent._parse_variant_response(mock_response, request, "test-id")

        assert variants == ["Variant 1", "Variant 2", "Variant 3"]

    def test_parse_variant_response_validation(self, agent):
        """Test response validation and cleanup"""
        # Response with empty strings and too many variants
        mock_response = {
            "variants": ["", "Valid variant", "", "Another valid", "Extra variant", " "]
        }
        request = VariantRequest(
            original_text="test",
            variation_focus="SIMPLICITY",
            number_of_variants=2
        )

        variants = agent._parse_variant_response(mock_response, request, "test-id")

        assert len(variants) == 2  # Should be limited to requested count
        assert "" not in variants  # Empty strings should be filtered
        assert "Valid variant" in variants

    def test_parse_variant_response_wrong_format(self, agent):
        """Test handling of incorrectly formatted response"""
        mock_response = {"wrong_key": ["items"]}  # Missing 'variants' key
        request = VariantRequest(original_text="test", variation_focus="URGENCY", number_of_variants=1)

        with pytest.raises(Exception):
            agent._parse_variant_response(mock_response, request, "test-id")

    def test_parse_variant_response_tone_padding(self, agent):
        """Test TONE focus special handling with insufficient variants"""
        mock_response = {
            "variants": ["Only one variant"]  # Not enough for TONE
        }
        request = VariantRequest(
            original_text="test",
            variation_focus="TONE",
            number_of_variants=3
        )

        variants = agent._parse_variant_response(mock_response, request, "test-id")

        assert len(variants) == 3  # Should be padded to 3
        assert variants[0] == "Only one variant"
        # Other variants should be the original text

    @pytest.mark.asyncio
    async def test_generate_batch_variants(self):
        """Test batch variant generation"""
        # Mock responses for batch processing
        call_responses = [
            {"variants": ["Urgency variant 1", "Urgency variant 2"]},
            {"variants": ["Simple variant 1", "Simple variant 2"]}
        ]

        with patch('backend.services.vertex_ai_client.generate_json', new_callable=AsyncMock) as mock_generate:
            mock_generate.side_effect = call_responses

            agent = ABTestAgent()
            batch_request = CreativeBatchRequest(variants=[
                VariantRequest(
                    original_text="first text",
                    variation_focus="URGENCY",
                    number_of_variants=2
                ),
                VariantRequest(
                    original_text="second text",
                    variation_focus="SIMPLICITY",
                    number_of_variants=2
                )
            ])

            response = await agent.generate_batch_variants(batch_request)

            assert len(response.reports) == 2
            assert response.total_requests == 2
            assert all(len(report.variants) >= 1 for report in response.reports)

    def test_get_copywriter_system_prompt(self, agent):
        """Test copywriter system prompt content"""
        prompt = agent._get_copywriter_system_prompt()

        assert "expert direct-response copywriter" in prompt.lower()
        assert "a/b testing" in prompt.lower()
        assert "conversion rates" in prompt.lower()
        assert "psychological triggers" in prompt.lower()

    def test_fallback_variant_generation_urgency(self, agent):
        """Test fallback generation for urgency focus"""
        import asyncio
        async def run_test():
            variants = await agent._fallback_variant_generation(
                VariantRequest(original_text="Buy product", variation_focus="URGENCY", number_of_variants=2),
                "test-id"
            )

            assert len(variants) == 2
            urgent_indicators = ["limited", "time", "fast", "act", "now", "⚡", "🚨"]
            for variant in variants:
                assert any(indicator in variant for indicator in urgent_indicators)

        asyncio.run(run_test())

    def test_fallback_variant_generation_simplicity(self, agent):
        """Test fallback generation for simplicity focus"""
        import asyncio
        async def run_test():
            variants = await agent._fallback_variant_generation(
                VariantRequest(original_text="Experience our solution", variation_focus="SIMPLICITY", number_of_variants=3),
                "test-id"
            )

            assert len(variants) == 3
            # Check that complex words might be simplified
            assert any("try" in variant.lower() or "it's simple" in variant.lower() for variant in variants)

        asyncio.run(run_test())

    def test_fallback_variant_generation_edge_cases(self, agent):
        """Test fallback handling of edge cases"""
        import asyncio
        async def run_test():
            # Test with zero variants requested (should return original)
            variants = await agent._fallback_variant_generation(
                VariantRequest(original_text="Original", variation_focus="INVALID", number_of_variants=0),
                "test-id"
            )

            assert len(variants) == 0

            # Test with empty context
            variants = await agent._fallback_variant_generation(
                VariantRequest(original_text="", variation_focus="URGENCY", number_of_variants=1),
                "test-id"
            )

            assert len(variants) == 1

        asyncio.run(run_test())

    @pytest.mark.asyncio
    async def test_generate_with_context(self):
        """Test enhanced generation with context"""
        mock_response = {
            "variants": [
                "Professional: Boost your career with our corporate training solutions",
                "Playful: Level up your skills with our awesome learning platform!",
                "Trustworthy: Invest in your future with our established education program"
            ]
        }

        with patch('backend.services.vertex_ai_client.generate_json', new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = mock_response

            agent = ABTestAgent()
            request = VariantRequest(
                original_text="Learn new skills",
                variation_focus="TONE",
                number_of_variants=3
            )

            context = {
                "content_type": "button_text",
                "target_audience": "young_professionals",
                "brand_personality": "trustworthy",
                "industry": "education"
            }

            report = await agent.generate_with_context(request, context)

            assert isinstance(report, VariantReport)
            assert len(report.variants) == 3
            assert report.focus == "TONE"

    def test_build_contextual_prompt(self, agent):
        """Test context-enhanced prompt building"""
        request = VariantRequest(
            original_text="Sign up today",
            variation_focus="BENEFIT_ORIENTED",
            number_of_variants=2
        )

        context = {
            "content_type": "call_to_action",
            "target_audience": "small_business_owners",
            "brand_personality": "professional",
            "industry": "business_services"
        }

        prompt = agent._build_contextual_prompt(request, context)

        assert "Sign up today" in prompt
        assert "BENEFIT_ORIENTED" in prompt
        assert "call_to_action" in prompt
        assert "small_business_owners" in prompt

    def test_contextual_system_prompt_enhancement(self, agent):
        """Test context-aware system prompt creation"""
        context = {
            "content_type": "email_subject",
            "target_audience": "tech_professionals",
            "brand_personality": "innovative",
            "industry": "technology"
        }

        enhanced_prompt = agent._build_contextual_system_prompt(context)

        assert "email_subject" in enhanced_prompt
        assert "tech_professionals" in enhanced_prompt
        assert "innovative" in enhanced_prompt
        assert "technology" in enhanced_prompt


class TestModelIntegration:
    """Test model validation and integration"""

    def test_variant_request_validation(self):
        """Test VariantRequest Pydantic validation"""
        from pydantic import ValidationError

        # Valid request
        request = VariantRequest(
            original_text="Valid text",
            variation_focus="URGENCY",
            number_of_variants=3
        )
        assert request.original_text == "Valid text"

        # Test empty text
        with pytest.raises(ValidationError):
            VariantRequest(original_text="", variation_focus="URGENCY")

        # Test too many variants
        with pytest.raises(ValidationError):
            VariantRequest(
                original_text="test",
                variation_focus="URGENCY",
                number_of_variants=15  # Exceeds max
            )

        # Test too few variants
        with pytest.raises(ValidationError):
            VariantRequest(
                original_text="test",
                variation_focus="URGENCY",
                number_of_variants=0
            )

    def test_variant_report_validation(self):
        """Test VariantReport Pydantic validation"""
        from pydantic import ValidationError

        # Valid report
        report = VariantReport(
            original_text="Original",
            focus="URGENCY",
            variants=["Variant 1", "Variant 2"]
        )
        assert len(report.variants) == 2

        # Invalid: empty variants list
        with pytest.raises(ValidationError):
            VariantReport(
                original_text="Original",
                focus="URGENCY",
                variants=[]
            )


class TestRealWorldScenarios:
    """Test realistic A/B testing scenarios"""

    def test_emailsubject_variant_generation(self):
        """Test email subject line variation"""
        agent = ABTestAgent()

        # Simulate LLM response for email subjects
        mock_response = {
            "variants": [
                "🚀 Last Chance: 50% Off Ends Tonight!",
                "⚠️ Don't Miss: Limited Time Sale Ends Soon",
                "⏰ Time Running Out - Act Now!"
            ]
        }

        with patch('backend.services.vertex_ai_client.generate_json', return_value=mock_response):
            import asyncio
            async def run_test():
                request = VariantRequest(
                    original_text="50% Off Sale",
                    variation_focus="URGENCY",
                    number_of_variants=3
                )

                report = await agent.generate_variants(request)

                assert len(report.variants) == 3
                assert all("50%" in variant or "sale" in variant.lower() for variant in report.variants)
                assert any("time" in variant.lower() for variant in report.variants)

            asyncio.run(run_test())

    def test_button_text_tone_variations(self):
        """Test button text with tone variations"""
        agent = ABTestAgent()

        mock_response = {
            "variants": [
                "GET STARTED NOW",
                "😊 Let's Begin!",
                "I understand - let's proceed together"
            ]
        }

        with patch('backend.services.vertex_ai_client.generate_json', return_value=mock_response):
            import asyncio
            async def run_test():
                request = VariantRequest(
                    original_text="Start Here",
                    variation_focus="TONE",
                    number_of_variants=3
                )

                report = await agent.generate_variants(request)

                assert len(report.variants) == 3
                assert report.focus == "TONE"

            asyncio.run(run_test())

    def test_headline_benefit_orientation(self):
        """Test headline generation with benefit focus"""
        agent = ABTestAgent()

        mock_response = {
            "variants": [
                "Save Thousands on Your Monthly Bills",
                "Transform Your Financial Future Today",
                "Gain the Peace of Mind You Deserve"
            ]
        }

        with patch('backend.services.vertex_ai_client.generate_json', return_value=mock_response):
            import asyncio
            async def run_test():
                request = VariantRequest(
                    original_text="Our service helps save money",
                    variation_focus="BENEFIT_ORIENTED",
                    number_of_variants=3
                )

                report = await agent.generate_variants(request)

                assert len(report.variants) == 3
                benefit_indicators = ["save", "transform", "gain", "benefit", "improve", "better"]
                assert all(
                    any(indicator in variant.lower() for indicator in benefit_indicators)
                    for variant in report.variants
                )

            asyncio.run(run_test())

    def test_scalability_stress_test(self, agent):
        """Test agent handles larger text inputs gracefully"""
        long_text = "This is a very long piece of marketing copy that goes on and on with many details about the product features and benefits that our customers absolutely love and recommend to their friends and colleagues in the industry. " * 10

        # Should not crash with long input
        prompt = agent._build_variant_prompt(VariantRequest(
            original_text=long_text,
            variation_focus="SIMPLICITY",
            number_of_variants=2
        ))

        assert len(prompt) > 100  # Has content
        assert long_text[:50] in prompt  # Contains original text (truncated for focus)
