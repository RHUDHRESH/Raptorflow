"""Communications API (email/contact)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel, Field

from backend.config import settings
from backend.services.email_service import email_service

router = APIRouter(prefix="/communications", tags=["communications"])


class ContactRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    email: str = Field(..., min_length=3, max_length=254)
    subject: str = Field(default="General inquiry", min_length=1, max_length=160)
    message: str = Field(..., min_length=10, max_length=5000)
    source: str = Field(default="contact-page", max_length=120)
    workspace_id: Optional[str] = Field(default=None, max_length=64)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ContactResponse(BaseModel):
    accepted: bool
    status: str
    support_delivery: str = ""
    ack_delivery: str = ""


@router.post("/contact", response_model=ContactResponse)
async def submit_contact(
    payload: ContactRequest,
    x_workspace_id: Optional[str] = Header(None, alias="x-workspace-id"),
) -> ContactResponse:
    if "@" not in payload.email:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid email address",
        )

    workspace_id = payload.workspace_id or x_workspace_id or ""
    support_to = getattr(settings, "SUPPORT_EMAIL_TO", "") or settings.EMAIL_FROM

    timestamp = datetime.now(timezone.utc).isoformat()
    context = {
        "name": payload.name.strip(),
        "email": payload.email,
        "subject": payload.subject.strip(),
        "message": payload.message.strip(),
        "source": payload.source,
        "workspace_id": workspace_id or "n/a",
        "metadata": payload.metadata,
        "submitted_at": timestamp,
    }

    if not getattr(email_service, "api_key", None):
        return ContactResponse(
            accepted=True,
            status="logged_only",
            support_delivery="skipped",
            ack_delivery="skipped",
        )

    inbound = email_service.send(
        to=support_to,
        subject=f"[Contact] {payload.subject.strip()}",
        template_name="contact_inbound.html",
        context=context,
    )

    ack = email_service.send(
        to=payload.email,
        subject="We received your message",
        template_name="contact_ack.html",
        context=context,
    )

    return ContactResponse(
        accepted=inbound.get("status") == "success",
        status="sent" if inbound.get("status") == "success" else "partial",
        support_delivery=inbound.get("status", "error"),
        ack_delivery=ack.get("status", "error"),
    )
