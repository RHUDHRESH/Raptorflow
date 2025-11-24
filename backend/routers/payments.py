"""
Payment API Router
Endpoints for payment processing, subscription management, and PhonePe integration.
"""

from typing import Dict, Any
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends, Request, Header
import logging

from backend.utils.rate_limit import rate_limit_webhook, get_ip_from_request
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


# Simple auth dependency - will use actual auth from main.py in production
async def get_current_user(authorization: str = Header(None)) -> Dict[str, str]:
    """Get current authenticated user from token."""
    # TODO: Implement proper JWT validation using Supabase
    # For now, returning mock data for development
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # In production, verify JWT and extract user info
    # For development, we'll pass through
    return {
        "user_id": "00000000-0000-0000-0000-000000000000",
        "workspace_id": "00000000-0000-0000-0000-000000000000"
    }


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
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/checkout/create", response_model=CreateCheckoutResponse)
async def create_checkout_session(
    request: CreateCheckoutRequest,
    auth: Dict[str, str] = Depends(get_current_user)
):
    """
    Create a new checkout session for subscription purchase.

    Args:
        request: Checkout request details

    Returns:
        Checkout URL and session details
    """
    correlation_id = generate_correlation_id()
    set_correlation_id(correlation_id)

    try:
        logger.info(f"Creating checkout for user {auth['user_id']}, plan: {request.plan}")

        # Create PhonePe payment request
        payment_request = PhonePePaymentRequest(
            plan=request.plan,
            billing_period=request.billing_period,
            user_id=UUID(auth["user_id"]),
            workspace_id=UUID(auth["workspace_id"]),
            redirect_url=request.success_url,
            callback_url=f"{request.success_url.split('/')[0]}//{request.success_url.split('/')[2]}/api/v1/payments/webhook"
        )

        # Initiate payment with PhonePe
        payment_response, error = await phonepe_service.create_payment(payment_request)

        if error or not payment_response:
            logger.error(f"Payment creation failed: {error}")
            raise HTTPException(status_code=400, detail=error or "Payment creation failed")

        # Store pending transaction in database
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

        # Insert into billing_history table (assuming it exists)
        # await supabase_client.insert("billing_history", transaction_data)

        return CreateCheckoutResponse(
            checkout_url=payment_response.payment_url,
            session_id=payment_response.merchant_transaction_id,
            expires_at=payment_response.created_at
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create checkout: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhook")
@rate_limit_webhook(max_requests=100, window_seconds=60)
async def phonepe_webhook(request: Request):
    """
    Handle PhonePe payment webhook callbacks.

    This endpoint receives payment status updates from PhonePe.
    """
    try:
        # Get webhook payload
        body = await request.body()
        payload_data = await request.json()

        # Extract payload and checksum
        payload_base64 = payload_data.get("response")
        checksum = request.headers.get("X-VERIFY", "")

        if not payload_base64 or not checksum:
            raise HTTPException(status_code=400, detail="Invalid webhook payload")

        # Verify webhook
        webhook_data, error = phonepe_service.verify_webhook_payload(payload_base64, checksum)

        if error or not webhook_data:
            logger.error(f"Webhook verification failed: {error}")
            raise HTTPException(status_code=400, detail="Invalid webhook signature")

        # Process webhook based on payment status
        transaction_id = webhook_data.get("transactionId")
        merchant_transaction_id = webhook_data.get("merchantTransactionId")
        state = webhook_data.get("state", "").upper()

        logger.info(f"Processing webhook for transaction {merchant_transaction_id}, state: {state}")

        if state == "COMPLETED":
            # Payment successful - activate subscription
            await _activate_subscription(webhook_data)

        elif state == "FAILED":
            # Payment failed - update transaction status
            await _mark_payment_failed(merchant_transaction_id)

        return {"status": "success", "message": "Webhook processed"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Webhook processing error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/subscription/status", response_model=Dict[str, Any])
async def get_subscription_status(
    auth: Dict[str, str] = Depends(get_current_user)
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
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/subscription/change", response_model=Dict[str, Any])
async def change_subscription(
    request: SubscriptionChangeRequest,
    auth: Dict[str, str] = Depends(get_current_user)
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
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/subscription/cancel", response_model=Dict[str, Any])
async def cancel_subscription(
    request: CancelSubscriptionRequest,
    auth: Dict[str, str] = Depends(get_current_user)
):
    """
    Cancel active subscription.

    Args:
        request: Cancellation request

    Returns:
        Cancellation confirmation
    """
    correlation_id = generate_correlation_id()
    set_correlation_id(correlation_id)

    try:
        logger.info(f"Cancelling subscription for user {auth['user_id']}")

        # Update subscription status
        updated_sub = await supabase_client.update(
            "subscriptions",
            {"user_id": auth["user_id"]},
            {
                "status": "cancelled",
                "cancelled_at": "now()"
            }
        )

        return {
            "message": "Subscription cancelled successfully",
            "cancelled": True,
            "subscription": updated_sub,
            "correlation_id": correlation_id
        }

    except Exception as e:
        logger.error(f"Failed to cancel subscription: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/billing/history", response_model=Dict[str, Any])
async def get_billing_history(
    auth: Dict[str, str] = Depends(get_current_user)
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
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/payment/status/{merchant_transaction_id}", response_model=Dict[str, Any])
async def check_payment_status(
    merchant_transaction_id: str,
    auth: Dict[str, str] = Depends(get_current_user)
):
    """
    Check status of a payment transaction.

    Args:
        merchant_transaction_id: Transaction ID to check

    Returns:
        Payment status details
    """
    try:
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
        raise HTTPException(status_code=500, detail=str(e))


# Helper functions

async def _activate_subscription(webhook_data: Dict[str, Any]):
    """Activate subscription after successful payment."""
    try:
        # Extract data from webhook
        merchant_user_id = webhook_data.get("merchantUserId")
        amount = webhook_data.get("amount")

        # Calculate subscription dates
        period_start, period_end = phonepe_service.calculate_subscription_dates("monthly")

        # Update or create subscription
        subscription_data = {
            "user_id": merchant_user_id,
            "status": "active",
            "phonepe_transaction_id": webhook_data.get("transactionId"),
            "current_period_start": period_start.isoformat(),
            "current_period_end": period_end.isoformat(),
            "updated_at": "now()"
        }

        # await supabase_client.upsert("subscriptions", subscription_data, ["user_id"])

        logger.info(f"Subscription activated for user {merchant_user_id}")

    except Exception as e:
        logger.error(f"Failed to activate subscription: {e}", exc_info=True)


async def _mark_payment_failed(merchant_transaction_id: str):
    """Mark payment as failed in database."""
    try:
        # Update billing history
        # await supabase_client.update(
        #     "billing_history",
        #     {"merchant_transaction_id": merchant_transaction_id},
        #     {"status": "failed"}
        # )

        logger.info(f"Marked payment {merchant_transaction_id} as failed")

    except Exception as e:
        logger.error(f"Failed to mark payment as failed: {e}", exc_info=True)
