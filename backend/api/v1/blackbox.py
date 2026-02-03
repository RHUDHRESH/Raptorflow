"""
Blackbox strategy generation API endpoints.
"""

import uuid
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from memory.controller import MemoryController
from pydantic import BaseModel, Field
from workflows.blackbox import BlackboxWorkflow

from cognitive import CognitiveEngine

from ..agents.dispatcher import AgentDispatcher
from ..agents.specialists.blackbox_strategist import BlackboxStrategist
from ..core.database import get_db
from fastapi import Query
from ..dependencies import (
    get_agent_dispatcher,
    get_cognitive_engine,
    get_memory_controller,
)

router = APIRouter(prefix="/blackbox", tags=["blackbox"])


class StrategyGenerationRequest(BaseModel):
    """Request model for strategy generation."""

    focus_area: str = Field(
        ...,
        description="Area of focus: acquisition, retention, revenue, brand_equity, virality",
    )
    business_context: str = Field(
        ..., description="Business context and current situation"
    )
    constraints: Optional[str] = Field(None, description="Constraints and limitations")
    risk_tolerance: int = Field(default=5, description="Risk tolerance level (1-10)")
    timeline: Optional[str] = Field(
        None, description="Desired timeline for implementation"
    )
    budget_range: Optional[str] = Field(None, description="Budget range for strategy")
    workspace_id: str = Field(..., description="Workspace ID")
    user_id: str = Field(..., description="User ID")


class StrategyResponse(BaseModel):
    """Response model for strategy generation."""

    success: bool
    strategy_id: str
    strategy_name: str
    focus_area: str
    risk_level: int
    risk_reasons: List[str]
    phases: List[Dict[str, Any]]
    expected_upside: str
    potential_downside: str
    implementation_steps: List[str]
    success_metrics: List[str]
    tokens_used: int
    cost_usd: float
    error: Optional[str]


class StrategyListResponse(BaseModel):
    """Response model for strategy listing."""

    success: bool
    strategies: List[Dict[str, Any]]
    total_count: int
    error: Optional[str]


class StrategyAcceptRequest(BaseModel):
    """Request model for accepting a strategy."""

    strategy_id: str
    workspace_id: str
    user_id: str
    convert_to_move: bool = Field(default=True, description="Convert strategy to move")
    move_name: Optional[str] = Field(None, description="Name for the move if converted")


class StrategyAcceptResponse(BaseModel):
    """Response model for strategy acceptance."""

    success: bool
    strategy_id: str
    status: str
    move_id: Optional[str]
    message: str
    error: Optional[str]


# Global instance
blackbox_strategist = BlackboxStrategist()


@router.post("/generate", response_model=StrategyResponse)
async def generate_strategy(
    request: StrategyGenerationRequest,
    background_tasks: BackgroundTasks,
    user_id: str = Query(..., description="User ID"),
    db=Depends(get_db),
    memory_controller: MemoryController = Depends(get_memory_controller),
    cognitive_engine: CognitiveEngine = Depends(get_cognitive_engine),
    agent_dispatcher: AgentDispatcher = Depends(get_agent_dispatcher),
):
    """
    Generate a Blackbox strategy using creative but ethical approaches.

    This endpoint uses the BlackboxWorkflow to create innovative
    strategies for business challenges across different focus areas.
    """
    try:
        # Validate focus area
        valid_focus_areas = [
            "acquisition",
            "retention",
            "revenue",
            "brand_equity",
            "virality",
        ]
        if request.focus_area not in valid_focus_areas:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid focus area. Must be one of: {valid_focus_areas}",
            )

        # Validate risk tolerance
        if not 1 <= request.risk_tolerance <= 10:
            raise HTTPException(
                status_code=400, detail="Risk tolerance must be between 1 and 10"
            )

        # Initialize workflow
        workflow = BlackboxWorkflow(
            db_client=db,
            memory_controller=memory_controller,
            cognitive_engine=cognitive_engine,
            agent_dispatcher=agent_dispatcher,
        )

        # Generate strategy using BlackboxWorkflow
        result = await workflow.generate_strategy(
            workspace_id=request.workspace_id, volatility_level=request.risk_tolerance
        )

        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=f"Strategy generation failed: {result.get('error')}",
            )

        strategy_id = result["strategy_id"]
        strategy_output = result["strategy"]
        risk_assessment = result["risk_assessment"]

        return StrategyResponse(
            success=True,
            strategy_id=strategy_id,
            strategy_name=strategy_output.get(
                "title", f"{request.focus_area.title()} Strategy"
            ),
            focus_area=request.focus_area,
            risk_level=int(risk_assessment.get("risk_score", 0.5) * 10),
            risk_reasons=risk_assessment.get("risk_factors", []),
            phases=strategy_output.get("implementation_phases", []),
            expected_upside=strategy_output.get("expected_upside", ""),
            potential_downside=strategy_output.get("potential_downside", ""),
            implementation_steps=strategy_output.get("implementation_steps", []),
            success_metrics=strategy_output.get("success_metrics", []),
            tokens_used=result.get("tokens_used", 0),
            cost_usd=result.get("cost_usd", 0.0),
            error=None,
        )

    except HTTPException:
        raise
    except Exception as e:
        return StrategyResponse(
            success=False,
            strategy_id="",
            strategy_name="",
            focus_area=request.focus_area,
            risk_level=0,
            risk_reasons=[],
            phases=[],
            expected_upside="",
            potential_downside="",
            implementation_steps=[],
            success_metrics=[],
            tokens_used=0,
            cost_usd=0.0,
            error=f"Strategy generation failed: {str(e)}",
        )


