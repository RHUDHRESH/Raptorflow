"""
Twitter/X Service - OAuth integration and API wrapper for Twitter.
"""

import structlog
from typing import Dict, Any, Optional, List
from uuid import UUID
import httpx

from backend.config.settings import get_settings
from backend.services.supabase_client import supabase_client

logger = structlog.get_logger(__name__)
settings = get_settings()


class TwitterService:
    """Twitter API v2 integration."""
    
    def __init__(self):
        self.base_url = "https://api.twitter.com/2"
        self.api_key = settings.TWITTER_API_KEY
        self.api_secret = settings.TWITTER_API_SECRET
    
    async def get_access_token(self, workspace_id: UUID) -> Optional[str]:
        """Retrieves stored Twitter access token."""
        try:
            integration = await supabase_client.fetch_one(
                "integrations",
                {"workspace_id": str(workspace_id), "platform": "twitter"}
            )
            return integration.get("access_token") if integration else None
        except Exception as e:
            logger.error(f"Failed to get Twitter token: {e}")
            return None
    
    async def create_tweet(
        self,
        text: str,
        workspace_id: UUID,
        account_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Creates a single tweet."""
        access_token = await self.get_access_token(workspace_id)
        if not access_token:
            raise ValueError("Twitter not connected")
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        payload = {"text": text}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/tweets",
                    headers=headers,
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()
                
                result = response.json()
                tweet_id = result["data"]["id"]
                
                return {
                    "id": tweet_id,
                    "url": f"https://twitter.com/i/web/status/{tweet_id}",
                    "status": "published"
                }
        except Exception as e:
            logger.error(f"Failed to create tweet: {e}")
            raise
    
    async def create_thread(
        self,
        tweets: List[str],
        workspace_id: UUID,
        account_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Creates a Twitter thread."""
        tweet_ids = []
        reply_to_id = None
        
        for tweet_text in tweets:
            headers = {
                "Authorization": f"Bearer {await self.get_access_token(workspace_id)}",
                "Content-Type": "application/json"
            }
            
            payload = {"text": tweet_text}
            if reply_to_id:
                payload["reply"] = {"in_reply_to_tweet_id": reply_to_id}
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/tweets",
                    headers=headers,
                    json=payload,
                    timeout=30.0
                )
                result = response.json()
                reply_to_id = result["data"]["id"]
                tweet_ids.append(reply_to_id)
        
        return {
            "ids": tweet_ids,
            "thread_url": f"https://twitter.com/i/web/status/{tweet_ids[0]}",
            "status": "published"
        }


twitter_service = TwitterService()

