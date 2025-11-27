# backend/routers/herald.py
# RaptorFlow Codex - Herald Lord API Endpoints
# Phase 2A Week 7 - Communications & Announcements

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
import logging
from datetime import datetime

from backend_lord_herald import HeraldLord
from dependencies import get_current_user, get_current_workspace

logger = logging.getLogger(__name__)

# Get Herald instance (singleton)
herald: Optional[HeraldLord] = None

async def get_herald() -> HeraldLord:
    """Get or initialize Herald Lord"""
    global herald
    if herald is None:
        herald = HeraldLord()
        await herald.initialize()
    return herald

router = APIRouter(prefix="/lords/herald", tags=["Herald Lord"])

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class SendMessageRequest(BaseModel):
    """Send message request"""
    channel: str
    recipient: str
    subject: str
    content: str
    priority: str = "normal"
    metadata: Dict[str, Any] = {}

class ScheduleAnnouncementRequest(BaseModel):
    """Schedule announcement request"""
    title: str
    content: str
    scope: str
    scope_id: str
    channels: List[str]
    scheduled_at: str
    recipients_count: int = 0

class CreateTemplateRequest(BaseModel):
    """Create message template request"""
    name: str
    template_type: str
    subject_template: str
    content_template: str
    variables: List[str] = []

class TrackDeliveryRequest(BaseModel):
    """Track delivery request"""
    message_id: Optional[str] = None
    announcement_id: Optional[str] = None
    period_days: int = 7

class GetReportRequest(BaseModel):
    """Get communication report request"""
    period_days: int = 30

# ============================================================================
# MESSAGE ENDPOINTS
# ============================================================================

@router.post("/messages/send", response_model=Dict[str, Any])
async def send_message(
    request: SendMessageRequest,
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    herald_lord: HeraldLord = Depends(get_herald)
):
    """
    Send a message through specified channel.

    The Herald Lord sends messages via email, SMS, push notifications,
    or other configured channels with priority-based handling.
    """
    logger.info(f"📨 Sending message to {request.recipient} via {request.channel}")

    try:
        result = await herald_lord.execute(
            task="send_message",
            parameters={
                "channel": request.channel,
                "recipient": request.recipient,
                "subject": request.subject,
                "content": request.content,
                "priority": request.priority,
                "metadata": request.metadata,
            }
        )

        if result.get("success", True):
            return {
                "status": "success",
                "data": result,
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Message sending failed")
            )

    except Exception as e:
        logger.error(f"❌ Message sending error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/messages", response_model=List[Dict[str, Any]])
async def get_messages(
    limit: int = 10,
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    herald_lord: HeraldLord = Depends(get_herald)
):
    """Get recent sent messages."""
    return await herald_lord.get_recent_messages(limit=limit)

@router.get("/messages/{message_id}", response_model=Dict[str, Any])
async def get_message(
    message_id: str,
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    herald_lord: HeraldLord = Depends(get_herald)
):
    """Get message details."""
    if message_id not in herald_lord.messages:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Message {message_id} not found"
        )

    return herald_lord.messages[message_id].to_dict()

# ============================================================================
# ANNOUNCEMENT ENDPOINTS
# ============================================================================

@router.post("/announcements/schedule", response_model=Dict[str, Any])
async def schedule_announcement(
    request: ScheduleAnnouncementRequest,
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    herald_lord: HeraldLord = Depends(get_herald)
):
    """
    Schedule an announcement.

    The Herald Lord schedules announcements across organization, guild, campaign,
    or individual scope with multi-channel support.
    """
    logger.info(f"📢 Scheduling announcement: {request.title}")

    try:
        result = await herald_lord.execute(
            task="schedule_announcement",
            parameters={
                "title": request.title,
                "content": request.content,
                "scope": request.scope,
                "scope_id": request.scope_id,
                "channels": request.channels,
                "scheduled_at": request.scheduled_at,
                "recipients_count": request.recipients_count,
            }
        )

        if result.get("success", True):
            return {
                "status": "success",
                "data": result,
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Announcement scheduling failed")
            )

    except Exception as e:
        logger.error(f"❌ Announcement scheduling error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/announcements", response_model=List[Dict[str, Any]])
async def get_announcements(
    limit: int = 10,
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    herald_lord: HeraldLord = Depends(get_herald)
):
    """Get recent announcements."""
    return await herald_lord.get_recent_announcements(limit=limit)

