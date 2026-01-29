"""Email service for payment notifications and user communications using Resend."""

import logging
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import resend
from jinja2 import Template

logger = logging.getLogger(__name__)


class EmailError(Exception):
    """Structured email service errors."""

    def __init__(self, message: str, error_type: str, context: Dict[str, Any] = None):
        super().__init__(message)
        self.error_type = error_type
        self.context = context or {}


@dataclass
class EmailRecipient:
    """Email recipient information."""

    email: str
    name: Optional[str] = None


@dataclass
class EmailTemplate:
    """Email template configuration."""

    template_name: str
    subject: str
    html_content: str
    text_content: Optional[str] = None


class EmailService:
    """Email service using Resend API for transactional emails."""

    def __init__(self):
        """Initialize email service with Resend."""
        self.api_key = os.getenv("RESEND_API_KEY")
        self.from_email = os.getenv("FROM_EMAIL", "noreply@raptorflow.com")
        self.from_name = os.getenv("FROM_NAME", "RaptorFlow")

        if not self.api_key:
            raise EmailError(
                "RESEND_API_KEY environment variable is required", "MISSING_API_KEY"
            )

        resend.api_key = self.api_key
        self.from_address = f"{self.from_name} <{self.from_email}>"

    def send_payment_confirmation(
        self,
        recipient: EmailRecipient,
        plan_name: str,
        amount: int,
        transaction_id: str,
        period_end: datetime,
        workspace_name: Optional[str] = None,
        billing_cycle: str = "monthly",
    ) -> bool:
        """Send payment confirmation email with plan-specific template."""
        try:
            # Select template based on plan
            template_file = self._get_plan_template_file(plan_name)
            subject = self._get_plan_subject(plan_name)

            # Generate HTML content using plan-specific template
            html_content = self._render_plan_specific_template(
                template_file=template_file,
                recipient_name=recipient.name,
                plan_name=plan_name,
                amount=amount,
                transaction_id=transaction_id,
                period_end=period_end,
                workspace_name=workspace_name,
                billing_cycle=billing_cycle,
            )

            # Send email
            params = {
                "from": self.from_address,
                "to": [recipient.email],
                "subject": subject,
                "html": html_content,
            }

            result = resend.Emails.send(params)

            if result.get("id"):
                logger.info(
                    f"Payment confirmation email sent to {recipient.email}, "
                    f"plan: {plan_name}, transaction_id: {transaction_id}, email_id: {result['id']}"
                )
                return True
            else:
                logger.error(f"Failed to send payment confirmation: {result}")
                return False

        except Exception as exc:
            logger.error(
                f"Failed to send payment confirmation to {recipient.email}: {exc}",
                extra={"recipient": recipient.email, "transaction_id": transaction_id},
            )
            raise EmailError(
                f"Payment confirmation email failed: {exc}",
                "PAYMENT_CONFIRMATION_ERROR",
                {"recipient": recipient.email, "transaction_id": transaction_id},
            ) from exc

    def send_payment_failure(
        self,
        recipient: EmailRecipient,
        plan_name: str,
        amount: int,
        transaction_id: str,
        error_message: Optional[str] = None,
        workspace_name: Optional[str] = None,
    ) -> bool:
        """Send payment failure notification."""
        try:
            subject = f"Payment Failed - {plan_name.title()} Plan"

            # Generate HTML content
            html_content = self._render_payment_failure_template(
                recipient_name=recipient.name,
                plan_name=plan_name,
                amount=amount,
                transaction_id=transaction_id,
                error_message=error_message,
                workspace_name=workspace_name,
            )

            # Send email
            params = {
                "from": self.from_address,
                "to": [recipient.email],
                "subject": subject,
                "html": html_content,
            }

            result = resend.Emails.send(params)

            if result.get("id"):
                logger.info(
                    f"Payment failure email sent to {recipient.email}, "
                    f"transaction_id: {transaction_id}, email_id: {result['id']}"
                )
                return True
            else:
                logger.error(f"Failed to send payment failure: {result}")
                return False

        except Exception as exc:
            logger.error(
                f"Failed to send payment failure to {recipient.email}: {exc}",
                extra={"recipient": recipient.email, "transaction_id": transaction_id},
            )
            raise EmailError(
                f"Payment failure email failed: {exc}",
                "PAYMENT_FAILURE_ERROR",
                {"recipient": recipient.email, "transaction_id": transaction_id},
            ) from exc

    def send_trial_ending(
        self,
        recipient: EmailRecipient,
        trial_end: datetime,
        workspace_name: Optional[str] = None,
    ) -> bool:
        """Send trial ending reminder."""
        try:
            days_remaining = (trial_end - datetime.now(trial_end.tzinfo)).days
            subject = f"Trial Ending in {days_remaining} Days"

            # Generate HTML content
            html_content = self._render_trial_ending_template(
                recipient_name=recipient.name,
                trial_end=trial_end,
                days_remaining=days_remaining,
                workspace_name=workspace_name,
            )

            # Send email
            params = {
                "from": self.from_address,
                "to": [recipient.email],
                "subject": subject,
                "html": html_content,
            }

            result = resend.Emails.send(params)

            if result.get("id"):
                logger.info(
                    f"Trial ending email sent to {recipient.email}, "
                    f"trial_end: {trial_end}, email_id: {result['id']}"
                )
                return True
            else:
                logger.error(f"Failed to send trial ending: {result}")
                return False

        except Exception as exc:
            logger.error(
                f"Failed to send trial ending to {recipient.email}: {exc}",
                extra={"recipient": recipient.email, "trial_end": trial_end},
            )
            raise EmailError(
                f"Trial ending email failed: {exc}",
                "TRIAL_ENDING_ERROR",
                {"recipient": recipient.email, "trial_end": trial_end},
            ) from exc

    def send_subscription_renewal(
        self,
        recipient: EmailRecipient,
        plan_name: str,
        amount: int,
        next_billing_date: datetime,
        workspace_name: Optional[str] = None,
    ) -> bool:
        """Send subscription renewal notification."""
        try:
            subject = f"Subscription Renewed - {plan_name.title()} Plan"

            # Generate HTML content
            html_content = self._render_renewal_template(
                recipient_name=recipient.name,
                plan_name=plan_name,
                amount=amount,
                next_billing_date=next_billing_date,
                workspace_name=workspace_name,
            )

            # Send email
            params = {
                "from": self.from_address,
                "to": [recipient.email],
                "subject": subject,
                "html": html_content,
            }

            result = resend.Emails.send(params)

            if result.get("id"):
                logger.info(
                    f"Renewal email sent to {recipient.email}, "
                    f"next_billing: {next_billing_date}, email_id: {result['id']}"
                )
                return True
            else:
                logger.error(f"Failed to send renewal: {result}")
                return False

        except Exception as exc:
            logger.error(
                f"Failed to send renewal to {recipient.email}: {exc}",
                extra={"recipient": recipient.email, "next_billing": next_billing_date},
            )
            raise EmailError(
                f"Renewal email failed: {exc}",
                "RENEWAL_ERROR",
                {"recipient": recipient.email, "next_billing": next_billing_date},
            ) from exc

    def send_invoice(
        self,
        recipient: EmailRecipient,
        invoice_data: Dict[str, Any],
        workspace_name: Optional[str] = None,
    ) -> bool:
        """Send invoice email."""
        try:
            invoice_number = invoice_data.get("invoice_number", "Unknown")
            subject = f"Invoice #{invoice_number}"

            # Generate HTML content
            html_content = self._render_invoice_template(
                recipient_name=recipient.name,
                invoice_data=invoice_data,
                workspace_name=workspace_name,
            )

            # Send email
            params = {
                "from": self.from_address,
                "to": [recipient.email],
                "subject": subject,
                "html": html_content,
            }

            result = resend.Emails.send(params)

            if result.get("id"):
                logger.info(
                    f"Invoice email sent to {recipient.email}, "
                    f"invoice: {invoice_number}, email_id: {result['id']}"
                )
                return True
            else:
                logger.error(f"Failed to send invoice: {result}")
                return False

        except Exception as exc:
            logger.error(
                f"Failed to send invoice to {recipient.email}: {exc}",
                extra={
                    "recipient": recipient.email,
                    "invoice": invoice_data.get("invoice_number"),
                },
            )
            raise EmailError(
                f"Invoice email failed: {exc}",
                "INVOICE_ERROR",
                {
                    "recipient": recipient.email,
                    "invoice": invoice_data.get("invoice_number"),
                },
            ) from exc

    # ------------------------------------------------------------------
    # Template rendering methods
    # ------------------------------------------------------------------

    def _render_payment_confirmation_template(
        self,
        recipient_name: Optional[str],
        plan_name: str,
        amount: int,
        transaction_id: str,
        period_end: datetime,
        workspace_name: Optional[str] = None,
    ) -> str:
        """Render payment confirmation email template."""
        template_str = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Payment Confirmation</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #2563eb; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; background: #f9fafb; }
        .footer { padding: 20px; text-align: center; font-size: 12px; color: #666; }
        .button { display: inline-block; padding: 12px 24px; background: #2563eb; color: white; text-decoration: none; border-radius: 4px; }
        .details { background: white; padding: 15px; border-radius: 4px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Payment Confirmed!</h1>
        </div>
        <div class="content">
            <p>Hi {{ recipient_name or "there" }},</p>
            <p>Your payment has been successfully processed. Here are your details:</p>

            <div class="details">
                <h3>Payment Details</h3>
                <p><strong>Plan:</strong> {{ plan_name.title() }}</p>
                <p><strong>Amount:</strong> ₹{{ "%.2f"|format(amount/100) }}</p>
                <p><strong>Transaction ID:</strong> {{ transaction_id }}</p>
                <p><strong>Next Billing:</strong> {{ period_end.strftime('%B %d, %Y') }}</p>
                {% if workspace_name %}
                <p><strong>Workspace:</strong> {{ workspace_name }}</p>
                {% endif %}
            </div>

            <p>Your subscription is now active. You can start using all features of your {{ plan_name }} plan.</p>

            <p style="text-align: center;">
                <a href="{{ dashboard_url }}" class="button">Go to Dashboard</a>
            </p>
        </div>
        <div class="footer">
            <p>Thank you for choosing RaptorFlow!</p>
            <p>If you have any questions, please contact our support team.</p>
        </div>
    </div>
</body>
</html>
        """

        template = Template(template_str)
        return template.render(
            recipient_name=recipient_name,
            plan_name=plan_name,
            amount=amount,
            transaction_id=transaction_id,
            period_end=period_end,
            workspace_name=workspace_name,
            dashboard_url=os.getenv("NEXT_PUBLIC_APP_URL", "https://raptorflow.com")
            + "/dashboard",
        )

    def _render_payment_failure_template(
        self,
        recipient_name: Optional[str],
        plan_name: str,
        amount: int,
        transaction_id: str,
        error_message: Optional[str] = None,
        workspace_name: Optional[str] = None,
    ) -> str:
        """Render payment failure email template."""
        template_str = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Payment Failed</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #dc2626; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; background: #f9fafb; }
        .footer { padding: 20px; text-align: center; font-size: 12px; color: #666; }
        .button { display: inline-block; padding: 12px 24px; background: #dc2626; color: white; text-decoration: none; border-radius: 4px; }
        .details { background: white; padding: 15px; border-radius: 4px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Payment Failed</h1>
        </div>
        <div class="content">
            <p>Hi {{ recipient_name or "there" }},</p>
            <p>We were unable to process your payment. Here are the details:</p>

            <div class="details">
                <h3>Failed Payment Details</h3>
                <p><strong>Plan:</strong> {{ plan_name.title() }}</p>
                <p><strong>Amount:</strong> ₹{{ "%.2f"|format(amount/100) }}</p>
                <p><strong>Transaction ID:</strong> {{ transaction_id }}</p>
                {% if workspace_name %}
                <p><strong>Workspace:</strong> {{ workspace_name }}</p>
                {% endif %}
                {% if error_message %}
                <p><strong>Error:</strong> {{ error_message }}</p>
                {% endif %}
            </div>

            <p>Don't worry! You can try again with a different payment method or contact our support team for assistance.</p>

            <p style="text-align: center;">
                <a href="{{ retry_url }}" class="button">Try Payment Again</a>
            </p>
        </div>
        <div class="footer">
            <p>If you continue to experience issues, please contact our support team.</p>
        </div>
    </div>
</body>
</html>
        """

        template = Template(template_str)
        return template.render(
            recipient_name=recipient_name,
            plan_name=plan_name,
            amount=amount,
            transaction_id=transaction_id,
            error_message=error_message,
            workspace_name=workspace_name,
            retry_url=os.getenv("NEXT_PUBLIC_APP_URL", "https://raptorflow.com")
            + "/onboarding/plans",
        )

    def _render_trial_ending_template(
        self,
        recipient_name: Optional[str],
        trial_end: datetime,
        days_remaining: int,
        workspace_name: Optional[str] = None,
    ) -> str:
        """Render trial ending reminder template."""
        template_str = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Trial Ending</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #f59e0b; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; background: #f9fafb; }
        .footer { padding: 20px; text-align: center; font-size: 12px; color: #666; }
        .button { display: inline-block; padding: 12px 24px; background: #2563eb; color: white; text-decoration: none; border-radius: 4px; }
        .details { background: white; padding: 15px; border-radius: 4px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Your Trial is Ending Soon</h1>
        </div>
        <div class="content">
            <p>Hi {{ recipient_name or "there" }},</p>
            <p>Your free trial will end in <strong>{{ days_remaining }} days</strong> on {{ trial_end.strftime('%B %d, %Y') }}.</p>

            <div class="details">
                <h3>Trial Details</h3>
                <p><strong>Trial Ends:</strong> {{ trial_end.strftime('%B %d, %Y') }}</p>
                <p><strong>Days Remaining:</strong> {{ days_remaining }}</p>
                {% if workspace_name %}
                <p><strong>Workspace:</strong> {{ workspace_name }}</p>
                {% endif %}
            </div>

            <p>Don't lose access to your workspace! Choose a plan to continue using RaptorFlow.</p>

            <p style="text-align: center;">
                <a href="{{ plans_url }}" class="button">Choose a Plan</a>
            </p>
        </div>
        <div class="footer">
            <p>We hope you're enjoying RaptorFlow!</p>
        </div>
    </div>
</body>
</html>
        """

        template = Template(template_str)
        return template.render(
            recipient_name=recipient_name,
            trial_end=trial_end,
            days_remaining=days_remaining,
            workspace_name=workspace_name,
            plans_url=os.getenv("NEXT_PUBLIC_APP_URL", "https://raptorflow.com")
            + "/onboarding/plans",
        )

    def _render_renewal_template(
        self,
        recipient_name: Optional[str],
        plan_name: str,
        amount: int,
        next_billing_date: datetime,
        workspace_name: Optional[str] = None,
    ) -> str:
        """Render subscription renewal template."""
        template_str = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Subscription Renewed</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #10b981; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; background: #f9fafb; }
        .footer { padding: 20px; text-align: center; font-size: 12px; color: #666; }
        .button { display: inline-block; padding: 12px 24px; background: #2563eb; color: white; text-decoration: none; border-radius: 4px; }
        .details { background: white; padding: 15px; border-radius: 4px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Subscription Renewed</h1>
        </div>
        <div class="content">
            <p>Hi {{ recipient_name or "there" }},</p>
            <p>Your {{ plan_name }} subscription has been successfully renewed.</p>

            <div class="details">
                <h3>Renewal Details</h3>
                <p><strong>Plan:</strong> {{ plan_name.title() }}</p>
                <p><strong>Amount:</strong> ₹{{ "%.2f"|format(amount/100) }}</p>
                <p><strong>Next Billing:</strong> {{ next_billing_date.strftime('%B %d, %Y') }}</p>
                {% if workspace_name %}
                <p><strong>Workspace:</strong> {{ workspace_name }}</p>
                {% endif %}
            </div>

            <p>Your subscription will continue without interruption. You can manage your subscription settings in your dashboard.</p>

            <p style="text-align: center;">
                <a href="{{ dashboard_url }}" class="button">Go to Dashboard</a>
            </p>
        </div>
        <div class="footer">
            <p>Thank you for your continued support!</p>
        </div>
    </div>
</body>
</html>
        """

        template = Template(template_str)
        return template.render(
            recipient_name=recipient_name,
            plan_name=plan_name,
            amount=amount,
            next_billing_date=next_billing_date,
            workspace_name=workspace_name,
            dashboard_url=os.getenv("NEXT_PUBLIC_APP_URL", "https://raptorflow.com")
            + "/dashboard",
        )

    def _render_invoice_template(
        self,
        recipient_name: Optional[str],
        invoice_data: Dict[str, Any],
        workspace_name: Optional[str] = None,
    ) -> str:
        """Render invoice email template."""
        template_str = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Invoice</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #6366f1; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; background: #f9fafb; }
        .footer { padding: 20px; text-align: center; font-size: 12px; color: #666; }
        .invoice-table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        .invoice-table th, .invoice-table td { border: 1px solid #ddd; padding: 12px; text-align: left; }
        .invoice-table th { background: #f3f4f6; }
        .total-row { font-weight: bold; background: #f3f4f6; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Invoice #{{ invoice_data.invoice_number }}</h1>
        </div>
        <div class="content">
            <p>Hi {{ recipient_name or "there" }},</p>
            <p>Here's your invoice for your recent payment:</p>

            <table class="invoice-table">
                <tr>
                    <th>Description</th>
                    <th>Quantity</th>
                    <th>Unit Price</th>
                    <th>Total</th>
                </tr>
                {% for item in invoice_data.items %}
                <tr>
                    <td>{{ item.description }}</td>
                    <td>{{ item.quantity }}</td>
                    <td>₹{{ "%.2f"|format(item.unit_price/100) }}</td>
                    <td>₹{{ "%.2f"|format(item.total/100) }}</td>
                </tr>
                {% endfor %}
                <tr class="total-row">
                    <td colspan="3">Total Amount</td>
                    <td>₹{{ "%.2f"|format(invoice_data.total_amount/100) }}</td>
                </tr>
            </table>

            <div class="details">
                <h3>Invoice Details</h3>
                <p><strong>Invoice Number:</strong> {{ invoice_data.invoice_number }}</p>
                <p><strong>Date:</strong> {{ invoice_data.date.strftime('%B %d, %Y') }}</p>
                <p><strong>Due Date:</strong> {{ invoice_data.due_date.strftime('%B %d, %Y') }}</p>
                <p><strong>Status:</strong> {{ invoice_data.status.title() }}</p>
                {% if workspace_name %}
                <p><strong>Workspace:</strong> {{ workspace_name }}</p>
                {% endif %}
            </div>

            <p>A copy of this invoice has been saved to your account dashboard.</p>
        </div>
        <div class="footer">
            <p>Thank you for your business!</p>
        </div>
    </div>
</body>
</html>
        """

        template = Template(template_str)
        return template.render(
            recipient_name=recipient_name,
            invoice_data=invoice_data,
            workspace_name=workspace_name,
        )

    def _get_plan_template_file(self, plan_name: str) -> str:
        """Get the template file path for a specific plan."""
        plan_templates = {
            "starter": "templates/email/payment-confirmation-starter.html",
            "growth": "templates/email/payment-confirmation-growth.html",
            "enterprise": "templates/email/payment-confirmation-enterprise.html",
        }

        template_file = plan_templates.get(plan_name.lower())
        if not template_file:
            # Fallback to starter template for unknown plans
            template_file = plan_templates["starter"]
            logger.warning(f"Unknown plan '{plan_name}', using starter template")

        return template_file

    def _get_plan_subject(self, plan_name: str) -> str:
        """Get the email subject for a specific plan."""
        plan_subjects = {
            "starter": "Welcome to RaptorFlow - Starter Plan Activated! 🎉",
            "growth": "Great Choice! Your RaptorFlow Growth Plan is Active! 🚀",
            "enterprise": "Welcome to Enterprise Excellence! Your RaptorFlow Enterprise Plan is Ready! ⭐",
        }

        return plan_subjects.get(
            plan_name.lower(), f"Welcome to RaptorFlow - {plan_name.title()} Plan"
        )

    def _render_plan_specific_template(
        self,
        template_file: str,
        recipient_name: Optional[str],
        plan_name: str,
        amount: int,
        transaction_id: str,
        period_end: datetime,
        workspace_name: Optional[str],
        billing_cycle: str,
    ) -> str:
        """Render plan-specific email template."""
        try:
            # Read template file
            with open(template_file, "r", encoding="utf-8") as f:
                template_content = f.read()

            # Create Jinja2 template
            template = Template(template_content)

            # Format amount
            formatted_amount = f"₹{amount/100:.2f}"

            # Prepare template variables
            template_vars = {
                "user_name": recipient_name or "there",
                "plan_name": plan_name.title(),
                "amount": formatted_amount,
                "transaction_id": transaction_id,
                "payment_date": datetime.now().strftime("%B %d, %Y"),
                "billing_cycle": billing_cycle.title(),
                "dashboard_url": "https://app.raptorflow.com/dashboard",
                "help_url": "https://help.raptorflow.com",
                "unsubscribe_url": "https://app.raptorflow.com/unsubscribe",
                "privacy_url": "https://raptorflow.com/privacy",
                "workspace_name": workspace_name,
            }

            # Add plan-specific variables
            if plan_name.lower() == "enterprise":
                template_vars.update(
                    {
                        "account_manager_name": "Sarah Johnson",
                        "account_manager_email": "sarah.johnson@raptorflow.com",
                        "account_manager_phone": "+1-555-0123",
                        "agreement_id": f"AGR-{transaction_id}",
                        "contract_term": "Annual",
                        "sla_url": "https://raptorflow.com/sla",
                        "enterprise_upgrade_url": "https://raptorflow.com/enterprise",
                    }
                )
            elif plan_name.lower() == "growth":
                template_vars.update(
                    {"enterprise_upgrade_url": "https://raptorflow.com/enterprise"}
                )

            return template.render(**template_vars)

        except FileNotFoundError:
            logger.error(f"Template file not found: {template_file}")
            # Fallback to basic template
            return self._render_fallback_payment_confirmation(
                recipient_name,
                plan_name,
                amount,
                transaction_id,
                period_end,
                workspace_name,
            )
        except Exception as exc:
            logger.error(f"Error rendering template {template_file}: {exc}")
            # Fallback to basic template
            return self._render_fallback_payment_confirmation(
                recipient_name,
                plan_name,
                amount,
                transaction_id,
                period_end,
                workspace_name,
            )

    def _render_fallback_payment_confirmation(
        self,
        recipient_name: Optional[str],
        plan_name: str,
        amount: int,
        transaction_id: str,
        period_end: datetime,
        workspace_name: Optional[str],
    ) -> str:
        """Fallback payment confirmation template."""
        formatted_amount = f"₹{amount/100:.2f}"

        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="padding: 20px; background: #f8f9fa;">
                <h1 style="color: #333;">Payment Confirmed!</h1>
                <p>Hi {recipient_name or 'there'},</p>
                <p>Your {plan_name.title()} plan has been activated successfully.</p>
                <p><strong>Amount:</strong> {formatted_amount}<br>
                <strong>Transaction ID:</strong> {transaction_id}<br>
                <strong>Date:</strong> {datetime.now().strftime('%B %d, %Y')}</p>
                <a href="https://app.raptorflow.com/dashboard" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Go to Dashboard</a>
            </div>
        </body>
        </html>
        """


# Singleton instance
email_service = EmailService()
