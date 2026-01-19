#!/usr/bin/env python3
"""
Campaign Node - Campaign orchestration logic
"""

import logging
import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from synapse import brain
from schemas import NodeInput, NodeOutput

logger = logging.getLogger("campaign")

@brain.register("campaign_orchestrator")
async def campaign_node(context: dict) -> dict:
    """Manage multi-step campaigns with timelines"""
    start_time = datetime.now()
    
    try:
        campaign_name = context.get("campaign_name", "Campaign")
        logger.info(f"🎯 Campaign Node: {campaign_name}")
        
        # Campaign orchestration logic
        campaign_data = {
            "campaign_id": context.get("campaign_id"),
            "name": campaign_name,
            "status": "running",
            "progress": 0,
            "total_steps": len(context.get("move_sequence", "").split(",")),
            "current_step": 1,
            "started_at": datetime.now().isoformat(),
            "timeline": {
                "phase": "execution",
                "estimated_completion": "2-3 hours",
                "milestones": ["Research", "Strategy", "Content", "Analysis"]
            }
        }
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return {
            "status": "success",
            "data": campaign_data,
            "next_step": "execute_moves",
            "execution_time": execution_time
        }
        
    except Exception as e:
        logger.error(f"Campaign Node Error: {e}")
        return {
            "status": "error",
            "error": str(e),
            "execution_time": (datetime.now() - start_time).total_seconds()
        }
