"""
Enhanced PhonePe Payment API v2
Complete payment integration with email notifications and subscription management
"""

import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional

from api.dependencies import get_auth_context, get_current_user
from core.models import AuthContext, User
from core.supabase_mgr import get_supabase_admin
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from pydantic import BaseModel
from services.email_service import EmailRecipient
from services.payment_service import (
    PaymentError,
    PaymentRequest,
    PaymentResponse,
    PaymentService,
    payment_service,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="", tags=["payments-v2"])


# Request/Response Models
class InitiatePaymentRequest(BaseModel):
    plan: str  # starter, growth, enterprise
    redirect_url: Optional[str] = None
    webhook_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class InitiatePaymentResponse(BaseModel):
    success: bool
    merchant_order_id: Optional[str] = None
    payment_url: Optional[str] = None
    transaction_id: Optional[str] = None
    status: Optional[str] = None
    error: Optional[str] = None
    expires_at: Optional[datetime] = None


class StatusResponse(BaseModel):
    success: bool
    status: Optional[str] = None
    transaction_id: Optional[str] = None
    amount: Optional[int] = None
    phonepe_transaction_id: Optional[str] = None
    subscription: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class PlansResponse(BaseModel):
    success: bool
    plans: Optional[list[Dict[str, Any]]] = None
    error: Optional[str] = None


class WebhookResponse(BaseModel):
    success: bool
    message: str


@router.post("/initiate", response_model=InitiatePaymentResponse)
async def initiate_payment(
    request: InitiatePaymentRequest,
    workspace_id: str = Query(..., description="Workspace ID"),
):
    """
    Initiate a payment for subscription plan
    """
    try:
        # Validate plan
        if request.plan not in payment_service.PLANS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid plan: {request.plan}. Valid plans: {list(payment_service.PLANS.keys())}",
            )

        # Get plan configuration
        plan_config = payment_service.PLANS[request.plan]

        # Create payment request
        payment_request = PaymentRequest(
            workspace_id=auth_context.workspace_id,
            plan=request.plan,
            amount=plan_config.amount,
            customer_email=auth_context.user.email,
            customer_name=auth_context.user.full_name,
            redirect_url=request.redirect_url,
            webhook_url=request.webhook_url,
            metadata=request.metadata,
        )

        # Initiate payment
        result = payment_service.initiate_payment(payment_request)

        if result.success:
            logger.info(
                f"Payment initiated successfully for workspace {auth_context.workspace_id}, "
                f"plan: {request.plan}, order_id: {result.merchant_order_id}"
            )
            return InitiatePaymentResponse(
                success=True,
                merchant_order_id=result.merchant_order_id,
                payment_url=result.payment_url,
                transaction_id=result.phonepe_transaction_id,
                status=result.status,
                expires_at=result.expires_at,
            )
        else:
            logger.error(f"Payment initiation failed: {result.error}")
            return InitiatePaymentResponse(success=False, error=result.error)

    except HTTPException:
        raise
    except PaymentError as exc:
        logger.error(f"Payment service error: {exc}")
        raise HTTPException(status_code=400, detail=f"Payment failed: {exc}")
    except Exception as exc:
        logger.error(f"Payment initiation error: {exc}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/status/{merchant_order_id}", response_model=StatusResponse)
async def get_payment_status(
    merchant_order_id: str, workspace_id: str = Query(..., description="Workspace ID")
):
    """
    Check payment status and subscription information
    """
    try:
        logger.info(f"Checking payment status: {merchant_order_id}")

        # Check payment status
        result = payment_service.check_payment_status(merchant_order_id)

        if result.success:
            # Get subscription information
            supabase = get_supabase_admin()
            subscription_result = (
                supabase.table("subscriptions")
                .select("*")
                .eq("workspace_id", auth_context.workspace_id)
                .eq("status", "active")
                .single()
                .execute()
            )

            subscription_data = None
            if subscription_result.data:
                subscription_data = {
                    "id": subscription_result.data["id"],
                    "plan": subscription_result.data["plan"],
                    "status": subscription_result.data["status"],
                    "current_period_end": subscription_result.data[
                        "current_period_end"
                    ],
                }

            return StatusResponse(
                success=True,
                status=result.status,
                transaction_id=result.phonepe_transaction_id,
                amount=result.amount,
                phonepe_transaction_id=result.phonepe_transaction_id,
                subscription=subscription_data,
            )
        else:
            return StatusResponse(success=False, error=result.error)

    except Exception as exc:
        logger.error(f"Status check error: {exc}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/plans", response_model=PlansResponse)
async def get_payment_plans():
    """
    Get available payment plans
    """
    try:
        plans = payment_service.get_payment_plans()
        return PlansResponse(success=True, plans=plans)
    except Exception as exc:
        logger.error(f"Get plans error: {exc}")
        return PlansResponse(success=False, error=str(exc))


@router.post("/webhook", response_model=WebhookResponse)
async def handle_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Handle PhonePe webhook callbacks
    """
    try:
        # Get authorization header
        authorization = request.headers.get("Authorization")
        if not authorization:
            raise HTTPException(status_code=401, detail="Missing Authorization header")

        # Get raw body
        body = await request.body()
        body_str = body.decode("utf-8")

        logger.info("Received PhonePe webhook")

        # Validate webhook
        validation_result = payment_service.validate_webhook(authorization, body_str)

        if validation_result["valid"]:
            webhook_data = validation_result["data"]

            logger.info(
                f"Webhook validated - Txn: {webhook_data.get('merchantTransactionId')}, "
                f"Code: {webhook_data.get('code')}"
            )

            # Process webhook in background
            background_tasks.add_task(
                payment_service.process_webhook_callback, webhook_data
            )

            return WebhookResponse(
                success=True, message="Webhook processed successfully"
            )
        else:
            logger.warning("Webhook validation failed")
            raise HTTPException(status_code=401, detail="Invalid webhook signature")

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Webhook error: {exc}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/health")
async def health_check():
    """
    Check payment service health
    """
    try:
        # Test payment service initialization
        plans = payment_service.get_payment_plans()
        return {
            "status": "healthy",
            "service": "payment_service",
            "plans_count": len(plans),
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as exc:
        logger.error(f"Health check failed: {exc}")
        return {
            "status": "unhealthy",
            "error": str(exc),
            "timestamp": datetime.now().isoformat(),
        }
