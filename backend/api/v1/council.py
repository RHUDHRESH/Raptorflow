import hashlib
import json
import logging
import re
from typing import Dict, List, Optional
from uuid import uuid4

import psycopg
from fastapi import APIRouter, Depends, HTTPException

from core.auth import get_current_user
from db import save_campaign, save_move, save_reasoning_chain
from models.api_models import (
    CouncilCampaignCreateRequest,
    CouncilCampaignPlanRequest,
    CouncilCampaignPlanResponse,
    CouncilMoveCreateRequest,
    CouncilMovePlanResponse,
    CouncilPlanRequest,
)
from services.council_service import CouncilService, get_council_service

logger = logging.getLogger("raptorflow.api.council")
router = APIRouter(tags=["council"])


def _slugify_campaign_title(title: str) -> str:
    candidate = re.sub(r"[^a-z0-9]+", "-", (title or "").lower()).strip("-")
    candidate = candidate or "campaign"
    return f"{candidate}-{uuid4().hex[:6]}"


def _extract_node_name(message: str) -> Optional[str]:
    if not message:
        return None
    if message.endswith(" timed out"):
        return message[: -len(" timed out")].strip() or None
    if " failed:" in message:
        return message.split(" failed:", 1)[0].strip() or None
    if message.endswith(" failed"):
        return message[: -len(" failed")].strip() or None
    return None


def _build_council_error(context: str, exc: Exception) -> Dict[str, str]:
    message = str(exc) or repr(exc)
    detail: Dict[str, str] = {
        "error": f"Council {context} failed.",
        "diagnostics": message,
        "error_type": type(exc).__name__,
    }
    node = _extract_node_name(message)
    if node:
        detail["node"] = node
    return detail


@router.post("/council/generate_move_plan", response_model=CouncilMovePlanResponse)
async def generate_move_plan(
    payload: CouncilPlanRequest,
    _current_user: dict = Depends(get_current_user),
    service: CouncilService = Depends(get_council_service),
):
    """Run the Council to generate a tactical move plan."""
    try:
        plan = await service.generate_move_plan(
            payload.workspace_id, payload.objective, payload.details
        )
        return plan
    except Exception as exc:
        logger.error("Failed to generate move plan", exc_info=exc)
        raise HTTPException(
            status_code=500,
            detail=_build_council_error("move plan generation", exc),
        )


@router.post(
    "/council/generate_campaign_plan", response_model=CouncilCampaignPlanResponse
)
async def generate_campaign_plan(
    payload: CouncilCampaignPlanRequest,
    _current_user: dict = Depends(get_current_user),
    service: CouncilService = Depends(get_council_service),
):
    """Generate a 90-day campaign arc and tactical moves via the Council."""
    try:
        plan = await service.generate_campaign_plan(
            payload.workspace_id,
            payload.objective,
            payload.details,
            payload.target_icp,
        )
        return plan
    except Exception as exc:
        logger.error("Failed to generate campaign plan", exc_info=exc)
        raise HTTPException(
            status_code=500,
            detail=_build_council_error("campaign planning", exc),
        )


@router.post("/moves/create")
async def persist_council_moves(
    payload: CouncilMoveCreateRequest,
    _current_user: dict = Depends(get_current_user),
):
    """Persist Council generated moves into Supabase."""
    try:
        chain_payload: Dict[str, object] = {
            "id": payload.rationale.reasoning_chain_id,
            "final_synthesis": payload.rationale.final_decree,
            "metrics": payload.rationale.consensus_metrics,
            "debate_history": [],
            "metadata": {"source": "council.moves"},
        }
        chain_id = await save_reasoning_chain(payload.workspace_id, chain_payload)
    except Exception as exc:
        logger.error("Failed to save reasoning chain", exc_info=exc)
        raise HTTPException(
            status_code=500,
            detail="Unable to persist the reasoning chain. Please retry.",
        )

    consensus_sha = hashlib.sha256(
        json.dumps(payload.rationale.consensus_metrics, sort_keys=True).encode("utf-8")
    ).hexdigest()

    move_ids: List[str] = []
    for move in payload.moves:
        refinement = dict(move.refinement_data or {})
        if move.muse_prompt:
            refinement.setdefault("muse_prompt", move.muse_prompt)
        refinement.setdefault("council_consensus_sha", consensus_sha)

        move_record = {
            "title": move.title,
            "description": move.description,
            "status": "pending",
            "priority": move.priority or 3,
            "move_type": move.move_type,
            "tool_requirements": move.tool_requirements or [],
            "refinement_data": refinement,
            "consensus_metrics": payload.rationale.consensus_metrics,
            "decree": payload.rationale.final_decree,
            "reasoning_chain_id": chain_id,
            "workspace_id": payload.workspace_id,
            "campaign_name": None,
        }
        move_ids.append(await save_move(payload.campaign_id, move_record))

    return {
        "success": True,
        "move_ids": move_ids,
        "reasoning_chain_id": chain_id,
    }


