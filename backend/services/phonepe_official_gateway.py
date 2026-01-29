"""
Official PhonePe Payment Gateway
Single source of truth for all PhonePe payment operations using official SDK v2.1.7
"""

import hashlib
import hmac
import json
import logging
import os
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional, List
from dataclasses import dataclass
from base64 import b64encode

import httpx
from phonepe.sdk.pg.payments import PhonePePayments
from phonepe.sdk.pg.common.models import PhonePeConfig, Environment

from core.supabase_mgr import get_supabase_admin
from core.webhook_security import webhook_security
from .email_service import EmailService, EmailRecipient


@dataclass
class PaymentRequest:
    """Payment request data structure"""

    workspace_id: str
    plan: str
    amount: int  # Amount in paise (₹1 = 100 paise)
    customer_email: str
    customer_name: str
    redirect_url: Optional[str] = None
    webhook_url: Optional[str] = None
    idempotency_key: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class PaymentResponse:
    """Payment response data structure"""

    success: bool
    merchant_order_id: str
    payment_url: Optional[str] = None
    phonepe_transaction_id: Optional[str] = None
    status: str = "pending"
    error: Optional[str] = None
    expires_at: Optional[datetime] = None


@dataclass
class PaymentStatus:
    """Payment status response"""

    success: bool
    status: str
    phonepe_transaction_id: Optional[str] = None
    amount: Optional[int] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


