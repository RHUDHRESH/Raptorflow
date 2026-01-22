"""
FastAPI endpoint for agent execution.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

from backend.agents.exceptions import AuthenticationError, ValidationError, WorkspaceError
from backend.config import validate_config
from backend.core.validation import validate_agent_request

logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

# Router
router = APIRouter(prefix="/api/v1/agents", tags=["agents"])

# Global instances - lazy initialized to avoid import-time blocking
_dispatcher = None
_context_loader = None


def get_dispatcher():
    """Lazy-load AgentDispatcher to avoid import-time GCP initialization."""
    global _dispatcher
    if _dispatcher is None:
        from agents.dispatcher import AgentDispatcher
        _dispatcher = AgentDispatcher()
    return _dispatcher


def get_context_loader():
    """Lazy-load ContextLoader to avoid import-time blocking."""
    global _context_loader
    if _context_loader is None:
        from agents.preprocessing import ContextLoader
        _context_loader = ContextLoader()
    return _context_loader


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
    http_request: Request,
    token: str = Depends(verify_token),
    workspace_id: str = Depends(validate_workspace),
    rate_ok: None = Depends(check_rate_limit),
):
    """Execute an agent request."""
    try:
        # Enhanced validation
        client_ip = http_request.client.host if http_request.client else None
        validated_request = validate_agent_request(request.dict(), client_ip)
        
        # Validate configuration
        if not validate_config():
            raise HTTPException(
                status_code=503, detail="Service configuration is invalid"
            )

        # Dispatch request with validated data
        result = await get_dispatcher().dispatch(
            request=validated_request.request,
            workspace_id=validated_request.workspace_id,
            user_id=validated_request.user_id,
            session_id=validated_request.session_id,
            context=validated_request.context,
            agent_hint=validated_request.agent_hint,
            fast_mode=validated_request.fast_mode,
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
        agents = get_dispatcher().registry.list_agents()
        return agents

    except Exception as e:
        logger.error(f"Failed to list agents: {e}")
        raise HTTPException(status_code=500, detail="Failed to list agents")


@router.get("/agents/{agent_name}", response_model=AgentInfoResponse)
async def get_agent_info(agent_name: str, token: str = Depends(verify_token)):
    """Get information about a specific agent."""
    try:
        agent_info = get_dispatcher().get_agent_info(agent_name)

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
        stats = get_dispatcher().get_dispatcher_stats()
        return DispatcherStatsResponse(**stats)

    except Exception as e:
        logger.error(f"Failed to get dispatcher stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get statistics")


@router.get("/history")
async def get_request_history(
    workspace_id: Optional[str] = None,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    token: str = Depends(verify_token),
):
    """Get request history with optional filtering."""
    try:
        history = get_dispatcher().get_request_history(
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
    """Check health of agent system."""
    try:
        # Use enhanced health monitoring
        from core.health import run_health_checks
        
        health = await run_health_checks()
        
        # Get dispatcher for agent-specific checks
        dispatcher = get_dispatcher()
        
        # Agent-specific health checks
        agent_health_status = await _check_agent_health(dispatcher)
        
        # Check skill registry health
        skill_registry_health = await _check_skill_registry_health(dispatcher)
        
        # Check tool registry health  
        tool_registry_health = await _check_tool_registry_health(dispatcher)
        
        # Check LLM availability
        llm_health = await _check_llm_health()
        
        return HealthResponse(
            status=health.status.value,
            timestamp=health.timestamp.isoformat(),
            dispatcher_status={
                "overall": health.checks[0].details if health.checks else {},
                "agent_health": agent_health_status,
                "skill_registry": skill_registry_health,
                "tool_registry": tool_registry_health,
                "llm_availability": llm_health
            },
            context_loader_status={},
            registered_agents=len(dispatcher.registry.list_agents()) if dispatcher.registry else 0,
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
        context = await get_context_loader().load_context(
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
            task = get_dispatcher().dispatch(
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
        get_dispatcher().clear_history()

        return {
            "success": True,
            "message": "History cleared",
            "cleared_at": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Failed to clear history: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear history")


# Agent-specific health check helper functions
async def _check_agent_health(dispatcher) -> Dict[str, Any]:
    """Check health of individual agents."""
    try:
        if not dispatcher or not hasattr(dispatcher, 'registry'):
            return {"status": "unhealthy", "error": "Dispatcher not available"}
        
        agents = dispatcher.registry.list_agents() if dispatcher.registry else []
        healthy_agents = []
        unhealthy_agents = []
        
        for agent_name in agents:
            try:
                # Try to get agent instance and check health
                agent_info = dispatcher.get_agent_info(agent_name)
                if agent_info:
                    # Check if agent has required components
                    has_tools = bool(agent_info.get('tools', []))
                    has_skills = bool(agent_info.get('skills', []))
                    has_llm = agent_info.get('model_tier') is not None
                    
                    if has_tools and has_skills and has_llm:
                        healthy_agents.append(agent_name)
                    else:
                        unhealthy_agents.append({
                            "agent": agent_name,
                            "issues": [
                                "No tools" if not has_tools else None,
                                "No skills" if not has_skills else None,
                                "No LLM" if not has_llm else None
                            ]
                        })
                else:
                    unhealthy_agents.append({
                        "agent": agent_name,
                        "issues": ["Agent info not available"]
                    })
            except Exception as e:
                unhealthy_agents.append({
                    "agent": agent_name,
                    "issues": [f"Health check failed: {str(e)}"]
                })
        
        return {
            "status": "healthy" if len(unhealthy_agents) == 0 else "degraded",
            "total_agents": len(agents),
            "healthy_agents": len(healthy_agents),
            "unhealthy_agents": len(unhealthy_agents),
            "unhealthy_details": unhealthy_agents
        }
        
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


async def _check_skill_registry_health(dispatcher) -> Dict[str, Any]:
    """Check health of skill registry."""
    try:
        if not dispatcher or not hasattr(dispatcher, 'skills_registry'):
            return {"status": "unhealthy", "error": "Skills registry not available"}
        
        skills_registry = dispatcher.skills_registry
        if not skills_registry:
            return {"status": "unhealthy", "error": "Skills registry is None"}
        
        # Get all available skills
        try:
            all_skills = skills_registry.list_all_skills()
            skill_count = len(all_skills)
            
            # Check skill categories
            categories = set()
            for skill in all_skills:
                if hasattr(skill, 'category'):
                    categories.add(skill.category.value)
            
            return {
                "status": "healthy",
                "total_skills": skill_count,
                "categories": list(categories),
                "sample_skills": [skill.name for skill in all_skills[:5]]
            }
            
        except Exception as e:
            return {"status": "degraded", "error": f"Skills registry error: {str(e)}"}
            
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


async def _check_tool_registry_health(dispatcher) -> Dict[str, Any]:
    """Check health of tool registry."""
    try:
        if not dispatcher or not hasattr(dispatcher, 'tool_registry'):
            return {"status": "unhealthy", "error": "Tool registry not available"}
        
        tool_registry = dispatcher.tool_registry
        if not tool_registry:
            return {"status": "unhealthy", "error": "Tool registry is None"}
        
        # Get all available tools
        try:
            all_tools = tool_registry.list_tools()
            tool_count = len(all_tools)
            
            # Check critical tools
            critical_tools = ["database", "web_search", "file_system"]
            available_critical = []
            missing_critical = []
            
            for tool_name in critical_tools:
                tool = tool_registry.get(tool_name)
                if tool:
                    available_critical.append(tool_name)
                else:
                    missing_critical.append(tool_name)
            
            status = "healthy"
            if len(missing_critical) > 0:
                status = "degraded"
            if len(available_critical) == 0:
                status = "unhealthy"
            
            return {
                "status": status,
                "total_tools": tool_count,
                "critical_tools_available": available_critical,
                "critical_tools_missing": missing_critical,
                "sample_tools": [tool.name for tool in all_tools[:5]]
            }
            
        except Exception as e:
            return {"status": "degraded", "error": f"Tool registry error: {str(e)}"}
            
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


async def _check_llm_health() -> Dict[str, Any]:
    """Check LLM availability and configuration."""
    try:
        from agents.llm import get_llm, LLMManager
        
        # Try to get LLM instances for different tiers
        tiers = ["flash_lite", "flash", "pro"]
        tier_status = {}
        
        for tier in tiers:
            try:
                llm = get_llm(tier)
                if llm:
                    # Test basic functionality
                    if hasattr(llm, 'health_check'):
                        is_healthy = await llm.health_check()
                    else:
                        # Basic check - see if we can access the LLM
                        is_healthy = bool(llm)
                    
                    tier_status[tier] = {
                        "status": "healthy" if is_healthy else "unhealthy",
                        "available": bool(llm)
                    }
                else:
                    tier_status[tier] = {
                        "status": "unavailable",
                        "available": False
                    }
            except Exception as e:
                tier_status[tier] = {
                    "status": "error",
                    "available": False,
                    "error": str(e)
                }
        
        # Overall LLM health
        healthy_tiers = [t for t, status in tier_status.items() if status["status"] == "healthy"]
        overall_status = "healthy" if len(healthy_tiers) > 0 else "unhealthy"
        
        return {
            "status": overall_status,
            "tiers": tier_status,
            "healthy_tiers": healthy_tiers,
            "total_tiers": len(tiers)
        }
        
    except ImportError:
        return {"status": "unhealthy", "error": "LLM module not available"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
