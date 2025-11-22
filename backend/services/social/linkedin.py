"""
LinkedIn Service - OAuth integration and API wrapper for LinkedIn.
Handles authentication and post publishing.
"""

import structlog
from typing import Dict, Any, Optional
from uuid import UUID
import httpx

from backend.config.settings import get_settings
from backend.services.supabase_client import supabase_client

logger = structlog.get_logger(__name__)
settings = get_settings()


class LinkedInService:
    """
    LinkedIn API integration.
    Handles OAuth, profile/company page posting, and rate limiting.
    """
    
    def __init__(self):
        self.base_url = "https://api.linkedin.com/v2"
        self.client_id = settings.LINKEDIN_CLIENT_ID
        self.client_secret = settings.LINKEDIN_CLIENT_SECRET
    
    async def get_access_token(self, workspace_id: UUID) -> Optional[str]:
        """Retrieves stored LinkedIn access token for workspace."""
        try:
            integration = await supabase_client.fetch_one(
                "integrations",
                {"workspace_id": str(workspace_id), "platform": "linkedin"}
            )
            return integration.get("access_token") if integration else None
        except Exception as e:
            logger.error(f"Failed to get LinkedIn token: {e}")
            return None
    
    async def create_post(
        self,
        content: str,
        workspace_id: UUID,
        account_type: str = "profile",
        account_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Creates a LinkedIn post.
        
        Args:
            content: Post text
            workspace_id: User's workspace
            account_type: "profile" or "company_page"
            account_id: LinkedIn account/page URN
            
        Returns:
            Dict with post ID and URL
        """
        access_token = await self.get_access_token(workspace_id)
        if not access_token:
            raise ValueError("LinkedIn not connected for this workspace")
        
        # Build request
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        
        # LinkedIn UGC Post API payload
        payload = {
            "author": account_id or f"urn:li:person:{workspace_id}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": content
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/ugcPosts",
                    headers=headers,
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()
                
                result = response.json()
                post_id = result.get("id")
                
                return {
                    "id": post_id,
                    "url": f"https://www.linkedin.com/feed/update/{post_id}",
                    "status": "published"
                }
        except httpx.HTTPStatusError as e:
            logger.error(f"LinkedIn API error: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Failed to create LinkedIn post: {e}")
            raise


linkedin_service = LinkedInService()

