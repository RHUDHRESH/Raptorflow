"""
Content service for business logic operations
Handles content-related business logic and validation
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from db.moves import MoveRepository
from db.muse_assets import MuseAssetRepository

from .core.models import ValidationError
from .core.supabase_mgr import get_supabase_client


class ContentService:
    """Service for content business logic"""

    def __init__(self):
        self.repository = MuseAssetRepository()
        self.move_repository = MoveRepository()
        self.supabase = get_supabase_client()

    async def create_asset(
        self, workspace_id: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create new content asset with validation

        Args:
            workspace_id: Workspace ID
            data: Asset data

        Returns:
            Created asset data
        """
        # Validate required fields
        if not data.get("title"):
            raise ValidationError("Asset title is required")

        if not data.get("content"):
            raise ValidationError("Asset content is required")

        # Validate asset type
        valid_types = [
            "email",
            "social_post",
            "blog",
            "ad_copy",
            "headline",
            "script",
            "carousel",
        ]
        if "asset_type" in data and data["asset_type"] not in valid_types:
            raise ValidationError(f"Invalid asset type: {data['asset_type']}")

        # Validate move if provided
        if "move_id" in data and data["move_id"]:
            move = await self.move_repository.get_by_id(data["move_id"], workspace_id)
            if not move:
                raise ValidationError("Move not found")

        # Validate target ICP if provided
        if "target_icp_id" in data and data["target_icp_id"]:
            icp = (
                await self.supabase.table("icp_profiles")
                .select("*")
                .eq("id", data["target_icp_id"])
                .eq("workspace_id", workspace_id)
                .single()
                .execute()
            )
            if not icp.data:
                raise ValidationError("Target ICP not found")

        return await self.repository.create(workspace_id, data)

    async def update_quality_score(
        self, asset_id: str, workspace_id: str, score: int
    ) -> Optional[Dict[str, Any]]:
        """
        Update quality score for asset

        Args:
            asset_id: Asset ID
            workspace_id: Workspace ID
            score: Quality score (0-100)

        Returns:
            Updated asset data or None if not found
        """
        if not isinstance(score, int) or score < 0 or score > 100:
            raise ValidationError("Quality score must be an integer between 0 and 100")

        asset = await self.repository.get_by_id(asset_id, workspace_id)
        if not asset:
            raise ValidationError("Asset not found")

        return await self.repository.update(
            asset_id, workspace_id, {"quality_score": score}
        )

    async def list_assets_for_move(
        self, workspace_id: str, move_id: str, filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        List assets for a specific move

        Args:
            workspace_id: Workspace ID
            move_id: Move ID
            filters: Optional filters

        Returns:
            List of asset data
        """
        # Verify move belongs to workspace
        move = await self.move_repository.get_by_id(move_id, workspace_id)
        if not move:
            raise ValidationError("Move not found")

        return await self.repository.list_by_move(workspace_id, move_id, filters)

    async def export_asset(
        self, asset_id: str, workspace_id: str, format: str = "json"
    ) -> Dict[str, Any]:
        """
        Export asset in specified format

        Args:
            asset_id: Asset ID
            workspace_id: Workspace ID
            format: Export format (json, html, txt, etc.)

        Returns:
            Exported asset data
        """
        asset = await self.repository.get_by_id(asset_id, workspace_id)
        if not asset:
            raise ValidationError("Asset not found")

        if format == "json":
            return asset
        elif format == "html":
            # Convert to HTML
            html_content = f"""
            <html>
            <head>
                <title>{asset.get('title', 'Untitled')}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; }}
                    .header {{ border-bottom: 2px solid #333; padding-bottom: 10px; }}
                    .content {{ margin-top: 20px; line-height: 1.6; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>{asset.get('title', 'Untitled')}</h1>
                    <p>Type: {asset.get('asset_type', 'Unknown')}</p>
                    <p>Created: {asset.get('created_at', 'Unknown')}</p>
                </div>
                <div class="content">
                    {asset.get('content_html', asset.get('content', ''))}
                </div>
            </body>
            </html>
            """
            return {"format": "html", "content": html_content}
        elif format == "txt":
            # Convert to plain text
            txt_content = f"""
{asset.get('title', 'Untitled')}
{'=' * len(asset.get('title', 'Untitled'))}

Type: {asset.get('asset_type', 'Unknown')}
Created: {asset.get('created_at', 'Unknown')}

{asset.get('content', '')}
            """.strip()
            return {"format": "txt", "content": txt_content}
        else:
            raise ValidationError(f"Unsupported export format: {format}")

    async def search_assets(
        self, workspace_id: str, query: str, filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search assets by content

        Args:
            workspace_id: Workspace ID
            query: Search query
            filters: Optional filters

        Returns:
            List of matching assets
        """
        return await self.repository.search(workspace_id, query, filters)

    async def list_assets_by_type(
        self,
        workspace_id: str,
        asset_type: str,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        List assets by type

        Args:
            workspace_id: Workspace ID
            asset_type: Asset type
            filters: Optional filters

        Returns:
            List of asset data
        """
        # Validate asset type
        valid_types = [
            "email",
            "social_post",
            "blog",
            "ad_copy",
            "headline",
            "script",
            "carousel",
        ]
        if asset_type not in valid_types:
            raise ValidationError(f"Invalid asset type: {asset_type}")

        return await self.repository.list_by_type(workspace_id, asset_type, filters)

    async def update_asset(
        self, asset_id: str, workspace_id: str, data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Update asset with validation

        Args:
            asset_id: Asset ID
            workspace_id: Workspace ID
            data: Update data

        Returns:
            Updated asset data or None if not found
        """
        asset = await self.repository.get_by_id(asset_id, workspace_id)
        if not asset:
            raise ValidationError("Asset not found")

        # Validate asset type if provided
        if "asset_type" in data:
            valid_types = [
                "email",
                "social_post",
                "blog",
                "ad_copy",
                "headline",
                "script",
                "carousel",
            ]
            if data["asset_type"] not in valid_types:
                raise ValidationError(f"Invalid asset type: {data['asset_type']}")

        # Validate status if provided
        if "status" in data:
            valid_statuses = ["draft", "review", "approved", "published", "archived"]
            if data["status"] not in valid_statuses:
                raise ValidationError(f"Invalid status: {data['status']}")

        # Validate quality score if provided
        if "quality_score" in data:
            score = data["quality_score"]
            if not isinstance(score, int) or score < 0 or score > 100:
                raise ValidationError(
                    "Quality score must be an integer between 0 and 100"
                )

        return await self.repository.update(asset_id, workspace_id, data)

    async def delete_asset(self, asset_id: str, workspace_id: str) -> bool:
        """
        Delete asset

        Args:
            asset_id: Asset ID
            workspace_id: Workspace ID

        Returns:
            True if deleted, False otherwise
        """
        asset = await self.repository.get_by_id(asset_id, workspace_id)
        if not asset:
            raise ValidationError("Asset not found")

        return await self.repository.delete(asset_id, workspace_id)

    async def get_asset_analytics(self, workspace_id: str) -> Dict[str, Any]:
        """
        Get analytics for content assets in workspace

        Args:
            workspace_id: Workspace ID

        Returns:
            Analytics data
        """
        assets = await self.repository.list_by_workspace(workspace_id)

        analytics = {
            "total_assets": len(assets),
            "by_type": {},
            "by_status": {},
            "average_quality_score": 0,
            "high_quality_assets": [],
            "assets_by_move": {},
        }

        total_quality = 0
        quality_count = 0

        for asset in assets:
            # Count by type
            asset_type = asset.get("asset_type", "unknown")
            analytics["by_type"][asset_type] = (
                analytics["by_type"].get(asset_type, 0) + 1
            )

            # Count by status
            status = asset.get("status", "draft")
            analytics["by_status"][status] = analytics["by_status"].get(status, 0) + 1

            # Quality score metrics
            quality_score = asset.get("quality_score")
            if quality_score is not None:
                total_quality += quality_score
                quality_count += 1

                if quality_score >= 80:
                    analytics["high_quality_assets"].append(asset)

            # Group by move
            move_id = asset.get("move_id")
            if move_id:
                if move_id not in analytics["assets_by_move"]:
                    analytics["assets_by_move"][move_id] = []
                analytics["assets_by_move"][move_id].append(asset)

        # Calculate average quality score
        if quality_count > 0:
            analytics["average_quality_score"] = round(total_quality / quality_count, 2)

        return analytics

    async def generate_content_variations(
        self, asset_id: str, workspace_id: str, variations: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Generate content variations for an asset

        Args:
            asset_id: Asset ID
            workspace_id: Workspace ID
            variations: Number of variations to generate

        Returns:
            List of generated variations
        """
        asset = await self.repository.get_by_id(asset_id, workspace_id)
        if not asset:
            raise ValidationError("Asset not found")

        # For now, create simple variations
        # In a real implementation, this would use AI to generate variations
        original_content = asset.get("content", "")
        asset_type = asset.get("asset_type", "text")

        generated_variations = []

        for i in range(variations):
            variation = {
                "workspace_id": workspace_id,
                "title": f"{asset.get('title', 'Untitled')} - Variation {i+1}",
                "content": f"Variation {i+1} of: {original_content}",
                "content_html": f"<p>Variation {i+1} of: {original_content}</p>",
                "asset_type": asset_type,
                "status": "draft",
                "quality_score": 70,  # Default score
                "metadata": {
                    "original_asset_id": asset_id,
                    "variation_number": i + 1,
                    "generated_at": datetime.utcnow().isoformat(),
                },
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            }

            created_variation = await self.repository.create(workspace_id, variation)
            if created_variation:
                generated_variations.append(created_variation)

        return generated_variations

    async def validate_asset_data(self, data: Dict[str, Any]) -> bool:
        """
        Validate asset data before saving

        Args:
            data: Asset data to validate

        Returns:
            True if valid, raises ValidationError if invalid
        """
        # Required fields
        required_fields = ["title", "content"]
        for field in required_fields:
            if not data.get(field):
                raise ValidationError(f"Required field missing: {field}")

        # Validate title length
        if len(data["title"]) > 200:
            raise ValidationError("Title too long (max 200 characters)")

        # Validate content length
        if len(data["content"]) > 50000:
            raise ValidationError("Content too long (max 50000 characters)")

        # Validate asset type
        if "asset_type" in data:
            valid_types = [
                "email",
                "social_post",
                "blog",
                "ad_copy",
                "headline",
                "script",
                "carousel",
            ]
            if data["asset_type"] not in valid_types:
                raise ValidationError(f"Invalid asset type: {data['asset_type']}")

        # Validate status
        if "status" in data:
            valid_statuses = ["draft", "review", "approved", "published", "archived"]
            if data["status"] not in valid_statuses:
                raise ValidationError(f"Invalid status: {data['status']}")

        # Validate quality score
        if "quality_score" in data:
            score = data["quality_score"]
            if not isinstance(score, int) or score < 0 or score > 100:
                raise ValidationError(
                    "Quality score must be an integer between 0 and 100"
                )

        # Validate JSON fields
        json_fields = ["metadata"]
        for field in json_fields:
            if field in data and not isinstance(data[field], dict):
                raise ValidationError(f"{field} must be a dictionary")

        return True
