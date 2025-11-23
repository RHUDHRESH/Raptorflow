"""
Metrics Collector Agent - Collects and normalizes metrics from multiple platforms.
Pulls performance data from Supabase and connected platforms (LinkedIn, Twitter, Instagram, etc.)
and normalizes them into a unified structure.
"""

import structlog
from typing import Dict, Any, List, Optional
from uuid import UUID
from datetime import datetime, timezone, timedelta
import httpx

from backend.services.vertex_ai_client import vertex_ai_client
from backend.services.supabase_client import supabase_client
from backend.utils.correlation import get_correlation_id
from backend.utils.cache import redis_cache

logger = structlog.get_logger(__name__)


class UnifiedMetrics:
    """Standardized metrics structure across all platforms."""

    def __init__(
        self,
        platform: str,
        impressions: int = 0,
        reach: int = 0,
        engagements: int = 0,
        clicks: int = 0,
        shares: int = 0,
        comments: int = 0,
        likes: int = 0,
        saves: int = 0,
        followers: int = 0,
        followers_change: int = 0,
        engagement_rate: float = 0.0,
        click_through_rate: float = 0.0,
        timestamp: datetime = None,
        raw_data: Dict[str, Any] = None
    ):
        self.platform = platform
        self.impressions = impressions
        self.reach = reach
        self.engagements = engagements
        self.clicks = clicks
        self.shares = shares
        self.comments = comments
        self.likes = likes
        self.saves = saves
        self.followers = followers
        self.followers_change = followers_change
        self.engagement_rate = engagement_rate
        self.click_through_rate = click_through_rate
        self.timestamp = timestamp or datetime.now(timezone.utc)
        self.raw_data = raw_data or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "platform": self.platform,
            "impressions": self.impressions,
            "reach": self.reach,
            "engagements": self.engagements,
            "clicks": self.clicks,
            "shares": self.shares,
            "comments": self.comments,
            "likes": self.likes,
            "saves": self.saves,
            "followers": self.followers,
            "followers_change": self.followers_change,
            "engagement_rate": self.engagement_rate,
            "click_through_rate": self.click_through_rate,
            "timestamp": self.timestamp.isoformat(),
            "raw_data": self.raw_data
        }


