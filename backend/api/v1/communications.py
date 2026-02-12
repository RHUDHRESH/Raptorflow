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
    name = payload.name.strip()
    email = payload.email.strip()
    subject = payload.subject.strip() or "General inquiry"
    message = payload.message.strip()

    if "@" not in email:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid email address",
        )
    if len(message) < 10:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Message is too short",
        )

    workspace_id = payload.workspace_id or x_workspace_id or ""
    support_to = getattr(settings, "SUPPORT_EMAIL_TO", "") or settings.EMAIL_FROM

    timestamp = datetime.now(timezone.utc).isoformat()
    context = {
        "name": name,
        "email": email,
        "subject": subject,
        "message": message,
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
        subject=f"[Contact] {subject}",
        template_name="contact_inbound.html",
        context=context,
    )

    ack = email_service.send(
        to=email,
        subject="We received your message",
        template_name="contact_ack.html",
        context=context,
    )

    support_delivery = inbound.get("status", "error")
    ack_delivery = ack.get("status", "error")
    support_ok = support_delivery == "success"
    ack_ok = ack_delivery == "success"

    if support_ok and ack_ok:
        status_value = "sent"
    elif support_ok or ack_ok:
        status_value = "partial"
    else:
        # Keep contact UX non-blocking even when provider-side restrictions apply.
        status_value = "queued"

    return ContactResponse(
        accepted=True,
        status=status_value,
        support_delivery=support_delivery,
        ack_delivery=ack_delivery,
    )
