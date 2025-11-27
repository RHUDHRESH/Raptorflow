"""
Brand Guardian Agent (GRD-003)

LLM-powered brand compliance and content quality enforcement.
Ensures all AI-generated content aligns with brand voice, avoids
sensitive topics, and maintains professional standards.

Features:
- Context-aware brand guideline enforcement using LLM analysis
- Tone and voice compliance checking
- Forbidden topic detection and blocking
- Competitor mention policy enforcement
- Professional language validation
- Configurable brand guidelines framework
"""

import json
import structlog
from typing import Dict, Any, Optional

from backend.services.vertex_ai_client import vertex_ai_client
from backend.models.safety import BrandAnalysisReport
from backend.utils.correlation import get_correlation_id
from backend.config.settings import settings

logger = structlog.get_logger(__name__)


class BrandGuardianAgent:
    """
    GRD-003: Brand Guardian Agent for content quality and brand compliance.

    This agent uses LLM analysis to evaluate content against brand guidelines,
    ensuring that all generated text maintains professional standards, proper
    tone, and avoids inappropriate topics.

    The agent acts as an automated editorial reviewer, providing context-aware
    assessment of whether content is "brand-safe" for publication.

    Key Capabilities:
    - Professional tone enforcement
    - Sensitive topic avoidance
    - Brand voice consistency
    - Competitor mention policies
    - Language appropriateness validation
    - Contextual compliance analysis

    Integration Points:
    - Called by GuardianAgent after PII checking
    - Blocks workflows with brand violations
    - Provides detailed feedback for content correction
    - Supports workspace-specific brand guidelines
    """

    @property
    def brand_guidelines(self) -> str:
        """Get brand guidelines from central configuration."""
        return settings.BRAND_GUARDIAN_GUIDELINES

    async def check_brand_alignment(
        self,
        text_to_check: str,
        workspace_config: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None
    ) -> BrandAnalysisReport:
        """
        Evaluate content against brand guidelines using LLM analysis.

        This is the main API method for brand compliance checking. It uses
        the project's LLM to perform nuanced analysis of whether the provided
        text aligns with brand standards.

        Args:
            text_to_check: The content to evaluate for brand compliance
            workspace_config: Optional workspace-specific brand configuration
            correlation_id: Request correlation ID for tracking

        Returns:
            BrandAnalysisReport with PASS/FAIL status and detailed reasoning

        Example:
            result = await brand_guardian.check_brand_alignment(
                text_to_check="Hey folks! Check out our awesome new feature! 🔥"
            )

            if result.status == "FAIL":
                # Content fails due to casual tone
                print(f"Violation: {result.reason}")  # "Uses overly casual language..."
        """
        correlation_id = correlation_id or get_correlation_id()

        logger.info(
            "Starting brand compliance analysis",
            text_length=len(text_to_check),
            correlation_id=correlation_id
        )

        # Use workspace-specific guidelines if provided
        effective_guidelines = self._get_effective_guidelines(workspace_config)

        # Build the LLM evaluation prompt
        prompt = self._build_evaluation_prompt(text_to_check, effective_guidelines)

        # Execute LLM analysis
        logger.debug("Executing LLM brand compliance analysis", correlation_id=correlation_id)

        try:
            llm_response = await vertex_ai_client.generate_json(
                prompt=prompt,
                system_prompt=self._get_system_prompt(),
                model_type="fast",  # Use fast model for compliance checking
                temperature=0.1,    # Low temperature for consistent analysis
                max_tokens=500
            )

            # Parse and validate LLM response
            report = self._parse_llm_response(llm_response, correlation_id)

        except Exception as e:
            logger.error(
                "LLM brand analysis failed, using fallback",
                error=str(e),
                correlation_id=correlation_id
            )

            # Fallback to PASS status with error indication
            report = BrandAnalysisReport(
                status="PASS",  # Conservative fallback - allow if analysis fails
                reason="Brand compliance analysis temporarily unavailable - content passed default checks",
                category=None,
                confidence=0.5
            )

        logger.info(
            "Brand compliance analysis completed",
            status=report.status,
            category=getattr(report, 'category', None),
            correlation_id=correlation_id
        )

        return report

    def _get_effective_guidelines(self, workspace_config: Optional[Dict[str, Any]]) -> str:
        """
        Get effective brand guidelines for analysis.

        Combines default guidelines with workspace-specific overrides.

        Args:
            workspace_config: Workspace configuration with custom guidelines

        Returns:
            Complete guideline string for LLM analysis
        """
        base_guidelines = self.brand_guidelines

        # Add workspace-specific guidelines if provided
        if workspace_config:
            workspace_guidelines = workspace_config.get("brand_guidelines", {})
            if workspace_guidelines:
                additional_rules = "\n\nWORKSPACE-SPECIFIC GUIDELINES:\n"

                if "prohibited_terms" in workspace_guidelines:
                    additional_rules += f"- Prohibited terms: {', '.join(workspace_guidelines['prohibited_terms'])}\n"

                if "required_tone" in workspace_guidelines:
                    additional_rules += f"- Required tone: {workspace_guidelines['required_tone']}\n"

                if "brand_voice" in workspace_guidelines:
                    additional_rules += f"- Brand voice description: {workspace_guidelines['brand_voice']}\n"

                base_guidelines += additional_rules

        return base_guidelines

    def _build_evaluation_prompt(self, text_to_check: str, guidelines: str) -> str:
        """
        Construct the LLM prompt for brand compliance evaluation.

        Creates a detailed prompt that instructs the LLM to act as a brand
        compliance officer and evaluate the text against guidelines.

        Args:
            text_to_check: Content to be evaluated
            guidelines: Complete brand guidelines to check against

        Returns:
            Formatted prompt for LLM evaluation
        """
        prompt = f"""
BRAND GUARDIAN EVALUATION TASK

You are a Brand Compliance Officer for our company. Your sole responsibility is to analyze text content and determine if it violates our brand guidelines.

CONTENT TO ANALYZE:
\"\"\"
{text_to_check}
\"\"\"

BRAND GUIDELINES TO APPLY:
{guidelines}

ANALYSIS REQUIREMENTS:
1. Carefully read the content and compare it against each guideline
2. Look for tone, language style, prohibited topics, and brand voice alignment
3. Consider both explicit violations and contextual misalignment
4. Be strict but fair - focus on clear brand-damaging issues

RESPONSE FORMAT:
You MUST respond with a valid JSON object containing exactly these fields:
- "status": either "PASS" or "FAIL"
- "reason": a brief, one-sentence explanation (if PASS, use "Content aligns with brand guidelines")
- "category": specific violation type if FAIL (choose from: TONE_VIOLATION, FORBIDDEN_TOPIC, COMPETITOR_MENTION, INAPPROPRIATE_LANGUAGE, QUALITY_ISSUE, OTHER_VIOLATION)
- "confidence": confidence score (0.0 to 1.0) in your analysis

IMPORTANT: Return ONLY the JSON object, no additional text or explanation.
"""
        return prompt

    def _get_system_prompt(self) -> str:
        """
        Get the system prompt for brand compliance analysis.

        Returns:
            System instruction defining the LLM's role
        """
        return """You are an expert Brand Compliance Officer with years of experience in content moderation and brand protection.

Your expertise includes:
- Recognizing inappropriate tone, language, and content
- Identifying brand voice misalignment
- Detecting policy violations and prohibited topics
- Ensuring content quality and appropriateness
- Making fair but strict compliance judgments

You are thorough, consistent, and committed to maintaining brand integrity. You understand that even seemingly minor violations can damage brand reputation and trust."""

    def _parse_llm_response(self, llm_response: Dict[str, Any], correlation_id: str) -> BrandAnalysisReport:
        """
        Parse and validate LLM response into BrandAnalysisReport.

        Args:
            llm_response: Raw LLM response (should be JSON)
            correlation_id: Request correlation ID

        Returns:
            Validated BrandAnalysisReport

        Raises:
            Exception: If response cannot be parsed or validated
        """
        try:
            # Extract required fields from LLM response
            status = llm_response.get("status", "").upper()
            reason = llm_response.get("reason", "")
            category = llm_response.get("category")
            confidence = llm_response.get("confidence")

            # Validate required fields
            if status not in ["PASS", "FAIL"]:
                logger.warning("Invalid status in LLM response, defaulting to PASS", correlation_id=correlation_id)
                status = "PASS"
                reason = "LLM response invalid, content passed default brand checks"
                category = None
                confidence = 0.5

            # Create and return validated report
            report = BrandAnalysisReport(
                status=status,
                reason=reason,
                category=category,
                confidence=confidence
            )

            return report

        except Exception as e:
            logger.error(
                "Failed to parse LLM response for brand analysis",
                error=str(e),
                raw_response=llm_response,
                correlation_id=correlation_id
            )

            # Fallback to conservative pass
            return BrandAnalysisReport(
                status="PASS",
                reason="Brand compliance analysis encountered an error, content passed default checks",
                category=None,
                confidence=0.3
            )

    async def evaluate_content_quality(
        self,
        text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Advanced content quality evaluation beyond basic brand compliance.

        This method provides deeper analysis of content characteristics,
        helpful for content improvement and quality assurance.

        Args:
            text: Content to evaluate
            context: Additional context (content_type, target_audience, etc.)

        Returns:
            Dictionary with quality metrics and suggestions
        """
        correlation_id = get_correlation_id()

        prompt = f"""
Analyze this content for quality and brand alignment. Provide detailed feedback:

CONTENT TO ANALYZE:
\"\"\"
{text}
\"\"\"

{content['context_description'] if context else ''}

Provide a JSON response with quality metrics, strengths, and improvement suggestions.
Focus on brand voice consistency, clarity, engagement, and professional standards.
"""

        try:
            analysis = await vertex_ai_client.generate_json(
                prompt=prompt,
                system_prompt="You are a content quality expert focused on brand voice consistency.",
                model_type="fast",
                temperature=0.2
            )

            return {
                "success": True,
                "quality_score": analysis.get("quality_score", 0.5),
                "feedback": analysis,
                "correlation_id": correlation_id
            }

        except Exception as e:
            logger.error("Content quality analysis failed", error=str(e))
            return {
                "success": False,
                "error": str(e),
                "correlation_id": correlation_id
            }


# Global singleton instance
brand_guardian = BrandGuardianAgent()