class MetricsCollectorAgent:
    """
    Collects and normalizes metrics from all connected platforms.
    Provides a unified interface for analytics across different channels.
    """

    def __init__(self):
        self.llm = vertex_ai_client
        self.cache_ttl = 300  # 5 minutes cache for metrics

    async def collect_metrics(
        self,
        workspace_id: UUID,
        move_id: Optional[UUID] = None,
        platforms: Optional[List[str]] = None,
        time_range_days: int = 7,
        correlation_id: str = None
    ) -> Dict[str, Any]:
        """
        Collects metrics from all connected platforms and normalizes them.

        Args:
            workspace_id: User's workspace
            move_id: Optional campaign to filter metrics
            platforms: Specific platforms to collect from (or all if None)
            time_range_days: How many days back to collect
            correlation_id: Request correlation ID

        Returns:
            Dictionary with unified metrics by platform and aggregated totals
        """
        correlation_id = correlation_id or get_correlation_id()
        logger.info(
            "Collecting analytics metrics",
            workspace_id=workspace_id,
            move_id=move_id,
            platforms=platforms,
            time_range_days=time_range_days,
            correlation_id=correlation_id
        )

        # Check cache first
        cache_key = f"metrics:{workspace_id}:{move_id}:{time_range_days}"
        cached = await redis_cache.get(cache_key)
        if cached:
            logger.info("Returning cached metrics", correlation_id=correlation_id)
            return cached

        # Get connected platforms
        integrations = await supabase_client.fetch_all(
            "integrations",
            {"workspace_id": str(workspace_id), "status": "active"}
        )

        if platforms:
            integrations = [i for i in integrations if i["platform"] in platforms]

        platform_metrics = {}
        errors = {}

        for integration in integrations:
            platform = integration["platform"]
            try:
                # Fetch platform metrics
                raw_metrics = await self._fetch_platform_metrics(
                    platform,
                    integration.get("access_token"),
                    integration.get("account_id"),
                    move_id,
                    time_range_days,
                    correlation_id
                )

                # Normalize to unified format
                unified = self._normalize_metrics(platform, raw_metrics)
                platform_metrics[platform] = unified.to_dict()

                # Store snapshot in database
                await supabase_client.insert("metrics_snapshot", {
                    "id": str(UUID(int=0)),  # Will be auto-generated
                    "workspace_id": str(workspace_id),
                    "move_id": str(move_id) if move_id else None,
                    "platform": platform,
                    "metrics": unified.to_dict(),
                    "collected_at": datetime.now(timezone.utc).isoformat()
                })

                logger.info(
                    f"Collected {platform} metrics",
                    impressions=unified.impressions,
                    engagements=unified.engagements,
                    correlation_id=correlation_id
                )

            except Exception as e:
                logger.error(
                    f"Failed to collect {platform} metrics: {e}",
                    correlation_id=correlation_id
                )
                errors[platform] = str(e)

        # Calculate aggregated totals
        aggregated = self._aggregate_metrics(platform_metrics)

        result = {
            "platform_metrics": platform_metrics,
            "aggregated": aggregated,
            "errors": errors,
            "collection_time": datetime.now(timezone.utc).isoformat(),
            "time_range_days": time_range_days
        }

        # Cache the result
        await redis_cache.set(cache_key, result, ttl=self.cache_ttl)

        return result

    async def _fetch_platform_metrics(
        self,
        platform: str,
        access_token: str,
        account_id: str,
        move_id: Optional[UUID],
        time_range_days: int,
        correlation_id: str
    ) -> Dict[str, Any]:
        """Fetches raw metrics from a specific platform API."""

        if platform == "linkedin":
            return await self._fetch_linkedin_metrics(access_token, account_id, time_range_days)
        elif platform == "twitter":
            return await self._fetch_twitter_metrics(access_token, account_id, time_range_days)
        elif platform == "instagram":
            return await self._fetch_instagram_metrics(access_token, account_id, time_range_days)
        elif platform == "youtube":
            return await self._fetch_youtube_metrics(access_token, account_id, time_range_days)
        elif platform == "email":
            return await self._fetch_email_metrics(account_id, move_id, time_range_days)
        else:
            logger.warning(f"Unsupported platform: {platform}", correlation_id=correlation_id)
            return {"error": f"Unsupported platform: {platform}"}

    async def _fetch_linkedin_metrics(
        self,
        access_token: str,
        account_id: str,
        time_range_days: int
    ) -> Dict[str, Any]:
        """Fetches LinkedIn page/profile analytics."""
        try:
            async with httpx.AsyncClient() as client:
                # Calculate time range
                start_date = datetime.now(timezone.utc) - timedelta(days=time_range_days)
                start_timestamp = int(start_date.timestamp() * 1000)
                end_timestamp = int(datetime.now(timezone.utc).timestamp() * 1000)

                # LinkedIn Analytics API - Organization Stats
                response = await client.get(
                    f"https://api.linkedin.com/v2/organizationalEntityShareStatistics",
                    headers={"Authorization": f"Bearer {access_token}"},
                    params={
                        "q": "organizationalEntity",
                        "organizationalEntity": account_id,
                        "timeIntervals.timeGranularityType": "DAY",
                        "timeIntervals.timeRange.start": start_timestamp,
                        "timeIntervals.timeRange.end": end_timestamp
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()

                # Aggregate stats across time periods
                total_impressions = 0
                total_clicks = 0
                total_likes = 0
                total_comments = 0
                total_shares = 0

                for element in data.get("elements", []):
                    stats = element.get("totalShareStatistics", {})
                    total_impressions += stats.get("impressionCount", 0)
                    total_clicks += stats.get("clickCount", 0)
                    total_likes += stats.get("likeCount", 0)
                    total_comments += stats.get("commentCount", 0)
                    total_shares += stats.get("shareCount", 0)

                # Get follower count
                follower_response = await client.get(
                    f"https://api.linkedin.com/v2/networkSizes/{account_id}",
                    headers={"Authorization": f"Bearer {access_token}"},
                    params={"edgeType": "CompanyFollowedByMember"},
                    timeout=30.0
                )
                follower_data = follower_response.json()

                return {
                    "impressions": total_impressions,
                    "clicks": total_clicks,
                    "likes": total_likes,
                    "comments": total_comments,
                    "shares": total_shares,
                    "followers": follower_data.get("firstDegreeSize", 0),
                    "engagements": total_likes + total_comments + total_shares
                }

        except Exception as e:
            logger.error(f"LinkedIn metrics error: {e}")
            return {"error": str(e)}

    async def _fetch_twitter_metrics(
        self,
        access_token: str,
        account_id: str,
        time_range_days: int
    ) -> Dict[str, Any]:
        """Fetches Twitter/X analytics."""
        try:
            async with httpx.AsyncClient() as client:
                # Twitter API v2 - User Metrics
                start_time = (datetime.now(timezone.utc) - timedelta(days=time_range_days)).isoformat() + "Z"

                response = await client.get(
                    f"https://api.twitter.com/2/users/{account_id}/tweets",
                    headers={"Authorization": f"Bearer {access_token}"},
                    params={
                        "tweet.fields": "public_metrics",
                        "start_time": start_time,
                        "max_results": 100
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()

                total_impressions = 0
                total_likes = 0
                total_retweets = 0
                total_replies = 0

                for tweet in data.get("data", []):
                    metrics = tweet.get("public_metrics", {})
                    total_impressions += metrics.get("impression_count", 0)
                    total_likes += metrics.get("like_count", 0)
                    total_retweets += metrics.get("retweet_count", 0)
                    total_replies += metrics.get("reply_count", 0)

                # Get user info for follower count
                user_response = await client.get(
                    f"https://api.twitter.com/2/users/{account_id}",
                    headers={"Authorization": f"Bearer {access_token}"},
                    params={"user.fields": "public_metrics"},
                    timeout=30.0
                )
                user_data = user_response.json()
                user_metrics = user_data.get("data", {}).get("public_metrics", {})

                return {
                    "impressions": total_impressions,
                    "likes": total_likes,
                    "retweets": total_retweets,
                    "replies": total_replies,
                    "followers": user_metrics.get("followers_count", 0),
                    "engagements": total_likes + total_retweets + total_replies
                }

        except Exception as e:
            logger.error(f"Twitter metrics error: {e}")
            return {"error": str(e)}

    async def _fetch_instagram_metrics(
        self,
        access_token: str,
        account_id: str,
        time_range_days: int
    ) -> Dict[str, Any]:
        """Fetches Instagram insights."""
        try:
            async with httpx.AsyncClient() as client:
                # Instagram Graph API - Account Insights
                since = int((datetime.now(timezone.utc) - timedelta(days=time_range_days)).timestamp())
                until = int(datetime.now(timezone.utc).timestamp())

                response = await client.get(
                    f"https://graph.instagram.com/{account_id}/insights",
                    params={
                        "access_token": access_token,
                        "metric": "impressions,reach,profile_views,follower_count",
                        "period": "day",
                        "since": since,
                        "until": until
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()

                # Parse insights
                impressions = 0
                reach = 0
                profile_views = 0
                followers = 0

                for insight in data.get("data", []):
                    metric_name = insight.get("name")
                    values = insight.get("values", [])

                    if metric_name == "impressions":
                        impressions = sum(v.get("value", 0) for v in values)
                    elif metric_name == "reach":
                        reach = sum(v.get("value", 0) for v in values)
                    elif metric_name == "profile_views":
                        profile_views = sum(v.get("value", 0) for v in values)
                    elif metric_name == "follower_count":
                        followers = values[-1].get("value", 0) if values else 0

                # Get media insights for engagement
                media_response = await client.get(
                    f"https://graph.instagram.com/{account_id}/media",
                    params={
                        "access_token": access_token,
                        "fields": "like_count,comments_count,saved_by_count",
                        "limit": 100
                    },
                    timeout=30.0
                )
                media_data = media_response.json()

                total_likes = 0
                total_comments = 0
                total_saves = 0

                for media in media_data.get("data", []):
                    total_likes += media.get("like_count", 0)
                    total_comments += media.get("comments_count", 0)
                    total_saves += media.get("saved_by_count", 0)

                return {
                    "impressions": impressions,
                    "reach": reach,
                    "profile_views": profile_views,
                    "followers": followers,
                    "likes": total_likes,
                    "comments": total_comments,
                    "saves": total_saves,
                    "engagements": total_likes + total_comments + total_saves
                }

        except Exception as e:
            logger.error(f"Instagram metrics error: {e}")
            return {"error": str(e)}

    async def _fetch_youtube_metrics(
        self,
        access_token: str,
        channel_id: str,
        time_range_days: int
    ) -> Dict[str, Any]:
        """Fetches YouTube channel analytics."""
        try:
            async with httpx.AsyncClient() as client:
                # YouTube Analytics API
                start_date = (datetime.now(timezone.utc) - timedelta(days=time_range_days)).strftime("%Y-%m-%d")
                end_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

                response = await client.get(
                    "https://youtubeanalytics.googleapis.com/v2/reports",
                    headers={"Authorization": f"Bearer {access_token}"},
                    params={
                        "ids": f"channel=={channel_id}",
                        "startDate": start_date,
                        "endDate": end_date,
                        "metrics": "views,estimatedMinutesWatched,likes,comments,shares,subscribersGained",
                        "dimensions": "day"
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()

                # Aggregate metrics
                rows = data.get("rows", [])
                total_views = sum(row[1] for row in rows)
                total_watch_time = sum(row[2] for row in rows)
                total_likes = sum(row[3] for row in rows)
                total_comments = sum(row[4] for row in rows)
                total_shares = sum(row[5] for row in rows)
                subscribers_gained = sum(row[6] for row in rows)

                return {
                    "views": total_views,
                    "watch_time_minutes": total_watch_time,
                    "likes": total_likes,
                    "comments": total_comments,
                    "shares": total_shares,
                    "subscribers_gained": subscribers_gained,
                    "engagements": total_likes + total_comments + total_shares
                }

        except Exception as e:
            logger.error(f"YouTube metrics error: {e}")
            return {"error": str(e)}

    async def _fetch_email_metrics(
        self,
        account_id: str,
        move_id: Optional[UUID],
        time_range_days: int
    ) -> Dict[str, Any]:
        """Fetches email campaign metrics from Supabase."""
        try:
            # Query email assets for this move
            filters = {
                "type": "email",
                "status": "published"
            }
            if move_id:
                filters["move_id"] = str(move_id)

            email_assets = await supabase_client.fetch_all("assets", filters)

            # Aggregate metrics from metadata
            total_sent = 0
            total_delivered = 0
            total_opens = 0
            total_clicks = 0
            total_bounces = 0
            total_unsubscribes = 0

            for asset in email_assets:
                metadata = asset.get("metadata", {})
                email_metrics = metadata.get("email_metrics", {})

                total_sent += email_metrics.get("sent", 0)
                total_delivered += email_metrics.get("delivered", 0)
                total_opens += email_metrics.get("opens", 0)
                total_clicks += email_metrics.get("clicks", 0)
                total_bounces += email_metrics.get("bounces", 0)
                total_unsubscribes += email_metrics.get("unsubscribes", 0)

            return {
                "sent": total_sent,
                "delivered": total_delivered,
                "opens": total_opens,
                "clicks": total_clicks,
                "bounces": total_bounces,
                "unsubscribes": total_unsubscribes,
                "engagements": total_opens + total_clicks
            }

        except Exception as e:
            logger.error(f"Email metrics error: {e}")
            return {"error": str(e)}

    def _normalize_metrics(self, platform: str, raw_metrics: Dict[str, Any]) -> UnifiedMetrics:
        """Normalizes platform-specific metrics into unified format."""

        if "error" in raw_metrics:
            return UnifiedMetrics(platform=platform, raw_data=raw_metrics)

        # Map platform-specific fields to unified structure
        if platform == "linkedin":
            impressions = raw_metrics.get("impressions", 0)
            engagements = raw_metrics.get("engagements", 0)
            return UnifiedMetrics(
                platform=platform,
                impressions=impressions,
                engagements=engagements,
                clicks=raw_metrics.get("clicks", 0),
                likes=raw_metrics.get("likes", 0),
                comments=raw_metrics.get("comments", 0),
                shares=raw_metrics.get("shares", 0),
                followers=raw_metrics.get("followers", 0),
                engagement_rate=engagements / impressions if impressions > 0 else 0.0,
                raw_data=raw_metrics
            )

        elif platform == "twitter":
            impressions = raw_metrics.get("impressions", 0)
            engagements = raw_metrics.get("engagements", 0)
            return UnifiedMetrics(
                platform=platform,
                impressions=impressions,
                engagements=engagements,
                likes=raw_metrics.get("likes", 0),
                shares=raw_metrics.get("retweets", 0),
                comments=raw_metrics.get("replies", 0),
                followers=raw_metrics.get("followers", 0),
                engagement_rate=engagements / impressions if impressions > 0 else 0.0,
                raw_data=raw_metrics
            )

        elif platform == "instagram":
            impressions = raw_metrics.get("impressions", 0)
            reach = raw_metrics.get("reach", 0)
            engagements = raw_metrics.get("engagements", 0)
            return UnifiedMetrics(
                platform=platform,
                impressions=impressions,
                reach=reach,
                engagements=engagements,
                likes=raw_metrics.get("likes", 0),
                comments=raw_metrics.get("comments", 0),
                saves=raw_metrics.get("saves", 0),
                followers=raw_metrics.get("followers", 0),
                engagement_rate=engagements / impressions if impressions > 0 else 0.0,
                raw_data=raw_metrics
            )

        elif platform == "youtube":
            views = raw_metrics.get("views", 0)
            engagements = raw_metrics.get("engagements", 0)
            return UnifiedMetrics(
                platform=platform,
                impressions=views,
                engagements=engagements,
                likes=raw_metrics.get("likes", 0),
                comments=raw_metrics.get("comments", 0),
                shares=raw_metrics.get("shares", 0),
                followers=raw_metrics.get("subscribers_gained", 0),
                engagement_rate=engagements / views if views > 0 else 0.0,
                raw_data=raw_metrics
            )

        elif platform == "email":
            sent = raw_metrics.get("sent", 0)
            delivered = raw_metrics.get("delivered", 0)
            opens = raw_metrics.get("opens", 0)
            clicks = raw_metrics.get("clicks", 0)
            return UnifiedMetrics(
                platform=platform,
                impressions=delivered,
                engagements=opens + clicks,
                clicks=clicks,
                engagement_rate=opens / delivered if delivered > 0 else 0.0,
                click_through_rate=clicks / opens if opens > 0 else 0.0,
                raw_data=raw_metrics
            )

        else:
            return UnifiedMetrics(platform=platform, raw_data=raw_metrics)

    def _aggregate_metrics(self, platform_metrics: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregates metrics across all platforms."""

        total_impressions = 0
        total_reach = 0
        total_engagements = 0
        total_clicks = 0
        total_shares = 0
        total_comments = 0
        total_likes = 0
        total_followers = 0

        for platform, metrics in platform_metrics.items():
            total_impressions += metrics.get("impressions", 0)
            total_reach += metrics.get("reach", 0)
            total_engagements += metrics.get("engagements", 0)
            total_clicks += metrics.get("clicks", 0)
            total_shares += metrics.get("shares", 0)
            total_comments += metrics.get("comments", 0)
            total_likes += metrics.get("likes", 0)
            total_followers += metrics.get("followers", 0)

        # Calculate aggregate rates
        engagement_rate = total_engagements / total_impressions if total_impressions > 0 else 0.0
        click_through_rate = total_clicks / total_impressions if total_impressions > 0 else 0.0

        return {
            "total_impressions": total_impressions,
            "total_reach": total_reach,
            "total_engagements": total_engagements,
            "total_clicks": total_clicks,
            "total_shares": total_shares,
            "total_comments": total_comments,
            "total_likes": total_likes,
            "total_followers": total_followers,
            "engagement_rate": round(engagement_rate, 4),
            "click_through_rate": round(click_through_rate, 4)
        }


# Global singleton instance
metrics_collector_agent = MetricsCollectorAgent()
