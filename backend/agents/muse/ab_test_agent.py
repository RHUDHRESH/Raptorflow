"""
A/B Test Variant Agent (MUS-009)

Muse Guild's creative copy agent specializing in marketing optimization.
Generates multiple creative variations of marketing copy tailored to specific
focuses like urgency, tone, simplicity, or benefit orientation.

Features:
- Dynamic prompt engineering for different creative focuses
- Expert copywriter role-playing for high-quality variations
- Structured JSON output for reliable parsing
- Multiple variant generation per request
- Error handling with graceful degradation

Variation Focuses:
- URGENCY: Creates scarcity and immediacy
- TONE: Multiple tone variations (professional, playful, empathetic)
- SIMPLICITY: Clear, simple language for broader appeal
- BENEFIT_ORIENTED: Focus on customer benefits and value
- EMOTIONAL: Emotional connection and storytelling
- QUESTIONS: Curiosity-driven question format

Creative Process:
1. Analyze original text and requested focus
2. Build tailored prompt for expert copywriter role
3. Generate specified number of variations
4. Return structured report with evidence-based suggestions
"""

import json
import structlog
from typing import Dict, Any, List, Optional

from backend.models.muse import VariantRequest, VariantReport, CreativeBatchRequest, CreativeBatchResponse
from backend.services.vertex_ai_client import vertex_ai_client
from backend.utils.correlation import get_correlation_id

logger = structlog.get_logger(__name__)


