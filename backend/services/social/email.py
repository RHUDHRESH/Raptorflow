"""
Email Service - SMTP/Gmail API integration for sending marketing emails.
"""

import structlog
from typing import Dict, Any, Optional
from uuid import UUID
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from backend.config.settings import get_settings
from backend.services.supabase_client import supabase_client

logger = structlog.get_logger(__name__)
settings = get_settings()


class EmailService:
    """
    Email delivery service using SMTP or Gmail API.
    Handles transactional and marketing emails.
    """
    
    def __init__(self):
        self.smtp_host = "smtp.gmail.com"  # Or custom SMTP
        self.smtp_port = 587
    
    async def get_smtp_credentials(self, workspace_id: UUID) -> Optional[Dict[str, str]]:
        """Retrieves stored SMTP credentials."""
        try:
            integration = await supabase_client.fetch_one(
                "integrations",
                {"workspace_id": str(workspace_id), "platform": "email"}
            )
            if integration:
                return {
                    "username": integration.get("smtp_username"),
                    "password": integration.get("smtp_password"),
                    "from_email": integration.get("from_email")
                }
            return None
        except Exception as e:
            logger.error(f"Failed to get SMTP credentials: {e}")
            return None
    
    async def send_email(
        self,
        to_email: str,
        to_name: Optional[str],
        subject: str,
        body: str,
        from_name: str,
        from_email: Optional[str],
        reply_to: Optional[str],
        workspace_id: UUID,
        track_opens: bool = True,
        track_clicks: bool = True
    ) -> Dict[str, Any]:
        """Sends an email via SMTP."""
        credentials = await self.get_smtp_credentials(workspace_id)
        if not credentials:
            raise ValueError("Email not configured for workspace")
        
        # Create message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{from_name} <{from_email or credentials['from_email']}>"
        msg["To"] = f"{to_name} <{to_email}>" if to_name else to_email
        if reply_to:
            msg["Reply-To"] = reply_to
        
        # Add tracking pixel if enabled
        if track_opens:
            tracking_pixel = f'<img src="https://track.raptorflow.com/open/{workspace_id}/{to_email}" width="1" height="1" />'
            body += tracking_pixel
        
        # Add body
        msg.attach(MIMEText(body, "html"))
        
        try:
            # Send via SMTP
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(credentials["username"], credentials["password"])
                server.send_message(msg)
            
            logger.info("Email sent", to=to_email)
            return {
                "message_id": f"msg_{workspace_id}_{to_email}",
                "status": "sent"
            }
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            raise


email_service = EmailService()

