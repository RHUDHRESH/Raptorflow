"""
Instagram Agent - Posts to Instagram using Instagram Graph API.
Handles images, carousels, reels, and stories.
"""

import structlog
from typing import Dict, Any, Optional, List
from uuid import UUID
from datetime import datetime

from backend.services.social.instagram import instagram_service
from backend.models.content import ContentVariant, AssetMetadata
from backend.utils.correlation import get_correlation_id
from backend.utils.queue import redis_queue

logger = structlog.get_logger(__name__)


class InstagramAgent:
    """
    Publishes content to Instagram.
    Handles single posts, carousels, reels, and stories.
    """
    
    def __init__(self):
        self.instagram = instagram_service
        self.caption_limit = 2200
    
    async def format_caption(self, variant: ContentVariant) -> str:
        """
        Formats caption for Instagram (max 2200 chars).
        Adds hashtags and line breaks.
        """
        content = variant.content
        
        # Get hashtags
        hashtags = variant.platform_specific_attributes.get("hashtags", [])
        if not hashtags and variant.seo_keywords:
            hashtags = [f"#{kw.replace(' ', '')}" for kw in variant.seo_keywords[:30]]  # Instagram allows 30
        
        # Format with line breaks
        formatted_caption = content
        
        # Add hashtags
        if hashtags:
            # Instagram best practice: put hashtags after content or in first comment
            formatted_caption += f"\n.\n.\n.\n{' '.join(hashtags[:30])}"
        
        # Truncate if needed
        if len(formatted_caption) > self.caption_limit:
            formatted_caption = formatted_caption[:self.caption_limit-3] + "..."
            logger.warning("Instagram caption truncated")
        
        return formatted_caption
    
    async def post_to_instagram(
        self,
        variant: ContentVariant,
        workspace_id: UUID,
        account_id: Optional[str] = None,
        image_url: Optional[str] = None,
        image_urls: Optional[List[str]] = None,  # For carousel
        post_type: str = "feed",  # feed, reel, story, carousel
        schedule_time: Optional[datetime] = None,
        correlation_id: str = None
    ) -> Dict[str, Any]:
        """
        Posts content to Instagram.
        
        Args:
            variant: Content (caption)
            workspace_id: User's workspace
            account_id: Instagram account ID
            image_url: Single image URL
            image_urls: Multiple images for carousel
            post_type: feed, reel, story, carousel
            schedule_time: Optional scheduled post time
            
        Returns:
            Dict with media_id, status, url
        """
        correlation_id = correlation_id or get_correlation_id()
        logger.info("Posting to Instagram", post_type=post_type, scheduled=schedule_time is not None, correlation_id=correlation_id)
        
        # Format caption
        caption = await self.format_caption(variant)
        
        # Validate media
        if post_type in ["feed", "reel", "story"] and not image_url:
            raise ValueError(f"Instagram {post_type} requires an image/video URL")
        if post_type == "carousel" and not image_urls:
            raise ValueError("Instagram carousel requires multiple image URLs")
        
        # If scheduled, queue the task
        if schedule_time and schedule_time > datetime.utcnow():
            await redis_queue.enqueue(
                task_name="publish_instagram",
                payload={
                    "caption": caption,
                    "workspace_id": str(workspace_id),
                    "account_id": account_id,
                    "image_url": image_url,
                    "image_urls": image_urls,
                    "post_type": post_type,
                    "schedule_time": schedule_time.isoformat()
                },
                priority="medium"
            )
            logger.info("Instagram post scheduled", schedule_time=schedule_time, correlation_id=correlation_id)
            return {
                "status": "scheduled",
                "schedule_time": schedule_time.isoformat(),
                "message": "Post queued for publishing"
            }
        
        # Post immediately
        try:
            if post_type == "carousel":
                result = await self.instagram.create_carousel(
                    caption=caption,
                    image_urls=image_urls,
                    workspace_id=workspace_id,
                    account_id=account_id
                )
            else:
                result = await self.instagram.create_post(
                    caption=caption,
                    image_url=image_url,
                    post_type=post_type,
                    workspace_id=workspace_id,
                    account_id=account_id
                )
            
            logger.info("Instagram post published", media_id=result.get("id"), correlation_id=correlation_id)
            return {
                "status": "published",
                "media_id": result.get("id"),
                "permalink": result.get("permalink"),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("Failed to post to Instagram", error=str(e), correlation_id=correlation_id)
            return {
                "status": "failed",
                "error": str(e)
            }


instagram_agent = InstagramAgent()

