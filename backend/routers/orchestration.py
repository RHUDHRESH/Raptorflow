"""
Orchestration Router - API endpoints for master workflow orchestration.
Coordinates end-to-end workflows across all domain graphs.
"""

import structlog
from typing import Annotated, Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from backend.utils.auth import get_current_user_and_workspace
try:
    from backend.graphs.master_graph import master_graph_runnable, MasterGraphState, WorkflowGoal
except ImportError:
    logger.warning("Could not import master_graph, using mocks. Orchestration will not work.")
    from enum import Enum
    class WorkflowGoal(str, Enum):
        FULL_CAMPAIGN = "full_campaign"
        RESEARCH_ONLY = "research_only"
        STRATEGY_ONLY = "strategy_only"
        CONTENT_ONLY = "content_only"
        PUBLISH = "publish"
        ONBOARD = "onboard"
    
    MasterGraphState = Dict[str, Any]
    
    class MockRunnable:
        async def ainvoke(self, *args, **kwargs):
            raise NotImplementedError("Master graph not available")
    master_graph_runnable = MockRunnable()
from backend.services.supabase_client import supabase_client
from backend.utils.correlation import generate_correlation_id

router = APIRouter(prefix="/orchestration", tags=["Orchestration"])
logger = structlog.get_logger(__name__)


# --- Request/Response Models ---

class WorkflowExecuteRequest(BaseModel):
    """Request to execute a workflow."""
    goal: WorkflowGoal = Field(..., description="Workflow goal/objective")

    # Optional IDs for resuming or building on existing data
    onboarding_session_id: Optional[str] = None
    icp_id: Optional[UUID] = None
    strategy_id: Optional[UUID] = None
    content_ids: Optional[List[UUID]] = None

    # Domain-specific parameters
    research_query: Optional[str] = Field(None, description="Specific research query or industry")
    research_mode: Optional[str] = Field("quick", description="Research depth: 'quick' or 'deep'")
    strategy_mode: Optional[str] = Field("quick", description="Strategy mode: 'quick' or 'comprehensive'")
    content_type: Optional[str] = Field(None, description="Content type: blog, email, social_post, etc.")
    content_params: Optional[Dict[str, Any]] = Field(None, description="Additional content generation parameters")
    publish_platforms: Optional[List[str]] = Field(None, description="Platforms to publish to: linkedin, twitter, etc.")

    class Config:
        json_schema_extra = {
            "example": {
                "goal": "full_campaign",
                "research_query": "B2B SaaS startups",
                "research_mode": "deep",
                "strategy_mode": "comprehensive",
                "content_type": "blog",
                "content_params": {
                    "topic": "How to scale SaaS sales",
                    "tone": "professional",
                    "length": "long"
                },
                "publish_platforms": ["linkedin"]
            }
        }


class WorkflowStatusResponse(BaseModel):
    """Workflow execution status."""
    workflow_id: str
    correlation_id: str
    goal: str
    current_stage: str
    completed_stages: List[str]
    failed_stages: List[str]
    success: bool
    message: Optional[str]
    started_at: str
    completed_at: Optional[str]

    # Results from each stage
    onboarding_result: Optional[Dict[str, Any]] = None
    research_result: Optional[Dict[str, Any]] = None
    strategy_result: Optional[Dict[str, Any]] = None
    content_result: Optional[Dict[str, Any]] = None
    critic_review: Optional[Dict[str, Any]] = None
    integration_result: Optional[Dict[str, Any]] = None
    execution_result: Optional[Dict[str, Any]] = None

    errors: List[Dict[str, str]] = []


class WorkflowListResponse(BaseModel):
    """List of workflows."""
    workflows: List[Dict[str, Any]]
    total: int


# --- Endpoints ---

