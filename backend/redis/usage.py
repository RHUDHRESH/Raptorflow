"""
Usage tracking service using Redis.

Tracks API usage, resource consumption, and billing metrics
with workspace isolation and fraud prevention.
"""

import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from .client import get_redis
from .critical_fixes import UsageDataValidator


class UsageTracker:
    """Redis-based usage tracking service."""

    KEY_PREFIX = "usage:"
    DAILY_PREFIX = "daily:"
    MONTHLY_PREFIX = "monthly:"
    REALTIME_PREFIX = "realtime:"

    def __init__(self):
        self.redis = get_redis()
        self.validator = UsageDataValidator()

    def _get_key(self, workspace_id: str, period: str, date: str) -> str:
        """Get Redis key for usage tracking."""
        return f"{self.KEY_PREFIX}{period}{workspace_id}:{date}"

    def _get_realtime_key(self, workspace_id: str) -> str:
        """Get Redis key for realtime usage."""
        return f"{self.REALTIME_PREFIX}{workspace_id}"

    async def track_usage(
        self,
        workspace_id: str,
        event_type: str,
        quantity: float,
        metadata: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None,
    ) -> bool:
        """Track a usage event."""
        if timestamp is None:
            timestamp = datetime.now()

        # Create usage event
        usage_data = {
            "event_type": event_type,
            "quantity": quantity,
            "timestamp": timestamp.isoformat(),
            "metadata": metadata or {},
        }

        # Validate usage data
        try:
            validated_data = self.validator.validate_usage_data(
                {"events": [usage_data]}
            )
        except ValueError as e:
            raise ValueError(f"Invalid usage data: {e}")

        # Track in different time windows
        date_str = timestamp.strftime("%Y-%m-%d")
        month_str = timestamp.strftime("%Y-%m")

        # Daily usage
        daily_key = self._get_key(workspace_id, self.DAILY_PREFIX, date_str)
        await self._add_usage_to_key(daily_key, validated_data["events"][0])

        # Monthly usage
        monthly_key = self._get_key(workspace_id, self.MONTHLY_PREFIX, month_str)
        await self._add_usage_to_key(monthly_key, validated_data["events"][0])

        # Realtime usage (for current limits)
        realtime_key = self._get_realtime_key(workspace_id)
        await self._add_usage_to_key(
            realtime_key, validated_data["events"][0], ttl=3600
        )

        return True

    async def _add_usage_to_key(
        self, key: str, event: Dict[str, Any], ttl: Optional[int] = None
    ):
        """Add usage event to a tracking key."""
        # Use Redis hash to store usage by type
        field = f"{event['event_type']}:{event['timestamp']}"

        # Store event data
        await self.redis.async_client.hset(key, field, json.dumps(event))

        # Update totals
        total_field = f"total:{event['event_type']}"
        current_total = await self.redis.async_client.hget(key, total_field)
        new_total = float(current_total or 0) + event["quantity"]
        await self.redis.async_client.hset(key, total_field, str(new_total))

        # Set TTL if provided
        if ttl:
            await self.redis.async_client.expire(key, ttl)

    async def get_daily_usage(
        self, workspace_id: str, date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get daily usage for workspace."""
        if date is None:
            date = datetime.now()

        date_str = date.strftime("%Y-%m-%d")
        key = self._get_key(workspace_id, self.DAILY_PREFIX, date_str)

        return await self._get_usage_from_key(key)

    async def get_monthly_usage(
        self, workspace_id: str, year: Optional[int] = None, month: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get monthly usage for workspace."""
        if year is None or month is None:
            now = datetime.now()
            year = now.year
            month = now.month

        month_str = f"{year:04d}-{month:02d}"
        key = self._get_key(workspace_id, self.MONTHLY_PREFIX, month_str)

        return await self._get_usage_from_key(key)

    async def get_realtime_usage(self, workspace_id: str) -> Dict[str, Any]:
        """Get current realtime usage for workspace."""
        key = self._get_realtime_key(workspace_id)
        return await self._get_usage_from_key(key)

    async def _get_usage_from_key(self, key: str) -> Dict[str, Any]:
        """Get usage data from Redis key."""
        # Get all hash fields
        hash_data = await self.redis.async_client.hgetall(key)

        if not hash_data:
            return {"events": [], "totals": {}}

        # Parse data
        events = []
        totals = {}

        for field, value in hash_data.items():
            if field.startswith("total:"):
                event_type = field.replace("total:", "")
                totals[event_type] = float(value)
            elif ":" in field:
                try:
                    event = json.loads(value)
                    events.append(event)
                except (json.JSONDecodeError, ValueError):
                    continue

        return {"events": events, "totals": totals}

    async def get_usage_summary(
        self, workspace_id: str, days: int = 30
    ) -> Dict[str, Any]:
        """Get usage summary for the last N days."""
        summary = {"daily_usage": {}, "totals": {}, "trends": {}}

        # Collect daily data
        for i in range(days):
            date = datetime.now() - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            daily_data = await self.get_daily_usage(workspace_id, date)
            summary["daily_usage"][date_str] = daily_data["totals"]

        # Calculate totals
        for daily_totals in summary["daily_usage"].values():
            for event_type, quantity in daily_totals.items():
                summary["totals"][event_type] = (
                    summary["totals"].get(event_type, 0) + quantity
                )

        # Calculate trends (simple average comparison)
        if len(summary["daily_usage"]) > 1:
            recent_days = list(summary["daily_usage"].values())[:7]  # Last 7 days
            older_days = list(summary["daily_usage"].values())[7:14]  # Previous 7 days

            for event_type in summary["totals"].keys():
                recent_avg = sum(d.get(event_type, 0) for d in recent_days) / len(
                    recent_days
                )
                older_avg = (
                    sum(d.get(event_type, 0) for d in older_days) / len(older_days)
                    if older_days
                    else 0
                )

                trend = (recent_avg - older_avg) / older_avg if older_avg > 0 else 0
                summary["trends"][event_type] = {
                    "change_percent": trend * 100,
                    "direction": (
                        "up" if trend > 0 else "down" if trend < 0 else "stable"
                    ),
                }

        return summary

    async def check_usage_limits(
        self, workspace_id: str, limits: Dict[str, float]
    ) -> Dict[str, Any]:
        """Check if workspace is within usage limits."""
        realtime_usage = await self.get_realtime_usage(workspace_id)

        violations = []
        remaining = {}

        for event_type, limit in limits.items():
            current_usage = realtime_usage["totals"].get(event_type, 0)
            remaining[event_type] = max(0, limit - current_usage)

            if current_usage > limit:
                violations.append(
                    {
                        "event_type": event_type,
                        "current": current_usage,
                        "limit": limit,
                        "overage": current_usage - limit,
                    }
                )

        return {
            "within_limits": len(violations) == 0,
            "violations": violations,
            "remaining": remaining,
        }

    async def set_usage_limit(
        self, workspace_id: str, event_type: str, limit: float, period: str = "monthly"
    ) -> bool:
        """Set usage limit for workspace."""
        limit_key = f"limit:{period}:{workspace_id}:{event_type}"
        await self.redis.async_client.set(limit_key, str(limit), ex=2592000)  # 30 days
        return True

    async def get_usage_limit(
        self, workspace_id: str, event_type: str, period: str = "monthly"
    ) -> Optional[float]:
        """Get usage limit for workspace."""
        limit_key = f"limit:{period}:{workspace_id}:{event_type}"
        limit_str = await self.redis.async_client.get(limit_key)
        return float(limit_str) if limit_str else None

    async def cleanup_old_usage_data(self, retention_days: int = 90):
        """Clean up old usage data."""
        # This would typically be run as a background job
        cutoff_date = datetime.now() - timedelta(days=retention_days)

        # In production, implement proper cleanup logic
        # For now, this is a placeholder
        pass

    async def export_usage_data(
        self, workspace_id: str, start_date: datetime, end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Export usage data for date range."""
        all_events = []
        current_date = start_date

        while current_date <= end_date:
            daily_data = await self.get_daily_usage(workspace_id, current_date)
            all_events.extend(daily_data["events"])
            current_date += timedelta(days=1)

        return all_events

    async def get_top_consumers(
        self, event_type: str, limit: int = 10, period: str = "monthly"
    ) -> List[Dict[str, Any]]:
        """Get top consumers by usage."""
        # This would require maintaining a sorted set of usage by workspace
        # For now, return placeholder data
        return []
