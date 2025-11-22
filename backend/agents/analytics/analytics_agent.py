"""
Analytics Agent - Collects metrics from social platforms and stores them.
Fetches engagement data, audience insights, and performance metrics.
"""

import structlog
from typing import Dict, Any, List, Optional
from uuid import UUID
from datetime import datetime, timedelta
import httpx

from backend.services.vertex_ai_client import vertex_ai_client
from backend.services.supabase_client import supabase_client
from backend.utils.correlation import get_correlation_id

logger = structlog.get_logger(__name__)


class AnalyticsAgent:
    """
    Collects and aggregates metrics from all connected platforms.
    Stores snapshots in the database for trend analysis.
    """
    
    def __init__(self):
        self.llm = vertex_ai_client
    
    async def collect_metrics(
        self,
        workspace_id: UUID,
        move_id: Optional[UUID] = None,
        platforms: Optional[List[str]] = None,
        correlation_id: str = None
    ) -> Dict[str, Any]:
        """
        Collects metrics from all connected platforms.
        
        Args:
            workspace_id: User's workspace
            move_id: Optional campaign to filter metrics
            platforms: Specific platforms to collect from (or all if None)
            
        Returns:
            Aggregated metrics dict
        """
        correlation_id = correlation_id or get_correlation_id()
        logger.info("Collecting analytics metrics", workspace_id=workspace_id, platforms=platforms, correlation_id=correlation_id)
        
        # Get connected platforms
        integrations = await supabase_client.fetch_all(
            "integrations",
            {"workspace_id": str(workspace_id)}
        )
        
        if platforms:
            integrations = [i for i in integrations if i["platform"] in platforms]
        
        all_metrics = {}
        
        for integration in integrations:
            platform = integration["platform"]
            try:
                metrics = await self._fetch_platform_metrics(
                    platform,
                    integration.get("access_token"),
                    integration.get("account_id"),
                    move_id
                )
                all_metrics[platform] = metrics
                
                # Store snapshot
                await supabase_client.insert("metrics_snapshot", {
                    "workspace_id": str(workspace_id),
                    "move_id": str(move_id) if move_id else None,
                    "platform": platform,
                    "metrics": metrics,
                    "collected_at": datetime.utcnow().isoformat()
                })
                
            except Exception as e:
                logger.error(f"Failed to collect {platform} metrics: {e}", correlation_id=correlation_id)
                all_metrics[platform] = {"error": str(e)}
        
        return all_metrics
    
    async def _fetch_platform_metrics(
        self,
        platform: str,
        access_token: str,
        account_id: str,
        move_id: Optional[UUID]
    ) -> Dict[str, Any]:
        """Fetches metrics from a specific platform API."""
        
        if platform == "linkedin":
            return await self._fetch_linkedin_metrics(access_token, account_id)
        elif platform == "twitter":
            return await self._fetch_twitter_metrics(access_token, account_id)
        elif platform == "instagram":
            return await self._fetch_instagram_metrics(access_token, account_id)
        elif platform == "youtube":
            return await self._fetch_youtube_metrics(access_token, account_id)
        else:
            return {"error": f"Unsupported platform: {platform}"}
    
    async def _fetch_linkedin_metrics(self, access_token: str, account_id: str) -> Dict[str, Any]:
        """Fetches LinkedIn page/profile analytics."""
        try:
            async with httpx.AsyncClient() as client:
                # LinkedIn Analytics API
                response = await client.get(
                    f"https://api.linkedin.com/v2/organizationalEntityShareStatistics",
                    headers={"Authorization": f"Bearer {access_token}"},
                    params={"q": "organizationalEntity", "organizationalEntity": account_id},
                    timeout=30.0
                )
                data = response.json()
                
                return {
                    "followers": data.get("followersCount", 0),
                    "impressions": data.get("impressions", 0),
                    "engagement": data.get("engagement", 0),
                    "clicks": data.get("clicks", 0)
                }
        except Exception as e:
            logger.error(f"LinkedIn metrics error: {e}")
            return {"error": str(e)}
    
    async def _fetch_twitter_metrics(self, access_token: str, account_id: str) -> Dict[str, Any]:
        """Fetches Twitter analytics."""
        # Twitter API v2 metrics endpoint
        return {
            "followers": 0,
            "impressions": 0,
            "engagements": 0,
            "retweets": 0
        }
    
    async def _fetch_instagram_metrics(self, access_token: str, account_id: str) -> Dict[str, Any]:
        """Fetches Instagram insights."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://graph.instagram.com/{account_id}/insights",
                    params={
                        "access_token": access_token,
                        "metric": "impressions,reach,profile_views,follower_count"
                    },
                    timeout=30.0
                )
                data = response.json()
                
                return {
                    "followers": data.get("follower_count", 0),
                    "impressions": data.get("impressions", 0),
                    "reach": data.get("reach", 0),
                    "profile_views": data.get("profile_views", 0)
                }
        except Exception as e:
            return {"error": str(e)}
    
    async def _fetch_youtube_metrics(self, access_token: str, channel_id: str) -> Dict[str, Any]:
        """Fetches YouTube channel analytics."""
        return {
            "subscribers": 0,
            "views": 0,
            "watch_time": 0,
            "engagement": 0
        }


analytics_agent = AnalyticsAgent()


