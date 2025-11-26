"""
Canva Agent - Execution agent for Canva design generation.
Orchestrates design creation and asset management.
"""

import structlog
from typing import Dict, Any, Optional, List
from uuid import UUID

from backend.services.canva_service import canva_service
from backend.agents.safety.asset_quality_agent import asset_quality_agent
from backend.services.supabase_client import supabase_client
from backend.utils.correlation import get_correlation_id

logger = structlog.get_logger(__name__)


class CanvaAgent:
    """
    Agent for creating designs with Canva.
    Validates quality and stores assets.
    """
    
    def __init__(self):
        self.canva = canva_service
        self.quality_checker = asset_quality_agent
    
    async def create_branded_asset(
        self,
        asset_type: str,
        headline: str,
        body: Optional[str] = None,
        workspace_id: UUID = None,
        brand_settings: Optional[Dict] = None,
        correlation_id: str = None
    ) -> Dict[str, Any]:
        """
        Creates a branded visual asset using Canva.
        
        Args:
            asset_type: social_post, quote_card, infographic, etc.
            headline: Main text
            body: Supporting text
            workspace_id: User's workspace
            brand_settings: Brand colors, logo, fonts
            
        Returns:
            Asset metadata with URL
        """
        correlation_id = correlation_id or get_correlation_id()
        logger.info("Creating Canva asset", asset_type=asset_type, correlation_id=correlation_id)
        
        # Create design
        image_url = await self.canva.create_social_post(
            headline=headline,
            body=body or "",
            brand_colors=brand_settings.get("colors") if brand_settings else None,
            logo_url=brand_settings.get("logo_url") if brand_settings else None,
            workspace_id=workspace_id,
            template_type=asset_type
        )
        
        # Validate quality
        quality_report = await self.quality_checker.validate_image(
            image_url,
            asset_type=asset_type,
            correlation_id=correlation_id
        )
        
        if not quality_report["is_valid"]:
            logger.warning("Generated asset failed quality check", issues=quality_report["issues"], correlation_id=correlation_id)
            # Could retry with different template or adjust settings
        
        # Store asset metadata
        asset_record = await supabase_client.insert("assets", {
            "workspace_id": str(workspace_id),
            "type": asset_type,
            "url": image_url,
            "source_tool": "canva",
            "metadata": {
                "headline": headline,
                "body": body,
                "quality_report": quality_report
            }
        })
        
        return {
            "asset_id": asset_record["id"],
            "url": image_url,
            "quality_report": quality_report,
            "status": "created"
        }


canva_agent = CanvaAgent()