@router.post(
    "/execute",
    response_model=WorkflowStatusResponse,
    summary="Execute Workflow",
    description="Execute an end-to-end marketing workflow across multiple domain graphs"
)
async def execute_workflow(
    request: WorkflowExecuteRequest,
    auth: Annotated[dict, Depends(get_current_user_and_workspace)]
):
    """
    Execute a complete workflow based on the specified goal.

    **Workflow Goals:**
    - `full_campaign`: Complete end-to-end campaign (research → strategy → content → publish → analytics)
    - `research_only`: Generate ICP and customer intelligence only
    - `strategy_only`: Generate marketing strategy (requires ICP)
    - `content_only`: Generate content (requires strategy)
    - `publish`: Publish existing content to platforms
    - `onboard`: Just onboarding questionnaire

    **Features:**
    - Automatic correlation ID tracking across all stages
    - Content safety review with critic agent
    - Conditional branching based on goal
    - Retry logic for failed stages
    - Comprehensive error handling
    """
    user_id = auth["user_id"]
    workspace_id = auth["workspace_id"]
    correlation_id = generate_correlation_id()

    logger.info(
        "Executing workflow",
        workspace_id=workspace_id,
        goal=request.goal,
        correlation_id=correlation_id
    )

    try:
        # Build initial state
        initial_state: MasterGraphState = {
            "correlation_id": correlation_id,
            "workflow_id": str(UUID(int=0)),  # Will be generated in initialize node
            "workspace_id": str(workspace_id),
            "user_id": str(user_id),
            "goal": request.goal,
            "current_stage": "pending",
            "completed_stages": [],
            "failed_stages": [],
            "started_at": "",
            "completed_at": None,

            # Optional IDs
            "onboarding_session_id": request.onboarding_session_id,
            "icp_id": str(request.icp_id) if request.icp_id else None,
            "strategy_id": str(request.strategy_id) if request.strategy_id else None,
            "content_ids": [str(cid) for cid in request.content_ids] if request.content_ids else None,

            # Domain parameters
            "research_query": request.research_query,
            "research_mode": request.research_mode,
            "strategy_mode": request.strategy_mode,
            "content_type": request.content_type,
            "content_params": request.content_params,
            "publish_platforms": request.publish_platforms,

            # Results (will be populated by graphs)
            "onboarding_result": None,
            "research_result": None,
            "strategy_result": None,
            "content_result": None,
            "critic_review": None,
            "integration_result": None,
            "execution_result": None,

            # Error handling
            "errors": [],
            "retry_count": 0,

            # Output
            "success": False,
            "message": None
        }

        # Execute master graph
        logger.info("Invoking master graph", correlation_id=correlation_id)
        final_state = await master_graph_runnable.ainvoke(
            initial_state,
            config={"configurable": {"thread_id": correlation_id}}
        )

        # Store workflow execution record
        workflow_data = {
            "workflow_id": final_state["workflow_id"],
            "workspace_id": str(workspace_id),
            "user_id": str(user_id),
            "correlation_id": correlation_id,
            "goal": request.goal,
            "current_stage": final_state["current_stage"],
            "completed_stages": final_state["completed_stages"],
            "failed_stages": final_state["failed_stages"],
            "success": final_state["success"],
            "message": final_state.get("message"),
            "started_at": final_state["started_at"],
            "completed_at": final_state.get("completed_at"),
            "errors": final_state["errors"],
            "results": {
                "onboarding": final_state.get("onboarding_result"),
                "research": final_state.get("research_result"),
                "strategy": final_state.get("strategy_result"),
                "content": final_state.get("content_result"),
                "critic": final_state.get("critic_review"),
                "integration": final_state.get("integration_result"),
                "execution": final_state.get("execution_result")
            }
        }

        # Save to database
        try:
            await supabase_client.insert("workflow_executions", workflow_data)
        except Exception as db_error:
            logger.warning(f"Failed to save workflow to DB: {db_error}", correlation_id=correlation_id)
            # Continue even if DB save fails

        logger.info(
            "Workflow completed",
            workflow_id=final_state["workflow_id"],
            success=final_state["success"],
            completed_stages=len(final_state["completed_stages"]),
            failed_stages=len(final_state["failed_stages"]),
            correlation_id=correlation_id
        )

        # Return response
        return WorkflowStatusResponse(
            workflow_id=final_state["workflow_id"],
            correlation_id=correlation_id,
            goal=request.goal,
            current_stage=final_state["current_stage"],
            completed_stages=final_state["completed_stages"],
            failed_stages=final_state["failed_stages"],
            success=final_state["success"],
            message=final_state.get("message"),
            started_at=final_state["started_at"],
            completed_at=final_state.get("completed_at"),
            onboarding_result=final_state.get("onboarding_result"),
            research_result=final_state.get("research_result"),
            strategy_result=final_state.get("strategy_result"),
            content_result=final_state.get("content_result"),
            critic_review=final_state.get("critic_review"),
            integration_result=final_state.get("integration_result"),
            execution_result=final_state.get("execution_result"),
            errors=final_state["errors"]
        )

    except Exception as e:
        logger.error(f"Workflow execution failed: {e}", correlation_id=correlation_id, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Workflow execution failed: {str(e)}"
        )


