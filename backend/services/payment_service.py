"""Payment service for PhonePe integration and subscription management."""

import hashlib
import hmac
import json
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional, List
from dataclasses import dataclass

import httpx
from core.supabase_mgr import get_supabase_admin
from core.webhook_security import webhook_security
from services.email_service import email_service, EmailRecipient

logger = logging.getLogger(__name__)


class PaymentError(Exception):
    """Structured payment service errors."""

    def __init__(self, message: str, error_type: str, context: Dict[str, Any] = None):
        super().__init__(message)
        self.error_type = error_type
        self.context = context or {}


@dataclass
class PaymentPlan:
    """Payment plan configuration."""

    name: str
    amount: int  # in paise
    currency: str = "INR"
    interval: str = "month"  # month, year
    trial_days: int = 7


@dataclass
class PaymentRequest:
    """Payment request data."""

    workspace_id: str
    plan: str
    amount: int
    customer_email: str
    customer_name: Optional[str] = None
    redirect_url: Optional[str] = None
    webhook_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class PaymentResponse:
    """Payment response data."""

    success: bool
    merchant_order_id: Optional[str] = None
    payment_url: Optional[str] = None
    phonepe_transaction_id: Optional[str] = None
    status: Optional[str] = None
    error: Optional[str] = None
    expires_at: Optional[datetime] = None


