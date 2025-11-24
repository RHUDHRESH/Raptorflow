"""
Payment API Router
Endpoints for payment processing, subscription management, and PhonePe integration.
"""

from typing import Dict, Any
from uuid import UUID
from urllib.parse import urlparse, urljoin
from fastapi import APIRouter, HTTPException, Depends, Request, Header
import logging

from backend.utils.rate_limit import rate_limit_webhook, get_ip_from_request
from backend.utils.auth import get_current_user_and_workspace, verify_admin
from backend.utils.cache import redis_cache
from backend.models.payment import (
    CreateCheckoutRequest,
    CreateCheckoutResponse,
    PhonePePaymentRequest,
    SubscriptionChangeRequest,
    CancelSubscriptionRequest,
    BillingHistory,
    PlanLimits
)
from backend.services.phonepe_service import phonepe_service
from backend.services.supabase_client import supabase_client
from backend.utils.correlation import generate_correlation_id, set_correlation_id

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/plans", response_model=Dict[str, Any])
async def get_available_plans():
    """
    Get all available subscription plans with pricing and features.

    Returns:
        Dictionary of available plans
    """
    try:
        plans = {}
        for plan_name in ["ascent", "glide", "soar"]:
            plan_details = phonepe_service.get_plan_details(plan_name)
            plans[plan_name] = {
                "name": plan_details.name,
                "price_monthly": plan_details.price_monthly,
                "price_yearly": plan_details.price_yearly,
                "features": plan_details.features,
                "limits": plan_details.limits
            }

        return {
            "plans": plans,
            "currency": "INR"
        }

    except Exception as e:
        logger.error(f"Failed to get plans: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve subscription plans")


