"""
Daily Wins repository for database operations
"""

from datetime import date, datetime
from typing import Any, Dict, List, Optional

from backend.core.supabase_mgr import get_supabase_client
from .base import Repository
from .filters import Filter, build_query
from .pagination import PaginatedResult, Pagination


class DailyWinsRepository(Repository):
    """Repository for daily wins operations"""

    def __init__(self):
        super().__init__(get_supabase_client())

    async def get_today(self, workspace_id: str) -> Optional[Dict[str, Any]]:
        """Get today's daily win for a workspace"""
        today = date.today().isoformat()
        result = (
            self.client.table("daily_wins")
            .select("*")
            .eq("workspace_id", workspace_id)
            .eq("win_date", today)
            .single()
            .execute()
        )
        return result.data

    async def get_by_date(
        self, workspace_id: str, target_date: date
    ) -> Optional[Dict[str, Any]]:
        """Get daily win for a specific date"""
        result = (
            self.client.table("daily_wins")
            .select("*")
            .eq("workspace_id", workspace_id)
            .eq("win_date", target_date.isoformat())
            .single()
            .execute()
        )
        return result.data

    async def list_by_date_range(
        self,
        workspace_id: str,
        start_date: date,
        end_date: date,
        pagination: Optional[Pagination] = None,
    ) -> PaginatedResult:
        """List daily wins within a date range"""
        query = (
            self.client.table("daily_wins")
            .select("*")
            .eq("workspace_id", workspace_id)
            .gte("win_date", start_date.isoformat())
            .lte("win_date", end_date.isoformat())
        )

        if pagination:
            query = query.order("win_date", desc=True).range(
                pagination.page * pagination.page_size,
                (pagination.page + 1) * pagination.page_size - 1,
            )

        result = query.execute()

        if pagination:
            count_result = (
                self.client.table("daily_wins")
                .select("id", count="exact")
                .eq("workspace_id", workspace_id)
                .gte("win_date", start_date.isoformat())
                .lte("win_date", end_date.isoformat())
                .execute()
            )
            total = count_result.count or 0

            return PaginatedResult(
                items=result.data or [],
                total=total,
                page=pagination.page,
                page_size=pagination.page_size,
                total_pages=(total + pagination.page_size - 1) // pagination.page_size,
            )

        return PaginatedResult(
            items=result.data or [],
            total=len(result.data or []),
            page=0,
            page_size=len(result.data or []),
            total_pages=1,
        )

    async def mark_posted(
        self, win_id: str, posted_at: Optional[datetime] = None
    ) -> Optional[Dict[str, Any]]:
        """Mark a daily win as posted"""
        update_data = {
            "status": "posted",
            "posted_at": (posted_at or datetime.utcnow()).isoformat(),
        }

        result = (
            self.client.table("daily_wins")
            .update(update_data)
            .eq("id", win_id)
            .execute()
        )

        if result.data:
            return result.data[0]
        return None

    async def get_unposted_wins(
        self, workspace_id: str, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get unposted daily wins for a workspace"""
        result = (
            self.client.table("daily_wins")
            .select("*")
            .eq("workspace_id", workspace_id)
            .eq("status", "idea")
            .order("win_date", desc=True)
            .limit(limit)
            .execute()
        )
        return result.data or []

    async def get_posted_wins(
        self, workspace_id: str, days: int = 30, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get recently posted daily wins"""
        from datetime import timedelta

        start_date = (date.today() - timedelta(days=days)).isoformat()
        result = (
            self.client.table("daily_wins")
            .select("*")
            .eq("workspace_id", workspace_id)
            .eq("status", "posted")
            .gte("win_date", start_date)
            .order("posted_at", desc=True)
            .limit(limit)
            .execute()
        )
        return result.data or []

    async def get_win_statistics(
        self, workspace_id: str, days: int = 30
    ) -> Dict[str, Any]:
        """Get statistics for daily wins"""
        from datetime import timedelta

        start_date = (date.today() - timedelta(days=days)).isoformat()

        # Get all wins in date range
        result = (
            self.client.table("daily_wins")
            .select("*")
            .eq("workspace_id", workspace_id)
            .gte("win_date", start_date)
            .execute()
        )
        wins = result.data or []

        if not wins:
            return {
                "workspace_id": workspace_id,
                "days_analyzed": days,
                "total_wins": 0,
            }

        # Calculate statistics
        total_wins = len(wins)
        posted_wins = len([w for w in wins if w.get("status") == "posted"])
        idea_wins = len([w for w in wins if w.get("status") == "idea"])

        # Platform distribution
        platforms = {}
        for win in wins:
            platform = win.get("platform", "unknown")
            platforms[platform] = platforms.get(platform, 0) + 1

        # Engagement metrics
        total_estimated_minutes = sum(w.get("estimated_minutes", 0) for w in wins)
        avg_relevance_score = (
            sum(w.get("relevance_score", 0) for w in wins) / total_wins if wins else 0
        )

        # Posting rate
        posting_rate = (posted_wins / total_wins * 100) if total_wins > 0 else 0

        # Daily breakdown
        daily_counts = {}
        for win in wins:
            win_date = win["win_date"]
            daily_counts[win_date] = daily_counts.get(win_date, 0) + 1

        return {
            "workspace_id": workspace_id,
            "days_analyzed": days,
            "total_wins": total_wins,
            "posted_wins": posted_wins,
            "idea_wins": idea_wins,
            "posting_rate": posting_rate,
            "platforms": platforms,
            "total_estimated_minutes": total_estimated_minutes,
            "average_relevance_score": avg_relevance_score,
            "daily_breakdown": daily_counts,
        }

    async def get_platform_performance(
        self, workspace_id: str, days: int = 30
    ) -> Dict[str, Any]:
        """Get performance metrics by platform"""
        from datetime import timedelta

        start_date = (date.today() - timedelta(days=days)).isoformat()

        # Get wins in date range
        result = (
            self.client.table("daily_wins")
            .select("*")
            .eq("workspace_id", workspace_id)
            .gte("win_date", start_date)
            .execute()
        )
        wins = result.data or []

        # Group by platform
        platform_stats = {}
        for win in wins:
            platform = win.get("platform", "unknown")
            if platform not in platform_stats:
                platform_stats[platform] = {
                    "total_wins": 0,
                    "posted_wins": 0,
                    "total_minutes": 0,
                    "total_relevance": 0,
                    "avg_relevance": 0,
                }

            stats = platform_stats[platform]
            stats["total_wins"] += 1
            stats["total_minutes"] += win.get("estimated_minutes", 0)
            stats["total_relevance"] += win.get("relevance_score", 0)

            if win.get("status") == "posted":
                stats["posted_wins"] += 1

        # Calculate averages and rates
        for platform, stats in platform_stats.items():
            if stats["total_wins"] > 0:
                stats["avg_relevance"] = stats["total_relevance"] / stats["total_wins"]
                stats["posting_rate"] = stats["posted_wins"] / stats["total_wins"] * 100
                stats["avg_minutes"] = stats["total_minutes"] / stats["total_wins"]
            else:
                stats["avg_relevance"] = 0
                stats["posting_rate"] = 0
                stats["avg_minutes"] = 0

        return {
            "workspace_id": workspace_id,
            "days_analyzed": days,
            "platform_stats": platform_stats,
        }

    async def get_trending_topics(
        self, workspace_id: str, days: int = 7
    ) -> List[Dict[str, Any]]:
        """Get trending topics from recent daily wins"""
        from collections import Counter
        from datetime import timedelta

        start_date = (date.today() - timedelta(days=days)).isoformat()

        # Get recent wins
        result = (
            self.client.table("daily_wins")
            .select("topic, relevance_score")
            .eq("workspace_id", workspace_id)
            .gte("win_date", start_date)
            .execute()
        )
        wins = result.data or []

        # Count topics
        topic_counter = Counter()
        topic_relevance = {}

        for win in wins:
            topic = win.get("topic", "")
            if topic:
                topic_counter[topic] += 1
                if topic not in topic_relevance:
                    topic_relevance[topic] = []
                topic_relevance[topic].append(win.get("relevance_score", 0))

        # Calculate trending scores (frequency * average relevance)
        trending_topics = []
        for topic, count in topic_counter.most_common(20):
            avg_relevance = (
                sum(topic_relevance[topic]) / len(topic_relevance[topic])
                if topic_relevance[topic]
                else 0
            )
            trending_score = count * avg_relevance

            trending_topics.append(
                {
                    "topic": topic,
                    "frequency": count,
                    "avg_relevance": avg_relevance,
                    "trending_score": trending_score,
                }
            )

        # Sort by trending score
        trending_topics.sort(key=lambda x: x["trending_score"], reverse=True)

        return trending_topics[:10]  # Return top 10

    async def expand_win(
        self, win_id: str, expanded_content: str, content_html: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Expand a daily win with full content"""
        update_data = {"expanded_content": expanded_content, "status": "expanded"}

        if content_html:
            update_data["content_html"] = content_html

        result = (
            self.client.table("daily_wins")
            .update(update_data)
            .eq("id", win_id)
            .execute()
        )

        if result.data:
            return result.data[0]
        return None

    async def link_to_asset(self, win_id: str, asset_id: str) -> bool:
        """Link a daily win to a muse asset"""
        result = (
            self.client.table("daily_wins")
            .update({"expanded_content_id": asset_id})
            .eq("id", win_id)
            .execute()
        )
        return len(result.data or []) > 0

    async def get_content_calendar(
        self, workspace_id: str, start_date: date, end_date: date
    ) -> List[Dict[str, Any]]:
        """Get content calendar for date range"""
        result = (
            self.client.table("daily_wins")
            .select("*")
            .eq("workspace_id", workspace_id)
            .gte("win_date", start_date.isoformat())
            .lte("win_date", end_date.isoformat())
            .order("win_date")
            .execute()
        )
        wins = result.data or []

        # Build calendar data
        calendar = []
        for win in wins:
            calendar.append(
                {
                    "date": win["win_date"],
                    "topic": win.get("topic"),
                    "angle": win.get("angle"),
                    "hook": win.get("hook"),
                    "platform": win.get("platform"),
                    "status": win.get("status"),
                    "estimated_minutes": win.get("estimated_minutes"),
                    "relevance_score": win.get("relevance_score"),
                    "posted_at": win.get("posted_at"),
                    "has_content": win.get("expanded_content") is not None
                    or win.get("expanded_content_id") is not None,
                }
            )

        return calendar

    async def bulk_update_status(self, win_ids: List[str], status: str) -> int:
        """Update status for multiple daily wins"""
        valid_statuses = ["idea", "expanded", "posted", "archived"]
        if status not in valid_statuses:
            raise ValueError(
                f"Invalid status: {status}. Must be one of: {valid_statuses}"
            )

        update_data = {"status": status}
        if status == "posted":
            update_data["posted_at"] = datetime.utcnow().isoformat()

        # Update in batches
        updated_count = 0
        batch_size = 50

        for i in range(0, len(win_ids), batch_size):
            batch = win_ids[i : i + batch_size]
            result = (
                self.client.table("daily_wins")
                .update(update_data)
                .in_("id", batch)
                .execute()
            )
            updated_count += len(result.data or [])

        return updated_count

    async def get_productivity_metrics(
        self, workspace_id: str, days: int = 30
    ) -> Dict[str, Any]:
        """Get productivity metrics for daily wins"""
        from datetime import timedelta

        start_date = (date.today() - timedelta(days=days)).isoformat()

        # Get wins in date range
        result = (
            self.client.table("daily_wins")
            .select("*")
            .eq("workspace_id", workspace_id)
            .gte("win_date", start_date)
            .execute()
        )
        wins = result.data or []

        if not wins:
            return {
                "workspace_id": workspace_id,
                "days_analyzed": days,
                "total_wins": 0,
            }

        # Calculate productivity metrics
        total_wins = len(wins)
        posted_wins = len([w for w in wins if w.get("status") == "posted"])
        total_minutes = sum(w.get("estimated_minutes", 0) for w in wins)

        # Daily averages
        days_with_wins = len(set(w["win_date"] for w in wins))
        avg_wins_per_day = total_wins / days if days > 0 else 0
        avg_minutes_per_day = total_minutes / days if days > 0 else 0
        avg_minutes_per_win = total_minutes / total_wins if total_wins > 0 else 0

        # Consistency metrics
        ideal_wins = days  # One win per day
        consistency_rate = (total_wins / ideal_wins * 100) if ideal_wins > 0 else 0

        # Quality metrics
        avg_relevance = (
            sum(w.get("relevance_score", 0) for w in wins) / total_wins
            if total_wins > 0
            else 0
        )
        high_quality_wins = len([w for w in wins if w.get("relevance_score", 0) >= 80])
        quality_rate = (high_quality_wins / total_wins * 100) if total_wins > 0 else 0

        return {
            "workspace_id": workspace_id,
            "days_analyzed": days,
            "total_wins": total_wins,
            "posted_wins": posted_wins,
            "days_with_wins": days_with_wins,
            "total_minutes": total_minutes,
            "avg_wins_per_day": avg_wins_per_day,
            "avg_minutes_per_day": avg_minutes_per_day,
            "avg_minutes_per_win": avg_minutes_per_win,
            "consistency_rate": consistency_rate,
            "avg_relevance_score": avg_relevance,
            "high_quality_wins": high_quality_wins,
            "quality_rate": quality_rate,
        }

    async def archive_old_wins(self, workspace_id: str, days_old: int = 90) -> int:
        """Archive old daily wins"""
        from datetime import timedelta

        cutoff_date = (date.today() - timedelta(days=days_old)).isoformat()

        result = (
            self.client.table("daily_wins")
            .update({"status": "archived"})
            .eq("workspace_id", workspace_id)
            .lt("win_date", cutoff_date)
            .neq("status", "archived")
            .execute()
        )

        return len(result.data or [])
