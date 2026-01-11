"""
FastAPI endpoint for agent execution.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

from ...agents.dispatcher import AgentDispatcher
from ...agents.exceptions import AuthenticationError, ValidationError, WorkspaceError
from ...agents.preprocessing import ContextLoader
from ...config import validate_config

logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

# Router
router = APIRouter(prefix="/api/v1/agents", tags=["agents"])

# Global instances (in production, these would be dependency injected)
dispatcher = AgentDispatcher()
context_loader = ContextLoader()


# Pydantic models
class AgentRequest(BaseModel):
    """Request model for agent execution."""

    request: str = Field(
        ..., min_length=1, max_length=10000, description="User request"
    )
    workspace_id: str = Field(
        ..., min_length=3, max_length=100, description="Workspace ID"
    )
    user_id: str = Field(..., min_length=3, max_length=100, description="User ID")
    session_id: str = Field(..., min_length=3, max_length=100, description="Session ID")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    agent_hint: Optional[str] = Field(None, description="Agent name hint")
    fast_mode: bool = Field(False, description="Use fast routing mode")


class AgentResponse(BaseModel):
    """Response model for agent execution."""

    success: bool
    agent: str
    workspace_id: str
    user_id: str
    session_id: str
    execution_time_seconds: float
    timestamp: str
    routing_decision: Optional[Dict[str, Any]] = None
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    error_code: Optional[str] = None


class AgentInfoResponse(BaseModel):
    """Response model for agent information."""

    agent_name: str
    description: str
    model_tier: str
    tools: List[str]
    usage_stats: Dict[str, Any]


class DispatcherStatsResponse(BaseModel):
    """Response model for dispatcher statistics."""

    total_requests: int
    successful_requests: int
    success_rate: float
    average_execution_time: float
    agent_usage: Dict[str, int]
    registered_agents: List[str]
    max_history: int
    current_history_size: int


class HealthResponse(BaseModel):
    """Response model for health check."""

    status: str
    timestamp: str
    dispatcher_status: Dict[str, Any]
    context_loader_status: Dict[str, Any]
    registered_agents: int


# Authentication dependency
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify authentication token."""
    try:
        # In a real implementation, this would verify the JWT token
        # For now, we'll just check that a token is provided
        if not credentials.credentials:
            raise AuthenticationError("No token provided")

        # TODO: Implement proper JWT verification
        return credentials.credentials

    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")


# Workspace validation dependency
async def validate_workspace(workspace_id: str, token: str = Depends(verify_token)):
    """Validate workspace access."""
    try:
        # In a real implementation, this would check if the user has access to the workspace
        # For now, we'll just validate the format
        if not workspace_id or len(workspace_id) < 3:
            raise ValidationError("Invalid workspace ID")

        return workspace_id

    except Exception as e:
        logger.error(f"Workspace validation failed: {e}")
        raise HTTPException(status_code=403, detail="Workspace access denied")


# Rate limiting (simple in-memory implementation)
class RateLimiter:
    """Simple rate limiter for API endpoints."""

    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, List[datetime]] = {}

    async def check_rate_limit(self, key: str) -> bool:
        """Check if the key has exceeded the rate limit."""
        now = datetime.now()

        # Clean old requests
        if key in self.requests:
            self.requests[key] = [
                req_time
                for req_time in self.requests[key]
                if (now - req_time).total_seconds() < self.window_seconds
            ]
        else:
            self.requests[key] = []

        # Check if under limit
        if len(self.requests[key]) >= self.max_requests:
            return False

        # Add current request
        self.requests[key].append(now)
        return True


rate_limiter = RateLimiter()


# Rate limiting dependency
async def check_rate_limit(
    workspace_id: str, user_id: str, token: str = Depends(verify_token)
):
    """Check rate limits for the user."""
    key = f"{workspace_id}:{user_id}"

    if not await rate_limiter.check_rate_limit(key):
        raise HTTPException(
            status_code=429, detail="Rate limit exceeded. Please try again later."
        )


# Endpoints
@router.post("/execute", response_model=AgentResponse)
async def execute_agent(
    request: AgentRequest,
    token: str = Depends(verify_token),
    workspace_id: str = Depends(validate_workspace),
    rate_ok: None = Depends(check_rate_limit),
):
    """Execute an agent request."""
    try:
        # Validate configuration
        if not validate_config():
            raise HTTPException(
                status_code=503, detail="Service configuration is invalid"
            )

        # Dispatch request
        result = await dispatcher.dispatch(
            request=request.request,
            workspace_id=request.workspace_id,
            user_id=request.user_id,
            session_id=request.session_id,
            context=request.context,
            agent_hint=request.agent_hint,
            fast_mode=request.fast_mode,
        )

        # Convert to response model
        response = AgentResponse(**result)

        # Log successful execution
        logger.info(
            f"Agent executed successfully: {response.agent} "
            f"for workspace {response.workspace_id} "
            f"in {response.execution_time_seconds:.2f}s"
        )

        return response

    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    except WorkspaceError as e:
        logger.error(f"Workspace error: {e}")
        raise HTTPException(status_code=403, detail=str(e))

    except AuthenticationError as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(status_code=401, detail=str(e))

    except Exception as e:
        logger.error(f"Agent execution failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/agents", response_model=List[str])
