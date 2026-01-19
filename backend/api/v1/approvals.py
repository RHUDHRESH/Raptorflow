"""
Approval management API endpoints.
"""

import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from backend.agents.graphs.hitl import HITLGraph
from backend.core.auth import get_current_user
from backend.core.database import get_db

router = APIRouter(prefix="/approvals", tags=["approvals"])


class ApprovalListResponse(BaseModel):
    """Response model for listing pending approvals."""

    success: bool
    pending_approvals: List[Dict[str, Any]]
    total_count: int
    error: Optional[str]


class ApprovalResponse(BaseModel):
    """Response model for single approval."""

    success: bool
    approval: Optional[Dict[str, Any]]
    error: Optional[str]


class ApprovalDecisionRequest(BaseModel):
    """Request model for approval decision."""

    gate_id: str
    workspace_id: str
    user_id: str
    approved: bool = Field(..., description="Whether to approve or reject")
    reason: str = Field(default="", description="Reason for decision")
    approver_id: Optional[str] = Field(None, description="ID of the approver")


class ApprovalDecisionResponse(BaseModel):
    """Response model for approval decision."""

    success: bool
    gate_id: str
    approval_status: str
    approval_reason: str
    approval_timestamp: str
    pending_approval: bool
    error: Optional[str]


class ApprovalStatusResponse(BaseModel):
    """Response model for approval status."""

    success: bool
    gate_id: str
    approval_status: str
    approval_request: Dict[str, Any]
    approval_timestamp: Optional[str]
    pending_approval: bool
    error: Optional[str]


class ApprovalCreateRequest(BaseModel):
    """Request model for creating approval gate."""

    output: str = Field(..., description="Output requiring approval")
    workspace_id: str = Field(..., description="Workspace ID")
    user_id: str = Field(..., description="User ID")
    session_id: str = Field(..., description="Session ID")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")


class ApprovalCreateResponse(BaseModel):
    """Response model for creating approval gate."""

    success: bool
    gate_id: str
    risk_level: str
    approval_type: str
    approval_status: str
    timeout_duration: int
    approval_request: Dict[str, Any]
    pending_approval: bool
    error: Optional[str]


# Global instance
hitl_graph = HITLGraph()


@router.get("/pending", response_model=ApprovalListResponse)
async def list_pending_approvals(
    workspace_id: str,
    risk_level: Optional[str] = None,
    approval_type: Optional[str] = None,
    limit: int = Query(default=50, description="Maximum approvals to return"),
    offset: int = 0,
    current_user: Dict = Depends(get_current_user),
    db=Depends(get_db),
):
    """
    List all pending approvals for a workspace.

    Returns a paginated list of approval gates that are waiting for human review.
    """
    try:
        # Get pending approvals from HITL graph
        pending_approvals = await hitl_graph.get_pending_approvals(workspace_id)

        # Apply filters
        if risk_level:
            pending_approvals = [
                approval
                for approval in pending_approvals
                if approval.get("risk_level") == risk_level
            ]

        if approval_type:
            pending_approvals = [
                approval
                for approval in pending_approvals
                if approval.get("approval_type") == approval_type
            ]

        # Apply pagination
        total_count = len(pending_approvals)
        paginated_approvals = pending_approvals[offset : offset + limit]

        return ApprovalListResponse(
            success=True,
            pending_approvals=paginated_approvals,
            total_count=total_count,
            error=None,
        )

    except Exception as e:
        return ApprovalListResponse(
            success=False,
            pending_approvals=[],
            total_count=0,
            error=f"Failed to list pending approvals: {str(e)}",
        )


@router.post("/{gate_id}/approve", response_model=ApprovalDecisionResponse)
async def approve_request(
    gate_id: str,
    request: ApprovalDecisionRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict = Depends(get_current_user),
    db=Depends(get_db),
):
    """
    Approve a pending approval request.

    This endpoint processes an approval decision and continues the workflow.
    """
    try:
        # Process approval using HITL graph
        result = await hitl_graph.process_approval_response(
            gate_id=gate_id,
            workspace_id=request.workspace_id,
            session_id=request.session_id,
            approved=request.approved,
            reason=request.reason,
            approver_id=request.approver_id or request.user_id,
        )

        if not result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=f"Approval processing failed: {result.get('error')}",
            )

        # Update approval in database (async background task)
        background_tasks.add_task(
            update_approval_in_database,
            gate_id=gate_id,
            request=request,
            result=result,
            db=db,
        )

        return ApprovalDecisionResponse(
            success=True,
            gate_id=gate_id,
            approval_status=result.get("approval_status"),
            approval_reason=result.get("approval_reason", ""),
            approval_timestamp=result.get(
                "approval_timestamp", datetime.now().isoformat()
            ),
            pending_approval=result.get("pending_approval", False),
            error=None,
        )

    except HTTPException:
        raise
    except Exception as e:
        return ApprovalDecisionResponse(
            success=False,
            gate_id=gate_id,
            approval_status="error",
            approval_reason="",
            approval_timestamp="",
            pending_approval=False,
            error=f"Approval processing failed: {str(e)}",
        )


@router.post("/{gate_id}/reject", response_model=ApprovalDecisionResponse)
async def reject_request(
    gate_id: str,
    request: ApprovalDecisionRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict = Depends(get_current_user),
    db=Depends(get_db),
):
    """
    Reject a pending approval request.

    This endpoint processes a rejection and may trigger workflow revisions.
    """
    try:
        # Ensure approved is False for rejection
        request.approved = False

        # Process rejection using HITL graph
        result = await hitl_graph.process_approval_response(
            gate_id=gate_id,
            workspace_id=request.workspace_id,
            session_id=request.session_id,
            approved=False,
            reason=request.reason,
            approver_id=request.approver_id or request.user_id,
        )

        if not result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=f"Rejection processing failed: {result.get('error')}",
            )

        # Update approval in database (async background task)
        background_tasks.add_task(
            update_approval_in_database,
            gate_id=gate_id,
            request=request,
            result=result,
            db=db,
        )

        return ApprovalDecisionResponse(
            success=True,
            gate_id=gate_id,
            approval_status=result.get("approval_status"),
            approval_reason=result.get("approval_reason", ""),
            approval_timestamp=result.get(
                "approval_timestamp", datetime.now().isoformat()
            ),
            pending_approval=result.get("pending_approval", False),
            error=None,
        )

    except HTTPException:
        raise
    except Exception as e:
        return ApprovalDecisionResponse(
            success=False,
            gate_id=gate_id,
            approval_status="error",
            approval_reason="",
            approval_timestamp="",
            pending_approval=False,
            error=f"Rejection processing failed: {str(e)}",
        )


@router.get("/{gate_id}/status", response_model=ApprovalStatusResponse)
async def get_approval_status(
    gate_id: str,
    workspace_id: str,
    current_user: Dict = Depends(get_current_user),
    db=Depends(get_db),
):
    """
    Get the status of a specific approval gate.
    """
    try:
        # Query approval from database
        approval = await db.fetchrow(
            "SELECT * FROM approval_gates WHERE id = $1 AND workspace_id = $2",
            gate_id,
            workspace_id,
        )

        if not approval:
            return ApprovalStatusResponse(
                success=False,
                gate_id=gate_id,
                approval_status="not_found",
                approval_request={},
                approval_timestamp=None,
                pending_approval=False,
                error="Approval gate not found",
            )

        approval_data = dict(approval)

        return ApprovalStatusResponse(
            success=True,
            gate_id=gate_id,
            approval_status=approval_data.get("approval_status", "pending"),
            approval_request=approval_data.get("approval_request", {}),
            approval_timestamp=approval_data.get("approval_timestamp"),
            pending_approval=approval_data.get("approval_status") == "pending",
            error=None,
        )

    except Exception as e:
        return ApprovalStatusResponse(
            success=False,
            gate_id=gate_id,
            approval_status="error",
            approval_request={},
            approval_timestamp=None,
            pending_approval=False,
            error=f"Failed to get approval status: {str(e)}",
        )


@router.post("/create", response_model=ApprovalCreateResponse)
async def create_approval_gate(
    request: ApprovalCreateRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict = Depends(get_current_user),
    db=Depends(get_db),
):
    """
    Create a new approval gate for content requiring human review.

    This endpoint creates an approval gate and returns the gate information
    for workflow integration.
    """
    try:
        # Create approval gate using HITL graph
        result = await hitl_graph.create_approval_gate(
            output=request.output,
            workspace_id=request.workspace_id,
            user_id=request.user_id,
            session_id=request.session_id,
            context=request.context or {},
        )

        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=f"Approval gate creation failed: {result.get('error')}",
            )

        # Save approval gate to database (async background task)
        background_tasks.add_task(
            save_approval_gate_to_database,
            gate_id=result.get("gate_id"),
            request=request,
            result=result,
            db=db,
        )

        return ApprovalCreateResponse(
            success=True,
            gate_id=result.get("gate_id"),
            risk_level=result.get("risk_level"),
            approval_type=result.get("approval_type"),
            approval_status=result.get("approval_status"),
            timeout_duration=result.get("timeout_duration"),
            approval_request=result.get("approval_request"),
            pending_approval=result.get("pending_approval"),
            error=None,
        )

    except HTTPException:
        raise
    except Exception as e:
        return ApprovalCreateResponse(
            success=False,
            gate_id="",
            risk_level="",
            approval_type="",
            approval_status="error",
            timeout_duration=0,
            approval_request={},
            pending_approval=False,
            error=f"Approval gate creation failed: {str(e)}",
        )


@router.get("/history", response_model=Dict[str, Any])
async def get_approval_history(
    workspace_id: str,
    days: int = 30,
    status: Optional[str] = None,
    risk_level: Optional[str] = None,
    current_user: Dict = Depends(get_current_user),
    db=Depends(get_db),
):
    """
    Get approval history for a workspace.
    """
    try:
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # Query approval history
        query = """
            SELECT * FROM approval_gates
            WHERE workspace_id = $1 AND created_at BETWEEN $2 AND $3
        """
        params = [workspace_id, start_date, end_date]

        if status:
            query += " AND approval_status = $4"
            params.append(status)

        if risk_level:
            query += f" AND approval_request->>'risk_level' = ${len(params) + 1}"
            params.append(risk_level)

        query += " ORDER BY created_at DESC"

        approvals = await db.fetch(query, *params)

        # Calculate summary statistics
        total_approvals = len(approvals)
        approved_count = sum(1 for a in approvals if a["approval_status"] == "approved")
        rejected_count = sum(1 for a in approvals if a["approval_status"] == "rejected")
        pending_count = sum(1 for a in approvals if a["approval_status"] == "pending")

        return {
            "success": True,
            "approvals": [dict(approval) for approval in approvals],
            "summary": {
                "total_approvals": total_approvals,
                "approved_count": approved_count,
                "rejected_count": rejected_count,
                "pending_count": pending_count,
                "approval_rate": (
                    (approved_count / total_approvals * 100)
                    if total_approvals > 0
                    else 0
                ),
            },
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": days,
            },
        }

    except Exception as e:
        return {"success": False, "error": f"Failed to get approval history: {str(e)}"}


@router.get("/analytics", response_model=Dict[str, Any])
async def get_approval_analytics(
    workspace_id: str,
    days: int = 30,
    current_user: Dict = Depends(get_current_user),
    db=Depends(get_db),
):
    """
    Get analytics for approval performance.
    """
    try:
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # Get approval analytics
        analytics = await db.fetchrow(
            """
            SELECT
                COUNT(*) as total_approvals,
                COUNT(CASE WHEN approval_status = 'approved' THEN 1 END) as approved,
                COUNT(CASE WHEN approval_status = 'rejected' THEN 1 END) as rejected,
                COUNT(CASE WHEN approval_status = 'pending' THEN 1 END) as pending,
                AVG(EXTRACT(EPOCH FROM (approval_timestamp - created_at))/3600) as avg_approval_hours,
                COUNT(CASE WHEN approval_request->>'risk_level' = 'critical' THEN 1 END) as critical_count,
                COUNT(CASE WHEN approval_request->>'risk_level' = 'high' THEN 1 END) as high_count,
                COUNT(CASE WHEN approval_request->>'risk_level' = 'medium' THEN 1 END) as medium_count,
                COUNT(CASE WHEN approval_request->>'risk_level' = 'low' THEN 1 END) as low_count
            FROM approval_gates
            WHERE workspace_id = $1 AND created_at BETWEEN $2 AND $3
            """,
            workspace_id,
            start_date,
            end_date,
        )

        # Get approval type breakdown
        type_breakdown = await db.fetch(
            """
            SELECT
                approval_request->>'approval_type' as approval_type,
                COUNT(*) as count,
                COUNT(CASE WHEN approval_status = 'approved' THEN 1 END) as approved,
                COUNT(CASE WHEN approval_status = 'rejected' THEN 1 END) as rejected
            FROM approval_gates
            WHERE workspace_id = $1 AND created_at BETWEEN $2 AND $3
            GROUP BY approval_request->>'approval_type'
            ORDER BY count DESC
            """,
            workspace_id,
            start_date,
            end_date,
        )

        return {
            "success": True,
            "summary": dict(analytics) if analytics else {},
            "type_breakdown": [dict(record) for record in type_breakdown],
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": days,
            },
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to get approval analytics: {str(e)}",
        }


@router.delete("/{gate_id}", response_model=Dict[str, Any])
async def cancel_approval(
    gate_id: str,
    workspace_id: str,
    reason: str = "",
    current_user: Dict = Depends(get_current_user),
    db=Depends(get_db),
):
    """
    Cancel a pending approval gate.
    """
    try:
        # Check if approval exists and is pending
        approval = await db.fetchrow(
            "SELECT * FROM approval_gates WHERE id = $1 AND workspace_id = $2 AND approval_status = 'pending'",
            gate_id,
            workspace_id,
        )

        if not approval:
            raise HTTPException(
                status_code=404, detail="Pending approval gate not found"
            )

        # Update approval status to cancelled
        await db.execute(
            "UPDATE approval_gates SET approval_status = 'cancelled', cancellation_reason = $1, updated_at = NOW() WHERE id = $2",
            reason,
            gate_id,
        )

        return {"success": True, "message": "Approval gate cancelled successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to cancel approval: {str(e)}"
        )


# Helper functions
async def save_approval_gate_to_database(
    gate_id: str, request: ApprovalCreateRequest, result: Dict[str, Any], db
):
    """Save approval gate to database."""
    try:
        await db.execute(
            """
            INSERT INTO approval_gates (
                id, workspace_id, user_id, session_id, output,
                risk_level, approval_type, approval_status,
                approval_request, timeout_duration, pending_approval,
                created_at, updated_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, NOW(), NOW())
            """,
            gate_id,
            request.workspace_id,
            request.user_id,
            request.session_id,
            request.output,
            result.get("risk_level"),
            result.get("approval_type"),
            result.get("approval_status"),
            result.get("approval_request"),
            result.get("timeout_duration"),
            result.get("pending_approval"),
        )
    except Exception as e:
        print(f"Failed to save approval gate to database: {e}")


async def update_approval_in_database(
    gate_id: str, request: ApprovalDecisionRequest, result: Dict[str, Any], db
):
    """Update approval decision in database."""
    try:
        await db.execute(
            """
            UPDATE approval_gates SET
                approval_status = $1,
                approval_reason = $2,
                approver_id = $3,
                approval_timestamp = $4,
                pending_approval = $5,
                updated_at = NOW()
            WHERE id = $6
            """,
            result.get("approval_status"),
            result.get("approval_reason"),
            request.approver_id or request.user_id,
            result.get("approval_timestamp"),
            result.get("pending_approval"),
            gate_id,
        )
    except Exception as e:
        print(f"Failed to update approval in database: {e}")