@router.get("/strategies", response_model=StrategyListResponse)
async def list_strategies(
    workspace_id: str,
    limit: int = Query(default=50, description="Maximum strategies to return"),
    offset: int = 0,
    focus_area: Optional[str] = None,
    status: Optional[str] = None,
    user_id: str = Query(..., description="User ID"),
    db=Depends(get_db),
):
    """
    List Blackbox strategies for a workspace.

    Returns a paginated list of strategies with optional filtering.
    """
    try:
        # Query strategies from database
        query = "SELECT * FROM blackbox_strategies WHERE workspace_id = $1"
        params = [workspace_id]

        if focus_area:
            query += " AND focus_area = $2"
            params.append(focus_area)

        if status:
            query += " AND status = ${len(params) + 1}"
            params.append(status)

        query += " ORDER BY created_at DESC LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}"
        params.extend([limit, offset])

        strategies = await db.fetch(query, *params)

        # Get total count
        count_query = "SELECT COUNT(*) FROM blackbox_strategies WHERE workspace_id = $1"
        count_params = [workspace_id]

        if focus_area:
            count_query += " AND focus_area = $2"
            count_params.append(focus_area)

        if status:
            count_query += " AND status = ${len(count_params) + 1}"
            count_params.append(status)

        total_count = await db.fetchval(count_query, *count_params)

        return StrategyListResponse(
            success=True,
            strategies=[dict(strategy) for strategy in strategies],
            total_count=total_count,
            error=None,
        )

    except Exception as e:
        return StrategyListResponse(
            success=False,
            strategies=[],
            total_count=0,
            error=f"Failed to list strategies: {str(e)}",
        )


@router.get("/strategies/{strategy_id}", response_model=Dict[str, Any])
async def get_strategy(
    strategy_id: str,
    workspace_id: str,
    user_id: str = Query(..., description="User ID"),
    db=Depends(get_db),
):
    """
    Get a specific strategy by ID.
    """
    try:
        # Query strategy from database
        strategy = await db.fetchrow(
            "SELECT * FROM blackbox_strategies WHERE id = $1 AND workspace_id = $2",
            strategy_id,
            workspace_id,
        )

        if not strategy:
            raise HTTPException(status_code=404, detail="Strategy not found")

        return {"success": True, "strategy": dict(strategy)}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get strategy: {str(e)}")


@router.post("/strategies/{strategy_id}/accept", response_model=StrategyAcceptResponse)
async def accept_strategy(
    strategy_id: str,
    request: StrategyAcceptRequest,
    background_tasks: BackgroundTasks,
    user_id: str = Query(..., description="User ID"),
    db=Depends(get_db),
    memory_controller: MemoryController = Depends(get_memory_controller),
    cognitive_engine: CognitiveEngine = Depends(get_cognitive_engine),
    agent_dispatcher: AgentDispatcher = Depends(get_agent_dispatcher),
):
    """
    Accept a Blackbox strategy and optionally convert it to a move.

    This endpoint marks a strategy as accepted and can create a corresponding
    move for implementation.
    """
    try:
        # Initialize workflow
        workflow = BlackboxWorkflow(
            db_client=db,
            memory_controller=memory_controller,
            cognitive_engine=cognitive_engine,
            agent_dispatcher=agent_dispatcher,
        )

        # Mark as accepted in database
        await db.execute(
            "UPDATE blackbox_strategies SET status = 'accepted', accepted_at = NOW() WHERE id = $1",
            strategy_id,
        )

        move_id = None

        # Convert to move if requested
        if request.convert_to_move:
            result = await workflow.convert_to_move(strategy_id)
            if result.get("success"):
                move_id = result["move_ids"][0] if result["move_ids"] else None

        return StrategyAcceptResponse(
            success=True,
            strategy_id=strategy_id,
            status="accepted",
            move_id=move_id,
            message=f"Strategy accepted successfully"
            + (f" and converted to move {move_id}" if move_id else ""),
            error=None,
        )

    except HTTPException:
        raise
    except Exception as e:
        return StrategyAcceptResponse(
            success=False,
            strategy_id=strategy_id,
            status="error",
            move_id=None,
            message="Failed to accept strategy",
            error=str(e),
        )


