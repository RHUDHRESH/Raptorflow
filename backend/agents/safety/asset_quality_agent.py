"""
Asset Quality Agent - Checks design quality of generated images and visual assets.
Validates resolution, format, and adherence to design guidelines.
"""

import structlog
from typing import Dict, Any, Optional
from PIL import Image
import io
import httpx

from backend.utils.correlation import get_correlation_id

logger = structlog.get_logger(__name__)


class AssetQualityAgent:
    """
    Validates quality of visual assets (images, videos, designs).
    Checks resolution, file size, format, and basic quality metrics.
    """
    
    def __init__(self):
        self.min_resolution = {
            "social_post": (1080, 1080),
            "banner": (1200, 628),
            "thumbnail": (1280, 720),
            "profile": (400, 400)
        }
        
        self.max_file_size_mb = 10
        self.supported_formats = ["JPEG", "PNG", "WEBP", "GIF"]
    
    async def validate_image(
        self,
        image_url: str,
        asset_type: str = "social_post",
        correlation_id: str = None
    ) -> Dict[str, Any]:
        """
        Validates an image asset.
        
        Args:
            image_url: URL of the image
            asset_type: Type of asset (social_post, banner, etc.)
            
        Returns:
            Validation result
        """
        correlation_id = correlation_id or get_correlation_id()
        logger.info("Validating image asset", image_url=image_url, asset_type=asset_type, correlation_id=correlation_id)
        
        issues = []
        
        try:
            # Download image
            async with httpx.AsyncClient() as client:
                response = await client.get(image_url, timeout=30.0)
                response.raise_for_status()
                image_data = response.content
            
            # Load with PIL
            image = Image.open(io.BytesIO(image_data))
            
            # Check format
            if image.format not in self.supported_formats:
                issues.append({
                    "type": "unsupported_format",
                    "severity": "high",
                    "description": f"Format '{image.format}' is not supported",
                    "suggestion": f"Convert to {', '.join(self.supported_formats)}"
                })
            
            # Check resolution
            min_width, min_height = self.min_resolution.get(asset_type, (1080, 1080))
            width, height = image.size
            
            if width < min_width or height < min_height:
                issues.append({
                    "type": "low_resolution",
                    "severity": "high",
                    "description": f"Resolution {width}x{height} is below minimum {min_width}x{min_height} for {asset_type}",
                    "suggestion": f"Increase resolution to at least {min_width}x{min_height}"
                })
            
            # Check file size
            file_size_mb = len(image_data) / (1024 * 1024)
            if file_size_mb > self.max_file_size_mb:
                issues.append({
                    "type": "large_file_size",
                    "severity": "medium",
                    "description": f"File size {file_size_mb:.2f}MB exceeds {self.max_file_size_mb}MB",
                    "suggestion": "Compress image or reduce dimensions"
                })
            
            # Check aspect ratio for social posts
            if asset_type == "social_post":
                aspect_ratio = width / height
                if not (0.8 <= aspect_ratio <= 1.9):
                    issues.append({
                        "type": "unusual_aspect_ratio",
                        "severity": "low",
                        "description": f"Aspect ratio {aspect_ratio:.2f} may not display well on all platforms",
                        "suggestion": "Consider 1:1 or 16:9 ratios for better compatibility"
                    })
            
            # Basic quality heuristics
            if image.mode != "RGB" and image.mode != "RGBA":
                issues.append({
                    "type": "color_mode",
                    "severity": "low",
                    "description": f"Color mode '{image.mode}' may cause display issues",
                    "suggestion": "Convert to RGB or RGBA"
                })
            
            is_valid = len([i for i in issues if i["severity"] == "high"]) == 0
            
            return {
                "is_valid": is_valid,
                "issues": issues,
                "metadata": {
                    "format": image.format,
                    "resolution": f"{width}x{height}",
                    "file_size_mb": round(file_size_mb, 2),
                    "color_mode": image.mode
                },
                "recommendation": "approve" if is_valid else "reject" if len(issues) > 2 else "review"
            }
            
        except Exception as e:
            logger.error(f"Failed to validate image: {e}", correlation_id=correlation_id)
            return {
                "is_valid": False,
                "issues": [{
                    "type": "validation_error",
                    "severity": "critical",
                    "description": f"Could not validate image: {str(e)}"
                }],
                "metadata": {},
                "recommendation": "reject"
            }


asset_quality_agent = AssetQualityAgent()

