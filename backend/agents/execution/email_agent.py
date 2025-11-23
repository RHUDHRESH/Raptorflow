"""
Email Agent - Sends emails via Gmail API or SMTP.
Handles email campaigns, tracking, and deliverability.
"""

import structlog
from typing import Dict, Any, Optional, List
from uuid import UUID
from datetime import datetime, timezone

from backend.services.social.email import email_service
from backend.models.content import ContentVariant
from backend.utils.correlation import get_correlation_id
from backend.utils.queue import redis_queue

logger = structlog.get_logger(__name__)


class EmailAgent:
    """
    Sends marketing emails.
    Handles personalization, tracking, and deliverability best practices.
    """
    
    def __init__(self):
        self.email_service = email_service
    
    async def format_email(self, variant: ContentVariant) -> Dict[str, str]:
        """
        Extracts subject line and body from email content.
        """
        content = variant.content
        
        # Try to extract subject line (usually first line or marked)
        lines = content.split("\n")
        subject = lines[0] if lines else "Your update from RaptorFlow"
        
        # Check if first line looks like a subject
        if len(subject) > 150 or "\n\n" not in content:
            # Might not be separated, generate default
            subject = "Your personalized update"
            body = content
        else:
            # Remove subject from body
            body = "\n".join(lines[1:]).strip()
        
        # Clean up subject
        subject = subject.replace("Subject:", "").replace("Subject Line:", "").strip()
        
        return {
            "subject": subject,
            "body": body
        }
    
    async def send_email(
        self,
        variant: ContentVariant,
        workspace_id: UUID,
        to_email: str,
        to_name: Optional[str] = None,
        from_name: str = "RaptorFlow",
        from_email: Optional[str] = None,
        reply_to: Optional[str] = None,
        schedule_time: Optional[datetime] = None,
        track_opens: bool = True,
        track_clicks: bool = True,
        correlation_id: str = None
    ) -> Dict[str, Any]:
        """
        Sends an email.
        
        Args:
            variant: Email content
            workspace_id: User's workspace
            to_email: Recipient email
            to_name: Recipient name (for personalization)
            from_name: Sender name
            from_email: Sender email (defaults to workspace email)
            reply_to: Reply-to address
            schedule_time: Optional scheduled send time
            track_opens: Track email opens
            track_clicks: Track link clicks
            
        Returns:
            Dict with message_id, status
        """
        correlation_id = correlation_id or get_correlation_id()
        logger.info("Sending email", to_email=to_email, scheduled=schedule_time is not None, correlation_id=correlation_id)
        
        # Format email
        formatted = await self.format_email(variant)
        subject = formatted["subject"]
        body = formatted["body"]
        
        # Personalize if name provided
        if to_name:
            body = body.replace("{{name}}", to_name)
            body = body.replace("Hi there", f"Hi {to_name}")
        
        # If scheduled, queue the task
        if schedule_time and schedule_time > datetime.now(timezone.utc):
            await redis_queue.enqueue(
                task_name="send_email",
                payload={
                    "subject": subject,
                    "body": body,
                    "to_email": to_email,
                    "to_name": to_name,
                    "from_name": from_name,
                    "from_email": from_email,
                    "reply_to": reply_to,
                    "workspace_id": str(workspace_id),
                    "track_opens": track_opens,
                    "track_clicks": track_clicks,
                    "schedule_time": schedule_time.isoformat()
                },
                priority="high"  # Email delivery is high priority
            )
            logger.info("Email scheduled", schedule_time=schedule_time, correlation_id=correlation_id)
            return {
                "status": "scheduled",
                "schedule_time": schedule_time.isoformat(),
                "message": "Email queued for sending"
            }
        
        # Send immediately
        try:
            result = await self.email_service.send_email(
                to_email=to_email,
                to_name=to_name,
                subject=subject,
                body=body,
                from_name=from_name,
                from_email=from_email,
                reply_to=reply_to,
                workspace_id=workspace_id,
                track_opens=track_opens,
                track_clicks=track_clicks
            )
            
            logger.info("Email sent", message_id=result.get("message_id"), correlation_id=correlation_id)
            return {
                "status": "sent",
                "message_id": result.get("message_id"),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error("Failed to send email", error=str(e), to_email=to_email, correlation_id=correlation_id)
            return {
                "status": "failed",
                "error": str(e)
            }
    
    async def send_bulk_emails(
        self,
        variant: ContentVariant,
        workspace_id: UUID,
        recipients: List[Dict[str, str]],  # [{"email": "...", "name": "..."}]
        from_name: str = "RaptorFlow",
        schedule_time: Optional[datetime] = None,
        correlation_id: str = None
    ) -> Dict[str, Any]:
        """
        Sends bulk emails (email campaign).
        
        Args:
            variant: Email content
            workspace_id: User's workspace
            recipients: List of recipient dicts with email and name
            from_name: Sender name
            schedule_time: Optional scheduled send time
            
        Returns:
            Dict with sent_count, failed_count, status
        """
        correlation_id = correlation_id or get_correlation_id()
        logger.info("Sending bulk emails", count=len(recipients), correlation_id=correlation_id)
        
        results = []
        for recipient in recipients:
            result = await self.send_email(
                variant=variant,
                workspace_id=workspace_id,
                to_email=recipient["email"],
                to_name=recipient.get("name"),
                from_name=from_name,
                schedule_time=schedule_time,
                correlation_id=correlation_id
            )
            results.append(result)
        
        sent_count = sum(1 for r in results if r["status"] in ["sent", "scheduled"])
        failed_count = sum(1 for r in results if r["status"] == "failed")
        
        return {
            "status": "completed",
            "total": len(recipients),
            "sent": sent_count,
            "failed": failed_count,
            "results": results
        }


email_agent = EmailAgent()

