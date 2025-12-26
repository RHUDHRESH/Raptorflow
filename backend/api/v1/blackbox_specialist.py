from typing import Any, Dict
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from core.auth import get_current_user, get_tenant_id
from core.vault import Vault
from services.blackbox_service import BlackboxService

router = APIRouter(prefix="/v1/blackbox/specialist", tags=["blackbox"])


def get_blackbox_service():
    """Dependency provider for BlackboxService."""
    vault = Vault()
    return BlackboxService(vault)


@router.post("/run/{agent_id}/{move_id}")
async def run_specialist_agent(
    agent_id: str,
    move_id: UUID,
    state_override: Dict[str, Any] = None,
    _current_user: dict = Depends(get_current_user),
    service: BlackboxService = Depends(get_blackbox_service),
    tenant_id: UUID = Depends(get_tenant_id),
):
    """
    SOTA Endpoint: Directly triggers a specific specialist agent.
    Useful for 'Verify' or 'Run Analysis' buttons in the UI.
    """
    # Map agent_id to specialist class
    from agents.blackbox_specialist import (
        BlackboxCritiqueAgent,
        CompetitorIntelligenceAgent,
        LearningAgent,
        ROIAnalystAgent,
        StrategicDriftAgent,
    )

    agents = {
        "roi_analyst": ROIAnalystAgent,
        "strategic_drift": StrategicDriftAgent,
        "competitor_intelligence": CompetitorIntelligenceAgent,
        "blackbox_critique": BlackboxCritiqueAgent,
        "learning_agent": LearningAgent,
    }

    if agent_id not in agents:
        raise HTTPException(
            status_code=404, detail=f"Specialist agent '{agent_id}' not found."
        )

    # Initialize agent
    agent_cls = agents[agent_id]
    agent = agent_cls()

    # Gather context (standard state)
    traces = service.get_telemetry_by_move(str(move_id), tenant_id)
    outcomes = service.get_outcomes_by_move(move_id, tenant_id)

    initial_state = {
        "move_id": str(move_id),
        "telemetry_data": traces,
        "outcomes": outcomes,
        "findings": [str(t.get("trace", "")) for t in traces],
        "status": [],
    }

    if state_override:
        initial_state.update(state_override)

    # Run agent
    result = await agent.run(initial_state)

    # Task 94: If findings were generated, persist them as learnings
    if "findings" in result and result["findings"]:
        for finding in result["findings"]:
            l_type = service.categorize_learning(finding)
            service.upsert_learning_embedding(
                content=finding, learning_type=l_type, source_ids=[move_id]
            )

    return {
        "agent_id": agent_id,
        "move_id": move_id,
        "result": result,
        "status": "success",
    }
