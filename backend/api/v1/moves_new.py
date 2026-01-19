"""
NEW Moves API - Campaign and move orchestration using Synapse
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from synapse import brain

router = APIRouter(prefix="/moves", tags=["moves"])

class MoveRequest(BaseModel):
    move_name: str
    context: Dict[str, Any] = {}
    user_id: str
    workspace_id: str
    flow_id: str = "default"

class MoveResponse(BaseModel):
    success: bool
    data: Dict[str, Any] = {}
    error: str = ""

@router.post("/execute", response_model=MoveResponse)
async def execute_move(request: MoveRequest):
    """Execute a strategic move using Synapse"""
    try:
        # Create input context
        context = {
            "task": request.move_name,
            **request.context,
            "user_id": request.user_id,
            "workspace_id": request.workspace_id,
            "flow_id": request.flow_id
        }
        
        # Execute the move sequence
        result = await brain.run_move(request.move_name, context, request.flow_id)
        
        return MoveResponse(
            success=result.get("status") == "success",
            data=result.get("data", {}),
            error=result.get("error") or ""
        )
        
    except Exception as e:
        return MoveResponse(
            success=False,
            error=str(e)
        )

@router.get("/available", response_model=Dict[str, List[str]])
async def list_available_moves():
    """List all available move sequences"""
    try:
        return {
            "moves": ["market_research", "content_creation", "competitive_analysis", "product_launch"]
        }
    except Exception as e:
        return {"error": str(e)}
