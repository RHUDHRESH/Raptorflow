"""Resend email service.

Canonical email integration using Resend + Jinja2 templates.
All transactional emails go through this module.
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape

logger = logging.getLogger(__name__)

# Template directory
_TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates" / "email"
_jinja_env: Optional[Environment] = None


def _get_jinja() -> Environment:
    """Lazy-init Jinja2 environment."""
    global _jinja_env
    if _jinja_env is None:
        _jinja_env = Environment(
            loader=FileSystemLoader(str(_TEMPLATE_DIR)),
            autoescape=select_autoescape(["html"]),
        )
    return _jinja_env


def _get_resend():
    """Lazy-import resend and configure API key."""
    try:
        import resend

        from backend.config.settings import get_settings

        settings = get_settings()
        if not settings.RESEND_API_KEY:
            logger.warning("Resend disabled: RESEND_API_KEY not configured")
            return None
        resend.api_key = settings.RESEND_API_KEY
        return resend
    except ImportError:
        logger.warning("Resend disabled: resend package not installed")
        return None


def _send(
    to: str,
    subject: str,
    template_name: str,
    context: Dict[str, Any],
) -> Dict[str, Any]:
    """Render a template and send via Resend."""
    resend = _get_resend()
    if resend is None:
        return {"status": "error", "error": "Resend not configured"}

    from backend.config.settings import get_settings

    settings = get_settings()

    try:
        jinja = _get_jinja()
        template = jinja.get_template(template_name)
        html = template.render(**context)

        params = {
            "from_": settings.EMAIL_FROM,
            "to": [to],
            "subject": subject,
            "html": html,
        }
        result = resend.Emails.send(params)
        logger.info("Email sent: %s -> %s (%s)", template_name, to, subject)
        return {"status": "success", "id": result.get("id", "")}
    except Exception as exc:
        logger.error("Email send failed: %s", exc)
        return {"status": "error", "error": str(exc)}


# ── Public API ────────────────────────────────────────────────────────────────


def send_welcome(to: str, user_name: str, app_url: str = "") -> Dict[str, Any]:
    """Send welcome email after signup."""
    from backend.config.settings import get_settings

    if not app_url:
        app_url = "https://app.raptorflow.com"

    return _send(
        to=to,
        subject="Welcome to Raptorflow",
        template_name="welcome.html",
        context={"user_name": user_name, "app_url": app_url},
    )


def send_workspace_invite(
    to: str,
    inviter_name: str,
    workspace_name: str,
    invite_url: str,
) -> Dict[str, Any]:
    """Send workspace invitation email."""
    return _send(
        to=to,
        subject=f"You've been invited to {workspace_name}",
        template_name="workspace_invite.html",
        context={
            "inviter_name": inviter_name,
            "workspace_name": workspace_name,
            "invite_url": invite_url,
        },
    )


def send_password_reset(to: str, reset_url: str, expires_in: str = "1 hour") -> Dict[str, Any]:
    """Send password reset email."""
    return _send(
        to=to,
        subject="Reset your Raptorflow password",
        template_name="password_reset.html",
        context={"reset_url": reset_url, "expires_in": expires_in},
    )


def send_payment_confirmation(
    to: str,
    plan_name: str,
    amount: str,
    currency: str = "INR",
    date: str = "",
    receipt_url: str = "",
) -> Dict[str, Any]:
    """Send payment confirmation email."""
    return _send(
        to=to,
        subject=f"Payment confirmed — {plan_name}",
        template_name="payment_confirmation.html",
        context={
            "plan_name": plan_name,
            "amount": amount,
            "currency": currency,
            "date": date,
            "receipt_url": receipt_url,
        },
    )


def send_account_deactivation(to: str, user_name: str, retention_days: int = 30) -> Dict[str, Any]:
    """Send account deactivation confirmation."""
    return _send(
        to=to,
        subject="Your Raptorflow account has been deactivated",
        template_name="account_deactivation.html",
        context={"user_name": user_name, "retention_days": retention_days},
    )


def send_export_ready(to: str, export_name: str, download_url: str, expires_in: str = "7 days") -> Dict[str, Any]:
    """Send export ready notification."""
    return _send(
        to=to,
        subject=f"Your export is ready — {export_name}",
        template_name="export_ready.html",
        context={
            "export_name": export_name,
            "download_url": download_url,
            "expires_in": expires_in,
        },
    )
