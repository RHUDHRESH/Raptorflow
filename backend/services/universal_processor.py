"""
Universal Intelligence Processor
Accepts any input (files, URLs, text), orchestrates extraction across 7 pillars.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from uuid import UUID
import json

from backend.services.vertex_ai_client import vertex_ai_client
from backend.services.web_scraper import WebScraper

from backend.agents.intelligence import (
    AudiencePillar, ValuePillar, DifferentiationPillar,
    CompetitorPillar, DiscoveryPillar, RemarkabilityPillar, ProofPillar
)

logger = logging.getLogger(__name__)

class UniversalIntelligenceProcessor:
    """
    The Brain that coordinates intelligence extraction.
    """
    
    def __init__(self):
        self.ai_client = vertex_ai_client
        self.web_scraper = WebScraper()
        
        # Initialize Pillars
        self.pillars = {
            1: AudiencePillar(),
            2: ValuePillar(),
            3: DifferentiationPillar(),
            4: CompetitorPillar(),
            5: DiscoveryPillar(),
            6: RemarkabilityPillar(),
            7: ProofPillar()
        }
    
    async def process_upload(self, upload_data: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """
        Process a single upload (file or URL) and extract raw intelligence.
        """
        upload_type = upload_data.get("type", "unknown")
        content = upload_data.get("content")
        
        logger.info(f"Processing upload type: {upload_type} for session: {session_id}")
        
        extracted_data = {}
        
        if upload_type == "url":
            extracted_data = await self._process_url(content)
        elif upload_type in ["pdf", "document", "text"]:
            extracted_data = await self._process_text(content)
        elif upload_type == "image":
            extracted_data = await self._process_image(content)
        else:
            logger.warning(f"Unknown upload type: {upload_type}")
        
        # After extraction, we should route this data to relevant pillars
        # For now, we just return the raw extraction
        return extracted_data

    async def _process_url(self, url: str) -> Dict[str, Any]:
        """Scrape and analyze a URL"""
        try:
            # 1. Scrape content
            scraped_content = await self.web_scraper.scrape_url(url)
            
            # 2. AI Analysis of the page
            prompt = f"""
            Analyze this website content for marketing intelligence:
            URL: {url}
            Content: {scraped_content[:5000]}... (truncated)
            
            Extract:
            - What do they sell?
            - Who is the target audience?
            - Value proposition?
            - Competitors mentioned?
            - Pricing?
            - Testimonials/Proof?
            """
            
            analysis = await self.ai_client.generate_json(prompt, model_type="reasoning")
            return {"source": url, "type": "website", "data": analysis}
            
        except Exception as e:
            logger.error(f"URL processing failed for {url}: {e}")
            return {"error": str(e)}

    async def _process_text(self, text: str) -> Dict[str, Any]:
        """Analyze raw text or document content"""
        try:
            prompt = f"""
            Extract business intelligence from this text:
            {text[:5000]}...
            
            Identify:
            - Company/Product
            - Target Audience
            - Key Benefits
            - Competition
            - Pricing
            """
            analysis = await self.ai_client.generate_json(prompt, model_type="reasoning")
            return {"source": "text_upload", "type": "document", "data": analysis}
        except Exception as e:
            logger.error(f"Text processing failed: {e}")
            return {"error": str(e)}

    async def _process_image(self, image_data: str) -> Dict[str, Any]:
        """Analyze image (OCR + Visual Understanding)"""
        # Placeholder for image processing
        # In a real implementation, we'd use the vertex_ai_client.ocr_image or gemini vision
        return {"message": "Image processing not yet fully implemented"}

    async def synthesize_intelligence(self, all_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Combine data from multiple uploads into a cohesive intelligence report.
        """
        prompt = f"""
        Synthesize this marketing intelligence data from multiple sources:
        {json.dumps(all_data, default=str)}
        
        Organize into 7 Pillars:
        1. Audience (Who?)
        2. Value (Why?)
        3. Differentiation (Unique?)
        4. Competition (Who else?)
        5. Discovery (Where?)
        6. Remarkability (Wow factor?)
        7. Proof (Evidence?)
        
        Return structured JSON.
        """
        
        return await self.ai_client.generate_json(prompt, model_type="reasoning")

# Singleton instance
universal_processor = UniversalIntelligenceProcessor()
