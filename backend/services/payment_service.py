import json
import logging
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional, Protocol
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse
from uuid import uuid4

from core.config import get_settings
from db import get_db_connection

BRIDGE_PATH = Path(__file__).resolve().parents[1] / "phonepe" / "phonepeBridge.js"
FINAL_ORDER_STATES = {"COMPLETED", "SUCCESS"}

logger = logging.getLogger("raptorflow.payment_service")


class PhonePeCallbackError(RuntimeError):
    """Raised when PhonePe callback validation fails."""


class PhonePeGateway(Protocol):
    def pay(
        self, merchant_order_id: str, amount_paise: int, redirect_url: str
    ) -> Dict[str, Any]: ...

    def get_order_status(self, merchant_order_id: str) -> Dict[str, Any]: ...

    def validate_callback(
        self,
        username: str,
        password: str,
        authorization: str,
        response_body: str,
    ) -> Dict[str, Any]: ...


class PhonePeNodeClient:
    """Bridge that calls the PhonePe Node SDK via a Node.js helper script."""

    def __init__(self, bridge_path: Path = BRIDGE_PATH) -> None:
        self.bridge_path = bridge_path

    def _run(self, action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        result = subprocess.run(
            ["node", str(self.bridge_path), action],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            error_message = (result.stderr or result.stdout).strip()
            raise RuntimeError(f"PhonePe SDK error: {error_message}")

        if not result.stdout:
            return {}

        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise RuntimeError("PhonePe SDK returned invalid JSON") from exc

    def pay(
        self, merchant_order_id: str, amount_paise: int, redirect_url: str
    ) -> Dict[str, Any]:
        return self._run(
            "pay",
            {
                "merchantOrderId": merchant_order_id,
                "amount": amount_paise,
                "redirectUrl": redirect_url,
            },
        )

    def get_order_status(self, merchant_order_id: str) -> Dict[str, Any]:
        return self._run("status", {"merchantOrderId": merchant_order_id})

    def validate_callback(
        self,
        username: str,
        password: str,
        authorization: str,
        response_body: str,
    ) -> Dict[str, Any]:
        return self._run(
            "validate",
            {
                "username": username,
                "password": password,
                "authorization": authorization,
                "responseBody": response_body,
            },
        )


class PaymentService:
    """
    PhonePe Standard Checkout v2 integration with subscription management.
    Handles transaction initiation, status verification, webhook validation, and subscription lifecycle.
    """

    def __init__(self, gateway: Optional[PhonePeGateway] = None):
        self.settings = get_settings()
        self.gateway = gateway or PhonePeNodeClient()
        self.order_states: Dict[str, str] = {}
        self.processed_orders: set[str] = set()
        self.initiated_orders: set[str] = set()
        self._validated = False

    def _validate_phonepe_settings(self) -> None:
        env_value = str(self.settings.PHONEPE_ENV or "").upper()
        if env_value not in {"SANDBOX", "PRODUCTION", "UAT"}:
            raise ValueError(
                "PHONEPE_ENV must be set to SANDBOX, PRODUCTION, or UAT (case-insensitive)."
            )

        has_client_creds = all(
            [
                self.settings.PHONEPE_CLIENT_ID,
                self.settings.PHONEPE_CLIENT_SECRET,
                self.settings.PHONEPE_CLIENT_VERSION,
            ]
        )
        has_merchant_creds = all(
            [
                self.settings.PHONEPE_MERCHANT_ID,
                self.settings.PHONEPE_SALT_KEY,
                self.settings.PHONEPE_SALT_INDEX,
            ]
        )

        if not has_client_creds and not has_merchant_creds:
            raise ValueError(
                "Missing PhonePe configuration: set client credentials or merchant credentials."
            )

    def _ensure_webhook_credentials(self) -> None:
        if not (
            self.settings.PHONEPE_WEBHOOK_USERNAME
            and self.settings.PHONEPE_WEBHOOK_PASSWORD
        ):
            raise ValueError(
                "Missing PhonePe webhook credentials: PHONEPE_WEBHOOK_USERNAME/PHONEPE_WEBHOOK_PASSWORD."
            )

    def initiate_payment(
        self, user_id: str, amount: float, transaction_id: str, redirect_url: str
    ) -> Dict[str, Any]:
        """Initiates a payment request with PhonePe."""
        self._ensure_phonepe_ready()
        merchant_order_id = transaction_id or str(uuid4())
        amount_paise = int(round(amount * 100))

        response = self.gateway.pay(merchant_order_id, amount_paise, redirect_url)
        self.initiated_orders.add(merchant_order_id)

        return {
            "url": response.get("redirectUrl"),
            "merchantOrderId": merchant_order_id,
        }

    def get_order_status(self, merchant_order_id: str) -> Dict[str, Any]:
        """Fetch the order status from PhonePe."""
        self._ensure_phonepe_ready()
        return self.gateway.get_order_status(merchant_order_id)

    def _record_order_state(self, merchant_order_id: str, state: Optional[str]) -> bool:
        if not state:
            return False

        if self.order_states.get(merchant_order_id) == state:
            return False

        self.order_states[merchant_order_id] = state

        if state in FINAL_ORDER_STATES:
            self.processed_orders.add(merchant_order_id)

        return True

    def handle_webhook(self, authorization: str, response_body: str) -> Dict[str, str]:
        """Validates webhook callback and updates order state idempotently."""
        self._ensure_phonepe_ready()
        self._ensure_webhook_credentials()
        try:
            callback = self.gateway.validate_callback(
                self.settings.PHONEPE_WEBHOOK_USERNAME,
                self.settings.PHONEPE_WEBHOOK_PASSWORD,
                authorization,
                response_body,
            )
        except RuntimeError as exc:
            raise PhonePeCallbackError(str(exc)) from exc

        payload = callback.get("payload") or {}
        merchant_order_id = payload.get("merchantOrderId")
        if not merchant_order_id:
            raise ValueError("Missing merchantOrderId in callback payload.")

        if merchant_order_id in self.processed_orders:
            return {"status": "already_processed"}

        order_status = self.get_order_status(merchant_order_id)
        self._record_order_state(merchant_order_id, order_status.get("state"))

        return {"status": "received"}

    def _ensure_phonepe_ready(self) -> None:
        if not self._validated:
            self._validate_phonepe_settings()
            self._validated = True

    async def create_payment_session(
        self,
        workspace_id: str,
        plan_id: str,
        amount: float,
        currency: str = "INR",
        return_url: str = None,
        callback_url: str = None,
        promo_code: Optional[str] = None,
        discount_amount: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Create a payment session and record transaction in database."""
        self._ensure_phonepe_ready()

        merchant_order_id = str(uuid4())
        amount_paise = int(round(amount * 100))

        # Record transaction in database
        async with get_db_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    INSERT INTO payment_transactions
                    (workspace_id, plan_id, merchant_order_id, amount, currency, status, payment_method, promo_code, discount_amount)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """,
                    (
                        workspace_id,
                        plan_id,
                        merchant_order_id,
                        amount,
                        currency,
                        "pending",
                        "phonepe",
                        promo_code,
                        discount_amount,
                    ),
                )
                transaction_id = await cur.fetchone()

        # Initiate PhonePe payment
        redirect_url = return_url or f"{self.settings.FRONTEND_URL}/billing/success"
        redirect_url = _append_query_params(
            redirect_url, {"order_id": merchant_order_id}
        )
        response = self.gateway.pay(merchant_order_id, amount_paise, redirect_url)

        self.initiated_orders.add(merchant_order_id)

        logger.info(
            f"Created payment session {merchant_order_id} for workspace {workspace_id}"
        )

        return {
            "payment_url": response.get("redirectUrl"),
            "merchant_order_id": merchant_order_id,
            "transaction_id": str(transaction_id[0]) if transaction_id else None,
            "amount": amount,
            "currency": currency,
        }

    async def handle_payment_callback(
        self, authorization: str, response_body: str
    ) -> Dict[str, Any]:
        """Handle PhonePe callback and update subscription status."""
        self._ensure_phonepe_ready()
        self._ensure_webhook_credentials()

        try:
            callback = self.gateway.validate_callback(
                self.settings.PHONEPE_WEBHOOK_USERNAME,
                self.settings.PHONEPE_WEBHOOK_PASSWORD,
                authorization,
                response_body,
            )
        except RuntimeError as exc:
            raise PhonePeCallbackError(str(exc)) from exc

        payload = callback.get("payload") or {}
        merchant_order_id = payload.get("merchantOrderId")
        if not merchant_order_id:
            raise ValueError("Missing merchantOrderId in callback payload.")

        if merchant_order_id in self.processed_orders:
            return {"status": "already_processed"}

        order_status = self.gateway.get_order_status(merchant_order_id)
        result = await self._process_payment_for_order(
            merchant_order_id, order_status
        )

        self._record_order_state(merchant_order_id, result["payment_state"])

        return result

    async def confirm_payment_session(
        self, workspace_id: str, merchant_order_id: str
    ) -> Dict[str, Any]:
        """Confirm payment after redirect when webhook credentials are unavailable."""
        self._ensure_phonepe_ready()
        order_status = self.gateway.get_order_status(merchant_order_id)
        result = await self._process_payment_for_order(
            merchant_order_id, order_status, workspace_id=workspace_id
        )
        self._record_order_state(merchant_order_id, result["payment_state"])
        return result

    async def _process_payment_for_order(
        self,
        merchant_order_id: str,
        order_status: Dict[str, Any],
        workspace_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        payment_state = order_status.get("state")

        async with get_db_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    SELECT id, workspace_id, plan_id, amount, subscription_id, promo_code
                    FROM payment_transactions
                    WHERE merchant_order_id = %s
                """,
                    (merchant_order_id,),
                )
                transaction = await cur.fetchone()

                if not transaction:
                    raise ValueError(f"Transaction {merchant_order_id} not found")

                (
                    transaction_id,
                    tx_workspace_id,
                    plan_id,
                    amount,
                    subscription_id,
                    promo_code,
                ) = transaction

                if workspace_id and str(tx_workspace_id) != str(workspace_id):
                    raise ValueError("Workspace mismatch for payment confirmation.")

                new_status = (
                    "completed" if payment_state in FINAL_ORDER_STATES else "failed"
                )
                await cur.execute(
                    """
                    UPDATE payment_transactions
                    SET status = %s, gateway_response = %s, processed_at = NOW()
                    WHERE id = %s
                """,
                    (new_status, json.dumps(order_status), transaction_id),
                )

                if payment_state in FINAL_ORDER_STATES and not subscription_id:
                    await self._create_subscription(
                        conn, cur, tx_workspace_id, plan_id, merchant_order_id
                    )
                    if promo_code:
                        await self._redeem_promo_code(cur, promo_code)

                await self._send_payment_notification(
                    tx_workspace_id, new_status, amount
                )

        return {"status": "processed", "payment_state": payment_state}

    async def _create_subscription(
        self, conn, cur, workspace_id: str, plan_id: str, merchant_order_id: str
    ) -> str:
        """Create a new subscription for a workspace."""

        # Get plan details
        await cur.execute(
            """
            SELECT billing_interval, price
            FROM plans
            WHERE id = %s AND is_active = true
        """,
            (plan_id,),
        )
        plan = await cur.fetchone()

        if not plan:
            raise ValueError(f"Plan {plan_id} not found or inactive")

        billing_interval, price = plan

        # Calculate subscription period
        now = datetime.utcnow()
        if billing_interval == "monthly":
            period_end = now + timedelta(days=30)
        else:  # yearly
            period_end = now + timedelta(days=365)

        # Create subscription
        await cur.execute(
            """
            INSERT INTO subscriptions
            (workspace_id, plan_id, status, current_period_start, current_period_end,
             phonepe_merchant_order_id)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """,
            (workspace_id, plan_id, "active", now, period_end, merchant_order_id),
        )

        subscription = await cur.fetchone()
        subscription_id = subscription[0]

        # Update transaction with subscription ID
        await cur.execute(
            """
            UPDATE payment_transactions
            SET subscription_id = %s
            WHERE merchant_order_id = %s
        """,
            (subscription_id, merchant_order_id),
        )

        # Initialize usage tracking
        await self._initialize_usage_tracking(
            cur, workspace_id, subscription_id, plan_id
        )

        logger.info(
            f"Created subscription {subscription_id} for workspace {workspace_id}"
        )
        return subscription_id

    async def _initialize_usage_tracking(
        self, cur, workspace_id: str, subscription_id: str, plan_id: str
    ) -> None:
        """Initialize usage tracking for a new subscription."""

        # Get plan limits
        await cur.execute(
            """
            SELECT max_icp_profiles, max_campaigns, max_users, api_quota_daily, storage_quota_gb
            FROM plans
            WHERE id = %s
        """,
            (plan_id,),
        )
        plan_limits = await cur.fetchone()

        if not plan_limits:
            return

        max_icp, max_campaigns, max_users, api_quota, storage_gb = plan_limits

        # Insert usage tracking records
        usage_metrics = [
            ("icp_profiles", max_icp),
            ("campaigns", max_campaigns),
            ("users", max_users),
            ("api_calls_daily", api_quota),
            ("storage_gb", storage_gb),
        ]

        for metric_name, limit_value in usage_metrics:
            if limit_value and limit_value > 0:  # Only track if there's a limit
                await cur.execute(
                    """
                    INSERT INTO subscription_usage
                    (workspace_id, subscription_id, metric_name, limit_value, reset_date)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (workspace_id, subscription_id, metric_name)
                    DO UPDATE SET limit_value = EXCLUDED.limit_value
                """,
                    (
                        workspace_id,
                        subscription_id,
                        metric_name,
                        limit_value,
                        datetime.utcnow(),
                    ),
                )

    async def _send_payment_notification(
        self, workspace_id: str, status: str, amount: float
    ) -> None:
        """Send payment notification via notification system."""
        try:
            # Import here to avoid circular imports
            from services.notification_service import notification_service

            if status == "completed":
                title = "Payment Successful"
                message = (
                    f"Your payment of ₹{amount:.2f} has been processed successfully."
                )
                notification_type = "payment_success"
            else:
                title = "Payment Failed"
                message = f"Your payment of ₹{amount:.2f} could not be processed. Please try again."
                notification_type = "payment_failed"

            await notification_service.send_notification(
                workspace_id=workspace_id,
                title=title,
                message=message,
                type=notification_type,
                data={"amount": amount, "status": status},
            )

        except Exception as e:
            logger.error(f"Failed to send payment notification: {e}")

    async def _redeem_promo_code(self, cur, promo_code: str) -> None:
        """Increment promo code redemption count after successful payment."""
        await cur.execute(
            """
            UPDATE promo_codes
            SET redemption_count = redemption_count + 1,
                updated_at = NOW()
            WHERE LOWER(code) = LOWER(%s)
        """,
            (promo_code,),
        )

    async def get_subscription_details(self, workspace_id: str) -> Dict[str, Any]:
        """Get current subscription details and usage quotas for a workspace."""
        async with get_db_connection() as conn:
            async with conn.cursor() as cur:
                # Get subscription with plan details
                await cur.execute(
                    """
                    SELECT s.*, p.name as plan_name, p.description as plan_description,
                           p.features, p.max_icp_profiles, p.max_campaigns, p.max_users,
                           p.api_quota_daily, p.storage_quota_gb
                    FROM subscriptions s
                    JOIN plans p ON s.plan_id = p.id
                    WHERE s.workspace_id = %s
                    ORDER BY s.created_at DESC
                    LIMIT 1
                """,
                    (workspace_id,),
                )
                subscription = await cur.fetchone()

                if not subscription:
                    return {"subscription": None, "usage": {}}

                # Get current usage
                await cur.execute(
                    """
                    SELECT metric_name, current_usage, limit_value, reset_date
                    FROM subscription_usage
                    WHERE workspace_id = %s
                """,
                    (workspace_id,),
                )
                usage_records = await cur.fetchall()

                usage = {}
                for (
                    metric_name,
                    current_usage,
                    limit_value,
                    reset_date,
                ) in usage_records:
                    usage[metric_name] = {
                        "current": current_usage,
                        "limit": limit_value,
                        "reset_date": reset_date.isoformat() if reset_date else None,
                        "percentage": (
                            (current_usage / limit_value * 100)
                            if limit_value > 0
                            else 0
                        ),
                    }

                # Format subscription data
                subscription_data = {
                    "id": subscription[0],
                    "plan_id": subscription[2],
                    "status": subscription[3],
                    "current_period_start": subscription[4].isoformat(),
                    "current_period_end": subscription[5].isoformat(),
                    "plan_name": subscription[13],
                    "plan_description": subscription[14],
                    "features": subscription[15],
                    "limits": {
                        "icp_profiles": subscription[16],
                        "campaigns": subscription[17],
                        "users": subscription[18],
                        "api_calls_daily": subscription[19],
                        "storage_gb": subscription[20],
                    },
                }

                return {"subscription": subscription_data, "usage": usage}

    async def cancel_subscription(
        self, workspace_id: str, cancellation_reason: str = None
    ) -> Dict[str, Any]:
        """Cancel or downgrade subscription for a workspace."""
        async with get_db_connection() as conn:
            async with conn.cursor() as cur:
                # Get active subscription
                await cur.execute(
                    """
                    SELECT id, plan_id, status
                    FROM subscriptions
                    WHERE workspace_id = %s AND status = 'active'
                """,
                    (workspace_id,),
                )
                subscription = await cur.fetchone()

                if not subscription:
                    raise ValueError("No active subscription found")

                subscription_id, plan_id, status = subscription

                # Cancel subscription
                await cur.execute(
                    """
                    UPDATE subscriptions
                    SET status = 'cancelled',
                        cancelled_at = NOW(),
                        cancellation_reason = %s
                    WHERE id = %s
                """,
                    (cancellation_reason, subscription_id),
                )

                # Send notification
                await self._send_payment_notification(workspace_id, "cancelled", 0)

                logger.info(
                    f"Cancelled subscription {subscription_id} for workspace {workspace_id}"
                )

                return {"status": "cancelled", "subscription_id": subscription_id}


def _append_query_params(url: str, params: Dict[str, str]) -> str:
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    for key, value in params.items():
        query[key] = [value]
    new_query = urlencode(query, doseq=True)
    return urlunparse(parsed._replace(query=new_query))


payment_service = PaymentService()
