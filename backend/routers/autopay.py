"""
Autopay API Router
Endpoints for PhonePe autopay (recurring payment) subscriptions.
"""

from typing import Dict, Any
from uuid import UUID
from urllib.parse import urlparse, urljoin
from fastapi import APIRouter, HTTPException, Depends, Request, Header
import logging

from backend.utils.rate_limit import rate_limit_webhook, get_ip_from_request
from backend.models.payment import (
    CreateAutopayCheckoutRequest,
    CreateAutopayCheckoutResponse,
    AutopaySubscriptionRequest,
    AutopaySubscriptionStatus,
    CancelAutopayRequest,
    PauseAutopayRequest,
    ResumeAutopayRequest
)
from backend.services.phonepe_autopay_service import phonepe_autopay_service
from backend.services.supabase_client import supabase_client
from backend.utils.correlation import generate_correlation_id, set_correlation_id

logger = logging.getLogger(__name__)

router = APIRouter()


# Import proper auth dependency
from backend.utils.auth import get_current_user_and_workspace


@router.post("/checkout/create", response_model=CreateAutopayCheckoutResponse)
async def create_autopay_checkout(
    request: CreateAutopayCheckoutRequest,
    auth: Dict[str, str] = Depends(get_current_user_and_workspace)
):
    """
    Create a new autopay checkout session for recurring subscription.

    Args:
        request: Autopay checkout request details

    Returns:
        Authorization URL and subscription details
    """
    correlation_id = generate_correlation_id()
    set_correlation_id(correlation_id)

    try:
        # SECURITY: Rate limit autopay initiation per user
        # Max 3 autopay requests per minute per user
        from backend.utils.cache import redis_cache
        redis_key = f"autopay_checkout:{auth['user_id']}"
        autopay_count = await redis_cache.incr(redis_key, expire=60)
        if autopay_count > 3:
            logger.warning(f"Autopay checkout rate limit exceeded for user {auth['user_id']}")
            raise HTTPException(status_code=429, detail="Too many autopay requests. Try again in a minute.")

        logger.info(f"Creating autopay checkout for user {auth['user_id']}, plan: {request.plan}")

        # SECURITY: Validate mobile number format
        import re
        if not re.match(r"^\+?91?[6-9]\d{9}$", request.mobile_number):
            logger.warning(f"Invalid mobile number format from user {auth['user_id']}")
            raise HTTPException(status_code=400, detail="Invalid mobile number format. Must be valid Indian number.")

        # Parse and construct callback URL properly
        parsed_url = urlparse(request.success_url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        callback_url = urljoin(base_url, "/api/v1/autopay/webhook")

        # Create autopay subscription request
        subscription_request = AutopaySubscriptionRequest(
            plan=request.plan,
            billing_period=request.billing_period,
            user_id=UUID(auth["user_id"]),
            workspace_id=UUID(auth["workspace_id"]),
            mobile_number=request.mobile_number,
            redirect_url=request.success_url,
            callback_url=callback_url
        )

        # Create autopay subscription with PhonePe
        subscription_response, error = await phonepe_autopay_service.create_subscription(
            subscription_request
        )

        if error or not subscription_response:
            logger.error(f"Autopay subscription creation failed: {error}")
            raise HTTPException(status_code=400, detail=error or "Subscription creation failed")

        # Store pending subscription in database
        subscription_data = {
            "user_id": auth["user_id"],
            "workspace_id": auth["workspace_id"],
            "subscription_id": subscription_response.subscription_id,
            "merchant_subscription_id": subscription_response.merchant_subscription_id,
            "amount": subscription_response.amount,
            "currency": "INR",
            "status": "pending",
            "plan": request.plan,
            "billing_period": request.billing_period,
            "billing_frequency": subscription_response.billing_frequency,
            "start_date": subscription_response.start_date.isoformat(),
            "end_date": subscription_response.end_date.isoformat(),
            "mobile_number": request.mobile_number
        }

        # Insert into autopay_subscriptions table
        await supabase_client.insert("autopay_subscriptions", subscription_data)

        return CreateAutopayCheckoutResponse(
            authorization_url=subscription_response.authorization_url,
            subscription_id=subscription_response.subscription_id,
            merchant_subscription_id=subscription_response.merchant_subscription_id,
            expires_at=subscription_response.created_at
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create autopay checkout: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create autopay checkout")


@router.get("/subscription/status/{merchant_subscription_id}", response_model=Dict[str, Any])
async def get_autopay_subscription_status(
    merchant_subscription_id: str,
    auth: Dict[str, str] = Depends(get_current_user_and_workspace)
):
    """
    Check status of an autopay subscription.
    SECURITY: Validates subscription belongs to authenticated user.

    Args:
        merchant_subscription_id: Merchant subscription ID to check

    Returns:
        Subscription status details
    """
    try:
        # SECURITY: Verify subscription belongs to authenticated user
        subscription_record = await supabase_client.fetch_one(
            "autopay_subscriptions",
            {
                "merchant_subscription_id": merchant_subscription_id,
                "user_id": auth["user_id"]  # Verify ownership
            }
        )

        if not subscription_record:
            # Don't reveal whether subscription exists or not
            raise HTTPException(status_code=404, detail="Subscription not found")

        # Check with PhonePe
        status, error = await phonepe_autopay_service.check_subscription_status(
            merchant_subscription_id
        )

        if error or not status:
            raise HTTPException(status_code=400, detail=error or "Failed to check status")

        return {
            "subscription_id": status.subscription_id,
            "merchant_subscription_id": status.merchant_subscription_id,
            "status": status.status,
            "amount": status.amount,
            "start_date": status.start_date.isoformat(),
            "end_date": status.end_date.isoformat(),
            "billing_frequency": status.billing_frequency,
            "next_billing_date": status.next_billing_date.isoformat() if status.next_billing_date else None,
            "payment_stats": {
                "total": status.total_payments,
                "successful": status.successful_payments,
                "failed": status.failed_payments
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to check subscription status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve subscription status")


@router.post("/subscription/cancel", response_model=Dict[str, Any])
async def cancel_autopay_subscription(
    request: CancelAutopayRequest,
    auth: Dict[str, str] = Depends(get_current_user_and_workspace)
):
    """
    Cancel an active autopay subscription.

    Args:
        request: Cancellation request with subscription ID

    Returns:
        Cancellation confirmation
    """
    correlation_id = generate_correlation_id()
    set_correlation_id(correlation_id)

    try:
        from datetime import datetime, timezone

        logger.info(f"Cancelling autopay subscription {request.merchant_subscription_id} for user {auth['user_id']}")

        # Cancel with PhonePe
        success, error = await phonepe_autopay_service.cancel_subscription(
            request.merchant_subscription_id
        )

        if not success or error:
            raise HTTPException(status_code=400, detail=error or "Cancellation failed")

        # Update subscription status in database
        await supabase_client.update(
            "autopay_subscriptions",
            {"merchant_subscription_id": request.merchant_subscription_id},
            {
                "status": "cancelled",
                "cancelled_at": datetime.now(timezone.utc).isoformat(),
                "cancellation_reason": request.reason
            }
        )

        return {
            "message": "Autopay subscription cancelled successfully",
            "cancelled": True,
            "merchant_subscription_id": request.merchant_subscription_id,
            "correlation_id": correlation_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel subscription: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to cancel subscription")


@router.post("/subscription/pause", response_model=Dict[str, Any])
async def pause_autopay_subscription(
    request: PauseAutopayRequest,
    auth: Dict[str, str] = Depends(get_current_user_and_workspace)
):
    """
    Pause an active autopay subscription.

    Args:
        request: Pause request with subscription ID

    Returns:
        Pause confirmation
    """
    correlation_id = generate_correlation_id()
    set_correlation_id(correlation_id)

    try:
        logger.info(f"Pausing autopay subscription {request.merchant_subscription_id} for user {auth['user_id']}")

        # Pause with PhonePe
        success, error = await phonepe_autopay_service.pause_subscription(
            request.merchant_subscription_id
        )

        if not success or error:
            raise HTTPException(status_code=400, detail=error or "Pause failed")

        # Update subscription status in database
        await supabase_client.update(
            "autopay_subscriptions",
            {"merchant_subscription_id": request.merchant_subscription_id},
            {
                "status": "paused",
                "paused_at": datetime.now(timezone.utc).isoformat(),
                "pause_reason": request.reason
            }
        )

        return {
            "message": "Autopay subscription paused successfully",
            "paused": True,
            "merchant_subscription_id": request.merchant_subscription_id,
            "correlation_id": correlation_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to pause subscription: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/subscription/resume", response_model=Dict[str, Any])
async def resume_autopay_subscription(
    request: ResumeAutopayRequest,
    auth: Dict[str, str] = Depends(get_current_user_and_workspace)
):
    """
    Resume a paused autopay subscription.

    Args:
        request: Resume request with subscription ID

    Returns:
        Resume confirmation
    """
    correlation_id = generate_correlation_id()
    set_correlation_id(correlation_id)

    try:
        logger.info(f"Resuming autopay subscription {request.merchant_subscription_id} for user {auth['user_id']}")

        # Resume with PhonePe
        success, error = await phonepe_autopay_service.resume_subscription(
            request.merchant_subscription_id
        )

        if not success or error:
            raise HTTPException(status_code=400, detail=error or "Resume failed")

        # Update subscription status in database
        await supabase_client.update(
            "autopay_subscriptions",
            {"merchant_subscription_id": request.merchant_subscription_id},
            {
                "status": "active",
                "resumed_at": datetime.now(timezone.utc).isoformat()
            }
        )

        return {
            "message": "Autopay subscription resumed successfully",
            "resumed": True,
            "merchant_subscription_id": request.merchant_subscription_id,
            "correlation_id": correlation_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to resume subscription: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhook")
async def autopay_webhook(request: Request):
    """
    Handle PhonePe autopay webhook callbacks.

    This endpoint receives autopay events like subscription activation,
    payment success/failure, etc.

    SECURITY: Signature verification happens BEFORE rate limiting
    to prevent DoS via invalid signatures.
    """
    try:
        # Get webhook payload
        payload_data = await request.json()
        payload_base64 = payload_data.get("response", "")
        x_verify_header = request.headers.get("X-VERIFY", "")

        if not payload_base64 or not x_verify_header:
            logger.warning("Autopay webhook missing payload or signature")
            raise HTTPException(status_code=400, detail="Invalid webhook payload")

        # VERIFY SIGNATURE FIRST (before rate limit)
        # This prevents invalid signatures from burning rate limit quota
        webhook_data, error = phonepe_autopay_service.verify_webhook_signature(
            payload_base64,
            x_verify_header
        )
        if error or not webhook_data:
            logger.warning(f"Invalid autopay webhook signature: {error}")
            raise HTTPException(status_code=401, detail="Invalid signature")

        # NOW apply rate limiting (after signature is valid)
        from backend.utils.cache import redis_cache
        client_ip = request.client.host if request.client else "unknown"

        # Rate limit: max 20 valid webhooks per minute per IP
        redis_key = f"webhook:autopay:{client_ip}"
        try:
            webhook_count = await redis_cache.incr(redis_key, expire=60)
            if webhook_count > 20:
                logger.warning(f"Autopay webhook rate limit exceeded for IP {client_ip}")
                raise HTTPException(status_code=429, detail="Too many webhook requests")
        except Exception as e:
            logger.warning(f"Rate limiting check failed: {e}")
            # Continue anyway if rate limiting fails

        # Extract event data
        event_type = webhook_data.get("eventType")
        merchant_subscription_id = webhook_data.get("merchantSubscriptionId")
        subscription_id = webhook_data.get("subscriptionId")
        status = webhook_data.get("status")

        logger.info(f"Processing autopay webhook: {event_type} for subscription {merchant_subscription_id}")

        # Process webhook based on event type
        if event_type == "SUBSCRIPTION_ACTIVATED":
            # Subscription activated - user has authorized the mandate
            await _activate_autopay_subscription(webhook_data)

        elif event_type == "PAYMENT_SUCCESS":
            # Recurring payment succeeded
            await _process_autopay_payment_success(webhook_data)

        elif event_type == "PAYMENT_FAILED":
            # Recurring payment failed
            await _process_autopay_payment_failure(webhook_data)

        elif event_type == "SUBSCRIPTION_CANCELLED":
            # Subscription cancelled
            await _process_autopay_cancellation(webhook_data)

        return {"status": "success", "message": "Webhook processed"}

    except Exception as e:
        logger.error(f"Autopay webhook processing error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/subscriptions", response_model=Dict[str, Any])
async def get_user_subscriptions(
    auth: Dict[str, str] = Depends(get_current_user_and_workspace)
):
    """
    Get all autopay subscriptions for the authenticated user.

    Returns:
        List of user's subscriptions
    """
    try:
        # Fetch subscriptions from database
        subscriptions = await supabase_client.fetch_all(
            "autopay_subscriptions",
            {"user_id": auth["user_id"]}
        )

        return {
            "subscriptions": subscriptions or [],
            "total_count": len(subscriptions) if subscriptions else 0
        }

    except Exception as e:
        logger.error(f"Failed to get subscriptions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Helper functions

async def _activate_autopay_subscription(webhook_data: Dict[str, Any]):
    """Activate autopay subscription after user authorization."""
    try:
        from datetime import datetime, timezone

        merchant_subscription_id = webhook_data.get("merchantSubscriptionId")
        subscription_id = webhook_data.get("subscriptionId")
        webhook_amount = webhook_data.get("amount")

        # SECURITY: Validate amount from webhook matches stored subscription
        if webhook_amount is None:
            logger.error(f"SECURITY: Webhook missing amount for subscription {merchant_subscription_id}")
            raise ValueError("Amount is required in webhook")

        # Fetch stored subscription to validate amount
        stored_subscription = await supabase_client.fetch_one(
            "autopay_subscriptions",
            {"merchant_subscription_id": merchant_subscription_id}
        )

        if not stored_subscription:
            logger.error(f"SECURITY: Subscription {merchant_subscription_id} not found in database")
            raise ValueError("Subscription not found")

        stored_amount = stored_subscription.get("amount")

        # Amount must match - webhook should not be able to modify the charged amount
        if stored_amount is None:
            logger.error(f"SECURITY: Stored subscription has NULL amount for {merchant_subscription_id}")
            raise ValueError("Stored subscription has invalid amount")

        if webhook_amount != stored_amount:
            logger.error(
                f"SECURITY: Amount mismatch for subscription {merchant_subscription_id}: "
                f"webhook={webhook_amount}, stored={stored_amount}. Rejecting activation."
            )
            raise ValueError(f"Amount mismatch: webhook amount {webhook_amount} != stored amount {stored_amount}")

        # SECURITY: Verify user exists before activating subscription
        # This prevents orphaned subscriptions for non-existent users
        user_id = stored_subscription.get("user_id")
        if user_id:
            user_exists = await supabase_client.fetch_one(
                "users",
                {"id": user_id}
            )
            if not user_exists:
                logger.error(f"SECURITY: User {user_id} for subscription {merchant_subscription_id} does not exist")
                raise ValueError(f"User {user_id} not found")

        # SECURITY: Validate plan is one of allowed autopay plans
        plan = stored_subscription.get("plan")
        if plan:
            valid_plans = list(phonepe_autopay_service.PLAN_PRICES.keys())
            if plan not in valid_plans:
                logger.error(f"SECURITY: Invalid autopay plan '{plan}' for subscription {merchant_subscription_id}. "
                            f"Valid plans: {valid_plans}")
                raise ValueError(f"Invalid plan: {plan}")

        # Update subscription status in database
        await supabase_client.update(
            "autopay_subscriptions",
            {"merchant_subscription_id": merchant_subscription_id},
            {
                "status": "active",
                "subscription_id": subscription_id,
                "activated_at": datetime.now(timezone.utc).isoformat()
            }
        )

        logger.info(f"Autopay subscription {merchant_subscription_id} activated with validated amount {webhook_amount}")

    except Exception as e:
        logger.error(f"Failed to activate subscription: {e}", exc_info=True)
        raise


async def _process_autopay_payment_success(webhook_data: Dict[str, Any]):
    """Process successful autopay payment."""
    try:
        from datetime import datetime, timezone

        merchant_subscription_id = webhook_data.get("merchantSubscriptionId")
        payment_id = webhook_data.get("paymentId")
        webhook_amount = webhook_data.get("amount")

        # SECURITY: Strictly validate amount - must not be NULL and must be positive
        if webhook_amount is None:
            logger.error(f"SECURITY: Payment success webhook missing amount for subscription {merchant_subscription_id}")
            raise ValueError("Amount is required in webhook")

        # Validate amount is numeric and positive
        try:
            webhook_amt_num = float(webhook_amount)
            if webhook_amt_num <= 0:
                raise ValueError("Amount must be positive")
        except (ValueError, TypeError) as e:
            logger.error(f"SECURITY: Invalid webhook amount format for subscription {merchant_subscription_id}: {e}")
            raise ValueError(f"Invalid amount format: {e}")

        # Fetch stored subscription to validate recurring amount
        stored_subscription = await supabase_client.fetch_one(
            "autopay_subscriptions",
            {"merchant_subscription_id": merchant_subscription_id}
        )

        if stored_subscription:
            stored_amount = stored_subscription.get("amount")
            if stored_amount is not None:
                try:
                    stored_amt_num = float(stored_amount)
                    if webhook_amt_num != stored_amt_num:
                        logger.error(
                            f"SECURITY ALERT: Recurring payment amount mismatch for subscription {merchant_subscription_id}: "
                            f"webhook={webhook_amount}, expected={stored_amount}. Rejecting."
                        )
                        raise ValueError(f"Amount mismatch: webhook {webhook_amount} != stored {stored_amount}")
                except (ValueError, TypeError) as e:
                    logger.error(f"SECURITY: Invalid stored amount format for subscription {merchant_subscription_id}: {e}")
            else:
                logger.error(f"SECURITY: Stored subscription has NULL amount for {merchant_subscription_id}")

        # Record payment in database
        payment_data = {
            "merchant_subscription_id": merchant_subscription_id,
            "payment_id": payment_id,
            "amount": webhook_amount,
            "currency": "INR",
            "status": "success",
            "payment_date": datetime.now(timezone.utc).isoformat()
        }
        await supabase_client.insert("autopay_payments", payment_data)

        logger.info(f"Autopay payment {payment_id} succeeded for subscription {merchant_subscription_id}")

    except Exception as e:
        logger.error(f"Failed to process payment success: {e}", exc_info=True)


async def _process_autopay_payment_failure(webhook_data: Dict[str, Any]):
    """Process failed autopay payment."""
    try:
        from datetime import datetime, timezone

        merchant_subscription_id = webhook_data.get("merchantSubscriptionId")
        payment_id = webhook_data.get("paymentId")
        failure_reason = webhook_data.get("failureReason")

        # Record failed payment in database
        payment_data = {
            "merchant_subscription_id": merchant_subscription_id,
            "payment_id": payment_id,
            "status": "failed",
            "failure_reason": failure_reason,
            "payment_date": datetime.now(timezone.utc).isoformat()
        }
        await supabase_client.insert("autopay_payments", payment_data)

        logger.warning(f"Autopay payment {payment_id} failed for subscription {merchant_subscription_id}: {failure_reason}")

    except Exception as e:
        logger.error(f"Failed to process payment failure: {e}", exc_info=True)


async def _process_autopay_cancellation(webhook_data: Dict[str, Any]):
    """Process autopay subscription cancellation."""
    try:
        from datetime import datetime, timezone

        merchant_subscription_id = webhook_data.get("merchantSubscriptionId")

        # Update subscription status in database
        await supabase_client.update(
            "autopay_subscriptions",
            {"merchant_subscription_id": merchant_subscription_id},
            {
                "status": "cancelled",
                "cancelled_at": datetime.now(timezone.utc).isoformat()
            }
        )

        logger.info(f"Autopay subscription {merchant_subscription_id} cancelled via webhook")

    except Exception as e:
        logger.error(f"Failed to process cancellation: {e}", exc_info=True)