@router.get("/announcements/{announcement_id}", response_model=Dict[str, Any])
async def get_announcement(
    announcement_id: str,
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    herald_lord: HeraldLord = Depends(get_herald)
):
    """Get announcement details."""
    if announcement_id not in herald_lord.announcements:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Announcement {announcement_id} not found"
        )

    return herald_lord.announcements[announcement_id].to_dict()

# ============================================================================
# TEMPLATE ENDPOINTS
# ============================================================================

@router.post("/templates/create", response_model=Dict[str, Any])
async def create_template(
    request: CreateTemplateRequest,
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    herald_lord: HeraldLord = Depends(get_herald)
):
    """
    Create a message template.

    Templates support variable substitution for personalization
    across different message types and channels.
    """
    logger.info(f"📝 Creating template: {request.name}")

    try:
        result = await herald_lord.execute(
            task="manage_template",
            parameters={
                "action": "create",
                "name": request.name,
                "template_type": request.template_type,
                "subject_template": request.subject_template,
                "content_template": request.content_template,
                "variables": request.variables,
            }
        )

        if result.get("success", True):
            return {
                "status": "success",
                "data": result,
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Template creation failed")
            )

    except Exception as e:
        logger.error(f"❌ Template creation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/templates", response_model=Dict[str, Any])
async def get_templates(
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    herald_lord: HeraldLord = Depends(get_herald)
):
    """Get all message templates."""
    result = await herald_lord.execute(
        task="manage_template",
        parameters={"action": "list"}
    )

    return {
        "status": "success",
        "data": result,
    }

@router.get("/templates/{template_id}", response_model=Dict[str, Any])
async def get_template(
    template_id: str,
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    herald_lord: HeraldLord = Depends(get_herald)
):
    """Get template details."""
    result = await herald_lord.execute(
        task="manage_template",
        parameters={"action": "get", "template_id": template_id}
    )

    if result.get("success", True):
        return {
            "status": "success",
            "data": result,
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result.get("error", "Template not found")
        )

# ============================================================================
# DELIVERY TRACKING ENDPOINTS
# ============================================================================

@router.post("/delivery/track", response_model=Dict[str, Any])
async def track_delivery(
    request: TrackDeliveryRequest,
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    herald_lord: HeraldLord = Depends(get_herald)
):
    """
    Track message or announcement delivery.

    Track real-time delivery status, open rates, and engagement metrics
    for messages and announcements.
    """
    logger.info(f"📊 Tracking delivery for message/announcement")

    try:
        result = await herald_lord.execute(
            task="track_delivery",
            parameters={
                "message_id": request.message_id or "",
                "announcement_id": request.announcement_id or "",
                "period_days": request.period_days,
            }
        )

        if result.get("success", True):
            return {
                "status": "success",
                "data": result,
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Tracking failed")
            )

    except Exception as e:
        logger.error(f"❌ Delivery tracking error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ============================================================================
# REPORTING ENDPOINTS
# ============================================================================

@router.post("/reporting/communication-report", response_model=Dict[str, Any])
async def get_communication_report(
    request: GetReportRequest,
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    herald_lord: HeraldLord = Depends(get_herald)
):
    """
    Generate communication report.

    Generate comprehensive reports on message delivery, open rates,
    click rates, and communication metrics over specified periods.
    """
    logger.info(f"📈 Generating communication report for {request.period_days} days")

    try:
        result = await herald_lord.execute(
            task="get_communication_report",
            parameters={
                "period_days": request.period_days,
            }
        )

        if result.get("success", True):
            return {
                "status": "success",
                "data": result,
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Report generation failed")
            )

    except Exception as e:
        logger.error(f"❌ Report generation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/reports", response_model=List[Dict[str, Any]])
async def get_reports(
    limit: int = 10,
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    herald_lord: HeraldLord = Depends(get_herald)
):
    """Get recent communication reports."""
    return await herald_lord.get_recent_reports(limit=limit)

# ============================================================================
# STATUS & METRICS ENDPOINTS
# ============================================================================

@router.get("/status", response_model=Dict[str, Any])
async def get_herald_status(
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    herald_lord: HeraldLord = Depends(get_herald)
):
    """Get Herald status and performance summary."""
    summary = await herald_lord.get_performance_summary()

    return {
        "agent": {
            "name": herald_lord.name,
            "role": herald_lord.role,
            "status": herald_lord.status,
        },
        "performance": summary,
        "timestamp": datetime.utcnow().isoformat()
    }
