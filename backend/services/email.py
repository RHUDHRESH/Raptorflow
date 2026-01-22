"""
Resend Email Service
Handles transactional emails
"""

import logging
import os
from typing import Any, Dict, List, Optional, Union

import resend

# Configure logging
logger = logging.getLogger(__name__)


class ResendEmailService:
    """
    Email service using Resend
    """

    def __init__(self):
        self.api_key = os.getenv("RESEND_API_KEY")
        self.sender_email = os.getenv("RESEND_FROM_EMAIL") or os.getenv(
            "SENDER_EMAIL_ADDRESS", "onboarding@resend.dev"
        )  # Default Resend dev email

        if not self.api_key:
            logger.warning("RESEND_API_KEY not set. Email service disabled.")
        else:
            resend.api_key = self.api_key

    def send_email(
        self,
        to: Union[str, List[str]],
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
    ) -> bool:
        """
        Send an email
        """
        if not self.api_key:
            logger.warning("Attempted to send email without API key")
            return False

        try:
            params = {
                "from": self.sender_email,
                "to": to,
                "subject": subject,
                "html": html_content,
            }
            if text_content:
                params["text"] = text_content

            r = resend.Emails.send(params)
            logger.info(f"Email sent to {to}: {r}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {to}: {e}")
            return False

    def send_welcome_email(self, user_email: str, plan_name: str) -> bool:
        """
        Send welcome email upon purchase
        """
        subject = "Welcome to RaptorFlow!"
        # Simple HTML template
        html_content = f"""
        <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto;">
            <h1>Welcome to RaptorFlow</h1>
            <p>Thank you for subscribing to the <strong>{plan_name}</strong> plan.</p>
            <p>We are thrilled to have you on board. Your account has been upgraded and you now have access to all premium features.</p>
            <br>
            <a href="https://app.raptorflow.com/dashboard" style="background-color: #000; color: #fff; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Go to Dashboard</a>
            <br><br>
            <p>Best regards,<br>The RaptorFlow Team</p>
        </div>
        """
        return self.send_email(user_email, subject, html_content)


# Singleton
email_service = ResendEmailService()
