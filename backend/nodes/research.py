#!/usr/bin/env python3
"""
Research Node - Market research and competitor analysis
"""

import logging
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from synapse import brain
from schemas import NodeInput, NodeOutput

logger = logging.getLogger("research")

@brain.register("research_node")
async def research_node(context: dict) -> dict:
    """Perform market research"""
    try:
        task = context.get("task", "Research task")
        logger.info(f"🔍 Research Node: {task}")
        
        # Simple research simulation
        if "competitor" in task.lower():
            research_data = {
                "competitors": ["Competitor A", "Competitor B"],
                "market_share": "A: 35%, B: 25%",
                "analysis": "Both target similar demographics"
            }
        elif "market" in task.lower():
            research_data = {
                "market_size": "$50M",
                "growth_rate": "15%",
                "key_segments": ["Enterprise", "SMB", "Startup"]
            }
        else:
            research_data = {
                "summary": f"Research completed for {task}",
                "sources": 5,
                "confidence": 0.8
            }
        
        return {
            "status": "success",
            "data": research_data,
            "next_step": "strategy"
        }
        
    except Exception as e:
        logger.error(f"Research Node Error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }
