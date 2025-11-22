"""
Social Copy Agent - Generates platform-specific social media posts.
Adapts content for LinkedIn, Twitter, Instagram with proper formatting.
"""

import json
import structlog
from typing import List, Dict, Any, Literal, Optional
from uuid import UUID

from backend.config.prompts import SOCIAL_COPY_SYSTEM_PROMPT
from backend.services.vertex_ai_client import vertex_ai_client
from backend.models.content import ContentVariant, Hook
from backend.models.persona import ICPProfile
from backend.utils.correlation import get_correlation_id
from backend.utils.cache import redis_cache

logger = structlog.get_logger(__name__)


class SocialCopyAgent:
    """
    Generates platform-optimized social media content.
    Uses creative_fast model for rapid social post generation.
    """
    
    def __init__(self):
        self.llm = vertex_ai_client
        self.platform_specs = {
            "linkedin": {
                "max_length": 3000,
                "optimal_length": "150-300 words",
                "tone": "Professional, thought-leadership",
                "features": "Hashtags (3-5), @mentions, line breaks for readability",
                "best_formats": "Career insights, industry trends, case studies"
            },
            "twitter": {
                "max_length": 280,
                "optimal_length": "100-240 characters",
                "tone": "Concise, punchy, conversational",
                "features": "Hashtags (1-2), @mentions, threads for longer content",
                "best_formats": "Hot takes, quick tips, questions, threads"
            },
            "instagram": {
                "max_length": 2200,
                "optimal_length": "138-150 characters for feed, longer for carousels",
                "tone": "Visual-first, storytelling, authentic",
                "features": "Hashtags (20-30), emoji usage, line breaks",
                "best_formats": "Behind-the-scenes, user stories, visual quotes"
            },
            "facebook": {
                "max_length": 63206,
                "optimal_length": "40-80 characters for high engagement",
                "tone": "Friendly, community-focused",
                "features": "Hashtags (optional), @mentions, questions",
                "best_formats": "Questions, polls, community stories"
            },
            "tiktok": {
                "max_length": 2200,
                "optimal_length": "300 characters",
                "tone": "Fun, authentic, trend-driven",
                "features": "Hashtags (3-5), trending sounds, challenges",
                "best_formats": "Short videos, tutorials, trends"
            }
        }
    
    async def generate_social_post(
        self,
        topic: str,
        icp_profile: ICPProfile,
        platform: Literal["linkedin", "twitter", "instagram", "facebook", "tiktok"],
        hook: Optional[Hook] = None,
        cta: Optional[str] = None,
        hashtags: Optional[List[str]] = None,
        brand_voice: Optional[str] = None,
        include_emoji: bool = True,
        correlation_id: str = None
    ) -> ContentVariant:
        """
        Generates a platform-optimized social media post.
        
        Args:
            topic: What the post is about
            icp_profile: Target audience
            platform: Social platform to optimize for
            hook: Optional pre-generated hook to include
            cta: Call-to-action
            hashtags: Specific hashtags to include
            brand_voice: Brand voice guidelines
            include_emoji: Whether to use emojis
            
        Returns:
            ContentVariant with platform-optimized content
        """
        correlation_id = correlation_id or get_correlation_id()
        logger.info("Generating social post", platform=platform, topic=topic, correlation_id=correlation_id)
        
        cache_key = f"social:{platform}:{icp_profile.id}:{topic}:{include_emoji}"
        cached_post = await redis_cache.get(cache_key)
        if cached_post:
            logger.info("Returning cached social post", correlation_id=correlation_id)
            return ContentVariant(**cached_post)
        
        # Get platform specs
        specs = self.platform_specs[platform]
        pain_points_str = ", ".join(icp_profile.pain_points[:2]) if icp_profile.pain_points else "N/A"
        
        prompt = f"""Create a {platform} post for:

**Topic**: {topic}
**Target Audience**: {icp_profile.name}
- Pain Points: {pain_points_str}
- Motivation: {icp_profile.psychographics.motivation or 'N/A'}

**Platform Specs**:
- Optimal Length: {specs['optimal_length']}
- Tone: {specs['tone']}
- Features: {specs['features']}
- Best Formats: {specs['best_formats']}

{f"**Hook to Include**: {hook.text}" if hook else ""}
{f"**CTA**: {cta}" if cta else ""}
{f"**Required Hashtags**: {', '.join(hashtags)}" if hashtags else ""}
{f"**Brand Voice**: {brand_voice}" if brand_voice else ""}
**Emoji Usage**: {"Yes, use relevant emojis" if include_emoji else "No emojis"}

**Requirements**:
1. Follow {platform} best practices and character limits
2. Hook attention in first line
3. Format for easy scanning (line breaks, bullets if applicable)
4. Use conversational, authentic language
5. Include relevant hashtags (platform-appropriate count)
6. Clear CTA or engagement prompt
7. Optimize for {platform}'s algorithm

Generate the post now. Output plain text format.
"""
        
        messages = [
            {"role": "system", "content": SOCIAL_COPY_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
        
        try:
            # Use creative_fast for rapid social post generation
            post_content = await self.llm.chat_completion(
                messages,
                model_type="creative_fast",
                temperature=0.85  # Higher creativity for social
            )
            
            # Extract hashtags from content
            import re
            found_hashtags = re.findall(r'#\w+', post_content)
            
            variant = ContentVariant(
                format="short_social_post",
                content=post_content,
                word_count=len(post_content.split()),
                readability_score=0.9,  # Social content is highly readable
                seo_keywords=[],
                platform_specific_attributes={
                    "platform": platform,
                    "hashtags": found_hashtags,
                    "character_count": len(post_content),
                    "includes_emoji": include_emoji
                }
            )
            
            # Cache for 7 days
            await redis_cache.set(cache_key, variant.model_dump(), ttl=604800)
            
            logger.info("Social post generated", platform=platform, char_count=len(post_content), correlation_id=correlation_id)
            return variant
            
        except Exception as e:
            logger.error("Error generating social post", error=str(e), correlation_id=correlation_id)
            raise
    
    async def generate_twitter_thread(
        self,
        topic: str,
        icp_profile: ICPProfile,
        thread_length: int = 5,
        brand_voice: Optional[str] = None,
        correlation_id: str = None
    ) -> List[ContentVariant]:
        """
        Generates a Twitter/X thread with connected tweets.
        
        Args:
            topic: Thread topic
            icp_profile: Target audience
            thread_length: Number of tweets (3-10 recommended)
            brand_voice: Brand voice guidelines
            
        Returns:
            List of ContentVariant tweets
        """
        correlation_id = correlation_id or get_correlation_id()
        logger.info("Generating Twitter thread", length=thread_length, correlation_id=correlation_id)
        
        prompt = f"""Create a {thread_length}-tweet Twitter thread on: {topic}

**Target Audience**: {icp_profile.name}
**Tone**: Engaging, insightful, conversational

**Thread Structure**:
- Tweet 1: Hook tweet (grab attention, create curiosity)
- Tweets 2-{thread_length-1}: Educational/value tweets (one idea per tweet)
- Tweet {thread_length}: Conclusion + CTA

**Requirements**:
1. Each tweet max 280 characters
2. Number tweets (1/thread_length, 2/thread_length, etc.)
3. Use line breaks for readability
4. Include 1-2 hashtags in first tweet only
5. Each tweet should stand alone but connect to next
6. No emojis in first tweet, occasional in others

Output as JSON array of tweets:
[{{"tweet_number": 1, "content": "Tweet text...", "character_count": 150}}]
"""
        
        messages = [
            {"role": "system", "content": SOCIAL_COPY_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
        
        try:
            llm_response = await self.llm.chat_completion(
                messages,
                model_type="creative_fast",
                temperature=0.8,
                response_format={"type": "json_object"}
            )
            
            tweets_data = json.loads(llm_response)
            if not isinstance(tweets_data, list):
                raise ValueError("LLM did not return JSON array of tweets")
            
            thread = []
            for tweet_data in tweets_data[:thread_length]:
                variant = ContentVariant(
                    format="short_social_post",
                    content=tweet_data["content"],
                    word_count=len(tweet_data["content"].split()),
                    platform_specific_attributes={
                        "platform": "twitter",
                        "tweet_number": tweet_data["tweet_number"],
                        "character_count": tweet_data.get("character_count", len(tweet_data["content"]))
                    }
                )
                thread.append(variant)
            
            logger.info("Twitter thread generated", length=len(thread), correlation_id=correlation_id)
            return thread
            
        except Exception as e:
            logger.error("Error generating Twitter thread", error=str(e), correlation_id=correlation_id)
            raise


social_copy_agent = SocialCopyAgent()