@router.post("/campaigns/create")
async def persist_campaign_with_moves(
    payload: CouncilCampaignCreateRequest,
    _current_user: dict = Depends(get_current_user),
):
    """Persist campaign blueprint and associated moves with transactional consistency."""
    from db import get_db_transaction

    campaign_title = payload.campaign_data.title or "Campaign"
    campaign_tag = _slugify_campaign_title(campaign_title)
    campaign_payload = payload.campaign_data.model_dump()
    campaign_payload["workspace_id"] = payload.workspace_id
    campaign_payload["campaign_tag"] = campaign_tag

    try:
        async with get_db_transaction() as conn:
            # Create campaign first
            async with conn.cursor() as cur:
                query = """
                    INSERT INTO campaigns (
                        tenant_id, workspace_id, title, objective, status,
                        arc_data, phase_order, milestones, campaign_tag,
                        kpi_targets, audit_data
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id;
                """
                await cur.execute(
                    query,
                    (
                        payload.workspace_id,
                        payload.workspace_id,
                        campaign_payload.get("title"),
                        campaign_payload.get("objective"),
                        campaign_payload.get("status", "draft"),
                        psycopg.types.json.Jsonb(campaign_payload.get("arc_data", {})),
                        psycopg.types.json.Jsonb(
                            campaign_payload.get("phase_order", [])
                        ),
                        psycopg.types.json.Jsonb(
                            campaign_payload.get("milestones", [])
                        ),
                        campaign_tag,
                        psycopg.types.json.Jsonb(
                            campaign_payload.get("kpi_targets", {})
                        ),
                        psycopg.types.json.Jsonb(
                            campaign_payload.get("audit_data", {})
                        ),
                    ),
                )
                result = await cur.fetchone()
                campaign_id = str(result[0])

            # Create moves associated with the campaign
            move_ids: List[str] = []
            for i, move in enumerate(payload.moves):
                refinement = dict(move.refinement_data or {})
                if move.muse_prompt:
                    refinement.setdefault("muse_prompt", move.muse_prompt)
                refinement.setdefault("campaign_tag", campaign_tag)
                refinement.setdefault("campaignName", campaign_title)

                move_record = {
                    "title": move.title,
                    "description": move.description,
                    "status": "pending",
                    "priority": move.priority or 3,
                    "move_type": move.move_type,
                    "tool_requirements": move.tool_requirements or [],
                    "refinement_data": refinement,
                    "workspace_id": payload.workspace_id,
                    "campaign_name": campaign_title,
                    "campaign_id": campaign_id,
                }

                # Insert move with ordering
                async with conn.cursor() as cur:
                    query = """
                        INSERT INTO moves (
                            campaign_id, workspace_id, title, description, status, priority,
                            move_type, tool_requirements, refinement_data, consensus_metrics,
                            decree, reasoning_chain_id, campaign_name,
                            checklist, assets, daily_metrics,
                            confidence, started_at, completed_at, paused_at,
                            rag_status, rag_reason
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id;
                    """
                    await cur.execute(
                        query,
                        (
                            campaign_id,
                            move_record.get("workspace_id"),
                            move_record.get("title"),
                            move_record.get("description"),
                            move_record.get("status", "pending"),
                            move_record.get("priority", 3),
                            move_record.get("move_type"),
                            psycopg.types.json.Jsonb(
                                move_record.get("tool_requirements", [])
                            ),
                            psycopg.types.json.Jsonb(
                                move_record.get("refinement_data", {})
                            ),
                            psycopg.types.json.Jsonb(
                                move_record.get("consensus_metrics", {})
                            ),
                            move_record.get("decree"),
                            move_record.get("reasoning_chain_id"),
                            move_record.get("campaign_name"),
                            psycopg.types.json.Jsonb(move_record.get("checklist", [])),
                            psycopg.types.json.Jsonb(move_record.get("assets", [])),
                            psycopg.types.json.Jsonb(
                                move_record.get("daily_metrics", [])
                            ),
                            move_record.get("confidence"),
                            move_record.get("started_at"),
                            move_record.get("completed_at"),
                            move_record.get("paused_at"),
                            move_record.get("rag_status"),
                            move_record.get("rag_reason"),
                        ),
                    )
                    move_result = await cur.fetchone()
                    move_ids.append(str(move_result[0]))

            return {
                "success": True,
                "campaign_id": campaign_id,
                "move_ids": move_ids,
                "campaign_tag": campaign_tag,
                "move_count": len(move_ids),
            }

    except Exception as exc:
        logger.error("Failed to persist campaign with moves", exc_info=exc)
        raise HTTPException(
            status_code=500,
            detail="Unable to persist campaign data. Transaction rolled back.",
        )
