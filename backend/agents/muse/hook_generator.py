"""
Hook Generator (MUS-008)

Muse Guild's viral content specialist. Creates compelling, scroll-stopping
hooks designed to capture attention in short-form content, social media,
and digital advertising.

Features:
- Viral hook generation for various topics
- Attention-grabbing opening lines
- Scroll-stopping copy techniques
- Social media optimized formats
- Error handling and quality assurance

Generation Flow:
1. Receive topic and context
2. Generate 5 viral hooks using proven formulas
3. Format for immediate impact and engagement
4. Return curated hook collection
"""

import structlog
from typing import List

from backend.models.muse import HookRequest, HookReport
from backend.services.vertex_ai_client import vertex_ai_client
from backend.utils.correlation import get_correlation_id

logger = structlog.get_logger(__name__)


class HookGeneratorAgent:
    """
    MUS-008: Hook Generator Agent for viral content creation.

    This agent specializes in creating attention-grabbing, share-worthy
    hooks that stop the scroll and drive engagement across social platforms.
    It uses proven viral content formulas and psychological triggers to
    maximize immediate attention and curiosity.

    Key Capabilities:
    - Viral hook creation using psychological triggers
    - Scroll-stopping copy techniques
    - Social media optimized formats
    - Topic-relevant hook generation
    - Batch hook production for content series

    Hook Types Generated:
    - Question hooks that spark curiosity
    - Contrarian statements that challenge norms
    - Statement hooks that make bold claims
    - Numbered lists that promise value
    - Story hooks that create emotional connection

    Integration Points:
    - Social media managers for viral content creation
    - Video creators for attention-grabbing openings
    - Advertising teams for click-worthy headlines
    - Content creators for engagement optimization
    - Marketing teams for campaign hooks
    """

    def __init__(self):
        """Initialize the Hook Generator Agent."""
        logger.info("Hook Generator Agent (MUS-008) initialized")

        # Hook generation parameters
        self.hooks_per_request = 5  # Always generates 5 hooks for comprehensive options

        # Viral hook formulas and patterns
        self.hook_patterns = [
            "question_based",
            "contrarian_statement",
            "bold_claim",
            "what_if_scenario",
            "never_knew_fact",
            "secret_reveal",
            "controversial_opinion"
        ]

    async def generate_hooks(self, request: HookRequest) -> HookReport:
        """
        Generate viral hooks for the specified topic.

        Main entry point for hook creation. Analyzes the topic and generates
        multiple viral hook variations that are optimized for scroll-stopping
        attention and engagement across social platforms.

        Args:
            request: HookRequest containing topic for hook generation

        Returns:
            HookReport with 5 viral hook variations

        Example:
            request = HookRequest(topic="AI automation in business")
            report = await agent.generate_hooks(request)
            # Returns 5 hooks like:
            # - "What if AI could 10x your business overnight?"
            # - "Stop wasting money - Here's what billionaires do instead..."
            # - etc.
        """
        correlation_id = get_correlation_id()

        logger.info(
            "Generating viral hooks",
            topic=request.topic,
            correlation_id=correlation_id
        )

        try:
            # Build generation prompt
            prompt = self._build_hook_prompt(request.topic)

            # Generate hooks with LLM
            hooks = await self._generate_with_llm(prompt, correlation_id)

            # Create report
            report = HookReport(hooks=hooks)

            logger.info(
                "Hook generation completed successfully",
                hooks_created=len(hooks),
                correlation_id=correlation_id
            )

            return report

        except Exception as e:
            logger.error(
                "Hook generation failed",
                error=str(e),
                topic=request.topic,
                correlation_id=correlation_id
            )

            # Return fallback report with generic hooks
            fallback_hooks = [
                f"What if I told you {request.topic} could change everything?",
                f"The surprising truth about {request.topic}...",
                f"You won't believe what happened when I tried {request.topic}",
                f"This {request.topic} secret changed my business forever",
                f"Why {request.topic} is about to explode in popularity"
            ]

            return HookReport(hooks=fallback_hooks)

    def _build_hook_prompt(self, topic: str) -> str:
        """
        Build the LLM prompt for viral hook generation.

        Creates a comprehensive prompt that guides the LLM to act as a viral
        content expert and generate scroll-stopping hooks using proven techniques.

        Args:
            topic: The topic for which to generate hooks

        Returns:
            Structured prompt for hook generation
        """
        prompt = f"""
You are a viral content copywriter with 8+ years of experience creating hooks that go viral on TikTok, Instagram, YouTube, and LinkedIn. Your hooks consistently stop the scroll and drive millions of views.

Your task: Generate 5 compelling, scroll-stopping hooks for content about: "{topic}"

HOOK CRITERIA:
- Each hook must be short (10-25 words maximum)
- Extremely attention-grabbing and intriguing
- Create curiosity or emotional response
- Work well as video titles, social media posts, or ad headlines
- Feel urgent or important
- Make people want to click, watch, or read immediately

HOOK FORMULAS TO USE (create one of each type):
1. QUESTION HOOK: Start with a provocative question
2. STATEMENT HOOK: Make a bold, surprising statement
3. NUMBERED HOOK: Promise a specific number of valuable insights
4. CONTRARIAN HOOK: Challenge common beliefs or popular opinions
5. STORY HOOK: Hint at a relatable story or transformation

EXAMPLES OF GREAT HOOKS:
- "What billionaires know about money that you don't"
- "This morning routine changed my life in 30 days"
- "The #1 lie preventing your success"
- "Watch what happens when I tried this viral trend"
- "Why everyone I know is suddenly doing THIS"

Return your 5 hooks as a JSON object with one key: "hooks", containing an array of exactly 5 strings.

Example format: {{"hooks": ["Hook 1 here", "Hook 2 here", "Hook 3 here", "Hook 4 here", "Hook 5 here"]}}

CRITICAL: Make each hook optimized for virality and engagement. Focus on psychological triggers like curiosity, social proof, fear of missing out, or desire for improvement.
"""
        return prompt

    async def _generate_with_llm(self, prompt: str, correlation_id: str) -> List[str]:
        """
        Execute LLM generation and parse hook results.

        Args:
            prompt: Complete hook generation prompt
            correlation_id: Request correlation ID

        Returns:
            List of generated viral hooks

        Raises:
            Exception: If LLM call fails and can't be recovered
        """
        try:
            response = await vertex_ai_client.generate_json(
                prompt=prompt,
                system_prompt=self._get_viral_copywriter_prompt(),
                model_type="creative",
                temperature=0.8,    # High creativity for attention-grabbing hooks
                max_tokens=500      # Allow room for hook variations
            )

            # Parse and validate response
            hooks = self._parse_hooks(response, correlation_id)

            return hooks

        except Exception as e:
            logger.warning(
                f"LLM hook generation failed: {e}",
                correlation_id=correlation_id
            )
            raise

    def _parse_hooks(self, response: dict, correlation_id: str) -> List[str]:
        """
        Parse and validate hook generation response.

        Args:
            response: Raw LLM response containing hooks
            correlation_id: Request correlation ID

        Returns:
            List of validated hook strings

        Raises:
            Exception: If response cannot be properly parsed
        """
        try:
            if not isinstance(response, dict) or "hooks" not in response:
                raise ValueError("Invalid response format: missing hooks key")

            hooks = response["hooks"]

            if not isinstance(hooks, list):
                raise ValueError("hooks must be a list")

            # Validate and clean hooks
            validated_hooks = []
            for i, hook in enumerate(hooks):
                if isinstance(hook, str) and hook.strip():
                    clean_hook = hook.strip()
                    if 5 <= len(clean_hook) <= 200:  # Reasonable length limits
                        validated_hooks.append(clean_hook)

            if len(validated_hooks) == 0:
                logger.warning("No valid hooks parsed", correlation_id=correlation_id)
                raise ValueError("No valid hooks found in response")

            # Ensure we have exactly 5 hooks (pad if necessary)
            while len(validated_hooks) < 5 and len(validated_hooks) > 0:
                validated_hooks.append(validated_hooks[-1])  # Duplicate last hook

            # Limit to 5 hooks maximum
            validated_hooks = validated_hooks[:5]

            logger.debug(
                f"Successfully parsed {len(validated_hooks)} hooks",
                correlation_id=correlation_id
            )

            return validated_hooks

        except Exception as e:
            logger.error(
                f"Failed to parse hooks response: {e}",
                correlation_id=correlation_id
            )
            raise

    def _get_viral_copywriter_prompt(self) -> str:
        """
        Get system prompt defining the LLM's role as a viral copywriter.

        Returns:
            System instruction for viral hook creation
        """
        return """You are a master viral copywriter specialized in creating hooks that explode across social media platforms. You have spent 8+ years studying what makes content go viral, analyzing millions of views, and perfecting the art of attention-grabbing copywriting.

Your expertise includes:
- Psychological triggers and human behavior patterns
- Platform-specific optimization (TikTok, Instagram, YouTube, LinkedIn)
- Viral content formulas and attention-grabbing techniques
- Scroll-stopping copy that converts curiosity into engagement
- Emotional hooks and desire-driven messaging

You excel at:
- Creating irresistible curiosity gaps
- Using social proof and scarcity effectively
- Writing copy that feels urgent and important
- Crafting statements that challenge listeners' beliefs
- Generating questions that demand answers

Your hooks always:
- Are short and punchy (under 25 words)
- Create immediate emotional response
- Make people stop what they're doing to watch/listen/read
- Feel authentic and not overly salesy
- Work across multiple social media platforms

You understand that viral hooks are not about information, they're about creating desire to consume the full content."""


# Global singleton instance
hook_generator_agent = HookGeneratorAgent()