class ABTestAgent:
    """
    MUS-009: A/B Test Variant Agent for marketing copy optimization.

    This agent specializes in generating creative variations of marketing copy
    to support A/B testing campaigns. Using sophisticated prompt engineering
    and expert copywriter guidance, it produces multiple high-quality alternatives
    focused on specific creative strategies that can drive better engagement.

    Key Capabilities:
    - Dynamic focus-based variation generation
    - Expert copywriter role-playing for quality
    - Structured JSON output for reliable automation
    - Multiple variants per request for comprehensive testing
    - Error handling and fallback mechanisms

    Creative Strategies:
    - URGENCY: Scarcity, limited time, FOMO elements
    - TONE: Professional, playful, empathetic variations
    - SIMPLICITY: Clear, accessible language for broader reach
    - BENEFITS: Customer-centric value propositions
    - EMOTIONAL: Storytelling and emotional connections
    - QUESTIONS: Curiosity-driven engagement hooks

    Integration Points:
    - Marketing teams for campaign optimization
    - Content teams for messaging refinement
    - Product teams for value proposition testing
    - Automated A/B testing workflows
    """

    def __init__(self):
        """Initialize the A/B Test Variant Agent."""
        logger.info("A/B Test Variant Agent (MUS-009) initialized")

        # Available variation focuses with their descriptions
        self.focus_instructions = {
            "URGENCY": "Rewrite the text to create a strong sense of immediacy, scarcity, and urgency. Include elements like limited time offers, countdown language, or fear of missing out. Make the reader feel they need to act now or risk losing out.",

            "TONE": "Rewrite the text in three distinct tones: 1) Professional/Corporate tone (authoritative and business-like), 2) Playful/Casual tone (friendly and approachable), and 3) Empathetic/Understanding tone (supportive and understanding of customer needs).",  # Note: Always generates 3 variants regardless of requested number

            "SIMPLICITY": "Rewrite the text to be as clear and simple as possible. Use short words and sentences (aim for 5th-grade reading level). Remove jargon and complex terminology. Make it easy to understand quickly, prioritizing clarity over sophistication.",

            "BENEFIT_ORIENTED": "Rewrite the text to focus exclusively on customer benefits and outcomes. Emphasize what the customer gains, how it improves their life/situation, and the positive results they can expect. Remove or minimize features/specifications in favor of benefits.",

            "EMOTIONAL": "Rewrite the text to connect emotionally with the reader. Use storytelling elements, address feelings/concerns, or create an emotional journey. Make it relatable and human-centered rather than purely logical or feature-based.",

            "QUESTIONS": "Rewrite the text as a series of engaging questions that spark curiosity and make the reader think differently. Transform statements into questions that highlight problems, desires, or possibilities. Create intrigue and conversation.",

            "SOCIAL_PROOF": "Rewrite the text to incorporate social proof elements. Include references to trust indicators like customer testimonials, user counts, awards, or industry recognition. Make it feel like others are already benefiting.",

            "RISK_REVERSAL": "Rewrite the text focusing on risk elimination. Address potential concerns, remove obstacles, and provide guarantees. Make the reader feel completely safe and confident in their decision.",

            "EXCLUSIVITY": "Rewrite the text to emphasize exclusivity and premium positioning. Include elements of prestige, special access, or VIP treatment. Make it feel special and discerning.",

            "PROBLEM_SOLUTION": "Rewrite the text following the classic problem-agitate-solution format. Clearly state the problem, make the reader feel the pain, then present your solution as the ideal resolution."
        }

        # Default focus for unrecognized types
        self.default_focus_instruction = "Rewrite the text to create multiple creative variations that would work well for A/B testing. Each variation should offer a different perspective or approach while maintaining the core message. Make them different enough to show statistically significant results but still true to the original intent."

    async def generate_variants(self, request: VariantRequest) -> VariantReport:
        """
        Generate creative variations of marketing copy based on specified focus.

        This is the main API method for creating A/B testing variants. It takes
        the original text and generates creative alternatives focused on specific
        marketing psychology principles that can drive better engagement.

        Args:
            request: VariantRequest containing original text, focus, and variant count

        Returns:
            VariantReport with the original text, focus, and generated variants

        Example:
            request = VariantRequest(
                original_text="Buy our product today!",
                variation_focus="URGENCY",
                number_of_variants=3
            )
            report = await agent.generate_variants(request)
            # Returns 3 urgency-focused variations
        """
        correlation_id = get_correlation_id()

        logger.info(
            "Generating copy variants",
            text_length=len(request.original_text),
            focus=request.variation_focus,
            variant_count=request.number_of_variants,
            correlation_id=correlation_id
        )

        try:
            # Build dynamic prompt based on focus
            prompt = self._build_variant_prompt(request)

            # Generate variants using LLM
            variants = await self._generate_with_llm(prompt, request, correlation_id)

            # Create report
            report = VariantReport(
                original_text=request.original_text,
                focus=request.variation_focus,
                variants=variants
            )

            logger.info(
                "Variant generation completed successfully",
                variants_generated=len(variants),
                correlation_id=correlation_id
            )

            return report

        except Exception as e:
            logger.error(
                "Variant generation failed",
                error=str(e),
                focus=request.variation_focus,
                correlation_id=correlation_id
            )

            # Return fallback report
            return VariantReport(
                original_text=request.original_text,
                focus=request.variation_focus,
                variants=[request.original_text]  # Fallback to original if all else fails
            )

    async def generate_batch_variants(self, batch_request: CreativeBatchRequest) -> CreativeBatchResponse:
        """
        Generate variants for multiple pieces of marketing copy.

        Processes multiple variant requests efficiently, useful for
        optimizing entire marketing campaigns or testing multiple elements.

        Args:
            batch_request: CreativeBatchRequest containing multiple variant requests

        Returns:
            CreativeBatchResponse with variant reports for all requests

        Example:
            batch = CreativeBatchRequest(variants=[
                VariantRequest(original_text="CTA 1", variation_focus="URGENCY"),
                VariantRequest(original_text="CTA 2", variation_focus="SIMPLICITY")
            ])
            response = await agent.generate_batch_variants(batch)
        """
        correlation_id = get_correlation_id()

        logger.info(
            "Processing batch variant generation",
            request_count=len(batch_request.variants),
            correlation_id=correlation_id
        )

        reports = []
        for i, variant_request in enumerate(batch_request.variants):
            logger.debug(f"Processing variant request {i + 1}")
            report = await self.generate_variants(variant_request)
            reports.append(report)

        response = CreativeBatchResponse(
            reports=reports,
            total_requests=len(batch_request.variants)
        )

        logger.info(
            "Batch variant generation completed",
            total_requests=len(batch_request.variants),
            correlation_id=correlation_id
        )

        return response

    def _build_variant_prompt(self, request: VariantRequest) -> str:
        """
        Build a dynamic LLM prompt based on the requested variation focus.

        Creates a tailored prompt that guides the LLM to act as an expert
        copywriter specializing in the specific creative focus requested.

        Args:
            request: VariantRequest with text, focus, and count

        Returns:
            Structured prompt for the LLM
        """
        # Get focus-specific instructions
        focus_instruction = self.focus_instructions.get(
            request.variation_focus.upper(),
            self.default_focus_instruction
        )

        # Handle TONE special case (always generates 3 variants)
        if request.variation_focus.upper() == "TONE":
            variant_count = 3
            variant_note = "(Note: TONE focus always generates 3 variants - one for each tone style)"
        else:
            variant_count = min(request.number_of_variants, 10)  # Cap at 10
            variant_note = ""

        prompt = f"""
EXPERT DIRECT-RESPONSE COPYWRITER TASK

You are an expert direct-response copywriter with 15+ years of experience in A/B testing and conversion optimization. Your specialty is creating compelling variations that outperform control versions.

ORIGINAL TEXT TO OPTIMIZE:
"{request.original_text}"

CREATIVE FOCUS: {request.variation_focus.upper()}

FOCUS INSTRUCTIONS:
{focus_instruction}

REQUIREMENTS:
- Generate exactly {variant_count} creative variations
- Each variation must be different enough for meaningful A/B testing
- Maintain the core message and intent of the original text
- Keep variations similar in length to the original (if applicable)
- Focus on psychological triggers and emotional responses
- Ensure all variations are appropriate and conversion-focused

{variant_note}

OUTPUT FORMAT:
Return ONLY a valid JSON object with one key: 'variants', which is a list of exactly {variant_count} strings representing your creative variations.

Example format: {{"variants": ["Variation 1 here", "Variation 2 here", "Variation 3 here"]}}

CRITICAL: Ensure the JSON is valid and the variants list has exactly {variant_count} items.
"""
        return prompt

    async def _generate_with_llm(
        self,
        prompt: str,
        request: VariantRequest,
        correlation_id: str
    ) -> List[str]:
        """
        Execute LLM generation with error handling and parsing.

        Args:
            prompt: Complete LLM prompt
            request: Original request for context
            correlation_id: Request correlation ID

        Returns:
            List of generated variants

        Raises:
            Exception: If LLM call fails and can't be recovered
        """
        try:
            llm_response = await vertex_ai_client.generate_json(
                prompt=prompt,
                system_prompt=self._get_copywriter_system_prompt(),
                model_type="creative",  # Use creative model for copy generation
                temperature=0.8,        # Higher creativity for variations
                max_tokens=1000         # Allow room for multiple variants
            )

            # Parse and validate the response
            variants = self._parse_variant_response(llm_response, request, correlation_id)

            return variants

        except Exception as e:
            logger.warning(
                "LLM variant generation failed, trying fallback method",
                error=str(e),
                correlation_id=correlation_id
            )

            # Try fallback with simpler prompt
            return await self._fallback_variant_generation(request, correlation_id)

    def _get_copywriter_system_prompt(self) -> str:
        """
        Get the system prompt defining the LLM's role as a copywriter.

        Returns:
            System instruction for copywriter behavior
        """
        return """You are an expert direct-response copywriter specializing in A/B testing and marketing optimization. You have 15+ years of experience creating copy variations that significantly improve conversion rates across email, landing pages, buttons, headlines, and CTAs.

Your expertise includes:
- Psychological triggers and consumer behavior
- Tone, urgency, and emotional manipulation for better engagement
- Simplicity and clarity for broader audience appeal
- Benefit-focused messaging that speaks to customer needs
- Question-based copy that creates curiosity and engagement
- Social proof and risk reversal techniques
- A/B testing best practices and statistical significance

You excel at creating compelling, conversion-focused copy variations that maintain brand voice while dramatically improving performance. Your variations are always ethical, effective, and targeted for measurable business results.

Key principles:
- Test different psychological approaches for each variant
- Maintain core value proposition while varying approach
- Focus on emotional and logical triggers for engagement
- Consider audience psychology and decision-making patterns
- Balance creativity with tested conversion principles"""

    def _parse_variant_response(
        self,
        llm_response: Dict[str, Any],
        request: VariantRequest,
        correlation_id: str
    ) -> List[str]:
        """
        Parse and validate the LLM response containing variants.

        Args:
            llm_response: Raw LLM response with variants
            request: Original request for validation context
            correlation_id: Request correlation ID

        Returns:
            List of variant strings

        Raises:
            Exception: If response cannot be properly parsed
        """
        try:
            # Extract variants from response
            variants = llm_response.get("variants", [])

            if not isinstance(variants, list):
                logger.warning("LLM returned variants in wrong format", correlation_id=correlation_id)
                raise ValueError("Variants not in expected list format")

            # Filter out empty strings and validate
            valid_variants = []
            for i, variant in enumerate(variants):
                if isinstance(variant, str) and variant.strip():
                    clean_variant = variant.strip()
                    if len(clean_variant) > 0 and len(clean_variant) <= 5000:  # Reasonable length limit
                        valid_variants.append(clean_variant)

            if not valid_variants:
                logger.warning("No valid variants found in LLM response", correlation_id=correlation_id)
                raise ValueError("No valid variants in response")

            # Special handling for TONE focus (should have exactly 3 variants)
            if request.variation_focus.upper() == "TONE" and len(valid_variants) < 3:
                logger.warning("TONE focus should have 3 variants but got fewer", correlation_id=correlation_id)
                # Pad with original text or generate simple variations
                while len(valid_variants) < 3:
                    valid_variants.append(request.original_text)

            # Ensure we have the requested number of variants (up to the available valid ones)
            target_count = request.number_of_variants
            if len(valid_variants) > target_count:
                valid_variants = valid_variants[:target_count]
            elif len(valid_variants) < target_count:
                logger.warning(f"Returned {len(valid_variants)} variants but {target_count} requested", correlation_id=correlation_id)
                # Duplicate the last variant to meet count (rare edge case)
                while len(valid_variants) < target_count:
                    valid_variants.append(valid_variants[-1])

            logger.debug(
                f"Successfully parsed {len(valid_variants)} variants",
                correlation_id=correlation_id
            )

            return valid_variants

        except Exception as e:
            logger.error(
                "Failed to parse variant response",
                error=str(e),
                response_keys=list(llm_response.keys()) if isinstance(llm_response, dict) else None,
                correlation_id=correlation_id
            )
            raise

    async def _fallback_variant_generation(
        self,
        request: VariantRequest,
        correlation_id: str
    ) -> List[str]:
        """
        Fallback variant generation when primary method fails.

        Uses simple transformation rules based on the focus to provide
        basic variations if the LLM is unavailable.

        Args:
            request: Original variant request
            correlation_id: Request correlation ID

        Returns:
            List of basic fallback variants
        """
        logger.info("Using fallback variant generation", correlation_id=correlation_id)

        variants = []
        base_text = request.original_text

        # Simple fallback strategies based on focus
        focus = request.variation_focus.upper()

        if focus == "URGENCY":
            variants = [
                f"⚡ {base_text} - Act Now!",
                f"LIMITED TIME: {base_text}",
                f"{base_text} - Don't Wait!"
            ]
        elif focus == "SIMPLICITY":
            # Simple fallback - remove complex words and shorten
            variants = [
                base_text.replace("experience", "try").replace("solution", "fix"),
                f"It's simple: {base_text.lower()}",
                base_text[:50] + "..." if len(base_text) > 50 else base_text
            ]
        elif focus == "BENEFIT_ORIENTED":
            variants = [
                f"Get the benefits: {base_text}",
                f"You'll love how {base_text.lower()}",
                f"Experience the advantages: {base_text}"
            ]
        elif focus == " QUESTIONS":
            variants = [
                f"Ready for {base_text.lower()}? Here's why:",
                f"Ever wanted {base_text.lower()}? Here's your chance.",
                f"What if {base_text.lower()}? Discover more."
            ]
        else:
            # Generic fallback variations
            variants = [
                f"{base_text}!",
                f"→ {base_text} ↓",
                f"Discover: {base_text}"
            ]

        # Ensure we have at least one variant and match requested count
        if not variants:
            variants = [base_text]

        variants = variants[:request.number_of_variants]

        logger.info(
            f"Generated {len(variants)} fallback variants",
            correlation_id=correlation_id
        )

        return variants

    def get_available_focuses(self) -> List[str]:
        """
        Get list of all available variation focuses.

        Returns:
            List of supported focus identifiers
        """
        return list(self.focus_instructions.keys())

    def get_focus_description(self, focus: str) -> Optional[str]:
        """
        Get detailed description of a specific focus.

        Args:
            focus: Focus identifier to describe

        Returns:
            Focus description or None if focus doesn't exist
        """
        return self.focus_instructions.get(focus.upper())

    async def generate_with_context(
        self,
        request: VariantRequest,
        context: Optional[Dict[str, Any]] = None
    ) -> VariantReport:
        """
        Generate variants with additional context for more sophisticated suggestions.

        Enhanced generation that considers content type, target audience,
        brand personality, and industry context for more relevant variations.

        Args:
            request: Base variant request
            context: Additional context information

        Returns:
            Enhanced variant report
        """
        if context:
            # Enhance the request with context information
            correlation_id = get_correlation_id()

            # Add context to the system prompt for more relevant generation
            contextual_system_prompt = self._build_contextual_system_prompt(context)

            # Build prompt with context
            prompt = self._build_contextual_prompt(request, context)

            try:
                llm_response = await vertex_ai_client.generate_json(
                    prompt=prompt,
                    system_prompt=contextual_system_prompt,
                    model_type="creative",
                    temperature=0.8,
                    max_tokens=1200
                )

                variants = self._parse_variant_response(llm_response, request, correlation_id)

                return VariantReport(
                    original_text=request.original_text,
                    focus=request.variation_focus,
                    variants=variants
                )

            except Exception as e:
                logger.warning(
                    "Contextual generation failed, falling back to standard method",
                    error=str(e),
                    correlation_id=correlation_id
                )

        # Fall back to standard generation
        return await self.generate_variants(request)

    def _build_contextual_system_prompt(self, context: Dict[str, Any]) -> str:
        """Build enhanced system prompt with context awareness."""
        base_prompt = self._get_copywriter_system_prompt()

        context_prompt = f"""
{base_prompt}

ADDITIONAL CONTEXT FOR THIS GENERATION:
- Content Type: {context.get('content_type', 'General marketing copy')}
- Target Audience: {context.get('target_audience', 'General audience')}
- Brand Personality: {context.get('brand_personality', 'Professional')}
- Industry: {context.get('industry', 'General business')}

Tailor your copy variations to be specifically relevant to this context. Consider the audience's preferences, the content format requirements, and the industry standards when creating variations."""

        return context_prompt

    def _build_contextual_prompt(self, request: VariantRequest, context: Dict[str, Any]) -> str:
        """Build prompt enhanced with context information."""
        base_prompt = self._build_variant_prompt(request)

        context_addition = f"""
CONTEXT INFORMATION:
- Content Type: {context.get('content_type', 'General marketing copy')}
- Target Audience: {context.get('target_audience', 'General audience')}
- Brand Personality: {context.get('brand_personality', 'Professional')}
- Industry: {context.get('industry', 'General business')}

Consider this context when generating variations to make them more relevant and effective."""

        enhanced_prompt = base_prompt.replace("REQUIREMENTS:", f"{context_addition}\n\nREQUIREMENTS:")
        return enhanced_prompt


# Global singleton instance
ab_test_agent = ABTestAgent()
