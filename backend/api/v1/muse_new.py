"""
NEW Muse API - Simplified content generation using Synapse
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from synapse import brain
from schemas import NodeInput, NodeOutput

router = APIRouter(prefix="/muse", tags=["muse"])

class ContentRequest(BaseModel):
    task: str
    context: Dict[str, Any] = {}
    user_id: str
    workspace_id: str
    session_id: str = "default"

class ContentResponse(BaseModel):
    success: bool
    content: str = ""
    seo_score: float = 0.0
    suggestions: list = []
    error: str = ""

@router.post("/generate", response_model=ContentResponse)
async def generate_content(request: ContentRequest):
    """Generate content using Synapse brain"""
    try:
        # Create input for content node
        node_input = NodeInput(
            task=request.task,
            context=request.context,
            user_id=request.user_id,
            workspace_id=request.workspace_id,
            session_id=request.session_id
        )
        
        # Execute content node
        result = await brain.run_node("content_creator", {
            "task": request.task,
            "context": request.context,
            "user_id": request.user_id,
            "workspace_id": request.workspace_id,
            "session_id": request.session_id
        })
        
        # Execute SEO node if content was created
        if result.get("status") == "success":
            seo_result = await brain.run_node("seo_skill", {
                "content": result["data"]["content"]
            })
            result["data"]["seo_score"] = seo_result["data"].get("seo_score", 0.0)
            result["data"]["seo_suggestions"] = seo_result["data"].get("suggestions", [])
        
        return ContentResponse(
            success=result.get("status") == "success",
            content=result.get("data", {}).get("content", ""),
            seo_score=result.get("data", {}).get("seo_score", 0.0),
            suggestions=result.get("data", {}).get("seo_suggestions", []),
            error=result.get("error") or ""
        )
        
    except Exception as e:
        return ContentResponse(
            success=False,
            error=str(e)
        )
