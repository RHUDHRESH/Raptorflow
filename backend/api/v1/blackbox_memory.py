from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel

from core.auth import get_current_user, get_tenant_id
from core.vault import Vault
from services.blackbox_service import BlackboxService

router = APIRouter(prefix="/v1/blackbox/memory", tags=["blackbox"])


def get_blackbox_service():
    """Dependency provider for BlackboxService."""
    vault = Vault()
    return BlackboxService(vault)


class LearningCreate(BaseModel):
    content: str
    learning_type: str
    source_ids: Optional[List[UUID]] = None


class EvidenceLink(BaseModel):
    learning_id: UUID
    trace_ids: List[UUID]


@router.post("/upsert", status_code=status.HTTP_201_CREATED)
def upsert_learning(
    learning: LearningCreate,
    tenant_id: UUID = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    service: BlackboxService = Depends(get_blackbox_service),
):
    """Generates embedding and persists a new strategic learning."""
    service.upsert_learning_embedding(
        content=learning.content,
        learning_type=learning.learning_type,
        source_ids=learning.source_ids,
        tenant_id=tenant_id,
        user_id=current_user.get("id"),
    )
    return {"status": "persisted"}


@router.get("/search", response_model=List[Dict])
def search_memory(
    query: str,
    limit: int = 5,
    tenant_id: UUID = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    service: BlackboxService = Depends(get_blackbox_service),
):
    """Searches strategic memory for relevant insights."""
    return service.search_strategic_memory(
        query=query, limit=limit, tenant_id=tenant_id, user_id=current_user.get("id")
    )


@router.post("/link-evidence")
def link_evidence(
    link: EvidenceLink,
    tenant_id: UUID = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    service: BlackboxService = Depends(get_blackbox_service),
):
    """Links existing traces to a learning."""
    service.link_learning_to_evidence(
        learning_id=link.learning_id,
        trace_ids=link.trace_ids,
        tenant_id=tenant_id,
        user_id=current_user.get("id"),
        enforce_access=True,
    )
    return {"status": "linked"}


@router.get("/planner-context")
def get_planner_context(
    move_type: str,
    limit: int = 5,
    tenant_id: UUID = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    service: BlackboxService = Depends(get_blackbox_service),
):
    """Retrieves formatted context for the planner agent."""
    context = service.get_memory_context_for_planner(
        move_type=move_type,
        limit=limit,
        tenant_id=tenant_id,
        user_id=current_user.get("id"),
    )
    return {"context": context}


@router.delete("/prune")
def prune_memory(
    learning_type: str,
    before: datetime,
    tenant_id: UUID = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    service: BlackboxService = Depends(get_blackbox_service),
):
    """Removes outdated learnings."""
    service.prune_strategic_memory(
        learning_type=learning_type,
        before=before,
        tenant_id=tenant_id,
        user_id=current_user.get("id"),
    )
    return {"status": "pruned"}
