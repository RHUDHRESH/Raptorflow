"""
Expert Council API Endpoints
"""

import logging
from typing import Any, Dict, List, Optional

from db.council import CouncilRepository
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ..core.auth import get_current_user, get_workspace_id
from ..core.models import User
from ..services.expert_council import create_swarm_session, get_expert_council_swarm
from ..services.foundation import FoundationService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/council", tags=["council"])


class CouncilRequest(BaseModel):
    """Request for council swarm execution."""

    mission: str
    context_override: Optional[Dict[str, Any]] = None


class CouncilResponse(BaseModel):
    """Response for council swarm execution."""

    session_id: str
    mission: str
    contributions: List[Dict[str, Any]]
    final_output: Optional[str]
    consensus_reached: bool
    swarm_status: str
    skills_loaded: List[str]


@router.post("/execute", response_model=CouncilResponse)
async def execute_council(
    request: CouncilRequest,
    user: User = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id),
):
    """
    Triggers an Expert Council Swarm session and persists it.
    """
    try:
        swarm = get_expert_council_swarm()
        foundation_service = FoundationService()
        council_repo = CouncilRepository()

        # 1. Gather context
        foundation = await foundation_service.get_foundation_with_metrics(workspace_id)
        if not foundation:
            raise HTTPException(
                status_code=404, detail="Foundation data required for swarm execution."
            )

        context = {
            "company_name": foundation.get("company_name"),
            "industry": foundation.get("industry"),
            "mission": foundation.get("mission"),
            "ricps": [r.model_dump() for r in foundation.get("ricps", [])],
        }

        if request.context_override:
            context.update(request.context_override)

        # 2. Initialize swarm session
        state = create_swarm_session(request.mission, context)

        # 3. Run the swarm graph
        logger.info(f"Starting Expert Council Swarm for workspace {workspace_id}")
        final_state = await swarm.workflow.ainvoke(state)

        discussion = final_state["discussion"]

        # 4. PERSIST to DB
        db_data = {
            "mission": request.mission,
            "contributions": [c.model_dump() for c in discussion.contributions],
            "skills_loaded": final_state["skills_loaded"],
            "final_report": final_state["final_report"],
            "consensus_reached": discussion.consensus_reached,
            "status": final_state["swarm_status"],
            "accuracy_score": final_state["performance_metrics"].get("accuracy", 0.0),
        }
        await council_repo.create_session(workspace_id, db_data)

        return CouncilResponse(
            session_id=discussion.session_id,
            mission=discussion.mission,
            contributions=db_data["contributions"],
            final_output=db_data["final_report"],
            consensus_reached=db_data["consensus_reached"],
            swarm_status=db_data["status"],
            skills_loaded=db_data["skills_loaded"],
        )

    except Exception as e:
        logger.error(f"Council execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