async def list_agents(token: str = Depends(verify_token)):
    """List all available agents."""
    try:
        agents = dispatcher.registry.list_agents()
        return agents

    except Exception as e:
        logger.error(f"Failed to list agents: {e}")
        raise HTTPException(status_code=500, detail="Failed to list agents")


@router.get("/agents/{agent_name}", response_model=AgentInfoResponse)
async def get_agent_info(agent_name: str, token: str = Depends(verify_token)):
    """Get information about a specific agent."""
    try:
        agent_info = dispatcher.get_agent_info(agent_name)

        if not agent_info:
            raise HTTPException(status_code=404, detail="Agent not found")

        return AgentInfoResponse(**agent_info)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get agent info: {e}")
        raise HTTPException(status_code=500, detail="Failed to get agent info")


@router.get("/stats", response_model=DispatcherStatsResponse)
async def get_dispatcher_stats(token: str = Depends(verify_token)):
    """Get dispatcher statistics."""
    try:
        stats = dispatcher.get_dispatcher_stats()
        return DispatcherStatsResponse(**stats)

    except Exception as e:
        logger.error(f"Failed to get dispatcher stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get statistics")


@router.get("/history")
async def get_request_history(
    workspace_id: Optional[str] = None,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    limit: int = Field(100, ge=1, le=1000),
    token: str = Depends(verify_token),
):
    """Get request history with optional filtering."""
    try:
        history = dispatcher.get_request_history(
            workspace_id=workspace_id,
            user_id=user_id,
            session_id=session_id,
            limit=limit,
        )

        return {
            "history": history,
            "total": len(history),
            "filters": {
                "workspace_id": workspace_id,
                "user_id": user_id,
                "session_id": session_id,
                "limit": limit,
            },
        }

    except Exception as e:
        logger.error(f"Failed to get request history: {e}")
        raise HTTPException(status_code=500, detail="Failed to get history")


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Check the health of the agent system."""
    try:
        # Get dispatcher health
        dispatcher_health = dispatcher.get_health_status()

        # Get context loader stats
        context_stats = context_loader.get_context_loading_stats()

        # Get registered agents count
        agents_count = len(dispatcher.registry.list_agents())

        # Determine overall status
        overall_status = "healthy"
        if dispatcher_health.get("status") != "healthy":
            overall_status = "degraded"

        return HealthResponse(
            status=overall_status,
            timestamp=datetime.now().isoformat(),
            dispatcher_status=dispatcher_health,
            context_loader_status=context_stats,
            registered_agents=agents_count,
        )

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            timestamp=datetime.now().isoformat(),
            dispatcher_status={"error": str(e)},
            context_loader_status={"error": str(e)},
            registered_agents=0,
        )


@router.post("/context/load")
async def load_context(
    workspace_id: str,
    user_id: str,
    session_id: str,
    context_type: str = "full",
    token: str = Depends(verify_token),
    workspace_valid: str = Depends(validate_workspace),
):
    """Load context for a workspace."""
    try:
        context = await context_loader.load_context(
            workspace_id=workspace_id,
            user_id=user_id,
            session_id=session_id,
            context_type=context_type,
        )

        return {
            "success": True,
            "context": context,
            "loaded_at": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Failed to load context: {e}")
        raise HTTPException(status_code=500, detail="Failed to load context")


@router.post("/batch-execute")
async def batch_execute_agents(
    requests: List[AgentRequest],
    background_tasks: BackgroundTasks,
    token: str = Depends(verify_token),
):
    """Execute multiple agent requests in parallel."""
    try:
        if len(requests) > 10:
            raise HTTPException(
                status_code=400, detail="Maximum 10 requests allowed per batch"
            )

        # Execute requests in parallel
        tasks = []
        for req in requests:
            task = dispatcher.dispatch(
                request=req.request,
                workspace_id=req.workspace_id,
                user_id=req.user_id,
                session_id=req.session_id,
                context=req.context,
                agent_hint=req.agent_hint,
                fast_mode=req.fast_mode,
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        responses = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                responses.append(
                    {
                        "success": False,
                        "error": str(result),
                        "error_code": "BATCH_EXECUTION_FAILED",
                        "request_index": i,
                    }
                )
            else:
                responses.append(result)

        return {
            "success": True,
            "batch_size": len(requests),
            "results": responses,
            "timestamp": datetime.now().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch execution failed: {e}")
        raise HTTPException(status_code=500, detail="Batch execution failed")


@router.delete("/history")
async def clear_history(
    workspace_id: Optional[str] = None,
    user_id: Optional[str] = None,
    token: str = Depends(verify_token),
):
    """Clear request history (admin only)."""
    try:
        # In a real implementation, this would check admin permissions
        dispatcher.clear_history()

        return {
            "success": True,
            "message": "History cleared",
            "cleared_at": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Failed to clear history: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear history")
