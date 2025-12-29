import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse

from core.auth import get_current_user, get_tenant_id
from models.api_models import BaseResponseModel
from models.notification_models import (
    NotificationChannel,
    NotificationPreferencesRequest,
    NotificationPriority,
    NotificationProcessRequest,
    NotificationScheduleRequest,
    NotificationSendRequest,
    NotificationTemplateRequest,
    NotificationType,
)
from services.notification_service import NotificationService, get_notification_service

logger = logging.getLogger("raptorflow.api.notifications")

router = APIRouter(prefix="/v1/notifications", tags=["notifications"])


@router.post("/send", response_model=BaseResponseModel)
async def send_notification(
    request: NotificationSendRequest,
    background_tasks: BackgroundTasks,
    tenant_id: UUID = Depends(get_tenant_id),
    _current_user: dict = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
):
    """Send a notification via specified channels and return delivery summary."""
    try:
        # Validate request
        if not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")

        if not request.recipients:
            raise HTTPException(
                status_code=400, detail="At least one recipient is required"
            )

        # Send notification
        result = await service.send_notification(
            workspace_id=str(tenant_id),
            message=request.message,
            subject=request.subject,
            recipients=request.recipients,
            channels=[c.value for c in request.channels],
            notification_type=request.type.value,
            priority=request.priority.value,
            metadata=request.metadata,
            template_id=request.template_id,
            template_variables=request.template_variables,
            user_id=_current_user.get("id"),
        )

        # Schedule real-time delivery via WebSocket/SSE
        if result.get("success"):
            notification_data = result["data"]
            background_tasks.add_task(
                _broadcast_notification_realtime,
                str(tenant_id),
                notification_data,
                request.recipients,
            )

        return BaseResponseModel(
            success=result.get("success", False),
            message=result.get("message", "Notification sent"),
            data=result.get("data"),
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")
        raise HTTPException(status_code=500, detail="Failed to send notification")


@router.post("/schedule", response_model=BaseResponseModel)
async def schedule_notification(
    request: NotificationScheduleRequest,
    tenant_id: UUID = Depends(get_tenant_id),
    _current_user: dict = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
):
    """Schedule a notification for future delivery."""
    try:
        # Validate scheduling time
        if request.scheduled_at <= datetime.utcnow():
            raise HTTPException(
                status_code=400, detail="Scheduled time must be in the future"
            )

        # Validate frequency and end date
        if request.frequency != "once" and not request.end_date:
            raise HTTPException(
                status_code=400,
                detail="End date is required for recurring notifications",
            )

        # Schedule notification
        result = await service.schedule_notification(
            workspace_id=str(tenant_id),
            notification_data=request.notification_data,
            recipients=request.recipients,
            channels=[c.value for c in request.channels],
            scheduled_at=request.scheduled_at,
            frequency=request.frequency.value,
            end_date=request.end_date,
            max_occurrences=request.max_occurrences,
            timezone=request.timezone,
            business_hours_only=request.business_hours_only,
            retry_failed=request.retry_failed,
            max_retries=request.max_retries,
            user_id=_current_user.get("id"),
        )

        return BaseResponseModel(
            success=result.get("success", False),
            message=result.get("message", "Notification scheduled"),
            data=result.get("data"),
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to schedule notification: {e}")
        raise HTTPException(status_code=500, detail="Failed to schedule notification")


@router.get("/preferences", response_model=BaseResponseModel)
async def get_notification_preferences(
    user_id: Optional[str] = Query(None),
    tenant_id: UUID = Depends(get_tenant_id),
    _current_user: dict = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
):
    """Return user preferences and global settings."""
    try:
        # Use current user if no specific user_id provided
        target_user_id = user_id or _current_user.get("id")

        result = await service.get_notification_preferences(
            workspace_id=str(tenant_id), user_id=target_user_id
        )

        return BaseResponseModel(
            success=result.get("success", False),
            message="Preferences retrieved",
            data=result.get("data"),
        )

    except Exception as e:
        logger.error(f"Failed to get preferences: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve preferences")


@router.post("/preferences", response_model=BaseResponseModel)
async def update_notification_preferences(
    preferences: NotificationPreferencesRequest,
    tenant_id: UUID = Depends(get_tenant_id),
    _current_user: dict = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
):
    """Update user notification preferences."""
    try:
        # Store preferences in database
        from db import get_db_connection

        async with get_db_connection() as conn:
            async with conn.cursor() as cur:
                # Upsert preferences
                query = """
                    INSERT INTO notification_preferences (
                        workspace_id, tenant_id, user_id, email_notifications,
                        sms_notifications, push_notifications, in_app_notifications,
                        business_hours_only, quiet_hours_enabled, quiet_hours_start,
                        quiet_hours_end, timezone, notification_types
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (workspace_id, user_id)
                    DO UPDATE SET
                        email_notifications = EXCLUDED.email_notifications,
                        sms_notifications = EXCLUDED.sms_notifications,
                        push_notifications = EXCLUDED.push_notifications,
                        in_app_notifications = EXCLUDED.in_app_notifications,
                        business_hours_only = EXCLUDED.business_hours_only,
                        quiet_hours_enabled = EXCLUDED.quiet_hours_enabled,
                        quiet_hours_start = EXCLUDED.quiet_hours_start,
                        quiet_hours_end = EXCLUDED.quiet_hours_end,
                        timezone = EXCLUDED.timezone,
                        notification_types = EXCLUDED.notification_types,
                        updated_at = NOW()
                    RETURNING id
                """

                await cur.execute(
                    query,
                    (
                        str(tenant_id),
                        str(tenant_id),
                        _current_user.get("id"),
                        preferences.email_notifications,
                        preferences.sms_notifications,
                        preferences.push_notifications,
                        preferences.in_app_notifications,
                        preferences.business_hours_only,
                        preferences.quiet_hours_enabled,
                        preferences.quiet_hours_start,
                        preferences.quiet_hours_end,
                        preferences.timezone,
                        preferences.notification_types,
                    ),
                )

        return BaseResponseModel(
            success=True,
            message="Preferences updated successfully",
            data={"preferences": preferences.dict()},
        )

    except Exception as e:
        logger.error(f"Failed to update preferences: {e}")
        raise HTTPException(status_code=500, detail="Failed to update preferences")


@router.post("/templates", response_model=BaseResponseModel)
async def manage_notification_templates(
    request: NotificationTemplateRequest,
    tenant_id: UUID = Depends(get_tenant_id),
    _current_user: dict = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
):
    """Manage notification templates via list/create/update operations."""
    try:
        # Validate request based on action
        if request.action == "create":
            if not request.name or not request.content:
                raise HTTPException(
                    status_code=400,
                    detail="Name and content are required for template creation",
                )
            if not request.channel:
                raise HTTPException(
                    status_code=400, detail="Channel is required for template creation"
                )

        elif request.action == "update":
            if not request.template_id:
                raise HTTPException(
                    status_code=400,
                    detail="Template ID is required for template update",
                )

        # Manage templates
        result = await service.manage_notification_templates(
            workspace_id=str(tenant_id),
            action=request.action,
            template_data=request.dict(exclude_none=True),
            user_id=_current_user.get("id"),
        )

        return BaseResponseModel(
            success=result.get("success", False),
            message=f"Template {request.action} completed",
            data=result.get("data"),
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to manage templates: {e}")
        raise HTTPException(status_code=500, detail="Failed to manage templates")


@router.get("/analytics", response_model=BaseResponseModel)
async def get_notification_analytics(
    period: str = Query("30_days", regex="^(24_hours|7_days|30_days|90_days)$"),
    tenant_id: UUID = Depends(get_tenant_id),
    _current_user: dict = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
):
    """Return analytics summary, channel performance, engagement metrics, and insights."""
    try:
        result = await service.get_notification_analytics(
            workspace_id=str(tenant_id), period=period
        )

        return BaseResponseModel(
            success=result.get("success", False),
            message="Analytics retrieved",
            data=result.get("data"),
        )

    except Exception as e:
        logger.error(f"Failed to get analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve analytics")


@router.post("/process", response_model=BaseResponseModel)
async def process_signal_notifications(
    request: NotificationProcessRequest,
    background_tasks: BackgroundTasks,
    tenant_id: UUID = Depends(get_tenant_id),
    _current_user: dict = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
):
    """Process radar signal IDs and generate top alerts."""
    try:
        if not request.signal_ids:
            raise HTTPException(status_code=400, detail="Signal IDs are required")

        # Process notifications
        notifications = await service.process_signal_notifications(
            workspace_id=str(tenant_id),
            signal_ids=request.signal_ids,
            tenant_preferences=request.tenant_preferences,
        )

        # Schedule real-time delivery for generated notifications
        for notification in notifications:
            recipients = notification.get("recipients", [])
            if recipients:
                background_tasks.add_task(
                    _broadcast_notification_realtime,
                    str(tenant_id),
                    notification,
                    recipients,
                )

        return BaseResponseModel(
            success=True,
            message=f"Processed {len(request.signal_ids)} signals, generated {len(notifications)} notifications",
            data={
                "processed_signals": len(request.signal_ids),
                "generated_notifications": len(notifications),
                "notifications": notifications,
            },
        )

    except Exception as e:
        logger.error(f"Failed to process signal notifications: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to process signal notifications"
        )


@router.get("/digest/daily", response_model=BaseResponseModel)
async def get_daily_digest(
    tenant_id: UUID = Depends(get_tenant_id),
    _current_user: dict = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
):
    """Return the daily digest of signals and notifications."""
    try:
        digest = await service.get_daily_digest(workspace_id=str(tenant_id))

        return BaseResponseModel(
            success=True, message="Daily digest retrieved", data=digest
        )

    except Exception as e:
        logger.error(f"Failed to get daily digest: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve daily digest")


@router.get("/my", response_model=BaseResponseModel)
async def get_my_notifications(
    status: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    tenant_id: UUID = Depends(get_tenant_id),
    _current_user: dict = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
):
    """Get notifications for the current user with pagination."""
    try:
        result = await service.get_user_notifications(
            workspace_id=str(tenant_id),
            user_id=_current_user.get("id"),
            status=status,
            type=type,
            limit=limit,
            offset=offset,
        )

        return BaseResponseModel(
            success=True, message="Notifications retrieved", data=result
        )

    except Exception as e:
        logger.error(f"Failed to get user notifications: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve notifications")


@router.post("/{notification_id}/read", response_model=BaseResponseModel)
async def mark_notification_read(
    notification_id: str,
    tenant_id: UUID = Depends(get_tenant_id),
    _current_user: dict = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
):
    """Mark a notification as read."""
    try:
        success = await service.mark_notification_read(
            workspace_id=str(tenant_id),
            notification_id=notification_id,
            user_id=_current_user.get("id"),
        )

        if not success:
            raise HTTPException(status_code=404, detail="Notification not found")

        return BaseResponseModel(success=True, message="Notification marked as read")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to mark notification as read: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to mark notification as read"
        )


@router.get("/stream")
async def notification_stream(
    tenant_id: UUID = Depends(get_tenant_id),
    _current_user: dict = Depends(get_current_user),
):
    """Server-Sent Events endpoint for real-time notification delivery."""

    async def event_generator():
        """Generate SSE events for notifications."""
        try:
            # Store connection in active connections
            connection_id = f"{tenant_id}_{_current_user.get('id')}"
            _active_connections[connection_id] = asyncio.Queue()

            # Send initial connection event
            yield {
                "event": "connected",
                "data": json.dumps(
                    {
                        "message": "Connected to notification stream",
                        "user_id": _current_user.get("id"),
                        "workspace_id": str(tenant_id),
                    }
                ),
            }

            # Keep connection alive and send notifications
            while True:
                try:
                    # Wait for notification or heartbeat
                    queue = _active_connections[connection_id]
                    notification = await asyncio.wait_for(queue.get(), timeout=30.0)

                    yield {"event": "notification", "data": json.dumps(notification)}

                except asyncio.TimeoutError:
                    # Send heartbeat
                    yield {
                        "event": "heartbeat",
                        "data": json.dumps(
                            {"timestamp": datetime.utcnow().isoformat()}
                        ),
                    }

        except Exception as e:
            logger.error(f"SSE stream error: {e}")
        finally:
            # Clean up connection
            if connection_id in _active_connections:
                del _active_connections[connection_id]

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        },
    )


# Global storage for active SSE connections
_active_connections: Dict[str, asyncio.Queue] = {}


async def _broadcast_notification_realtime(
    workspace_id: str, notification: Dict[str, Any], recipients: List[str]
):
    """Broadcast notification to relevant users via SSE."""

    for recipient in recipients:
        connection_id = f"{workspace_id}_{recipient}"

        if connection_id in _active_connections:
            try:
                # Add notification to user's queue
                await _active_connections[connection_id].put(
                    {
                        "notification": notification,
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )

                logger.info(f"Broadcasted notification to user {recipient}")

            except Exception as e:
                logger.error(f"Failed to broadcast notification to {recipient}: {e}")
                # Remove broken connection
                if connection_id in _active_connections:
                    del _active_connections[connection_id]


# WebSocket alternative (for future implementation)
@router.websocket("/ws/{workspace_id}")
async def websocket_endpoint(websocket, workspace_id: str):
    """WebSocket endpoint for real-time notifications."""
    await websocket.accept()

    try:
        # Authenticate user (would need to pass token in query params)
        # For now, just accept connection

        while True:
            # Keep connection alive
            try:
                await websocket.receive_text()
            except:
                break

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await websocket.close()