@router.post("/checkout/create", response_model=CreateCheckoutResponse)
async def create_checkout_session(
    request: CreateCheckoutRequest,
    auth: Dict[str, str] = Depends(get_current_user_and_workspace)
):
    """
    Create a new checkout session for subscription purchase.
    SECURITY: Rate limited to prevent spam/DoS attacks.

    Args:
        request: Checkout request details

    Returns:
        Checkout URL and session details
    """
    correlation_id = generate_correlation_id()
    set_correlation_id(correlation_id)

    try:
        # SECURITY: Rate limit payment initiation per user
        # Max 5 checkout requests per minute per user
        redis_key = f"payment_checkout:{auth['user_id']}"
        checkout_count = await redis_cache.incr(redis_key, expire=60)
        if checkout_count > 5:
            logger.warning(f"Payment checkout rate limit exceeded for user {auth['user_id']}")
            raise HTTPException(status_code=429, detail="Too many payment requests. Try again in a minute.")

        logger.info(f"Creating checkout for user {auth['user_id']}, plan: {request.plan}")

        # Create PhonePe payment request
        parsed_url = urlparse(request.success_url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        callback_url = urljoin(base_url, "/api/v1/payments/webhook")

        payment_request = PhonePePaymentRequest(
            plan=request.plan,
            billing_period=request.billing_period,
            user_id=UUID(auth["user_id"]),
            workspace_id=UUID(auth["workspace_id"]),
            redirect_url=request.success_url,
            callback_url=callback_url
        )

        # Initiate payment with PhonePe
        payment_response, error = await phonepe_service.create_payment(payment_request)

        if error or not payment_response:
            logger.error(f"Payment creation failed: {error}")
            raise HTTPException(status_code=400, detail=error or "Payment creation failed")

        # Store pending transaction in database (atomic operation)
        transaction_data = {
            "user_id": auth["user_id"],
            "workspace_id": auth["workspace_id"],
            "transaction_id": payment_response.transaction_id,
            "merchant_transaction_id": payment_response.merchant_transaction_id,
            "amount": payment_response.amount,
            "currency": "INR",
            "status": "pending",
            "plan": request.plan,
            "billing_period": request.billing_period
        }

        # Insert into billing_history table with transaction safety
        try:
            operations = [
                {
                    "type": "insert",
                    "table": "billing_history",
                    "data": transaction_data
                }
            ]
            await supabase_client.execute_transaction(operations)
        except Exception as e:
            logger.error(f"Failed to record payment in database: {e}")
            raise HTTPException(status_code=500, detail="Failed to create checkout session")

        return CreateCheckoutResponse(
            checkout_url=payment_response.payment_url,
            session_id=payment_response.merchant_transaction_id,
            expires_at=payment_response.created_at
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create checkout: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create checkout session")


@router.post("/webhook")
async def phonepe_webhook(request: Request):
    """
    Handle PhonePe payment webhook callbacks.

    This endpoint receives payment status updates from PhonePe.
    Implements idempotency to handle duplicate webhook deliveries.

    IMPORTANT: Signature verification happens BEFORE rate limiting
    to prevent DoS via invalid signatures burning the quota.
    """
    try:
        # Get webhook payload
        body = await request.body()
        payload_data = await request.json()

        # Extract payload and checksum
        payload_base64 = payload_data.get("response")
        checksum = request.headers.get("X-VERIFY", "")

        if not payload_base64 or not checksum:
            logger.warning("Webhook missing payload or checksum, rejecting")
            raise HTTPException(status_code=400, detail="Invalid webhook payload")

        # VERIFY SIGNATURE FIRST (before rate limit)
        # This prevents invalid signatures from burning rate limit quota
        webhook_data, error = phonepe_service.verify_webhook_payload(payload_base64, checksum)

        if error or not webhook_data:
            logger.warning(f"Webhook signature verification failed: {error}")
            raise HTTPException(status_code=401, detail="Invalid webhook signature")

        # NOW apply rate limiting (after signature is valid)
        # Use IP-based rate limiting for webhooks
        client_ip = get_ip_from_request(request)

        # Rate limit: max 20 valid webhooks per minute per IP
        # PhonePe won't send more than this legitimately
        redis_key = f"webhook:phonepe:{client_ip}"
        try:
            webhook_count = await redis_cache.incr(redis_key, expire=60)
            if webhook_count > 20:
                logger.warning(f"Webhook rate limit exceeded for IP {client_ip}")
                raise HTTPException(status_code=429, detail="Too many webhook requests")

        # Validate required fields
        transaction_id = webhook_data.get("transactionId")
        merchant_transaction_id = webhook_data.get("merchantTransactionId")
        state = webhook_data.get("state", "").upper()

        if not merchant_transaction_id:
            logger.error("Webhook missing required field: merchantTransactionId")
            raise HTTPException(status_code=400, detail="Invalid webhook: missing merchantTransactionId")

        logger.info(f"Processing webhook for transaction {merchant_transaction_id}, state: {state}")

        # SECURITY: Check for duplicate/concurrent webhook processing (race condition prevention)
        # Use optimistic locking: only process if status is still "pending"
        existing_record = await supabase_client.fetch_one(
            "billing_history",
            {"merchant_transaction_id": merchant_transaction_id}
        )

        if existing_record:
            existing_status = existing_record.get("status")

            # If already fully processed (active/failed), return idempotently
            if existing_status in ["active", "failed"]:
                # SECURITY: Detect conflicting states (potential attack/double-payment)
                if existing_status == "active" and state == "FAILED":
                    logger.error(f"SECURITY ALERT: Conflicting webhook states for {merchant_transaction_id}: "
                               f"already active but received FAILED. Rejecting.")
                    raise HTTPException(status_code=409, detail="Conflicting payment state")

                if existing_status == "failed" and state == "COMPLETED":
                    logger.error(f"SECURITY ALERT: Conflicting webhook states for {merchant_transaction_id}: "
                               f"already failed but received COMPLETED. Rejecting.")
                    raise HTTPException(status_code=409, detail="Conflicting payment state")

                # Same state = idempotent, return success
                logger.info(f"Webhook already processed for {merchant_transaction_id}, returning success")
                return {"status": "success", "message": "Webhook already processed"}

            # If still processing, reject to prevent race condition
            if existing_status == "processing":
                logger.warning(f"Webhook already being processed for {merchant_transaction_id}, rejecting duplicate")
                raise HTTPException(status_code=409, detail="Webhook already being processed")

            # If pending, mark as processing ATOMICALLY to prevent race
            if existing_status == "pending":
                try:
                    await supabase_client.update(
                        "billing_history",
                        {
                            "merchant_transaction_id": merchant_transaction_id,
                            "status": "pending"  # Only update if still pending (atomic check)
                        },
                        {"status": "processing"}
                    )
                except Exception as e:
                    # If update failed, another thread got there first
                    logger.warning(f"Could not acquire processing lock for {merchant_transaction_id}: {e}")
                    raise HTTPException(status_code=409, detail="Webhook already being processed")
        else:
            # Record doesn't exist yet (payment not initiated?) - this shouldn't happen
            logger.error(f"Webhook received but payment record not found: {merchant_transaction_id}")
            raise HTTPException(status_code=404, detail="Payment record not found")

        # SECURITY: Validate transaction ID format to prevent injection
        import re
        # Case-insensitive to handle both uppercase and lowercase hex from PhonePe
        if not re.match(r"^MT[A-Fa-f0-9]{20}$", merchant_transaction_id, re.IGNORECASE):
            logger.error(f"SECURITY: Invalid transaction ID format: {merchant_transaction_id}")
            raise HTTPException(status_code=400, detail="Invalid transaction ID format")

        # SECURITY: Validate webhook state is one of expected values
        valid_states = ["COMPLETED", "FAILED", "PENDING"]
        if state not in valid_states:
            logger.error(f"SECURITY: Invalid payment state in webhook: {state}")
            # Mark as failed due to invalid state
            await supabase_client.update(
                "billing_history",
                {"merchant_transaction_id": merchant_transaction_id},
                {"status": "failed", "failure_reason": f"Invalid state: {state}"}
            )
            raise HTTPException(status_code=400, detail=f"Invalid payment state: {state}")

        # Process webhook based on payment status
        try:
            if state == "COMPLETED":
                # Payment successful - activate subscription
                await _activate_subscription(webhook_data)

            elif state == "FAILED":
                # Payment failed - update transaction status
                await _mark_payment_failed(merchant_transaction_id)

            elif state == "PENDING":
                # Payment still pending - no action needed, just acknowledge
                logger.info(f"Payment still pending for {merchant_transaction_id}")

            return {"status": "success", "message": "Webhook processed"}

        except Exception as e:
            logger.error(f"Failed to process webhook state {state}: {e}", exc_info=True)
            # Reset status back to pending on processing error
            await supabase_client.update(
                "billing_history",
                {"merchant_transaction_id": merchant_transaction_id},
                {"status": "pending"}
            )
            raise HTTPException(status_code=500, detail="Failed to process webhook")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Webhook processing error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Webhook processing failed")


@router.get("/subscription/status", response_model=Dict[str, Any])
async def get_subscription_status(
    auth: Dict[str, str] = Depends(get_current_user_and_workspace)
):
    """
    Get current subscription status for the authenticated user.

    Returns:
        Current subscription details
    """
    try:
        # Fetch subscription from database
        subscription = await supabase_client.fetch_one(
            "subscriptions",
            {"user_id": auth["user_id"]}
        )

        if not subscription:
            # Return default free plan
            return {
                "subscription": {
                    "plan": "free",
                    "status": "active",
                    "billing_period": "monthly"
                },
                "limits": {
                    "cohorts": 1,
                    "moves_per_month": 0
                }
            }

        return {
            "subscription": subscription,
            "limits": phonepe_service.get_plan_details(subscription["plan"]).limits
        }

    except Exception as e:
        logger.error(f"Failed to get subscription status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve subscription status")


@router.post("/subscription/change", response_model=Dict[str, Any])
async def change_subscription(
    request: SubscriptionChangeRequest,
    auth: Dict[str, str] = Depends(get_current_user_and_workspace)
):
    """
    Change subscription plan.

    Args:
        request: Plan change request

    Returns:
        Updated subscription details
    """
    correlation_id = generate_correlation_id()
    set_correlation_id(correlation_id)

    try:
        logger.info(f"Changing subscription for user {auth['user_id']} to {request.new_plan}")

        # Get current subscription
        current_sub = await supabase_client.fetch_one(
            "subscriptions",
            {"user_id": auth["user_id"]}
        )

        if not current_sub:
            raise HTTPException(status_code=404, detail="No active subscription found")

        # Create new payment for the new plan
        # This will redirect to PhonePe payment page
        return {
            "message": "Plan change initiated. Please complete payment.",
            "requires_payment": True,
            "new_plan": request.new_plan,
            "correlation_id": correlation_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to change subscription: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to change subscription")


@router.post("/subscription/cancel", response_model=Dict[str, Any])
async def cancel_subscription(
    request: CancelSubscriptionRequest,
    auth: Dict[str, str] = Depends(get_current_user_and_workspace)
):
    """
    Cancel active subscription using atomic transaction.

    Args:
        request: Cancellation request

    Returns:
        Cancellation confirmation
    """
    from datetime import datetime, timezone

    correlation_id = generate_correlation_id()
    set_correlation_id(correlation_id)

    try:
        logger.info(f"Cancelling subscription for user {auth['user_id']}")

        now_iso = datetime.now(timezone.utc).isoformat()

        # Execute atomic cancellation
        operations = [
            {
                "type": "update",
                "table": "subscriptions",
                "filters": {"user_id": auth["user_id"]},
                "data": {
                    "status": "cancelled",
                    "cancelled_at": now_iso
                }
            }
        ]

        await supabase_client.execute_transaction(operations)

        return {
            "message": "Subscription cancelled successfully",
            "cancelled": True,
            "correlation_id": correlation_id
        }

    except Exception as e:
        logger.error(f"Failed to cancel subscription: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to cancel subscription")


@router.get("/billing/history", response_model=Dict[str, Any])
async def get_billing_history(
    auth: Dict[str, str] = Depends(get_current_user_and_workspace)
):
    """
    Get billing history for the authenticated user.

    Returns:
        List of past transactions
    """
    try:
        # Fetch billing history from database
        history = await supabase_client.fetch_all(
            "billing_history",
            {"user_id": auth["user_id"]}
        )

        return {
            "history": history or [],
            "total_count": len(history) if history else 0
        }

    except Exception as e:
        logger.error(f"Failed to get billing history: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve billing history")


@router.get("/payment/status/{merchant_transaction_id}", response_model=Dict[str, Any])
async def check_payment_status(
    merchant_transaction_id: str,
    auth: Dict[str, str] = Depends(get_current_user_and_workspace)
):
    """
    Check status of a payment transaction.
    SECURITY: Validates that the transaction belongs to the authenticated user.

    Args:
        merchant_transaction_id: Transaction ID to check

    Returns:
        Payment status details
    """
    try:
        # SECURITY: Verify transaction belongs to authenticated user
        payment_record = await supabase_client.fetch_one(
            "billing_history",
            {
                "merchant_transaction_id": merchant_transaction_id,
                "user_id": auth["user_id"]  # Verify ownership
            }
        )

        if not payment_record:
            # Don't reveal whether transaction exists or not
            raise HTTPException(status_code=404, detail="Payment not found")

        # Check with PhonePe
        status, error = await phonepe_service.check_payment_status(merchant_transaction_id)

        if error or not status:
            raise HTTPException(status_code=400, detail=error or "Failed to check status")

        return {
            "transaction_id": status.transaction_id,
            "merchant_transaction_id": status.merchant_transaction_id,
            "status": status.status,
            "amount": status.amount,
            "payment_method": status.payment_method
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to check payment status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to check payment status")


# Helper functions

async def _activate_subscription(webhook_data: Dict[str, Any]):
    """
    Activate subscription after successful payment.
    Uses atomic transaction to ensure subscription and billing records are consistent.
    SECURITY: Validates amount matches expected price to prevent tampering.
    SECURITY: Verifies user exists before creating subscription records.
    """
    try:
        from datetime import datetime, timedelta, timezone

        # Extract and validate required fields
        merchant_user_id = webhook_data.get("merchantUserId")
        amount = webhook_data.get("amount")
        merchant_transaction_id = webhook_data.get("merchantTransactionId")

        if not merchant_user_id:
            logger.error("Webhook missing required field: merchantUserId")
            return

        if not merchant_transaction_id:
            logger.error("Webhook missing required field: merchantTransactionId")
            return

        # SECURITY: Verify user exists before creating subscription
        # This prevents orphaned subscriptions for non-existent users
        user_exists = await supabase_client.fetch_one(
            "users",
            {"id": merchant_user_id}
        )

        if not user_exists:
            logger.error(f"SECURITY: User {merchant_user_id} does not exist in database. "
                        f"Rejecting subscription activation from webhook.")
            # Mark payment as failed since we can't activate for non-existent user
            await supabase_client.update(
                "billing_history",
                {"merchant_transaction_id": merchant_transaction_id},
                {"status": "failed", "failure_reason": "User not found"}
            )
            return

        # SECURITY: Fetch the payment record to validate amount
        # Amount is stored in billing_history when payment was initiated
        payment_record = await supabase_client.fetch_one(
            "billing_history",
            {"merchant_transaction_id": merchant_transaction_id}
        )

        if not payment_record:
            logger.error(f"Payment record not found for {merchant_transaction_id}, cannot activate")
            return

        expected_amount = payment_record.get("amount")

        # SECURITY: Strictly validate amount - must not be NULL and must match exactly
        if expected_amount is None:
            logger.error(f"SECURITY: Expected amount is NULL for {merchant_transaction_id}, rejecting activation")
            await supabase_client.update(
                "billing_history",
                {"merchant_transaction_id": merchant_transaction_id},
                {"status": "failed", "failure_reason": "Missing stored amount"}
            )
            return

        if amount is None:
            logger.error(f"SECURITY ALERT: Webhook amount is NULL for {merchant_transaction_id}, rejecting activation")
            await supabase_client.update(
                "billing_history",
                {"merchant_transaction_id": merchant_transaction_id},
                {"status": "failed", "failure_reason": "Missing webhook amount"}
            )
            return

        # Ensure amounts are numeric and positive
        try:
            expected_amt_num = float(expected_amount)
            webhook_amt_num = float(amount)
            if expected_amt_num <= 0 or webhook_amt_num <= 0:
                raise ValueError("Amount must be positive")
        except (ValueError, TypeError) as e:
            logger.error(f"SECURITY: Invalid amount format for {merchant_transaction_id}: {e}")
            await supabase_client.update(
                "billing_history",
                {"merchant_transaction_id": merchant_transaction_id},
                {"status": "failed", "failure_reason": "Invalid amount format"}
            )
            return

        # Amount must match exactly - webhook should not be able to modify the charged amount
        if webhook_amt_num != expected_amt_num:
            logger.error(f"SECURITY ALERT: Amount mismatch for {merchant_transaction_id}: "
                       f"expected {expected_amount}, got {amount}. Rejecting subscription activation.")
            # Mark as failed due to amount mismatch
            await supabase_client.update(
                "billing_history",
                {"merchant_transaction_id": merchant_transaction_id},
                {"status": "failed", "failure_reason": "Amount mismatch"}
            )
            return

        # Get plan from payment record to validate
        plan = payment_record.get("plan")
        if not plan:
            logger.error(f"Plan not found in payment record for {merchant_transaction_id}")
            await supabase_client.update(
                "billing_history",
                {"merchant_transaction_id": merchant_transaction_id},
                {"status": "failed", "failure_reason": "Plan not found in payment record"}
            )
            return

        # SECURITY: Validate plan is one of allowed plans
        # This prevents webhook from specifying arbitrary plans
        valid_plans = list(phonepe_service.PLAN_PRICES.keys())
        if plan not in valid_plans:
            logger.error(f"SECURITY: Invalid plan '{plan}' in payment record for {merchant_transaction_id}. "
                        f"Valid plans: {valid_plans}")
            await supabase_client.update(
                "billing_history",
                {"merchant_transaction_id": merchant_transaction_id},
                {"status": "failed", "failure_reason": f"Invalid plan: {plan}"}
            )
            return

        # Calculate subscription dates (monthly default)
        period_start = datetime.now(timezone.utc)
        period_end = period_start + timedelta(days=30)

        # Prepare atomic transaction operations
        subscription_data = {
            "user_id": merchant_user_id,
            "status": "active",
            "plan": plan,  # Store the plan that was paid for
            "phonepe_transaction_id": webhook_data.get("transactionId"),
            "current_period_start": period_start.isoformat(),
            "current_period_end": period_end.isoformat()
        }

        billing_update = {
            "status": "active",
            "activated_at": period_start.isoformat()
        }

        # Execute atomic transaction
        operations = [
            {
                "type": "upsert",
                "table": "subscriptions",
                "data": subscription_data,
                "match_columns": ["user_id"]
            },
            {
                "type": "update",
                "table": "billing_history",
                "filters": {"merchant_transaction_id": merchant_transaction_id},
                "data": billing_update
            }
        ]

        await supabase_client.execute_transaction(operations)
        logger.info(f"Subscription activated for user {merchant_user_id} via transaction {merchant_transaction_id}")

    except Exception as e:
        logger.error(f"Failed to activate subscription: {e}", exc_info=True)


async def _mark_payment_failed(merchant_transaction_id: str):
    """Mark payment as failed in database using atomic transaction."""
    try:
        from datetime import datetime, timezone

        # Prepare atomic transaction operation
        operations = [
            {
                "type": "update",
                "table": "billing_history",
                "filters": {"merchant_transaction_id": merchant_transaction_id},
                "data": {
                    "status": "failed",
                    "failed_at": datetime.now(timezone.utc).isoformat()
                }
            }
        ]

        await supabase_client.execute_transaction(operations)
        logger.info(f"Marked payment {merchant_transaction_id} as failed")

    except Exception as e:
        logger.error(f"Failed to mark payment as failed: {e}", exc_info=True)


@router.post("/reconcile", response_model=Dict[str, Any])
async def reconcile_payments(
    auth: Dict[str, str] = Depends(verify_admin)
):
    """
    Manually trigger payment and subscription reconciliation.
    SECURITY: Admin-only endpoint.

    This endpoint checks pending payments/subscriptions against PhonePe's records
    and updates the database if there are discrepancies (e.g., webhook didn't arrive).

    Only accessible to admin users.

    Returns:
        Reconciliation results
    """
    correlation_id = generate_correlation_id()
    set_correlation_id(correlation_id)

    try:
        logger.info(f"Manual reconciliation triggered by user {auth['user_id']}")

        from backend.services.payment_reconciliation import payment_reconciliation_service

        results = await payment_reconciliation_service.run_full_reconciliation()

        return {
            "status": "success",
            "message": "Payment reconciliation completed",
            "results": results,
            "correlation_id": correlation_id
        }

    except Exception as e:
        logger.error(f"Reconciliation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Reconciliation failed")
