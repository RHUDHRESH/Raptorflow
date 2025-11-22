"""
Instagram Service - OAuth integration via Instagram Graph API.
"""

import structlog
from typing import Dict, Any, Optional, List
from uuid import UUID
import httpx

from backend.config.settings import get_settings
from backend.services.supabase_client import supabase_client

logger = structlog.get_logger(__name__)
settings = get_settings()


class InstagramService:
    """Instagram Graph API integration."""
    
    def __init__(self):
        self.base_url = "https://graph.instagram.com/v18.0"
        self.access_token = settings.INSTAGRAM_ACCESS_TOKEN
    
    async def get_access_token(self, workspace_id: UUID) -> Optional[str]:
        """Retrieves stored Instagram access token."""
        try:
            integration = await supabase_client.fetch_one(
                "integrations",
                {"workspace_id": str(workspace_id), "platform": "instagram"}
            )
            return integration.get("access_token") if integration else None
        except Exception as e:
            logger.error(f"Failed to get Instagram token: {e}")
            return None
    
    async def create_post(
        self,
        caption: str,
        image_url: str,
        post_type: str,
        workspace_id: UUID,
        account_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Creates Instagram post (feed/reel/story)."""
        access_token = await self.get_access_token(workspace_id)
        if not access_token:
            raise ValueError("Instagram not connected")
        
        # Instagram requires 2-step process: create container, then publish
        params = {
            "access_token": access_token,
            "caption": caption,
            "image_url": image_url
        }
        
        try:
            async with httpx.AsyncClient() as client:
                # Step 1: Create container
                response = await client.post(
                    f"{self.base_url}/{account_id}/media",
                    params=params,
                    timeout=30.0
                )
                container_id = response.json()["id"]
                
                # Step 2: Publish
                publish_response = await client.post(
                    f"{self.base_url}/{account_id}/media_publish",
                    params={"access_token": access_token, "creation_id": container_id},
                    timeout=30.0
                )
                
                media_id = publish_response.json()["id"]
                
                return {
                    "id": media_id,
                    "permalink": f"https://instagram.com/p/{media_id}",
                    "status": "published"
                }
        except Exception as e:
            logger.error(f"Failed to create Instagram post: {e}")
            raise
    
    async def create_carousel(
        self,
        caption: str,
        image_urls: List[str],
        workspace_id: UUID,
        account_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Creates Instagram carousel."""
        access_token = await self.get_access_token(workspace_id)
        
        # Create container for each image
        children_ids = []
        async with httpx.AsyncClient() as client:
            for image_url in image_urls:
                response = await client.post(
                    f"{self.base_url}/{account_id}/media",
                    params={
                        "access_token": access_token,
                        "image_url": image_url,
                        "is_carousel_item": True
                    }
                )
                children_ids.append(response.json()["id"])
            
            # Create carousel container
            carousel_response = await client.post(
                f"{self.base_url}/{account_id}/media",
                params={
                    "access_token": access_token,
                    "caption": caption,
                    "media_type": "CAROUSEL",
                    "children": ",".join(children_ids)
                }
            )
            
            # Publish
            publish_response = await client.post(
                f"{self.base_url}/{account_id}/media_publish",
                params={
                    "access_token": access_token,
                    "creation_id": carousel_response.json()["id"]
                }
            )
            
            return {
                "id": publish_response.json()["id"],
                "permalink": f"https://instagram.com/p/{publish_response.json()['id']}",
                "status": "published"
            }


instagram_service = InstagramService()