class PaymentError(Exception):
    """Payment processing error"""

    def __init__(
        self, message: str, error_type: str, context: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_type = error_type
        self.context = context or {}
        super().__init__(message)


class PhonePeOfficialGateway:
    """
    Official PhonePe Payment Gateway
    Single source of truth for all PhonePe payment operations
    """

    # Payment plans configuration
    PLANS = {
        "starter": {"amount": 4900, "name": "STARTER"},
        "growth": {"amount": 14900, "name": "GROWTH"},
        "enterprise": {"amount": 49900, "name": "ENTERPRISE"},
    }

    def __init__(self):
        """Initialize PhonePe gateway with official SDK"""
        self.logger = logging.getLogger(__name__)
        self.supabase = get_supabase_admin()
        self.email_service = EmailService()

        # Initialize PhonePe SDK
        self.merchant_id = os.getenv("PHONEPE_MERCHANT_ID")
        self.salt_key = os.getenv("PHONEPE_SALT_KEY")
        self.salt_index = os.getenv("PHONEPE_SALT_INDEX", "1")
        self.environment = os.getenv("PHONEPE_ENVIRONMENT", "sandbox")

        if not all([self.merchant_id, self.salt_key]):
            raise PaymentError(
                "PhonePe credentials not configured", "MISSING_CREDENTIALS"
            )

        # Configure PhonePe SDK
        config = PhonePeConfig(
            merchant_id=self.merchant_id,
            salt_key=self.salt_key,
            salt_index=int(self.salt_index),
            environment=(
                Environment.SANDBOX
                if self.environment == "sandbox"
                else Environment.PRODUCTION
            ),
        )

        self.phonepe = PhonePePayments(config)

        self.logger.info(f"PhonePe gateway initialized for {self.environment}")

    def initiate_payment(self, request: PaymentRequest) -> PaymentResponse:
        """
        Initiate payment using official PhonePe SDK
        """
        try:
            # Validate request
            self._validate_payment_request(request)

            # Generate unique order ID
            merchant_order_id = self._generate_order_id()

            # Check idempotency if key provided
            if request.idempotency_key:
                existing_response = self._check_idempotency(request.idempotency_key)
                if existing_response:
                    self.logger.info(
                        f"Returning cached response for idempotency key: {request.idempotency_key}"
                    )
                    return existing_response

            # Create payment record
            transaction_data = {
                "workspace_id": request.workspace_id,
                "merchant_order_id": merchant_order_id,
                "amount": request.amount,
                "plan": request.plan,
                "customer_email": request.customer_email,
                "customer_name": request.customer_name,
                "status": "pending",
                "payment_method": "phonepe",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "metadata": request.metadata or {},
            }

            # Store transaction in database
            result = (
                self.supabase.table("payment_transactions")
                .insert(transaction_data)
                .select()
                .single()
                .execute()
            )

            if not result.data:
                raise PaymentError(
                    "Failed to create payment transaction", "DATABASE_ERROR"
                )

            transaction = result.data

            # Prepare PhonePe payment request
            phonepe_request = {
                "merchantTransactionId": merchant_order_id,
                "amount": request.amount,
                "merchantUserId": request.workspace_id,
                "redirectUrl": request.redirect_url
                or f"{os.getenv('NEXT_PUBLIC_APP_URL')}/onboarding/plans/callback",
                "redirectMode": "POST",
                "callbackUrl": request.webhook_url
                or f"{os.getenv('NEXT_PUBLIC_APP_URL')}/api/webhooks/phonepe",
                "paymentInstrument": {"type": "PAY_PAGE"},
                "deviceContext": {"deviceOS": "WEB"},
            }

            # Call PhonePe SDK
            try:
                phonepe_response = self.phonepe.pay(phonepe_request)

                if not phonepe_response.success:
                    raise PaymentError(
                        f"PhonePe API error: {phonepe_response.message}",
                        "PHONEPE_API_ERROR",
                    )

                # Update transaction with PhonePe details
                self.supabase.table("payment_transactions").update(
                    {
                        "phonepe_transaction_id": phonepe_response.data.merchantTransactionId,
                        "payment_url": phonepe_response.data.instrumentResponse.redirectInfo.url,
                        "expires_at": datetime.now(timezone.utc).isoformat(),
                    }
                ).eq("id", transaction["id"]).execute()

                response = PaymentResponse(
                    success=True,
                    merchant_order_id=merchant_order_id,
                    payment_url=phonepe_response.data.instrumentResponse.redirectInfo.url,
                    phonepe_transaction_id=phonepe_response.data.merchantTransactionId,
                    status="pending",
                    expires_at=datetime.now(timezone.utc),
                )

                # Store idempotency response if key provided
                if request.idempotency_key:
                    self._store_idempotency_response(request.idempotency_key, response)

                self.logger.info(f"Payment initiated successfully: {merchant_order_id}")
                return response

            except Exception as e:
                # Update transaction status to failed
                self.supabase.table("payment_transactions").update(
                    {
                        "status": "failed",
                        "error_message": str(e),
                        "failed_at": datetime.now(timezone.utc).isoformat(),
                    }
                ).eq("id", transaction["id"]).execute()

                raise PaymentError(
                    f"Payment initiation failed: {str(e)}", "PAYMENT_INITIATION_FAILED"
                )

        except PaymentError:
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error in payment initiation: {str(e)}")
            raise PaymentError(
                "Payment initiation failed due to internal error",
                "INTERNAL_ERROR",
                {"original_error": str(e)},
            )

    def check_payment_status(self, merchant_order_id: str) -> PaymentStatus:
        """
        Check payment status using official PhonePe SDK
        """
        try:
            # Get transaction from database
            result = (
                self.supabase.table("payment_transactions")
                .select("*")
                .eq("merchant_order_id", merchant_order_id)
                .single()
                .execute()
            )

            if not result.data:
                raise PaymentError("Transaction not found", "TRANSACTION_NOT_FOUND")

            transaction = result.data

            # If already completed, return cached status
            if transaction["status"] in ["completed", "failed"]:
                return PaymentStatus(
                    success=True,
                    status=transaction["status"],
                    phonepe_transaction_id=transaction.get("phonepe_transaction_id"),
                    amount=transaction["amount"],
                    completed_at=(
                        datetime.fromisoformat(transaction["completed_at"])
                        if transaction.get("completed_at")
                        else None
                    ),
                )

            # Check status with PhonePe SDK
            try:
                phonepe_response = self.phonepe.get_transaction_status(
                    merchant_order_id
                )

                if not phonepe_response.success:
                    raise PaymentError(
                        f"PhonePe status check error: {phonepe_response.message}",
                        "PHONEPE_STATUS_ERROR",
                    )

                phonepe_data = phonepe_response.data
                new_status = self._map_phonepe_status(phonepe_data.state)

                # Update transaction in database
                update_data = {
                    "status": new_status,
                    "phonepe_transaction_id": phonepe_data.transactionId,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                }

                if new_status == "completed":
                    update_data["completed_at"] = datetime.now(timezone.utc).isoformat()
                    # Activate subscription
                    self._activate_subscription(
                        transaction["workspace_id"], transaction["plan"]
                    )

                    # Send confirmation email
                    self._send_confirmation_email(transaction)

                elif new_status == "failed":
                    update_data["failed_at"] = datetime.now(timezone.utc).isoformat()
                    update_data["error_message"] = phonepe_data.responseMessage

                self.supabase.table("payment_transactions").update(update_data).eq(
                    "id", transaction["id"]
                ).execute()

                return PaymentStatus(
                    success=True,
                    status=new_status,
                    phonepe_transaction_id=phonepe_data.transactionId,
                    amount=phonepe_data.amount,
                    completed_at=(
                        datetime.now(timezone.utc)
                        if new_status == "completed"
                        else None
                    ),
                )

            except Exception as e:
                self.logger.error(f"PhonePe status check failed: {str(e)}")
                raise PaymentError(
                    f"Status check failed: {str(e)}", "STATUS_CHECK_FAILED"
                )

        except PaymentError:
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error in status check: {str(e)}")
            raise PaymentError(
                "Status check failed due to internal error",
                "INTERNAL_ERROR",
                {"original_error": str(e)},
            )

    def process_webhook(self, webhook_data: Dict[str, Any]) -> bool:
        """
        Process PhonePe webhook with enhanced security
        """
        try:
            # Validate webhook signature
            if not self._validate_webhook_signature(webhook_data):
                raise PaymentError(
                    "Invalid webhook signature", "WEBHOOK_SIGNATURE_INVALID"
                )

            # Validate webhook structure
            merchant_order_id = webhook_data.get("merchantTransactionId")
            if not merchant_order_id:
                raise PaymentError(
                    "Missing merchantTransactionId in webhook", "WEBHOOK_INVALID_DATA"
                )

            # Check for replay attacks
            if self._is_webhook_processed(webhook_data):
                self.logger.warning(f"Duplicate webhook received: {merchant_order_id}")
                return True  # Return success for idempotency

            # Get transaction
            result = (
                self.supabase.table("payment_transactions")
                .select("*")
                .eq("merchant_order_id", merchant_order_id)
                .single()
                .execute()
            )

            if not result.data:
                raise PaymentError(
                    "Webhook for unknown transaction", "WEBHOOK_UNKNOWN_TRANSACTION"
                )

            transaction = result.data

            # Process webhook based on status
            webhook_status = webhook_data.get("code")
            phonepe_data = webhook_data.get("data", {})

            if webhook_status == "PAYMENT_SUCCESS":
                new_status = "completed"
                completed_at = datetime.now(timezone.utc).isoformat()

                # Update transaction
                self.supabase.table("payment_transactions").update(
                    {
                        "status": new_status,
                        "phonepe_transaction_id": phonepe_data.get("transactionId"),
                        "completed_at": completed_at,
                        "webhook_processed_at": datetime.now(timezone.utc).isoformat(),
                    }
                ).eq("id", transaction["id"]).execute()

                # Activate subscription
                self._activate_subscription(
                    transaction["workspace_id"], transaction["plan"]
                )

                # Send confirmation email
                self._send_confirmation_email(transaction)

            elif webhook_status == "PAYMENT_FAILED":
                new_status = "failed"
                failed_at = datetime.now(timezone.utc).isoformat()

                # Update transaction
                self.supabase.table("payment_transactions").update(
                    {
                        "status": new_status,
                        "phonepe_transaction_id": phonepe_data.get("transactionId"),
                        "failed_at": failed_at,
                        "error_message": phonepe_data.get(
                            "responseMessage", "Payment failed"
                        ),
                        "webhook_processed_at": datetime.now(timezone.utc).isoformat(),
                    }
                ).eq("id", transaction["id"]).execute()

                # Send failure email
                self._send_failure_email(transaction)

            # Mark webhook as processed
            self._mark_webhook_processed(webhook_data)

            self.logger.info(f"Webhook processed successfully: {merchant_order_id}")
            return True

        except PaymentError:
            raise
        except Exception as e:
            self.logger.error(f"Webhook processing failed: {str(e)}")
            raise PaymentError(
                "Webhook processing failed",
                "WEBHOOK_PROCESSING_FAILED",
                {"original_error": str(e)},
            )

    def get_payment_plans(self) -> List[Dict[str, Any]]:
        """Get available payment plans"""
        plans = []
        for plan_key, plan_config in self.PLANS.items():
            plans.append(
                {
                    "name": plan_key,
                    "display_name": plan_config["name"],
                    "amount": plan_config["amount"],
                    "currency": "INR",
                    "interval": "month",
                    "trial_days": 14 if plan_key == "starter" else 0,
                    "display_amount": f"₹{plan_config['amount'] // 100}",
                }
            )
        return plans

    def _validate_payment_request(self, request: PaymentRequest):
        """Validate payment request"""
        if request.plan not in self.PLANS:
            raise PaymentError(f"Invalid plan: {request.plan}", "INVALID_PLAN")

        expected_amount = self.PLANS[request.plan]["amount"]
        if request.amount != expected_amount:
            raise PaymentError(
                f"Amount mismatch for plan {request.plan}: expected {expected_amount}, got {request.amount}",
                "AMOUNT_MISMATCH",
            )

        if request.amount < 100:  # Minimum ₹1
            raise PaymentError("Amount must be at least ₹1", "AMOUNT_TOO_LOW")

        if request.amount > 10000000:  # Maximum ₹1,00,000
            raise PaymentError("Amount exceeds maximum limit", "AMOUNT_TOO_HIGH")

    def _generate_order_id(self) -> str:
        """Generate unique merchant order ID"""
        timestamp = int(time.time())
        random_str = uuid.uuid4().hex[:8].upper()
        return f"ORD{timestamp}{random_str}"

    def _map_phonepe_status(self, phonepe_status: str) -> str:
        """Map PhonePe status to internal status"""
        status_mapping = {
            "COMPLETED": "completed",
            "FAILED": "failed",
            "PENDING": "pending",
            "USER_NOT_LOGGED_IN": "failed",
            "AUTHORIZATION_FAILED": "failed",
            "TRANSACTION_NOT_FOUND": "pending",
        }
        return status_mapping.get(phonepe_status, "pending")

    def _activate_subscription(self, workspace_id: str, plan: str):
        """Activate subscription for workspace"""
        try:
            # Calculate subscription period
            now = datetime.now(timezone.utc)
            period_start = now
            period_end = now.replace(year=now.year + 1)  # 1 year from now

            # Create or update subscription
            self.supabase.rpc(
                "upsert_subscription",
                {
                    "workspace_id": workspace_id,
                    "plan": plan,
                    "status": "active",
                    "current_period_start": period_start.isoformat(),
                    "current_period_end": period_end.isoformat(),
                },
            ).execute()

            self.logger.info(f"Subscription activated for workspace {workspace_id}")

        except Exception as e:
            self.logger.error(f"Failed to activate subscription: {str(e)}")
            # Don't fail the payment if subscription activation fails

    def _send_confirmation_email(self, transaction: Dict[str, Any]):
        """Send payment confirmation email"""
        try:
            plan_config = self.PLANS.get(transaction["plan"], {})
            amount_display = f"₹{transaction['amount'] // 100}"

            recipient = EmailRecipient(
                email=transaction["customer_email"],
                name=transaction["customer_name"],
                template="payment_confirmation",
                data={
                    "plan_name": plan_config.get("name", transaction["plan"]),
                    "amount": amount_display,
                    "transaction_id": transaction["phonepe_transaction_id"],
                    "merchant_order_id": transaction["merchant_order_id"],
                    "workspace_id": transaction["workspace_id"],
                },
            )

            self.email_service.send_email(recipient)

        except Exception as e:
            self.logger.error(f"Failed to send confirmation email: {str(e)}")

    def _send_failure_email(self, transaction: Dict[str, Any]):
        """Send payment failure email"""
        try:
            recipient = EmailRecipient(
                email=transaction["customer_email"],
                name=transaction["customer_name"],
                template="payment_failure",
                data={
                    "transaction_id": transaction["merchant_order_id"],
                    "error_message": transaction.get("error_message", "Payment failed"),
                },
            )

            self.email_service.send_email(recipient)

        except Exception as e:
            self.logger.error(f"Failed to send failure email: {str(e)}")

    def _validate_webhook_signature(self, webhook_data: Dict[str, Any]) -> bool:
        """Validate PhonePe webhook signature with enhanced security"""
        try:
            # Get PhonePe salt key
            salt_key = os.getenv("PHONEPE_SALT_KEY")
            if not salt_key:
                raise PaymentError(
                    "PhonePe salt key not configured", "MISSING_SALT_KEY"
                )

            # Extract signature from webhook data or header
            signature = webhook_data.get("signature") or webhook_data.get("x-verify")
            if not signature:
                raise PaymentError("Missing webhook signature", "MISSING_SIGNATURE")

            # Use webhook security manager for comprehensive validation
            webhook_security.validate_webhook(webhook_data, signature, salt_key)
            return True

        except Exception as e:
            self.logger.error(f"Webhook signature validation failed: {str(e)}")
            return False

    def _is_webhook_processed(self, webhook_data: Dict[str, Any]) -> bool:
        """Check if webhook has been processed (replay protection)"""
        # This would check Redis or database for processed webhook IDs
        # For now, return False (should be implemented properly)
        return False

    def _mark_webhook_processed(self, webhook_data: Dict[str, Any]):
        """Mark webhook as processed to prevent replay attacks"""
        # This would store webhook ID in Redis or database
        # For now, do nothing (should be implemented properly)
        pass

    def _check_idempotency(self, idempotency_key: str) -> Optional[PaymentResponse]:
        """Check for existing response using idempotency key"""
        # This would check Redis for cached response
        # For now, return None (should be implemented properly)
        return None

    def _store_idempotency_response(
        self, idempotency_key: str, response: PaymentResponse
    ):
        """Store response for idempotency"""
        # This would store response in Redis with TTL
        # For now, do nothing (should be implemented properly)
        pass


# Global instance
phonepe_gateway = PhonePeOfficialGateway()
