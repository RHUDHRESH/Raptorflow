"""
Blog Writer Agent - Generates long-form thought-leadership articles.
Uses creative model (Claude Sonnet 4.5) for high-quality content.
"""

import json
import structlog
from typing import List, Dict, Any, Optional
from uuid import UUID

from backend.config.prompts import BLOG_WRITER_SYSTEM_PROMPT
from backend.services.vertex_ai_client import vertex_ai_client
from backend.models.content import ContentVariant
from backend.models.persona import ICPProfile
from backend.utils.correlation import get_correlation_id
from backend.utils.cache import redis_cache
from backend.agents.base_agent import BaseAgent

logger = structlog.get_logger(__name__)


class BlogWriterAgent(BaseAgent):
    """
    Generates comprehensive blog posts and long-form articles.
    Uses creative model (Claude Sonnet) for best quality.
    """
    
    def __init__(self):
        super().__init__(name="blog_writer")
        self.llm = vertex_ai_client

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the blog writing task.
        
        Args:
            payload: Dictionary containing:
                - topic: str
                - icp_profile: ICPProfile (dict or object)
                - keywords: List[str]
                - word_count_target: int
                - tone: str
                - include_sections: List[str]
                - brand_voice: str
        """
        try:
            # Extract parameters
            topic = payload.get("topic")
            icp_data = payload.get("icp_profile")
            
            # Handle ICP profile being passed as dict or object
            if isinstance(icp_data, dict):
                icp_profile = ICPProfile(**icp_data)
            else:
                icp_profile = icp_data

            keywords = payload.get("keywords", [])
            word_count_target = payload.get("word_count_target", 1200)
            tone = payload.get("tone", "professional")
            include_sections = payload.get("include_sections")
            brand_voice = payload.get("brand_voice")
            correlation_id = payload.get("correlation_id")

            self.log(f"Executing blog writer task: {topic}", level="info")

            # Generate content
            variant = await self.write_blog_post(
                topic=topic,
                icp_profile=icp_profile,
                keywords=keywords,
                word_count_target=word_count_target,
                tone=tone,
                include_sections=include_sections,
                brand_voice=brand_voice,
                correlation_id=correlation_id
            )

            # Publish completion event
            await self.publish_event(
                "agent.content.blog_generated",
                {
                    "topic": topic,
                    "word_count": variant.word_count,
                    "variant_id": str(variant.id) if hasattr(variant, "id") else None
                }
            )

            return {
                "status": "success",
                "result": variant,
                "metadata": {
                    "word_count": variant.word_count,
                    "model": "claude-3-5-sonnet"
                }
            }

        except Exception as e:
            self.log(f"Blog generation failed: {str(e)}", level="error")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def write_blog_post(
        self,
        topic: str,
        icp_profile: ICPProfile,
        keywords: List[str] = None,
        word_count_target: int = 1200,
        tone: str = "professional",
        include_sections: List[str] = None,
        brand_voice: Optional[str] = None,
        correlation_id: str = None
    ) -> ContentVariant:
        """
        Generates a complete blog post with SEO optimization.
        
        Args:
            topic: Blog post topic/title
            icp_profile: Target audience
            keywords: SEO keywords to include
            word_count_target: Approximate word count
            tone: professional, casual, thought-leadership, educational
            include_sections: Specific sections to include (e.g., ["intro", "case_study", "conclusion"])
            brand_voice: Optional brand voice guidelines
            
        Returns:
            ContentVariant with markdown blog post
        """
        correlation_id = correlation_id or get_correlation_id()
        logger.info("Writing blog post", topic=topic, word_count=word_count_target, correlation_id=correlation_id)
        
        cache_key = f"blog:{icp_profile.id}:{topic}:{word_count_target}:{tone}"
        cached_post = await redis_cache.get(cache_key)
        if cached_post:
            logger.info("Returning cached blog post", correlation_id=correlation_id)
            return ContentVariant(**cached_post)
        
        # Build context
        keywords_str = ", ".join(keywords) if keywords else "N/A"
        pain_points_str = ", ".join(icp_profile.pain_points[:3]) if icp_profile.pain_points else "N/A"
        goals_str = ", ".join(icp_profile.goals[:2]) if icp_profile.goals else "N/A"
        sections_str = ", ".join(include_sections) if include_sections else "Standard blog structure"
        
        prompt = f"""Write a comprehensive, high-quality blog post for:

**Topic**: {topic}
**Target Word Count**: {word_count_target} words
**Target Audience**: {icp_profile.name}
- Role: {icp_profile.demographics.buyer_role or 'Professional'}
- Pain Points: {pain_points_str}
- Goals: {goals_str}
- Industry: {icp_profile.demographics.industry or 'General'}

**SEO Keywords**: {keywords_str}
**Tone**: {tone}
**Structure**: {sections_str}

{f"**Brand Voice Guidelines**: {brand_voice}" if brand_voice else ""}

**Requirements**:
1. Hook the reader in the intro with a compelling question or stat
2. Use subheadings (H2, H3) for readability
3. Naturally incorporate SEO keywords (don't keyword stuff)
4. Include actionable insights and examples
5. Address the audience's pain points and offer solutions
6. End with a strong conclusion and subtle CTA
7. Write in markdown format
8. Use storytelling and data where appropriate

Generate the blog post now. Output as markdown.
"""
        
        messages = [
            {"role": "system", "content": BLOG_WRITER_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
        
        try:
            # Use creative model (Claude Sonnet) for best quality
            blog_content = await self.llm.chat_completion(
                messages,
                model_type="creative",
                temperature=0.7,
                max_tokens=4096
            )
            
            # Count words (rough estimate)
            word_count = len(blog_content.split())
            
            variant = ContentVariant(
                format="long_form_blog",
                content=blog_content,
                word_count=word_count,
                readability_score=0.8,  # Placeholder - could integrate actual readability check
                seo_keywords=keywords or [],
                platform_specific_attributes={"format": "markdown"}
            )
            
            # Cache for 7 days
            await redis_cache.set(cache_key, variant.model_dump(), ttl=604800)
            
            logger.info("Blog post generated", word_count=word_count, correlation_id=correlation_id)
            return variant
            
        except Exception as e:
            logger.error("Error writing blog post", error=str(e), correlation_id=correlation_id)
            raise


blog_writer_agent = BlogWriterAgent()
