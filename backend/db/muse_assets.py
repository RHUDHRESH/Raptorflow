"""
Muse Assets repository for database operations
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from ..core.supabase import get_supabase_client
from .base import Repository
from .filters import Filter, build_query
from .pagination import PaginatedResult, Pagination


class MuseAssetRepository(Repository):
    """Repository for muse asset operations"""

    def __init__(self):
        super().__init__(get_supabase_client())

    async def list_by_type(
        self,
        workspace_id: str,
        asset_type: str,
        pagination: Optional[Pagination] = None,
    ) -> PaginatedResult:
        """List assets by type for a workspace"""
        query = (
            self.client.table("muse_assets")
            .select("*")
            .eq("workspace_id", workspace_id)
            .eq("asset_type", asset_type)
        )

        if pagination:
            query = query.order("created_at", desc=True).range(
                pagination.page * pagination.page_size,
                (pagination.page + 1) * pagination.page_size - 1,
            )

        result = query.execute()

        if pagination:
            count_result = (
                self.client.table("muse_assets")
                .select("id", count="exact")
                .eq("workspace_id", workspace_id)
                .eq("asset_type", asset_type)
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

    async def list_by_move(
        self, move_id: str, pagination: Optional[Pagination] = None
    ) -> PaginatedResult:
        """List assets for a specific move"""
        query = self.client.table("muse_assets").select("*").eq("move_id", move_id)

        if pagination:
            query = query.order("created_at", desc=True).range(
                pagination.page * pagination.page_size,
                (pagination.page + 1) * pagination.page_size - 1,
            )

        result = query.execute()

        if pagination:
            count_result = (
                self.client.table("muse_assets")
                .select("id", count="exact")
                .eq("move_id", move_id)
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

    async def list_by_icp(
        self, target_icp_id: str, pagination: Optional[Pagination] = None
    ) -> PaginatedResult:
        """List assets targeting a specific ICP"""
        query = (
            self.client.table("muse_assets")
            .select("*")
            .eq("target_icp_id", target_icp_id)
        )

        if pagination:
            query = query.order("created_at", desc=True).range(
                pagination.page * pagination.page_size,
                (pagination.page + 1) * pagination.page_size - 1,
            )

        result = query.execute()

        if pagination:
            count_result = (
                self.client.table("muse_assets")
                .select("id", count="exact")
                .eq("target_icp_id", target_icp_id)
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

    async def search(
        self,
        workspace_id: str,
        query: str,
        asset_types: Optional[List[str]] = None,
        pagination: Optional[Pagination] = None,
    ) -> PaginatedResult:
        """Search assets by content"""
        db_query = (
            self.client.table("muse_assets")
            .select("*")
            .eq("workspace_id", workspace_id)
        )

        # Add text search
        if query:
            db_query = db_query.or_(f"title.ilike.%{query}%,content.ilike.%{query}%")

        # Filter by asset types
        if asset_types:
            db_query = db_query.in_("asset_type", asset_types)

        if pagination:
            db_query = db_query.order("created_at", desc=True).range(
                pagination.page * pagination.page_size,
                (pagination.page + 1) * pagination.page_size - 1,
            )

        result = db_query.execute()

        if pagination:
            # Build count query
            count_query = (
                self.client.table("muse_assets")
                .select("id", count="exact")
                .eq("workspace_id", workspace_id)
            )
            if query:
                count_query = count_query.or_(
                    f"title.ilike.%{query}%,content.ilike.%{query}%"
                )
            if asset_types:
                count_query = count_query.in_("asset_type", asset_types)

            count_result = count_query.execute()
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

    async def update_quality_score(
        self, asset_id: str, quality_score: int
    ) -> Optional[Dict[str, Any]]:
        """Update asset quality score"""
        if quality_score < 0 or quality_score > 100:
            raise ValueError("Quality score must be between 0 and 100")

        result = (
            self.client.table("muse_assets")
            .update({"quality_score": quality_score})
            .eq("id", asset_id)
            .execute()
        )

        if result.data:
            return result.data[0]
        return None

    async def get_assets_for_move(self, move_id: str) -> List[Dict[str, Any]]:
        """Get all assets for a move"""
        result = (
            self.client.table("muse_assets")
            .select("*")
            .eq("move_id", move_id)
            .order("created_at", desc=True)
            .execute()
        )
        return result.data or []

    async def get_asset_with_metadata(self, asset_id: str) -> Optional[Dict[str, Any]]:
        """Get asset with full metadata and related info"""
        asset_result = (
            self.client.table("muse_assets")
            .select("*")
            .eq("id", asset_id)
            .single()
            .execute()
        )

        if not asset_result.data:
            return None

        asset = asset_result.data

        # Get move info if linked
        if asset.get("move_id"):
            move_result = (
                self.client.table("moves")
                .select("name, status")
                .eq("id", asset["move_id"])
                .single()
                .execute()
            )
            asset["move_info"] = move_result.data

        # Get ICP info if targeted
        if asset.get("target_icp_id"):
            icp_result = (
                self.client.table("icp_profiles")
                .select("name, tagline")
                .eq("id", asset["target_icp_id"])
                .single()
                .execute()
            )
            asset["icp_info"] = icp_result.data

        return asset

    async def export_asset(
        self, asset_id: str, format: str = "json"
    ) -> Optional[Dict[str, Any]]:
        """Export asset in specified format"""
        asset = await self.get(asset_id)
        if not asset:
            return None

        if format == "json":
            return {
                "id": asset["id"],
                "title": asset["title"],
                "content": asset["content"],
                "content_html": asset.get("content_html"),
                "asset_type": asset["asset_type"],
                "metadata": asset.get("metadata", {}),
                "quality_score": asset.get("quality_score"),
                "created_at": asset["created_at"],
                "updated_at": asset["updated_at"],
            }
        elif format == "text":
            return {
                "title": asset["title"],
                "content": asset["content"],
                "type": asset["asset_type"],
                "created": asset["created_at"],
            }
        elif format == "html":
            return {
                "title": asset["title"],
                "content": asset.get("content_html") or asset["content"],
                "type": asset["asset_type"],
                "created": asset["created_at"],
            }
        else:
            raise ValueError(f"Unsupported export format: {format}")

    async def get_asset_analytics(
        self,
        workspace_id: str,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Get asset analytics for a workspace"""
        query = (
            self.client.table("muse_assets")
            .select("*")
            .eq("workspace_id", workspace_id)
        )

        if date_from:
            query = query.gte("created_at", date_from.isoformat())
        if date_to:
            query = query.lte("created_at", date_to.isoformat())

        result = query.execute()
        assets = result.data or []

        # Calculate analytics
        total_assets = len(assets)
        assets_by_type = {}
        quality_scores = []
        assets_with_quality = 0

        for asset in assets:
            asset_type = asset.get("asset_type", "unknown")
            assets_by_type[asset_type] = assets_by_type.get(asset_type, 0) + 1

            if asset.get("quality_score") is not None:
                quality_scores.append(asset["quality_score"])
                assets_with_quality += 1

        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0

        # Daily creation trends
        daily_counts = {}
        for asset in assets:
            date = asset["created_at"][:10]  # Extract date part
            daily_counts[date] = daily_counts.get(date, 0) + 1

        return {
            "total_assets": total_assets,
            "assets_by_type": assets_by_type,
            "average_quality_score": avg_quality,
            "assets_with_quality_score": assets_with_quality,
            "quality_score_coverage": (
                (assets_with_quality / total_assets * 100) if total_assets > 0 else 0
            ),
            "daily_creation_trends": daily_counts,
            "date_range": {
                "from": date_from.isoformat() if date_from else None,
                "to": date_to.isoformat() if date_to else None,
            },
        }

    async def get_high_quality_assets(
        self, workspace_id: str, min_score: int = 80, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get high quality assets for a workspace"""
        result = (
            self.client.table("muse_assets")
            .select("*")
            .eq("workspace_id", workspace_id)
            .gte("quality_score", min_score)
            .order("quality_score", desc=True)
            .limit(limit)
            .execute()
        )
        return result.data or []

    async def get_recent_assets(
        self, workspace_id: str, days: int = 7, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get recent assets for a workspace"""
        from datetime import timedelta

        date_cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
        result = (
            self.client.table("muse_assets")
            .select("*")
            .eq("workspace_id", workspace_id)
            .gte("created_at", date_cutoff)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return result.data or []

    async def bulk_update_status(self, asset_ids: List[str], status: str) -> int:
        """Update status for multiple assets"""
        valid_statuses = ["draft", "published", "archived"]
        if status not in valid_statuses:
            raise ValueError(
                f"Invalid status: {status}. Must be one of: {valid_statuses}"
            )

        # Update in batches to avoid request size limits
        updated_count = 0
        batch_size = 50

        for i in range(0, len(asset_ids), batch_size):
            batch = asset_ids[i : i + batch_size]
            result = (
                self.client.table("muse_assets")
                .update({"status": status})
                .in_("id", batch)
                .execute()
            )
            updated_count += len(result.data or [])

        return updated_count

    async def get_asset_templates(
        self, workspace_id: str, asset_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get asset templates for a workspace"""
        query = (
            self.client.table("muse_assets")
            .select("*")
            .eq("workspace_id", workspace_id)
            .eq("status", "template")
        )

        if asset_type:
            query = query.eq("asset_type", asset_type)

        result = query.order("title").execute()
        return result.data or []

    async def create_from_template(
        self, template_id: str, new_title: str, workspace_id: str, **kwargs
    ) -> Optional[Dict[str, Any]]:
        """Create new asset from template"""
        template = await self.get(template_id)
        if not template:
            return None

        # Copy template data
        asset_data = {
            "workspace_id": workspace_id,
            "title": new_title,
            "content": template["content"],
            "content_html": template.get("content_html"),
            "asset_type": template["asset_type"],
            "metadata": template.get("metadata", {}),
            "status": "draft",
        }

        # Override with provided kwargs
        asset_data.update(kwargs)

        result = self.client.table("muse_assets").insert(asset_data).execute()

        if result.data:
            return result.data[0]
        return None

    async def get_asset_engagement(self, asset_id: str) -> Dict[str, Any]:
        """Get engagement metrics for an asset"""
        # This would typically integrate with analytics systems
        # For now, return basic metrics from the asset itself
        asset = await self.get(asset_id)
        if not asset:
            return {}

        return {
            "asset_id": asset_id,
            "quality_score": asset.get("quality_score", 0),
            "views": asset.get("metadata", {}).get("views", 0),
            "shares": asset.get("metadata", {}).get("shares", 0),
            "downloads": asset.get("metadata", {}).get("downloads", 0),
            "last_viewed": asset.get("metadata", {}).get("last_viewed"),
            "created_at": asset["created_at"],
            "updated_at": asset["updated_at"],
        }

    async def update_engagement_metrics(
        self, asset_id: str, metrics: Dict[str, Any]
    ) -> bool:
        """Update engagement metrics for an asset"""
        asset = await self.get(asset_id)
        if not asset:
            return False

        # Update metadata with engagement metrics
        metadata = asset.get("metadata", {})
        metadata.update(metrics)

        result = (
            self.client.table("muse_assets")
            .update({"metadata": metadata})
            .eq("id", asset_id)
            .execute()
        )
        return len(result.data or []) > 0
