"""
Email Infrastructure Layer
Handles email sending via Resend
"""

import logging
import os
from typing import Any, Dict, List, Optional

import httpx
from pydantic import BaseModel, EmailStr

logger = logging.getLogger(__name__)


class EmailConfig(BaseModel):
    """Email configuration"""

    api_key: str
    from_email: str
    from_name: str = "RaptorFlow"


class EmailRecipient(BaseModel):
    """Email recipient"""

    email: EmailStr
    name: Optional[str] = None


class EmailAttachment(BaseModel):
    """Email attachment"""

    filename: str
    content: str  # base64 encoded
    content_type: str


class EmailMessage(BaseModel):
    """Email message"""

    to: List[EmailRecipient]
    subject: str
    html: Optional[str] = None
    text: Optional[str] = None
    cc: Optional[List[EmailRecipient]] = None
    bcc: Optional[List[EmailRecipient]] = None
    attachments: Optional[List[EmailAttachment]] = None


class EmailClient:
    """Resend email client wrapper"""

    def __init__(self, config: Optional[EmailConfig] = None):
        self.config = config or self._load_config()
        self.client: Optional[httpx.AsyncClient] = None
        self.api_url = "https://api.resend.com"

    def _ensure_client(self) -> None:
        if self.client is None:
            self.client = httpx.AsyncClient()

    def _load_config(self) -> EmailConfig:
        """Load email configuration from environment"""
        return EmailConfig(
            api_key=os.getenv("RESEND_API_KEY", ""),
            from_email=os.getenv("FROM_EMAIL", "noreply@raptorflow.com"),
            from_name=os.getenv("FROM_NAME", "RaptorFlow"),
        )

    async def send(self, message: EmailMessage) -> Dict[str, Any]:
        """Send an email via Resend API"""
        try:
            if not self.config.api_key:
                return {"success": False, "error": "No RESEND_API_KEY configured"}

            self._ensure_client()
            headers = {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
            }

            # Build payload
            payload = {
                "from": f"{self.config.from_name} <{self.config.from_email}>",
                "to": [r.email for r in message.to],
                "subject": message.subject,
            }

            if message.html:
                payload["html"] = message.html
            if message.text:
                payload["text"] = message.text

            if message.cc:
                payload["cc"] = [r.email for r in message.cc]
            if message.bcc:
                payload["bcc"] = [r.email for r in message.bcc]

            if message.attachments:
                payload["attachments"] = [
                    {
                        "filename": a.filename,
                        "content": a.content,
                        "content_type": a.content_type,
                    }
                    for a in message.attachments
                ]

            response = await self.client.post(
                f"{self.api_url}/emails",
                headers=headers,
                json=payload,
            )

            if response.status_code in [200, 201]:
                result = response.json()
                logger.info(f"Email sent successfully: {result.get('id')}")
                return {"success": True, "id": result.get("id")}
            else:
                logger.error(
                    f"Email send failed: {response.status_code} - {response.text}"
                )
                return {"success": False, "error": response.text}

        except Exception as e:
            logger.error(f"Email send error: {e}")
            return {"success": False, "error": str(e)}

    async def send_template(
        self,
        to: List[EmailRecipient],
        template_id: str,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Send a templated email"""
        # For now, just log that templates aren't implemented
        logger.warning("Email templates not yet implemented")
        return {"success": False, "error": "Templates not implemented"}

    async def health_check(self) -> Dict[str, Any]:
        """Check email service health"""
        try:
            if not self.config.api_key:
                return {
                    "status": "unhealthy",
                    "message": "No API key configured",
                }

            self._ensure_client()

            # Try to list domains (lightweight check)
            headers = {"Authorization": f"Bearer {self.config.api_key}"}
            response = await self.client.get(
                f"{self.api_url}/domains",
                headers=headers,
            )

            return {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "message": (
                    "Email service OK"
                    if response.status_code == 200
                    else f"Error: {response.status_code}"
                ),
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": str(e),
            }


_email_client: Optional[EmailClient] = None


def get_email() -> EmailClient:
    """Get email client instance"""
    global _email_client
    if _email_client is None:
        _email_client = EmailClient()
    return _email_client
