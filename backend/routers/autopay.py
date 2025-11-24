"""
Autopay API Router
Endpoints for PhonePe autopay (recurring payment) subscriptions.
"""

from typing import Dict, Any
from uuid import UUID
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
        logger.info(f"Creating autopay checkout for user {auth['user_id']}, plan: {request.plan}")

        # Create autopay subscription request
        subscription_request = AutopaySubscriptionRequest(
            plan=request.plan,
            billing_period=request.billing_period,
            user_id=UUID(auth["user_id"]),
            workspace_id=UUID(auth["workspace_id"]),
            mobile_number=request.mobile_number,
            redirect_url=request.success_url,
            callback_url=f"{request.success_url.split('/')[0]}//{request.success_url.split('/')[2]}/api/v1/autopay/webhook"
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
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/subscription/status/{merchant_subscription_id}", response_model=Dict[str, Any])
async def get_autopay_subscription_status(
    merchant_subscription_id: str,
    auth: Dict[str, str] = Depends(get_current_user_and_workspace)
):
    """
    Check status of an autopay subscription.

    Args:
        merchant_subscription_id: Merchant subscription ID to check

    Returns:
        Subscription status details
    """
    try:
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
        raise HTTPException(status_code=500, detail=str(e))


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
                "cancelled_at": "now()",
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
        raise HTTPException(status_code=500, detail=str(e))


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
                "paused_at": "now()",
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
                "resumed_at": "now()"
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
@rate_limit_webhook(max_requests=100, window_seconds=60)
async def autopay_webhook(request: Request):
    """
    Handle PhonePe autopay webhook callbacks.

    This endpoint receives autopay events like subscription activation,
    payment success/failure, etc.
    """
    try:
        # Get webhook payload
        payload_base64 = (await request.body()).decode('utf-8')
        x_verify_header = request.headers.get("X-VERIFY", "")

        # Verify webhook signature for security
        webhook_data, error = phonepe_autopay_service.verify_webhook_signature(
            payload_base64,
            x_verify_header
        )
        if error or not webhook_data:
            logger.warning(f"Invalid autopay webhook signature: {error}")
            raise HTTPException(status_code=401, detail="Invalid signature")

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
        merchant_subscription_id = webhook_data.get("merchantSubscriptionId")
        subscription_id = webhook_data.get("subscriptionId")

        # Update subscription status in database
        await supabase_client.update(
            "autopay_subscriptions",
            {"merchant_subscription_id": merchant_subscription_id},
            {
                "status": "active",
                "subscription_id": subscription_id,
                "activated_at": "now()"
            }
        )

        logger.info(f"Autopay subscription {merchant_subscription_id} activated")

    except Exception as e:
        logger.error(f"Failed to activate subscription: {e}", exc_info=True)


async def _process_autopay_payment_success(webhook_data: Dict[str, Any]):
    """Process successful autopay payment."""
    try:
        merchant_subscription_id = webhook_data.get("merchantSubscriptionId")
        payment_id = webhook_data.get("paymentId")
        amount = webhook_data.get("amount")

        # Record payment in database
        payment_data = {
            "merchant_subscription_id": merchant_subscription_id,
            "payment_id": payment_id,
            "amount": amount,
            "currency": "INR",
            "status": "success",
            "payment_date": "now()"
        }
        await supabase_client.insert("autopay_payments", payment_data)

        logger.info(f"Autopay payment {payment_id} succeeded for subscription {merchant_subscription_id}")

    except Exception as e:
        logger.error(f"Failed to process payment success: {e}", exc_info=True)


async def _process_autopay_payment_failure(webhook_data: Dict[str, Any]):
    """Process failed autopay payment."""
    try:
        merchant_subscription_id = webhook_data.get("merchantSubscriptionId")
        payment_id = webhook_data.get("paymentId")
        failure_reason = webhook_data.get("failureReason")

        # Record failed payment in database
        payment_data = {
            "merchant_subscription_id": merchant_subscription_id,
            "payment_id": payment_id,
            "status": "failed",
            "failure_reason": failure_reason,
            "payment_date": "now()"
        }
        await supabase_client.insert("autopay_payments", payment_data)

        logger.warning(f"Autopay payment {payment_id} failed for subscription {merchant_subscription_id}: {failure_reason}")

    except Exception as e:
        logger.error(f"Failed to process payment failure: {e}", exc_info=True)


async def _process_autopay_cancellation(webhook_data: Dict[str, Any]):
    """Process autopay subscription cancellation."""
    try:
        merchant_subscription_id = webhook_data.get("merchantSubscriptionId")

        # Update subscription status in database
        await supabase_client.update(
            "autopay_subscriptions",
            {"merchant_subscription_id": merchant_subscription_id},
            {
                "status": "cancelled",
                "cancelled_at": "now()"
            }
        )

        logger.info(f"Autopay subscription {merchant_subscription_id} cancelled via webhook")

    except Exception as e:
        logger.error(f"Failed to process cancellation: {e}", exc_info=True)
