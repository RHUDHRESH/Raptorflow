"""Resend email service.

Canonical email integration using Resend + Jinja2 templates.
All transactional emails go through this module.
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape

from backend.services.base_service import BaseService
from backend.services.registry import registry
from backend.services.exceptions import ServiceError, ServiceUnavailableError

logger = logging.getLogger(__name__)

# Template directory
_TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates" / "email"

class EmailService(BaseService):
    def __init__(self):
        super().__init__("email_service")
        self._jinja_env: Optional[Environment] = None
        self._resend = None
        self.api_key = None
        self.from_email = None
        self.delivery_enabled = True

    async def initialize(self) -> None:
        """Initialize Jinja2 environment and Resend client."""
        try:
            # Initialize Jinja2
            self._jinja_env = Environment(
                loader=FileSystemLoader(str(_TEMPLATE_DIR)),
                autoescape=select_autoescape(["html"]),
            )

            # Initialize Resend
            try:
                import resend
                from backend.config.settings import get_settings
                settings = get_settings()
                
                self.api_key = settings.RESEND_API_KEY
                self.from_email = settings.EMAIL_FROM
                self.delivery_enabled = bool(getattr(settings, "ENABLE_EMAIL_DELIVERY", True))

                if not self.delivery_enabled:
                    logger.info("Email delivery disabled by ENABLE_EMAIL_DELIVERY=false")
                    await super().initialize()
                    return

                if not self.api_key:
                    logger.warning("Resend disabled: RESEND_API_KEY not configured")
                else:
                    resend.api_key = self.api_key
                    self._resend = resend
            except ImportError:
                logger.warning("Resend disabled: resend package not installed")

            await super().initialize()
        except Exception as e:
            logger.error(f"Failed to initialize EmailService: {e}")
            # Don't raise, allowing app to start even if email is broken

    async def check_health(self) -> Dict[str, Any]:
        """Check service health status."""
        if not self.delivery_enabled:
            return {"status": "disabled", "detail": "Email delivery disabled by config"}
        if not self._resend or not self.api_key:
             return {"status": "disabled", "detail": "Resend not configured"}
        return {"status": "healthy"}

    def _get_jinja(self) -> Environment:
        """Lazy-init Jinja2 environment if not already initialized."""
        if self._jinja_env is None:
             self._jinja_env = Environment(
                loader=FileSystemLoader(str(_TEMPLATE_DIR)),
                autoescape=select_autoescape(["html"]),
            )
        return self._jinja_env

    def send(
        self,
        to: str,
        subject: str,
        template_name: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Render a template and send via Resend."""
        
        def _execute():
            if not self._resend:
                return {"status": "error", "error": "Resend not configured"}

            try:
                jinja = self._get_jinja()
                template = jinja.get_template(template_name)
                html = template.render(**context)

                sender = (self.from_email or "").strip() or "noreply@raptorflow.in"

                def _send_with_sender(from_value: str):
                    params = {
                        "from": from_value,
                        "to": [to],
                        "subject": subject,
                        "html": html,
                    }
                    return self._resend.Emails.send(params)

                result = _send_with_sender(sender)

                logger.info("Email sent: %s -> %s (%s)", template_name, to, subject)
                return {"status": "success", "id": result.get("id", "")}
            except Exception as exc:
                logger.error("Email send failed: %s", exc)
                return {"status": "error", "error": str(exc)}

        # Wrap in execute_with_retry if we want retry logic for email sending
        # Since this is a synchronous method calling external API, we can wrap it.
        # But wait, execute_with_retry is async.
        # The original `_send` was synchronous.
        # To maintain backward compatibility while using BaseService features, we might need an async version.
        # However, for now, we'll keep the sync interface for backward compatibility
        # and just call the internal logic.
        # Ideally, we should migrate callers to await send_async().
        
        return _execute()

    async def send_async(
        self,
        to: str,
        subject: str,
        template_name: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Async version of send with retry logic."""
        
        def _execute_sync():
            return self.send(to, subject, template_name, context)

        # BaseService.execute_with_retry handles sync functions too, but runs them... actually it runs them directly if not coroutine.
        # So we can just pass the sync function.
        return await self.execute_with_retry(_execute_sync)

    # ── Public API Shortcuts ──

    def send_welcome(self, to: str, user_name: str, app_url: str = "") -> Dict[str, Any]:
        if not app_url:
            app_url = "https://app.raptorflow.com"
        return self.send(
            to=to,
            subject="Welcome to Raptorflow",
            template_name="welcome.html",
            context={"user_name": user_name, "app_url": app_url},
        )

    def send_workspace_invite(self, to: str, inviter_name: str, workspace_name: str, invite_url: str) -> Dict[str, Any]:
        return self.send(
            to=to,
            subject=f"You've been invited to {workspace_name}",
            template_name="workspace_invite.html",
            context={
                "inviter_name": inviter_name,
                "workspace_name": workspace_name,
                "invite_url": invite_url,
            },
        )

    def send_password_reset(self, to: str, reset_url: str, expires_in: str = "1 hour") -> Dict[str, Any]:
        return self.send(
            to=to,
            subject="Reset your Raptorflow password",
            template_name="password_reset.html",
            context={"reset_url": reset_url, "expires_in": expires_in},
        )

    def send_payment_confirmation(self, to: str, plan_name: str, amount: str, currency: str = "INR", date: str = "", receipt_url: str = "") -> Dict[str, Any]:
        return self.send(
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

    def send_account_deactivation(self, to: str, user_name: str, retention_days: int = 30) -> Dict[str, Any]:
        return self.send(
            to=to,
            subject="Your Raptorflow account has been deactivated",
            template_name="account_deactivation.html",
            context={"user_name": user_name, "retention_days": retention_days},
        )

    def send_export_ready(self, to: str, export_name: str, download_url: str, expires_in: str = "7 days") -> Dict[str, Any]:
        return self.send(
            to=to,
            subject=f"Your export is ready — {export_name}",
            template_name="export_ready.html",
            context={
                "export_name": export_name,
                "download_url": download_url,
                "expires_in": expires_in,
            },
        )

# Global instance
email_service = EmailService()
registry.register(email_service)

# Backward compatibility wrappers
def _send(to: str, subject: str, template_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
    return email_service.send(to, subject, template_name, context)

def send_welcome(to: str, user_name: str, app_url: str = "") -> Dict[str, Any]:
    return email_service.send_welcome(to, user_name, app_url)

def send_workspace_invite(to: str, inviter_name: str, workspace_name: str, invite_url: str) -> Dict[str, Any]:
    return email_service.send_workspace_invite(to, inviter_name, workspace_name, invite_url)

def send_password_reset(to: str, reset_url: str, expires_in: str = "1 hour") -> Dict[str, Any]:
    return email_service.send_password_reset(to, reset_url, expires_in)

def send_payment_confirmation(to: str, plan_name: str, amount: str, currency: str = "INR", date: str = "", receipt_url: str = "") -> Dict[str, Any]:
    return email_service.send_payment_confirmation(to, plan_name, amount, currency, date, receipt_url)

def send_account_deactivation(to: str, user_name: str, retention_days: int = 30) -> Dict[str, Any]:
    return email_service.send_account_deactivation(to, user_name, retention_days)

def send_export_ready(to: str, export_name: str, download_url: str, expires_in: str = "7 days") -> Dict[str, Any]:
    return email_service.send_export_ready(to, export_name, download_url, expires_in)
