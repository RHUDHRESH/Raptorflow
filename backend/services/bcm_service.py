"""
BCM Evolution Service
Orchestrates the full lifecycle of the 'Everything' BCM engine.
"""
import json
import logging
from typing import Dict, Any, Optional
from backend.services.bcm_projector import BCMProjector
from backend.services.bcm_recorder import BCMEventRecorder
from backend.agents.universal.agent import UniversalAgent
from backend.schemas.bcm_evolution import EventType

logger = logging.getLogger(__name__)

class BCMService:
    """Service for managing BCM evolution and AI-driven refinement"""
    
    def __init__(self, db_client=None):
        self.db = db_client
        self.projector = BCMProjector(db_client=db_client)
        self.recorder = BCMEventRecorder(db_client=db_client)
        self.agent = UniversalAgent()

    async def refine_context(self, workspace_id: str, ucid: str) -> Dict[str, Any]:
        """
        Runs the AI refinement loop to evolve the business context.
        """
        try:
            # 1. Project latest state
            current_state = await self.projector.get_latest_state(workspace_id, ucid)
            
            # 2. Fetch raw events for AI analysis (last 50)
            events_result = await self.recorder.db.table("bcm_events") \
                .select("*") \
                .eq("workspace_id", workspace_id) \
                .order("created_at", desc=True) \
                .limit(50) \
                .execute()
            
            # 3. Invoke Universal Agent with bcm_refinement skill
            agent_input = {
                "current_bcm": current_state.model_dump_json(),
                "recent_events": json.dumps(events_result.data)
            }
            
            response = await self.agent.run_step("bcm_refinement", agent_input)
            
            if not response.get("success"):
                raise Exception(f"AI Refinement failed: {response.get('error')}")
                
            refinement_data = json.loads(response["output"])
            
            # 4. Record the refinement as a new event
            await self.recorder.record_event(
                workspace_id=workspace_id,
                event_type=EventType.AI_REFINEMENT,
                payload=refinement_data,
                ucid=ucid
            )
            
            return refinement_data
            
        except Exception as e:
            logger.error(f"Error in BCM refinement loop: {e}")
            raise

    async def analyze_evolution(self, workspace_id: str, ucid: str) -> Dict[str, Any]:
        """
        Recalculates the evolution index and syncs it to the primary workspaces table.
        """
        try:
            # 1. Project the latest state (triggers dynamic calculation)
            state = await self.projector.get_latest_state(workspace_id, ucid)
            
            # 2. Persist to workspaces table for fast high-level lookup
            await self.db.table("workspaces").update({
                "evolution_index": state.history.evolution_index,
                "current_bcm_ucid": ucid
            }).eq("id", workspace_id).execute()
            
            return {
                "workspace_id": workspace_id,
                "ucid": ucid,
                "evolution_index": state.history.evolution_index,
                "total_events": state.history.total_events
            }
        except Exception as e:
            logger.error(f"Failed to analyze BCM evolution for {workspace_id}: {e}")
            raise