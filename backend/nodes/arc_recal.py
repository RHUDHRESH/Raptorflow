#!/usr/bin/env python3
"""
Arc Recalculator Node - Fluid scheduling logic
Handles the 'push back' and 'Breathing Arc' logic.
"""

import logging
from datetime import datetime, timedelta, UTC
from typing import Dict, Any

from backend.synapse import brain
from backend.core.supabase_mgr import get_supabase_client

logger = logging.getLogger("arc_recal")

@brain.register("arc_recal_node")
async def arc_recal_node(context: Dict) -> Dict:
    """
    Recalculates subsequent task dates when a prerequisite is missed or finished late.
    """
    workspace_id = context.get("workspace_id")
    move_id = context.get("move_id")
    trigger_task_id = context.get("trigger_task_id")
    
    if not workspace_id or not move_id:
        return {"status": "error", "error": "Missing required context for recalculation"}
        
    client = get_supabase_client()
    
    try:
        logger.info(f"🌀 Recalculating arc for move {move_id}")
        
        # 1. Fetch all pending tasks for this move, ordered by scheduled_for
        result = client.table("scheduled_tasks") \
            .select("id, scheduled_for, priority") \
            .eq("move_id", move_id) \
            .eq("status", "pending") \
            .order("scheduled_for", asc=True) \
            .execute()
            
        pending_tasks = result.data or []
        
        if not pending_tasks:
            return {"status": "success", "data": {"message": "No pending tasks to recalculate"}}
            
        # 2. Push everything back by 24 hours (Fluid logic)
        # This is a simple implementation; a better one would preserve relative offsets.
        now = datetime.now(UTC)
        
        for i, task in enumerate(pending_tasks):
            # Calculate new date: Today + (i + 1) days
            new_date = now + timedelta(days=i + 1)
            
            client.table("scheduled_tasks").update({
                "scheduled_for": new_date.isoformat(),
                "status": "pushed_back"
            }).eq("id", task["id"]).execute()
            
        # 3. Log thought
        await brain.log_thought(
            entity_id=move_id,
            entity_type="move",
            agent_name="ArcRecalculator",
            thought=f"Recalculated {len(pending_tasks)} tasks due to delay in task {trigger_task_id}.",
            workspace_id=workspace_id
        )
        
        return {
            "status": "success",
            "data": {
                "tasks_updated": len(pending_tasks),
                "next_execution_date": (now + timedelta(days=1)).isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"🔥 Arc Recalculation failed: {e}")
        return {"status": "error", "error": str(e)}
