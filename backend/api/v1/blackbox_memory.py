from fastapi import APIRouter, Depends, status, Query
from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel
from backend.services.blackbox_service import BlackboxService
from backend.core.vault import Vault

router = APIRouter(prefix="/v1/blackbox/memory", tags=["blackbox"])


def get_blackbox_service():
    """Dependency provider for BlackboxService."""
    vault = Vault()
    return BlackboxService(vault)


class CategorizeRequest(BaseModel):
    content: str


@router.get("/search", response_model=List[Dict])
def search_memory(
    query: str, 
    limit: int = 5, 
    service: BlackboxService = Depends(get_blackbox_service)
):
    """Searches strategic learnings via vector similarity."""
    return service.search_strategic_memory(query=query, limit=limit)


@router.post("/categorize")
def categorize_learning(
    request: CategorizeRequest, 
    service: BlackboxService = Depends(get_blackbox_service)
):
    """Automatically categorizes a learning string."""
    category = service.categorize_learning(request.content)
    return {"content": request.content, "category": category}


@router.delete("/prune")
def prune_memory(
    learning_type: str, 
    before: Optional[datetime] = None, 
    service: BlackboxService = Depends(get_blackbox_service)
):
    """Prunes old learnings of a specific type."""
    target_date = before or datetime.now()
    service.prune_strategic_memory(learning_type=learning_type, before=target_date)
    return {"status": "pruned", "type": learning_type, "before": target_date}