@router.get(
    "/workflows",
    response_model=WorkflowListResponse,
    summary="List Workflows",
    description="List all workflow executions for the workspace"
)
async def list_workflows(
    auth: Annotated[dict, Depends(get_current_user_and_workspace)],
    limit: int = 20,
    offset: int = 0
):
    """
    List all workflow executions for the current workspace.
    """
    workspace_id = auth["workspace_id"]

    logger.info("Listing workflows", workspace_id=workspace_id, limit=limit, offset=offset)

    try:
        # Query workflows from database
        workflows = await supabase_client.query(
            "workflow_executions",
            filters={"workspace_id": str(workspace_id)},
            limit=limit,
            offset=offset,
            order_by="created_at.desc"
        )

        # Get total count
        count_result = await supabase_client.count(
            "workflow_executions",
            filters={"workspace_id": str(workspace_id)}
        )

        total = count_result if isinstance(count_result, int) else len(workflows)

        return WorkflowListResponse(
            workflows=workflows,
            total=total
        )

    except Exception as e:
        logger.error(f"Failed to list workflows: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list workflows: {str(e)}"
        )


@router.get(
    "/workflows/{workflow_id}",
    response_model=WorkflowStatusResponse,
    summary="Get Workflow Status",
    description="Get detailed status of a specific workflow execution"
)
async def get_workflow_status(
    workflow_id: str,
    auth: Annotated[dict, Depends(get_current_user_and_workspace)]
):
    """
    Get detailed status and results of a specific workflow execution.
    """
    workspace_id = auth["workspace_id"]

    logger.info("Getting workflow status", workflow_id=workflow_id, workspace_id=workspace_id)

    try:
        # Query workflow from database
        workflow = await supabase_client.query_one(
            "workflow_executions",
            filters={
                "workflow_id": workflow_id,
                "workspace_id": str(workspace_id)
            }
        )

        if not workflow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workflow {workflow_id} not found"
            )

        # Extract results
        results = workflow.get("results", {})

        return WorkflowStatusResponse(
            workflow_id=workflow["workflow_id"],
            correlation_id=workflow["correlation_id"],
            goal=workflow["goal"],
            current_stage=workflow["current_stage"],
            completed_stages=workflow["completed_stages"],
            failed_stages=workflow["failed_stages"],
            success=workflow["success"],
            message=workflow.get("message"),
            started_at=workflow["started_at"],
            completed_at=workflow.get("completed_at"),
            onboarding_result=results.get("onboarding"),
            research_result=results.get("research"),
            strategy_result=results.get("strategy"),
            content_result=results.get("content"),
            critic_review=results.get("critic"),
            integration_result=results.get("integration"),
            execution_result=results.get("execution"),
            errors=workflow.get("errors", [])
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get workflow status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get workflow status: {str(e)}"
        )


@router.post(
    "/workflows/{workflow_id}/retry",
    response_model=WorkflowStatusResponse,
    summary="Retry Failed Workflow",
    description="Retry a failed workflow from the last successful stage"
)
async def retry_workflow(
    workflow_id: str,
    auth: Annotated[dict, Depends(get_current_user_and_workspace)]
):
    """
    Retry a failed workflow from the last successful stage.
    """
    workspace_id = auth["workspace_id"]
    correlation_id = generate_correlation_id()

    logger.info(
        "Retrying workflow",
        workflow_id=workflow_id,
        workspace_id=workspace_id,
        correlation_id=correlation_id
    )

    try:
        # Get original workflow
        original_workflow = await supabase_client.query_one(
            "workflow_executions",
            filters={
                "workflow_id": workflow_id,
                "workspace_id": str(workspace_id)
            }
        )

        if not original_workflow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workflow {workflow_id} not found"
            )

        if original_workflow["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot retry a successful workflow"
            )

        # TODO: Implement retry logic by reconstructing initial state
        # and resuming from the last successful stage

        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Retry functionality coming soon"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retry workflow: {e}", correlation_id=correlation_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retry workflow: {str(e)}"
        )
