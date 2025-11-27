"""
Test suite for Brand Guardian Agent

Tests brand compliance checking functionality,
ensuring LLM-based analysis produces correct PASS/FAIL
assessments with proper violation categorization.
"""

import pytest
import json
from unittest.mock import AsyncMock, patch

from backend.agents.safety.brand_guardian import brand_guardian, BrandGuardianAgent
from backend.models.safety import BrandAnalysisReport


class TestBrandGuardianAgent:
    """Test BrandGuardianAgent core functionality"""

    @pytest.fixture
    def agent(self):
        """Create a fresh agent instance for each test"""
        return BrandGuardianAgent()

    def test_agent_initialization(self, agent):
        """Test agent initializes with brand guidelines"""
        assert hasattr(agent, 'brand_guidelines')
        assert "PROFESSIONAL TONE" in agent.brand_guidelines
        assert "FORBIDDEN TOPICS" in agent.brand_guidelines
        assert "COMPETITOR POLICY" in agent.brand_guidelines

    def test_get_effective_guidelines_default(self, agent):
        """Test effective guidelines with no workspace config"""
        guidelines = agent._get_effective_guidelines(None)
        assert guidelines == agent.brand_guidelines

    def test_get_effective_guidelines_with_workspace(self, agent):
        """Test effective guidelines with workspace-specific config"""
        workspace_config = {
            "brand_guidelines": {
                "prohibited_terms": ["competitor_x", "competitor_y"],
                "required_tone": "formal business",
                "brand_voice": "corporate professional"
            }
        }

        guidelines = agent._get_effective_guidelines(workspace_config)

        # Should contain both default and workspace-specific guidelines
        assert "PROFESSIONAL TONE" in guidelines
        assert "competitor_x" in guidelines
        assert "formal business" in guidelines
        assert "corporate professional" in guidelines

    def test_build_evaluation_prompt_basic(self, agent):
        """Test evaluation prompt construction"""
        text = "Test content here"
        guidelines = "Test guidelines"

        prompt = agent._build_evaluation_prompt(text, guidelines)

        assert "Test content here" in prompt
        assert "Test guidelines" in prompt
        assert "BRAND GUARDIAN EVALUATION TASK" in prompt
        assert '"status"' in prompt
        assert '"reason"' in prompt
        assert '"category"' in prompt

    @pytest.mark.asyncio
    async def test_check_brand_alignment_pass_success(self):
        """Test successful PASS response from LLM"""
        pass_response = {
            "status": "PASS",
            "reason": "Content aligns with brand guidelines",
        }

        with patch('backend.services.vertex_ai_client.generate_json', new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = pass_response

            agent = BrandGuardianAgent()
            report = await agent.check_brand_alignment("Safe content")

            assert isinstance(report, BrandAnalysisReport)
            assert report.status == "PASS"
            assert report.reason == "Content aligns with brand guidelines"
            assert report.category is None
            assert report.confidence is None

    @pytest.mark.asyncio
    async def test_check_brand_alignment_fail_tone_violation(self):
        """Test FAIL response for tone violation"""
        fail_response = {
            "status": "FAIL",
            "reason": "Uses overly casual language, violating the professional tone requirement",
            "category": "TONE_VIOLATION",
            "confidence": 0.85
        }

        with patch('backend.services.vertex_ai_client.generate_json', new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = fail_response

            agent = BrandGuardianAgent()
            report = await agent.check_brand_alignment("Hey guys! This is awesome!")

            assert report.status == "FAIL"
            assert "casual language" in report.reason.lower()
            assert report.category == "TONE_VIOLATION"
            assert report.confidence == 0.85

    @pytest.mark.asyncio
    async def test_check_brand_alignment_fail_forbidden_topic(self):
        """Test FAIL response for forbidden topic"""
        fail_response = {
            "status": "FAIL",
            "reason": "Discussion of politics is prohibited",
            "category": "FORBIDDEN_TOPIC",
            "confidence": 0.92
        }

        with patch('backend.services.vertex_ai_client.generate_json', new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = fail_response

            agent = BrandGuardianAgent()
            report = await agent.check_brand_alignment("Politics is important for our business")

            assert report.status == "FAIL"
            assert "politics" in report.reason.lower()
            assert report.category == "FORBIDDEN_TOPIC"
            assert report.confidence == 0.92

    @pytest.mark.asyncio
    async def test_check_brand_alignment_fail_competitor(self):
        """Test FAIL response for competitor mention"""
        fail_response = {
            "status": "FAIL",
            "reason": "Direct competitor comparison violates brand policy",
            "category": "COMPETITOR_MENTION",
            "confidence": 0.78
        }

        with patch('backend.services.vertex_ai_client.generate_json', new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = fail_response

            agent = BrandGuardianAgent()
            report = await agent.check_brand_alignment("Better than our competitor")

            assert report.status == "FAIL"
            assert "competitor" in report.reason.lower()
            assert report.category == "COMPETITOR_MENTION"
            assert report.confidence == 0.78

    @pytest.mark.asyncio
    async def test_check_brand_alignment_invalid_status(self):
        """Test handling of invalid status from LLM"""
        invalid_response = {
            "status": "INVALID_STATUS",
            "reason": "Some analysis",
            "category": "TONE_VIOLATION"
        }

        with patch('backend.services.vertex_ai_client.generate_json', new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = invalid_response

            agent = BrandGuardianAgent()
            report = await agent.check_brand_alignment("Content with invalid status")

            # Should default to PASS with fallback reason
            assert report.status == "PASS"
            assert "default brand checks" in report.reason

    @pytest.mark.asyncio
    async def test_check_brand_alignment_parse_error(self):
        """Test handling of unparseable LLM response"""
        with patch('backend.services.vertex_ai_client.generate_json', new_callable=AsyncMock) as mock_generate:
            # Simulate parsing error by returning non-dict
            mock_generate.return_value = "Not a dictionary"

            agent = BrandGuardianAgent()
            report = await agent.check_brand_alignment("Content that breaks parsing")

            # Should return fallback PASS
            assert report.status == "PASS"
            assert "error" in report.reason or "unavailable" in report.reason
            assert report.confidence is None or report.confidence < 0.5

    @pytest.mark.asyncio
    async def test_check_brand_alignment_llm_exception(self):
        """Test handling of LLM service exceptions"""
        with patch('backend.services.vertex_ai_client.generate_json', side_effect=Exception("LLM Service Down")):
            agent = BrandGuardianAgent()
            report = await agent.check_brand_alignment("Content when LLM fails")

            # Should return conservative fallback
            assert report.status == "PASS"
            assert ("error" in report.reason.lower() or
                   "unavailable" in report.reason.lower())
            assert report.confidence < 0.5 if report.confidence else True

    @pytest.mark.asyncio
    async def test_check_brand_alignment_missing_fields(self):
        """Test handling of incomplete LLM response"""
        incomplete_response = {"status": "PASS"}  # Missing required fields

        with patch('backend.services.vertex_ai_client.generate_json', new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = incomplete_response

            agent = BrandGuardianAgent()
            report = await agent.check_brand_alignment("Content with partial response")

            # Should handle gracefully despite missing fields
            assert report.status == "PASS"
            assert report.reason is not None  # Should use default or fallback

    @pytest.mark.asyncio
    async def test_check_brand_alignment_workspace_config(self):
        """Test brand analysis with workspace-specific configuration"""
        pass_response = {
            "status": "PASS",
            "reason": "Content aligns with workspace guidelines",
        }

        workspace_config = {
            "brand_guidelines": {
                "prohibited_terms": ["banned_word"],
                "required_tone": "technical"
            }
        }

        with patch('backend.services.vertex_ai_client.generate_json', new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = pass_response

            agent = BrandGuardianAgent()
            report = await agent.check_brand_alignment(
                "Technical content here",
                workspace_config
            )

            # Verify the call included workspace config
            call_args = mock_generate.call_args
            prompt_arg = call_args[1]['prompt']

            # Prompt should contain workspace-specific guidelines
            assert "banned_word" in prompt_arg
            assert "technical" in prompt_arg

    def test_get_system_prompt(self, agent):
        """Test system prompt content"""
        system_prompt = agent._get_system_prompt()

        assert "Brand Compliance Officer" in system_prompt
        assert "content moderation" in system_prompt
        assert "brand integrity" in system_prompt

    @pytest.mark.asyncio
    async def test_evaluate_content_quality_success(self):
        """Test advanced content quality evaluation"""
        quality_response = {
            "quality_score": 0.85,
            "strengths": ["Clear messaging", "Professional tone"],
            "suggestions": ["Add more examples"]
        }

        with patch('backend.services.vertex_ai_client.generate_json', new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = quality_response

            agent = BrandGuardianAgent()
            result = await agent.evaluate_content_quality("Test content")

            assert result["success"] == True
            assert result["quality_score"] == 0.85
            assert result["feedback"] == quality_response
            assert "correlation_id" in result

    @pytest.mark.asyncio
    async def test_evaluate_content_quality_failure(self):
        """Test content quality evaluation failure"""
        with patch('backend.services.vertex_ai_client.generate_json', side_effect=Exception("Service error")):
            agent = BrandGuardianAgent()
            result = await agent.evaluate_content_quality("Fail content")

            assert result["success"] == False
            assert "error" in result
            assert "correlation_id" in result

    def test_single_instance_pattern(self):
        """Test that brand_guardian is a singleton instance"""
        assert isinstance(brand_guardian, BrandGuardianAgent)
        assert hasattr(brand_guardian, 'check_brand_alignment')


class TestBrandAnalysisReport:
    """Test BrandAnalysisReport model functionality"""

    def test_report_creation_pass(self):
        """Test creating a PASS report"""
        report = BrandAnalysisReport(
            status="PASS",
            reason="Content aligns with brand guidelines"
        )

        assert report.status == "PASS"
        assert report.reason == "Content aligns with brand guidelines"
        assert report.category is None
        assert report.confidence is None

    def test_report_creation_fail_with_details(self):
        """Test creating a FAIL report with full details"""
        report = BrandAnalysisReport(
            status="FAIL",
            reason="Casual language detected",
            category="TONE_VIOLATION",
            confidence=0.87
        )

        assert report.status == "FAIL"
        assert report.reason == "Casual language detected"
        assert report.category == "TONE_VIOLATION"
        assert report.confidence == 0.87

    def test_report_with_optional_fields_none(self):
        """Test report with optional fields as None"""
        report = BrandAnalysisReport(
            status="PASS",
            reason="All good"
        )

        assert report.category is None
        assert report.confidence is None

        # Should not raise errors when accessing
        assert report.category is None
        assert report.confidence is None

    def test_report_model_dump(self):
        """Test report serialization"""
        report = BrandAnalysisReport(
            status="FAIL",
            reason="Violation found",
            category="FORBIDDEN_TOPIC",
            confidence=0.9
        )

        data = report.model_dump()

        assert data["status"] == "FAIL"
        assert data["reason"] == "Violation found"
        assert data["category"] == "FORBIDDEN_TOPIC"
        assert data["confidence"] == 0.9


class TestIntegrationScenarios:
    """Test real-world integration scenarios"""

    @pytest.mark.asyncio
    async def test_mixed_content_types(self):
        """Test various content types that should pass/fail"""
        test_cases = [
            # (content, expected_status, expected_category)
            ("Our solution delivers excellent results.", "PASS", None),
            ("Hey guys! This is awesome! 🔥", "FAIL", "TONE_VIOLATION"),
            ("Politics is important for democracy.", "FAIL", "FORBIDDEN_TOPIC"),
            ("Compare us to other solutions.", "FAIL", "COMPETITOR_MENTION"),
            ("We completely guarantee your success.", "FAIL", "QUALITY_ISSUE"),
        ]

        agent = BrandGuardianAgent()

        for content, expected_status, expected_category in test_cases:
            # Mock LLM response for each test
            mock_response = {
                "status": expected_status,
                "reason": f"Test response for: {content[:30]}...",
                "category": expected_category,
                "confidence": 0.8
            }

            with patch('backend.services.vertex_ai_client.generate_json', return_value=mock_response):
                report = await agent.check_brand_alignment(content)

                assert report.status == expected_status
                if expected_category:
                    assert report.category == expected_category
                else:
                    assert report.category is None

    @pytest.mark.asyncio
    async def test_brand_guideline_coverage(self):
        """Test that important brand guidelines are evaluated correctly"""
        # Test professional tone requirement
        professional_content = "Our solution enhances operational efficiency through advanced analytics."
        casual_content = "Stuff works pretty well, I guess."

        agent = BrandGuardianAgent()

        # Mock responses for professional vs casual
        pass_response = {"status": "PASS", "reason": "Professional tone"}
        fail_response = {"status": "FAIL", "reason": "Casual language", "category": "TONE_VIOLATION"}

        # Test professional content
        with patch('backend.services.vertex_ai_client.generate_json', return_value=pass_response):
            report = await agent.check_brand_alignment(professional_content)
            assert report.status == "PASS"

        # Test casual content
        with patch('backend.services.vertex_ai_client.generate_json', return_value=fail_response):
            report = await agent.check_brand_alignment(casual_content)
            assert report.status == "FAIL"
            assert report.category == "TONE_VIOLATION"

    @pytest.mark.asyncio
    async def test_violation_categories_coverage(self):
        """Test all expected violation categories"""
        violations_tests = [
            ("TONE_VIOLATION", "Hey folks! Check this out!"),
            ("FORBIDDEN_TOPIC", "Political opinions matter."),
            ("COMPETITOR_MENTION", "Unlike our competitors..."),
            ("INAPPROPRIATE_LANGUAGE", "This sucks!"),
            ("QUALITY_ISSUE", "We guarantee 100% success rate!"),
        ]

        agent = BrandGuardianAgent()

        for category, content in violations_tests:
            mock_response = {
                "status": "FAIL",
                "reason": f"{category} detected",
                "category": category,
                "confidence": 0.8
            }

            with patch('backend.services.vertex_ai_client.generate_json', return_value=mock_response):
                report = await agent.check_brand_alignment(content)

                assert report.status == "FAIL"
                assert report.category == category
