"""
Swarm Router

FastAPI endpoints for triggering and managing agent swarm workflows.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio

from backend.dependencies import get_db, get_redis, get_user
from backend.messaging.event_bus import EventBus
from backend.messaging.context_bus import ContextBus
from backend.messaging.agent_registry import AgentRegistry
from backend.orchestration.swarm_orchestrator import SwarmOrchestrator
from backend.workflows.move_creation_workflow import create_move_with_swarm


router = APIRouter(prefix="/api/v1/swarm", tags=["swarm"])


# ============================================================================
# Request/Response Models
# ============================================================================

class GoalRequest(BaseModel):
    """Request to create a move"""

    goal_type: str  # "reach", "engagement", "conversion", "revenue", etc.
    description: str
    cohorts: List[str] = []
    timeframe_days: int = 14
    intensity: str = "standard"  # light, standard, aggressive
    budget: Optional[float] = None


class WorkflowResponse(BaseModel):
    """Workflow execution response"""

    workflow_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class WorkflowStatus(BaseModel):
    """Workflow status"""

    workflow_id: str
    type: str
    status: str
    created_at: str
    started_at: Optional[str]
    completed_at: Optional[str]
    result: Optional[Dict[str, Any]]
    error: Optional[str]


class AgentStatus(BaseModel):
    """Agent status in registry"""

    agent_id: str
    agent_name: str
    status: str
    current_load: int
    max_concurrent: int
    load_percentage: float
    success_rate: float
    avg_latency_ms: float
    capabilities: List[str]
    pod: str


class SwarmStats(BaseModel):
    """Overall swarm statistics"""

    total_agents: int
    total_capacity: int
    total_load: int
    avg_success_rate: float
    available_agents: int
    agents_by_pod: Dict[str, int]


# ============================================================================
# WORKFLOW ENDPOINTS
# ============================================================================

@router.post("/workflows/move-creation", response_model=WorkflowResponse)
async def create_move_workflow(
    goal: GoalRequest,
    background_tasks: BackgroundTasks,
    db = Depends(get_db),
    redis_client = Depends(get_redis),
    current_user = Depends(get_user)
):
    """
    Create a marketing move using the full swarm

    This endpoint:
    1. Creates a workflow
    2. Fans out to multiple agents in parallel
    3. Handles conflict resolution
    4. Returns workflow ID immediately
    5. Executes in background

    Example:
        POST /api/v1/swarm/workflows/move-creation
        {
            "goal_type": "conversion",
            "description": "Q1 revenue push",
            "cohorts": ["founders", "marketing-leaders"],
            "timeframe_days": 14,
            "intensity": "standard"
        }
    """

    try:
        # Initialize orchestrator
        event_bus = EventBus(redis_client)
        context_bus = ContextBus(redis_client)
        registry = AgentRegistry(redis_client)

        orchestrator = SwarmOrchestrator(
            event_bus,
            context_bus,
            registry,
            db,
            None  # LLM client
        )

        # Create workflow
        workflow_id = await orchestrator.create_workflow(
            workflow_type="move_creation",
            goal=goal.model_dump(),
            user_id=current_user.id,
            workspace_id=current_user.workspace_id
        )

        # Execute in background
        background_tasks.add_task(
            _execute_workflow_background,
            orchestrator,
            workflow_id,
            goal
        )

        return WorkflowResponse(
            workflow_id=workflow_id,
            status="running",
            result=None
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflows/{workflow_id}/status", response_model=WorkflowStatus)
async def get_workflow_status(
    workflow_id: str,
    redis_client = Depends(get_redis),
    db = Depends(get_db)
):
    """
    Get workflow status and progress

    Example:
        GET /api/v1/swarm/workflows/wf_abc123/status
    """

    try:
        event_bus = EventBus(redis_client)
        context_bus = ContextBus(redis_client)
        registry = AgentRegistry(redis_client)

        orchestrator = SwarmOrchestrator(
            event_bus,
            context_bus,
            registry,
            db,
            None
        )

        status = orchestrator.get_workflow_status(workflow_id)

        if "error" in status:
            raise HTTPException(status_code=404, detail=status["error"])

        return WorkflowStatus(**status)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflows/{workflow_id}/cancel")
async def cancel_workflow(
    workflow_id: str,
    redis_client = Depends(get_redis),
    db = Depends(get_db)
):
    """
    Cancel a running workflow

    Example:
        POST /api/v1/swarm/workflows/wf_abc123/cancel
    """

    try:
        event_bus = EventBus(redis_client)
        context_bus = ContextBus(redis_client)
        registry = AgentRegistry(redis_client)

        orchestrator = SwarmOrchestrator(
            event_bus,
            context_bus,
            registry,
            db,
            None
        )

        workflow = orchestrator.workflows.get(workflow_id)
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")

        # Cancel workflow
        workflow["status"] = "cancelled"

        return {"status": "cancelled", "workflow_id": workflow_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# AGENT ENDPOINTS
# ============================================================================

@router.get("/agents", response_model=List[AgentStatus])
async def list_agents(
    redis_client = Depends(get_redis),
    pod: Optional[str] = None
):
    """
    List all registered agents

    Example:
        GET /api/v1/swarm/agents
        GET /api/v1/swarm/agents?pod=creation
    """

    try:
        registry = AgentRegistry(redis_client)

        if pod:
            agents = registry.list_agents_by_pod(pod)
        else:
            agents = registry.list_all_agents()

        return [
            AgentStatus(
                agent_id=agent.agent_id,
                agent_name=agent.agent_name,
                status="healthy" if agent.is_available else "busy",
                current_load=agent.current_load,
                max_concurrent=agent.max_concurrent,
                load_percentage=agent.load_percentage,
                success_rate=agent.success_rate,
                avg_latency_ms=agent.avg_latency_ms,
                capabilities=agent.capabilities,
                pod=agent.pod
            )
            for agent in agents
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents/{agent_id}", response_model=AgentStatus)
async def get_agent_status(
    agent_id: str,
    redis_client = Depends(get_redis)
):
    """
    Get status of a specific agent

    Example:
        GET /api/v1/swarm/agents/STRAT-01
    """

    try:
        registry = AgentRegistry(redis_client)
        agent = registry.get_agent(agent_id)

        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")

        return AgentStatus(
            agent_id=agent.agent_id,
            agent_name=agent.agent_name,
            status="healthy" if agent.is_available else "busy",
            current_load=agent.current_load,
            max_concurrent=agent.max_concurrent,
            load_percentage=agent.load_percentage,
            success_rate=agent.success_rate,
            avg_latency_ms=agent.avg_latency_ms,
            capabilities=agent.capabilities,
            pod=agent.pod
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# SWARM STATISTICS
# ============================================================================

@router.get("/stats", response_model=SwarmStats)
async def get_swarm_stats(redis_client = Depends(get_redis)):
    """
    Get overall swarm statistics

    Example:
        GET /api/v1/swarm/stats
    """

    try:
        registry = AgentRegistry(redis_client)
        stats = registry.get_registry_stats()

        return SwarmStats(**stats)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def swarm_health(redis_client = Depends(get_redis)):
    """
    Check swarm health

    Returns:
        - Green: All agents healthy
        - Yellow: Some agents degraded
        - Red: Critical issues
    """

    try:
        registry = AgentRegistry(redis_client)
        agents = registry.list_all_agents()

        if not agents:
            return {
                "status": "red",
                "message": "No agents registered",
                "agents_online": 0
            }

        available = sum(1 for a in agents if a.is_available)
        healthy = sum(1 for a in agents if a.success_rate > 0.8)

        total = len(agents)
        availability = available / total if total > 0 else 0

        if availability >= 0.8 and healthy >= total * 0.7:
            status = "green"
        elif availability >= 0.5:
            status = "yellow"
        else:
            status = "red"

        return {
            "status": status,
            "agents_online": available,
            "agents_total": total,
            "availability_percentage": availability * 100,
            "healthy_agents": healthy
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# BACKGROUND TASK
# ============================================================================

async def _execute_workflow_background(
    orchestrator: SwarmOrchestrator,
    workflow_id: str,
    goal: GoalRequest
):
    """Execute workflow in background"""

    try:
        await orchestrator.execute_workflow(
            workflow_id,
            create_move_with_swarm
        )
    except Exception as e:
        print(f"[Swarm] Workflow {workflow_id} failed: {e}")


# ============================================================================
# DEBUG ENDPOINTS (Dev only)
# ============================================================================

@router.post("/debug/trigger-agent")
async def debug_trigger_agent(
    agent_id: str,
    message_type: str,
    payload: Dict[str, Any],
    redis_client = Depends(get_redis)
):
    """
    Debug endpoint to manually trigger an agent

    Example:
        POST /api/v1/swarm/debug/trigger-agent
        {
            "agent_id": "STRAT-01",
            "message_type": "goal.request",
            "payload": {"goal_type": "conversion"}
        }
    """

    try:
        from backend.messaging.event_bus import AgentMessage, EventType

        event_bus = EventBus(redis_client)

        # Create message
        message = AgentMessage(
            type=EventType[message_type.upper().replace(".", "_")],
            origin="API",
            targets=[agent_id],
            payload=payload,
            correlation_id=f"debug_{agent_id}",
            priority="MEDIUM"
        )

        event_bus.publish(message)

        return {
            "status": "published",
            "agent_id": agent_id,
            "message_id": message.id
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/debug/message-history/{correlation_id}")
async def debug_message_history(
    correlation_id: str,
    redis_client = Depends(get_redis)
):
    """
    Debug endpoint to view message history for a workflow

    Example:
        GET /api/v1/swarm/debug/message-history/move_123
    """

    try:
        event_bus = EventBus(redis_client)
        history = event_bus.get_event_history(correlation_id)

        return {"correlation_id": correlation_id, "messages": history}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
