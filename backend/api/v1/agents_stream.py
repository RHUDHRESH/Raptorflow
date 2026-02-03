"""
Streaming agents API endpoints for real-time responses.
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Any, AsyncGenerator, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from ..agents.dispatcher import AgentDispatcher
from ..agents.routing.pipeline import RoutingPipeline
from fastapi import Query
from ..core.database import get_db

router = APIRouter(prefix="/agents", tags=["agents"])


class AgentRequest(BaseModel):
    """Request model for agent execution."""

    request_type: str = Field(..., description="Type of request")
    request_data: Dict[str, Any] = Field(..., description="Request data")
    workspace_id: str = Field(..., description="Workspace ID")
    user_id: str = Field(..., description="User ID")
    session_id: Optional[str] = Field(None, description="Session ID for tracking")
    fast_mode: bool = Field(default=False, description="Use fast routing mode")
    stream: bool = Field(default=True, description="Stream response")


class AgentResponse(BaseModel):
    """Response model for agent execution."""

    success: bool
    output: Optional[str]
    agent: str
    routing_path: List[str]
    tokens_used: int
    cost_usd: float
    requires_approval: bool
    approval_gate_id: Optional[str]
    error: Optional[str]


# Global instances
agent_dispatcher = AgentDispatcher()
routing_pipeline = RoutingPipeline()


async def generate_sse_events(
    request: AgentRequest, current_user: Dict, db
) -> AsyncGenerator[str, None]:
    """
    Generate Server-Sent Events for streaming agent responses.
    """
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())

        # Send start event
        yield f"event: start\ndata: {json.dumps({'session_id': session_id, 'timestamp': datetime.now().isoformat()})}\n\n"

        # Route the request
        yield f"event: routing\ndata: {json.dumps({'status': 'routing', 'message': 'Determining best agent for request'})}\n\n"

        routing_decision = await routing_pipeline.route(
            request=request.request_data.get("query", ""),
            workspace_id=request.workspace_id,
            fast_mode=request.fast_mode,
        )

        yield f"event: routed\ndata: {json.dumps({'agent': routing_decision.target_agent, 'confidence': routing_decision.confidence})}\n\n"

        # Execute the agent
        yield f"event: executing\ndata: {json.dumps({'status': 'executing', 'agent': routing_decision.target_agent})}\n\n"

        # For streaming, we'll simulate progress updates
        # In a real implementation, this would stream actual agent output
        for i in range(5):
            await asyncio.sleep(0.5)  # Simulate processing time
            progress = (i + 1) * 20
            yield f"event: progress\ndata: {json.dumps({'progress': progress, 'message': f'Processing step {i+1}/5'})}\n\n"

        # Get final result
        result = await agent_dispatcher.dispatch(
            request=request.request_data.get("query", ""),
            workspace_id=request.workspace_id,
            user_id=request.user_id,
            session_id=session_id,
            fast_mode=request.fast_mode,
        )

        # Send final result
        final_data = {
            "success": not result.get("error"),
            "output": result.get("output"),
            "agent": routing_decision.target_agent,
            "routing_path": routing_decision.routing_path,
            "tokens_used": result.get("tokens_used", 0),
            "cost_usd": result.get("cost_usd", 0.0),
            "requires_approval": result.get("requires_approval", False),
            "approval_gate_id": result.get("approval_gate_id"),
            "error": result.get("error"),
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
        }

        yield f"event: complete\ndata: {json.dumps(final_data)}\n\n"

    except Exception as e:
        # Send error event
        error_data = {
            "error": str(e),
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
        }
        yield f"event: error\ndata: {json.dumps(error_data)}\n\n"


@router.post("/execute/stream")
async def execute_agent_stream(
    request: AgentRequest,
    background_tasks: BackgroundTasks,
    user_id: str = Query(..., description="User ID"),
    db=Depends(get_db),
):
    """
    Execute agent with streaming response.

    This endpoint provides real-time updates during agent execution
    using Server-Sent Events (SSE).
    """
    try:
        if not request.stream:
            raise HTTPException(
                status_code=400, detail="Stream must be true for this endpoint"
            )

        # Log execution start (async background task)
        background_tasks.add_task(
            log_agent_execution, request=request, user_id=user_id, db=db
        )

        # Return streaming response
        return StreamingResponse(
            generate_sse_events(request, user_id, db),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Cache-Control",
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Streaming execution failed: {str(e)}"
        )


@router.post("/execute", response_model=AgentResponse)
async def execute_agent(
    request: AgentRequest,
    background_tasks: BackgroundTasks,
    user_id: str = Query(..., description="User ID"),
    db=Depends(get_db),
):
    """
    Execute agent without streaming.

    This endpoint provides the same functionality as the streaming endpoint
    but returns a single response after completion.
    """
    try:
        if request.stream:
            raise HTTPException(
                status_code=400, detail="Stream must be false for this endpoint"
            )

        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())

        # Route the request
        routing_decision = await routing_pipeline.route(
            request=request.request_data.get("query", ""),
            workspace_id=request.workspace_id,
            fast_mode=request.fast_mode,
        )

        # Execute the agent
        result = await agent_dispatcher.dispatch(
            request=request.request_data.get("query", ""),
            workspace_id=request.workspace_id,
            user_id=request.user_id,
            session_id=session_id,
            fast_mode=request.fast_mode,
        )

        # Log execution (async background task)
        background_tasks.add_task(
            log_agent_execution, request=request, current_user=current_user, db=db
        )

        return AgentResponse(
            success=not result.get("error"),
            output=result.get("output"),
            agent=routing_decision.target_agent,
            routing_path=routing_decision.routing_path,
            tokens_used=result.get("tokens_used", 0),
            cost_usd=result.get("cost_usd", 0.0),
            requires_approval=result.get("requires_approval", False),
            approval_gate_id=result.get("approval_gate_id"),
            error=result.get("error"),
        )

    except HTTPException:
        raise
    except Exception as e:
        return AgentResponse(
            success=False,
            output=None,
            agent="",
            routing_path=[],
            tokens_used=0,
            cost_usd=0.0,
            requires_approval=False,
            approval_gate_id=None,
            error=f"Agent execution failed: {str(e)}",
        )


@router.get("/status/{session_id}", response_model=Dict[str, Any])
async def get_session_status(
    session_id: str,
    workspace_id: str,
    user_id: str = Query(..., description="User ID"),
    db=Depends(get_db),
):
    """
    Get the status of an agent execution session.

    Returns current state and progress for active or recent sessions.
    """
    try:
        # Query session from database
        session = await db.fetchrow(
            """
            SELECT * FROM agent_sessions
            WHERE id = $1 AND workspace_id = $2
            ORDER BY created_at DESC
            LIMIT 1
            """,
            session_id,
            workspace_id,
        )

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        session_data = dict(session)

        # Get execution logs for this session
        execution_logs = await db.fetch(
            """
            SELECT * FROM agent_execution_logs
            WHERE session_id = $1 AND workspace_id = $2
            ORDER BY created_at DESC
            LIMIT 10
            """,
            session_id,
            workspace_id,
        )

        return {
            "success": True,
            "session": session_data,
            "execution_logs": [dict(log) for log in execution_logs],
            "is_active": session_data.get("status") == "active",
        }

    except HTTPException:
        raise
    except Exception as e:
        return {"success": False, "error": f"Failed to get session status: {str(e)}"}


@router.get("/sessions", response_model=Dict[str, Any])
async def list_sessions(
    workspace_id: str,
    limit: int = Query(default=50, description="Maximum sessions to return"),
    status: Optional[str] = None,
    agent: Optional[str] = None,
    user_id: str = Query(..., description="User ID"),
    db=Depends(get_db),
):
    """
    List agent execution sessions for a workspace.

    Returns paginated list of sessions with optional filtering.
    """
    try:
        # Build query
        query = "SELECT * FROM agent_sessions WHERE workspace_id = $1"
        params = [workspace_id]
        param_index = 2

        if status:
            query += f" AND status = ${param_index}"
            params.append(status)
            param_index += 1

        if agent:
            query += f" AND agent_name = ${param_index}"
            params.append(agent)
            param_index += 1

        query += f" ORDER BY created_at DESC LIMIT ${param_index}"
        params.append(limit)

        # Execute query
        sessions = await db.fetch(query, *params)

        return {
            "success": True,
            "sessions": [dict(session) for session in sessions],
            "total_count": len(sessions),
        }

    except Exception as e:
        return {"success": False, "error": f"Failed to list sessions: {str(e)}"}


@router.post("/sessions/{session_id}/cancel", response_model=Dict[str, Any])
async def cancel_session(
    session_id: str,
    workspace_id: str,
    reason: str = "",
    user_id: str = Query(..., description="User ID"),
    db=Depends(get_db),
):
    """
    Cancel an active agent execution session.
    """
    try:
        # Check if session exists and is active
        session = await db.fetchrow(
            "SELECT * FROM agent_sessions WHERE id = $1 AND workspace_id = $2 AND status = 'active'",
            session_id,
            workspace_id,
        )

        if not session:
            raise HTTPException(status_code=404, detail="Active session not found")

        # Update session status
        await db.execute(
            """
            UPDATE agent_sessions SET
                status = 'cancelled',
                cancellation_reason = $1,
                ended_at = NOW()
            WHERE id = $2
            """,
            reason,
            session_id,
        )

        return {"success": True, "message": "Session cancelled successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to cancel session: {str(e)}"
        )


@router.get("/agents", response_model=Dict[str, Any])
async def list_available_agents(user_id: str = Query(..., description="User ID")):
    """
    List all available agents and their capabilities.
    """
    try:
        # Get available agents from dispatcher
        agents = agent_dispatcher.list_agents()

        # Format agent information
        agent_list = []
        for agent_name, agent_class in agents.items():
            agent_info = {
                "name": agent_name,
                "description": getattr(
                    agent_class, "__doc__", "No description available"
                ),
                "capabilities": getattr(agent_class, "capabilities", []),
                "model_tier": getattr(agent_class, "model_tier", "FLASH"),
            }
            agent_list.append(agent_info)

        return {"success": True, "agents": agent_list, "total_count": len(agent_list)}

    except Exception as e:
        return {"success": False, "error": f"Failed to list agents: {str(e)}"}


@router.get("/health", response_model=Dict[str, Any])
async def get_agent_health(user_id: str = Query(..., description="User ID")):
    """
    Get health status of agent system components.
    """
    try:
        # Check dispatcher health
        dispatcher_healthy = agent_dispatcher is not None

        # Check routing pipeline health
        routing_healthy = routing_pipeline is not None

        # Get system metrics
        health_status = {
            "dispatcher": "healthy" if dispatcher_healthy else "unhealthy",
            "routing_pipeline": "healthy" if routing_healthy else "unhealthy",
            "overall": (
                "healthy" if dispatcher_healthy and routing_healthy else "degraded"
            ),
        }

        return {
            "success": True,
            "health": health_status,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        return {"success": False, "error": f"Failed to get health status: {str(e)}"}


# Helper functions
async def log_agent_execution(request: AgentRequest, current_user: Dict, db):
    """Log agent execution for analytics."""
    try:
        session_id = request.session_id or str(uuid.uuid4())

        # Create session record
        await db.execute(
            """
            INSERT INTO agent_sessions (
                id, workspace_id, user_id, request_type, request_data,
                fast_mode, stream, status, created_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW())
            """,
            session_id,
            request.workspace_id,
            request.user_id,
            request.request_type,
            request.request_data,
            request.fast_mode,
            request.stream,
            "started",
        )

        # Log execution start
        await db.execute(
            """
            INSERT INTO agent_execution_logs (
                workspace_id, user_id, session_id, request_type,
                request_data, created_at
            ) VALUES ($1, $2, $3, $4, $5, NOW())
            """,
            request.workspace_id,
            request.user_id,
            session_id,
            request.request_type,
            request.request_data,
        )

    except Exception as e:
        print(f"Failed to log agent execution: {e}")


async def update_session_status(
    session_id: str, status: str, result: Dict[str, Any], db
):
    """Update session status with results."""
    try:
        await db.execute(
            """
            UPDATE agent_sessions SET
                status = $1,
                result = $2,
                ended_at = NOW()
            WHERE id = $3
            """,
            status,
            result,
            session_id,
        )
    except Exception as e:
        print(f"Failed to update session status: {e}")