@router.post("/strategies/{strategy_id}/reject", response_model=Dict[str, Any])
async def reject_strategy(
    strategy_id: str,
    workspace_id: str,
    reason: str = "",
    user_id: str = Query(..., description="User ID"),
    db=Depends(get_db),
):
    """
    Reject a Blackbox strategy.
    """
    try:
        # Check if strategy exists
        strategy = await db.fetchrow(
            "SELECT * FROM blackbox_strategies WHERE id = $1 AND workspace_id = $2",
            strategy_id,
            workspace_id,
        )

        if not strategy:
            raise HTTPException(status_code=404, detail="Strategy not found")

        # Update strategy status
        await db.execute(
            "UPDATE blackbox_strategies SET status = 'rejected', rejection_reason = $1, rejected_at = NOW() WHERE id = $2",
            reason,
            strategy_id,
        )

        return {"success": True, "message": "Strategy rejected successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to reject strategy: {str(e)}"
        )


@router.delete("/strategies/{strategy_id}", response_model=Dict[str, Any])
async def delete_strategy(
    strategy_id: str,
    workspace_id: str,
    user_id: str = Query(..., description="User ID"),
    db=Depends(get_db),
):
    """
    Delete a blackbox strategy.
    """
    try:
        # Check if strategy exists
        existing_strategy = await db.fetchrow(
            "SELECT * FROM blackbox_strategies WHERE id = $1 AND workspace_id = $2",
            strategy_id,
            workspace_id,
        )

        if not existing_strategy:
            raise HTTPException(status_code=404, detail="Strategy not found")

        # Delete strategy
        await db.execute(
            "DELETE FROM blackbox_strategies WHERE id = $1 AND workspace_id = $2",
            strategy_id,
            workspace_id,
        )

        return {"success": True, "message": "Strategy deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to delete strategy: {str(e)}"
        )


# Helper functions
async def save_strategy_to_database(
    strategy_id: str,
    request: StrategyGenerationRequest,
    result: Dict[str, Any],
    strategy_output: Dict[str, Any],
    db,
):
    """Save generated strategy to database."""
    try:
        await db.execute(
            """
            INSERT INTO blackbox_strategies (
                id, workspace_id, user_id, name, focus_area, risk_level,
                risk_reasons, phases, expected_upside, potential_downside,
                implementation_steps, success_metrics, business_context,
                constraints, risk_tolerance, timeline, budget_range,
                tokens_used, cost_usd, status, created_at, updated_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, NOW(), NOW())
            """,
            strategy_id,
            request.workspace_id,
            request.user_id,
            strategy_output.get("name", f"{request.focus_area.title()} Strategy"),
            request.focus_area,
            strategy_output.get("risk_level", 5),
            strategy_output.get("risk_reasons", []),
            strategy_output.get("phases", []),
            strategy_output.get("expected_upside", ""),
            strategy_output.get("potential_downside", ""),
            strategy_output.get("implementation_steps", []),
            strategy_output.get("success_metrics", []),
            request.business_context,
            request.constraints,
            request.risk_tolerance,
            request.timeline,
            request.budget_range,
            result.get("tokens_used", 0),
            result.get("cost_usd", 0.0),
            "generated",
        )
    except Exception as e:
        # Log error but don't fail the request
        print(f"Failed to save strategy to database: {e}")


async def convert_strategy_to_move(
    strategy: Dict[str, Any],
    move_name: Optional[str],
    workspace_id: str,
    user_id: str,
    db,
):
    """Convert a Blackbox strategy to a move."""
    try:
        # Generate move name if not provided
        if not move_name:
            move_name = f"Move: {strategy['name']}"

        # Extract move details from strategy
        phases = strategy.get("phases", [])
        implementation_steps = strategy.get("implementation_steps", [])
        success_metrics = strategy.get("success_metrics", [])

        # Create move record
        move_id = str(uuid.uuid4())

        await db.execute(
            """
            INSERT INTO moves (
                id, workspace_id, user_id, name, category, description,
                objectives, success_metrics, implementation_steps,
                duration_days, status, created_at, updated_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, NOW(), NOW())
            """,
            move_id,
            workspace_id,
            user_id,
            move_name,
            strategy["focus_area"],
            f"Generated from Blackbox strategy: {strategy['name']}",
            strategy.get("expected_upside", ""),
            success_metrics,
            implementation_steps,
            len(phases) * 7,  # Estimate 7 days per phase
            "planned",
        )

        # Link strategy to move
        await db.execute(
            "UPDATE blackbox_strategies SET converted_to_move_id = $1 WHERE id = $2",
            move_id,
            strategy["id"],
        )

        return move_id

    except Exception as e:
        print(f"Failed to convert strategy to move: {e}")
        return None
