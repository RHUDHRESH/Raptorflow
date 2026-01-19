#!/usr/bin/env python3
"""
SEO Node - Analyzes content for search optimization
"""

import logging
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from synapse import brain
from schemas import NodeInput, NodeOutput

logger = logging.getLogger("seo")

@brain.register("seo_skill")
async def seo_node(context: dict) -> dict:
    """Analyze content SEO"""
    start_time = datetime.now()
    
    try:
        logger.info(f"🔍 SEO Node: Analyzing content")
        
        content = context.get("content", "")
        if not content:
            return {
                "status": "error",
                "error": "No content provided for SEO analysis"
            }
        
        # Simple SEO analysis
        word_count = len(content.split())
        has_headings = "##" in content or "###" in content
        has_links = "http" in content.lower()
        
        # Calculate basic SEO score
        seo_score = 0.5  # Base score
        if word_count > 100:
            seo_score += 0.2
        if has_headings:
            seo_score += 0.2
        if has_links:
            seo_score += 0.1
        
        suggestions = []
        if word_count < 100:
            suggestions.append("Consider adding more content (aim for 300+ words)")
        if not has_headings:
            suggestions.append("Add headings (## or ###) for better SEO")
        if not has_links:
            suggestions.append("Include relevant links to improve authority")
        
        return {
            "status": "success",
            "data": {
                "seo_score": min(1.0, seo_score),
                "word_count": word_count,
                "has_headings": has_headings,
                "has_links": has_links,
                "suggestions": suggestions
            }
        }
        
    except Exception as e:
        logger.error(f"SEO Node Error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }
