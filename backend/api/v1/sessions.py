"""
Enhanced session management API endpoints for Raptorflow agents.
Includes comprehensive session analytics and performance tracking.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from ..core.metrics import get_analytics_manager
from ..core.performance import get_performance_optimizer
from ..core.session_manager import (
    Session,
    SessionStatus,
    SessionType,
    get_session_manager,
)
from ..core.sessions import get_session_manager as get_redis_session_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sessions", tags=["sessions"])


# Dependency for authentication
async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
) -> Optional[str]:
    """Extract user ID from credentials."""
    try:
        if credentials and credentials.credentials:
            # In a real implementation, this would validate the token
            # For now, return a simple user identifier
            return (
                credentials.credentials.split(":")[0]
                if ":" in credentials.credentials
                else credentials.credentials
            )
    except Exception as e:
        logger.error(f"Failed to extract user ID: {e}")
        return None


@router.post("/")
async def create_session(
    request_data: Dict[str, Any], user_id: str = Query(..., description="User ID")
):
    """Create a new enhanced session."""
    try:
        # Use Redis session manager for enhanced features
        session_manager = await get_redis_session_manager()

        # Validate required fields
        workspace_id = request_data.get("workspace_id")
        session_type = request_data.get("session_type", "chat")

        if not workspace_id:
            raise HTTPException(status_code=400, detail="workspace_id is required")

        # Convert session type
        try:
            session_type_enum = SessionType(session_type)
        except ValueError:
            raise HTTPException(
                status_code=400, detail=f"Invalid session type: {session_type}"
            )

        # Create enhanced session
        session_id = await session_manager.create_session(
            user_id=user_id,
            workspace_id=workspace_id,
            session_type=session_type_enum,
            initial_context=request_data.get("context"),
            metadata=request_data.get("metadata"),
        )

        # Record session creation metric
        analytics_manager = await get_analytics_manager()
        await analytics_manager.record_session_event(
            "session_created", 1, session_id, user_id, workspace_id
        )

        return {
            "status": "success",
            "data": {
                "session_id": session_id,
                "session_type": session_type_enum.value,
                "workspace_id": workspace_id,
                "user_id": user_id,
                "created_at": datetime.utcnow().isoformat(),
            },
            "message": f"Enhanced session created successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create session: {e}")
        raise HTTPException(status_code=500, detail="Failed to create session")


@router.get("/{session_id}")
async def get_session(
    session_id: str, user_id: str = Query(..., description="User ID")
):
    """Get session details."""
    try:
        session_manager = get_session_manager()
        session = session_manager.get_session(session_id)

        if not session:
            raise HTTPException(
                status_code=404, detail=f"Session {session_id} not found"
            )

        # Check if user owns this session
        if session.session_data.user_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="Access denied: Session belongs to different user",
            )

        return {
            "status": "success",
            "data": session.to_dict(),
            "message": f"Session retrieved successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get session: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve session")


@router.put("/{session_id}")
async def update_session(
    session_id: str,
    update_data: Dict[str, Any],
    user_id: str = Query(..., description="User ID"),
):
    """Update session context."""
    try:
        session_manager = get_session_manager()
        session = session_manager.get_session(session_id)

        if not session:
            raise HTTPException(
                status_code=404, detail=f"Session {session_id} not found"
            )

        # Check if user owns this session
        if session.session_data.user_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="Access denied: Session belongs to different user",
            )

        # Update session
        success = session_manager.update_session(
            session_id=session_id,
            context_update=update_data.get("context"),
            metadata_update=update_data.get("metadata"),
        )

        if not success:
            raise HTTPException(status_code=400, detail="Failed to update session")

        return {
            "status": "success",
            "data": session.to_dict(),
            "message": "Session updated successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update session: {e}")
        raise HTTPException(status_code=500, detail="Failed to update session")


@router.delete("/{session_id}")
async def terminate_session(
    session_id: str,
    user_id: str = Query(..., description="User ID"),
    reason: str = "User request",
):
    """Terminate a session."""
    try:
        session_manager = get_session_manager()
        session = session_manager.get_session(session_id)

        if not session:
            raise HTTPException(
                status_code=404, detail=f"Session {session_id} not found"
            )

        # Check if user owns this session
        if session.session_data.user_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="Access denied: Session belongs to different user",
            )

        # Terminate session
        success = session_manager.terminate_session(session_id, reason)

        if not success:
            raise HTTPException(status_code=400, detail="Failed to terminate session")

        return {
            "status": "success",
            "data": session.to_dict(),
            "message": f"Session terminated: {reason}",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to terminate session: {e}")
        raise HTTPException(status_code=500, detail="Failed to terminate session")


@router.get("/user/{user_id}")
async def get_user_sessions(user_id: str):
    """Get all sessions for a user."""
    try:
        session_manager = get_session_manager()
        session_ids = session_manager.get_user_sessions(user_id)

        sessions = []
        for session_id in session_ids:
            session = session_manager.get_session(session_id)
            if session:
                sessions.append(session.to_dict())

        return {
            "status": "success",
            "data": {
                "user_id": user_id,
                "sessions": sessions,
                "total_sessions": len(sessions),
            },
            "message": f"Retrieved {len(sessions)} sessions for user {user_id}",
        }

    except Exception as e:
        logger.error(f"Failed to get user sessions: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve user sessions")


@router.get("/workspace/{workspace_id}")
async def get_workspace_sessions(workspace_id: str):
    """Get all sessions in a workspace."""
    try:
        session_manager = get_session_manager()
        session_ids = session_manager.get_workspace_sessions(workspace_id)

        sessions = []
        for session_id in session_ids:
            session = session_manager.get_session(session_id)
            if session:
                sessions.append(session.to_dict())

        return {
            "status": "success",
            "data": {
                "workspace_id": workspace_id,
                "sessions": sessions,
                "total_sessions": len(sessions),
            },
            "message": f"Retrieved {len(sessions)} sessions for workspace {workspace_id}",
        }

    except Exception as e:
        logger.error(f"Failed to get workspace sessions: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve workspace sessions"
        )


@router.get("/types")
async def get_session_types():
    """Get available session types."""
    try:
        return {
            "status": "success",
            "data": [session_type.value for session_type in SessionType],
            "message": "Session types retrieved successfully",
        }
    except Exception as e:
        logger.error(f"Failed to get session types: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve session types")


@router.get("/analytics/dashboard")
async def get_dashboard_analytics(
    workspace_id: Optional[str] = Query(None),
    hours: int = Query(24, ge=1, le=168),
    user_id: str = Depends(get_current_user_id),
):
    """Get comprehensive dashboard analytics."""
    try:
        analytics_manager = await get_analytics_manager()
        dashboard_data = await analytics_manager.get_dashboard_analytics(
            workspace_id=workspace_id, hours=hours
        )

        return {
            "status": "success",
            "data": dashboard_data,
            "message": "Dashboard analytics retrieved successfully",
        }

    except Exception as e:
        logger.error(f"Failed to get dashboard analytics: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve dashboard analytics"
        )


@router.get("/analytics/user/{user_id}")
async def get_user_analytics(
    user_id: str,
    days: int = Query(30, ge=1, le=365),
    current_user_id: str = Query(..., description="Current User ID"),
):
    """Get user behavior analytics."""
    try:
        # Users can only access their own analytics
        if user_id != current_user_id:
            raise HTTPException(
                status_code=403,
                detail="Access denied: Cannot access other user analytics",
            )

        analytics_manager = await get_analytics_manager()
        user_pattern = await analytics_manager.session_analytics.analyze_user_behavior(
            user_id=user_id, days=days
        )

        if not user_pattern:
            raise HTTPException(
                status_code=404, detail="No user analytics data available"
            )

        return {
            "status": "success",
            "data": {
                "user_id": user_pattern.user_id,
                "session_frequency": user_pattern.session_frequency,
                "avg_session_duration": user_pattern.avg_session_duration,
                "peak_usage_hours": user_pattern.peak_usage_hours,
                "preferred_session_types": user_pattern.preferred_session_types,
                "feature_usage": user_pattern.feature_usage,
                "churn_risk": user_pattern.churn_risk,
                "engagement_score": user_pattern.engagement_score,
                "analysis_period_days": days,
            },
            "message": f"User analytics retrieved for {user_id}",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve user analytics")


@router.get("/analytics/performance")
async def get_performance_analytics(
    agent_name: Optional[str] = Query(None),
    workspace_id: Optional[str] = Query(None),
    hours: int = Query(24, ge=1, le=168),
    user_id: str = Query(..., description="User ID"),
):
    """Get performance analytics."""
    try:
        analytics_manager = await get_analytics_manager()
        performance_data = (
            await analytics_manager.performance_analytics.analyze_performance(
                agent_name=agent_name, workspace_id=workspace_id, hours=hours
            )
        )

        return {
            "status": "success",
            "data": performance_data,
            "message": "Performance analytics retrieved successfully",
        }

    except Exception as e:
        logger.error(f"Failed to get performance analytics: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve performance analytics"
        )


@router.get("/analytics/trends")
async def get_resource_trends(
    hours: int = Query(24, ge=1, le=168),
    user_id: str = Query(..., description="User ID"),
):
    """Get resource usage trends."""
    try:
        analytics_manager = await get_analytics_manager()
        trends_data = await analytics_manager.performance_analytics.get_resource_trends(
            hours=hours
        )

        return {
            "status": "success",
            "data": trends_data,
            "message": "Resource trends retrieved successfully",
        }

    except Exception as e:
        logger.error(f"Failed to get resource trends: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve resource trends"
        )


@router.get("/stats")
async def get_session_stats():
    """Get session manager statistics."""
    try:
        # Get both legacy and Redis session manager stats
        legacy_manager = get_session_manager()
        redis_manager = await get_redis_session_manager()

        legacy_stats = legacy_manager.get_session_stats()

        # Redis manager metrics
        redis_metrics = redis_manager.get_metrics()

        # Performance optimizer stats
        perf_optimizer = get_performance_optimizer()
        perf_stats = perf_optimizer.get_performance_stats()

        return {
            "status": "success",
            "data": {
                "legacy_session_manager": legacy_stats,
                "redis_session_manager": redis_metrics,
                "performance_optimizer": perf_stats,
                "system_health": "operational",
            },
            "message": "Comprehensive session statistics retrieved successfully",
        }

    except Exception as e:
        logger.error(f"Failed to get session stats: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve session statistics"
        )