class PaymentService:
    """Payment service for PhonePe integration."""

    # Payment plans configuration
    PLANS = {
        "starter": PaymentPlan("starter", 4900, "INR", "month", 7),  # ₹49/month
        "growth": PaymentPlan("growth", 14900, "INR", "month", 7),  # ₹149/month
        "enterprise": PaymentPlan("enterprise", 49900, "INR", "month", 7),  # ₹499/month
    }

    def __init__(self):
        """Initialize payment service."""
        self.supabase = get_supabase_admin()
        self.merchant_id = os.getenv("PHONEPE_MERCHANT_ID")
        self.salt_key = os.getenv("PHONEPE_SALT_KEY")
        self.salt_index = os.getenv("PHONEPE_SALT_INDEX", "1")
        self.environment = os.getenv("PHONEPE_ENVIRONMENT", "sandbox")

        # PhonePe API URLs
        if self.environment == "production":
            self.base_url = "https://api.phonepe.com/apis/pg"
        else:
            self.base_url = "https://api.phonepe.com/apis/pg-sandbox"

        # Validate required environment variables
        if not self.merchant_id or not self.salt_key:
            raise PaymentError(
                "PHONEPE_MERCHANT_ID and PHONEPE_SALT_KEY are required",
                "MISSING_CREDENTIALS",
            )

    def initiate_payment(self, request: PaymentRequest) -> PaymentResponse:
        """Initiate a PhonePe payment."""
        try:
            # Validate plan
            if request.plan not in self.PLANS:
                raise PaymentError(
                    f"Invalid plan: {request.plan}",
                    "INVALID_PLAN",
                    {"plan": request.plan},
                )

            plan_config = self.PLANS[request.plan]

            # Validate amount matches plan
            if request.amount != plan_config.amount:
                raise PaymentError(
                    f"Amount mismatch for plan {request.plan}: expected {plan_config.amount}, got {request.amount}",
                    "AMOUNT_MISMATCH",
                    {
                        "plan": request.plan,
                        "expected": plan_config.amount,
                        "actual": request.amount,
                    },
                )

            # Generate merchant order ID
            merchant_order_id = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:6].upper()}"

            # Create payment transaction record
            transaction_data = {
                "workspace_id": request.workspace_id,
                "merchant_order_id": merchant_order_id,
                "amount": request.amount,
                "currency": request.currency or "INR",
                "status": "pending",
                "metadata": {
                    "plan": request.plan,
                    "customer_email": request.customer_email,
                    "customer_name": request.customer_name,
                    **(request.metadata or {}),
                },
            }

            result = (
                self.supabase.table("payment_transactions")
                .insert(transaction_data)
                .select("*")
                .single()
                .execute()
            )
            if not result.data:
                raise PaymentError(
                    "Failed to create payment transaction", "TRANSACTION_CREATE_ERROR"
                )

            transaction = result.data

            # Prepare PhonePe payment request
            phonepe_request = {
                "merchantId": self.merchant_id,
                "merchantTransactionId": merchant_order_id,
                "merchantUserId": request.workspace_id,
                "amount": request.amount,
                "redirectUrl": request.redirect_url
                or f"{os.getenv('NEXT_PUBLIC_APP_URL', 'http://localhost:3000')}/onboarding/plans/callback",
                "redirectMode": "REDIRECT",
                "callbackUrl": request.webhook_url
                or f"{os.getenv('NEXT_PUBLIC_API_URL', 'http://localhost:8000')}/api/payments/webhook",
                "paymentInstrument": {"type": "PAY_PAGE"},
                "deviceContext": {"deviceOS": "WEB"},
            }

            # Add customer info if provided
            if request.customer_email or request.customer_name:
                phonepe_request["customerInfo"] = {}
                if request.customer_email:
                    phonepe_request["customerInfo"][
                        "customerEmail"
                    ] = request.customer_email
                if request.customer_name:
                    phonepe_request["customerInfo"][
                        "customerName"
                    ] = request.customer_name

            # Generate X-VERIFY header
            payload = json.dumps(phonepe_request, separators=(",", ":"))
            base64_payload = self._encode_base64(payload)
            verify_string = f"{base64_payload}/pg/v1/pay{self.salt_key}"
            x_verify = (
                self._generate_sha256_checksum(verify_string) + f"###{self.salt_index}"
            )

            # Make PhonePe API call
            headers = {
                "Content-Type": "application/json",
                "X-VERIFY": x_verify,
                "X-MERCHANT-ID": self.merchant_id,
            }

            api_url = f"{self.base_url}/pg/v1/pay"
            request_body = {"request": base64_payload}

            with httpx.Client(timeout=30.0) as client:
                response = client.post(api_url, json=request_body, headers=headers)
                response.raise_for_status()
                phonepe_response = response.json()

            if phonepe_response.get("success"):
                payment_url = phonepe_response["data"]["instrumentResponse"][
                    "redirectInfo"
                ]["url"]
                phonepe_transaction_id = phonepe_response["data"][
                    "merchantTransactionId"
                ]

                # Update transaction with PhonePe response
                update_data = {
                    "phonepe_transaction_id": phonepe_transaction_id,
                    "phonepe_response": phonepe_response,
                    "status": "pending",
                }
                self.supabase.table("payment_transactions").update(update_data).eq(
                    "merchant_order_id", merchant_order_id
                ).execute()

                logger.info(
                    f"Payment initiated successfully: {merchant_order_id}, "
                    f"workspace: {request.workspace_id}, plan: {request.plan}"
                )

                return PaymentResponse(
                    success=True,
                    merchant_order_id=merchant_order_id,
                    payment_url=payment_url,
                    phonepe_transaction_id=phonepe_transaction_id,
                    status="pending",
                    expires_at=datetime.now(timezone.utc).replace(
                        hour=23, minute=59, second=59
                    ),
                )
            else:
                error_msg = phonepe_response.get("message", "Unknown error")
                logger.error(f"PhonePe payment initiation failed: {error_msg}")

                # Update transaction with error
                update_data = {"status": "failed", "phonepe_response": phonepe_response}
                self.supabase.table("payment_transactions").update(update_data).eq(
                    "merchant_order_id", merchant_order_id
                ).execute()

                return PaymentResponse(
                    success=False, merchant_order_id=merchant_order_id, error=error_msg
                )

        except PaymentError:
            raise
        except Exception as exc:
            logger.error(f"Payment initiation error: {exc}")
            raise PaymentError(
                f"Payment initiation failed: {exc}",
                "PAYMENT_INITIATION_ERROR",
                {"workspace_id": request.workspace_id, "plan": request.plan},
            ) from exc

    def check_payment_status(self, merchant_order_id: str) -> PaymentResponse:
        """Check payment status from PhonePe."""
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
                raise PaymentError(
                    f"Transaction not found: {merchant_order_id}",
                    "TRANSACTION_NOT_FOUND",
                    {"merchant_order_id": merchant_order_id},
                )

            transaction = result.data

            # If already completed, return cached status
            if transaction["status"] in ["completed", "failed"]:
                return PaymentResponse(
                    success=transaction["status"] == "completed",
                    merchant_order_id=merchant_order_id,
                    phonepe_transaction_id=transaction.get("phonepe_transaction_id"),
                    status=transaction["status"],
                    error=(
                        None
                        if transaction["status"] == "completed"
                        else "Payment failed"
                    ),
                )

            # Check status with PhonePe
            verify_string = (
                f"/pg/v1/status/{self.merchant_id}/{merchant_order_id}{self.salt_key}"
            )
            x_verify = (
                self._generate_sha256_checksum(verify_string) + f"###{self.salt_index}"
            )

            headers = {
                "Content-Type": "application/json",
                "X-VERIFY": x_verify,
                "X-MERCHANT-ID": self.merchant_id,
            }

            api_url = (
                f"{self.base_url}/pg/v1/status/{self.merchant_id}/{merchant_order_id}"
            )

            with httpx.Client(timeout=30.0) as client:
                response = client.get(api_url, headers=headers)
                response.raise_for_status()
                phonepe_response = response.json()

            if phonepe_response.get("success"):
                payment_data = phonepe_response["data"]
                phonepe_status = payment_data.get("state", "UNKNOWN")
                phonepe_transaction_id = payment_data.get("transactionId")

                # Map PhonePe status to our status
                if phonepe_status == "COMPLETED":
                    status = "completed"
                elif phonepe_status == "FAILED":
                    status = "failed"
                elif phonepe_status == "PENDING":
                    status = "pending"
                else:
                    status = "pending"

                # Update transaction in database
                update_data = {
                    "status": status,
                    "phonepe_transaction_id": phonepe_transaction_id,
                    "phonepe_response": phonepe_response,
                }
                self.supabase.table("payment_transactions").update(update_data).eq(
                    "merchant_order_id", merchant_order_id
                ).execute()

                # If payment completed, activate subscription
                if status == "completed":
                    self._activate_subscription(
                        transaction["workspace_id"], transaction["metadata"]["plan"]
                    )

                return PaymentResponse(
                    success=status == "completed",
                    merchant_order_id=merchant_order_id,
                    phonepe_transaction_id=phonepe_transaction_id,
                    status=status,
                    amount=transaction["amount"],
                )
            else:
                error_msg = phonepe_response.get("message", "Unknown error")
                logger.error(f"PhonePe status check failed: {error_msg}")
                return PaymentResponse(
                    success=False, merchant_order_id=merchant_order_id, error=error_msg
                )

        except PaymentError:
            raise
        except Exception as exc:
            logger.error(f"Payment status check error: {exc}")
            raise PaymentError(
                f"Payment status check failed: {exc}",
                "STATUS_CHECK_ERROR",
                {"merchant_order_id": merchant_order_id},
            ) from exc

    def validate_webhook(self, authorization: str, body: str) -> Dict[str, Any]:
        """Validate PhonePe webhook signature with enhanced security."""
        try:
            # Extract X-VERIFY from authorization header
            if not authorization:
                raise PaymentError(
                    "Missing authorization header", "MISSING_WEBHOOK_HEADER"
                )

            # Handle both "X-VERIFY " and raw signature formats
            if authorization.startswith("X-VERIFY "):
                x_verify = authorization[9:]  # Remove "X-VERIFY " prefix
            else:
                x_verify = authorization

            # Split signature and salt index
            parts = x_verify.split("###")
            if len(parts) != 2:
                raise PaymentError(
                    "Invalid X-VERIFY format", "INVALID_WEBHOOK_SIGNATURE"
                )

            signature, salt_index = parts

            # Parse webhook body first to validate structure
            webhook_data = json.loads(body)

            # Use webhook security manager for comprehensive validation
            webhook_security.validate_webhook(webhook_data, signature, self.salt_key)

            return {"valid": True, "data": webhook_data}

        except json.JSONDecodeError as exc:
            raise PaymentError(
                f"Invalid webhook JSON: {exc}", "INVALID_WEBHOOK_JSON"
            ) from exc
        except PaymentError:
            raise
        except Exception as exc:
            raise PaymentError(
                f"Webhook validation failed: {exc}", "WEBHOOK_VALIDATION_ERROR"
            ) from exc

    def process_webhook_callback(self, webhook_data: Dict[str, Any]) -> bool:
        """Process PhonePe webhook callback."""
        try:
            merchant_transaction_id = webhook_data.get("merchantTransactionId")
            code = webhook_data.get("code")
            data = webhook_data.get("data", {})

            if not merchant_transaction_id:
                raise PaymentError(
                    "Missing merchantTransactionId in webhook", "MISSING_TRANSACTION_ID"
                )

            # Get transaction from database
            result = (
                self.supabase.table("payment_transactions")
                .select("*")
                .eq("merchant_order_id", merchant_transaction_id)
                .single()
                .execute()
            )
            if not result.data:
                logger.warning(
                    f"Webhook for unknown transaction: {merchant_transaction_id}"
                )
                return False

            transaction = result.data

            # Process based on callback code
            if code == "PAYMENT_SUCCESS":
                return self._process_payment_success(transaction, data)
            elif code == "PAYMENT_ERROR":
                return self._process_payment_failure(transaction, data)
            else:
                logger.warning(f"Unknown webhook code: {code}")
                return False

        except Exception as exc:
            logger.error(f"Webhook processing error: {exc}")
            return False

    def get_payment_plans(self) -> List[Dict[str, Any]]:
        """Get available payment plans."""
        return [
            {
                "name": plan.name,
                "amount": plan.amount,
                "currency": plan.currency,
                "interval": plan.interval,
                "trial_days": plan.trial_days,
                "display_amount": f"₹{plan.amount / 100:.0f}",
            }
            for plan in self.PLANS.values()
        ]

    # ------------------------------------------------------------------
    # Private helper methods
    # ------------------------------------------------------------------

    def _encode_base64(self, data: str) -> str:
        """Encode string to base64."""
        import base64

        return base64.b64encode(data.encode()).decode()

    def _generate_sha256_checksum(self, data: str) -> str:
        """Generate SHA256 checksum."""
        return hashlib.sha256(data.encode()).hexdigest()

    def _activate_subscription(self, workspace_id: str, plan: str) -> bool:
        """Activate subscription for workspace."""
        try:
            # Calculate subscription period
            now = datetime.now(timezone.utc)
            period_end = (
                now.replace(day=28)
                if now.day <= 28
                else now.replace(month=now.month + 1, day=28)
            )

            # Create or update subscription
            subscription_data = {
                "workspace_id": workspace_id,
                "plan": plan,
                "status": "active",
                "current_period_start": now.isoformat(),
                "current_period_end": period_end.isoformat(),
            }

            # Use upsert function
            result = self.supabase.rpc(
                "upsert_subscription", subscription_data
            ).execute()

            if result.data:
                logger.info(
                    f"Subscription activated for workspace {workspace_id}, plan: {plan}"
                )

                # Send confirmation email
                self._send_payment_confirmation_email(workspace_id, plan)

                return True
            else:
                logger.error(
                    f"Failed to activate subscription for workspace {workspace_id}"
                )
                return False

        except Exception as exc:
            logger.error(f"Subscription activation error: {exc}")
            return False

    def _process_payment_success(
        self, transaction: Dict[str, Any], phonepe_data: Dict[str, Any]
    ) -> bool:
        """Process successful payment webhook."""
        try:
            # Update transaction status
            update_data = {
                "status": "completed",
                "phonepe_response": phonepe_data,
                "payment_method": phonepe_data.get("paymentInstrument", {}).get(
                    "type", "unknown"
                ),
            }
            self.supabase.table("payment_transactions").update(update_data).eq(
                "id", transaction["id"]
            ).execute()

            # Activate subscription
            plan = transaction["metadata"]["plan"]
            success = self._activate_subscription(transaction["workspace_id"], plan)

            if success:
                logger.info(
                    f"Payment success processed: {transaction['merchant_order_id']}"
                )
            else:
                logger.error(
                    f"Failed to activate subscription after payment success: {transaction['merchant_order_id']}"
                )

            return success

        except Exception as exc:
            logger.error(f"Payment success processing error: {exc}")
            return False

    def _process_payment_failure(
        self, transaction: Dict[str, Any], phonepe_data: Dict[str, Any]
    ) -> bool:
        """Process failed payment webhook."""
        try:
            # Update transaction status
            update_data = {
                "status": "failed",
                "phonepe_response": phonepe_data,
                "payment_method": phonepe_data.get("paymentInstrument", {}).get(
                    "type", "unknown"
                ),
            }
            self.supabase.table("payment_transactions").update(update_data).eq(
                "id", transaction["id"]
            ).execute()

            # Send failure email
            self._send_payment_failure_email(transaction, phonepe_data)

            logger.info(
                f"Payment failure processed: {transaction['merchant_order_id']}"
            )
            return True

        except Exception as exc:
            logger.error(f"Payment failure processing error: {exc}")
            return False

    def _send_payment_confirmation_email(self, workspace_id: str, plan: str) -> None:
        """Send payment confirmation email."""
        try:
            # Get workspace and user details
            workspace_result = (
                self.supabase.table("workspaces")
                .select("*")
                .eq("id", workspace_id)
                .single()
                .execute()
            )
            if not workspace_result.data:
                return

            workspace = workspace_result.data
            user_result = (
                self.supabase.table("users")
                .select("*")
                .eq("id", workspace["owner_id"])
                .single()
                .execute()
            )
            if not user_result.data:
                return

            user = user_result.data

            # Get latest transaction
            transaction_result = (
                self.supabase.table("payment_transactions")
                .select("*")
                .eq("workspace_id", workspace_id)
                .eq("status", "completed")
                .order("created_at", desc=True)
                .limit(1)
                .execute()
            )

            if not transaction_result.data:
                return

            transaction = transaction_result.data[0]

            # Send email
            recipient = EmailRecipient(email=user["email"], name=user.get("full_name"))
            plan_config = self.PLANS[plan]

            email_service.send_payment_confirmation(
                recipient=recipient,
                plan_name=plan,
                amount=transaction["amount"],
                transaction_id=transaction["merchant_order_id"],
                period_end=datetime.now(timezone.utc).replace(
                    month=datetime.now().month + 1, day=28
                ),
                workspace_name=workspace["name"],
            )

        except Exception as exc:
            logger.error(f"Failed to send payment confirmation email: {exc}")

    def _send_payment_failure_email(
        self, transaction: Dict[str, Any], phonepe_data: Dict[str, Any]
    ) -> None:
        """Send payment failure email."""
        try:
            # Get workspace and user details
            workspace_result = (
                self.supabase.table("workspaces")
                .select("*")
                .eq("id", transaction["workspace_id"])
                .single()
                .execute()
            )
            if not workspace_result.data:
                return

            workspace = workspace_result.data
            user_result = (
                self.supabase.table("users")
                .select("*")
                .eq("id", workspace["owner_id"])
                .single()
                .execute()
            )
            if not user_result.data:
                return

            user = user_result.data

            # Send email
            recipient = EmailRecipient(email=user["email"], name=user.get("full_name"))
            plan = transaction["metadata"]["plan"]

            email_service.send_payment_failure(
                recipient=recipient,
                plan_name=plan,
                amount=transaction["amount"],
                transaction_id=transaction["merchant_order_id"],
                error_message=phonepe_data.get("message"),
                workspace_name=workspace["name"],
            )

        except Exception as exc:
            logger.error(f"Failed to send payment failure email: {exc}")


# Singleton instance
payment_service = PaymentService()
