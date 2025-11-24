"""
Canva Service - Integration with Canva API for design generation.
Populates templates and creates branded visual assets.
"""

import structlog
from typing import Dict, Any, Optional, List
from uuid import UUID
import httpx

from backend.config.settings import get_settings
from backend.services.supabase_client import supabase_client

logger = structlog.get_logger(__name__)
settings = get_settings()


class CanvaService:
    """
    Canva API integration for automated design creation.
    Supports template population and asset generation.
    """
    
    def __init__(self):
        self.base_url = "https://api.canva.com/v1"
        self.api_key = settings.CANVA_API_KEY
    
    async def get_access_token(self, workspace_id: UUID) -> Optional[str]:
        """Retrieves stored Canva access token."""
        try:
            integration = await supabase_client.fetch_one(
                "integrations",
                {"workspace_id": str(workspace_id), "platform": "canva"}
            )
            return integration.get("access_token") if integration else None
        except Exception as e:
            logger.error(f"Failed to get Canva token: {e}")
            return None
    
    async def create_design_from_template(
        self,
        template_id: str,
        data: Dict[str, Any],
        workspace_id: UUID,
        output_format: str = "png"
    ) -> Dict[str, Any]:
        """
        Creates a design from a Canva template.
        
        Args:
            template_id: Canva template ID
            data: Data to populate template (e.g., {"headline": "...", "body": "..."})
            workspace_id: User's workspace
            output_format: png, jpg, pdf
            
        Returns:
            Dict with design ID and export URL
        """
        access_token = await self.get_access_token(workspace_id)
        if not access_token:
            raise ValueError("Canva not connected for this workspace")
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # Canva Autofill API
        payload = {
            "design_id": template_id,
            "data": data
        }
        
        try:
            async with httpx.AsyncClient() as client:
                # Step 1: Autofill template
                response = await client.post(
                    f"{self.base_url}/autofills",
                    headers=headers,
                    json=payload,
                    timeout=60.0
                )
                response.raise_for_status()
                
                autofill_job = response.json()
                design_id = autofill_job["design"]["id"]
                
                # Step 2: Export design
                export_response = await client.post(
                    f"{self.base_url}/designs/{design_id}/export",
                    headers=headers,
                    json={"file_type": output_format},
                    timeout=60.0
                )
                export_response.raise_for_status()
                
                export_job = export_response.json()
                export_url = export_job["url"]
                
                return {
                    "design_id": design_id,
                    "export_url": export_url,
                    "format": output_format,
                    "status": "completed"
                }
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Canva API error: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Failed to create Canva design: {e}")
            raise
    
    async def create_social_post(
        self,
        headline: str,
        body: str,
        brand_colors: Optional[List[str]] = None,
        logo_url: Optional[str] = None,
        workspace_id: UUID = None,
        template_type: str = "instagram_post"
    ) -> str:
        """
        Creates a branded social post using a template.
        
        Returns:
            URL of the generated image
        """
        # Default template IDs (would be configurable per workspace)
        template_ids = {
            "instagram_post": "DAFaUynxPsM",  # Example template ID
            "linkedin_post": "DAFaUy_xPsN",
            "quote_card": "DAFaUy_xPsO"
        }
        
        template_id = template_ids.get(template_type, template_ids["instagram_post"])
        
        data = {
            "headline": headline,
            "body": body
        }
        
        if brand_colors:
            data["brand_color_1"] = brand_colors[0]
            if len(brand_colors) > 1:
                data["brand_color_2"] = brand_colors[1]
        
        if logo_url:
            data["logo_image"] = logo_url
        
        result = await self.create_design_from_template(
            template_id,
            data,
            workspace_id
        )
        
        return result["export_url"]


canva_service = CanvaService()




