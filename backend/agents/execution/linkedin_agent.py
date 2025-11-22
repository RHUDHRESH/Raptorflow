"""
LinkedIn Agent - Posts content to LinkedIn using LinkedIn API.
Handles profiles, company pages, formatting, and scheduling.
"""

import structlog
from typing import Dict, Any, Optional
from uuid import UUID
from datetime import datetime

from backend.services.social.linkedin import linkedin_service
from backend.models.content import ContentVariant
from backend.utils.correlation import get_correlation_id
from backend.utils.queue import redis_queue

logger = structlog.get_logger(__name__)


class LinkedInAgent:
    """
    Publishes content to LinkedIn (personal profiles and company pages).
    Handles rate limiting, formatting, and hashtags.
    """
    
    def __init__(self):
        self.linkedin = linkedin_service
    
    async def format_post(self, variant: ContentVariant) -> str:
        """
        Formats content for LinkedIn's requirements.
        - Max 3000 characters
        - Line breaks for readability
        - 3-5 hashtags at end
        """
        content = variant.content
        
        # Extract hashtags if present
        hashtags = variant.platform_specific_attributes.get("hashtags", [])
        
        # Ensure we have hashtags
        if not hashtags:
            # Extract from keywords or use defaults
            keywords = variant.seo_keywords[:5] if variant.seo_keywords else []
            hashtags = [f"#{kw.replace(' ', '')}" for kw in keywords]
        
        # LinkedIn best practice: add line breaks for readability
        formatted_content = content.replace("\n\n", "\n\n")  # Already formatted
        
        # Add hashtags at end
        if hashtags:
            formatted_content += f"\n\n{' '.join(hashtags[:5])}"
        
        # Truncate if too long
        if len(formatted_content) > 3000:
            formatted_content = formatted_content[:2997] + "..."
            logger.warning("LinkedIn post truncated", original_length=len(content))
        
        return formatted_content
    
    async def post_to_linkedin(
        self,
        variant: ContentVariant,
        workspace_id: UUID,
        account_type: str = "profile",  # profile or company_page
        account_id: Optional[str] = None,
        schedule_time: Optional[datetime] = None,
        correlation_id: str = None
    ) -> Dict[str, Any]:
        """
        Posts content to LinkedIn.
        
        Args:
            variant: Content to post
            workspace_id: User's workspace
            account_type: "profile" or "company_page"
            account_id: LinkedIn account/page ID
            schedule_time: Optional scheduled post time
            
        Returns:
            Dict with post_id, status, url
        """
        correlation_id = correlation_id or get_correlation_id()
        logger.info("Posting to LinkedIn", account_type=account_type, scheduled=schedule_time is not None, correlation_id=correlation_id)
        
        # Format content
        formatted_content = await self.format_post(variant)
        
        # If scheduled, queue the task
        if schedule_time and schedule_time > datetime.utcnow():
            await redis_queue.enqueue(
                task_name="publish_linkedin",
                payload={
                    "content": formatted_content,
                    "workspace_id": str(workspace_id),
                    "account_type": account_type,
                    "account_id": account_id,
                    "schedule_time": schedule_time.isoformat()
                },
                priority="medium"
            )
            logger.info("LinkedIn post scheduled", schedule_time=schedule_time, correlation_id=correlation_id)
            return {
                "status": "scheduled",
                "schedule_time": schedule_time.isoformat(),
                "message": "Post queued for publishing"
            }
        
        # Post immediately
        try:
            result = await self.linkedin.create_post(
                content=formatted_content,
                workspace_id=workspace_id,
                account_type=account_type,
                account_id=account_id
            )
            
            logger.info("LinkedIn post published", post_id=result.get("id"), correlation_id=correlation_id)
            return {
                "status": "published",
                "post_id": result.get("id"),
                "url": result.get("url"),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("Failed to post to LinkedIn", error=str(e), correlation_id=correlation_id)
            return {
                "status": "failed",
                "error": str(e)
            }


linkedin_agent = LinkedInAgent()

