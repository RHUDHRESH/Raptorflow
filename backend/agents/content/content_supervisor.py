"""
Content Supervisor Agent - Orchestrates all content generation workflows.
Coordinates hook generation, content writing, brand voice application, and quality review.
"""

import asyncio
import structlog
from typing import Dict, Any, List, Optional
from uuid import UUID, uuid4
from datetime import datetime

from backend.agents.base_agent import BaseSupervisor
from backend.agents.content.hook_generator import hook_generator_agent
from backend.agents.content.blog_writer import blog_writer_agent
from backend.agents.content.email_writer import email_writer_agent
from backend.agents.content.social_copy import social_copy_agent
from backend.agents.content.brand_voice import brand_voice_agent
from backend.agents.content.carousel_agent import carousel_agent
from backend.agents.safety.critic_agent import critic_agent
from backend.models.content import (
    ContentRequest, ContentResponse, ContentVariant, Hook, BrandVoiceProfile
)
from backend.models.persona import ICPProfile
from backend.services.supabase_client import supabase_client
from backend.utils.correlation import get_correlation_id, set_correlation_id
from backend.utils.cache import redis_cache

logger = structlog.get_logger(__name__)


class ContentSupervisor(BaseSupervisor):
    """
    Tier 1 Supervisor: Content Generation

    Coordinates all content generation sub-agents:
    1. Hook Generator → generates compelling hooks
    2. Content Writer → creates the main content (blog/email/social/carousel)
    3. Brand Voice → applies brand voice consistency
    4. Critic → reviews quality and provides feedback

    Implements caching, validation, error handling, and retry logic.
    """

    def __init__(self):
        super().__init__(name="ContentSupervisor")
        self.max_retries = 3
        self.retry_delay = 2  # seconds
        self.hook_cache_ttl = 86400  # 24 hours
        self.content_cache_ttl = 3600  # 1 hour

        # Register sub-agents
        self.sub_agents = {
            "hook_generator": hook_generator_agent,
            "blog_writer": blog_writer_agent,
            "email_writer": email_writer_agent,
            "social_copy": social_copy_agent,
            "brand_voice": brand_voice_agent,
            "carousel": carousel_agent,
            "critic": critic_agent,
        }

    async def execute(self, goal: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute content generation workflow.

        Args:
            goal: High-level content goal (e.g., "Generate blog post about AI")
            context: Contains content_request, icp_profile, brand_voice, etc.

        Returns:
            ContentResponse with generated variants and metadata
        """
        correlation_id = context.get("correlation_id") or get_correlation_id()
        set_correlation_id(correlation_id)

        self.log(f"Starting content generation: {goal}", correlation_id=correlation_id)

        try:
            # Extract and validate inputs
            content_request = self._validate_input(context)
            icp_profile = context.get("icp_profile")
            brand_voice_profile = context.get("brand_voice_profile")
            strategy_id = context.get("strategy_id")

            # Check cache first
            cache_key = self._generate_cache_key(content_request)
            cached_response = await redis_cache.get(cache_key)
            if cached_response:
                self.log("Returning cached content", correlation_id=correlation_id)
                return cached_response

            # Step 1: Generate hooks (if needed for this content type)
            hooks = await self._generate_hooks_with_retry(
                content_request, icp_profile, correlation_id
            )

            # Step 2: Generate main content
            content_variants = await self._generate_content_with_retry(
                content_request, icp_profile, hooks, correlation_id
            )

            # Step 3: Apply brand voice (if profile provided)
            if brand_voice_profile:
                content_variants = await self._apply_brand_voice(
                    content_variants, brand_voice_profile, correlation_id
                )

            # Step 4: Run critic review (if quality threshold required)
            if context.get("require_critic_review", False):
                content_variants = await self._run_critic_loop(
                    content_variants,
                    content_request.content_type,
                    icp_profile,
                    brand_voice_profile,
                    correlation_id
                )

            # Build final response
            response = await self._build_response(
                content_request,
                content_variants,
                hooks,
                correlation_id
            )

            # Cache the result
            await redis_cache.set(cache_key, response, ttl=self.content_cache_ttl)

            self.log("Content generation completed",
                    variants=len(content_variants),
                    correlation_id=correlation_id)

            return response

        except Exception as e:
            self.log(f"Content generation failed: {e}",
                    level="error",
                    correlation_id=correlation_id)
            raise

    def _validate_input(self, context: Dict[str, Any]) -> ContentRequest:
        """
        Validates input payload and content request.

        Raises:
            ValueError: If validation fails
        """
        if "content_request" not in context:
            raise ValueError("Missing required field: content_request")

        content_request = context["content_request"]

        # Validate topic length
        if not content_request.topic or len(content_request.topic.strip()) < 5:
            raise ValueError("Topic must be at least 5 characters long")

        if len(content_request.topic) > 200:
            raise ValueError("Topic exceeds maximum length of 200 characters")

        # Validate content type specific requirements
        content_type = content_request.content_type

        if content_type == "blog_post":
            # Blog should have reasonable length
            length = content_request.length or "medium"
            if length not in ["short", "medium", "long"]:
                raise ValueError("Invalid blog length. Must be: short, medium, or long")

        elif content_type == "email":
            # Email sequences should be reasonable length
            num_emails = context.get("sequence_length", 1)
            if num_emails < 1 or num_emails > 10:
                raise ValueError("Email sequence length must be between 1 and 10")

        elif content_type == "social_post":
            # Social posts need a platform
            if not content_request.platform:
                raise ValueError("Platform required for social posts")

            valid_platforms = ["linkedin", "twitter", "instagram", "facebook", "tiktok"]
            if content_request.platform not in valid_platforms:
                raise ValueError(f"Platform must be one of: {', '.join(valid_platforms)}")

        elif content_type == "carousel":
            # Validate carousel slide count
            slide_count = context.get("slide_count", 10)
            if slide_count < 5 or slide_count > 15:
                raise ValueError("Carousel must have between 5 and 15 slides")

        return content_request

    async def _generate_hooks_with_retry(
        self,
        content_request: ContentRequest,
        icp_profile: Optional[ICPProfile],
        correlation_id: str
    ) -> List[Hook]:
        """
        Generate hooks with caching and retry logic.

        Hooks are generated for blog posts and emails.
        Cached for 24 hours for identical topics.
        """
        content_type = content_request.content_type

        # Only generate hooks for certain content types
        if content_type not in ["blog_post", "email", "social_post"]:
            return []

        if not icp_profile:
            self.log("No ICP profile provided, skipping hooks", correlation_id=correlation_id)
            return []

        # Check hook cache
        hook_cache_key = f"hooks:{icp_profile.id}:{content_request.topic}:{content_type}"
        cached_hooks = await redis_cache.get(hook_cache_key)
        if cached_hooks:
            self.log("Returning cached hooks", correlation_id=correlation_id)
            return [Hook(**h) for h in cached_hooks]

        # Generate with retry
        hook_type = "subject_line" if content_type == "email" else "tagline"

        for attempt in range(self.max_retries):
            try:
                hooks = await hook_generator_agent.generate_hooks(
                    topic=content_request.topic,
                    icp_profile=icp_profile,
                    hook_type=hook_type,
                    count=10,  # Generate 10 distinct hooks as per requirements
                    tone=content_request.tone or "engaging",
                    correlation_id=correlation_id
                )

                # Cache for 24 hours
                await redis_cache.set(
                    hook_cache_key,
                    [h.model_dump() for h in hooks],
                    ttl=self.hook_cache_ttl
                )

                return hooks

            except Exception as e:
                if attempt < self.max_retries - 1:
                    self.log(f"Hook generation failed (attempt {attempt + 1}), retrying...",
                            error=str(e), correlation_id=correlation_id)
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                else:
                    self.log("Hook generation failed after retries",
                            level="error", error=str(e), correlation_id=correlation_id)
                    return []  # Return empty list rather than failing entire workflow

    async def _generate_content_with_retry(
        self,
        content_request: ContentRequest,
        icp_profile: Optional[ICPProfile],
        hooks: List[Hook],
        correlation_id: str
    ) -> List[ContentVariant]:
        """
        Generate main content with retry logic.
        Routes to appropriate content agent based on content_type.
        """
        if not icp_profile:
            raise ValueError("ICP profile required for content generation")

        content_type = content_request.content_type

        for attempt in range(self.max_retries):
            try:
                # Route to appropriate agent
                if content_type == "blog_post":
                    variant = await self._generate_blog(
                        content_request, icp_profile, hooks, correlation_id
                    )

                elif content_type == "email":
                    variant = await self._generate_email(
                        content_request, icp_profile, hooks, correlation_id
                    )

                elif content_type == "social_post":
                    variant = await self._generate_social_post(
                        content_request, icp_profile, hooks, correlation_id
                    )

                elif content_type == "carousel":
                    variant = await self._generate_carousel(
                        content_request, icp_profile, correlation_id
                    )

                else:
                    raise ValueError(f"Unsupported content type: {content_type}")

                return [variant]  # Return as list for consistency

            except Exception as e:
                if attempt < self.max_retries - 1:
                    self.log(f"Content generation failed (attempt {attempt + 1}), retrying...",
                            error=str(e), correlation_id=correlation_id)
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                else:
                    raise

    async def _generate_blog(
        self,
        content_request: ContentRequest,
        icp_profile: ICPProfile,
        hooks: List[Hook],
        correlation_id: str
    ) -> ContentVariant:
        """Generate blog post content."""
        word_count_map = {"short": 800, "medium": 1200, "long": 2000}
        word_count = word_count_map.get(content_request.length or "medium", 1200)

        return await blog_writer_agent.write_blog_post(
            topic=content_request.topic,
            icp_profile=icp_profile,
            keywords=content_request.keywords,
            word_count_target=word_count,
            tone=content_request.tone or "professional",
            correlation_id=correlation_id
        )

    async def _generate_email(
        self,
        content_request: ContentRequest,
        icp_profile: ICPProfile,
        hooks: List[Hook],
        correlation_id: str
    ) -> ContentVariant:
        """Generate email content."""
        return await email_writer_agent.write_email(
            purpose=content_request.topic,
            icp_profile=icp_profile,
            email_type="nurture",
            formula="PAS",
            subject_line=hooks[0].text if hooks else None,
            cta=content_request.cta_text,
            correlation_id=correlation_id
        )

    async def _generate_social_post(
        self,
        content_request: ContentRequest,
        icp_profile: ICPProfile,
        hooks: List[Hook],
        correlation_id: str
    ) -> ContentVariant:
        """Generate social media post."""
        platform = content_request.platform or "linkedin"

        return await social_copy_agent.generate_social_post(
            topic=content_request.topic,
            icp_profile=icp_profile,
            platform=platform,
            hook=hooks[0] if hooks else None,
            cta=content_request.cta_text,
            hashtags=content_request.keywords,
            correlation_id=correlation_id
        )

    async def _generate_carousel(
        self,
        content_request: ContentRequest,
        icp_profile: ICPProfile,
        correlation_id: str
    ) -> ContentVariant:
        """Generate carousel content."""
        return await carousel_agent.generate_carousel(
            topic=content_request.topic,
            icp_profile=icp_profile,
            slide_count=10,
            carousel_type="educational",
            platform=content_request.platform or "linkedin",
            correlation_id=correlation_id
        )

    async def _apply_brand_voice(
        self,
        variants: List[ContentVariant],
        brand_voice_profile: BrandVoiceProfile,
        correlation_id: str
    ) -> List[ContentVariant]:
        """
        Apply brand voice to all content variants.
        """
        self.log("Applying brand voice to variants",
                variants=len(variants), correlation_id=correlation_id)

        branded_variants = []

        for variant in variants:
            try:
                branded_content = await brand_voice_agent.apply_brand_voice(
                    content=variant.content,
                    brand_voice_profile=brand_voice_profile,
                    correlation_id=correlation_id
                )

                # Create new variant with branded content
                branded_variant = ContentVariant(
                    variant_id=variant.variant_id,
                    format=variant.format,
                    content=branded_content,
                    headline=variant.headline,
                    summary=variant.summary,
                    word_count=len(branded_content.split()),
                    readability_score=variant.readability_score,
                    quality_score=variant.quality_score,
                    seo_keywords=variant.seo_keywords,
                    hashtags=variant.hashtags,
                    platform_specific_attributes={
                        **variant.platform_specific_attributes,
                        "brand_voice_applied": True
                    }
                )
                branded_variants.append(branded_variant)

            except Exception as e:
                self.log(f"Brand voice application failed for variant {variant.variant_id}",
                        level="warning", error=str(e), correlation_id=correlation_id)
                # Keep original variant if branding fails
                branded_variants.append(variant)

        return branded_variants

    async def _run_critic_loop(
        self,
        variants: List[ContentVariant],
        content_type: str,
        icp_profile: Optional[ICPProfile],
        brand_voice_profile: Optional[BrandVoiceProfile],
        correlation_id: str,
        max_iterations: int = 2,
        target_score: float = 85.0
    ) -> List[ContentVariant]:
        """
        Run critic review loop to iteratively improve content quality.
        """
        self.log("Running critic review loop",
                variants=len(variants),
                max_iterations=max_iterations,
                correlation_id=correlation_id)

        improved_variants = []

        for variant in variants:
            try:
                # Run iterative improvement
                result = await critic_agent.iterative_improve(
                    initial_content=variant.content,
                    content_type=content_type,
                    max_iterations=max_iterations,
                    target_score=int(target_score),
                    target_icp=icp_profile.model_dump() if icp_profile else None,
                    brand_voice=brand_voice_profile.model_dump() if brand_voice_profile else None,
                    correlation_id=correlation_id
                )

                # Create improved variant
                improved_variant = ContentVariant(
                    variant_id=variant.variant_id,
                    format=variant.format,
                    content=result["final_content"],
                    headline=variant.headline,
                    summary=variant.summary,
                    word_count=len(result["final_content"].split()),
                    readability_score=variant.readability_score,
                    quality_score=result["final_score"] / 100.0,  # Convert to 0-1 scale
                    seo_keywords=variant.seo_keywords,
                    hashtags=variant.hashtags,
                    platform_specific_attributes={
                        **variant.platform_specific_attributes,
                        "critic_iterations": result["iterations"],
                        "critic_review_history": result["history"]
                    }
                )
                improved_variants.append(improved_variant)

            except Exception as e:
                self.log(f"Critic review failed for variant {variant.variant_id}",
                        level="warning", error=str(e), correlation_id=correlation_id)
                # Keep original variant if critic fails
                improved_variants.append(variant)

        return improved_variants

    async def _build_response(
        self,
        content_request: ContentRequest,
        variants: List[ContentVariant],
        hooks: List[Hook],
        correlation_id: str
    ) -> Dict[str, Any]:
        """
        Build final ContentResponse with all generated content.
        """
        # Find best variant (highest quality score)
        best_variant = max(variants, key=lambda v: v.quality_score or 0.0)

        # Build response
        response = {
            "content_id": str(uuid4()),
            "request": content_request.model_dump(),
            "variants": [v.model_dump() for v in variants],
            "recommended_variant_id": best_variant.variant_id,
            "hooks": [h.model_dump() for h in hooks],
            "seo_metadata": {
                "keywords": content_request.keywords,
                "topic": content_request.topic
            },
            "hashtags": content_request.keywords,
            "suggested_visuals": [],
            "overall_quality_score": best_variant.quality_score or 0.85,
            "critique": None,
            "suggestions_for_improvement": [],
            "status": "draft",
            "reviewed_by": None,
            "reviewed_at": None,
            "generated_at": datetime.utcnow().isoformat(),
            "published_at": None,
            "correlation_id": correlation_id
        }

        return response

    def _generate_cache_key(self, content_request: ContentRequest) -> str:
        """
        Generate cache key for content request.
        """
        key_parts = [
            content_request.content_type,
            content_request.topic,
            str(content_request.persona_id or "no_persona"),
            content_request.tone or "default",
            content_request.length or "medium"
        ]
        return "content:" + ":".join(key_parts)


# Global instance
content_supervisor = ContentSupervisor()
