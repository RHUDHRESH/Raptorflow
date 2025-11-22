"""
YouTube Agent - Uploads videos and manages YouTube content.
Handles video uploads, descriptions, thumbnails, and playlists.
"""

import structlog
from typing import Dict, Any, Optional, List
from uuid import UUID
from datetime import datetime

from backend.services.social.youtube import youtube_service
from backend.models.content import ContentVariant
from backend.utils.correlation import get_correlation_id
from backend.utils.queue import redis_queue

logger = structlog.get_logger(__name__)


class YouTubeAgent:
    """
    Publishes videos to YouTube.
    Handles uploads, SEO optimization, and scheduling.
    """
    
    def __init__(self):
        self.youtube = youtube_service
        self.title_limit = 100
        self.description_limit = 5000
    
    async def format_description(self, variant: ContentVariant) -> str:
        """
        Formats video description for YouTube.
        Includes SEO keywords, timestamps, links.
        """
        content = variant.content
        
        # Add keywords for SEO
        keywords = variant.seo_keywords
        if keywords:
            content += f"\n\n🔑 Keywords: {', '.join(keywords)}"
        
        # Truncate if needed
        if len(content) > self.description_limit:
            content = content[:self.description_limit-3] + "..."
        
        return content
    
    async def upload_to_youtube(
        self,
        variant: ContentVariant,
        workspace_id: UUID,
        channel_id: Optional[str] = None,
        video_file_path: str = None,
        video_url: str = None,
        title: str = None,
        thumbnail_url: Optional[str] = None,
        tags: Optional[List[str]] = None,
        category: str = "22",  # People & Blogs
        privacy: str = "public",  # public, unlisted, private
        schedule_time: Optional[datetime] = None,
        correlation_id: str = None
    ) -> Dict[str, Any]:
        """
        Uploads video to YouTube.
        
        Args:
            variant: Content (description)
            workspace_id: User's workspace
            channel_id: YouTube channel ID
            video_file_path: Local video file path
            video_url: Or video URL to download
            title: Video title
            thumbnail_url: Custom thumbnail URL
            tags: Video tags
            category: YouTube category ID
            privacy: public, unlisted, or private
            schedule_time: Optional scheduled publish time
            
        Returns:
            Dict with video_id, status, url
        """
        correlation_id = correlation_id or get_correlation_id()
        logger.info("Uploading to YouTube", privacy=privacy, scheduled=schedule_time is not None, correlation_id=correlation_id)
        
        # Validate
        if not video_file_path and not video_url:
            raise ValueError("Either video_file_path or video_url must be provided")
        if not title:
            raise ValueError("Video title is required")
        
        # Format description
        description = await self.format_description(variant)
        
        # Format title
        if len(title) > self.title_limit:
            title = title[:self.title_limit-3] + "..."
        
        # Use SEO keywords as tags
        if not tags:
            tags = variant.seo_keywords[:15] if variant.seo_keywords else []  # YouTube allows 500 chars of tags
        
        # If scheduled, queue the task
        if schedule_time and schedule_time > datetime.utcnow():
            await redis_queue.enqueue(
                task_name="publish_youtube",
                payload={
                    "title": title,
                    "description": description,
                    "workspace_id": str(workspace_id),
                    "channel_id": channel_id,
                    "video_file_path": video_file_path,
                    "video_url": video_url,
                    "thumbnail_url": thumbnail_url,
                    "tags": tags,
                    "category": category,
                    "privacy": "private",  # Upload as private initially, publish at schedule_time
                    "publish_at": schedule_time.isoformat()
                },
                priority="low"  # Video uploads are lower priority
            )
            logger.info("YouTube upload scheduled", schedule_time=schedule_time, correlation_id=correlation_id)
            return {
                "status": "scheduled",
                "schedule_time": schedule_time.isoformat(),
                "message": "Video upload queued"
            }
        
        # Upload immediately
        try:
            result = await self.youtube.upload_video(
                title=title,
                description=description,
                video_file_path=video_file_path,
                video_url=video_url,
                workspace_id=workspace_id,
                channel_id=channel_id,
                thumbnail_url=thumbnail_url,
                tags=tags,
                category=category,
                privacy=privacy
            )
            
            logger.info("Video uploaded to YouTube", video_id=result.get("id"), correlation_id=correlation_id)
            return {
                "status": "published",
                "video_id": result.get("id"),
                "url": f"https://youtube.com/watch?v={result.get('id')}",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("Failed to upload to YouTube", error=str(e), correlation_id=correlation_id)
            return {
                "status": "failed",
                "error": str(e)
            }


youtube_agent = YouTubeAgent()

